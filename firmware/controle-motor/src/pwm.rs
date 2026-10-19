//! Pulso em ns para o duty do LEDC.

use crate::controller::Limits;

/// Duty do LEDC para um pulso, preso entre o pulso de parada e o teto.
///
/// É a última barreira antes do hardware: o firmware não escreve no LEDC por
/// outro caminho. No teto o arredondamento é para baixo, para o pulso gerado
/// nunca passar dele nem por uma fração de µs.
pub fn duty_for(pulse_ns: u32, lim: &Limits, freq_hz: u32, bits: u32) -> u32 {
    let scale = (1u64 << bits) * freq_hz as u64;
    let pulse = pulse_ns.clamp(lim.stop_ns(), lim.ceiling_ns()) as u64;
    let rounded = (pulse * scale + 500_000_000) / 1_000_000_000;
    let ceiling = lim.ceiling_ns() as u64 * scale / 1_000_000_000;
    rounded.min(ceiling) as u32
}

/// Pulso que um duty gera, em ns (para o registro).
pub fn pulse_ns_for(duty: u32, freq_hz: u32, bits: u32) -> u32 {
    let scale = (1u64 << bits) * freq_hz as u64;
    ((duty as u64 * 1_000_000_000 + scale / 2) / scale) as u32
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

    #[test]
    fn stop_pulse_at_50_hz_16_bits() {
        let d = duty_for(1_000_000, &LIM, 50, 16);
        assert_eq!(d, 3277);
        assert_eq!(pulse_ns_for(d, 50, 16), 1_000_061);
    }

    #[test]
    fn resolution_is_a_third_of_a_microsecond() {
        let a = duty_for(1_200_000, &LIM, 50, 16);
        let b = duty_for(1_200_400, &LIM, 50, 16);
        assert_eq!(b - a, 1);
    }

    #[test]
    fn output_never_leaves_stop_to_ceiling() {
        for pulse in [0, 500_000, 999_999, 1_400_001, 1_832_000, 2_000_000, u32::MAX] {
            let p = pulse_ns_for(duty_for(pulse, &LIM, 50, 16), 50, 16);
            assert!((999_000..=1_400_000).contains(&p), "{pulse} → {p}");
        }
        for pulse in (1_000_000..=1_400_000).step_by(37) {
            let p = pulse_ns_for(duty_for(pulse, &LIM, 50, 16), 50, 16);
            assert!(p <= 1_400_000);
            // meio passo (153 ns) arredondando; no teto, até um passo para baixo
            assert!((p as i64 - pulse as i64).abs() <= 306, "{pulse} → {p}");
        }
    }
}
