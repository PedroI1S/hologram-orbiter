# Critérios de aceitação — Hologram Orbiter v3.0

Verificação automática a partir do modelo (spec §9). Gerado por `CAD/generate.py`.
Valores marcados como medidos vêm de traçado de raios na malha final (`CAD/probe.py`),
não dos parâmetros de entrada.

| Critério | Valor no modelo | Requisito | Resultado | Nota |
|---|---:|---|:---:|---|
| Raio do plano médio do painel | 100.0 | 100 ±0,1 mm | ✅ | medido: ombro da longarina na malha da aranha ([74.0, 74.0, 74.0]) + 26 da face de contato |
| Datum D | 104.0 | 104 ±0,2 mm | ✅ | da malha do painel |
| Δh entre painéis | 0.0 | ≤ ±0,5 mm | ✅ | os três painéis são o mesmo STL |
| Ponta da espiga | 96.0 – 96.0 – 96.0 | 96 ±0,1 mm | ✅ | medido na malha |
| Profundidade do socket | 22.5 | 22.5 ±0,1 mm | ✅ | medido: primeiro material no eixo do socket |
| Parede entre o fundo do socket e a cavidade | 1.5 | ≥ 1,2 mm | ✅ | medido |
| Piso sob o canal do LED | 0.8 | ≥ 0,6 mm (nominal 0.80) | ✅ | medido a meia altura no centro; na borda do canal: 0.8; na junta: 0.8. Ponte de 12.4 mm |
| Terra entre o piso e a parede de 2,0 | 2.8 | ≥ 2,0 mm (parede local 2,8 em 1 mm de cada lado do canal) | ✅ | medido |
| Furos M3 livres em toda a torre | True – True | livres (sem pino de casca invertida) | ✅ | raio ao longo do eixo de cada parafuso: enrolamento 0 em toda a extensão (06-PENDENCIAS A1) |
| Bolso da porca M3 e torre | 2.8 – 2.8 | bolso 2.8 ±0,1 mm; torre sólida de −15,2 a +18, só o socket (z ±3.1) a interrompe | ✅ | medido ao longo do eixo de cada parafuso; vãos: [[[-3.1, 3.1]], [[-3.1, 3.1]]] |
| Parede ao redor do bolso de porca | 1.65 | ≥ 1,5 mm | ✅ | geometria: torre Ø10, hexágono de circunraio 3,35 |
| Casca da carenagem | 0.8 | 0.8 ±0,05 mm | ✅ | medido no flanco plano |
| Menor parede estrutural do modelo | 0.8 | ≥ 0,8 mm | ✅ | mínimo entre piso do canal, casca da carenagem, borda do disco fora dos rasgos, pele da tampa e nervuras (1,0 mm, conforme spec §5.1) |
| Enrolamento por raios — painel | 0 – 0 | 0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm | ✅ | 18719 raios, passo 1.0 mm |
| Enrolamento por raios — aranha | 0 – 0 | 0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm | ✅ | 16660 raios, passo 1.5 mm |
| Enrolamento por raios — tampa | 0 – 0 | 0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm | ✅ | 7885 raios, passo 1.0 mm |
| Enrolamento por raios — base | 0 – 0 | 0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm | ✅ | 18612 raios, passo 3.0 mm |
| Enrolamento por raios — suporte do ímã | 0 – 0 | 0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm | ✅ | 10195 raios, passo 0.5 mm |
| Furo do cubo livre | True | livre | ✅ | Ø8.0 para eixo medido em Ø8.0 |
| Rebaixo da arruela | 0.0 | 0.0 ±0,1 mm (zero: arruela no topo do cubo) | ✅ | medido; 6.0 mm de cubo sob a arruela |
| Pele sobre os alívios do cubo | 2.0 | ≥ 2,0 mm | ✅ | medido |
| Arruela passa pelo colar Ø8.0 do eixo | 0.5 | furo − colar ≥ 0,3 mm | ✅ | arruela Ø20 × Ø8.5 × 2.0 (aluminio 2 mm, cortada da mesma chapa da R01 (referencia de corte inclui o disco)). Uma arruela M6 (furo 6,4) assentaria no colar e a porca não apertaria o cubo |
| Porca não toca o colar do eixo | 1.0 | topo da arruela ≥ topo do colar + 0,5 mm | ✅ | colar até 1.0 acima do topo do cubo (desenho: ressalto 2 + colar 5); arruela até 2.0 |
| Rosca sobrando acima da porca | 3.0 | ≥ 1 mm | ✅ | eixo de 14 mm acima da campânula (desenho; não medido); na leitura de 12 mm sobrariam 1.0. Porca fina de 3 mm sobre arruela de 2.0, sem rebaixo; trava química no lugar do anel de nylon |
| Trilhos do berço acima da porca | 9.0 | ≥ 5.0 mm (topo da porca) | ✅ |  |
| Fundo da bateria acima da ponta do eixo | 1.0 – 3.0 | ≥ 1,0 mm nas duas leituras do eixo (14 e 12 mm sobre a campânula) | ✅ | piso medido na malha em Z = 9.0; ponta do eixo em +8.0 (leitura de 14) e +6.0 (leitura de 12). Critério novo: o eixo é mais alto que a porca e nenhum critério os comparava |
| Assento da arruela livre acima do cubo | 10.5 | menor raio sólido ≥ 10.3 mm (raio da arruela + 0,3) | ✅ | varredura de 360 raios na espessura da arruela; os trilhos do berço são o material mais interno |
| Bateria cabe na baia sobre a porca | 26.0 | ≤ 29 mm | ✅ | pack de 17 mm sobre trilhos em Z=9 |
| Berço da bateria dentro da baia (meia-diagonal) | 32.26 | ≤ 39 mm | ✅ | abas de topo inclusas |
| Layout da baia: envelope, interferências e faixas dos feixes | ok | tudo dentro de r = 38,5 e Z ≤ 25, sem interferência, piso livre nas faixas dos feixes | ✅ | 4 componentes; pilares em [[21.5, -3.0], [32.5, -3.0], [32.5, 13.0], [21.5, 13.0], [-34.0, -9.25], [-20.0, -9.25], [-20.0, 9.25], [-34.0, 9.25]] |
| Eletrônica embarcada (estimada) dentro da folga | 15.0 | ≤ 15 g | ✅ | massas de catálogo, não pesadas; o XL4015 sozinho (~18 g) estouraria |
| Contrapeso planejado do layout | 2.19 – 0.87 | cabe nos alívios (≤ 13.9 g cada) e deixa resíduo ≤ 8.4 g·mm | ✅ | desbalanceamento nominal 63.0 g·mm a 23.3° (admissível 8.4); correção a 203.3° repartida em 2.19 g no alívio de 180°, 0.87 g no alívio de 300°; resíduo 0.06 g·mm. Fontes: eletrônica da baia 72.6 g·mm a 14°; aranha (malha) 10.2 g·mm a 146°; tampa (malha) 9.6 g·mm a 180°; sensor hall nu 5.8 g·mm a 20° |
| Área livre de ventilação do cubo | 475.6 | ≥ 300 mm², sem abrir a baia | ✅ | 3 rasgos de 60° fora da baia (r 41.5–45.0) |
| Área livre de ventilação da base | 1152.0 | ≥ 600 mm², na lateral | ✅ | 8 janelas na parede lateral da baia |
| A × Cd do boss carenado | 237.6 – 316.8 | ≤ 350 mm² | ✅ | estimativa por razão de finura, não CFD |
| Massa por painel montado | 42.14 | ≤ 45 g | ✅ |  |
| Massa do rotor completo | 278.59 | ≤ 280 g | ✅ | inclui bateria (50 g medidos), fitas, ferragens, folga de eletrônica de 15 g e o contrapeso planejado de 3.1 g |
| Massa da aranha | 70.99 | ≤ 75 g (alvo) | ✅ | alvo revisto: os 55 g da spec são anteriores ao cubo Ø92 e à baia de 26 |
| Massa da tampa | 10.12 | ≤ 12 g (alvo) | ✅ | alvo revisto para Ø82 |
| Massa da base + torre | 319.8 | ≤ 330 g (alvo) | ✅ | peça estática; o custo é tempo de impressão |
| Perpendicularidade torre/base | 0.0 | ≤ 1° | ✅ | no CAD é zero; verificar na peça impressa |
| Contato da base | 0.0 | sem balanço; ≤ 0,2 mm em 3 pontos a 120° | ✅ | no CAD é plano; verificar na peça impressa |
| Malhas (arestas não-manifold no gerador) | 0 | 0 | ✅ | validação independente em reports/stl_validation.json |
| Base + brim cabe na mesa | 296.0 | ≤ 300 mm | ✅ | extensão medida na malha (com abas) 280.0 + 2 × 8 de brim |
| Piso da baia íntegro sob os furos da flange | 0.0 – 12.0 | sólido de Z = 0 até a flange inferior (12) | ✅ | 06-PENDENCIAS B3; furos só na flange superior: True |
| Rebaixo da flange livra as cabeças dos M3 do motor | 3.5 – 16.0 | profundidade ≥ 3.3 mm e raio livre ≥ 15.5 mm | ✅ | medido na malha; cabeça Ø5.5 × 3.0 em r = 12.42 (retângulo 16 × 19). Os M4 em PCD 40 ficam fora do rebaixo e continuam definindo o assento da chapa |
| Abas de grampo com furo livre | True | livre | ✅ | 4 abas a 90°, furo Ø5 em r = 149 |
| Fita de 201,4 mm cabe no canal | 102.9 | ≤ 104 mm (topo do painel) | ✅ | batente em Z=-98.5 por causa do bolso de fios |
| Suporte do ímã com dois pontos de fixação | 2 | ≥ 2 parafusos | ✅ | 06-PENDENCIAS B4; arco a 4.6 mm da campânula |
| Folga do suporte do ímã à campânula | 4.6 | ≥ 2 mm | ✅ | campânula medida em Ø28 |
| Canaleta de assento dentro da pista | 2.8 – 2.8 | lábios ≥ 1,2 mm | ✅ | provisão (invólucro fora de escopo): canaleta r 132.8–137.2 |
| Cilindro encomendado cabe na canaleta | 0.2 – 0.2 | folga ≥ 0 nos dois lados | ✅ | Ø int 266, parede 4, contra canaleta de 4.4 |
| Folga radial rotor → cilindro encomendado | 24.0 | ≥ 10 mm após deflexão | ✅ | informativo: raio dinâmico 109.0 contra Ø int 266 |
| Folga vertical topo do rotor → borda do cilindro encomendado | 17.0 | ≥ 10 mm | ✅ | informativo: cilindro de 305 mm apoiado em Z=5 |

**Resultado:** 54 de 54 critérios atendidos.
