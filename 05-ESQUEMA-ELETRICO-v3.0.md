# Esquema elétrico — Hologram Orbiter v3.0

Duas cadeias elétricas independentes, que **não se tocam**. Não há anel coletor.

**No rotor** (§1 a §7): bateria, controlador, sensor de índice e as três fitas,
tudo girando a 1800 RPM.

**Na parte fixa** (§8): fonte de bancada, ESC, motor e o gerador do sinal de
acelerador. Mais o ímã, que é o único elemento fixo que o rotor "vê".

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
> os 9,1 admissíveis. Dessoldado, o TO-92 pesa 0,2 g e cabe no bolso do CAD.

### 2.2 3,3 V não aciona a fita com segurança

A HD107S em 5 V pede `V_IH ≥ 0,7 × VDD = 3,5 V`; o ESP32-C3 entrega 3,3 V. A
15,4 Mbit/s, com fio correndo dentro do rotor, isso não é margem.

**Adotado:** `74AHCT125` nos dois sinais. A família AHCT tem entrada TTL
(V_IH 2,0 V) e saída de 5 V — é exatamente o conversor 3,3 → 5 V.

**Alternativa sem componente:** buck em 4,5 V baixa o limiar para ~3,15 V. Mas
aí o regulador da placa ESP32 fica sem folga de dropout. Só use se abrir mão de
alimentar a placa pelo mesmo trilho.

## 3. Pinos do ESP32-C3

| Sinal | Pino | Vai para | Nota |
|---|---|---|---|
| SPI CLK | GPIO 4 | 74AHCT125 entrada A | 20 MHz, DMA |
| SPI MOSI | GPIO 6 | 74AHCT125 entrada B | dados da cadeia |
| ÍNDICE | GPIO 3 | saída do A3144 | interrupção na borda de descida |
| V_BAT | GPIO 0 (ADC) | divisor **150k / 47k** | 1,72 V a 7,2 V (LiFe cheia) · corte em 1,38 V (= 5,8 V) |
| 5V | 5V | trilho do buck | — |
| 3V3 | 3V3 | pull-up do hall | regulador da placa |
| GND | GND | trilho comum | estrela no cubo |

A numeração é sugestão. O que importa: CLK e MOSI saindo do periférico SPI, e o
índice num pino com interrupção.

## 4. Chicote por longarina

O sulco tem 4,4 × 3 mm. Seis condutores cabem em duas camadas: 2 × AWG 24 mais
1 × AWG 28 embaixo (3,7 mm), 3 × AWG 28 em cima — 2,35 mm de altura total.

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

## 5. Orçamento de energia

| Cenário | Potência | Na bateria LiFePO4 2S (6,6 V) | Autonomia 800 mAh |
|---|---:|---:|---:|
| Branco pleno, 87 LEDs | 27,3 W | 4,1 A (5C) | 12 min |
| Conteúdo claro (30 %) | 9,0 W | 1,4 A | 35 min |
| **Típico POV (15 %)** | **5,1 W** | **0,77 A** | **~60 min** |

Conteúdo POV é majoritariamente escuro, então 15 % é o caso realista. O branco
pleno dimensiona o buck e os condutores, não a autonomia.

| Taxa de dados | Quadros/s | Mbit/s | |
|---|---:|---:|---|
| 1800 RPM × 180 colunas | 5400 | 15,4 | folgado |
| 2000 RPM × 180 colunas | 6000 | 17,2 | folgado |
| 1800 RPM × 256 colunas | 7680 | 22,0 | cabe |

Cadeia única de 87 LEDs = 2859 bits por quadro. SPI a 20 MHz com DMA cobre todos
os casos; a HD107S aceita até 30 MHz.

## 6. Firmware — o mínimo

```
ÍNDICE     interrupção na borda do A3144, uma vez por volta
           T_volta = t[n] − t[n−1]        (mede a rotação real)
           coluna k dispara em  t[n] + k · T_volta / 180

MAPEAMENTO um quadro = 87 LEDs, na ordem física da cadeia
             LED  0 – 28  → painel 1, ângulo θ
             LED 29 – 57  → painel 2, ângulo θ + 120°
             LED 58 – 86  → painel 3, ângulo θ + 240°
           os três lêem colunas diferentes do mesmo instante

SPI        20 MHz, modo 0, DMA, buffer duplo
           quadro APA102: 32 bits de início + 87 × 32 + 44 de fim

BATERIA    LiFePO4 2S: 7,2 V cheia · 6,6 no platô · 5,0 vazia
           ADC a cada 2 s; corte em 1,38 V (= 5,8 V), que é o limite
           de entrada do buck, não o da química
           apaga a imagem e pisca um LED de aviso
           divisor 150k/47k: 8,4 V lê 2,00 V. NÃO use 100k/56k — daria
           3,02 V, e o ADC do ESP32-C3 a 12 dB só é linear até ~2,5 V,
           então bateria cheia cairia na região não linear.
```

## 7. Montagem na baia

Layout no CAD (`spider.bay_layout`; render `exports/preview/montagem_baia.png`).
Coordenadas do rotor: braço 1 em +x, Z = 0 no topo do cubo.

| Item | Envelope | Onde | Massa (catálogo) |
|---|---:|---|---:|
| Bateria LiFePO4 2S | 58 × 30 × 17 | berço central, deitada em y, sobre trilhos em Z = 6; a arruela e a porca fina terminam em Z = 5 | 50 g (medida) |
| Placa de interface: 74AHCT125, pull-up, divisor, polyfuse, chave slide, JST-XH | 15 × 20 × 8 | +x, x 19,5…34,5 · y −5…15, em pilares de 6 mm, sob a janela da tampa; os terminais do hall sobem debaixo dela | 5,5 g |
| ESP32-C3 Super Mini | 18 × 22,5 × 5 | −x, x −36…−18 · y ±11, em pilares de 6 mm; USB-C para −y | 3,0 g |
| Buck 5 V mini560 | 22 × 17 × 6 | em pé numa ranhura na parede da baia a 140°, indutor para dentro | 2,0 g |
| C bulk 1000 µF | Ø10 × 20 | em pé numa cerca em (22,5, −22), lado +x | 2,5 g |
| Fios internos | — | — | 2,0 g |
| A3144 **nu** | TO-92 | bolso na face inferior do cubo, r = 29 mm, azimute 20° — **não use a placa HW-477** | 0,2 g |

A baia tem **Ø78 × 26 mm** (cubo Ø92), com 21 mm úteis acima da porca. Tudo
elevado em pilares deixa o piso livre para os três feixes dos painéis, que saem
pelas janelas da parede em Z 0,8–5,8.

**A baia é intrinsecamente assimétrica**, e o esboço mostra quanto: com essas
massas de catálogo o desbalanceamento nominal é de **73 g·mm a 14°**, oito vezes
o admissível, corrigido com **2,2 g de massa de tungstênio no alívio de 180°**
da face inferior do cubo (r ≈ 33). O gerador refaz essa conta a cada mudança de
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
alvo ao longo de 8 segundos — e isso ele não faz bem.

E o ESC **não tem tempo de rampa**: o manual do BLHeli_S expõe *startup power*,
não duração. A rampa é responsabilidade deste gerador, inteira.

### 8.2 O que o firmware do gerador precisa fazer

```
ARMAÇÃO   ao ligar, manter 1000 µs por ~2 s antes de qualquer coisa.
          O BLHeli_S só arma vendo mínimo estável; sinal ausente ou
          alto na energização = ESC não arma, por segurança.

RAMPA     de 1000 µs até o alvo em >= 8 s, linear.
          8 s exigem 3,5 A só para acelerar; 12 s baixam para 2,3 A.

PARADA    botão físico -> 1000 µs imediato. NÃO corte a alimentação
          com o rotor girando: sem sinal o ESC entra em modo de falha
          e o comportamento não é definido.

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

O LittleBee Spring usa um EFM8BB21, que o **Bluejay** suporta. Reflashar é
gratuito e adiciona **telemetria de rotação por DShot bidirecional** — o Arduino
passa a ler a rotação real, o que dispensa o tacômetro da lista de instrumentação
e serve direto aos Bloqueadores A e D.

Não adiciona governor. Se o Bloqueador E mostrar imagem instável, a malha se
fecharia aqui, no Arduino — mas a conta de estabilidade indica que não será
preciso: a inércia do rotor mantém a variação entre voltas em 0,03 a 0,11 %,
contra 0,14 % de orçamento.
