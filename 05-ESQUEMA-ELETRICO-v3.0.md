# Esquema elétrico do rotor — Hologram Orbiter v3.0

Tudo neste documento gira a 1800 RPM. **Não há anel coletor:** bateria,
controlador, sensor de índice e as três fitas viajam juntos. A parte fixa tem
apenas o motor, o ESC, a fonte de bancada e um ímã.

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
| V_BAT | GPIO 0 (ADC) | divisor 100k / 56k | 3,02 V a 8,4 V · corte em 2,37 V |
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

| Cenário | Potência | Na bateria 2S | Autonomia 850 mAh |
|---|---:|---:|---:|
| Branco pleno, 87 LEDs | 27,3 W | 4,34 A | 14 min |
| Conteúdo claro (30 %) | 9,0 W | 1,44 A | 42 min |
| **Típico POV (15 %)** | **5,1 W** | **0,81 A** | **74 min** |

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

BATERIA    ADC a cada 2 s; abaixo de 2,37 V (= 6,6 V, 3,3 V/célula)
           apaga a imagem e pisca um LED de aviso
```

### 5.1 Se só houver célula 1S

Uma 1S de 1000 mAh (45 × 26 × 10) cabe, mas troca o buck por um **boost de 5 V** e
exige **limitar o brilho global no firmware** — a HD107S tem campo de 5 bits para
isso. A 3,7 V a corrente de entrada sobe a 8,7 A em branco pleno e a 10,7 A com a
célula quase vazia; um módulo desse porte não cabe na baia. Limitando a saída a
~10 W, a entrada cai para 3,2–3,9 A.

O divisor do ADC muda para **1:2 (100k/100k)**: 2,1 V a 4,2 V, corte em 1,5 V
(3,0 V por célula).

Duas células 1S **não** formam um 2S aqui: lado a lado estouram o Ø66, empilhadas
estouram os 20 mm.

## 7. Montagem na baia

| Item | Envelope | Onde |
|---|---:|---|
| Bateria 2S 850 mAh | 55 × 30 × 13 | quatro apoios (não caixa), sobre a porca M6 rebaixada |
| Buck 5 V | ~25 × 20 × 10 | parede da baia, longe da bateria |
| ESP32-C3 Super Mini | 22 × 18 × 5 | parede oposta |
| 74AHCT125 + pull-up + divisor | ~20 × 15 | placa perfurada junto ao MCU |
| C bulk 1000 µF | Ø10 × 20 | junto à saída do buck |
| Chave e conector de carga | — | janela da tampa |
| A3144 | TO-92 | bolso na face inferior do cubo, r = 29 mm |

A baia tem Ø66 × 20 mm úteis, dos quais 5,6 vão para a porca. Com o pack de
55 × 30 × 13 no meio, sobram dois segmentos circulares nas laterais para o buck e
o MCU, e **apenas 7 mm acima do pack** — o capacitor de Ø10 deitado não passa aí e
precisa ir para um segmento lateral.

**Recomendado: subir `electronics_bay_height` de 20 para 25 mm.** Custa 2,2 g,
leva o topo do rotor a 216 mm (os painéis vão a 293, sem conflito) e transforma
7 mm de sobra em 12. **Confirme o layout com as placas reais em mãos antes de
fechar o cubo.** Tudo que entrar aqui precisa ficar centrado: **1 mm de
excentricidade em 48 g já são 48 g·mm**, seis vezes o admissível.
