//! Teclas da serial (115200 8N1). O monitor não ecoa; o firmware ecoa os
//! dígitos.
//!
//! Parar na hora é uma tecla só e vale a qualquer momento, inclusive no meio
//! de um número: espaço, `p`, Esc ou Ctrl-C. A serial seleciona o perfil,
//! dá partida com `g`, ajusta o alvo, encerra o chute e faz a parada suave.

use crate::controller::{Command, StartMode, StopSource};

/// Número digitado e abandonado é descartado depois deste tempo.
pub const ENTRY_TIMEOUT_MS: u32 = 10_000;
const MAX_DIGITS: u8 = 5;

pub const HELP: &str = "\
# Teclas (115200 8N1; comandos de uma tecla não precisam de Enter):
#   g                        PARTIDA (também pelo botão D32)
#   l / o                    perfil linear / overshoot (só parado; padrão linear)
#   espaço, p, Esc, Ctrl-C   PARAR na hora (a qualquer momento)
#   d                        parada suave: desce ao acelerador zero e para
#   k                        encerra o chute agora (ao ver o rotor girar)
#   1250 Enter               alvo de regime em µs (até o teto)
#   + / -                    alvo ±5 µs      > / <  alvo ±1 µs
#   r3 Enter                 subida até alvo/chute em s (3 a 30; só parado)
#   c2 Enter                 duração do chute do overshoot (0 a 5 s; só parado)
#   s                        estado          h ou ?  esta ajuda
#   W (maiúsculo)            trava o laço de propósito: ensaio do WATCHDOG";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Field {
    /// Alvo em µs.
    Target,
    /// Subida em s.
    Ramp,
    /// Chute em s.
    Kick,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action {
    Command(Command),
    Status,
    Help,
    /// Ecoar este byte; `0x08` apaga o último caractere.
    Echo(u8),
    /// Travar o laço até o watchdog reiniciar o chip (05 §8.2: "confirmar
    /// na bancada, junto com a PARADA"). Em giro, o pulso fica no último
    /// valor até o reinício e então some.
    Freeze,
    Error(&'static str),
}

pub struct Console {
    entry: Option<Entry>,
    nudge_coarse_us: i16,
    nudge_fine_us: i16,
}

struct Entry {
    field: Field,
    value: u32,
    digits: u8,
    last_key_ms: u32,
}

const STOP: Action = Action::Command(Command::Stop(StopSource::Serial));

impl Console {
    pub const fn new(nudge_coarse_us: i16, nudge_fine_us: i16) -> Self {
        Self {
            entry: None,
            nudge_coarse_us,
            nudge_fine_us,
        }
    }

    /// Há um número sendo digitado (o registro periódico espera).
    pub fn is_editing(&self) -> bool {
        self.entry.is_some()
    }

    pub fn feed(&mut self, byte: u8, now_ms: u32) -> Option<Action> {
        if matches!(byte, b' ' | b'p' | b'P' | 0x1b | 0x03) {
            self.entry = None;
            return Some(STOP);
        }
        match self.entry.as_mut() {
            None => self.key(byte, now_ms),
            Some(entry) => {
                entry.last_key_ms = now_ms;
                match byte {
                    b'0'..=b'9' if entry.digits < MAX_DIGITS => {
                        entry.value = entry.value * 10 + (byte - b'0') as u32;
                        entry.digits += 1;
                        Some(Action::Echo(byte))
                    }
                    b'0'..=b'9' => self.abort("número longo demais"),
                    0x08 | 0x7f if entry.digits > 0 => {
                        entry.value /= 10;
                        entry.digits -= 1;
                        Some(Action::Echo(0x08))
                    }
                    0x08 | 0x7f => self.abort("entrada cancelada"),
                    b'\r' | b'\n' => self.finish(),
                    _ => self.abort("número interrompido: só dígitos e Enter"),
                }
            }
        }
    }

    /// Chamar a cada volta do laço: descarta número abandonado.
    pub fn poll(&mut self, now_ms: u32) -> Option<Action> {
        let entry = self.entry.as_ref()?;
        if now_ms.wrapping_sub(entry.last_key_ms) >= ENTRY_TIMEOUT_MS {
            return self.abort("número abandonado");
        }
        None
    }

    fn key(&mut self, byte: u8, now_ms: u32) -> Option<Action> {
        let nudge = |us| Some(Action::Command(Command::NudgeTarget(us)));
        match byte {
            b'g' | b'G' => Some(Action::Command(Command::Start)),
            b'l' | b'L' => Some(Action::Command(Command::SetStartMode(StartMode::Linear))),
            b'o' | b'O' => Some(Action::Command(Command::SetStartMode(StartMode::Overshoot))),
            b'+' | b'=' => nudge(self.nudge_coarse_us),
            b'-' | b'_' => nudge(-self.nudge_coarse_us),
            b'>' | b'.' => nudge(self.nudge_fine_us),
            b'<' | b',' => nudge(-self.nudge_fine_us),
            b'0'..=b'9' => {
                self.entry = Some(Entry {
                    field: Field::Target,
                    value: (byte - b'0') as u32,
                    digits: 1,
                    last_key_ms: now_ms,
                });
                Some(Action::Echo(byte))
            }
            b'r' | b'R' => self.prefix(Field::Ramp, b'r', now_ms),
            b'c' | b'C' => self.prefix(Field::Kick, b'c', now_ms),
            b'k' | b'K' => Some(Action::Command(Command::EndKick)),
            b'd' | b'D' => Some(Action::Command(Command::SoftStop)),
            b's' | b'S' => Some(Action::Status),
            b'h' | b'H' | b'?' => Some(Action::Help),
            b'W' => Some(Action::Freeze),
            b'\r' | b'\n' => None,
            _ => Some(Action::Error("tecla sem função; h mostra a ajuda")),
        }
    }

    fn prefix(&mut self, field: Field, echo: u8, now_ms: u32) -> Option<Action> {
        self.entry = Some(Entry {
            field,
            value: 0,
            digits: 0,
            last_key_ms: now_ms,
        });
        Some(Action::Echo(echo))
    }

    fn finish(&mut self) -> Option<Action> {
        let entry = self.entry.take()?;
        if entry.digits == 0 {
            return Some(Action::Error("número vazio"));
        }
        let command = match entry.field {
            Field::Target => match u16::try_from(entry.value) {
                Ok(us) => Command::SetTarget(us),
                Err(_) => return Some(Action::Error("alvo fora da faixa")),
            },
            Field::Ramp => Command::SetRamp(entry.value * 1000),
            Field::Kick => Command::SetKick(entry.value * 1000),
        };
        Some(Action::Command(command))
    }

    fn abort(&mut self, why: &'static str) -> Option<Action> {
        self.entry = None;
        Some(Action::Error(why))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn feed(c: &mut Console, bytes: &[u8]) -> Vec<Action> {
        bytes.iter().filter_map(|&b| c.feed(b, 0)).collect()
    }

    fn cmd(command: Command) -> Action {
        Action::Command(command)
    }

    #[test]
    fn stop_keys_always_stop_even_mid_number() {
        let mut c = Console::new(5, 1);
        for key in [b' ', b'p', b'P', 0x1b, 0x03] {
            assert_eq!(c.feed(key, 0), Some(STOP));
            c.feed(b'1', 0);
            c.feed(b'3', 0);
            assert!(c.is_editing());
            assert_eq!(c.feed(key, 0), Some(STOP));
            assert!(!c.is_editing());
        }
    }

    #[test]
    fn target_entry() {
        let mut c = Console::new(5, 1);
        let got = feed(&mut c, b"1350\r");
        assert_eq!(got.last(), Some(&cmd(Command::SetTarget(1350))));
        assert_eq!(&got[..4], &b"1350".map(Action::Echo));
        assert!(!c.is_editing());
        // Backspace corrige.
        let got = feed(&mut c, b"13x");
        assert_eq!(
            got.last(),
            Some(&Action::Error("número interrompido: só dígitos e Enter"))
        );
        let got = feed(&mut c, b"137\x7f5\n");
        assert_eq!(got.last(), Some(&cmd(Command::SetTarget(135))));
        let got = feed(&mut c, b"999999");
        assert_eq!(got.last(), Some(&Action::Error("número longo demais")));
        let got = feed(&mut c, b"70000\r");
        assert_eq!(got.last(), Some(&Action::Error("alvo fora da faixa")));
    }

    #[test]
    fn ramp_and_kick_entry() {
        let mut c = Console::new(5, 1);
        assert_eq!(
            feed(&mut c, b"r20\r").last(),
            Some(&cmd(Command::SetRamp(20_000)))
        );
        assert_eq!(
            feed(&mut c, b"c2\r").last(),
            Some(&cmd(Command::SetKick(2_000)))
        );
        assert_eq!(
            feed(&mut c, b"C0\n").last(),
            Some(&cmd(Command::SetKick(0)))
        );
        assert_eq!(
            feed(&mut c, b"c\r").last(),
            Some(&Action::Error("número vazio"))
        );
        assert_eq!(
            feed(&mut c, b"r\r").last(),
            Some(&Action::Error("número vazio"))
        );
        // "r 20": o espaço para, e o resto vira um alvo de 20 µs (que o
        // controlador recusa). Nada sobe.
        let got = feed(&mut c, b"r 20\r");
        assert!(got.contains(&STOP));
        assert_eq!(got.last(), Some(&cmd(Command::SetTarget(20))));
    }

    #[test]
    fn nudges_and_other_keys() {
        let mut c = Console::new(5, 1);
        assert_eq!(
            feed(&mut c, b"+=-_><.,"),
            [5, 5, -5, -5, 1, -1, 1, -1].map(|d| cmd(Command::NudgeTarget(d)))
        );
        assert_eq!(feed(&mut c, b"sS"), [Action::Status, Action::Status]);
        assert_eq!(feed(&mut c, b"h?"), [Action::Help, Action::Help]);
        assert_eq!(feed(&mut c, b"W"), [Action::Freeze]);
        assert_eq!(
            feed(&mut c, b"kK"),
            [cmd(Command::EndKick), cmd(Command::EndKick)]
        );
        assert_eq!(
            feed(&mut c, b"dD"),
            [cmd(Command::SoftStop), cmd(Command::SoftStop)]
        );
        // No meio de um número, k e d só interrompem a entrada.
        assert_eq!(
            feed(&mut c, b"12d").last(),
            Some(&Action::Error("número interrompido: só dígitos e Enter"))
        );
        assert!(matches!(feed(&mut c, b"w")[..], [Action::Error(_)]));
        assert_eq!(feed(&mut c, b"\r\n"), Vec::<Action>::new());
        assert!(matches!(feed(&mut c, b"x")[..], [Action::Error(_)]));
    }

    #[test]
    fn only_the_explicit_start_key_starts_the_motor() {
        let mut c = Console::new(5, 1);
        for b in 0..=255u8 {
            for prefix in [&b""[..], b"1", b"r", b"c"] {
                let mut bytes = prefix.to_vec();
                bytes.extend([b, b'\r']);
                for action in feed(&mut c, &bytes) {
                    if action == cmd(Command::Start) {
                        assert!(prefix.is_empty() && matches!(b, b'g' | b'G'));
                    }
                }
                c.feed(0x1b, 0);
            }
        }
    }

    #[test]
    fn terminal_selects_profiles_and_starts_the_controller() {
        use crate::{
            config,
            controller::{Controller, Event, Reply, State},
        };
        let mut console = Console::new(5, 1);
        let mut ctl = Controller::new(config::LIMITS, 1200, 3_000, 2_000, 0);
        assert_eq!(console.feed(b'g', 0), Some(cmd(Command::Start)));
        assert_eq!(
            ctl.command(Command::Start, 0),
            Reply::Rejected(crate::controller::Reject::Arming)
        );
        ctl.update(2_000);
        // Sequência real enviada pelo terminal, com CRLF.
        for action in feed(&mut console, b"l\r\n1250\r\nr3\r\ng\r\n") {
            if let Action::Command(command) = action {
                ctl.command(command, 2_000);
            }
        }
        assert_eq!(ctl.start_mode(), StartMode::Linear);
        assert_eq!(ctl.starts(), 1);
        assert_eq!(ctl.target_us(), 1250);
        let mut reached = false;
        for t in 2_001..=5_001 {
            if let Some(Event::Reached {
                target_us: 1250, ..
            }) = ctl.update(t)
            {
                reached = true;
            }
            assert!(ctl.pulse_ns() <= 1_250_000);
        }
        assert!(reached);
        assert_eq!(ctl.state(), State::Holding);
        for action in feed(&mut console, b"po\r\nc0\r\ng\r\n") {
            if let Action::Command(command) = action {
                ctl.command(command, 5_001);
            }
        }
        assert_eq!(ctl.start_mode(), StartMode::Overshoot);
        assert_eq!(ctl.starts(), 2);
        assert_eq!(
            ctl.update(8_001),
            Some(Event::KickReached { after_ms: 3_000 })
        );
        assert_eq!(ctl.pulse_ns(), config::LIMITS.kick_ns());
        assert!(matches!(ctl.update(8_002), Some(Event::KickEnded { .. })));
    }

    #[test]
    fn abandoned_entry_times_out() {
        let mut c = Console::new(5, 1);
        c.feed(b'1', 1_000);
        assert_eq!(c.poll(10_999), None);
        c.feed(b'2', 10_999);
        assert_eq!(c.poll(20_998), None);
        assert_eq!(c.poll(20_999), Some(Action::Error("número abandonado")));
        assert!(!c.is_editing());
        assert_eq!(c.poll(30_000), None);
    }
}
