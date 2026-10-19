# Firmware

**ESP32 da base: gerador do sinal do ESC** (esquema 05 §8), em Rust `no_std`
sobre o `esp-hal` 1.2. Escrito e gravado em 19/10/2026 na ESP32 da base
(revisão v3.1, dois núcleos), com a fonte do ESC desligada: armação, teclas,
botões (por jumper ao GND) e watchdog conferidos na placa. **Ainda não foi
ensaiado com o ESC.**

| Pasta | O que é |
|---|---|
| `controle-motor/` | Toda a lógica (armação, rampa, teto, parada, botões, teclas), sem hardware. Testada no Mac com `cargo test`. |
| `esp32-base/` | O programa da placa: liga a lógica ao LEDC, aos botões, à serial e aos watchdogs. |

Os valores de bancada ficam em [`controle-motor/src/config.rs`](controle-motor/src/config.rs).
Nada muda em execução: para mudar o teto, editar e regravar.

## Ligações

Como no 05 §8.1, com os nomes impressos na placa:

| Sinal | Pino | Ligação |
|---|---|---|
| Sinal do ESC | D25 | pull-down de 10 kΩ ao GND |
| Partida | D32 | botão ao GND, pull-up interno |
| Parada | D33 | botão ao GND, pull-up interno |
| GND | GND | comum com o ESC e a fonte |
| Serial | micro-USB | 115200 8N1: registro e teclas |

## O que o firmware faz (05 §8.2)

| Requisito | Como está feito | Verificado |
|---|---|---|
| ARMAÇÃO | 1000 µs desde a configuração do LEDC; nada é aceito por 2 s | testes; emulador; placa |
| RAMPA | só pelo botão D32; linear no comando, de 1148 µs (PPM mínimo do ESC) ao alvo em ≥ 12 s | testes (12,0 s, 21 µs/s até 1400 µs); emulador; placa (4,33 µs/s até 1200 µs) |
| PARADA | botão D33, ou espaço/`p`/Esc/Ctrl-C na serial: 1000 µs na hora, a qualquer momento | testes; emulador (serial); placa (botão) |
| TETO | todo pulso passa por `pwm::duty_for`, que prende entre 1000 µs e o teto, arredondando para baixo no teto | testes |
| WATCHDOG | dois: o do grupo de timers TIMG0 e o do RTC, 500 ms, os dois reiniciando o chip inteiro (o LEDC para e o pulso some) | emulador (TIMG0); placa: `W` reiniciou pelos dois |
| REINÍCIO | depois de qualquer reinício: 1000 µs, alvo padrão (1200 µs) e espera; a rampa nunca recomeça sozinha | emulador (travamento e pânico); placa |
| PÁGINA | não existe ainda; a serial ajusta o alvo e para, mas nunca dá partida | teste das 256 teclas |

Além do pedido:

- **Ajustes em giro** (novo alvo, `+`/`-`) andam na inclinação de fundo de
  escala, nos dois sentidos: 252 µs em 12 s = 21 µs/s com o teto atual.
  Descer devagar mantém o motor tracionando, sem devolver energia à fonte
  (o BLHeli_S freia ativamente quando o acelerador cai rápido).
- **Pânico** imprime a causa e reinicia; o boot seguinte mostra o motivo
  (`CoreSw`, `CoreMwdt0`, `SysRtcWdt`...) e avisa.
- Um botão pressionado na energização precisa ser solto antes de valer.
  Com a parada pressionada, a partida é ignorada.

### Pontos a ratificar

1. **A rampa parte de 1148 µs, não de 1000 µs.** Abaixo do PPM Min Throttle
   gravado (1148 µs) o ESC vê acelerador zero; partindo de 1000 µs até um
   alvo perto de 1400 µs, os primeiros ~4,4 s dos 12 s seriam mortos e a
   parte útil, com a corrente de partida, ficaria em ~7,6 s.
2. **A serial comanda o alvo e a parada.** O 05 diz "o motor só se comanda
   pelos botões", no contexto da página do celular. Aqui a partida continua
   só no botão; a serial do notebook do operador ajusta o alvo (necessário
   para calibrar o teto com o tacômetro) e para.
3. **Teto de 1400 µs estimado.** Ver `config.rs`: pelo modelo do 04,
   37 % do acelerador dá ~1590 RPM com o rotor a 7 V, abaixo dos 1800.
   O valor final é medido (abaixo).
4. **Dois watchdogs** em vez de um.

## Instalação (uma vez por máquina)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

```bash
cargo install espup espflash --locked
```

```bash
espup install --targets esp32
```

O `espup` grava `~/export-esp.sh`, que põe o ligador do Xtensa no `PATH`. Em
bash/zsh, `. ~/export-esp.sh` em cada terminal. Em fish, abrir um fish com
o ambiente:

```bash
bash -c '. ~/export-esp.sh; exec fish'
```

## Testar, compilar, gravar

A lógica, no Mac (não precisa do ambiente do ESP):

```bash
cd firmware/controle-motor && cargo test
```

O programa da placa:

```bash
cd firmware/esp32-base && cargo build --release
```

**Antes da primeira gravação**, com a fonte do ESC desligada, ler o chip. O
`esp-hal` não aceita ESP32 abaixo da revisão v3.0; com um chip mais antigo o
gerenciador de boot recusa o programa (nenhum pulso sai, mas nada funciona).
A mesma leitura confirma os dois núcleos que o 05 §8.1 pede:

```bash
espflash board-info --chip esp32
```

Gravar e abrir o monitor. Abrir o monitor reinicia a placa, e um motor
girando para; fechar também pode reiniciar:

```bash
cd firmware/esp32-base && cargo run --release
```

Só o monitor, gravando a sessão inteira num arquivo (o `script` do macOS
mantém o teclado funcionando):

```bash
script -q ensaio.log espflash monitor --chip esp32
```

As linhas que começam com `D;` são o registro, separado por `;` com vírgula
decimal: `t_ms;estado;pulso_us;acel_%;alvo_us;giro_s`. Mudanças de estado
saem na hora; em giro, uma linha a cada 200 ms.

## Teclas

| Tecla | Efeito |
|---|---|
| espaço, `p`, Esc, Ctrl-C | **parar**, a qualquer momento, inclusive no meio de um número |
| `1350` Enter | alvo em µs (recusado acima do teto) |
| `+` `-` | alvo ±5 µs |
| `>` `<` | alvo ±1 µs |
| `r20` Enter | rampa de partida em s (mínimo 12; só parado) |
| `s` | estado, inclusive a leitura dos dois botões |
| `h` `?` | ajuda |
| `W` | trava o laço de propósito, para o ensaio do watchdog |

## Bancada, em etapas

As regras de segurança do 04 valem desde a primeira etapa com o motor
ligado.

1. **Sem ESC.** Gravar e conferir no banner a revisão, o teto e "armado".
   Com `s`, ver os botões "solto"; segurar cada um e repetir `s`.
   Partida: as linhas `D;` sobem de 1148 µs. Parada pelo botão e pela
   serial. Se houver osciloscópio, medir no D25: 1000 µs parado e o
   período de 20 ms.
2. **ESC alimentado, fases desconectadas** (fonte a 7,0 V com limite de
   corrente, GND comum). Energizar o ESC com a placa já em 1000 µs: ele
   deve bipar e armar.
3. **Motor sem rotor, preso, sem hélice.** Alvo baixo (1200 µs) e
   partida. Conferir o sentido anti-horário visto de cima (pendente desde
   16/10). Conferir a PARADA pelo botão e pela serial, e o WATCHDOG: em
   giro, `W` → o motor para em menos de 1 s e o banner volta com
   `CoreMwdt0` ou `SysRtcWdt`.
4. **Calibrar o teto, com o rotor e a contenção do 04.** Subir em patamares
   com o tacômetro. Ao chegar ao teto sem 1800 RPM, subir `CEILING_US` no
   `config.rs` no máximo 25 µs, regravar e repetir. No pulso que der
   1800 RPM, fixar o teto, marcar `CEILING_MEASURED = true` e anotar
   pulso, tensão e RPM no registro de ensaio.
5. Daí em diante, os bloqueadores A e D do 04 usam este teto: patamares
   pelo alvo (`+`/`-` ou o número) e partidas de 12 s até ele.

## Emulador

O programa roda no QEMU da Espressif (`qemu-system-xtensa -machine esp32`)
com um eFuse que declare a revisão v3.0. Ali se verificaram o boot, a
armação, as teclas e o reinício pelo watchdog TIMG0. O QEMU não emula o
watchdog do RTC e lê os botões como pressionados (sem pull-up). A rampa foi
verificada numa cópia em que uma tecla substitui o botão, fora do
repositório.
