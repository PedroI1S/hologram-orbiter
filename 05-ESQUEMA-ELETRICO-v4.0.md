# Esquema elétrico — Hologram Orbiter v4.0

Duas cadeias elétricas independentes, que **não se tocam**. Não há anel coletor.

**No rotor** (§1 a §7): bateria LiFePO4 2S, chave/proteção, buck 5 V,
**ESP32-C3 Super Mini**, **interface SPI Quad** (buffer `74AHCT125` +
divisor + pull-up do Hall), sensor **A3144 nu** e as três fitas HD107S em
**4 condutores por painel**.

**Na parte fixa** (§8): fonte de bancada 10–12 V (30 A), grampo/resistor de
descarga, ESC LittleBee Spring 20A (`Brake on stop = On`), **motor AX-2810Q
750KV**, ESP32 da base e o ímã fixo `Ø4 × 2`.

**Entre as duas** (§9): enlace **ESP-NOW** da ESP32 da base (portal cativo/web)
para o ESP32-C3 do rotor (somente imagem, nunca comando de motor).

**Estado em 14/11/2026:** a topologia **SPI Quad** já está implementada na
placa perfurada ponto-a-ponto ([`MONTAGEM-PONTO-A-PONTO.md`](eletronica/interface/MONTAGEM-PONTO-A-PONTO.md))
e em teste inicial de bancada via [`firmware/teste-fitas-c3/`](firmware/teste-fitas-c3/).
O motor AX-2810Q e o ESC foram gravados e testados sem carga em
[`esc_blheli_s_2026-11-13/`](esc_blheli_s_2026-11-13/). A placa própria futura
prevista para a prateleira `Z = 28 mm` da baia Ø80/84×47 mm ainda não foi
projetada.

---

## 1. Topologia do rotor (SPI Quad implementado)

```
Bateria 2S LiFe ── chave (tangencial) ── fusível 7,5 A ─┬─► divisor 150k/47k + 100 nF ──► GPIO0 (ADC)
                                                        │
                                                        └─► buck 5,0 V ──┬─ C bulk 1000 µF
                                                                         │
      ┌──────────────────────────────────────────────────────────────────┤
      │ (estrela de potência 5 V / GND — NUNCA passar pela perfboard)    │
      ▼                                                                  ▼
 Painéis 1, 2 e 3 (+5 V e GND, AWG 24)                          ESP32-C3 (5V/GND), A3144 (VCC 5V) e 74AHCT125

ESP32-C3 (3,3 V)                                     74AHCT125 (5 V)
  GPIO4 (SPI CLK)  ──[R1 10k→GND]──► pino 2  →  pino 3 ──┬──[R6  33 Ω]──► Painel 1 CLK
                                                         ├──[R10 33 Ω]──► Painel 2 CLK
                                                         └──[R11 33 Ω]──► Painel 3 CLK
  GPIO6 (DATA P1)  ──[R2 10k→GND]──► pino 5  →  pino 6 ─────────────────► Painel 1 DATA
  GPIO5 (DATA P2)  ──[R8 10k→GND]──► pino 9  →  pino 8 ─────────────────► Painel 2 DATA
  GPIO7 (DATA P3)  ──[R9 10k→GND]──► pino 12 →  pino 11 ────────────────► Painel 3 DATA
  GPIO3 (ÍNDICE)   ◄───[R3 10k→3V3]────────────────────────────────────── A3144 OUT (coletor aberto)
```

**Potência em estrela, dados em paralelo (SPI Quad).** Cada painel recebe
**apenas 4 fios** do cubo (`+5 V`, `GND`, `CLK` e seu `DATA` dedicado); não há
retorno na ponta superior da fita, eliminando 6 fios extras e a defasagem serial
de `0,5°` e `1,0°` entre painéis da v3.0.

---

## 2. Armadilhas críticas (inalteradas)

### 2.1 Sensor Hall A3144 nu (não usar placa HW-477)
- O A3144 opera de **4,5 a 24 V**; alimentá-lo com **5 V**, mas com o
  **pull-up de `10 kΩ` ligado exclusivamente a `3V3` do ESP32-C3** (saída
  open-collector oscila 0–3,3 V). Pull-up em 5 V queima o `GPIO3`.
- Usar o TO-92 **nu** dessoldado do HW-477 (`0,2 g` no bolso `r = 29, az = 20°`).

### 2.2 Deslocamento de nível (`74AHCT125`) + pull-downs de boot
- A HD107S pede `V_IH ≥ 3,5 V` em 5 V. O `74AHCT125` converte `3,3 V → 5 V`,
  com todos os `/OE` (pinos 1, 4, 10, 13) aterrados e `100 nF` + `1 µF` no pino 14.
- **4 × `10 kΩ` ao GND** nas entradas de `CLK` e `D0/D1/D2` evitam que a fita
  receba ruído e acenda em branco pleno no reset antes do SPI inicializar.
- **3 × `33 Ω`** na saída comum de `CLK` (pino 3) amortecem reflexões nos
  três ramos idênticos de ~10 cm até os painéis.

---

## 3. Pinos do ESP32-C3 Super Mini

| Sinal | Pino | Ligações / nota |
|---|---|---|
| `SPI CLK` | **GPIO4** | entrada pino 2 do `74AHCT125` + pull-down `10 kΩ` → pino 3 → `3 × 33 Ω` |
| `DATA Painel 1` | **GPIO6** | entrada pino 5 do `74AHCT125` + pull-down `10 kΩ` → pino 6 |
| `DATA Painel 2` | **GPIO5** | entrada pino 9 do `74AHCT125` + pull-down `10 kΩ` → pino 8 |
| `DATA Painel 3` | **GPIO7** | entrada pino 12 do `74AHCT125` + pull-down `10 kΩ` → pino 11 |
| `ÍNDICE` | **GPIO3** | saída open-collector do A3144 + pull-up `10 kΩ` → `3V3` (borda de descida) |
| `V_BAT` | **GPIO0 (ADC)** | divisor **`150 kΩ / 47 kΩ`** + **`100 nF`** ao GND no pino (`1,72 V` @ 7,2 V · `1,38 V` @ 5,8 V) |
| `5V` / `3V3` / `GND` | pinos de alimentação | derivação da estrela (sem corrente de LEDs pelo C3) |

*(GPIO10 fica livre caso seja necessário usar o 4º bit de um periférico SPI Quad
por hardware no ESP-IDF/hal.)*

---

## 4. Chicote por longarina — 4 condutores idênticos

O sulco da aranha (`4,4 × 3 mm`, entrada pela parede da baia Ø80 em `r = 38–43`)
carrega **4 fios por painel**:

| Condutor | Bitola | Corrente máx. (80%) | Destino |
|---|---|---:|---|
| `+5 V` | AWG 24 | ~1,4 A | estrela 5 V do buck |
| `GND` | AWG 24 | ~1,4 A | estrela GND do buck |
| `CLK` | AWG 28 | sinal | resistor 33 Ω na interface (R6 / R10 / R11) |
| `DATA` | AWG 28 | sinal | pino 6, 8 ou 11 do `74AHCT125` |

Pesar os três chicotes reais para manter simetria exata (`Δm ≤ 0,084 g`).

---

## 5. Orçamento de energia e janela SPI Quad

- **Consumo estimado dos LEDs:** 87 × 60 mA × 5 V = `26,1 W` (100% branco) +
  `0,3 W` ESP32-C3. Até qualificar o buck `mini560` real (tensão mínima `≤ 5,5 V`
  e térmica), manter teto provisório **`f ≤ 80%`** e **`I_saída ≤ 4,25 A`**.
- **Temporização SPI Quad:** cada painel tem apenas **29 LEDs** por quadro
  (`32 + 29 × 32 + 32 = 992 bits`). A `20 MHz` em paralelo, um quadro dura
  **`49,6 µs`** dentro da janela de `185,19 µs` (`1800 RPM × 180 colunas`),
  deixando **`~135,6 µs`** de folga (mais do triplo da v3.0 em cadeia), além de
  permitir clocks mais baixos caso o divisor/cabo exija.

---

## 6. Interface física e prateleira na baia (v4.0)

1. **Configuração ativa de bancada (ponto-a-ponto):**
   - Placa perfurada **15 × 20 × 8 mm** (`≤ 5,5 g`, CI soldado direto sem soquete,
     resistores em pé) nos pilares `+x` (`x = 19,5..34,5`, `y = −5..+15`, `Z = 6..14`),
     seguindo [`eletronica/interface/MONTAGEM-PONTO-A-PONTO.md`](eletronica/interface/MONTAGEM-PONTO-A-PONTO.md).
   - ESP32-C3 em `−x` (`x = −36..−18`, `Z = 6..11`), buck `mini560` na ranhura a
     `140°`, capacitor `1000 µF` na cerca em `(22,5; −22)`, bateria LiFe `58 × 30 × 17`
     sobre trilhos em `Z = 10..27`.
2. **Reserva para placa própria futura:**
   - Baia **Ø80/84 × 47 mm** com prateleira de 4 mísulas em **`Z = 28 mm`**
     (retângulo M2 `63,2 × 36,5 mm`, envelope máximo `Ø74` com chanfros em `y = ±30`).
3. **Referência PCB não fabricada:**
   - Arquivos KiCad `r0.2` preservados em [`eletronica/interface/README.md`](eletronica/interface/README.md).

---

## 7. Acionamento na parte fixa (`AX-2810Q 750KV`)

```
Fonte 10–12 V (30 A) ──┬──► ESC LittleBee Spring 20A ──► AX-2810Q 750KV (3 fios Ø3 mm nos ganchos)
                       │         ▲ PWM servo (D25 + pull-down 10k)
  [Grampo / Resistor] ─┘         │
  (12,6 V < V < 16,8 V)     ESP32 da base (GPIO D32 partida, D33 parada, USB)
```

### 7.1 Configuração do ESC gravada em 13/11/2026 (`BLHeli_S 16.7`)

Registrado e verificado por releitura em [`esc_blheli_s_2026-11-13/`](esc_blheli_s_2026-11-13/):

| Parâmetro | Valor gravado | Motivo na v4.0 |
|---|---|---|
| `Startup Power` | **0,50** | +22% `Kt` no AX-2810Q (`R ≈ 0,225 Ω`) |
| `Demag Compensation` | **High** | proteção contra dessincronismo em rotor de alta inércia |
| `Motor Timing` | **Medium** | padrão 12N14P baixo Kv |
| `Low RPM Power Protection` | **Off** | evita corte em 16–20% da rotação a vazio |
| **`Brake on stop`** | **On** | **obrigatório** na suspensão para cruzar a crítica (`~263 RPM`) rapidamente (`~1,5 s`); **exige grampo no barramento** |
| `Direction` | **Normal** (confirmar giro anti-horário!) | ainda pendente confirmar sentido físico com o AX-2810Q |
| `PPM Min / Max` | `1148 / 1832 µs` | manter compatibilidade com `firmware/` |

### 7.2 Pedidos atualizados ao firmware da base (`firmware/controle-motor`)

Em relação à versão `0.3.0` (`1148–1831 µs`):
- Atravessar **`200–400 RPM` a `≥ 300 RPM/s`** (`≥ 50 µs/s` acima de `1200 µs`).
- Manter alvo mínimo em **`≥ 1200 µs`** e **não estacionar entre `760` e `870 RPM`**
  (modo de giro do palco).
- Recalcular/limitar o pulso de chute (`≤ 0,1 N·m` ou partir travado se
  necessário) para atender ao Bloqueador D (`P ≤ 36,1 W` e `RPM ≤ 1800`) e
  calibrar `CEILING_US` com tacômetro no `AX-2810Q` (~1350–1450 µs previstos a 10–12 V).

---

## 8. Enlace de imagem por ESP-NOW

Sem mudança de protocolo em relação à v3.0: página web + fila + aprovação
rodando no **Núcleo 0** da ESP32 da base (enquanto o PWM do motor roda por LEDC
no **Núcleo 1**, **sem nenhuma rota web capaz de comandar o motor**), enviando
quadros de `180 × 29` RGB ou carrossel `3 × 60 × 29` por ESP-NOW (com CRC-32)
ao ESP32-C3 do rotor, que atualiza no pulso do sensor Hall.
