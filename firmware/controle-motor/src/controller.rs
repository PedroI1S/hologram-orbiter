//! Máquina de estados do gerador: ARMAÇÃO, RAMPA, PARADA e TETO (05 §8.2).
//!
//! O pulso fica em nanossegundos para a rampa avançar frações de µs a cada
//! milissegundo sem acumular erro. Toda mudança em giro, para cima ou para
//! baixo, respeita a inclinação máxima — do PPM mínimo ao teto em
//! `min_ramp_ms` —, o que também evita desacelerar mais rápido que o arrasto
//! e devolver energia à fonte. A parada é a única mudança instantânea.

/// Rampa mais longa aceita pelo console.
pub const MAX_RAMP_MS: u32 = 300_000;

/// Faixa do sinal e tempos que o controlador nunca viola.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Limits {
    /// Pulso de armação e de parada, abaixo do PPM mínimo do ESC.
    pub stop_us: u16,
    /// Acelerador zero no ESC; a rampa parte daqui.
    pub ppm_min_us: u16,
    /// Acelerador máximo no ESC; nunca alcançado.
    pub ppm_max_us: u16,
    /// TETO: maior pulso que sai do LEDC.
    pub ceiling_us: u16,
    /// Do PPM mínimo ao teto em no mínimo este tempo.
    pub min_ramp_ms: u32,
    /// Pulso de parada mantido desde a energização antes de aceitar comandos.
    pub arming_ms: u32,
}

impl Limits {
    pub const fn is_valid(&self) -> bool {
        self.stop_us >= 900
            && self.stop_us < self.ppm_min_us
            && self.ppm_min_us < self.ceiling_us
            && self.ceiling_us < self.ppm_max_us
            && self.min_ramp_ms >= 12_000
            && self.min_ramp_ms <= MAX_RAMP_MS
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

    /// Do PPM mínimo ao teto, em ns.
    const fn span_ns(&self) -> u32 {
        (self.ceiling_us - self.ppm_min_us) as u32 * 1000
    }

    /// Maior inclinação permitida, em ns de pulso por segundo.
    pub const fn max_rate_ns_per_s(&self) -> u32 {
        rate(self.span_ns(), self.min_ramp_ms)
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
    /// Pulso a caminho do alvo.
    Ramping,
    /// Pulso no alvo.
    Holding,
}

impl State {
    pub const fn label(self) -> &'static str {
        match self {
            State::Arming => "ARMANDO",
            State::Stopped => "PARADO",
            State::Ramping => "RAMPA",
            State::Holding => "REGIME",
        }
    }

    pub const fn is_running(self) -> bool {
        matches!(self, State::Ramping | State::Holding)
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
    Stop(StopSource),
    /// Alvo absoluto, em µs.
    SetTarget(u16),
    /// Alvo relativo, em µs; satura no teto e logo acima do PPM mínimo.
    NudgeTarget(i16),
    /// Duração da rampa de partida, em ms.
    SetRamp(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Reply {
    Started { count: u32 },
    Stopped { was_running: bool },
    Target { target_us: u16, saturated: bool },
    Ramp { ramp_ms: u32 },
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
}

impl Reject {
    pub const fn message(self) -> &'static str {
        match self {
            Reject::Arming => "ainda armando o ESC",
            Reject::Running => "motor girando: pare antes",
            Reject::AboveCeiling => "acima do teto",
            Reject::NotAboveMinimum => "não passa do PPM mínimo; para parar use espaço ou p",
            Reject::RampTooShort => "rampa abaixo do mínimo",
            Reject::RampTooLong => "rampa acima do máximo",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Event {
    /// Fim da armação: o ESC viu o pulso de parada pelo tempo pedido.
    Armed,
    /// O pulso chegou ao alvo, `after_ms` depois do início do movimento.
    Reached { target_us: u16, after_ms: u32 },
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
    target_us: u16,
    ramp_ms: u32,
    starts: u32,
}

impl Controller {
    /// Começa armando, com o pulso de parada.
    pub fn new(lim: Limits, target_us: u16, ramp_ms: u32, now_ms: u32) -> Self {
        assert!(lim.is_valid());
        assert!(target_us > lim.ppm_min_us && target_us <= lim.ceiling_us);
        assert!(ramp_ms >= lim.min_ramp_ms && ramp_ms <= MAX_RAMP_MS);
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
            target_us,
            ramp_ms,
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
            State::Ramping => {
                self.advance(dt_ms);
                if self.pulse_ns != self.dest_ns {
                    return None;
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
                if self.state != State::Arming {
                    self.state = State::Stopped;
                }
                self.pulse_ns = self.lim.stop_ns();
                self.dest_ns = self.pulse_ns;
                self.carry = 0;
                Reply::Stopped { was_running }
            }
            Command::Start => match self.state {
                State::Arming => Reply::Rejected(Reject::Arming),
                State::Ramping | State::Holding => Reply::Rejected(Reject::Running),
                State::Stopped => {
                    self.starts += 1;
                    self.run_since_ms = now_ms;
                    // De 1000 a 1148 µs o ESC não vê diferença: o salto é
                    // dentro do acelerador zero, e a rampa inteira é útil.
                    self.pulse_ns = self.lim.ppm_min_ns();
                    let span_ns = self.target_ns() - self.pulse_ns;
                    self.begin_move(rate(span_ns, self.ramp_ms), now_ms);
                    Reply::Started { count: self.starts }
                }
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
        if self.state.is_running() && changed {
            // Ajuste em giro: inclinação de fundo de escala da rampa escolhida.
            // Alvo repetido não replaneja: a rampa em curso segue igual.
            self.begin_move(rate(self.lim.span_ns(), self.ramp_ms), now_ms);
        }
        Reply::Target {
            target_us: us,
            saturated,
        }
    }

    fn begin_move(&mut self, rate_ns_per_s: u32, now_ms: u32) {
        self.dest_ns = self.target_ns();
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

    /// Pulso a gerar agora, em ns, sempre entre o pulso de parada e o teto.
    pub fn pulse_ns(&self) -> u32 {
        self.pulse_ns
    }

    pub fn target_us(&self) -> u16 {
        self.target_us
    }

    pub fn ramp_ms(&self) -> u32 {
        self.ramp_ms
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
        ceiling_us: 1400,
        min_ramp_ms: 12_000,
        arming_ms: 2_000,
    };

    /// Controlador já armado em `t = 2000 ms`.
    fn armed(target_us: u16, ramp_ms: u32) -> Controller {
        let mut c = Controller::new(LIM, target_us, ramp_ms, 0);
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

    #[test]
    fn arming_holds_stop_pulse_and_refuses_start() {
        let mut c = Controller::new(LIM, 1200, 12_000, 0);
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
    fn stop_while_arming_keeps_arming() {
        let mut c = Controller::new(LIM, 1200, 12_000, 0);
        assert_eq!(
            c.command(Command::Stop(StopSource::Button), 10),
            Reply::Stopped { was_running: false }
        );
        assert_eq!(c.state(), State::Arming);
        assert_eq!(c.update(2_000), Some(Event::Armed));
    }

    #[test]
    fn start_ramps_linearly_from_ppm_min_to_target_in_ramp_time() {
        let mut c = armed(1400, 12_000);
        assert_eq!(c.command(Command::Start, 2_000), Reply::Started { count: 1 });
        assert_eq!(c.state(), State::Ramping);
        assert_eq!(c.pulse_ns(), 1_148_000);

        run(&mut c, 2_000, 8_000);
        let mid = c.pulse_ns() as i64;
        assert!((mid - 1_274_000).abs() <= 1_000, "meio da rampa: {mid}");

        let (t, e) = run(&mut c, 8_000, 20_000).unwrap();
        assert_eq!(t, 14_000);
        assert_eq!(
            e,
            Event::Reached {
                target_us: 1400,
                after_ms: 12_000
            }
        );
        assert_eq!(c.state(), State::Holding);
        assert_eq!(c.pulse_ns(), 1_400_000);
    }

    #[test]
    fn ramp_to_a_low_target_still_takes_the_whole_ramp_time() {
        let mut c = armed(1200, 12_000);
        c.command(Command::Start, 2_000);
        let (t, _) = run(&mut c, 2_000, 30_000).unwrap();
        // 52 µs em 12 s: 4333 ns/s arredondados para baixo, nunca mais curto.
        assert!((14_000..=14_010).contains(&t), "chegou em {t}");
    }

    #[test]
    fn longer_ramp_is_honoured() {
        let mut c = armed(1400, 12_000);
        assert_eq!(
            c.command(Command::SetRamp(30_000), 2_000),
            Reply::Ramp { ramp_ms: 30_000 }
        );
        c.command(Command::Start, 2_000);
        let (t, _) = run(&mut c, 2_000, 40_000).unwrap();
        assert_eq!(t, 32_000);
    }

    #[test]
    fn stop_is_immediate_from_any_running_state_and_allows_a_new_start() {
        let mut c = armed(1400, 12_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 5_000);
        assert!(c.pulse_ns() > 1_148_000);
        assert_eq!(
            c.command(Command::Stop(StopSource::Serial), 5_000),
            Reply::Stopped { was_running: true }
        );
        assert_eq!(c.state(), State::Stopped);
        assert_eq!(c.pulse_ns(), 1_000_000);
        run(&mut c, 5_000, 6_000);
        assert_eq!(c.pulse_ns(), 1_000_000);

        assert_eq!(c.command(Command::Start, 6_000), Reply::Started { count: 2 });
        assert_eq!(c.pulse_ns(), 1_148_000);
        run(&mut c, 6_000, 20_000);
        assert_eq!(c.command(Command::Start, 20_000), Reply::Rejected(Reject::Running));
        c.command(Command::Stop(StopSource::Button), 20_000);
        assert_eq!(c.pulse_ns(), 1_000_000);
    }

    #[test]
    fn target_limits() {
        let mut c = armed(1200, 12_000);
        assert_eq!(
            c.command(Command::SetTarget(1401), 2_000),
            Reply::Rejected(Reject::AboveCeiling)
        );
        assert_eq!(
            c.command(Command::SetTarget(1148), 2_000),
            Reply::Rejected(Reject::NotAboveMinimum)
        );
        assert_eq!(
            c.command(Command::SetTarget(1400), 2_000),
            Reply::Target {
                target_us: 1400,
                saturated: false
            }
        );
        assert_eq!(
            c.command(Command::NudgeTarget(5), 2_000),
            Reply::Target {
                target_us: 1400,
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
    fn adjustments_while_running_use_the_full_scale_rate_both_ways() {
        let mut c = armed(1300, 12_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 20_000);
        assert_eq!(c.pulse_ns(), 1_300_000);

        // 252 µs em 12 s = 21 µs/s: +21 µs levam 1 s.
        c.command(Command::SetTarget(1321), 20_000);
        assert_eq!(c.state(), State::Ramping);
        let (t, _) = run(&mut c, 20_000, 25_000).unwrap();
        assert_eq!(t, 21_000);

        c.command(Command::SetTarget(1279), 25_000);
        let (t, e) = run(&mut c, 25_000, 30_000).unwrap();
        assert_eq!(t, 27_000);
        assert_eq!(
            e,
            Event::Reached {
                target_us: 1279,
                after_ms: 2_000
            }
        );
    }

    #[test]
    fn repeating_the_target_mid_ramp_does_not_replan() {
        let mut c = armed(1300, 12_000);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 6_000);
        let before = c.pulse_ns();
        assert_eq!(
            c.command(Command::SetTarget(1300), 6_000),
            Reply::Target {
                target_us: 1300,
                saturated: false
            }
        );
        assert_eq!(c.pulse_ns(), before);
        let (t, e) = run(&mut c, 6_000, 20_000).unwrap();
        // A rampa de partida (152 µs em 12 s) segue, sem trocar de inclinação.
        assert!((14_000..=14_002).contains(&t), "chegou em {t}");
        assert!(matches!(e, Event::Reached { after_ms: 12_000..=12_002, .. }));

        // No teto, `+` satura sem replanejar.
        c.command(Command::Stop(StopSource::Serial), 20_000);
        c.command(Command::SetTarget(1400), 20_000);
        c.command(Command::Start, 20_000);
        run(&mut c, 20_000, 26_000);
        assert_eq!(
            c.command(Command::NudgeTarget(5), 26_000),
            Reply::Target {
                target_us: 1400,
                saturated: true
            }
        );
        let (_, e) = run(&mut c, 26_000, 40_000).unwrap();
        assert_eq!(
            e,
            Event::Reached {
                target_us: 1400,
                after_ms: 12_000
            }
        );
    }

    #[test]
    fn ramp_cannot_change_while_running_or_go_below_minimum() {
        let mut c = armed(1300, 12_000);
        assert_eq!(
            c.command(Command::SetRamp(11_999), 2_000),
            Reply::Rejected(Reject::RampTooShort)
        );
        assert_eq!(
            c.command(Command::SetRamp(MAX_RAMP_MS + 1), 2_000),
            Reply::Rejected(Reject::RampTooLong)
        );
        c.command(Command::Start, 2_000);
        assert_eq!(
            c.command(Command::SetRamp(20_000), 2_001),
            Reply::Rejected(Reject::Running)
        );
        assert_eq!(c.ramp_ms(), 12_000);
    }

    #[test]
    fn millisecond_counter_wraparound() {
        let t0 = u32::MAX - 5_000;
        let mut c = Controller::new(LIM, 1400, 12_000, t0);
        assert_eq!(run(&mut c, t0, t0.wrapping_add(2_000)).map(|x| x.1), Some(Event::Armed));
        let t1 = t0.wrapping_add(2_000);
        c.command(Command::Start, t1);
        let (t, e) = run(&mut c, t1, t1.wrapping_add(13_000)).unwrap();
        assert_eq!(t, t1.wrapping_add(12_000));
        assert!(matches!(e, Event::Reached { after_ms: 12_000, .. }));
        assert_eq!(c.running_ms(t), Some(12_000));
    }

    #[test]
    fn throttle_estimate() {
        let mut c = armed(1400, 12_000);
        assert_eq!(c.throttle_permille(), 0);
        c.command(Command::Start, 2_000);
        run(&mut c, 2_000, 20_000);
        // (1400 − 1148) / (1832 − 1148) = 36,8 %
        assert_eq!(c.throttle_permille(), 368);
    }

    /// Sequências aleatórias de comandos e intervalos: nenhuma passa do teto,
    /// sobe mais rápido que a rampa mínima ou gira sem partida pelo botão.
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
        for _ in 0..200 {
            let mut t = rnd();
            let mut c = Controller::new(LIM, 1200, 12_000, t);
            let mut started_since_stop = false;
            for _ in 0..2_000 {
                let dt = rnd() % 60;
                t = t.wrapping_add(dt);
                let before = c.pulse_ns();
                c.update(t);
                let after = c.pulse_ns();
                if after > before {
                    let allowed = max_rate * dt as u64 / 1000 + 1;
                    assert!((after - before) as u64 <= allowed, "subiu {} em {dt} ms", after - before);
                }
                let cmd = match rnd() % 12 {
                    0 => Some(Command::Start),
                    1 => Some(Command::Stop(StopSource::Serial)),
                    2 => Some(Command::SetTarget((rnd() % 1200 + 900) as u16)),
                    3 | 4 => Some(Command::NudgeTarget((rnd() % 41) as i16 - 20)),
                    5 => Some(Command::SetRamp(rnd() % 400_000)),
                    _ => None,
                };
                if let Some(cmd) = cmd {
                    let before = c.pulse_ns();
                    let reply = c.command(cmd, t);
                    match reply {
                        Reply::Started { .. } => started_since_stop = true,
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
                assert!(p >= LIM.stop_ns() && p <= LIM.ceiling_ns(), "pulso {p}");
                match c.state() {
                    State::Arming | State::Stopped => assert_eq!(p, LIM.stop_ns()),
                    State::Ramping | State::Holding => assert!(started_since_stop),
                }
            }
        }
    }
}
