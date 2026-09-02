# Medições de entrada pendentes — v3.0

Use paquímetro calibrado, três leituras. Depois de medir, atualize
`CAD/parameters.json` (campo indicado) e rode `scripts/build.sh`.

| # | O que medir | Campo em parameters.json | Valor atual (provisório) | Efeito |
|---|---|---|---|---|
| 1 | Altura da face superior da chapa até a face superior do cubo (com o motor montado) | `unverified_interfaces.motor_stack.plate_top_to_datum_b` | 30,0 | Datum B, altura do rotor, altura do poste do ímã |
| 2 | Eixo: início e fim da rosca M6 a partir da face da campânula; Ø e altura da parte lisa | `unverified_interfaces.shaft.*` | 5 lisos + 7 rosca | Engate da porca baixa; referência na montagem |
| 3 | Diâmetro útil de assento na face superior da campânula (é vazada?) | `unverified_interfaces.bell_seat.useful_seat_diameter` | 25 (assumido) | Se < 20: adaptador de hélice + furos PCD 19 |
| 4 | Padrão de furos do adaptador de hélice (qtd, PCD, Ø) | `unverified_interfaces.adapter_bolt_pattern.*` | 4 × Ø3,2 em PCD 19 | Furos de provisão no cubo |
| 5 | Eixo sai por baixo da base do motor? Quanto? | `motor_plate.center_clearance_diameter` | Ø12 | Furo central da chapa |
| 6 | Cilindro de contenção: ✔ cotas de encomenda em 02/09 (Ø int 266, parede 4, altura 305, sem fundo, com tampa). Falta: **conferir Ø interno e borda na peça recebida** e o ensaio de dobra (PMMA × PC) | `unverified_interfaces.containment.*` (`verified: true`, `source: cota_de_encomenda`) | Ø266 × 305 | Canaleta 4,4 × 3 em r = 135 já no STL; folga vertical 17 mm; folga radial 26,5 mm |
| 7 | Bateria comprada: comprimento, largura, altura, massa | `unverified_interfaces.battery.*`, `spider.battery_cradle.pack_*` | 57 × 30 × 13, 48 g | Berço, orçamento de massa |
| 8 | Placa ESP32, regulador 5 V, chave e conector de carga: dimensões e posição | `lid.access_window`, faixa livre x = 17…25 | placeholder | Janela da tampa, folga de 15 g na massa |
| 9 | Sensor hall (encapsulamento) e ímã (Ø × h) | `unverified_interfaces.hall_sensor`, `.magnet` | TO-92, Ø4 × 2 | Bolso do cubo, alojamento do poste |
| 10 | Porca M6 baixa e arruela escolhidas: altura e espessura | `unverified_interfaces.m6_nut.*` | 6,0 + 1,6 | Altura dos trilhos do berço (Z = 6) |
| 11 | Impressora: modelo e área útil real da mesa | `fdm_rules.printer_bed_mm`, `brim_mm` | 300 × 300, brim 8 | Base Ø280 + brim = 296 |

Fotografar a campânula e o adaptador com escala no mesmo plano.
