# Montagem ponto a ponto da interface (sem PCB)

> A PCB r0.2 **não será fabricada**. Este documento substitui a montagem SMD e o
> `fabricacao/mapa-fios.csv` para a versão soldada à mão. O circuito elétrico é
> o mesmo; muda o invólucro, o tamanho e o peso.

Estado de partida: **apenas U1 (74AHCT125) soldado**. Nada mais.

## 0. Antes de soldar: o envelope e o peso

O CAD reserva para a interface **15 × 20 × 8 mm** em (x 19,5…34,5 · y −5…15),
sobre pilares de 6 mm. Esse envelope foi calculado para SMD; uma montagem
manual cresce nos três eixos.

- DIP-14 nu tem ~19,3 × 6,4 mm de corpo e ~3,3 mm de altura. **Com soquete vai a
  8–10 mm** e não cabe nos 8 mm. Sem soquete, com pinos aparados, cabe.
- Resistor de 1/4 W deitado ocupa ~6,3 × 2,3 mm. São 13. Deitados, não cabem em
  300 mm². **Monte os resistores em pé** (um furo em cada ponta): o consumo de
  área cai para ~2 × 2 mm por resistor, ao custo de ~6,5 mm de altura.
- Se o CI for SOIC num adaptador SOP→DIP, a altura estoura. SOIC em breakout
  plano de 1,27 mm, com fios finos, fica baixo.
- **Pese a placa pronta.** O orçamento do CAD é 5,5 g. Cada grama a mais em
  r ≈ 30 mm vale ~30 g·mm contra os 8,4 g·mm admissíveis — refaça o
  balanceamento se passar disso.

Se não couber no envelope, **pare e reposicione** antes de soldar os fios. Não
force a placa contra a tampa nem contra os chicotes.

## 1. Materiais

| Item | Observação |
|---|---|
| Placa perfurada | 1,6 mm, passo 2,54 mm; cortar no tamanho medido na etapa 0 |
| Fio nú 0,5 mm | barramentos de GND e +5V |
| Fio flexível AWG28–30 | fios externos; comprimentos conforme a baia |
| Solda, fluxo, álcool isopropílico | — |
| Kapton e cola quente | alívio de tensão nas saídas de fio |
| Multímetro | continuidade, resistência e tensão |
| Fonte de bancada com limite de corrente | ensaio escalonado |
| Etiquetas ou fita colorida | identificar os 19 fios |

Componentes: U1, R1 R2 R8 R9 (10k), R3 (10k), R4 (150k), R5 (47k),
R6 R10 R11 (33 Ω), R7 R12 R13 (0 Ω ou fio), C1 C3 (100 nF), C2 (1 µF).

## 2. Identificar o CI e marcar a placa

1. Confirme o **pino 1** (ponto/chanfro no corpo; no DIP, o entalhe na ponta).
2. Com o entalhe para cima, a numeração do DIP-14 é:

```
        ┌──────∪──────┐
  GND ──┤1          14├── +5V
  CLK ──┤2          13├── GND
  CLK* ─┤3          12├── D2   (R9 → GND)
  GND ──┤4          11├── DATA P3
  D0 ───┤5          10├── GND
DATA P1 ┤6           9├── D1   (R8 → GND)
  GND ──┤7           8├── DATA P2
        └─────────────┘
```

3. Escreva os números 1…14 na placa, ao lado dos pinos, com caneta permanente.
   Depois de soldado, não dá mais para contar.
4. Teste de curto entre pinos vizinhos: sem continuidade.

## 3. Barramento de GND

1. Passe um fio nú ligando **1 → 4 → 7** pelo lado de baixo.
2. Outro fio ligando **10 → 13**, descendo até o pino 7.
3. Uma perna única de GND sai desse barramento para os fios externos.
4. **Confira:** continuidade entre 1, 4, 7, 10 e 13.

## 4. +5 V e desacoplamento

1. Fio nú do pino 14 até o ponto de +5V.
2. C1 (100 nF) e C2 (1 µF) entre esse ponto e o GND, **colados no pino 14**.
3. **Confira:** +5V sem continuidade com GND.

## 5. Pull-downs das entradas

| Resistor | De | Para |
|---|---|---|
| R1 10k | pino 2 | GND |
| R2 10k | pino 5 | GND |
| R8 10k | pino 9 | GND |
| R9 10k | pino 12 | GND |

**Confira:** ~10 kΩ de cada um dos pinos 2, 5, 9, 12 ao GND.

## 6. Saídas e resistores série

1. R6, R10, R11 (33 Ω) partem todos do **pino 3**, um para cada saída de CLK.
2. Pinos 6, 8 e 11: ponte de fio (R7, R12, R13 de 0 Ω).
3. Deixe um rabicho de ~5 cm em cada saída, etiquetado **P1 CLK**, **P1 DATA**,
   **P2 CLK**, **P2 DATA**, **P3 CLK**, **P3 DATA**.

**Confira:** ~33 Ω do pino 3 a cada CLK; continuidade direta do 6/8/11 ao DATA
correspondente.

## 7. Fios para o ESP32-C3 (9 fios)

Etiquete cada um na ponta. Comprimento conforme a distância até o C3.

| Fio | Solda em |
|---|---|
| 5V | barramento +5V |
| GND | barramento GND |
| 3V3 | topo do R3 (só o pull-up) |
| GPIO4 | nó do pino 2 (CLK) |
| GPIO6 | nó do pino 5 (D0) |
| GPIO5 | nó do pino 9 (D1) |
| GPIO7 | nó do pino 12 (D2) |
| GPIO3 | nó HALL (etapa 8) |
| GPIO0 | nó VBAT_ADC (etapa 9) |

Sugestão: soldar um **header fêmea 1×9** na placa e usar jumpers dupont até o
C3. Facilita trocar o C3 e medir sem dessoldar.

## 8. Hall A3144

Use o sensor **nu**, não o módulo HW-477.

1. R3 (10k) entre o **3V3** e o nó HALL.
2. Fios do sensor: VCC → +5V, GND → GND, OUT → nó HALL.
3. No TO-92, com a face marcada para você e terminais para baixo:
   **1 = VCC, 2 = GND, 3 = OUT**. Confira no componente real.

> O pull-up vai no **3V3**. No 5V ele entrega 5 V no GPIO3 e queima a entrada.

## 9. Divisor de bateria

1. R4 (150k) do fio **VBAT_SW** ao nó VBAT_ADC.
2. R5 (47k) do nó ao GND.
3. C3 (100 nF) do nó ao GND.
4. Fio do nó VBAT_ADC até o GPIO0.

VBAT_SW é a bateria **depois** da chave e do fusível, **antes** do buck.

**Confira:** ~197 kΩ de VBAT_SW ao GND e ~47 kΩ do nó ao GND.

## 10. Conferência sem energia

Com o C3 e os painéis desconectados:

| Medida | Esperado |
|---|---|
| GND: pinos 1, 4, 7, 10, 13 | 0 Ω entre si |
| +5V (14) × GND (7) | aberto |
| 2, 5, 9, 12 × GND | ~10 kΩ cada |
| pino 3 × cada CLK de painel | ~33 Ω |
| 6/8/11 × DATA do painel | 0 Ω |
| nó HALL × 3V3 | ~10 kΩ |
| VBAT_SW × GND | ~197 kΩ |
| nó VBAT_ADC × GND | ~47 kΩ |

Capacitores fazem a leitura subir devagar; espere o multímetro estabilizar.

## 11. Energização em etapas

**11.1 — só o buffer, 5 V da bancada, limite 100 mA, sem C3 e sem fitas.**
Corrente de poucos mA. Saídas 3, 6, 8 e 11 em ~0 V (entradas em nível baixo).

**11.2 — C3 só pelo USB** (bancada desconectada). Confira 3,3 V no topo do R3.
Passe um ímã no Hall: o GPIO3 deve alternar. Aplique 7,2 V em VBAT_SW e meça
~1,72 V no nó VBAT_ADC (1,38 V a 5,8 V).

**11.3 — 5 V pela estrela, USB desconectado, uma fita por vez.**
Limite inicial de 300 mA e brilho baixo no firmware. Nunca alimente painel pelo
pino 5V do C3 nem pelo USB.

**11.4 — as três fitas**, respeitando o teto provisório: f ≤ 80% e corrente
total na saída ≤ 4,25 A.

## 12. Fixação e acabamento

1. Cola quente ou kapton em **cada saída de fio**, a 5 mm da solda.
2. Pontas aparadas, nada passando por baixo da placa.
3. Etiquetas legíveis nos dois lados de cada par.
4. Pesar a placa e comparar com os 5,5 g do CAD. Registrar no diário de montagem.
5. Reinstalar nos pilares sem prender fio entre placa e pilar.

## Anexo A — netlist completa

```
U1.1  = GND
U1.2  = CLK3V3      (R1→GND, fio GPIO4)
U1.3  = CLKBUF       (R6→P1 CLK, R10→P2 CLK, R11→P3 CLK)
U1.4  = GND
U1.5  = D03V3        (R2→GND, fio GPIO6)
U1.6  = P1 DATA
U1.7  = GND
U1.8  = P2 DATA
U1.9  = D13V3        (R8→GND, fio GPIO5)
U1.10 = GND
U1.11 = P3 DATA
U1.12 = D23V3        (R9→GND, fio GPIO7)
U1.13 = GND
U1.14 = +5V          (C1, C2 → GND)

HALL  = R3→+3V3, fio GPIO3, OUT do A3144
VBATADC = R4→VBAT_SW, R5→GND, C3→GND, fio GPIO0
```

## Anexo B — pinagem do ESP32-C3 Super Mini

| Sinal | Pino do módulo |
|---|---|
| Clock SPI | GPIO4 |
| Dados painel 1 | GPIO6 |
| Dados painel 2 | GPIO5 |
| Dados painel 3 | GPIO7 |
| Índice (Hall) | GPIO3 |
| Tensão da bateria | GPIO0 (ADC) |
| Alimentação da placa | 5V |
| Pull-up do Hall | 3V3 |
| Referência | GND |

## Anexo C — o que continua fora da placa

```
bateria + → fusível 7,5 A → chave → VBAT_SW → buck IN+
bateria − → GND comum → buck IN−
buck OUT+ → estrela 5V → 3 painéis +, C3 5V, placa
buck OUT− → estrela GND → 3 painéis −, C3 GND, placa
1000 µF entre 5V e GND, no cubo
```

Os 5 V e o GND de cada painel saem da estrela, **nunca** da placa. A placa leva
apenas CLK e DATA de cada painel.
