# Esquema elétrico — Hologram Orbiter v3.0

Duas cadeias elétricas independentes, que **não se tocam**. Não há anel coletor.

**No rotor** (§1 a §7): bateria, controlador, sensor de índice e as três fitas,
tudo girando a 1800 RPM.

**Na parte fixa** (§8): fonte de bancada, ESC, motor e o gerador do sinal de
acelerador. Mais o ímã, que é o único elemento fixo que o rotor "vê".

**Revisado em 08/09/2026.** Este documento especifica um circuito e firmware
planejados. Não há firmware implementado neste pacote nem ensaio elétrico
aprovado. Buck, chicotes, medição térmica e temporização continuam pendentes.

Diagrama visual: **https://claude.ai/code/artifact/e2f8094c-8807-4ece-806d-f606767c67ab**

---

## 1. Topologia

```
Bateria 2S ─ chave ─ fusível 7,5 A ─ buck 5,0 V ─┬─ C bulk 1000 µF
                                                  │
                          ┌───────────────────────┼──────────────┐
                          │                       │              │
                     ESP32-C3                74AHCT125       A3144 (5 V)
                    (lógica 3,3 V) ──CLK/DATA──▶ (→ 5 V) ──┐   coletor aberto
                          ▲                                 │        │
                          └────────── índice ───────────────┼────────┘
                                                            │   pull-up 10k → 3V3
                                                            ▼
                          Painel 1 ─ Painel 2 ─ Painel 3    (cadeia de 87 LEDs)
                             ▲          ▲          ▲
                             └──────────┴──────────┘  5 V e GND em estrela
```

**Potência em estrela, dados em cadeia.** Cada painel recebe 5 V e GND direto do
cubo (1,74 A cada em branco pleno). Os dados percorrem um único barramento SPI
com os 87 LEDs em série.

## 2. As duas armadilhas

Nenhuma aparece na montagem. As duas aparecem quando a imagem não acende.

### 2.1 O A3144 não funciona a 3,3 V

Ele opera de **4,5 a 24 V**. Alimentado pelo 3V3 do ESP32, não comuta.

Como a saída é **coletor aberto**, a solução é limpa: sensor em **5 V** e
**pull-up de 10 kΩ no 3V3**. Quem define o nível alto é o pull-up, então o sinal
oscila de 0 a 3,3 V e a entrada do ESP32-C3 — que **não** tolera 5 V — fica
protegida.

> Pull-up para 5 V queima a porta. Sem pull-up nenhum, não há sinal.

> **Use o A3144 nu, não a placa HW-477.** O módulo tem pull-up próprio para o seu
> VCC: alimentado em 5 V, a saída vai a 5 V e queima a entrada do ESP32-C3. E a
> placa de 18 × 15 mm pesa 1,5–2,5 g, que a r = 29 mm valem 43 a 72 g·mm contra
> os **8,4** admissíveis. Dessoldado, o TO-92 pesa 0,2 g e cabe no bolso do CAD.

### 2.2 3,3 V não aciona a fita com segurança

A HD107S em 5 V pede `V_IH ≥ 0,7 × VDD = 3,5 V`; o ESP32-C3 entrega 3,3 V. A
15,4 Mbit/s, com fio correndo dentro do rotor, isso não é margem.

**Adotado:** `74AHCT125` nos dois sinais. A família AHCT tem entrada TTL
(V_IH 2,0 V) e saída de 5 V — é exatamente o conversor 3,3 → 5 V.

Ligar os dois `/OE` usados ao GND, fixar as entradas dos canais não usados em
nível definido e colocar 100 nF cerâmico junto a VCC/GND do CI. A pinagem depende
do encapsulamento comprado. O capacitor bulk não substitui esse desacoplamento.
[Datasheet Texas Instruments](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf).

**Não usar buck em 4,5 V como substituto garantido do buffer.** O limiar de
~3,15 V continua acima do V_OH mínimo de 0,8 × VDD = 2,64 V especificado para o
ESP32-C3. O regulador da Super Mini e a fita reais também precisam ser
identificados. [Datasheet ESP32-C3](https://documentation.espressif.com/esp32-c3_datasheet_en.html).

## 3. Pinos do ESP32-C3

| Sinal | Pino | Vai para | Nota |
|---|---|---|---|
| SPI CLK | GPIO 4 | 74AHCT125 entrada A | 20 MHz solicitados, 180 colunas, DMA; medir clock efetivo (§5) |
| SPI MOSI | GPIO 6 | 74AHCT125 entrada B | dados da cadeia |
| ÍNDICE | GPIO 3 | saída do A3144 | interrupção na borda de descida |
| V_BAT | GPIO 0 (ADC) | divisor **150k / 47k** + **100 nF ao GND no pino** | 1,72 V a 7,2 V (LiFe cheia) · corte em 1,38 V (= 5,8 V) |
| 5V | 5V | trilho do buck | — |
| 3V3 | 3V3 | pull-up do hall | regulador da placa |
| GND | GND | trilho comum | estrela no cubo |

A numeração é sugestão. O que importa: CLK e MOSI saindo do periférico SPI, e o
índice num pino com interrupção.

## 4. Chicote por longarina

O sulco tem 4,4 × 3 mm. A topologia exige **seis condutores**: duas vias de
potência, duas de entrada e duas de retorno da cadeia. A estimativa de duas
camadas (3,7 × 2,35 mm) depende dos diâmetros **com isolação**, ainda não medidos.
Conferir a rota inteira com o chicote real, incluindo janelas, diafragmas,
dobras e saída da fita; não declarar cabimento só pela bitola do cobre.

| Condutor | Bitola | Corrente | Cor | P1 | P2 | P3 |
|---|---|---:|---|:--:|:--:|---|
| +5 V | AWG 24 | 1,74 A | vermelho | ✓ | ✓ | ✓ |
| GND | AWG 24 | 1,74 A | preto | ✓ | ✓ | ✓ |
| CLK entrada | AWG 28 | — | amarelo | ✓ | ✓ | ✓ |
| DATA entrada | AWG 28 | — | verde | ✓ | ✓ | ✓ |
| CLK retorno | AWG 28 | — | amarelo/branco | ✓ | ✓ | montado, sem uso |
| DATA retorno | AWG 28 | — | verde/branco | ✓ | ✓ | montado, sem uso |

> **Monte o chicote idêntico nos três painéis.** A cadeia só precisa de retorno
> em dois, mas **meio grama de fio a menos no painel 3 gera 50 g·mm de
> desbalanceamento**, contra os 8,4 admissíveis — seis vezes o limite. Deixe o
> retorno do painel 3 montado e desconectado: custa 0,5 g de peso morto e poupa
> uma correção de 0,55 g.

O retorno sai da ponta superior da fita, desce pela cavidade aberta do painel —
passando pelos vãos dos diafragmas — e volta pelo bolso de fios da ponta
inferior. **Prenda com kapton a cada 50 mm:** fio solto dentro do painel oscila
e desbalanceia.

## 5. Orçamento de energia e temporização

Base de cálculo, **a confirmar na fita real**: 87 × 60 mA × 5 V = **26,1 W**
de LEDs em branco pleno. Seja `f` a fração efetiva dessa corrente RGB, incluindo
conteúdo e ajuste de brilho. 15% e 30% são cenários, não perfis medidos.
O ESP32-C3 acrescenta **0,3 W na saída do buck**, uma única vez. Com eficiência
assumida de 87,5%: `P_bat = (26,1·f + 0,3)/0,875`, `I_bat = P_bat/6,6` e
`t = 0,8/I_bat` horas. Consumo adicional do Hall/buffer, rádio, perdas dos fios,
capacidade útil e eficiência ao longo da descarga devem entrar após medição.

| Cenário | P LEDs | P saída buck (LEDs + ESP) | P bateria | I bateria a 6,6 V | Autonomia teórica |
|---|---:|---:|---:|---:|---:|
| Branco 100%, referência de dimensionamento | 26,10 W | 26,40 W | 30,17 W | 4,57 A | 10,5 min |
| Teto provisório de 80% | 20,88 W | 21,18 W | 24,21 W | 3,67 A | 13,1 min |
| Conteúdo equivalente a 30% | 7,83 W | 8,13 W | 9,29 W | 1,41 A | 34,1 min |
| Conteúdo equivalente a 15% | 3,915 W | 4,215 W | 4,82 W | 0,730 A | 65,8 min |

**Buck de exatamente 5 A não cobre branco pleno:** são 5,22 A de LEDs mais
0,06 A do ESP, antes dos demais consumos. Até qualificar o componente real,
especificar limite de corrente global: **f ≤ 80% e corrente total medida na
saída ≤ 4,25 A**, valendo o menor limite. Isso é um teto provisório para ensaio,
não a aprovação de qualquer módulo anunciado como 5 A. Verificar regulação,
ripple e temperatura com a tensão de entrada de 7,2 até 5,8 V e com a carga
máxima autorizada. O firmware deverá implementar a limitação antes do primeiro
acendimento; ainda não está implementado. Branco pleno exige redimensionamento
ou comprovação de capacidade contínua superior a 5,28 A. A autonomia útil fica
**pendente de ensaio**; não manter a promessa anterior de 45–50 min.

Um quadro planejado tem `32 + 87 × 32 + 44 = 2860 bits`. A quantidade de bits
de fim deve ser conferida com o lote HD107S real; 44 é a provisão atual da
cadeia. O buffer DMA pode ter 360 bytes alocados/alinhados, com comprimento de
transmissão explicitamente definido; se transmitir os 2880 bits, recalcular.

| RPM × colunas | Quadros/s | Taxa útil | Janela por quadro | Transmissão a 20 MHz | Folga antes do overhead |
|---|---:|---:|---:|---:|---:|
| 1800 × 180 | 5400 | 15,444 Mbit/s | 185,19 µs | 143,00 µs | 42,19 µs |
| 2000 × 180, não liberado | 6000 | 17,160 Mbit/s | 166,67 µs | 143,00 µs | 23,67 µs |
| 1800 × 256, experimental | 7680 | 21,965 Mbit/s | 130,21 µs | 143,00 µs | −12,79 µs |

Clock solicitado não é clock garantido: no ESP32-C3, pedir 30 MHz com fonte
de 80 MHz e divisor inteiro resulta normalmente em **26,67 MHz**. Ler a
frequência efetiva e medir no pino. Nesse clock, 2860 bits duram 107,25 µs;
256 colunas a 1800 RPM deixam 22,96 µs antes do overhead. A documentação do
driver dá ordem de **20 µs adicionais por transação de interrupção**: restariam
~2,96 µs, sem garantia de pior caso. A 2000 RPM/256 colunas a janela é 117,19 µs
e esse orçamento não fecha. A 2000 RPM/180 colunas em 20 MHz restariam só
~3,67 µs após esse overhead. Nenhum desses modos é considerado validado.
[Driver SPI ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c3/api-reference/peripherals/spi_master.html).

Validar com analisador lógico/osciloscópio o clock real, o tempo máximo entre
quadros e o atraso do índice até a saída, sob a carga de firmware prevista.
DMA e buffer duplo são escolhas de implementação; não comprovam jitter.

## 6. Firmware — o mínimo

```
ÍNDICE     interrupção na borda do A3144, uma vez por volta
           T_volta = t[n] − t[n−1]        (mede a rotação real)
           coluna k dispara em  t[n] + k · T_volta / 180

MAPEAMENTO um quadro = 87 LEDs, na ordem física da cadeia
             LED  0 – 28  → painel 1, ângulo θ
             LED 29 – 57  → painel 2, ângulo θ + 120°
             LED 58 – 86  → painel 3, ângulo θ + 240°
           acrescentar a fase correspondente ao instante real de atualização
           de cada LED, além da calibração de zero do Hall

SPI        20 MHz solicitado p/ 180 colunas, modo 0, DMA, buffer duplo
           quadro APA102: 32 bits de início + 87 × 32 + 44 de fim
           confirmar protocolo do lote HD107S e clock efetivo; ver §5

CORRENTE   limitar soma RGB a f <= 80% e I_saida medida <= 4,25 A
           reduzir mais se a qualificação do buck real exigir

BATERIA    LiFePO4 2S: 7,2 V cheia · 6,6 no platô · 5,0 vazia
           ATENÇÃO (pendência C7): confirme a ENTRADA MÍNIMA do buck real.
           Muitos módulos "mini560 5 V" pedem 7 V (ou V_out + 1,5 V). Se for
           esse o caso, o conversor passa quase toda a descarga em dropout,
           entrega V_in menos a queda e cai abaixo dos 4,5 V que garantem o
           V_IH da fita. O corte "em 5,8 V pelo dropout do buck" é PREMISSA,
           não datasheet. Mínimo aceitável: <= 5,5 V, ou trocar por buck-boost.
           ADC a cada 2 s; aviso/apagamento em 1,38 V (= 5,8 V)
           o limiar depende do buck real, não é proteção da química
           apagar a imagem não desconecta ESP/buck/bateria: definir proteção
           contra descarga profunda e estado de falha antes da integração
           divisor 150k/47k: 8,4 V lê 2,00 V. NÃO use 100k/56k — daria
           3,02 V, e o ADC do ESP32-C3 a 12 dB só é linear até ~2,5 V,
           então bateria cheia cairia na região não linear.
```

A atualização óptica precisa ser verificada, pois a HD107S pode atualizar cada
LED ao receber seu quadro de 32 bits. A 20 MHz, LEDs homólogos de painéis
consecutivos chegam separados por 29 × 32 / 20 MHz = **46,4 µs**, ou **0,501°**
a 1800 RPM; entre painéis 1 e 3 são **1,002°**, meia coluna de 180. O mapeamento
deve compensar esse atraso se confirmado no lote real; não atribuir toda imagem
tripla à montagem. [Descrição de atualização HD107S, Rose Lighting](https://www.rose-lighting.com/wp-content/uploads/sites/53/2020/05/HD107S-5050-Specificaion-V1.0.1.pdf).

## 7. Montagem na baia

Layout no CAD (`spider.bay_layout`; render `exports/preview/montagem_baia.png`).
Coordenadas do rotor: braço 1 em +x, Z = 0 no topo do cubo.

| Item | Envelope | Onde | Massa (catálogo) |
|---|---:|---|---:|
| Bateria LiFePO4 2S | 58 × 30 × 17 | berço central, deitada em y, sobre trilhos em Z = 9; a arruela e a porca fina terminam em Z = 5 | 50 g (medida) |
| Placa de interface: 74AHCT125, pull-up, divisor, polyfuse, chave slide, JST-XH | 15 × 20 × 8 | +x, x 19,5…34,5 · y −5…15, em pilares de 6 mm, sob a janela da tampa; os terminais do hall sobem debaixo dela | 5,5 g |
| ESP32-C3 Super Mini | 18 × 22,5 × 5 | −x, x −36…−18 · y ±11, em pilares de 6 mm; USB-C para −y | 3,0 g |
| Buck 5 V mini560 | 22 × 17 × 6 | em pé numa ranhura na parede da baia a 140°, indutor para dentro | 2,0 g |
| C bulk 1000 µF | Ø10 × 20 | em pé numa cerca em (22,5, −22), lado +x | 2,5 g |
| Fios internos | — | — | 2,0 g |
| A3144 **nu** | TO-92 | bolso na face inferior do cubo, r = 29 mm, azimute 20° — **não use a placa HW-477** | 0,2 g |

A baia tem **Ø78 × 29 mm** (cubo Ø92), com 24 mm úteis acima da porca. Tudo
elevado em pilares deixa o piso livre para os três feixes dos painéis, que saem
pelas janelas da parede em Z 0,8–5,8.

**A baia é intrinsecamente assimétrica**, e o esboço mostra quanto: com essas
massas de catálogo, somados os centróides que o gerador mede na aranha e na
tampa e o sensor hall, o desbalanceamento nominal é de **63,2 g·mm a 23°**, sete
vezes o admissível. A direção da correção não cai dentro de nenhum alívio, então
ela é repartida: **2,19 g de tungstênio no alívio de 180° e 0,86 g no de 300°**,
na face inferior do cubo (r ≈ 33). O gerador refaz essa conta a cada mudança de
posição ou massa: **pesar cada peça real e atualizar `mass_g`** antes de fixar.
Tudo que entrar aqui precisa ficar onde o CAD diz: **1 mm de excentricidade em
50 g já são 50 g·mm**, seis vezes o admissível.

---

## 8. A parte fixa

```
Fonte de bancada ──── ESC LittleBee Spring 20A ──── motor A2212 920KV
   6–7 V, ≥ 5 A        BLHeli_S, sinal servo            3 fases
        │                      ▲
        │                      │ PWM 1–2 ms, 50 Hz
        └──── GND ─────── Arduino (gerador de rampa)
                               │
                        botão de parada
```

### 8.1 Por que Arduino e não gerador de bancada

Você tem os dois. O gerador de bancada produz o pulso de 1–2 ms sem dificuldade,
mas **a rampa é a função que importa** — variar a largura de pulso de 1000 para o
alvo ao longo de pelo menos 12 segundos — e isso ele não faz bem.

E o ESC **não tem tempo de rampa**: o manual do BLHeli_S expõe *startup power*,
não duração. A rampa é responsabilidade deste gerador, inteira.

### 8.2 O que o firmware do gerador precisa fazer

```
ARMAÇÃO   ao ligar, manter 1000 µs por ~2 s antes de qualquer coisa.
          O BLHeli_S só arma vendo mínimo estável; sinal ausente ou
          alto na energização = ESC não arma, por segurança.

RAMPA     de 1000 µs até o alvo em >= 12 s, linear no comando.
          Confirmar a rampa de RPM: pulso linear não garante aceleração linear.
          Com J=0,00155 kg.m² e T_arrasto=51,4 mN.m, 12 s dão 7,30 A
          de fase e ~4,02 A na fonte de 7 V (eta_ESC=95%).
          8 s dariam 8,47 A/~4,98 A e reprovam o teto de 8 A/4,6 A.

PARADA    normal: botão físico -> 1000 µs; confirmar resposta do ESC na bancada.
          emergência: corte físico da fonte acessível ao operador.
          Nenhuma ação garante parada imediata; contenção fechada até rotor
          visivelmente imóvel e pelo menos 90 s após corte (plano de ensaios).

PATAMARES para o Bloqueador A: 600, 1000, 1400 e 1800 RPM, 2 min cada.
```

### 8.3 Três coisas que costumam queimar tempo

**GND comum.** Arduino, ESC e fonte de bancada precisam compartilhar o terra. Sem
isso o ESC lê ruído em vez de sinal. É o erro mais comum e o mais difícil de
diagnosticar.

**Nível lógico.** O ESC aceita 3,3 V ou 5 V no fio de sinal; qualquer Arduino
serve. O BEC do ESC, se houver, **não** deve alimentar o Arduino se a fonte de
bancada já estiver ligada — escolha uma fonte só.

**Configuração do ESC**, antes de qualquer ensaio de rotação:

| Parâmetro | Valor | Motivo |
|---|---|---|
| Direction | conforme o sentido anti-horário visto de cima | bordo de ataque em +y |
| **Brake on stop** | **desabilitado** | frear 27,6 J contra fonte de bancada empurra o barramento |
| **Low RPM power protect** | **desabilitado** | a 1800 RPM estamos a 26 % da rotação a vazio, o regime que ela limita |
| Startup power | começar baixo e subir | é o ajuste da partida com inércia 100× a de uma hélice |

### 8.4 Opcional, mas provavelmente vale

O LittleBee Spring usa um EFM8BB21, suportado pelo **Bluejay**. A opção de
reflash exige identificar o alvo exato e implementar/verificar **DShot
bidirecional no gerador**, inclusive a conversão de RPM elétrica pelo número
de pares de polos. Bluejay não aceita o sinal servo PWM de 1–2 ms deste plano;
reflash isolado interrompe esse controle. Não retirar o tacômetro antes de
qualificar a leitura de RPM. Ela também não substitui a referência angular
1/rev necessária ao balanceamento. [FAQ oficial Bluejay](https://github.com/bird-sanctuary/bluejay/wiki/FAQ).

Não adiciona governor. Se o Bloqueador E mostrar imagem instável, a malha se
fecharia aqui, no Arduino — mas a conta de estabilidade indica que não será
preciso: a inércia do rotor mantém a variação entre voltas em 0,03 a 0,11 %,
contra 0,14 % de orçamento.
