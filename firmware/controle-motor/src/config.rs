//! Valores de bancada. Mudar aqui e regravar: nada disto muda em execução.
//!
//! Faixa PPM: `esc_blheli_s_2026-10-16/parametros-gravados.json`.
//! Armação, rampa e teto: esquema 05 §8.2.

use crate::controller::{Limits, MAX_RAMP_MS};

/// Sinal servo de 50 Hz (05 §8).
pub const PWM_FREQ_HZ: u32 = 50;
/// Resolução do LEDC: a 50 Hz, 16 bits dão passos de 0,305 µs.
pub const PWM_BITS: u32 = 16;

/// Pulso de armação e de parada. O BLHeli_S só arma vendo acelerador zero,
/// e qualquer pulso abaixo de [`PPM_MIN_US`] é zero.
pub const STOP_US: u16 = 1000;
/// PPM Min Throttle gravado no ESC em 16/10/2026. A rampa parte daqui, e não
/// de 1000 µs, para os 12 s serem todos de acelerador.
pub const PPM_MIN_US: u16 = 1148;
/// PPM Max Throttle gravado. Com "Programming by TX" ligado, o ESC que vê
/// acelerador máximo ao energizar entra em programação: o teto fica abaixo.
pub const PPM_MAX_US: u16 = 1832;

/// TETO (05 §8.2): o maior pulso que sai do LEDC.
///
/// O valor final é o pulso que dá 1800 RPM com o rotor completo, medido com
/// o tacômetro na tensão de fonte em uso; sem governor, o mesmo pulso gira
/// mais rápido com mais tensão. Até essa medição vale 1400 µs (37 % do
/// acelerador), uma estimativa abaixo de 1800 RPM: pelo modelo do 04
/// (1,96 V de força contraeletromotriz + 4,95 A × 0,221 Ω), 1800 RPM com o
/// rotor pedem ~44 % a 7 V, e 37 % dão ~1590 RPM a 7 V e ~1410 RPM a 6 V.
/// O motor sem rotor chega a ~2300 RPM a 7 V.
///
/// Calibração: com o tacômetro, subir em passos de no máximo 25 µs,
/// regravando, até 1800 RPM com o rotor; anotar o pulso e a tensão no
/// registro de ensaio e marcar [`CEILING_MEASURED`].
pub const CEILING_US: u16 = 1400;
/// Passa a `true` junto com o [`CEILING_US`] medido; enquanto for `false`,
/// o firmware avisa na energização.
pub const CEILING_MEASURED: bool = false;

/// RAMPA: do PPM mínimo ao teto em pelo menos 12 s (05 §8.2; 04 Bloqueador D).
pub const MIN_RAMP_MS: u32 = 12_000;
/// ARMAÇÃO: pulso de parada por ~2 s antes de qualquer comando.
pub const ARMING_MS: u32 = 2_000;

/// Alvo ao ligar: baixo, para o primeiro giro do motor sem rotor.
pub const INITIAL_TARGET_US: u16 = 1200;
/// Rampa de partida ao ligar.
pub const INITIAL_RAMP_MS: u32 = MIN_RAMP_MS;

/// Passos das teclas `+`/`-` e `>`/`<`, em µs.
pub const NUDGE_COARSE_US: i16 = 5;
pub const NUDGE_FINE_US: i16 = 1;

/// Filtro de repique: a parada reage mais rápido que a partida.
pub const START_DEBOUNCE_MS: u32 = 50;
pub const STOP_DEBOUNCE_MS: u32 = 10;

/// WATCHDOG: sem alimentação por este tempo, o chip reinicia por inteiro,
/// o LEDC para e o ESC desliga o motor (05 §8.2).
pub const WATCHDOG_MS: u64 = 500;

/// Registro na serial: uma linha por período, em giro e parado.
pub const LOG_RUNNING_MS: u32 = 200;
pub const LOG_IDLE_MS: u32 = 5_000;

pub const LIMITS: Limits = Limits {
    stop_us: STOP_US,
    ppm_min_us: PPM_MIN_US,
    ppm_max_us: PPM_MAX_US,
    ceiling_us: CEILING_US,
    min_ramp_ms: MIN_RAMP_MS,
    arming_ms: ARMING_MS,
};

const _: () = {
    assert!(LIMITS.is_valid());
    assert!(INITIAL_TARGET_US > PPM_MIN_US && INITIAL_TARGET_US <= CEILING_US);
    assert!(INITIAL_RAMP_MS >= MIN_RAMP_MS && INITIAL_RAMP_MS <= MAX_RAMP_MS);
    // O maior pulso cabe no período.
    assert!((PPM_MAX_US as u32) * PWM_FREQ_HZ < 1_000_000);
    assert!(PWM_BITS >= 14 && PWM_BITS <= 20);
    assert!(NUDGE_COARSE_US > 0 && NUDGE_COARSE_US <= 25 && NUDGE_FINE_US > 0);
    assert!(STOP_DEBOUNCE_MS <= START_DEBOUNCE_MS);
    // Folga sobre uma volta do laço (1 ms), sem deixar o motor sem dono.
    assert!(WATCHDOG_MS >= 100 && WATCHDOG_MS <= 1_000);
};
