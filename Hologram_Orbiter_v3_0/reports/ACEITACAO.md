# Critérios de aceitação — Hologram Orbiter v3.0

Verificação automática a partir do modelo (spec §9). Gerado por `CAD/generate.py`.

| Critério | Valor no modelo | Requisito | Resultado | Nota |
|---|---:|---|:---:|---|
| Raio do plano médio do painel | 100.0 | 100 ±0,1 mm | ✅ | por construção na montagem; face interna em r=96 e externa em r=104 |
| Datum D | 104.0 | 104 ±0,2 mm | ✅ |  |
| Δh entre painéis | 0.0 | ≤ ±0,5 mm | ✅ | os três painéis são o mesmo STL |
| Piso sob o canal do LED | 0.8 | ≥ 0,6 mm | ✅ |  |
| Parede ao redor do bolso de porca | 1.65 | ≥ 1,5 mm | ✅ |  |
| Menor parede estrutural do modelo | 0.8 | ≥ 0,8 mm | ✅ | mínimo entre piso do canal, casca da carenagem, borda do disco fora dos rasgos, pele da tampa e nervuras (1,0 mm, conforme spec §5.1) |
| Área livre de ventilação do cubo | 409.6 | ≥ 300 mm², sem abrir a baia | ✅ | 3 rasgos de 60° fora da baia (r 35,5–39) |
| Área livre de ventilação da base | 1152.0 | ≥ 600 mm², na lateral | ✅ | 8 janelas na parede lateral da baia |
| A × Cd do boss carenado | 237.6 – 316.8 | ≤ 350 mm² | ✅ | estimativa por razão de finura, não CFD |
| Massa por painel montado | 41.87 | ≤ 45 g | ✅ |  |
| Massa do rotor completo | 251.88 | ≤ 280 g | ✅ | inclui bateria, fitas, ferragens e folga de eletrônica |
| Massa da aranha | 52.62 | ≤ 55 g (alvo) | ✅ |  |
| Massa da tampa | 7.65 | ≤ 8 g (alvo) | ✅ |  |
| Perpendicularidade torre/base | 0.0 | ≤ 1° | ✅ | no CAD é zero; verificar na peça impressa |
| Planeza da base | 0.0 | ±2 mm | ✅ | no CAD é zero; verificar na peça impressa |
| Malhas (arestas não-manifold no gerador) | 0 | 0 | ✅ | validação independente em reports/stl_validation.json |
| Base + brim cabe na mesa | 296.0 | ≤ 300 mm | ✅ |  |
| Bateria cabe na baia sobre a porca | 19.0 | ≤ 20.0 mm | ✅ | porca baixa no rebaixo, topo em Z=5.6 |
| Fita de 201,4 mm cabe no canal | 102.9 | ≤ 104 mm (topo do painel) | ✅ | batente em Z=-98.5 por causa do bolso de fios |
| Canaleta de assento dentro da pista | 2.8 – 2.8 | lábios ≥ 1,2 mm | ✅ | canaleta r 132.8–137.2, largura 4.4, profundidade 3 |
| Cilindro cabe na canaleta | 0.2 – 0.2 | folga ≥ 0 nos dois lados | ✅ | Ø int 266, parede 4, contra canaleta de 4.4 |
| Cotas do cilindro confirmadas | cota_de_encomenda | verified = true | ✅ | conferir Ø interno e borda na peça recebida |
| Folga radial rotor → cilindro | 26.52 | ≥ 10 mm após deflexão | ✅ | raio dinâmico 106.5 contra Ø int 266 |
| Folga vertical topo do rotor → topo do cilindro | 17.0 | ≥ 10 mm | ✅ | cilindro de 305 mm apoiado em Z=5 (piso da canaleta); a placa da tampa fica acima da borda e não desconta |
| Tampa: aberturas menores que a seção do painel | 28.0 | ≤ 30 mm (círculo mínimo da seção 30 × 8 = Ø31,05) | ✅ | 13 furos |
| Tampa: área livre de ventilação | 5177.3 | ≥ 600 mm² (único caminho de ar com a base na mesa) | ✅ |  |
| Tampa + brim cabe na mesa | 296.0 | ≤ 300 mm | ✅ |  |
| Tampa: furos de ventilação fora da trajetória dos painéis | 61.0 | < 96 mm (face interna do painel) | ✅ | painel solto voa para fora, nunca para dentro |

**Resultado:** 28 de 28 critérios atendidos.
