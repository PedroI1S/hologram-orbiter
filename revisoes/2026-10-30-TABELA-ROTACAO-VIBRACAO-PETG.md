# Tabela estimada de rotação e vibração — torre maciça em PETG

Condições informadas pelo operador: fonte de 10,4 V; rotor de 179,5 g sem
circuito; torre maciça em PETG, sem o furo central de Ø22 mm.
Geometria de referência: Ø30 × 150 mm. Motor de 52 g e chapa de 18 g,
CG a 31 mm acima da torre, conforme hipóteses do registro associado.

Cenários de frequência natural: 53,7 / 58,8 / 63,5 Hz, para módulos E de
1,5 / 1,8 / 2,1 GPa, respectivamente. A faixa entre cenários não é um
intervalo de confiança nem um envelope garantido de todas as ressonâncias.

| Pulso (µs) | RPM estimada | 1× (Hz) | 2× (Hz) | 3× (Hz) | Coincidência possível¹ |
|---|---:|---:|---:|---:|---|
| 1000 — parada | 0 | 0 | 0 | 0 | — |
| 1150 | 28 | 0,46 | 0,92 | 1,39 | — |
| 1160 | 160 | 2,67 | 5,33 | 8,00 | — |
| 1170 | 283 | 4,71 | 9,43 | 14,14 | — |
| 1180 | 398 | 6,64 | 13,28 | 19,92 | — |
| 1190 | 508 | 8,46 | 16,92 | 25,38 | — |
| 1200 | 611 | 10,19 | 20,38 | 30,57 | — |
| 1210 | 710 | 11,84 | 23,68 | 35,52 | — |
| 1220 | 806 | 13,43 | 26,85 | 40,28 | — |
| 1230 | 897 | 14,95 | 29,90 | 44,85 | — |
| 1240 | 985 | 16,42 | 32,84 | 49,27 | — |
| 1250 | 1071 | 17,85 | 35,69 | 53,54 | Próximo de 3× |
| 1260 | 1153 | 19,22 | 38,45 | 57,67 | 3× |
| 1270 | 1234 | 20,56 | 41,13 | 61,69 | 3× |
| 1280 | 1312 | 21,86 | 43,73 | 65,59 | — |
| 1290 | 1388 | 23,13 | 46,26 | 69,40 | — |
| 1300 | 1462 | 24,37 | 48,74 | 73,11 | — |
| 1310 | 1535 | 25,58 | 51,15 | 76,73 | — |
| 1320 | 1605 | 26,76 | 53,51 | 80,27 | Próximo de 2× |
| 1330 | 1675 | 27,91 | 55,82 | 83,73 | 2× |
| 1340 | 1743 | 29,04 | 58,08 | 87,13 | 2× |
| 1350 | 1809 | 30,15 | 60,30 | 90,45 | 2× |

¹ Coincidência de 2× ou 3× a frequência de giro com 53,7–63,5 Hz. A coluna
não indica ressonância medida. “—” significa apenas que 1×, 2× e 3× não
coincidem com essa faixa nos cálculos; não comprova operação sem ressonância.
1000 µs é comando de parada; 0 RPM aplica-se após cessar o movimento.
1150 µs é extrapolação próxima de acelerador zero e não garante partida.

## Faixas calculadas

| Componente | RPM estimada de coincidência | Pulso estimado | Cenário intermediário |
|---|---:|---:|---|
| 1× | 3220–3810 | 1609–1743 µs, fora do teto | 3528 RPM / 1677 µs |
| 2× | 1610–1905 | 1321–1365 µs | 1764 RPM / 1343 µs |
| 3× | 1073–1270 | 1250–1275 µs | 1176 RPM / 1263 µs |

O teto de 1350 µs fica dentro da faixa calculada de coincidência em 2×.
Pulsos fora dessas faixas não são patamares validados. Acelerar ou desacelerar
até um alvo também pode atravessar as faixas. O plano 04 prevê impacto com o
motor desenergizado e a montagem/fixação reais para medir a frequência natural;
o relato de ruptura e a pendência R02 continuam sem liberação por esta tabela.

## Modelo e limites

Usa-se o arrasto do rotor completo do CAD: 4,95 A a 1800 RPM, motor de
920 KV e resistência efetiva de 0,221 Ω. A remoção do circuito não foi usada
para reduzir o arrasto proporcionalmente ao peso. O arrasto real diferente,
a tensão real no barramento, a resposta do ESC e a comutação podem deslocar
a correspondência entre pulso e RPM. Confirmar RPM com tacômetro.

`d = (pulso_us − 1148)/684`

`Kt = 60/(2π × 920)`

`A = 0,221 × 4,95 / ω_1800²`

`ω = 2dV / [Kt + sqrt(Kt² + 4AdV)]`

`RPM = 60ω/(2π)`; frequências de ordem n: `f_n = n × RPM/60`.

A estimativa estrutural e suas hipóteses estão no
[registro da torre maciça](2026-10-30-TORRE-MACICA-PETG.md).
