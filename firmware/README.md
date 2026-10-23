# Firmware

**ESP32 da base: gerador do sinal do ESC** (esquema 05 §8), em Rust `no_std`
sobre o `esp-hal` 1.2. Escrito e gravado em 19/10/2026 na ESP32 da base
(revisão v3.1, dois núcleos), com a fonte do ESC desligada: armação, teclas,
botões (por jumper ao GND) e watchdog conferidos na placa. No mesmo dia,
com o ESC a 7,0 V e o motor sem rotor, partiu pela rampa e girou no sentido
anti-horário visto de cima (registro em
`esc_blheli_s_2026-10-16/registro.md`). **Ainda sem ensaio com o rotor.**

**Versão 0.2.0, 20/10/2026: partida com chute e fonte do ESC em 10–12 V.** Em
19/10, com a peça montada, a rampa de 12 s até 1200 µs não deu partida: o
ESC tentava três vezes e desistia. O rotor só partiu com 1400 µs e a fonte
em 10,4 V (`esc_blheli_s_2026-10-19/registro.md`). A partida agora sobe ao
chute de 1400 µs em 3 s, segura 2 s e desce ao alvo; o teto de regime caiu
para 1320 µs, estimado para 10–12 V; e há a parada suave (`d`). **A 0.2.0
passou nos testes no Mac, mas ainda não foi gravada nem conferida na placa.**

| Pasta | O que é |
|---|---|
| `controle-motor/` | Toda a lógica (armação, partida com chute, teto, parada, botões, teclas), sem hardware. Testada no Mac com `cargo test`. |
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
| ARMAÇÃO | 1000 µs desde a configuração do LEDC; nada é aceito por 2 s | testes; emulador; placa (0.1.0) |
| PARTIDA | só pelo botão D32; linear no comando, de 1148 µs (PPM mínimo do ESC) ao chute de 1400 µs em ≥ 3 s (84 µs/s); chute de 2 s (0 a 5 s), encerrado antes pela tecla `k`; descida ao alvo a 42 µs/s | testes (0.2.0: 3,0 s, 2,0 s e 4,762 s até 1200 µs); a rampa de 12 s da 0.1.0 foi conferida na placa |
| PARADA | na hora: botão D33, ou espaço/`p`/Esc/Ctrl-C na serial → 1000 µs, a qualquer momento. Suave: `d` desce ao PPM mínimo a 21 µs/s e então 1000 µs | testes; emulador e placa só a parada na hora (0.1.0) |
| TETO | o alvo de regime fica entre o PPM mínimo e o teto (1320 µs); acima do teto o pulso só fica na partida, por tempo limitado; todo pulso passa por `pwm::duty_for`, que prende entre 1000 µs e o chute, arredondando para baixo no chute | testes, inclusive o tempo acima do teto sob comandos aleatórios |
| WATCHDOG | dois: o do grupo de timers TIMG0 e o do RTC, 500 ms, os dois reiniciando o chip inteiro (o LEDC para e o pulso some) | emulador (TIMG0); placa: `W` reiniciou pelos dois (0.1.0) |
| REINÍCIO | depois de qualquer reinício: 1000 µs, alvo padrão (1200 µs) e espera; a partida nunca recomeça sozinha | emulador (travamento e pânico); placa (0.1.0) |
| PÁGINA | não existe ainda; a serial ajusta o alvo, encerra o chute e para, mas nunca dá partida | teste das 256 teclas |

Além do pedido:

- **Ajustes em giro** (novo alvo, `+`/`-`) e a **parada suave** andam a
  21 µs/s (do PPM mínimo ao chute, 252 µs, em 12 s), nos dois sentidos.
  Durante a partida, mudar o alvo só muda onde a descida termina. Descer
  devagar mantém o motor tracionando por mais tempo e devolve menos energia
  à fonte (o BLHeli_S freia ativamente quando o acelerador cai rápido), mas
  não zera a devolução: o barramento precisa do grampo ou resistor de
  descarga do 05 §8.2.
- **Pânico** imprime a causa e reinicia; o boot seguinte mostra o motivo
  (`CoreSw`, `CoreMwdt0`, `SysRtcWdt`...) e avisa.
- Um botão pressionado na energização precisa ser solto antes de valer.
  Com a parada pressionada, a partida é ignorada.

### Pontos a ratificar

1. **A subida parte de 1148 µs, não de 1000 µs.** Abaixo do PPM Min Throttle
   gravado (1148 µs) o ESC vê acelerador zero; partindo de 1000 µs, a
   primeira parte da subida seria morta.
2. **A serial comanda o alvo, o fim do chute e a parada.** O 05 diz "o motor
   só se comanda pelos botões", no contexto da página do celular. Aqui a
   partida continua só no botão; a serial do notebook do operador ajusta o
   alvo (necessário para calibrar o teto com o tacômetro), encerra o chute e
   para.
3. **Teto de regime de 1320 µs estimado.** Ver `config.rs`: pelo modelo do
   04, 25 % do acelerador dá ~1790 RPM com o rotor a 12 V e ~1560 RPM a
   10 V. O valor final é medido (abaixo), na tensão em uso.
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

O `espflash monitor` passa pelo carregador da ROM ao conectar. Em 19/10 ele
às vezes deixou a placa parada ali, sem o banner depois de "Commands" e sem
pulso no D25: nesse caso, Ctrl+R reinicia a placa no programa. No monitor,
Ctrl+C fecha o monitor em vez de parar o motor; para parar, espaço ou `p`
(na hora) ou `d` (suave).
Evitar o `screen`: rolar a tela nele manda setas (Esc `[` `A`) à placa.

As linhas que começam com `D;` são o registro, separado por `;` com vírgula
decimal: `t_ms;estado;pulso_us;acel_%;alvo_us;giro_s`. Mudanças de estado
saem na hora; em giro, uma linha a cada 200 ms. Estados: `ARMANDO`, `PARADO`,
`RAMPA` (subida ao chute ou ao alvo), `CHUTE`, `REGIME` e `PARANDO` (parada
suave). `giro_s` é o tempo desde a partida, não uma medida de rotação.

## Teclas

| Tecla | Efeito |
|---|---|
| espaço, `p`, Esc, Ctrl-C | **parar na hora**, a qualquer momento, inclusive no meio de um número |
| `d` | **parada suave**: desce ao acelerador zero a 21 µs/s e para |
| `k` | encerra o chute agora (ou a subida até ele) e desce ao alvo; para quando o rotor já gira |
| `1250` Enter | alvo de regime em µs (recusado acima do teto) |
| `+` `-` | alvo ±5 µs |
| `>` `<` | alvo ±1 µs |
| `r3` Enter | subida até o chute em s (3 a 30; só parado) |
| `c2` Enter | duração do chute em s (0 a 5; só parado) |
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
2. **ESC alimentado** (fonte a 10–12 V com limite de corrente de ~3 A, GND
   comum, grampo ou resistor de descarga no barramento do ESC). Energizar o
   ESC com a placa já em 1000 µs: ele deve bipar e armar.
3. **Motor sem rotor, preso, sem hélice.** Alvo baixo (1200 µs), `c0` para
   um chute curto, e partida. Conferir o sentido anti-horário visto de cima (confirmado em
   19/10 com Normal; conferir de novo se os fios do motor forem trocados). Conferir a PARADA pelo botão e pela serial, e o WATCHDOG: em
   giro, `W` → o motor para em menos de 1 s e o banner volta com
   `CoreMwdt0` ou `SysRtcWdt`.
4. **Calibrar o teto, com o rotor e a contenção do 04.** Partida com o
   chute; ao ver o rotor girar, `k`. Subir em patamares com o tacômetro, na
   tensão de fonte que vai ser usada. Ao chegar ao teto sem 1800 RPM, subir
   `CEILING_US` no `config.rs` no máximo 25 µs (sempre abaixo do chute),
   regravar e repetir. No pulso que der 1800 RPM, fixar o teto, marcar
   `CEILING_MEASURED = true` e anotar pulso, tensão e RPM no registro de
   ensaio.
5. Daí em diante, os bloqueadores A e D do 04 usam este teto: patamares
   pelo alvo (`+`/`-` ou o número) e partidas com chute até ele. Terminar
   cada ensaio pela parada suave (`d`).

## Emulador

O programa roda no QEMU da Espressif (`qemu-system-xtensa -machine esp32`)
com um eFuse que declare a revisão v3.0. Ali se verificaram o boot, a
armação, as teclas e o reinício pelo watchdog TIMG0. O QEMU não emula o
watchdog do RTC e lê os botões como pressionados (sem pull-up). A rampa foi
verificada numa cópia em que uma tecla substitui o botão, fora do
repositório. Tudo isso foi com a 0.1.0; a 0.2.0 não rodou no emulador.
