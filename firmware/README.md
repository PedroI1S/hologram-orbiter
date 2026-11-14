# Firmware

Conjunto de firmwares em Rust (`no_std` sobre `esp-hal`) para bancada e
operação do **Hologram Orbiter v4.0**.

| Pasta | O que é | Estado em 14/11/2026 |
|---|---|---|
| `controle-motor/` | Lógica pura do gerador de sinal do ESC (armação, partida linear ou overshoot, teto, parada, botões, teclas). Testada no Mac com `cargo test`. | **Ativo** (exige revisão de parâmetros e calibração de `CEILING_US` para `AX-2810Q` + suspensão `v4.0`) |
| `esp32-base/` | Programa da ESP32 da base (`no_std`): liga `controle-motor` ao LEDC (50 Hz), botões, serial e watchdogs. | **Ativo** (última gravação de `30/10/2026` foi para ensaio sem aranha no antigo `A2212`) |
| `teste-fitas-c3/` | Ensaio de bancada das três fitas **HD107S** no **ESP32-C3 Super Mini** pela placa de interface **SPI Quad** ponto a ponto. | **Ativo em bancada** (substituiu `../legado/v3.0/teste-fitas-esp32-base.rs`) |

---

## 1. Requisitos vigentes na v4.0 (`AX-2810Q 750KV` + suspensão em paralelogramo)

A promoção para **v4.0** (14/11/2026, ver
[`../05-ESQUEMA-ELETRICO-v4.0.md`](../05-ESQUEMA-ELETRICO-v4.0.md) e
[`../Hologram_Orbiter_v4/CAD/parameters.json`](../Hologram_Orbiter_v4/CAD/parameters.json))
altera o motor para **`AX-2810Q 750KV`** (`Kt = 12,73 mN·m/A`,
`R_efetiva = 0,225 Ω/fase`) e adota a **base suspensa em paralelogramo**
(translação crítica em **`~263 RPM`**, modo *yaw* em **`~759 RPM`**).

O ESC foi gravado e conferido em [`../esc_blheli_s_2026-11-13/`](../esc_blheli_s_2026-11-13/registro.md)
com **`Startup Power = 0,50`**, **`Demag = High`**, **`Brake on stop = On`** e
PPM `1148–1832 µs`.

**Alterações pendentes no `controle-motor/src/config.rs` antes de girar o rotor completo v4.0:**

1. **Cruzamento rápido da crítica de `~263 RPM`:** subir de `1148 µs` ao alvo
   com taxa `≥ 300 RPM/s` ao cruzar `~200–350 RPM` (não permanecer próximo à
   ressonância de translação).
2. **Alvo mínimo sustentado `≥ 1200 µs`:** não sustentar regime abaixo de
   `~600 RPM`.
3. **Evitar a banda de *yaw* (`760–870 RPM`):** passar por ela sem permanecer em
   regime contínuo no modo solto (`12,66 Hz` sem amortecimento estrutural).
4. **Calibrar `CEILING_US` para o `AX-2810Q 750KV` com tacômetro:** a `750 KV`,
   `1800 RPM` ocorre em fração de acelerador mais alta que no antigo `920 KV`;
   conferir também o **sentido anti-horário** visto de cima antes de montar a
   aranha. Só marcar `CEILING_MEASURED = true` após medir pulso, tensão e RPM
   com o rotor completo.
5. **Parada rápida + barramento protegido:** `Brake on stop = On` força o ESC a
   atravessar `~263 RPM` rapidamente ao parar, mas devolve energia regenerativa à
   fonte de bancada (`10–12 V / 30 A`). **Grampo ou resistor de descarga no
   barramento do ESC é obrigatório** antes de testar com rotor.

*(Referência do modelo médio com `AX-2810Q`, `R_ef = 0,225 Ω` e `10–12 V`: o
perfil de chute legado de `1400 µs` daria `16,37–19,65 A` de fase parado e pico
de `1680–1959 RPM`, acima dos critérios do Bloqueador D de [`../04-PLANO-DE-ENSAIOS-v4.0.md`](../04-PLANO-DE-ENSAIOS-v4.0.md) — não usar sem revisão.)*

---

## 2. Ensaio de bancada das fitas SPI Quad (`teste-fitas-c3/`)

Firmware em `firmware/teste-fitas-c3/` para o **ESP32-C3 Super Mini** acionar as
três fitas **HD107S** (protocolo APA102) em paralelo pela perfboard ponto a ponto
([`../eletronica/interface/MONTAGEM-PONTO-A-PONTO.md`](../eletronica/interface/MONTAGEM-PONTO-A-PONTO.md)),
substituindo o teste antigo de ESP32 da base arquivado em
[`../legado/v3.0/teste-fitas-esp32-base.rs`](../legado/v3.0/teste-fitas-esp32-base.rs).

| Sinal | ESP32-C3 | `74AHCT125` (U1) | Destino |
|---|---|---|---|
| `CLK` (comum) | `GPIO4` | pino `2 → 3` | `R6/R10/R11 (33 Ω)` → Painéis 1, 2 e 3 |
| `DATA P1` | `GPIO6` | pino `5 → 6` | Painel 1 |
| `DATA P2` | `GPIO5` | pino `9 → 8` | Painel 2 |
| `DATA P3` | `GPIO7` | pino `12 → 11` | Painel 3 |

Parâmetros de segurança em bancada: `NUM_LEDS = 29`, brilho global `4/31`
(`~0,25 A` por fita em branco pleno, `~0,75 A` total), clock `~250 kHz`
(`HALF_BIT_US = 1`), executando: (0) identificação P1 vermelho / P2 verde / P3
azul, (1) contagem cumulativa, (2) matiz defasada `120°` e (3) rampa de branco.

Compilar e gravar no ESP32-C3:

```bash
cd firmware/teste-fitas-c3 && cargo run --release
```

---

## 3. Gerador de sinal do ESC (`controle-motor/` + `esp32-base/`)

Os valores de bancada ficam em [`controle-motor/src/config.rs`](controle-motor/src/config.rs).
Para mudar o teto e os pulsos fixos, editar e regravar. Perfil, alvo e tempos
podem ser ajustados pela serial (não persistem após reiniciar).

### Ligações (esquema `05 §8.1`)

| Sinal | Pino | Ligação |
|---|---|---|
| Sinal do ESC | `D25` | pull-down de `10 kΩ` ao GND |
| Partida | `D32` | botão ao GND, pull-up interno |
| Parada | `D33` | botão ao GND, pull-up interno |
| GND | `GND` | comum com o ESC e a fonte |
| Serial | micro-USB | `115200 8N1`: registro e teclas |

### Requisitos implementados (`05 §8.2`)

| Requisito | Como está feito | Verificado |
|---|---|---|
| ARMAÇÃO | `1000 µs` desde a configuração do LEDC; nada é aceito por `2 s` | testes; emulador; placa (`0.1.0`) |
| PARTIDA | botão `D32` ou `g` na serial. Linear (padrão): de `1148 µs` ao alvo em `≥ 3 s`. Overshoot (`o`): sobe ao chute em `≥ 3 s`, segura `2 s` (`0–5 s`; `k` encerra antes), desce ao alvo a `~34 µs/s`. `l` volta ao linear; perfil só muda sem giro | testes dos dois perfis e comandos |
| PARADA | na hora: botão `D33`, ou espaço/`p`/Esc/Ctrl-C na serial → `1000 µs`, a qualquer momento. Suave: `d` desce ao PPM mínimo a `~17 µs/s` e então `1000 µs` | testes; parada na hora na placa (`0.1.0`) |
| TETO | alvos limitados a `TARGET_MIN_US..CEILING_US`; `pwm::duty_for` satura a saída | testes de limites, rampas e saída PWM |
| WATCHDOG | dois: `TIMG0` e `RTC`, `500 ms`, reiniciando o chip inteiro (o pulso para) | emulador (`TIMG0`); placa (`W` reiniciou pelos dois) |
| REINÍCIO | após qualquer reinício: `1000 µs`, alvo padrão (`1200 µs`) e espera; nunca recomeça sozinho | emulador e placa (`0.1.0`) |

### Histórico de bancada da fase anterior (`v3.0`, `A2212 920KV`, 19–30/10/2026)

> **Atenção:** os registros abaixo são da fase `v3.0` (`A2212 920KV`, `0,221 Ω`
> e base rígida); servem apenas como histórico do código em `controle-motor/`.
> A última gravação (`30/10/2026`, `v0.3.0` com `CEILING_US = 1831 µs`) foi
> feita para ensaio sem aranha no antigo motor e **não está validada para o
> `AX-2810Q 750KV` nem para o rotor v4.0**.

- `19/10/2026` (`v0.1.0` / `v0.2.0`): rampa de `12 s` até `1200 µs` não partiu
  o `A2212` com rotor; exigiu chute de `1400 µs` a `10,4 V`. Em `27/10/2026`
  houve ruptura de braço da aranha `v3.0` durante frenagem automática da
  sequência (`../revisoes/2026-10-27-RELATO-FALHA-ARANHA-FRENAGEM.md`).
- `30/10/2026` (`v0.3.0`): adicionou partida linear por padrão e comando `g` pela
  serial (`cargo test` OK; gravada na ESP32 rev. `v3.1` em `/dev/cu.usbserial-A5069RR4`,
  primeiro com teto `1350 µs` e depois elevado a `1831 µs` para teste sem aranha).

---

## Instalação (uma vez por máquina)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install espup espflash --locked
espup install --targets esp32
```

O `espup` grava `~/export-esp.sh` com o ligador Xtensa no `PATH`. Em bash/zsh,
executar `. ~/export-esp.sh` antes de compilar para ESP32. (O `teste-fitas-c3`
usa alvo RISC-V do ESP32-C3.)

## Testar, compilar, gravar

Lógica pura no Mac (não precisa do ambiente Xtensa):

```bash
cd firmware/controle-motor && cargo test
```

Programa da placa base (`esp32`):

```bash
cd firmware/esp32-base && cargo build --release
espflash board-info --chip esp32
cd firmware/esp32-base && cargo run --release
```

Monitor com registro em log:

```bash
script -q ensaio.log espflash monitor --chip esp32 --monitor-baud 115200
```

Se o `espflash monitor` parar no carregador da ROM, `Ctrl+R` reinicia no
programa; `Ctrl+C` fecha o monitor (não para o motor — para parar use espaço,
`p` ou `d`). Evitar `screen`. Linhas `D;` registram `t_ms;estado;pulso_us;acel_%;alvo_us;giro_s`.

## Teclas (`esp32-base`)

| Tecla | Efeito |
|---|---|
| `g` | **dar partida** no perfil selecionado; aguarda armação e exige botão de parada solto |
| `l` | selecionar **linear** (padrão); só sem giro |
| `o` | selecionar **overshoot** (sobe ao chute e desce ao alvo); só sem giro |
| espaço, `p`, Esc, Ctrl-C | **parar na hora**, a qualquer momento |
| `d` | **parada suave**: desce ao acelerador zero e para |
| `k` | encerra o chute agora e desce ao alvo |
| `<numero>` Enter | alvo em `µs` (`TARGET_MIN_US..CEILING_US`) |
| `+` `-` / `>` `<` | alvo `±5 µs` / `±1 µs` |
| `r<N>` Enter | tempo de subida em `s` (`3` a `30`; só parado) |
| `c<N>` Enter | duração do chute no overshoot em `s` (`0` a `5`; só parado) |
| `s` / `h` `?` | estado (inclui botões) / ajuda |
| `W` | trava o laço de propósito (ensaio do watchdog) |

## Bancada, em etapas

Obedecer integralmente às regras de segurança de [`../04-PLANO-DE-ENSAIOS-v4.0.md`](../04-PLANO-DE-ENSAIOS-v4.0.md):

1. **Sem ESC:** gravar, conferir banner, `s` (botões), rampa e parada na serial e osciloscópio no `D25` (`1000 µs` parado, `20 ms` de período).
2. **ESC alimentado (`10–12 V`, `30 A`, grampo/resistor de descarga no barramento):** energizar ESC com `1000 µs` no `D25`.
3. **Motor `AX-2810Q` sem aranha, preso:** conferir partida, sentido **anti-horário visto de cima**, parada pelo botão/serial e watchdog (`W`).
4. **Com base suspensa (`C0` aprovado), rotor completo e contenção:** calibrar `CEILING_US` com tacômetro para `1800 RPM` na tensão real, verificando corrente/temperatura nos bloqueadores `A`/`B`/`D`, e só então fixar `CEILING_MEASURED = true`.

## Emulador

O programa `esp32-base` foi testado em QEMU (`qemu-system-xtensa -machine esp32`)
na versão `0.1.0` (boot, armação, teclas e `TIMG0`). As revisões `0.2.0` e
`0.3.0` não rodaram no emulador.
