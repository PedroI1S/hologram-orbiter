# Relatório de validação CAD — Hologram Orbiter v3.0

Data: 03/09/2026, revisão 3.0.2. Unidade: milímetro. Gerador: Blender 5.2.1
LTS, solver booleano Manifold, um cortador por diferença. Validação
independente: leitor de STL binário próprio (`scripts/validate_stl.py`,
NumPy), sem Blender, com **teste de enrolamento por traçado de raios** e faces
coincidentes (`CAD/probe.py`).

## O que a regeneração corrigiu, e como foi comprovado

| Item | Antes (STL de 02/09) | Depois |
|---|---|---|
| A1 · cascas invertidas nos furos M3 | raio ao longo do eixo do parafuso: enrolamento **−1** em x −18…−15,2 (pino no bolso da porca) e em −3,1…+3,1 (barra no socket), nos dois furos; 132 trechos ruins na varredura de 1 mm | enrolamento 0 de −30 a +30 nos dois eixos; 0 trechos ruins em 6 227 raios |
| A2 · membrana no canal em X = −98,5 | não reproduzida pelo traçado de raios nem pela busca de faces coincidentes; corrigida por construção (bolso invade o canal em 0,2) | 0 faces coincidentes |
| Lâmina de ar na base (achado novo) | piso da baia terminava em Z = 3,95 e a flange inferior começava em 4,00: 0,05 mm de vazio sob a flange | material contínuo de Z = 0 a 12 sob os furos da flange |
| Canal em degrau da spec §5.1 (achado de Pedro) | PCB num canal raso de 0,6 e LEDs num rasgo 1,4 mais fundo — mas os LEDs ficam em cima do PCB: com a fita para fora eles sobressairiam 1,4 mm, e a faixa engrossada igual ao rasgo ainda deixava o piso ligado por uma linha (2 arestas não-manifold no cupom) | canal único 12,4 × 2,0, parede local 2,8 em 14,4 mm, piso 0,8 em ponte de 12,4; 0 arestas ruins |
| Poste da tampa sobre a raiz do braço (achado novo) | poste em +x tangenciava o topo do aerofólio em r 38–39,3: 1 aresta não-manifold | postes em y = ±35 |
| Fixação do eixo (achado do desenho do motor) | rebaixo Ø13/Ø21 × 2 com arruela M6 Ø20: o colar Ø8 × 5–7 do eixo ficaria acima do fundo do rebaixo e a arruela assentaria no colar — **o cubo não seria apertado** | sem rebaixo; arruela Ø20 × Ø8,5 × 2 em alumínio; porca M6 fina + trava química; três critérios novos |

## Malhas

Todos os 9 STL passaram: zero triângulos degenerados, zero arestas com
incidência diferente de duas faces, volume orientado positivo, base em Z = 0,
escala em mm, **zero trechos com enrolamento fora de {0, 1}, zero membranas,
zero faces coincidentes** ([`stl_validation.json`](stl_validation.json)).

| Arquivo | Triângulos | Componentes | Volume (cm³) | Envelope (mm) | Raios |
|---|---:|---:|---:|---|---:|
| 01_aranha_ABS | 11 230 | 1 | 64,93 | 148,8 × 171,8 × 32 | 17 903 @ 1,43 |
| 02_painel_LED_ABS_1x | 3 988 | 1 | 30,71 | 208 × 50 × 30 | 6 227 @ 1,73 |
| 02_painel_LED_ABS_3x_mesma_mesa | 11 964 | 3 | 92,14 | 208 × 170 × 30 | 15 939 @ 1,73 |
| 03_tampa_baia_ABS | 6 538 | 1 | 9,74 | 82 × 82 × 5 | 17 080 @ 0,68 |
| 04_05_base_torre_ABS_integradas | 7 690 | 1 | 308,98 | 280 × 280 × 154 | 30 492 @ 2,33 |
| 06_suporte_ima_ABS | 1 726 | 1 | 1,74 | 22 × 42 × 21,5 | 9 896 @ 0,5 |
| C01_cupom_junta | 60 | 1 | 9,69 | 58 × 24 × 12 | 10 268 @ 0,5 |
| C02_cupom_canal_LED | 154 | 1 | 3,40 | 30 × 30 × 8 | 6 076 @ 0,5 |
| R01_suporte_motor (alumínio, não imprimir) | 3 536 | 1 | 6,81 | 60 × 60 × 2 | 16 348 @ 0,5 |

O painel tem **1 componente** porque a cavidade é aberta por projeto (vão de
4 mm em cada diafragma, furo na parede interna e bolso na ponta da fita). O
envelope de 50 mm em Y é a corda de 30 mm mais a cauda da carenagem até
y = −35. As abas de grampo ficam nos cantos (r = 156 a 45°) e não aumentam o
envelope de 280 × 280.

## Critérios de aceitação (spec §9), medidos na malha

Verificação automática em [`ACEITACAO.md`](ACEITACAO.md): **51 de 51**. Os
valores geométricos saem de traçado de raios no STL final, não dos parâmetros.

| Critério | Modelo | Requisito | |
|---|---:|---|:-:|
| Raio do plano médio (ombro medido 74,0 + 26) | 100,0 | 100 ±0,1 | ✅ |
| Datum D · ponta da espiga | 104,0 · 96,0 | 104 ±0,2 · 96 ±0,1 | ✅ |
| Socket: profundidade · parede até a cavidade | 22,5 · 1,5 | 22,5 ±0,1 · ≥ 1,2 | ✅ |
| Piso sob o canal (centro, borda e junta) · terra piso→parede | 0,80 · 2,80 | ≥ 0,6 · ≥ 2,0 | ✅ |
| Furos M3 livres · bolso da porca 2,8, torre sólida até +18 | sim | — | ✅ |
| Casca da carenagem · menor parede | 0,80 · 0,80 | 0,8 ±0,05 · ≥ 0,8 | ✅ |
| Enrolamento por raios (painel, aranha, tampa, base, suporte) | 0 / 0 | 0 ruins, 0 membranas | ✅ |
| Furo do cubo livre · sem rebaixo · pele dos alívios 2,0 | sim | — | ✅ |
| Arruela passa pelo colar Ø8 (furo − colar) | 0,5 | ≥ 0,3 | ✅ |
| Porca não toca o colar (topo da arruela − topo do colar) | 1,0 | ≥ 0,5 | ✅ |
| Rosca sobrando acima da porca | 3,0 (1,0 na leitura de 12 mm) | ≥ 1 | ✅ |
| Topo da porca (+5) abaixo dos trilhos (6) · bateria 23 ≤ 26 · meia-diagonal 32,3 ≤ 39 | sim | — | ✅ |
| Layout da baia: envelope, interferências, faixas dos feixes | ok | — | ✅ |
| Eletrônica embarcada estimada | 15,0 g | ≤ 15 g | ✅ (no limite) |
| Contrapeso planejado | 2,2 g no alívio de 180° | dentro de ±18°, ≤ 13,9 g | ✅ |
| Ventilação do cubo · da base | 476 mm² · 1 152 mm² | ≥ 300 · ≥ 600 lateral | ✅ |
| A × Cd do boss carenado | 238–317 mm² | ≤ 350 | ✅ estimativa |
| Massa por painel montado · rotor completo | 42,1 g · **274,3 g** | ≤ 45 · ≤ 280 | ✅ (folga de 5,7 g) |
| Aranha · tampa · base + torre | 67,5 · 10,1 · 321,3 g | ≤ 75 · ≤ 12 · ≤ 330 (alvos) | ✅ |
| Malhas · base + brim na mesa | 0 não-manifold · 296 | 0 · ≤ 300 | ✅ |
| Piso íntegro sob os furos da flange · furos só na flange superior | Z 0…12 sólido | — | ✅ |
| Abas de grampo com furo livre · suporte do ímã com 2 parafusos, 4,6 mm da campânula | sim | — | ✅ |
| Fita de 201,4 mm no canal | 102,9 | ≤ 104 | ✅ |
| Provisão do cilindro (canaleta, folgas radial 26,5 e vertical 17) | informativo | — | ✅ |

## Cadeia de cotas em Z (montagem)

```
Z =   0    face de apoio da base
Z =   4    piso da baia (flange inferior fundida ao piso: sem lâmina de ar)
Z =   5    piso da canaleta de provisão do cilindro
Z = 154    topo da torre
Z = 156    face superior da chapa de alumínio
Z = 177,5  topo do poste do ímã (entreferro 2,5 mm)
Z = 180    Datum A — face inferior do cubo = topo da campânula (24 mm MEDIDOS)
Z = 186    Datum B — face superior do cubo; arruela 186–188, porca 188–191
Z = 187    topo do colar Ø8 do eixo (desenho: ressalto 2 + colar 5), dentro da arruela
Z = 189    plano médio dos painéis
Z = 192    trilhos do berço; bateria 192–209
Z = 194    ponta do eixo (192 na leitura de 12 mm)
Z =  85 … 293   envelope do rotor
```

## Fixação do eixo

| Grandeza | Valor |
|---|---:|
| Eixo (desenho) | ressalto Ø6,9 × 2 (assumido) + colar Ø8 × 5 + rosca M6 × 7 = 14 acima da campânula |
| Furo do cubo | Ø8 H8 (o colar centra o rotor) |
| Arruela | Ø20 × Ø8,5 × 2, alumínio, cortada da chapa R01; sobre o topo do cubo, sem rebaixo |
| Porca | M6 fina DIN 439B, 3 mm, Loctite 243, 0,6 N·m |
| Pilha sobre o topo do cubo | arruela 0–2 · porca 2–5 · colar até +1 · ponta do eixo em +8 (ou +6) |
| Pressão no ABS a 500 N | 1,9 MPa (259 mm²) |
| O que a arruela M6 Ø20 da spec faria | assentaria no colar (Ø8 > furo 6,4); porca apertaria o colar, cubo solto |

## Canal do LED (spec §5.1, corrigida em 03/09)

| Grandeza | Valor |
|---|---:|
| Canal | 12,4 × 2,0 (piso em x = 2,0): PCB de 0,4 colado no fundo, LEDs 5050 de 1,5–1,6 rentes à face |
| Parede local | 2,8 mm (cavidade em x = 1,2) numa faixa de 14,4 mm, inclusive onde o perfil afila para a fuga |
| Piso sob o canal, medido | **0,80 mm** no centro, na borda do canal e na junta |
| Terra de ligação piso→parede de 2,0 | 1,0 mm de cada lado, 2,8 mm de espessura (medido) |
| Ponte na impressão | 12,4 mm a 2,0 mm da mesa — a mesma do canal original de 1,2 |
| Custo de massa | +0,3 g por painel (painel nu 31,7 → 31,9 g) |
| Por que não o degrau da spec | os LEDs ficam em cima do PCB; o degrau só funcionaria com a fita de cabeça para baixo |

## Aranha, layout da baia e suporte do ímã

| Grandeza | Valor |
|---|---:|
| Cubo · baia | Ø92 × 6 · Ø82/Ø78 × 26 |
| Rasgos de refrigeração | 3 × 60° em r 41,5–45 = 476 mm² |
| Alívios de massa (plano 1 de balanceamento) | 3 × 36° em r 17–36, 4 mm de fundo, pele 2,0 medida; 13,9 g de tungstênio cabem em cada |
| Fillet cubo→braço | cunha a 45° sob o braço, r 45,5–53,3, 11 mm de largura, + alargamento em planta r 39–46 |
| Postes da tampa | Ø8 em y = ±35, encostados na parede |
| Berço | pack 58 × 30 × 17 sobre trilhos em Z = 6; topo em Z = 23 |
| Placa de interface (5,5 g) | 15 × 20 × 8 em (27, 5), Z 6–14, 4 pilares Ø3,5 com piloto Ø1,6; sob a janela da tampa |
| ESP32-C3 (3,0 g) | 18 × 22,5 × 5 em (−27, 0), Z 6–11, 4 pilares |
| Buck mini560 (2,0 g) | 6 × 17 × 22 em pé na ranhura da parede a 140° (guias 1,2 × 22) |
| Capacitor 1000 µF (2,5 g) | Ø10 × 20 em pé em (22,5, −22), cerca Ø12,6 × 3 |
| Fios (2,0 g) | no centro |
| Desbalanceamento nominal | 72,6 g·mm a 13,7° (admissível 8,4) |
| Contrapeso planejado | 2,2 g de tungstênio a 193,7°, no alívio de 180°, r ≈ 33 |
| Suporte do ímã | arco r 18,5–24,5 × 2,5 sob os M4 de ±45°, braço até r = 33,5, poste Ø8 × 21,5 em r = 29, 20°; 1,7 g |

## Base

| Grandeza | Valor |
|---|---:|
| Abas de grampo | 4 × (16 radiais × 20 × 8) a 45°, 135°, 225°, 315°; furo Ø5 em r = 149; extensão 280 + brim 8 = 296 |
| Furos M4 da flange | só na flange superior (Z 146–154); piso sólido de 0 a 12 sob eles |
| Canaleta de provisão | r 132,8–137,2 × 3, piso em Z = 5; lábios de 2,8 mm |
| Massa | 321,3 g (alvo 330) |

## Números derivados do modelo

| Grandeza | Valor |
|---|---:|
| CG do painel em ABS (z, referencial da junta) | −0,15 mm |
| CG do painel com fita e fios (estimado) | −1,18 mm |
| Força centrífuga com a massa CAD (42,1 g) | 149,7 N |
| Momento parasita na junta | 0,18 N·m |
| Corda da carenagem / largura frontal / finura | 49 / 22 / 2,23 |
| Rotor: CAD 173,5 g + fitas 18,6 + ferragens 12 + bateria 50 + arruela e porca 3 + eletrônica 15 + contrapeso 2,2 | 274,3 g |

## Não verificáveis no modelo

- **Eixo**: alturas do colar e da ponta a partir da face de apoio não medidas;
  o desenho não fecha a soma (5 + 7 ≠ 14). A fixação vale nas duas leituras.
- **Eletrônica da baia**: massas de catálogo; a folga do rotor é 5,7 g.
- Arruela e porca reais, ímã, eletrônica: `verified: false` em `parameters.json`.
- **A × Cd** é estimativa por razão de finura, não CFD nem ensaio.
- FEA, modal, fluência, retenção de parafusos, balanceamento instrumentado e
  térmica seguem não executados.

## Conclusão

Malhas válidas em topologia **e** em enrolamento; 51 critérios geométricos e
de montagem atendidos, medidos na malha. Liberados os cupons e a impressão de
painéis, aranha, tampa da baia, suporte do ímã e base; a chapa e o disco da
arruela saem do mesmo DXF. O conjunto não está liberado para operar a
1800 RPM; antes de comprar a porca, medir o colar e a ponta do eixo.
