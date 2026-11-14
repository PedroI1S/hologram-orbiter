# Lista de componentes — Hologram Orbiter v4.0

Atualizada em 14/11/2026 para a arquitetura **v4.0** (base suspensa em
paralelogramo em PETG + aranha reforçada com baia Ø80/84 × 47 mm + motor
**AX-2810Q 750KV** + topologia **SPI Quad** montada ponto-a-ponto). Preços em
BRL são estimativas de ordem de grandeza para orçamento, não cotações.

Legenda: ✅ já temos · 🛒 comprar / fabricar · ⚠️ decisão ou medição pendente

---

## 1. Peças impressas — PETG (estrutura) e ABS (painéis)

Todas geradas a partir de [`Hologram_Orbiter_v4/CAD/parameters.json`](Hologram_Orbiter_v4/CAD/parameters.json).
As massas são do sólido maciço (`1,27 g/cm³` PETG, `1,04 g/cm³` ABS); peças reais
com infill parcial pesam menos e devem ser pesadas após impressão.

| # | Peça (arquivo `exports/stl/`) | Mat. | Qtd | Vol (cm³) | Massa maciça | Limite |
|---|---|---|---:|---:|---:|---|
| 01 | `01_aranha_PETG.stl` (com aleta em D, alma em asa, baia Ø80/84×47 e prateleira) | PETG | 1 | 91,75 | 116,53 g | ≤ 135 g |
| 02 | `02_painel_LED_ABS_1x.stl` (`_3x_mesma_mesa.stl` para lote) | ABS | 3 | 30,71 | 31,94 g nu | ≤ 45 g montado |
| 03 | `03_tampa_baia_PETG.stl` (Ø84, postes 72 mm, janela + 6 copos) | PETG | 1 | 10,19 | 12,94 g | ≤ 14 g |
| 04 | `04_base_fixa_PETG_imprimir_invertida.stl` (casca cônica, batentes, abas) | PETG | 1 | 335,24 | 425,75 g | — |
| 05 | `05_palco_torre_PETG.stl` (palco, 8 aletas, torre Ø40, 3 ganchos, pás) | PETG | 1 | 389,29 | 494,40 g | — |
| 06 | `06_suporte_ima_PETG.stl` (arco livrando Ø35, 2 pontos M4, poste 26,5) | PETG | 1 | 2,01 | 2,55 g | — |
| 08 | `08_hastes_flexiveis_macia_1p5_8x.stl` (1,5 × 1,5 × 55 livre) | PETG | 2 lotes | 8,40/lote | 1,33 g/haste | 8 + 8 reserva |
| 09 | `09_buchas_trava_4x.stl` (buchas radiais da trava) | PETG/ABS | 1 lote | 4,58/lote | 1,45 g/bucha | 4 peças |
| 10 | `10_bandeja_amortecedor.stl` (opcional — cubas de óleo) | PETG | 1 | 24,34 | 30,92 g | opcional |
| C01 | `C01_cupom_junta.stl` | ABS | 1 | 9,69 | 10,07 g | imprimir 1º |
| C02 | `C02_cupom_canal_LED.stl` | ABS | 1 | 3,40 | 3,53 g | imprimir 1º |
| R01P | `R01P_suporte_motor_PLA_provisorio.stl` + `R01P_arruela_eixo_M4_PLA_provisoria.stl` | PLA | 1 | 7,42 | ~9,2 g | **só baixa rotação** |

**Filamento necessário:** ~1,1 kg de **PETG** (estrutura) e ~0,3–0,5 kg de
**ABS** (cupons + lote dos painéis com margem para retrabalho). Imprimir `C01`
e `C02` antes do lote dos painéis.

---

## 2. Acionamento e parte fixa

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Motor BLDC | **AX-2810Q 750KV**, ~72 g, lata Ø35 × 26 mm (catálogo), **base→serrilhado 29 mm** (medido 13/11), eixo liso Ø4×5 + **bucha Ø6**, rosca **M4×10**, 4×M3 em cruz 16/19, 3 fios Ø3 mm, `R_ef ≈ 0,225 Ω` | ✅ | — |
| ESC | **LittleBee Spring 20A**, `BLHeli_S 16.7` (gravado 13/11: `Brake=On`, `Startup=0,50`, `Demag=High`) | ✅ | — |
| Fonte de bancada | ajustável **10–12 V**, limite de corrente **30 A** | ✅ | — |
| Grampo / resistor de descarga no barramento ESC | limiar entre **12,6 V e 16,8 V** — **obrigatório** com `Brake on stop = On` | 🛒 | a cotar |
| Gerador de sinal do ESC | **ESP32 DevKit 30 pinos** (`firmware/esp32-base/`), também hospedará página web | ✅ | — |
| Botões partida / parada + pull-down ESC | 2 botões momentâneos (`D32`, `D33` ao GND) + `10 kΩ` (`D25` ao GND) | 🛒 | 3 |
| **Chapa R01 em alumínio 2 mm** | 60 × 60 mm, furo central **Ø11 mm** (`fabricacao/R01_*.dxf/.svg`) | 🛒 | 15 |
| **Arruela larga DIN 9021 M4** (aço) | `12 × 4,3 × 1,0 mm` — assenta no topo do cubo (sem rebaixo) | 🛒 | 2 |
| **Porca autotravante M4 DIN 985** (aço, 5 mm) | aperto a **`1,0 N·m`** (~1250 N est.); **não usar** porca-ogiva do motor | 🛒 | 2 |

---

## 3. Óptica e eletrônica de bordo (rotor)

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Fita LED | **HD107S 144 LED/m**, RGB, **12,0 × 2,0 mm**, 29 LEDs/painel (87 totais) | ✅ | — |
| Microcontrolador rotor | **ESP32-C3 Super Mini** (22,5 × 18 × 5 mm, ~3 g) | ✅ | — |
| Regulador 5 V | módulo **mini560 5 V / 5 A** (~2 g) — **qualificar `V_in_min ≤ 5,5 V`** e térmica antes de fechar | ⚠️ | 15 |
| Bateria rotor | **LiFePO4 2S 800 mAh 20C**, 58 × 30 × 17 mm, **50 g**, 6,6 V nominal | ✅ | — |
| Interface **SPI Quad** ponto-a-ponto | placa perfurada ≤ 15 × 20 × 8 mm (≤ 5,5 g), sem soquete (`MONTAGEM-PONTO-A-PONTO.md`) | 🔄 | — |
| Buffer deslocador 3,3 → 5 V | **74AHCT125** (DIP-14 ou SOIC-14; 4 canais: 1 CLK comum + 3 DATA) + `100 nF` + `1 µF` | ✅ | — |
| Resistores na interface | 4× `10 kΩ` (pull-down inputs) + 1× `10 kΩ` (pull-up Hall → 3V3) + **3× `33 Ω`** (série ramos CLK) + `150 kΩ` e `47 kΩ` + `100 nF` (divisor ADC) | ✅/🛒 | 5 |
| Sensor de índice | **A3144 nu** (TO-92 dessoldado do HW-477), VCC **5 V**, saída open-collector pull-up `3V3` → `GPIO3` | ✅ | — |
| Capacitor bulk | **1000 µF / 10 V** eletrolítico (colado na cerca da baia; suporta ~100 g) | 🛒 | 3 |
| Chave liga/desliga + proteção | chave de **curso tangencial** compatível com corrente DC do buck + fusível/polyfuse ~7,5 A | ⚠️ | 8 |
| Conectores bateria | **XT30** (potência) + **JST-XH 3 vias** (balanceamento) | 🛒 | 8 |
| Ímã de índice | neodímio **Ø4 × 2 mm** (N35 ou N52 se entreferro > 3 mm) | 🛒 | 2 |
| Chicote 4 condutores / painel | **AWG 24** (`+5V`, `GND` — ~2 m) + **AWG 28** (`CLK`, `DATA` — ~2 m) | 🛒 | 15 |
| Carregador **modo LiFe** | 3,6 V/célula (modo LiPo 4,2 V destrói o pack) | ⚠️ | 60 |

> **Nota sobre placa própria futura:** a baia v4 (`Ø80 × 47 mm`) reserva em
> `Z = 28..44 mm` uma prateleira com 4 mísulas (furos M2 em `63,2 × 36,5 mm`)
> para eventual PCB integrada de até `Ø74 mm` (chanfros `y = ±30`). Enquanto não
> existir, a montagem ponto-a-ponto + ESP32-C3 + mini560 nos pilares/ranhura
> inferiores permanece o circuito ativo. A PCB `r0.2` em `eletronica/interface/`
> fica como referência não fabricada.

---

## 4. Ferragens mecânicas e suspensão

| Item | Espec | Qtd | Sit. | ~R$ |
|---|---|---:|:--:|---:|
| **Parafusos das 8 hastes** | **M3 × 10** cilíndrico/panela + **porca M3** | 16 + 16 | 🛒 | 8 |
| **Parafusos da trava radial** | **M3 × 40** (ou × 35) + **porca M3** | 4 + 4 | 🛒 | 5 |
| **Parafusos da trava vertical** | **M3 × 10** (batentes) | 4 | 🛒 | 2 |
| Painéis → espigas | **M3 × 40** + **porca plana M3** (2,4 mm; Nyloc não entra) + Loctite 243 | 6 + 6 | 🛒 | 10 |
| Motor AX-2810Q → chapa R01 | **M3 × 6** (cruz 16/19; confirmar folga de rosca no AX antes de apertar) | 4 | 🛒 | 3 |
| Chapa R01 → flange da torre | **M4 × 16** (2) + **M4 × 20** (2, sob a aba do suporte do ímã) + porca Nyloc M4 | 4 + 4 | 🛒 | 5 |
| Tampa da baia | M3 × 10 autoatarraxante | 2 | 🛒 | 2 |
| **Óleo de silicone (opcional)** | **10 000 cSt** (diferencial de automodelo) — ~4 mL/cuba (~17 mL total) | 1 frasco | 🛒 | 35 |
| **EVA firme (opcional)** | tiras `14 × 6 × 6 mm` para bolsos dos batentes | 4 | 🛒 | 5 |
| Massa de balanceamento | fita/massa adesiva de tungstênio ou chumbo | — | 🛒 | 20 |
| Grampos tipo C / parafusos | fixar as **4 abas** da base fixa à bancada | 4 | 🛒 | 30 |

---

## 5. Instrumentação para os bloqueadores

| Item | Espec | Por quê | Sit. |
|---|---|---|---|
| **Balança de precisão** | **0,01 g** | verificar `Δm ≤ 0,084 g` e pesos de contrapeso | 🛒 |
| **Acelerometria** | 2 respostas independentes / MPU6050 (ou celular para mesa travada vs. solta) | ensaio de impacto **C0** + matriz 2 planos **C1** | ⚠️ |
| **Referência angular 1/rev fixa** | sensor óptico/reflexivo sincronizado com vibração | fase do balanceamento em G3 (antes do Hall) | ⚠️ |
| **Medição térmica sem contato / embarcada** | IR calibrado / sensor retido (nunca termopar com fio na campânula girante) | Bloqueador B (motor `< 55 °C`, bateria `< 45 °C`) | ⚠️ |
| **Tacômetro óptico** | leitura direta de RPM | calibrar pulso/RPM do AX-2810Q e checar `≤ 1800 RPM` na partida | ⚠️ |
| **Analisador lógico / osciloscópio** | leitura de SPI 20 MHz + barramento ESC | validar jitter SPI Quad/ESP-NOW e sobretensão na parada | ⚠️ |
| **Contenção fechada** | caixa rígida / **policarbonato** (deixa passar 2,4 GHz) | obrigatória em todo ensaio de giro (`27,6 J` no rotor) | 🛒 |
| Paquímetro digital + Câmera 240 fps | paquímetro 0,01 mm + celular | medições de entrada e inspeção visual (E) | ✅/🛒 |
