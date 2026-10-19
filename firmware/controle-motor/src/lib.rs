//! Lógica do gerador de sinal do ESC na ESP32 da base (esquema 05 §8.2).
//!
//! Nada aqui toca em hardware: roda no Mac com `cargo test`. O firmware em
//! `../esp32-base` só liga estas peças ao LEDC, aos botões e à serial.
//!
//! - [`config`]: os valores de bancada (teto, rampa, faixa do ESC).
//! - [`controller`]: armação, rampa, regime e parada.
//! - [`button`]: filtro de repique dos botões.
//! - [`console`]: teclas da serial.
//! - [`pwm`]: pulso em ns para o duty do LEDC.
#![cfg_attr(not(test), no_std)]

pub mod button;
pub mod config;
pub mod console;
pub mod controller;
pub mod pwm;
