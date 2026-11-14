//! Teste de bancada das fitas HD107S (protocolo APA102) — temporário.
//!
//! | Sinal | Pino | Ligação                          |
//! |-------|------|----------------------------------|
//! | CLK   | D18  | 330 Ω → CI da fita               |
//! | DATA  | D23  | 330 Ω → DI da fita               |
//!
//! Alimentação da fita vem da fonte de bancada (5 V, limite 1 A), com GND
//! comum com a placa. Não usar o 5 V do USB para o painel.
//!
//! Sequência: matiz completa em quatro intensidades, rampa de branco e as
//! sete cores primárias/secundárias em dois níveis. Restaurar o programa
//! normal do motor ao terminar o ensaio.

#![no_std]
#![no_main]

use esp_hal::{
    delay::Delay,
    gpio::{Level, Output, OutputConfig},
    main,
    uart::{self, Uart},
};
use esp_println::println;

esp_bootloader_esp_idf::esp_app_desc!();

/// LEDs do trecho em teste: 29 na seção que está na bancada.
const NUM_LEDS: usize = 29;

/// Meio período do clock, em µs. 1 µs ≈ 250 kHz, muito abaixo do limite de 30 MHz.
const HALF_BIT_US: u32 = 1;

/// Brilho global (0..=31). 8 ≈ 26 % do branco pleno: ~0,45 A no trecho de 29.
/// A intensidade fina é feita no RGB, não neste campo.
const BRIGHTNESS: u8 = 8;

/// Níveis de intensidade da varredura de matiz.
const HUE_LEVELS: [u8; 4] = [64, 128, 192, 255];

/// Cores primárias e secundárias, mais o branco.
const CORES: [(u8, u8, u8); 7] = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 255),
];

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    println!("\n# PÂNICO: {info}");
    esp_hal::system::software_reset()
}

#[main]
fn main() -> ! {
    let peripherals = esp_hal::init(esp_hal::Config::default());

    // Serial só para acompanhar o ensaio; não há entrada de teclas.
    let _serial = Uart::new(peripherals.UART0, uart::Config::default())
        .unwrap()
        .with_rx(peripherals.GPIO3)
        .with_tx(peripherals.GPIO1);

    let mut clk = Output::new(peripherals.GPIO18, Level::Low, OutputConfig::default());
    let mut data = Output::new(peripherals.GPIO23, Level::Low, OutputConfig::default());
    let delay = Delay::new();

    println!(
        "TESTE-FITAS: D18=CLK, D23=DATA, {NUM_LEDS} LEDs, brilho global {BRIGHTNESS}/31, clock ~250 kHz"
    );

    loop {
        // 0) Contagem cumulativa: o último LED que acender é onde a cadeia para.
        for n in 1..=NUM_LEDS {
            frame(&mut clk, &mut data, &delay, |i| {
                if i < n { (128, 128, 128) } else { (0, 0, 0) }
            });
            delay.delay_millis(200);
        }
        delay.delay_millis(500);

        // 1) Matiz completa, do vermelho ao magenta, em quatro intensidades.
        for &level in HUE_LEVELS.iter() {
            println!("MATIZ nivel {level}/255");
            for h in (0..=255u16).step_by(4) {
                let (r, g, b) = hue_to_rgb(h as u8);
                let (r, g, b) = escala((r, g, b), level);
                frame(&mut clk, &mut data, &delay, |_| (r, g, b));
                delay.delay_millis(35);
            }
        }

        // 2) Branco: rampa de 0 a 255 e de volta.
        println!("BRANCO rampa 0..255..0");
        for v in (0..=255u16).step_by(8) {
            frame(&mut clk, &mut data, &delay, |_| (v as u8, v as u8, v as u8));
            delay.delay_millis(60);
        }
        for v in (0..=255u16).rev().step_by(8) {
            frame(&mut clk, &mut data, &delay, |_| (v as u8, v as u8, v as u8));
            delay.delay_millis(60);
        }

        // 3) As sete cores, cada uma em meio brilho e em brilho pleno.
        for &level in [128u8, 255u8].iter() {
            for &(r, g, b) in CORES.iter() {
                let (r, g, b) = escala((r, g, b), level);
                frame(&mut clk, &mut data, &delay, |_| (r, g, b));
                delay.delay_millis(500);
            }
        }

        println!("APAGADO");
        frame(&mut clk, &mut data, &delay, |_| (0, 0, 0));
        delay.delay_millis(800);
    }
}

/// Matiz em 0..=255, saturação e valor plenos.
fn hue_to_rgb(h: u8) -> (u8, u8, u8) {
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

/// Escala o RGB por um nível de 0 a 255.
fn escala((r, g, b): (u8, u8, u8), level: u8) -> (u8, u8, u8) {
    let s = |v: u8| ((v as u16 * level as u16) / 255) as u8;
    (s(r), s(g), s(b))
}

/// Envia um quadro APA102 completo. `pixel` devolve (R, G, B) por índice.
fn frame<F>(clk: &mut Output<'_>, data: &mut Output<'_>, delay: &Delay, pixel: F)
where
    F: Fn(usize) -> (u8, u8, u8),
{
    // Quadro de início: 32 bits em zero.
    for _ in 0..4 {
        write_byte(clk, data, delay, 0x00);
    }

    for i in 0..NUM_LEDS {
        let (r, g, b) = pixel(i);
        // 0b111 + 5 bits de brilho global, depois B, G, R (ordem APA102).
        write_byte(clk, data, delay, 0b1110_0000 | BRIGHTNESS);
        write_byte(clk, data, delay, b);
        write_byte(clk, data, delay, g);
        write_byte(clk, data, delay, r);
    }

    // Quadro de fim: bits em 1; quatro bytes bastam para 29 LEDs.
    for _ in 0..4 {
        write_byte(clk, data, delay, 0xFF);
    }
}

/// Bit-bang MSB primeiro: dados estáveis antes da borda de subida do clock.
fn write_byte(clk: &mut Output<'_>, data: &mut Output<'_>, delay: &Delay, byte: u8) {
    for bit in (0..8).rev() {
        if (byte >> bit) & 1 == 1 {
            data.set_high();
        } else {
            data.set_low();
        }
        delay.delay_micros(HALF_BIT_US);

        clk.set_high();
        delay.delay_micros(HALF_BIT_US);
        clk.set_low();
    }
}
