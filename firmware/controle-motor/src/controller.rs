//! Máquina de estados do gerador: ARMAÇÃO, PARTIDA COM CHUTE, REGIME, PARADA
//! e TETO (05 §8.2).
//!
//! A partida sobe do PPM mínimo ao pulso de CHUTE, acima do teto de regime,
//! segura o chute por pouco tempo e desce ao alvo. A base não mede a
//! rotação: o chute acaba pelo tempo ou, antes, pela tecla do operador ao
//! ver o rotor girar. Acima do teto de regime o pulso só fica durante a
//! partida, por tempo limitado.
//!
//! O pulso fica em nanossegundos para a rampa avançar frações de µs a cada
//! milissegundo sem acumular erro. Toda descida em giro tem inclinação
//! limitada, para não frear mais rápido que o arrasto e devolver energia à
//! fonte; a parada na hora é a única mudança instantânea.

/// Subida mais longa aceita pelo console.
pub const MAX_RAMP_MS: u32 = 30_000;
/// Chute mais longo aceito pelo console.
pub const MAX_KICK_MS: u32 = 5_000;

/// Faixa do sinal e tempos que o controlador nunca viola.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Limits {
    /// Pulso de armação e de parada, abaixo do PPM mínimo do ESC.
    pub stop_us: u16,
    /// Acelerador zero no ESC; a subida parte daqui.
    pub ppm_min_us: u16,
    /// Acelerador máximo no ESC; nunca alcançado.
    pub ppm_max_us: u16,
    /// TETO de regime: maior alvo aceito.
    pub ceiling_us: u16,
    /// CHUTE: pulso da partida e maior pulso que sai do LEDC.
    pub kick_us: u16,
    /// Subida: do PPM mínimo ao chute em no mínimo este tempo.
    pub min_ramp_ms: u32,
    /// Descida depois do chute: do chute ao PPM mínimo neste tempo.
    pub fall_ms: u32,
    /// Ajustes em giro e parada suave: do chute ao PPM mínimo neste tempo.
    pub adjust_ms: u32,
    /// Pulso de parada mantido desde a energização antes de aceitar comandos.
    pub arming_ms: u32,
}

impl Limits {
    pub const fn is_valid(&self) -> bool {
        self.stop_us >= 900
            && self.stop_us < self.ppm_min_us
            && self.ppm_min_us < self.ceiling_us
            && self.ceiling_us < self.kick_us
            && self.kick_us < self.ppm_max_us
            && self.min_ramp_ms >= 3_000
            && self.min_ramp_ms <= MAX_RAMP_MS
            && self.fall_ms >= self.min_ramp_ms
            && self.adjust_ms >= self.min_ramp_ms
            && self.arming_ms >= 2_000
    }

    pub const fn stop_ns(&self) -> u32 {
        self.stop_us as u32 * 1000
    }

    pub const fn ppm_min_ns(&self) -> u32 {
        self.ppm_min_us as u32 * 1000
    }

    pub const fn ceiling_ns(&self) -> u32 {
        self.ceiling_us as u32 * 1000
    }

    pub const fn kick_ns(&self) -> u32 {
        self.kick_us as u32 * 1000
    }

    /// Do PPM mínimo ao chute, em ns: a escala de todas as inclinações.
    const fn span_ns(&self) -> u32 {
        (self.kick_us - self.ppm_min_us) as u32 * 1000
    }

    /// Maior inclinação permitida, em ns de pulso por segundo.
    pub const fn max_rate_ns_per_s(&self) -> u32 {
        rate(self.span_ns(), self.min_ramp_ms)
    }

    /// Descida do chute ao alvo, em ns/s.
    pub const fn fall_rate_ns_per_s(&self) -> u32 {
        rate(self.span_ns(), self.fall_ms)
    }

    /// Ajustes em giro e parada suave, em ns/s.
    pub const fn adjust_rate_ns_per_s(&self) -> u32 {
        rate(self.span_ns(), self.adjust_ms)
    }
}

/// Inclinação para percorrer `span_ns` em `ramp_ms`, arredondada para baixo
/// (o movimento nunca fica mais curto que o pedido) e nunca nula.
const fn rate(span_ns: u32, ramp_ms: u32) -> u32 {
    let r = (span_ns as u64 * 1000 / ramp_ms as u64) as u32;
    if r == 0 { 1 } else { r }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State {
    /// Pulso de parada desde a energização; nenhum comando é aceito.
    Arming,
    /// Pulso de parada; espera o botão de partida.
    Stopped,
    /// Pulso a caminho do chute (subida) ou do alvo.
    Ramping,
    /// Pulso no chute, por tempo limitado.
    Kicking,
    /// Pulso no alvo.
    Holding,
    /// Parada suave: pulso descendo ao PPM mínimo; depois, parada.
    Braking,
}

impl State {
    pub const fn label(self) -> &'static str {
        match self {
            State::Arming => "ARMANDO",
            State::Stopped => "PARADO",
            State::Ramping => "RAMPA",
            State::Kicking => "CHUTE",
            State::Holding => "REGIME",
            State::Braking => "PARANDO",
        }
    }

    pub const fn is_running(self) -> bool {
        matches!(
            self,
            State::Ramping | State::Kicking | State::Holding | State::Braking
        )
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StopSource {
    Button,
    Serial,
}

impl StopSource {
    pub const fn label(self) -> &'static str {
        match self {
            StopSource::Button => "pelo botão",
            StopSource::Serial => "pela serial",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Command {
    /// Só o botão de partida gera este comando.
    Start,
    /// Parada na hora.
    Stop(StopSource),
    /// Parada suave: desce ao PPM mínimo na inclinação de ajuste e para.
    SoftStop,
    /// Encerra o chute agora (ou a subida até ele) e desce ao alvo.
    EndKick,
    /// Alvo absoluto, em µs.
    SetTarget(u16),
    /// Alvo relativo, em µs; satura no teto e logo acima do PPM mínimo.
    NudgeTarget(i16),
    /// Duração da subida até o chute, em ms.
    SetRamp(u32),
    /// Duração do chute, em ms.
    SetKick(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reply {
    Started { count: u32 },
    Stopped { was_running: bool },
    SoftStop { was_running: bool },
    KickEnded,
    Target { target_us: u16, saturated: bool },
    Ramp { ramp_ms: u32 },
    Kick { kick_ms: u32 },
    Rejected(Reject),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reject {
    Arming,
    Running,
    AboveCeiling,
    NotAboveMinimum,
    RampTooShort,
    RampTooLong,
    KickTooLong,
    NotKicking,
}

impl Reject {
    pub const fn message(self) -> &'static str {
        match self {
            Reject::Arming => "ainda armando o ESC",
            Reject::Running => "motor girando: pare antes",
            Reject::AboveCeiling => "acima do teto",
            Reject::NotAboveMinimum => "não passa do PPM mínimo; para parar use espaço, p ou d",
            Reject::RampTooShort => "subida abaixo do mínimo",
            Reject::RampTooLong => "subida acima do máximo",
            Reject::KickTooLong => "chute acima do máximo",
            Reject::NotKicking => "fora do chute",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Event {
    /// Fim da armação: o ESC viu o pulso de parada pelo tempo pedido.
    Armed,
    /// O pulso chegou ao chute, `after_ms` depois da partida.
    KickReached { after_ms: u32 },
    /// O chute acabou pelo tempo; o pulso começa a descer ao alvo.
    KickEnded { held_ms: u32 },
    /// O pulso chegou ao alvo, `after_ms` depois do início do movimento.
    Reached { target_us: u16, after_ms: u32 },
    /// A parada suave chegou ao PPM mínimo e o pulso voltou ao de parada.
    SoftStopped { run_ms: u32 },
}

pub struct Controller {
    lim: Limits,
    state: State,
    pulse_ns: u32,
    dest_ns: u32,
    rate_ns_per_s: u32,
    /// Fração de ns ainda não aplicada, em milésimos.
    carry: u32,
    last_ms: u32,
    boot_ms: u32,
    move_since_ms: u32,
    run_since_ms: u32,
    kick_since_ms: u32,
    target_us: u16,
    ramp_ms: u32,
    kick_ms: u32,
    starts: u32,
}

impl Controller {
    /// Começa armando, com o pulso de parada.
    pub fn new(lim: Limits, target_us: u16, ramp_ms: u32, kick_ms: u32, now_ms: u32) -> Self {
        assert!(lim.is_valid());
        assert!(target_us > lim.ppm_min_us && target_us <= lim.ceiling_us);
        assert!(ramp_ms >= lim.min_ramp_ms && ramp_ms <= MAX_RAMP_MS);
        assert!(kick_ms <= MAX_KICK_MS);
        Self {
            lim,
            state: State::Arming,
            pulse_ns: lim.stop_ns(),
            dest_ns: lim.stop_ns(),
            rate_ns_per_s: 0,
            carry: 0,
            last_ms: now_ms,
            boot_ms: now_ms,
            move_since_ms: now_ms,
            run_since_ms: now_ms,
            kick_since_ms: now_ms,
            target_us,
            ramp_ms,
            kick_ms,
            starts: 0,
        }
    }

    /// Avança o relógio; chamar a cada volta do laço principal.
    pub fn update(&mut self, now_ms: u32) -> Option<Event> {
        let dt_ms = now_ms.wrapping_sub(self.last_ms);
        self.last_ms = now_ms;
        match self.state {
            State::Arming => {
                if now_ms.wrapping_sub(self.boot_ms) >= self.lim.arming_ms {
                    self.state = State::Stopped;
                    return Some(Event::Armed);
                }
                None
            }
            State::Stopped | State::Holding => None,
            State::Kicking => {
                let held_ms = now_ms.wrapping_sub(self.kick_since_ms);
                if held_ms < self.kick_ms {
                    return None;
                }
                self.end_kick(now_ms);
                Some(Event::KickEnded { held_ms })
            }
            State::Ramping | State::Braking => {
                self.advance(dt_ms);
                if self.pulse_ns != self.dest_ns {
                    return None;
                }
                if self.state == State::Braking {
                    let run_ms = now_ms.wrapping_sub(self.run_since_ms);
                    self.halt();
                    return Some(Event::SoftStopped { run_ms });
                }
                if self.dest_ns == self.lim.kick_ns() {
                    self.state = State::Kicking;
                    self.kick_since_ms = now_ms;
                    return Some(Event::KickReached {
                        after_ms: now_ms.wrapping_sub(self.move_since_ms),
                    });
                }
                self.state = State::Holding;
                Some(Event::Reached {
                    target_us: self.target_us,
                    after_ms: now_ms.wrapping_sub(self.move_since_ms),
                })
            }
        }
    }

    pub fn command(&mut self, command: Command, now_ms: u32) -> Reply {
        match command {
            Command::Stop(_) => {
                let was_running = self.state.is_running();
                self.halt();
                Reply::Stopped { was_running }
            }
            Command::SoftStop => match self.state {
                State::Arming | State::Stopped => Reply::SoftStop { was_running: false },
                // Já descendo: a parada suave segue igual.
                State::Braking => Reply::SoftStop { was_running: true },
                _ => {
                    let rate = self.lim.adjust_rate_ns_per_s();
                    self.begin_move(self.lim.ppm_min_ns(), rate, now_ms);
                    self.state = State::Braking;
                    Reply::SoftStop { was_running: true }
                }
            },
            Command::EndKick => {
                if self.in_kick() {
                    self.end_kick(now_ms);
                    Reply::KickEnded
                } else {
                    Reply::Rejected(Reject::NotKicking)
                }
            }
            Command::Start => match self.state {
                State::Arming => Reply::Rejected(Reject::Arming),
                State::Stopped => {
                    self.starts += 1;
                    self.run_since_ms = now_ms;
                    // De 1000 a 1148 µs o ESC não vê diferença: o salto é
                    // dentro do acelerador zero, e a subida inteira é útil.
                    self.pulse_ns = self.lim.ppm_min_ns();
                    let rate = rate(self.lim.span_ns(), self.ramp_ms);
                    self.begin_move(self.lim.kick_ns(), rate, now_ms);
                    Reply::Started { count: self.starts }
                }
                _ => Reply::Rejected(Reject::Running),
            },
            Command::SetTarget(us) => self.set_target(us, false, now_ms),
            Command::NudgeTarget(delta) => {
                let wanted = self.target_us as i32 + delta as i32;
                let clamped =
                    wanted.clamp(self.lim.ppm_min_us as i32 + 1, self.lim.ceiling_us as i32);
                self.set_target(clamped as u16, clamped != wanted, now_ms)
            }
            Command::SetRamp(ms) => {
                if self.state.is_running() {
                    Reply::Rejected(Reject::Running)
                } else if ms < self.lim.min_ramp_ms {
                    Reply::Rejected(Reject::RampTooShort)
                } else if ms > MAX_RAMP_MS {
                    Reply::Rejected(Reject::RampTooLong)
                } else {
                    self.ramp_ms = ms;
                    Reply::Ramp { ramp_ms: ms }
                }
            }
            Command::SetKick(ms) => {
                if self.state.is_running() {
                    Reply::Rejected(Reject::Running)
                } else if ms > MAX_KICK_MS {
                    Reply::Rejected(Reject::KickTooLong)
                } else {
                    self.kick_ms = ms;
                    Reply::Kick { kick_ms: ms }
                }
            }
        }
    }

    fn set_target(&mut self, us: u16, saturated: bool, now_ms: u32) -> Reply {
        if us > self.lim.ceiling_us {
            return Reply::Rejected(Reject::AboveCeiling);
        }
        if us <= self.lim.ppm_min_us {
            return Reply::Rejected(Reject::NotAboveMinimum);
        }
        let changed = us != self.target_us;
        self.target_us = us;
        // Na partida o alvo só muda onde a descida termina; na parada suave,
        // nada. Alvo repetido não replaneja: o movimento em curso segue igual.
        let adjustable = matches!(self.state, State::Ramping | State::Holding) && !self.in_kick();
        if adjustable && changed {
            let rate = self.lim.adjust_rate_ns_per_s();
            self.begin_move(self.target_ns(), rate, now_ms);
        }
        Reply::Target {
            target_us: us,
            saturated,
        }
    }

    /// Subindo ao chute ou nele.
    fn in_kick(&self) -> bool {
        self.state == State::Kicking
            || (self.state == State::Ramping && self.dest_ns == self.lim.kick_ns())
    }

    fn end_kick(&mut self, now_ms: u32) {
        let rate = self.lim.fall_rate_ns_per_s();
        self.begin_move(self.target_ns(), rate, now_ms);
    }

    /// Parada na hora: pulso de parada; durante a armação, segue armando.
    fn halt(&mut self) {
        if self.state != State::Arming {
            self.state = State::Stopped;
        }
        self.pulse_ns = self.lim.stop_ns();
        self.dest_ns = self.pulse_ns;
        self.carry = 0;
    }

    fn begin_move(&mut self, dest_ns: u32, rate_ns_per_s: u32, now_ms: u32) {
        self.dest_ns = dest_ns;
        self.rate_ns_per_s = rate_ns_per_s.min(self.lim.max_rate_ns_per_s());
        self.carry = 0;
        self.move_since_ms = now_ms;
        self.last_ms = now_ms;
        self.state = if self.pulse_ns == self.dest_ns {
            State::Holding
        } else {
            State::Ramping
        };
    }

    fn advance(&mut self, dt_ms: u32) {
        let total = self.rate_ns_per_s as u64 * dt_ms as u64 + self.carry as u64;
        let step = (total / 1000).min(u32::MAX as u64) as u32;
        self.carry = (total % 1000) as u32;
        self.pulse_ns = if self.pulse_ns < self.dest_ns {
            self.pulse_ns.saturating_add(step).min(self.dest_ns)
        } else {
            self.pulse_ns.saturating_sub(step).max(self.dest_ns)
        };
        if self.pulse_ns == self.dest_ns {
            self.carry = 0;
        }
    }

    fn target_ns(&self) -> u32 {
        self.target_us as u32 * 1000
    }

    pub fn state(&self) -> State {
        self.state
    }

    /// Pulso a gerar agora, em ns, sempre entre o pulso de parada e o chute.
    pub fn pulse_ns(&self) -> u32 {
        self.pulse_ns
    }

    pub fn target_us(&self) -> u16 {
        self.target_us
    }

    pub fn ramp_ms(&self) -> u32 {
        self.ramp_ms
    }

    pub fn kick_ms(&self) -> u32 {
        self.kick_ms
    }

    /// Partidas aceitas desde a energização.
    pub fn starts(&self) -> u32 {
        self.starts
    }

    pub fn limits(&self) -> &Limits {
        &self.lim
    }

    /// Tempo desde a última partida, enquanto gira.
    pub fn running_ms(&self, now_ms: u32) -> Option<u32> {
        self.state
            .is_running()
            .then(|| now_ms.wrapping_sub(self.run_since_ms))
    }

    /// Acelerador estimado pela faixa PPM do ESC, em décimos de por cento.
    pub fn throttle_permille(&self) -> u32 {
        let min = self.lim.ppm_min_ns();
        let range = (self.lim.ppm_max_us - self.lim.ppm_min_us) as u32 * 1000;
        (self.pulse_ns.saturating_sub(min) as u64 * 1000 / range as u64) as u32
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const LIM: Limits = Limits {
        stop_us: 1000,
        ppm_min_us: 1148,
        ppm_max_us: 1832,
        ceiling_us: 1320,
        kick_us: 1400,
        min_ramp_ms: 3_000,
        fall_ms: 6_000,
        adjust_ms: 12_000,
        arming_ms: 2_000,
    };

    /// Controlador já armado em `t = 2000 ms`.
    fn armed(target_us: u16, ramp_ms: u32, kick_ms: u32) -> Controller {
        let mut c = Controller::new(LIM, target_us, ramp_ms, kick_ms, 0);
        assert_eq!(c.update(2_000), Some(Event::Armed));
        c
    }

    /// Roda de `from` até `to` em passos de 1 ms; devolve o último evento.
    fn run(c: &mut Controller, from: u32, to: u32) -> Option<(u32, Event)> {
        let mut last = None;
        let mut t = from;
        while t != to {
            t = t.wrapping_add(1);
            if let Some(e) = c.update(t) {
                last = Some((t, e));
            }
        }
        last
    }

    /// Partida em `t = 2000 ms` e regime no alvo: subida de 3 s, chute de
    /// 2 s e descida a 42 µs/s. Devolve o instante do regime.
    fn started_and_holding(target_us: u16) -> (Controller, u32) {
        let mut c = armed(target_us, 3_000, 2_000);
        c.command(Command::Start, 2_000);
        let (t, e) = run(&mut c, 2_000, 30_000).unwrap();
        assert!(matches!(e, Event::Reached { .. }));
        assert_eq!(c.state(), State::Holding);
        (c, t)
    }

    #[test]
    fn arming_holds_stop_pulse_and_refuses_start() {
        let mut c = Controller::new(LIM, 1200, 3_000, 2_000, 0);
        for t in 0..2_000 {
            assert_eq!(c.update(t), None);
            assert_eq!(c.pulse_ns(), 1_000_000);
            assert_eq!(c.command(Command::Start, t), Reply::Rejected(Reject::Arming));
        }
        assert_eq!(c.update(2_000), Some(Event::Armed));
        assert_eq!(c.state(), State::Stopped);
        assert_eq!(c.update(2_001), None);
        assert_eq!(c.starts(), 0);
    }

    #[test]
    fn stops_while_arming_keep_arming() {
        let mut c = Controller::new(LIM, 1200, 3_000, 2_000, 0);
        assert_eq!(
            c.command(Command::Stop(StopSource::Button), 10),
            Reply::Stopped { was_running: false }
        );
        assert_eq!(c.command(Command::SoftStop, 11), Reply::SoftStop { was_running: false });
        assert_eq!(c.state(), State::Arming);
        assert_eq!(c.update(2_000), Some(Event::Armed));
    }

    #[test]
    fn start_rises_to_the_kick_holds_it_then_falls_to_the_target() {
        let mut c = armed(1200, 3_000, 2_000);
        assert_eq!(c.command(Command::Start, 2_000), Reply::Started { count: 1 });
        assert_eq!(c.state(), State::Ramping);
        assert_eq!(c.pulse_ns(), 1_148_000);

        // 252 µs em 3 s: 84 µs/s.
        run(&mut c, 2_000, 3_500);
        assert_eq!(c.pulse_ns(), 1_274_000);
        assert_eq!(run(&mut c, 3_500, 5_000), Some((5_000, Event::KickReached { after_ms: 3_000 })));
        assert_eq!(c.state(), State::Kicking);
        assert_eq!(c.pulse_ns(), 1_400_000);

        assert_eq!(run(&mut c, 5_000, 6_999), None);
        assert_eq!(c.pulse_ns(), 1_400_000);
        assert_eq!(c.update(7_000), Some(Event::KickEnded { held_ms: 2_000 }));
        assert_eq!(c.state(), State::Ramping);

        // 200 µs a 42 µs/s: 4762 ms.
        let (t, e) = run(&mut c, 7_000, 20_000).unwrap();
        assert_eq!(t, 11_762);
        assert_eq!(
            e,
            Event::Reached {
                target_us: 1200,
                after_ms: 4_762
            }
        );
        assert_eq!(c.state(), State::Holding);
        assert_eq!(c.pulse_ns(), 1_200_000);
        assert_eq!(c.running_ms(t), Some(9_762));
    }

    #[test]
    fn the_key_ends_the_kick_early_even_during_the_rise() {
        let mut c = armed(1200, 3_000, 2_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 4_000);
        let at_key = c.pulse_ns();
        assert_eq!(at_key, 1_316_000);
        assert_eq!(c.command(Command::EndKick, 4_000), Reply::KickEnded);
        assert_eq!(c.state(), State::Ramping);
        run(&mut c, 4_000, 4_001);
        assert!(c.pulse_ns() < at_key);
        let (_, e) = run(&mut c, 4_001, 20_000).unwrap();
        assert!(matches!(e, Event::Reached { target_us: 1200, .. }));
        assert_eq!(c.command(Command::EndKick, 20_000), Reply::Rejected(Reject::NotKicking));

        // No chute.
        c.command(Command::Stop(StopSource::Serial), 20_000);
        c.command(Command::Start, 20_000);
        run(&mut c, 20_000, 23_500);
        assert_eq!(c.state(), State::Kicking);
        assert_eq!(c.command(Command::EndKick, 23_500), Reply::KickEnded);
        let (t, _) = run(&mut c, 23_500, 40_000).unwrap();
        assert_eq!(t, 23_500 + 4_762);
    }

    #[test]
    fn zero_kick_time_falls_right_after_reaching_the_kick() {
        let mut c = armed(1300, 3_000, 0);
        c.command(Command::Start, 2_000);
        assert_eq!(run(&mut c, 2_000, 5_000), Some((5_000, Event::KickReached { after_ms: 3_000 })));
        assert_eq!(c.update(5_001), Some(Event::KickEnded { held_ms: 1 }));
        let (t, e) = run(&mut c, 5_001, 20_000).unwrap();
        // 100 µs a 42 µs/s: 2381 ms.
        assert_eq!(t, 5_001 + 2_381);
        assert!(matches!(e, Event::Reached { target_us: 1300, .. }));
    }

    #[test]
    fn longer_ramp_and_kick_are_honoured() {
        let mut c = armed(1200, 3_000, 2_000);
        assert_eq!(c.command(Command::SetRamp(12_000), 2_000), Reply::Ramp { ramp_ms: 12_000 });
        assert_eq!(c.command(Command::SetKick(5_000), 2_000), Reply::Kick { kick_ms: 5_000 });
        c.command(Command::Start, 2_000);
        assert_eq!(run(&mut c, 2_000, 15_000), Some((14_000, Event::KickReached { after_ms: 12_000 })));
        assert_eq!(run(&mut c, 15_000, 19_001), Some((19_000, Event::KickEnded { held_ms: 5_000 })));
    }

    #[test]
    fn ramp_and_kick_settings_only_while_stopped_and_in_range() {
        let mut c = armed(1300, 3_000, 2_000);
        assert_eq!(c.command(Command::SetRamp(2_999), 2_000), Reply::Rejected(Reject::RampTooShort));
        assert_eq!(
            c.command(Command::SetRamp(MAX_RAMP_MS + 1), 2_000),
            Reply::Rejected(Reject::RampTooLong)
        );
        assert_eq!(
            c.command(Command::SetKick(MAX_KICK_MS + 1), 2_000),
            Reply::Rejected(Reject::KickTooLong)
        );
        assert_eq!(c.command(Command::SetKick(0), 2_000), Reply::Kick { kick_ms: 0 });
        c.command(Command::Start, 2_000);
        assert_eq!(c.command(Command::SetRamp(20_000), 2_001), Reply::Rejected(Reject::Running));
        assert_eq!(c.command(Command::SetKick(1_000), 2_001), Reply::Rejected(Reject::Running));
        assert_eq!(c.ramp_ms(), 3_000);
        assert_eq!(c.kick_ms(), 0);
    }

    #[test]
    fn stop_is_immediate_from_every_running_state_and_allows_a_new_start() {
        // Subida, chute, descida, regime e parada suave.
        for at in [3_000, 6_000, 8_000, 20_000] {
            let mut c = armed(1200, 3_000, 2_000);
            c.command(Command::Start, 2_000);
            run(&mut c, 2_000, at);
            if at == 20_000 {
                c.command(Command::SoftStop, at);
                assert_eq!(c.state(), State::Braking);
            }
            assert!(c.pulse_ns() > 1_148_000);
            assert_eq!(
                c.command(Command::Stop(StopSource::Serial), at),
                Reply::Stopped { was_running: true }
            );
            assert_eq!(c.state(), State::Stopped);
            assert_eq!(c.pulse_ns(), 1_000_000);
            run(&mut c, at, at + 1_000);
            assert_eq!(c.pulse_ns(), 1_000_000);
            assert_eq!(c.command(Command::Start, at + 1_000), Reply::Started { count: 2 });
            assert_eq!(c.pulse_ns(), 1_148_000);
            assert_eq!(c.command(Command::Start, at + 1_000), Reply::Rejected(Reject::Running));
        }
    }

    #[test]
    fn soft_stop_falls_at_the_adjust_rate_then_stops() {
        let (mut c, t) = started_and_holding(1320);
        assert_eq!(c.command(Command::SoftStop, t), Reply::SoftStop { was_running: true });
        assert_eq!(c.state(), State::Braking);
        // Repetir não replaneja; mudar o alvo também não.
        assert_eq!(c.command(Command::SoftStop, t), Reply::SoftStop { was_running: true });
        c.command(Command::SetTarget(1300), t);
        assert_eq!(c.state(), State::Braking);
        // 172 µs a 21 µs/s: 8191 ms.
        let (end, e) = run(&mut c, t, t + 20_000).unwrap();
        assert_eq!(end, t + 8_191);
        assert!(matches!(e, Event::SoftStopped { .. }));
        assert_eq!(c.state(), State::Stopped);
        assert_eq!(c.pulse_ns(), 1_000_000);
        assert_eq!(c.command(Command::SoftStop, end), Reply::SoftStop { was_running: false });
        assert_eq!(c.command(Command::Start, end), Reply::Started { count: 2 });
    }

    #[test]
    fn soft_stop_during_the_kick_falls_from_there() {
        let mut c = armed(1200, 3_000, 2_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 6_000);
        assert_eq!(c.state(), State::Kicking);
        c.command(Command::SoftStop, 6_000);
        // 252 µs a 21 µs/s: 12 s, sem passar pelo alvo.
        let (end, e) = run(&mut c, 6_000, 30_000).unwrap();
        assert_eq!(end, 18_000);
        assert_eq!(e, Event::SoftStopped { run_ms: 16_000 });
    }

    #[test]
    fn target_limits() {
        let mut c = armed(1200, 3_000, 2_000);
        assert_eq!(c.command(Command::SetTarget(1321), 2_000), Reply::Rejected(Reject::AboveCeiling));
        assert_eq!(c.command(Command::SetTarget(1400), 2_000), Reply::Rejected(Reject::AboveCeiling));
        assert_eq!(
            c.command(Command::SetTarget(1148), 2_000),
            Reply::Rejected(Reject::NotAboveMinimum)
        );
        assert_eq!(
            c.command(Command::SetTarget(1320), 2_000),
            Reply::Target {
                target_us: 1320,
                saturated: false
            }
        );
        assert_eq!(
            c.command(Command::NudgeTarget(5), 2_000),
            Reply::Target {
                target_us: 1320,
                saturated: true
            }
        );
        c.command(Command::SetTarget(1150), 2_000);
        assert_eq!(
            c.command(Command::NudgeTarget(-5), 2_000),
            Reply::Target {
                target_us: 1149,
                saturated: true
            }
        );
        // Mudar o alvo parado não mexe no pulso.
        assert_eq!(c.pulse_ns(), 1_000_000);
        assert_eq!(c.state(), State::Stopped);
    }

    #[test]
    fn a_target_set_during_the_start_only_moves_where_the_fall_ends() {
        let mut c = armed(1200, 3_000, 2_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 4_000);
        c.command(Command::SetTarget(1300), 4_000);
        assert_eq!(c.state(), State::Ramping);
        assert_eq!(run(&mut c, 4_000, 5_000), Some((5_000, Event::KickReached { after_ms: 3_000 })));
        c.command(Command::NudgeTarget(5), 6_000);
        assert_eq!(c.state(), State::Kicking);
        run(&mut c, 6_000, 7_000);
        // 95 µs a 42 µs/s: 2262 ms.
        let (t, e) = run(&mut c, 7_000, 20_000).unwrap();
        assert_eq!(t, 7_000 + 2_262);
        assert!(matches!(e, Event::Reached { target_us: 1305, .. }));
    }

    #[test]
    fn adjustments_while_running_use_the_adjust_rate_both_ways() {
        let (mut c, t) = started_and_holding(1250);
        // 21 µs/s: +21 µs levam 1 s.
        c.command(Command::SetTarget(1271), t);
        assert_eq!(c.state(), State::Ramping);
        let (t1, _) = run(&mut c, t, t + 5_000).unwrap();
        assert_eq!(t1, t + 1_000);

        c.command(Command::SetTarget(1229), t1);
        let (t2, e) = run(&mut c, t1, t1 + 5_000).unwrap();
        assert_eq!(t2, t1 + 2_000);
        assert_eq!(
            e,
            Event::Reached {
                target_us: 1229,
                after_ms: 2_000
            }
        );
    }

    #[test]
    fn a_target_change_during_the_fall_switches_to_the_adjust_rate() {
        let mut c = armed(1200, 3_000, 2_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 8_000);
        // Descida a 42 µs/s desde 7000 ms: 1358 µs.
        assert_eq!(c.pulse_ns(), 1_358_000);
        c.command(Command::SetTarget(1316), 8_000);
        // 42 µs a 21 µs/s: 2 s.
        let (t, e) = run(&mut c, 8_000, 20_000).unwrap();
        assert_eq!(t, 10_000);
        assert!(matches!(e, Event::Reached { target_us: 1316, after_ms: 2_000 }));
        // Alvo repetido não replaneja.
        c.command(Command::SetTarget(1250), t);
        run(&mut c, t, t + 1_000);
        let before = c.pulse_ns();
        c.command(Command::SetTarget(1250), t + 1_000);
        run(&mut c, t + 1_000, t + 1_001);
        assert_eq!(c.pulse_ns(), before - 21);
    }

    #[test]
    fn millisecond_counter_wraparound() {
        let t0 = u32::MAX - 5_000;
        let mut c = Controller::new(LIM, 1200, 3_000, 2_000, t0);
        assert_eq!(run(&mut c, t0, t0.wrapping_add(2_000)).map(|x| x.1), Some(Event::Armed));
        let t1 = t0.wrapping_add(2_000);
        c.command(Command::Start, t1);
        let (t, e) = run(&mut c, t1, t1.wrapping_add(3_000)).unwrap();
        assert_eq!(t, t1.wrapping_add(3_000));
        assert_eq!(e, Event::KickReached { after_ms: 3_000 });
        let (t, e) = run(&mut c, t, t1.wrapping_add(20_000)).unwrap();
        assert_eq!(t, t1.wrapping_add(9_762));
        assert!(matches!(e, Event::Reached { after_ms: 4_762, .. }));
        assert_eq!(c.running_ms(t), Some(9_762));
    }

    #[test]
    fn throttle_estimate() {
        let mut c = armed(1320, 3_000, 2_000);
        assert_eq!(c.throttle_permille(), 0);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 5_000);
        // (1400 − 1148) / (1832 − 1148) = 36,8 %
        assert_eq!(c.throttle_permille(), 368);
        run(&mut c, 5_000, 20_000);
        // (1320 − 1148) / 684 = 25,1 %
        assert_eq!(c.throttle_permille(), 251);
    }

    /// Sequências aleatórias de comandos e intervalos: nenhuma passa do chute,
    /// fica acima do teto de regime fora da partida ou por mais tempo que o
    /// limite, muda mais rápido que a inclinação máxima ou gira sem partida
    /// pelo botão.
    #[test]
    fn invariants_under_random_commands() {
        let mut seed = 0x2545_f491u32;
        let mut rnd = move || {
            seed ^= seed << 13;
            seed ^= seed >> 17;
            seed ^= seed << 5;
            seed
        };
        let max_rate = LIM.max_rate_ns_per_s() as u64;
        let above_ns = (LIM.kick_ns() - LIM.ceiling_ns()) as u64;
        let slowest_rise = rate(LIM.span_ns(), MAX_RAMP_MS) as u64;
        let slowest_fall = LIM.adjust_rate_ns_per_s().min(LIM.fall_rate_ns_per_s()) as u64;
        // Acima do teto: a subida mais lenta, o chute mais longo e a descida
        // mais lenta, com folga para os passos de até 59 ms do teste.
        let max_above_ms = above_ns * 1000 / slowest_rise
            + MAX_KICK_MS as u64
            + above_ns * 1000 / slowest_fall
            + 250;
        for _ in 0..200 {
            let mut t = rnd();
            let mut c = Controller::new(LIM, 1200, 3_000, 2_000, t);
            let mut started_since_stop = false;
            let mut above_ms = 0u64;
            for _ in 0..3_000 {
                let dt = rnd() % 60;
                t = t.wrapping_add(dt);
                let before = c.pulse_ns();
                let was_running = c.state().is_running();
                c.update(t);
                let after = c.pulse_ns();
                let allowed = max_rate * dt as u64 / 1000 + 1;
                if after > before {
                    assert!((after - before) as u64 <= allowed, "subiu {} em {dt} ms", after - before);
                }
                // Na descida também: só a chegada da parada suave salta, e
                // dentro do acelerador zero.
                if after < before && c.state().is_running() {
                    assert!((before - after) as u64 <= allowed, "desceu {} em {dt} ms", before - after);
                }
                if was_running && c.state() == State::Stopped {
                    assert!((before - LIM.ppm_min_ns()) as u64 <= allowed);
                }
                let cmd = match rnd() % 16 {
                    0 => Some(Command::Start),
                    1 => Some(Command::Stop(StopSource::Serial)),
                    2 => Some(Command::SetTarget((rnd() % 1200 + 900) as u16)),
                    3 | 4 => Some(Command::NudgeTarget((rnd() % 41) as i16 - 20)),
                    5 => Some(Command::SetRamp(rnd() % 40_000)),
                    6 => Some(Command::SetKick(rnd() % 7_000)),
                    7 => Some(Command::SoftStop),
                    8 => Some(Command::EndKick),
                    _ => None,
                };
                if let Some(cmd) = cmd {
                    let before = c.pulse_ns();
                    let reply = c.command(cmd, t);
                    match reply {
                        Reply::Started { .. } => {
                            started_since_stop = true;
                            above_ms = 0;
                        }
                        Reply::Stopped { .. } => started_since_stop = false,
                        _ => {}
                    }
                    // Um comando só sobe o pulso instantaneamente na partida,
                    // e só até o PPM mínimo (acelerador zero).
                    if c.pulse_ns() > before {
                        assert!(matches!(reply, Reply::Started { .. }));
                        assert_eq!(c.pulse_ns(), LIM.ppm_min_ns());
                    }
                }
                let p = c.pulse_ns();
                assert!(p >= LIM.stop_ns() && p <= LIM.kick_ns(), "pulso {p}");
                if p > LIM.ceiling_ns() {
                    above_ms += dt as u64;
                    assert!(above_ms <= max_above_ms, "{above_ms} ms acima do teto");
                    assert!(matches!(
                        c.state(),
                        State::Ramping | State::Kicking | State::Braking
                    ));
                }
                match c.state() {
                    State::Arming | State::Stopped => assert_eq!(p, LIM.stop_ns()),
                    _ => assert!(started_since_stop),
                }
            }
        }
    }
}
