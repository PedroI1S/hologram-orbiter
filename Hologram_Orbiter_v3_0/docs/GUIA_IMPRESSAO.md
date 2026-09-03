# Guia de impressão — v3.0 (revisão 3.0.3, 03/09/2026)

Bico 0,4 mm, camada 0,2 mm, ABS em câmara fechada (spec §7). Mesa de
300 × 300 mm. Não altere a escala nem "conserte" os STL no fatiador: eles são
estanques, orientados e passaram no teste de enrolamento por raios; qualquer
cota muda em `CAD/parameters.json`.

## Sequência

1. `C01_cupom_junta.stl` e `C02_cupom_canal_LED.stl`. Conferir: espiga
   11 × 6 entra no socket 11,2 × 6,2 sem forçar e sem folga sensível; a fita
   HD107S real assenta no canal de **12,4 × 2,0** do cupom — PCB colado no
   fundo, LEDs rentes à face — com o piso de 0,8 mm íntegro e o bolso 8 × 3,5
   aberto. O C02 é uma fatia real de 30 mm da ponta do painel, impressa na
   mesma orientação: se a ponte de 12,4 mm do piso sair boa aqui, sai boa no
   lote.
2. Ajustar `quality.joint_xy_clearance_each_side` ou compensações se preciso e
   regenerar.
3. `02_painel_LED_ABS_3x_mesma_mesa.stl` — os três painéis no mesmo lote, mesmo
   filamento, mesmo perfil. Pesar os três: Δm ≤ 0,084 g é o alvo depois de
   montados; anotar.
4. `01_aranha_ABS.stl`, `03_tampa_baia_ABS.stl`, `06_suporte_ima_ABS.stl`.
5. `04_05_base_torre_ABS_integradas.stl` — liberada. Traz a canaleta de
   provisão do cilindro (4,4 × 3 mm em r = 135) e quatro abas de grampo nos
   cantos; não há furos periféricos.

## Orientação (já embutida nos STL, base em Z = 0)

| Peça | Como está no STL | Suporte |
|---|---|---|
| Painel | deitado, 208 mm em X, boss e carenagem para cima, canal do LED contra a mesa | **sim, em duas regiões** — ver "Balanços declarados" abaixo. Os bolsos hexagonais das porcas ficam de lado (ponte de 6 mm, ok) |
| Aranha | plana, face inferior do cubo na mesa | **sim, sob os braços**: eles ficam 6 mm acima da mesa (Datum B + 3). A cunha de 45° sob a raiz, os pilares de 6 mm, as guias de 22 mm do buck e a cerca do capacitor imprimem sem suporte; usar suporte em árvore com 0,2 mm de folga só sob os braços, de r ≈ 53 até a ponta |
| Tampa da baia | plana, pele na mesa; copos de balanceamento para cima | nenhum |
| Base + torre | torre em Z, sem inclinação | **sim, sob a flange superior** — ver "Balanços declarados". As janelas laterais de 12 mm são pontes curtas; as abas são maciças |
| Suporte do ímã | arco na mesa, poste para cima | nenhum |
| Cupom C02 | como o painel: deitado, canal contra a mesa | **sim, sob a fuga** (o cupom é uma fatia real: reproduz o mesmo balanço de 73°) |
| Cupom C01 | como exportado | nenhum |

## Balanços declarados

Análise de normais das malhas exportadas na orientação acima (base em Z = 0),
confirmada por contagem de área por faceta. O ângulo é medido **a partir da
vertical**: 0° é parede vertical, 90° é teto horizontal. O fatiador precisa de
suporte acima de 45°.

| Peça | Região | Ângulo | Área | Suporte |
|---|---|:---:|---:|---|
| Painel | fuga da lâmina, y −15…−5, z 0–3 | **73°** | ~2 100 mm² | **quebra-fácil**, 3 mm de altura × 10 mm de largura, ao longo dos 208 mm |
| Painel | cauda da carenagem, y −35…−15, z 5–17,5 | **58–65°** | 1 873 mm² | **em árvore, dentro da casca**, 0,2 mm de folga |
| Painel | nariz R4, primeiro 1 mm | 60–90° | ~400 mm² | tolerável, sem suporte |
| Base | face inferior da flange superior, Z = 146, r 16–27 | **90°** | 2 069 mm² | **em árvore**, da laje da baia até a flange |
| Aranha | face inferior dos braços, Z = 6 | 90° | 630 mm² | já declarado acima |

Três observações sobre a tabela, porque a revisão de 03/09 as levantou e a decisão
foi **manter a geometria e declarar o suporte**:

- **Fuga da lâmina (73°).** Com a face +x na mesa, o afilamento (4,−5) → (1,−15)
  sobe 3 mm em 10 mm de y: cada camada de 0,2 mm avança 0,67 mm sobre a
  anterior, 167 % da largura do filete de um bico de 0,4. Sem suporte o bico
  extruda no ar e a superfície que droopa é o **bordo de fuga aerodinâmico**. O
  suporte deixa marca ali; é o preço de não mexer no perfil. Alternativa
  registrada e descartada nesta revisão: perfil de fundo plano (face +x reta até
  y = −15, afilando só pelo lado −x), que imprimiria sem suporte.
- **Cauda da carenagem (58°).** Casca de 0,8 mm em 23 mm de rampa. Encurtar a
  cauda de y = −35 para −27 daria 45° e dispensaria o suporte, **mas** derruba a
  razão de finura de 2,23 para 1,86 e leva o A × Cd estimado para ~277–356 mm²,
  contra o critério de ≤ 350. Por isso a cauda fica e o suporte entra.
- **Flange da torre (90°).** Anel horizontal de 15 mm de largura a 146 mm de
  altura: **não é ponte**, não há apoio do outro lado. Sem suporte a face
  inferior sai como fio solto e os furos M4 ficam sem espessura útil. Suporte em
  árvore da laje da baia até a flange. Alternativa registrada e descartada: cone
  a 45° sob a flange (Ø60 em Z = 146 → Ø30 em Z = 131, ~10 g), que imprimiria
  sem suporte nenhum.

O canal do LED forma uma ponte de **12,4 mm a 2,0 mm da mesa**, com 0,8 mm de
espessura (4 camadas): é a superfície mais delicada do projeto, e é a mesma
ponte do canal original de 1,2 mm. Validar no cupom antes do lote de 208 mm;
se a ponte sair ruim, imprimir com a primeira camada da ponte mais lenta e
ventilação alta, antes de pensar em engrossar o piso.

## Perfis sugeridos

| Parâmetro | Painéis | Aranha | Tampa da baia | Base + torre | Suporte do ímã | Cupons |
|---|---:|---:|---:|---:|---:|---:|
| Perímetros | 3 | 4 | 3 | 4 | 3 | 3 |
| Infill | 35 % giroide | 35 % giroide | 30 % | 30 % giroide | 100 % | como a peça |
| Camadas topo/base | 5 | 5 | 4 | 5 | 4 | 5 |
| Brim | 5 mm | 5 mm | — | **8 mm** (abas nos cantos: brim termina em 118 mm do centro) | 3 mm | 3 mm |

Faça o bolso da porca (hexágono de circunraio 3,35), os furos piloto Ø1,6 dos
pilares e o furo Ø8 do cubo sem "expansão de furo" automática. Se o Ø8 sair
justo, alargar com broca de 8 mm; o cubo assenta pela face, não pelo furo.
**Nunca alargue além do colar real do eixo**: furo folgado desloca 279 g do
centro e não tem conserto.

## Ferragens e chapa

- **Chapa R01** em alumínio 2 mm, cortada pelo DXF/SVG 1:1. O mesmo desenho
  traz o **disco da arruela do eixo, Ø20 × Ø8,5**: cortar da mesma chapa. O
  furo de 8,5 passa pelo colar Ø8 do eixo; uma arruela M6 comum não passa e
  faria a porca apertar o colar em vez do cubo.
- **Porca do eixo: M6 fina DIN 439B (3 mm) com Loctite 243**, a 0,6 N·m. Não a
  cônica do motor, não a autotravante baixa de 6 mm.
- Dois dos quatro M4 da flange passam sob a aba do suporte do ímã (2,5 mm):
  **M4 × 20** nesses dois, M4 × 16 nos outros dois.
- Placas da baia nos pilares: parafusos **M2** nos furos piloto Ø1,6, ou cola.
  Buck na ranhura da parede com um ponto de cola; capacitor na cerca com cola.

## Critérios mínimos de aceite da peça impressa

- painel nu ≈ 31,9 g em densidade maciça; com infill ficará abaixo. Registrar
  a massa real dos três e usar o limite de 45 g montado;
- Datum D = 104 ±0,2 mm a partir da base do painel; Δh entre os três ≤ 0,5 mm;
- canal 12,4 × 2,0 com a fita real: PCB colado no fundo, LEDs rentes à face,
  piso íntegro;
- espiga/socket com 0,1 mm por lado; furos M3 livres de ponta a ponta (passar
  um M3 pelos dois furos de cada painel antes de montar);
- torre perpendicular à base ≤ 1°; base sem balanço, ≤ 0,2 mm em 3 pontos;
- todas as porcas capturadas; entreferro do hall 2–3 mm.

Nunca ensaie o rotor sem contenção, parada de emergência e operação remota.
Rampa de partida ≥ 8 s (pico previsto 8 A). Grampear a base pelas abas.
