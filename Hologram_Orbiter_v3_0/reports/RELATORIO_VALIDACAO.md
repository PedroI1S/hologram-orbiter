# Relatório de validação CAD — Hologram Orbiter v3.0

Data: 02/09/2026. Unidade: milímetro. Gerador: Blender 5.2 LTS, solver
booleano Manifold. Validação independente: leitor de STL binário próprio
(`scripts/validate_stl.py`, NumPy), sem Blender.

## Malhas

Todos os 10 STL passaram: zero triângulos degenerados, zero arestas com
incidência diferente de duas faces, volume orientado positivo, base em Z = 0,
escala em mm ([`stl_validation.json`](stl_validation.json)).

| Arquivo | Triângulos | Componentes | Volume (cm³) | Envelope (mm) |
|---|---:|---:|---:|---|
| 01_aranha_ABS | 9 250 | 1 | 50,59 | 148,8 × 171,8 × 26 |
| 02_painel_LED_ABS_1x | 3 134 | 1 | 30,45 | 208 × 50 × 30 |
| 02_painel_LED_ABS_3x_mesma_mesa | 9 402 | 3 | 91,36 | 208 × 170 × 30 |
| 03_tampa_baia_ABS | 6 312 | 1 | 7,36 | 70 × 70 × 5 |
| 04_05_base_torre_ABS_integradas | 9 572 | 1 | 298,24 | 280 × 280 × 154 |
| 06_poste_ima_ABS | 1 168 | 1 | 1,46 | 23,3 × 10,7 × 21,5 |
| 07_tampa_contencao_ABS | 6 984 | 1 | 183,55 | 280 × 280 × 6 |
| C01_cupom_junta | 60 | 1 | 9,69 | 58 × 24 × 12 |
| C02_cupom_canal_LED | 44 | 1 | 6,77 | 8 × 30 × 30 |
| R01_suporte_motor (alumínio, não imprimir) | 3 504 | 1 | 6,81 | 60 × 60 × 2 |

O painel tem **1 componente** porque a cavidade é aberta por projeto (vão de
4 mm em cada diafragma, furo na parede interna e bolso na ponta da fita): não
há volume selado. O envelope de 50 mm em Y é a corda de 30 mm mais a cauda da
carenagem até y = −35. Os volumes medidos pelo validador independente
coincidem com os do gerador (base 298,2 cm³ → 310 g; aranha 50,6 cm³ → 52,6 g
a 1,04 g/cm³).

## Critérios de aceitação (spec §9)

Verificação automática em [`ACEITACAO.md`](ACEITACAO.md). Resumo:

| Critério | Modelo | Requisito | |
|---|---:|---|:-:|
| Raio do plano médio | 100,0 | 100 ±0,1 | ✅ |
| Datum D | 104,0 | 104 ±0,2 | ✅ |
| Δh entre painéis | 0 (mesmo STL) | ≤ 0,5 | ✅ |
| Piso sob o canal do LED | 0,80 | ≥ 0,6 | ✅ |
| Parede ao redor do bolso de porca | 1,65 | ≥ 1,5 | ✅ |
| Menor parede estrutural | 0,80 (casca da carenagem, piso do canal) | ≥ 0,8 | ✅ |
| Ventilação do cubo | 410 mm², 3 rasgos entre os braços | ≥ 300, sem abrir a baia | ✅ |
| Ventilação da base | 1 152 mm², 8 janelas laterais | ≥ 600, lateral | ✅ |
| A × Cd do boss carenado | 238–317 mm² (A = 792, Cd 0,30–0,40) | ≤ 350 | ✅ estimativa |
| Massa por painel montado | 41,9 g | ≤ 45 | ✅ |
| Massa do rotor completo | 251,9 g | ≤ 280 | ✅ |
| Aranha / tampa | 52,6 g / 7,7 g | ≤ 55 / ≤ 8 | ✅ |
| Base + torre | 310,2 g | peça estática, sem critério | — |
| Tampa do cilindro | 190,9 g (placa de 3 mm) | peça estática, sem critério | — |
| Perpendicularidade, planeza | 0 no CAD | ≤ 1°, ±2 mm | verificar na peça |
| Malhas | 0 não-manifold, 0 degenerados | — | ✅ |
| Canaleta de assento dentro da pista | lábios 2,8 / 2,8 mm | ≥ 1,2 mm | ✅ |
| Cilindro cabe na canaleta | folga 0,2 / 0,2 mm | ≥ 0 | ✅ |
| Cotas do cilindro confirmadas | cota de encomenda | verified = true | ✅ |
| Folga radial rotor → cilindro | 26,5 mm (Ø int 266) | ≥ 10 | ✅ |
| Folga vertical topo do rotor → borda do cilindro | 17 mm (a placa da tampa fica acima da borda) | ≥ 10 | ✅ |
| Tampa: maior abertura | Ø28 | ≤ Ø30 (círculo mínimo da seção 30 × 8 do painel = Ø31,05) | ✅ |
| Tampa: área livre de ventilação | 5 177 mm² | ≥ 600 mm² | ✅ |
| Tampa: furos fora da trajetória dos painéis | até r = 61 | < 96 mm | ✅ |
| Tampa + brim cabe na mesa | 296 mm | ≤ 300 | ✅ |

Total: 28 de 28 critérios atendidos.

## Cadeia de cotas em Z (montagem)

```
Z =   0    face de apoio da base
Z =   4    piso da baia
Z =   5    piso da canaleta de assento do cilindro (pista de 8 mm, sulco de 3)
Z = 154    topo da torre
Z = 156    face superior da chapa de alumínio
Z = 177,5  topo do poste do ímã (entreferro 2,5 mm)
Z = 180    Datum A — face inferior do cubo (motor 24 mm, não medido)
Z = 186    Datum B — face superior do cubo
Z = 189    plano médio dos painéis
Z =  85 … 293   envelope do rotor
Z = 307    face inferior do anel de assento da tampa do cilindro
Z = 310    borda do cilindro (altura 305) = face inferior da placa da tampa → sobram 17 mm
Z = 313    topo da tampa (placa de 3 mm)
```

## Tampa do cilindro (peça 07)

| Grandeza | Valor |
|---|---:|
| Placa | Ø280 × 3 mm (`containment_cap.plate_thickness`, configurável) |
| Anel de assento | r 130 … 140 × 3 mm, com a mesma canaleta da base (r 132,8 … 137,2 × 3) |
| Furos de ventilação | 1 × Ø28 no centro + 12 × Ø22 em PCD 100 = 5 177 mm² livres |
| Maior abertura | Ø28, menor que o círculo mínimo da seção do painel (Ø31,05) |
| Alcance radial dos furos | r ≤ 61, dentro da face interna dos painéis (r = 96) |
| Massa | 190,9 g (≈ 62 g por mm de placa) |
| Impressão | face plana na mesa, anel e canaleta para cima, brim de 8 mm |

A espessura da placa não entra na folga vertical: a placa apoia na borda do
cilindro, por fora do volume do rotor. Com a base apoiada na mesa e a tampa
colocada, esses furos são o único caminho de ar do conjunto (ver
`docs/PENDENCIAS.md`, item 6a).

## Canaleta de assento do cilindro

| Grandeza | Valor |
|---|---:|
| Cilindro (cota de encomenda, 02/09/2026) | Ø interno 266, parede 4 (Ø externo 274), altura 305, sem fundo, com tampa |
| Canaleta | centrada em r = 135: r 132,8 … 137,2 (largura 4,4), 3 mm de profundidade, piso em Z = 5 |
| Folga de montagem | 0,2 mm por lado |
| Lábios da pista | 2,8 mm interno · 2,8 mm externo |
| Furos periféricos | removidos (sem faixa livre na pista; base não precisa ser parafusada) |
| Massa retirada pela canaleta | ≈ 11 g |

A canaleta é definida diretamente em `base_tower.containment_seat` (largura,
profundidade, raio do centro); o gerador confere que o cilindro de
`unverified_interfaces.containment` cabe nela com folga ≥ 0 e que sobram
lábios ≥ 1,2 mm na pista. Conferir o Ø interno na peça recebida antes de
imprimir a base.

## Números derivados do modelo

| Grandeza | Valor |
|---|---:|
| CG do painel em ABS (z, referencial da junta) | −0,02 mm |
| CG do painel com fita e fios (estimado) | −1,08 mm |
| Momento parasita na junta (F = 149 N × 1,08 mm) | 0,16 N·m |
| Força centrífuga com a massa CAD (41,9 g) | 148,8 N |
| Corda da carenagem / largura frontal / finura | 49 / 22 / 2,23 |
| Topo da porca M6 baixa acima do cubo | +5,6 mm |
| Bateria no berço | Z = 6 … 19 (baia de 20) |
| Fita de 201,4 mm | Z = −98,5 … +102,9 (topo do painel em 104) |
| Base + brim de 8 mm | 296 mm (mesa 300) |

## Reprovados ou não verificáveis

- **Contenção**: cotas de encomenda, não medidas na peça; material (PMMA ou
  PC) ainda sem ensaio de dobra.
- **Massa de peças estáticas** (base 310 g, tampa do cilindro 191 g) não é
  critério por decisão de 02/09/2026; só o rotor tem orçamento.
- **A × Cd** é estimativa por razão de finura, não CFD nem ensaio.
- Interfaces com `verified: false` em `parameters.json`: altura do conjunto
  motor, eixo, assento da campânula, adaptador, bateria, hall, ímã, porca,
  eletrônica, janela da tampa, cilindro.
- FEA, modal, fadiga, retenção de parafusos, balanceamento instrumentado e
  térmica seguem não executados.

## Conclusão

Malhas válidas e critérios geométricos do §9 atendidos. Liberados os cupons e
a impressão de painéis, aranha, tampa da baia, poste, base e tampa do
cilindro, as duas últimas com a canaleta de assento do cilindro encomendado
(Ø266 × 305, parede 4). O conjunto não está liberado para operar a 1800 RPM.
