# Firmware

**Faixa atual de alvos: 1150–1350 µs (30/10/2026).** O chute também está
limitado a 1350 µs. A armação e a parada continuam em 1000 µs; o alvo ao
ligar continua em 1200 µs. O PPM mínimo gravado no ESC permanece em
1148 µs. Os ajustes `+`/`-` e `>`/`<` saturam nos limites de alvo.
A saída PWM permite 1000–1350 µs para incluir armação, parada e rampas.

Com fonte de 10,4 V e a carga do rotor completo documentada no CAD
(4,95 A a 1800 RPM, motor de 920 KV, resistência efetiva de 0,221 Ω), o
modelo médio estima cerca de 28 RPM em 1150 µs, 611 RPM em 1200 µs e
1809 RPM em 1350 µs. A estimativa de 1150 µs é uma extrapolação próxima
do acelerador zero: não garante partida nem giro sustentado, pois o modelo
não representa atrito estático, comutação e potência mínima de partida.
Confirmar as rotações com tacômetro. Equação usada, igual à de `CAD/physics.py`:
`duty × V = Kt × ω + R × I_projeto × (ω/ω_projeto)²`, com
`duty = (pulso_us − 1148)/684` e `Kt = 60/(2π × 920)`.

Esta alteração passou em 39 testes, Clippy e compilação para ESP32.
**Ainda não gravada: a placa estava desconectada.** O registro de gravação
abaixo corresponde à configuração anterior de 1400 µs.

**Versão 0.3.0, 30/10/2026: partida linear por padrão e partida pelo terminal.**
O perfil linear sobe de 1148 µs diretamente ao alvo em 3 s, sem chute e sem
descida automática ao fim da partida. A tecla `o` seleciona o overshoot
anterior; `l` volta ao linear. A seleção só é aceita sem giro. `g` inicia pelo
terminal do computador, e o botão D32 inicia no mesmo perfil selecionado.
Após reiniciar, o perfil volta a linear e o motor espera nova partida.
Esta versão passou nos 34 testes no Mac, no Clippy e na compilação para
ESP32. Gravada em 30/10/2026 na ESP32 revisão v3.1 (4 MB), pela porta
`/dev/cu.usbserial-A5069RR4`, com verificação da gravação pelo espflash.
Conferidos pela serial: banner 0.3.0, fim da armação, estado `PARADO`,
perfil `linear`, alvo de 1200 µs e zero partidas. Nenhum comando de partida
foi enviado; os perfis ainda não foram ensaiados com o motor nesta versão.

**Registro da gravação anterior: teto ajustado em 30/10/2026 para 1400 µs**, por solicitação do operador,
ainda sem calibração com tacômetro. Gravado na ESP32 pela porta
`/dev/cu.usbserial-A5069RR4` em 30/10/2026, com verificação pelo espflash.
Conferidos pela serial: teto de 1400 µs e aceitação do alvo de 1400 µs
com estado `PARADO` e zero partidas. Alvo restaurado para 1200 µs.

**ESP32 da base: gerador do sinal do ESC** (esquema 05 §8), em Rust `no_std`
sobre o `esp-hal` 1.2. Escrito e gravado em 19/10/2026 na ESP32 da base
(revisão v3.1, dois núcleos), com a fonte do ESC desligada: armação, teclas,
botões (por jumper ao GND) e watchdog conferidos na placa. No mesmo dia,
com o ESC a 7,0 V e o motor sem rotor, partiu pela rampa e girou no sentido
anti-horário visto de cima (registro em
`esc_blheli_s_2026-10-16/registro.md`). **Naquele registro, ainda sem ensaio com o rotor;
ver o relato posterior de 27/10 abaixo.**

**Versão 0.2.0, 20/10/2026: partida com chute e fonte do ESC em 10–12 V.** Em
19/10, com a peça montada, a rampa de 12 s até 1200 µs não deu partida: o
ESC tentava três vezes e desistia. O rotor só partiu com 1400 µs e a fonte
em 10,4 V (`esc_blheli_s_2026-10-19/registro.md`). Nessa versão, a partida sobe ao
chute de 1400 µs em 3 s, segura 2 s e desce ao alvo; o teto de regime caiu
para 1320 µs, estimado para 10–12 V; e há a parada suave (`d`). **A 0.2.0
passou nos testes no Mac, mas ainda não foi gravada nem conferida na placa.**

**Premissa elétrica unificada em 27/10/2026:** fonte do ESC em **10–12 V**,
limite de corrente de **30 A**, conforme `../Hologram_Orbiter_v3_0/CAD/parameters.json`.
A fonte não limita o chute no modelo: parado, 16,7–20,0 A de fase; com chute de
2 s e descida até o alvo inicial de 1200 µs, pico de 1692 RPM a 10 V e
1964 RPM a 12 V. Esse perfil com overshoot excede os critérios do bloqueador D do plano
04 e precisa ser revisto antes do ensaio com rotor. A unificação documental
não altera os pulsos nem os tempos do firmware.

**Relato posterior recebido em 27/10/2026:** a partida com rampa funcionou
facilmente, mas houve oscilação do corpo na frenagem automática dentro da
sequência, seguida de ruptura de um braço da aranha. No modo overshoot, o fim
do chute inicia a descida automática até o alvo. Conferir versão, parâmetros e
log para identificar o trecho executado; ainda não há diagnóstico da causa
da ruptura. Novos giros suspensos pela R02 do documento 06. Este relato não
confirma qual versão estava gravada nem substitui o aceite de C/D.

| Pasta | O que é |
|---|---|
| `controle-motor/` | Toda a lógica (armação, partida linear ou overshoot, teto, parada, botões, teclas), sem hardware. Testada no Mac com `cargo test`. |
| `esp32-base/` | O programa da placa: liga a lógica ao LEDC, aos botões, à serial e aos watchdogs. |

Os valores de bancada ficam em [`controle-motor/src/config.rs`](controle-motor/src/config.rs).
Para mudar o teto e os pulsos fixos, editar e regravar. Perfil, alvo e tempos
podem ser ajustados pelo terminal; os ajustes não persistem após reiniciar.

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
| PARTIDA | botão D32 ou `g` na serial. Linear (padrão): de 1148 µs diretamente ao alvo em ≥ 3 s. Overshoot (`o`): sobe a 1350 µs em ≥ 3 s, segura 2 s (0 a 5 s; `k` encerra antes), desce ao alvo a ~34 µs/s. `l` volta ao linear; perfil só muda sem giro | testes dos dois perfis e dos comandos; a rampa de 12 s da 0.1.0 foi conferida na placa |
| PARADA | na hora: botão D33, ou espaço/`p`/Esc/Ctrl-C na serial → 1000 µs, a qualquer momento. Suave: `d` desce ao PPM mínimo a ~17 µs/s e então 1000 µs | testes; emulador e placa só a parada na hora (0.1.0) |
| TETO | alvos de 1150–1350 µs; chute de 1350 µs; `pwm::duty_for` limita a saída a 1000–1350 µs (inclui parada e rampas), arredondando para cima no mínimo e para baixo no máximo | testes de limites, rampas, paradas e saída PWM |
| WATCHDOG | dois: o do grupo de timers TIMG0 e o do RTC, 500 ms, os dois reiniciando o chip inteiro (o LEDC para e o pulso some) | emulador (TIMG0); placa: `W` reiniciou pelos dois (0.1.0) |
| REINÍCIO | depois de qualquer reinício: 1000 µs, alvo padrão (1200 µs) e espera; a partida nunca recomeça sozinha | emulador (travamento e pânico); placa (0.1.0) |
| PÁGINA | não existe ainda; a serial seleciona o perfil, dá partida, ajusta o alvo e para | testes de comandos e das 256 teclas: apenas `g`/`G` geram partida |

Além do pedido:

- **Ajustes em giro** (novo alvo, `+`/`-`) e a **parada suave** andam a
  21 µs/s (do PPM mínimo ao chute, 202 µs, em 12 s), nos dois sentidos.
  Na subida ao chute e durante o chute, mudar o alvo só muda onde a descida
  termina. Na partida linear, muda o destino usando a inclinação de ajuste.
  Descer
  devagar mantém o motor tracionando por mais tempo e devolve menos energia
  à fonte (o BLHeli_S freia ativamente quando o acelerador cai rápido), mas
  não zera a devolução: o barramento precisa do grampo ou resistor de
  descarga do 05 §8.2.
- **Pânico** imprime a causa e reinicia; o boot seguinte mostra o motivo
  (`CoreSw`, `CoreMwdt0`, `SysRtcWdt`...) e avisa.
- Um botão pressionado na energização precisa ser solto antes de valer.
  Com a parada pressionada, a partida é ignorada tanto pelo botão quanto
  pela serial, inclusive durante o filtro de repique.

### Pontos a ratificar

1. **A subida parte de 1148 µs, não de 1000 µs.** Abaixo do PPM Min Throttle
   gravado (1148 µs) o ESC vê acelerador zero; partindo de 1000 µs, a
   primeira parte da subida seria morta.
2. **A serial também dá partida desde a 0.3.0.** Por solicitação do operador,
   `g` inicia pelo notebook; `l`/`o` selecionam o perfil. A página do celular
   continua sem controle do motor. A serial também ajusta o alvo, encerra o
   chute e para.
3. **Teto de regime de 1350 µs, sem calibração.** Ver `config.rs`.
   O valor final é medido (abaixo), na tensão em uso.
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
| `g` | **dar partida** no perfil selecionado; aguarda armação e exige botão de parada solto |
| `l` | selecionar **linear** (padrão): sobe diretamente ao alvo, sem overshoot; só sem giro |
| `o` | selecionar **overshoot**: sobe ao chute e depois desce ao alvo; só sem giro |
| espaço, `p`, Esc, Ctrl-C | **parar na hora**, a qualquer momento, inclusive no meio de um número |
| `d` | **parada suave**: desce ao acelerador zero a ~17 µs/s e para |
| `k` | encerra o chute agora (ou a subida até ele) e desce ao alvo; para quando o rotor já gira |
| `1250` Enter | alvo em µs (1150–1350; recusado fora da faixa) |
| `+` `-` | alvo ±5 µs |
| `>` `<` | alvo ±1 µs |
| `r3` Enter | subida até o alvo (linear) ou até o chute (overshoot), em s (3 a 30; só parado) |
| `c2` Enter | duração do chute no modo overshoot, em s (0 a 5; só parado); ignorada no linear |
| `s` | estado, inclusive a leitura dos dois botões |
| `h` `?` | ajuda |
| `W` | trava o laço de propósito, para o ensaio do watchdog |

### Partida pelo terminal do computador

Após gravar a 0.3.0, conectar a ESP32 por USB e abrir o monitor:

```bash
espflash monitor --chip esp32 --monitor-baud 115200
```

Esperar a mensagem `armado`. Digitar `l`, depois `1200` Enter e `r3` Enter;
conferir o perfil e o alvo com `s`. Digitar `g` para partir. A rampa vai de
1148 µs até 1200 µs em aproximadamente 3 s e permanece nesse alvo.

Para usar overshoot, com o motor parado, digitar `o`, `c2` Enter e depois
`g`: sobe a 1350 µs, mantém o chute por 2 s e desce ao alvo. `c0` elimina
apenas a espera em 1350 µs; ainda existe o pico. Para eliminar o pico, usar
`l`. As teclas `l`, `o`, `g`, `s`, `p` e `d` não precisam de Enter; enviar
somente a tecla, sem escrever palavras como `linear` ou `start`.

`p` ou espaço param na hora; `d` faz a parada suave. No `espflash monitor`,
Ctrl+C fecha o monitor. O banner e `s` mostram o perfil selecionado.

## Bancada, em etapas

As regras de segurança do 04 valem desde a primeira etapa com o motor
ligado.

1. **Sem ESC.** Gravar e conferir no banner a revisão, o teto e "armado".
   Com `s`, ver os botões "solto"; segurar cada um e repetir `s`.
   Partida: as linhas `D;` sobem de 1148 µs. Parada pelo botão e pela
   serial. Se houver osciloscópio, medir no D25: 1000 µs parado e o
   período de 20 ms.
2. **ESC alimentado** (fonte a 10–12 V com limite de corrente de 30 A, GND
   comum, grampo ou resistor de descarga no barramento do ESC). Energizar o
   ESC com a placa já em 1000 µs: ele deve bipar e armar.
3. **Motor sem rotor, preso, sem hélice.** Selecionar `l`, alvo baixo
   (1200 µs), e `g` para partida linear. Conferir o sentido anti-horário visto de cima (confirmado em
   19/10 com Normal; conferir de novo se os fios do motor forem trocados). Conferir a PARADA pelo botão e pela serial, e o WATCHDOG: em
   giro, `W` → o motor para em menos de 1 s e o banner volta com
   `CoreMwdt0` ou `SysRtcWdt`.
4. **Após revisar o perfil de partida conforme o bloqueador D do 04,
   calibrar o teto, com o rotor e a contenção do 04.** Partida no perfil
   validado para a montagem. Se for overshoot, selecionar `o` e, ao ver o
   rotor girar, `k`. Subir em patamares com o tacômetro, na
   tensão de fonte que vai ser usada. Ao chegar ao teto sem 1800 RPM, subir
   `CEILING_US` no `config.rs` no máximo 25 µs (sem ultrapassar o chute),
   regravar e repetir. No pulso que der 1800 RPM, fixar o teto, marcar
   `CEILING_MEASURED = true` e anotar pulso, tensão e RPM no registro de
   ensaio.
5. Daí em diante, os bloqueadores A e D do 04 usam este teto: patamares
   pelo alvo (`+`/`-` ou o número) e partidas no perfil validado. Terminar
   cada ensaio pela parada suave (`d`).

## Emulador

O programa roda no QEMU da Espressif (`qemu-system-xtensa -machine esp32`)
com um eFuse que declare a revisão v3.0. Ali se verificaram o boot, a
armação, as teclas e o reinício pelo watchdog TIMG0. O QEMU não emula o
watchdog do RTC e lê os botões como pressionados (sem pull-up). A rampa foi
verificada numa cópia em que uma tecla substitui o botão, fora do
repositório. Tudo isso foi com a 0.1.0; a 0.2.0 e a 0.3.0 não rodaram no emulador.
