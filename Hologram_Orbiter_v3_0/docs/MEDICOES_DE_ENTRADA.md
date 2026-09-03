# Medições de entrada — v3.0

Use paquímetro calibrado, três leituras. Depois de medir, atualize
`CAD/parameters.json` (campo indicado) e rode `scripts/build.sh`. Estado em
03/09/2026.

## Já medidas ou fechadas pelo desenho cotado do motor

| O quê | Valor | Campo |
|---|---|---|
| Corpo do motor | Ø27,8 × 24 mm → Datum B = chapa + 30 | `unverified_interfaces.motor.body_*`, `motor_stack.plate_top_to_bell_face` |
| Face de apoio da campânula | plana, 5 raios; só o ressalto/colar do eixo no centro (entra no furo Ø8) | `unverified_interfaces.bell_seat` |
| Eixo (desenho) | colar Ø8 × 5 + rosca M6 × 7 numa saliência total de 14; ressalto Ø6,9 × 2 assumido sob o colar | `unverified_interfaces.shaft.*` |
| Fita HD107S | 12,0 × 2,0 mm (PCB ~0,4 + 5050 de 1,5–1,6) | `unverified_interfaces.led_strip` → canal 12,4 × 2,0 |
| Bateria LiFe 2S 800 mAh | 58 × 30 × 17 mm, 50 g | `unverified_interfaces.battery`, `spider.battery_cradle.pack_*`, `non_cad_masses_g.battery_pack` |
| Módulo hall HW-477 | placa 18 × 15; vai **nu** (TO-92) no bolso do cubo | `unverified_interfaces.hall_sensor` |
| Cilindro encomendado (provisão) | Ø int 266, parede 4, altura 305 | `unverified_interfaces.containment` |

## Ainda pendentes

| # | O que medir | Campo em parameters.json | Valor atual (provisório) | Efeito |
|---|---|---|---|---|
| 1 | **Eixo, a partir da face em que o cubo assenta: altura do topo do colar Ø8 e da ponta da rosca; Ø do colar** | `shaft.collar_top_above_bell`, `shaft.protrusion_above_bell`, `shaft.collar_diameter` | 7 · 14 · Ø8 (desenho; a soma 5 + 7 = 12 não fecha com 14) | Rosca sobrando (3 ou 1 mm), colar × arruela, furo do cubo |
| 2 | Eixo sai por baixo da base do motor? Quanto? | `motor_plate.center_clearance_diameter` | Ø12 | Furo central da chapa |
| 3 | Arruela cortada e porca fina compradas: espessura e altura reais | `unverified_interfaces.m6_nut.washer_thickness`, `.height` | 2,0 · 3,0 | Topo da porca (+5) contra os trilhos (Z = 9) |
| 4 | **Massa e envelope de cada componente da baia** (placa de interface, ESP32-C3, mini560, capacitor, fios) | `spider.bay_layout.components[*].mass_g`, `size_xyz`, `center_xy` | catálogo: 5,5 · 3,0 · 2,0 · 2,5 · 2,0 g | Folga do rotor (1,4 g), contrapeso (3,1 g), janela da tampa |
| 5 | Ímã: Ø × h e polaridade (face voltada ao sensor) | `unverified_interfaces.magnet`, `magnet_bracket.magnet_pocket_*` | Ø4 × 2 | Alojamento no poste, pulso de índice |
| 6 | Impressora: modelo e área útil real da mesa | `fdm_rules.printer_bed_mm`, `brim_mm` | 300 × 300, brim 8 | Base Ø280 + abas nos cantos + brim = 296 |
| 7 | Massa real das peças impressas (painéis, aranha, tampa) | — | densidade maciça no CAD | Orçamento do rotor |
