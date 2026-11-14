//! Ensaio de bancada das três fitas HD107S (protocolo APA102) pela placa de
//! interface ponto a ponto (eletronica/interface/MONTAGEM-PONTO-A-PONTO.md).
//!
//! | Sinal    | ESP32-C3 | U1 (74AHCT125) | Destino                    |
//! |----------|----------|----------------|----------------------------|
//! | CLK      | GPIO4    | 2 → 3          | R6/R10/R11 33 Ω → 3 painéis |
//! | DATA P1  | GPIO6    | 5 → 6          | Painel 1                   |
//! | DATA P2  | GPIO5    | 9 → 8          | Painel 2                   |
//! | DATA P3  | GPIO7    | 12 → 11        | Painel 3                   |
//!
//! O clock é comum: os três painéis recebem o mesmo quadro bit a bit, cada
//! um com o seu DATA. Brilho global baixo (4/31): branco pleno ≈ 0,25 A por
//! fita, ≈ 0,75 A com as três.
//!
//! Sequência (repete):
//! 0. Identificação: P1 vermelho, P2 verde, P3 azul, um de cada vez e depois
//!    juntos. Cor no painel errado = DATA trocado.
//! 1. Contagem cumulativa nos três: o último LED aceso é onde a cadeia para.
//! 2. Matiz completa, painéis defasados de 1/3 de volta.
//! 3. Rampa de branco 0..255..0.

#![no_std]
#![no_main]

use esp_hal::{
    delay::Delay,
    gpio::{Level, Output, OutputConfig},
    main,
};
use esp_println::println;

esp_bootloader_esp_idf::esp_app_desc!();

/// LEDs por painel (ajuste se o trecho na bancada for diferente).
const NUM_LEDS: usize = 29;

/// Brilho global APA102 (0..=31). A intensidade fina é feita no RGB.
const BRIGHTNESS: u8 = 4;

/// Meio período do clock em µs (~250 kHz, folgado para fios longos).
const HALF_BIT_US: u32 = 1;

type Rgb = (u8, u8, u8);
const APAGADO: Rgb = (0, 0, 0);

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    println!("\n# PANICO: {info}");
    esp_hal::system::software_reset()
}

struct Fitas<'a> {
    clk: Output<'a>,
    data: [Output<'a>; 3],
    delay: Delay,
}

impl Fitas<'_> {
    /// Envia um quadro aos três painéis. `pixel(painel, i)` devolve o RGB.
    fn quadro(&mut self, pixel: impl Fn(usize, usize) -> Rgb) {
        for _ in 0..4 {
            self.byte([0x00; 3]);
        }
        for i in 0..NUM_LEDS {
            let c = [pixel(0, i), pixel(1, i), pixel(2, i)];
            self.byte([0xE0 | BRIGHTNESS; 3]);
            self.byte(c.map(|(_, _, b)| b));
            self.byte(c.map(|(_, g, _)| g));
            self.byte(c.map(|(r, _, _)| r));
        }
        // Fim: ≥ NUM_LEDS/2 bordas extras; 4 bytes cobrem até 64 LEDs.
        for _ in 0..4 {
            self.byte([0xFF; 3]);
        }
    }

    fn byte(&mut self, b: [u8; 3]) {
        for bit in (0..8).rev() {
            for (pino, v) in self.data.iter_mut().zip(b) {
                pino.set_level(if (v >> bit) & 1 == 1 { Level::High } else { Level::Low });
            }
            self.delay.delay_micros(HALF_BIT_US);
            self.clk.set_high();
            self.delay.delay_micros(HALF_BIT_US);
            self.clk.set_low();
        }
    }

    fn todos(&mut self, c: Rgb) {
        self.quadro(|_, _| c);
    }
}

#[main]
fn main() -> ! {
    let p = esp_hal::init(esp_hal::Config::default());
    let cfg = OutputConfig::default();
    let mut f = Fitas {
        clk: Output::new(p.GPIO4, Level::Low, cfg),
        data: [
            Output::new(p.GPIO6, Level::Low, cfg),
            Output::new(p.GPIO5, Level::Low, cfg),
            Output::new(p.GPIO7, Level::Low, cfg),
        ],
        delay: Delay::new(),
    };
    let d = Delay::new();

    println!(
        "TESTE-FITAS-C3: CLK=GPIO4, P1=GPIO6, P2=GPIO5, P3=GPIO7, {NUM_LEDS} LEDs/painel, brilho {BRIGHTNESS}/31"
    );
    f.todos(APAGADO);
    d.delay_millis(500);

    const ID: [Rgb; 3] = [(255, 0, 0), (0, 255, 0), (0, 0, 255)];

    loop {
        println!("0) IDENTIFICACAO: P1 vermelho, P2 verde, P3 azul");
        for alvo in 0..3 {
            println!("   so P{}", alvo + 1);
            f.quadro(|p, _| if p == alvo { ID[p] } else { APAGADO });
            d.delay_millis(2000);
        }
        println!("   os tres juntos");
        f.quadro(|p, _| ID[p]);
        d.delay_millis(3000);

        println!("1) CONTAGEM cumulativa 1..{NUM_LEDS}");
        for n in 1..=NUM_LEDS {
            f.quadro(|_, i| if i < n { (128, 128, 128) } else { APAGADO });
            d.delay_millis(150);
        }
        d.delay_millis(1000);

        println!("2) MATIZ");
        for h in (0..=255u16).step_by(2) {
            f.quadro(|p, _| matiz((h as u8).wrapping_add(85 * p as u8)));
            d.delay_millis(25);
        }

        println!("3) BRANCO 0..255..0");
        for v in (0..=255u16).step_by(5).chain((0..=255u16).rev().step_by(5)) {
            f.todos((v as u8, v as u8, v as u8));
            d.delay_millis(30);
        }

        println!("APAGADO");
        f.todos(APAGADO);
        d.delay_millis(1000);
    }
}

/// Matiz 0..=255 com saturação e valor plenos.
fn matiz(h: u8) -> Rgb {
    let regiao = h / 43;
    let resto = (h - regiao * 43) * 6;
    match regiao {
        0 => (255, resto, 0),
        1 => (255 - resto, 255, 0),
        2 => (0, 255, resto),
        3 => (0, 255 - resto, 255),
        4 => (resto, 0, 255),
        _ => (255, 0, 255 - resto),
    }
}
