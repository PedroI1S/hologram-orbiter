//! Calibração temporária; restaurar o programa normal ao terminar.
#![no_std]
#![no_main]
use controle_motor::{config, pwm};
use esp_hal::{
    clock::CpuClock,
    gpio::{DriveMode, Input, InputConfig, Pull},
    ledc::{
        LSGlobalClkSource, Ledc, LowSpeed,
        channel::{self, ChannelHW, ChannelIFace},
        timer::{self, TimerIFace},
    },
    main,
    rtc_cntl::{Rtc, RwdtStage},
    time::{Duration, Instant, Rate},
    timer::timg::{MwdtStage, TimerGroup},
    uart::{self, Uart},
};
use esp_println::println;

esp_bootloader_esp_idf::esp_app_desc!();
const STOP_DUTY_PCT: u8 = 5;
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    esp_hal::system::software_reset()
}
fn raw_duty(us: u32) -> u32 {
    ((us as u64 * 65536 * 50 + 500000) / 1000000) as u32
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
    let duty = pwm::duty_for(lim.stop_ns(), &lim, config::PWM_FREQ_HZ, config::PWM_BITS);
    esc.set_duty_hw(duty);

    let stop_button = Input::new(
        peripherals.GPIO33,
        InputConfig::default().with_pull(Pull::Up),
    );

    let mut serial = Uart::new(peripherals.UART0, uart::Config::default())
        .unwrap()
        .with_rx(peripherals.GPIO3)
        .with_tx(peripherals.GPIO1);

    println!(
        "CAL pronto: 1000 us. H=max 1832 SOMENTE com fonte desligada; L=min 1136; p=1000; s=estado."
    );
    let mut mode = 0u8;
    let mut used = false;
    let mut since = Instant::now();
    loop {
        tg_wdt.feed();
        rtc.rwdt.feed();
        let mut b = [0u8];
        if serial.read_ready() && matches!(serial.read_buffered(&mut b), Ok(1)) {
            match b[0] {
                b'H' if !used && !stop_button.is_low() => {
                    used = true;
                    mode = 1;
                    since = Instant::now();
                    esc.set_duty_hw(raw_duty(1832));
                    println!(
                        "CAL MAX 1832 us; timeout 30 s. Energizar ESC, aguardar tons de maximo, enviar L."
                    );
                }
                b'L' if mode == 1 => {
                    mode = 2;
                    since = Instant::now();
                    esc.set_duty_hw(raw_duty(1136));
                    println!("CAL MIN 1136 us por 8 s; margem BLHeli cerca de 12 us.");
                }
                b'p' | b' ' | 27 | 3 => {
                    mode = 0;
                    esc.set_duty_hw(raw_duty(1000));
                    println!("CAL STOP 1000 us.");
                }
                b's' => println!(
                    "CAL modo={} (0=1000, 1=1832, 2=1136), max_usado={}",
                    mode, used
                ),
                _ => {}
            }
        }
        if stop_button.is_low()
            || (mode == 1 && since.elapsed() >= Duration::from_secs(30))
            || (mode == 2 && since.elapsed() >= Duration::from_secs(8))
        {
            if mode != 0 {
                println!(
                    "CAL retorno 1000 us. Conferir tons; software nao confirma gravacao no ESC."
                );
            }
            mode = 0;
            esc.set_duty_hw(raw_duty(1000));
        }
        let tick = Instant::now();
        while tick.elapsed() < Duration::from_millis(1) {}
    }
}
