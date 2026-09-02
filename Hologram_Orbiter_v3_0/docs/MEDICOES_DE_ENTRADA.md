# Medições de entrada pendentes — v3.0

Use paquímetro calibrado, três leituras. Depois de medir, atualize
`CAD/parameters.json` (campo indicado) e rode `scripts/build.sh`.

| # | O que medir | Campo em parameters.json | Valor atual (provisório) | Efeito |
|---|---|---|---|---|
| 1 | Altura da face superior da chapa até a face superior do cubo (com o motor montado) | `unverified_interfaces.motor_stack.plate_top_to_datum_b` | 30,0 | Datum B, altura do rotor, altura do poste do ímã |
| 5 | Eixo sai por baixo da base do motor? Quanto? | `motor_plate.center_clearance_diameter` | Ø12 | Furo central da chapa |
| 7 | Bateria comprada: comprimento, largura, altura, massa | `unverified_interfaces.battery.*`, `spider.battery_cradle.pack_*` | 57 × 30 × 13, 48 g | Berço, orçamento de massa |
| 8 | Placa ESP32, regulador 5 V, chave e conector de carga: dimensões e posição | `lid.access_window`, faixa livre x = 17…25 | placeholder | Janela da tampa, folga de 15 g na massa |
| 9 | Sensor hall (encapsulamento) e ímã (Ø × h) | `unverified_interfaces.hall_sensor`, `.magnet` | TO-92, Ø4 × 2 | Bolso do cubo, alojamento do poste |
| 10 | Porca M6 baixa e arruela escolhidas: altura e espessura | `unverified_interfaces.m6_nut.*` | 6,0 + 1,6 | Altura dos trilhos do berço (Z = 6) |
| 11 | Impressora: modelo e área útil real da mesa | `fdm_rules.printer_bed_mm`, `brim_mm` | 300 × 300, brim 8 | Base Ø280 + brim = 296 |

