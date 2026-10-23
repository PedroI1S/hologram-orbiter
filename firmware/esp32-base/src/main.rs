//! ESP32 da base: gerador do sinal do ESC (esquema 05 §8).
//!
//! | Sinal           | Pino | Ligação                                          |
//! |-----------------|------|--------------------------------------------------|
//! | Sinal do ESC    | D25  | pull-down de 10 kΩ ao GND                         |
//! | Partida         | D32  | botão ao GND, pull-up interno                     |
//! | Parada          | D33  | botão ao GND, pull-up interno                     |
//! | Serial          | USB  | 115200 8N1: registro e teclas (`h` mostra a ajuda) |
//!
//! A lógica fica em `controle-motor` e é testada no Mac; aqui só há a ligação
//! com o LEDC, os botões, a serial e o watchdog.
#![no_std]
#![no_main]
#![deny(
    clippy::mem_forget,
    reason = "mem::forget is generally not safe to do with esp_hal types, especially those \
    holding buffers for the duration of a data transfer."
)]

use core::fmt;

use controle_motor::{
    button::{Panel, Request},
    config,
    console::{self, Action, Console},
    controller::{Command, Controller, Event, Reply, StopSource},
    pwm,
};
use esp_hal::{
    clock::CpuClock,
    gpio::{DriveMode, Input, InputConfig, Pull},
    ledc::{
        LSGlobalClkSource, Ledc, LowSpeed,
        channel::{self, ChannelHW, ChannelIFace},
        timer::{self, TimerIFace},
    },
    main,
    rtc_cntl::{Rtc, RwdtStage, SocResetReason},
    time::{Duration, Instant, Rate},
    timer::timg::{MwdtStage, TimerGroup},
    uart::{self, Uart},
};
use esp_println::{print, println};

esp_bootloader_esp_idf::esp_app_desc!();

/// Duty inicial do canal, em %: o pulso de parada logo na configuração,
/// antes do valor exato.
const STOP_DUTY_PCT: u8 = (config::STOP_US as u32 * config::PWM_FREQ_HZ / 10_000) as u8;

/// Bytes da serial tratados por volta do laço de 1 ms.
const SERIAL_BYTES_PER_PASS: usize = 4;

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    // Reinício completo: o LEDC volta ao reset, o D25 cai no pull-down e o ESC
    // perde o sinal. No boot seguinte vale o REINÍCIO: 1000 µs e espera.
    println!("\n# PÂNICO: {info}");
    esp_hal::system::software_reset()
}

#[main]
fn main() -> ! {
    let peripherals = esp_hal::init(esp_hal::Config::default().with_cpu_clock(CpuClock::max()));

    // WATCHDOG primeiro: daqui em diante, travar é reiniciar. São dois,
    // independentes: o do grupo de timers (clock do APB) e o do RTC
    // (oscilador lento). Os dois reiniciam o chip inteiro, LEDC incluído.
    let timg0 = TimerGroup::new(peripherals.TIMG0);
    let mut tg_wdt = timg0.wdt;
    tg_wdt.set_timeout(
        MwdtStage::Stage0,
        Duration::from_millis(config::WATCHDOG_MS),
    );
    tg_wdt.enable();
    let mut rtc = Rtc::new(peripherals.RTC_TIMER);
    rtc.rwdt.set_timeout(
        RwdtStage::Stage0,
        Duration::from_millis(config::WATCHDOG_MS),
    );
    rtc.rwdt.enable();

    // Sinal do ESC: 50 Hz, 16 bits, já no pulso de parada.
    let mut ledc = Ledc::new(peripherals.LEDC);
    ledc.set_global_slow_clock(LSGlobalClkSource::APBClk);
    let mut pwm_timer = ledc.timer::<LowSpeed>(timer::Number::Timer0);
    pwm_timer
        .configure(timer::config::Config {
            duty: timer::config::Duty::Duty16Bit,
            clock_source: timer::LSClockSource::APBClk,
            frequency: Rate::from_hz(config::PWM_FREQ_HZ),
        })
        .unwrap();
    let mut esc = ledc.channel(channel::Number::Channel0, peripherals.GPIO25);
    esc.configure(channel::config::Config {
        timer: &pwm_timer,
        duty_pct: STOP_DUTY_PCT,
        drive_mode: DriveMode::PushPull,
    })
    .unwrap();

    let lim = config::LIMITS;
    let mut duty = pwm::duty_for(lim.stop_ns(), &lim, config::PWM_FREQ_HZ, config::PWM_BITS);
    esc.set_duty_hw(duty);

    let start_button = Input::new(
        peripherals.GPIO32,
        InputConfig::default().with_pull(Pull::Up),
    );
    let stop_button = Input::new(
        peripherals.GPIO33,
        InputConfig::default().with_pull(Pull::Up),
    );

    let mut serial = Uart::new(peripherals.UART0, uart::Config::default())
        .unwrap()
        .with_rx(peripherals.GPIO3)
        .with_tx(peripherals.GPIO1);

    banner();

    let t0 = now_ms();
    let mut ctl = Controller::new(
        lim,
        config::INITIAL_TARGET_US,
        config::INITIAL_RAMP_MS,
        config::INITIAL_KICK_MS,
        t0,
    );
    let mut panel = Panel::new(config::START_DEBOUNCE_MS, config::STOP_DEBOUNCE_MS, t0);
    let mut console = Console::new(config::NUDGE_COARSE_US, config::NUDGE_FINE_US);
    let mut next_log = t0;
    let mut logged_state = ctl.state();
    let mut tick = Instant::now();

    loop {
        tg_wdt.feed();
        rtc.rwdt.feed();
        let now = now_ms();

        if let Some(request) = panel.update(start_button.is_low(), stop_button.is_low(), now) {
            let command = match request {
                Request::Start => Command::Start,
                Request::Stop => Command::Stop(StopSource::Button),
            };
            apply(&mut ctl, command, now);
        }

        // Poucos bytes por volta: cada resposta trava na impressão, e uma
        // colagem longa não pode segurar o laço até o watchdog.
        let mut byte = [0u8];
        for _ in 0..SERIAL_BYTES_PER_PASS {
            if !serial.read_ready() {
                break;
            }
            // Erro de recepção (ruído, estouro): o byte é descartado.
            if !matches!(serial.read_buffered(&mut byte), Ok(1)) {
                continue;
            }
            let was_editing = console.is_editing();
            let action = console.feed(byte[0], now);
            if was_editing && !console.is_editing() {
                println!();
            }
            if let Some(action) = action {
                handle(action, &mut ctl, &panel, now);
            }
        }
        if let Some(action) = console.poll(now) {
            println!();
            handle(action, &mut ctl, &panel, now);
        }

        match ctl.update(now) {
            Some(Event::Armed) => println!(
                "# armado: {} µs por {} s; partida pelo botão D32",
                lim.stop_us,
                lim.arming_ms / 1000
            ),
            Some(Event::KickReached { after_ms }) => println!(
                "# CHUTE em {} µs após {} s de subida; dura {} s (k encerra antes)",
                lim.kick_us,
                Tenths(after_ms / 100),
                Tenths(ctl.kick_ms() / 100)
            ),
            Some(Event::KickEnded { held_ms }) => println!(
                "# fim do chute após {} s: descendo a {} µs",
                Tenths(held_ms / 100),
                ctl.target_us()
            ),
            Some(Event::Reached {
                target_us,
                after_ms,
            }) => println!(
                "# REGIME em {target_us} µs: {} s de movimento, {} s desde a partida",
                Tenths(after_ms / 100),
                Tenths(ctl.running_ms(now).unwrap_or(0) / 100)
            ),
            Some(Event::SoftStopped { run_ms }) => println!(
                "# PARADO (parada suave) após {} s de giro",
                Tenths(run_ms / 100)
            ),
            None => {}
        }

        // Fora da configuração, o LEDC só é escrito aqui, sempre por `duty_for`,
        // que prende o pulso no chute.
        let wanted = pwm::duty_for(ctl.pulse_ns(), &lim, config::PWM_FREQ_HZ, config::PWM_BITS);
        if wanted != duty {
            duty = wanted;
            esc.set_duty_hw(duty);
        }

        // Registro no período, e já na volta em que o estado muda.
        let due = now.wrapping_sub(next_log) as i32 >= 0 || ctl.state() != logged_state;
        if due && !console.is_editing() {
            log_line(&ctl, duty, now);
            logged_state = ctl.state();
            next_log = now.wrapping_add(if ctl.state().is_running() {
                config::LOG_RUNNING_MS
            } else {
                config::LOG_IDLE_MS
            });
        }

        while tick.elapsed() < Duration::from_millis(1) {}
        tick = Instant::now();
    }
}

fn now_ms() -> u32 {
    Instant::now().duration_since_epoch().as_millis() as u32
}

fn banner() {
    println!();
    println!("# ESP32 da base: gerador do ESC, {}", env!("CARGO_PKG_VERSION"));
    let reason = esp_hal::system::reset_reason();
    println!("# reinício: {reason:?}");
    if matches!(
        reason,
        Some(
            SocResetReason::CoreSw
                | SocResetReason::Cpu0Sw
                | SocResetReason::CoreMwdt0
                | SocResetReason::CoreMwdt1
                | SocResetReason::CpuMwdt0
                | SocResetReason::CoreRtcWdt
                | SocResetReason::Cpu0RtcWdt
                | SocResetReason::SysRtcWdt
                | SocResetReason::SysBrownOut
        )
    ) {
        println!("# ATENÇÃO: reinício por pânico, watchdog ou queda de tensão; ver acima");
    }
    let lim = config::LIMITS;
    println!(
        "# ESC: PPM {}–{} µs · parada {} µs · {} Hz",
        lim.ppm_min_us,
        lim.ppm_max_us,
        lim.stop_us,
        config::PWM_FREQ_HZ
    );
    println!(
        "# teto de regime {} µs{} · watchdog {} ms",
        lim.ceiling_us,
        if config::CEILING_MEASURED {
            ""
        } else {
            " (ESTIMADO, não medido com tacômetro)"
        },
        config::WATCHDOG_MS
    );
    println!(
        "# partida: subida de {} s ao chute de {} µs, chute de {} s, descida a {} µs/s",
        Tenths(config::INITIAL_RAMP_MS / 100),
        lim.kick_us,
        Tenths(config::INITIAL_KICK_MS / 100),
        lim.fall_rate_ns_per_s() / 1000
    );
    println!(
        "# ajustes em giro e parada suave (d) a {} µs/s; espaço, p e D33 param na hora",
        lim.adjust_rate_ns_per_s() / 1000
    );
    println!(
        "# armando: {} µs por {} s",
        lim.stop_us,
        lim.arming_ms / 1000
    );
    println!("{}", console::HELP);
    println!("# D;t_ms;estado;pulso_us;acel_%;alvo_us;giro_s");
}

/// Aplica um comando e conta o que aconteceu.
fn apply(ctl: &mut Controller, command: Command, now: u32) {
    let pulse_before = ctl.pulse_ns();
    let running_before = ctl.running_ms(now);
    match ctl.command(command, now) {
        Reply::Started { count } => println!(
            "# PARTIDA {count}: de {} a {} µs (chute) em {} s, chute de {} s, depois {} µs",
            ctl.limits().ppm_min_us,
            ctl.limits().kick_us,
            Tenths(ctl.ramp_ms() / 100),
            Tenths(ctl.kick_ms() / 100),
            ctl.target_us()
        ),
        Reply::Stopped { was_running } => {
            let Command::Stop(source) = command else {
                return;
            };
            match (was_running, running_before) {
                (true, Some(run_ms)) => println!(
                    "# PARADO {} em {} µs, após {} s de giro",
                    source.label(),
                    Tenths((pulse_before + 50) / 100),
                    Tenths(run_ms / 100)
                ),
                _ if source == StopSource::Serial => println!("# já parado"),
                _ => {}
            }
        }
        Reply::Target {
            target_us,
            saturated,
        } => println!(
            "# alvo {target_us} µs{}",
            if saturated { " (no limite)" } else { "" }
        ),
        Reply::SoftStop { was_running: true } => println!(
            "# PARADA SUAVE em {} µs: descendo ao acelerador zero a {} µs/s",
            Tenths((pulse_before + 50) / 100),
            ctl.limits().adjust_rate_ns_per_s() / 1000
        ),
        Reply::SoftStop { was_running: false } => println!("# já parado"),
        Reply::KickEnded => println!(
            "# chute encerrado pela tecla em {} µs: descendo a {} µs",
            Tenths((pulse_before + 50) / 100),
            ctl.target_us()
        ),
        Reply::Ramp { ramp_ms } => println!("# subida até o chute: {} s", ramp_ms / 1000),
        Reply::Kick { kick_ms } => println!("# chute: {} s", kick_ms / 1000),
        Reply::Rejected(reject) => println!("# recusado: {}", reject.message()),
    }
}

fn handle(action: Action, ctl: &mut Controller, panel: &Panel, now: u32) {
    match action {
        Action::Command(command) => apply(ctl, command, now),
        Action::Echo(0x08) => print!("\x08 \x08"),
        Action::Echo(byte) => print!("{}", byte as char),
        Action::Status => status(ctl, panel),
        Action::Help => println!("{}", console::HELP),
        Action::Error(why) => println!("# {why}"),
        Action::Freeze => {
            println!(
                "# ensaio do WATCHDOG: laço travado; reinício em {} ms",
                config::WATCHDOG_MS
            );
            #[allow(clippy::empty_loop)]
            loop {}
        }
    }
}

fn status(ctl: &Controller, panel: &Panel) {
    let lim = ctl.limits();
    let pressed = |p: bool| if p { "pressionado" } else { "solto" };
    println!(
        "# {} · pulso {} µs · alvo {} µs · subida {} s · chute {} µs por {} s · teto {} µs{} · partidas {}",
        ctl.state().label(),
        Tenths((ctl.pulse_ns() + 50) / 100),
        ctl.target_us(),
        ctl.ramp_ms() / 1000,
        lim.kick_us,
        ctl.kick_ms() / 1000,
        lim.ceiling_us,
        if config::CEILING_MEASURED {
            ""
        } else {
            " (estimado)"
        },
        ctl.starts()
    );
    println!(
        "# botões: partida {}, parada {}",
        pressed(panel.start_pressed()),
        pressed(panel.stop_pressed())
    );
}

/// Linha de registro: separador `;` e vírgula decimal, como no resto do projeto.
fn log_line(ctl: &Controller, duty: u32, now: u32) {
    let pulse_ns = pwm::pulse_ns_for(duty, config::PWM_FREQ_HZ, config::PWM_BITS);
    print!(
        "D;{now};{};{};{};{};",
        ctl.state().label(),
        Tenths((pulse_ns + 50) / 100),
        Tenths(ctl.throttle_permille()),
        ctl.target_us()
    );
    match ctl.running_ms(now) {
        Some(ms) => println!("{}", Tenths(ms / 100)),
        None => println!(),
    }
}

/// Valor em décimos, impresso com vírgula: `Tenths(12345)` → `1234,5`.
struct Tenths(u32);

impl fmt::Display for Tenths {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{},{}", self.0 / 10, self.0 % 10)
    }
}
