# Medições de entrada — Hologram Orbiter v4.0

Use paquímetro calibrado (três leituras) ou balança de `0,01 g`. Depois de
medir, atualize [`../CAD/parameters.json`](../CAD/parameters.json) (campo
indicado) e rode `./scripts/build.sh`. Estado atualizado em **14/11/2026**.

## Já medidas em bancada

| O quê | Valor | Campo em `CAD/parameters.json` |
|---|---|---|
| Base de assentamento do `AX-2810Q` | chapa → topo da base serrilhada **`29 mm`** (`Ø13`), fios `Ø3,0 mm`, lata **`Ø35 mm`** (`13/11/2026`) | `unverified_interfaces.motor_stack.*`, `unverified_interfaces.bell_seat`, `unverified_interfaces.motor.*` |
| Eixo do `AX-2810Q` | trecho liso **`Ø4 × 5 mm`** (c/ bucha **`Ø6`**), rosca **`M4 × 10 mm`** (`13/11/2026`) | `unverified_interfaces.shaft.*` |
| Furação da base do `AX-2810Q` | cruz, diagonais **`16` e `19 mm`**, `4 × M3` (`13/11/2026`) | `unverified_interfaces.motor.base_bolt_*` |
| Resistência efetiva por fase | **`0,4–0,5 Ω`** linha-linha descontadas as pontas (`5,3–5,4 Ω − 4,9 Ω`), adotado **`0,225 Ω/fase`** (`±25 %`, `13/11/2026`) | `physics_assumptions.effective_resistance_ohm` |
| Configuração gravada no ESC | `BLHeli_S 16.7`: `Startup Power 0,50`, `Demag High`, `Brake on stop On`, PPM `1148–1832 µs` (`13/11/2026`) | `startup_kick.ppm_*` + [`../../esc_blheli_s_2026-11-13/`](../../esc_blheli_s_2026-11-13/registro.md) |
| Fita HD107S | `12,0 × 2,0 mm` (PCB `~0,4` + 5050 `~1,6`) (`02/09/2026`) | `unverified_interfaces.led_strip` → canal `12,4 × 2,0` |
| Bateria LiFe 2S 800 mAh | `58 × 30 × 17 mm`, `50 g` (`02/09/2026`) | `unverified_interfaces.battery`, `spider.battery_cradle`, `non_cad_masses_g.battery_pack` |
| Módulo Hall HW-477 | placa `18 × 15`; vai **nu** (`A3144` TO-92) no bolso do cubo | `unverified_interfaces.hall_sensor` |

## Ainda pendentes

| # | O que medir | Campo em `parameters.json` | Valor atual (provisório) | Efeito |
|---|---|---|---|---|
| 1 | **Altura real do corpo do `AX-2810Q`** (divisão exata campânula × base serrilhada) | `unverified_interfaces.motor.body_height`, `motor_stack.plate_top_to_bell_face`, `shaft.boss_height` | `26 mm` de catálogo (`+ 3 mm` serrilhado = `29 mm` medido) | Folga cubo–campânula e cota real do **entreferro do Hall** (`2,5 mm` nominais) |
| 2 | **Chapa R01 em alumínio `2 mm` e alívio `Ø11`** (folga fios/cabeças M3 em `r = 8`) + **arruela `DIN 9021 M4`** e **porca `DIN 985 M4`** reais | `motor_plate.center_clearance_diameter`, `unverified_interfaces.m6_nut.*` | alívio `Ø11`; arruela `12 × 4,3 × 1,0`, porca `5 mm` | Assento no cubo PETG (`Ø6`), pré-carga `1,0 N·m` e sobra de rosca (`+3 mm`) |
| 3 | **Massa e envelope reais da eletrônica da baia** (perfboard SPI Quad montada, ESP32-C3, `mini560`, capacitor `1000 µF`, chave/fusível/fios e futura placa própria) | `spider.bay_layout.components[*]`, `non_cad_masses_g.onboard_electronics_allowance` | `5,5 + 3,0 + 2,0 + 2,5 + 2,0 + 14,0 = 29,0 g` (folga `40 g`) | Subtotal até `420 g`, contrapesos reais e janela da tampa |
| 4 | **Ímã `Ø4 × 2`:** dimensões reais, polaridade (`VCC = 5 V`, pull-up `3,3 V`) e campo espúrio do `AX-2810Q` no `A3144` | `unverified_interfaces.magnet.*`, `magnet_bracket.magnet_pocket_*` | `Ø4 × 2 mm`; `polarity_bench_confirmed: false` | Posição do pulso de índice e garantia de comutação sem falso disparo |
| 5 | **Chicotes SPI Quad de 4 condutores** (`+5 V`, `GND`, `CLK`, `DATA`) e ferragens de cada painel + massa real das peças impressas (PETG + ABS) | `unverified_interfaces.panel_wiring.*`, `non_cad_masses_g.*` | `panel_assembled ≈ 42,14 g`, `rotor = 352,14 g` (densidade maciça) | Reconciliar balanço (`Δm ≤ 0,084 g`), centro de gravidade e teto de `420 g` |
| 6 | **Impressora:** modelo e área útil real da mesa | `fdm_rules.printer_bed_mm`, `brim_mm` | `300 × 300`, brim `8` | Base fixa invertida + brim dá `296 × 296 mm` |
| 7 | **Ensaio de impacto `C0` da suspensão em paralelogramo** (palco vazio e com rotor; modo solto e travado; com/sem óleo) | `base_tower.suspension.rod.modulus_mpa`, `moving_mass_*` | `E_PETG = 1900 MPa`, translação `4,38 Hz`, combinado `89,3 Hz` | Confirma frequência crítica (`~263 RPM`), modo combinado (`< 95 Hz → teto 1643 RPM`) e amortecimento |

Além das medições dimensionais e de massa, permanecem obrigatórios os
bloqueadores físicos do plano [`04-PLANO-DE-ENSAIOS-v4.0.md`](../../04-PLANO-DE-ENSAIOS-v4.0.md):
resistência/fluência FDM, potência e térmica do `AX-2810Q`, balanceamento em
dois planos, calibração do pulso por tacômetro e partida revisada com grampo no
barramento do ESC.
