//! Filtro de repique dos botões de partida (D32) e parada (D33).
//!
//! O estado só muda depois de a leitura ficar estável pela janela inteira.
//! Começa como "pressionado": um botão preso ou segurado na energização
//! precisa ser solto antes de valer, e a partida nunca vem do boot.

pub struct Debouncer {
    stable: bool,
    raw: bool,
    since_ms: u32,
    window_ms: u32,
}

impl Debouncer {
    pub const fn new(window_ms: u32, now_ms: u32) -> Self {
        Self {
            stable: true,
            raw: true,
            since_ms: now_ms,
            window_ms,
        }
    }

    /// Recebe a leitura crua; devolve `true` só na borda de pressionar.
    pub fn update(&mut self, raw_pressed: bool, now_ms: u32) -> bool {
        if raw_pressed != self.raw {
            self.raw = raw_pressed;
            self.since_ms = now_ms;
            return false;
        }
        if self.raw != self.stable && now_ms.wrapping_sub(self.since_ms) >= self.window_ms {
            self.stable = self.raw;
            return self.stable;
        }
        false
    }

    /// Estado filtrado.
    pub fn pressed(&self) -> bool {
        self.stable
    }
}

/// O par de botões do operador.
pub struct Panel {
    start: Debouncer,
    stop: Debouncer,
}

/// O que os botões pedem nesta volta do laço.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Request {
    Start,
    Stop,
}

impl Panel {
    pub const fn new(start_window_ms: u32, stop_window_ms: u32, now_ms: u32) -> Self {
        Self {
            start: Debouncer::new(start_window_ms, now_ms),
            stop: Debouncer::new(stop_window_ms, now_ms),
        }
    }

    /// A parada vence: com ela pressionada, a partida é ignorada, inclusive a
    /// borda que chegar no mesmo instante.
    pub fn update(&mut self, start_raw: bool, stop_raw: bool, now_ms: u32) -> Option<Request> {
        let start_edge = self.start.update(start_raw, now_ms);
        let stop_edge = self.stop.update(stop_raw, now_ms);
        if stop_edge {
            Some(Request::Stop)
        } else if start_edge && !self.stop.pressed() {
            Some(Request::Start)
        } else {
            None
        }
    }

    pub fn start_pressed(&self) -> bool {
        self.start.pressed()
    }

    pub fn stop_pressed(&self) -> bool {
        self.stop.pressed()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn feed(d: &mut Debouncer, raw: bool, from: u32, to: u32) -> Vec<u32> {
        (from..to).filter(|&t| d.update(raw, t)).collect()
    }

    #[test]
    fn held_at_boot_needs_release_first() {
        let mut d = Debouncer::new(50, 0);
        assert!(feed(&mut d, true, 0, 1_000).is_empty());
        assert!(d.pressed());
        assert!(feed(&mut d, false, 1_000, 1_100).is_empty());
        assert!(!d.pressed());
        assert_eq!(feed(&mut d, true, 1_100, 1_200), vec![1_150]);
    }

    #[test]
    fn bounces_shorter_than_the_window_are_ignored() {
        let mut d = Debouncer::new(50, 0);
        feed(&mut d, false, 0, 100);
        for t in 100..400 {
            // repique: alterna a cada 20 ms
            assert!(!d.update((t / 20) % 2 == 0, t));
        }
        assert!(!d.pressed());
    }

    #[test]
    fn stop_wins_over_start() {
        let mut p = Panel::new(50, 10, 0);
        for t in 0..100 {
            assert_eq!(p.update(false, false, t), None);
        }
        // Os dois juntos: só a parada.
        let got: Vec<_> = (100..300).filter_map(|t| p.update(true, true, t)).collect();
        assert_eq!(got, vec![Request::Stop]);
        // Solta a parada com a partida ainda pressionada: nada (sem nova borda).
        let got: Vec<_> = (300..500).filter_map(|t| p.update(true, false, t)).collect();
        assert!(got.is_empty());
        // Solta e pressiona a partida de novo.
        (500..600).for_each(|t| assert_eq!(p.update(false, false, t), None));
        let got: Vec<_> = (600..700).filter_map(|t| p.update(true, false, t)).collect();
        assert_eq!(got, vec![Request::Start]);
    }

    #[test]
    fn stop_reacts_within_its_window() {
        let mut p = Panel::new(50, 10, 0);
        (0..100).for_each(|t| assert_eq!(p.update(false, false, t), None));
        let first = (100..200).find(|&t| p.update(false, true, t).is_some());
        assert_eq!(first, Some(110));
    }
}
