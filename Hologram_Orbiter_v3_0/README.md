# Hologram Orbiter v3.0 — pacote CAD para fabricação

CAD paramétrico, STL em milímetros, montagem Blender, cupons de calibração,
referência de corte da chapa e relatórios de validação do Hologram Orbiter
v3.0. A fonte de requisitos é
[`../01-ESPECIFICACAO-CAD-v3.0.md`](../01-ESPECIFICACAO-CAD-v3.0.md).
Ponto de operação congelado: raio 100 mm @ 1800 RPM = 90 Hz.

A pasta `../Hologram_Orbiter_v2_1/` é registro histórico e não foi alterada.

## Estado da liberação

**PROVISÓRIO — AGUARDANDO MEDIÇÕES. Não liberado para girar a 1800 RPM.**

Liberados para impressão: os dois cupons (`C01`, `C02`), o poste do ímã, os
painéis, a aranha, a tampa e a **base**. A base traz a canaleta de assento do
cilindro de contenção encomendado (Ø interno 266, parede 4, altura 305, com
tampa): sulco de 4,4 × 3 mm centrado em r = 135 na pista externa, 0,2 mm de
folga por lado. A tampa do cilindro é a peça impressa `07`, com a mesma
canaleta e 13 furos de ventilação; a espessura da placa é o parâmetro
`containment_cap.plate_thickness` (3 mm por padrão). Segue em aberto o ensaio
de material do cilindro ([`docs/PENDENCIAS.md`](docs/PENDENCIAS.md)).

## Arquivos

| Uso | Arquivo | Qtd |
|---|---|---:|
| Aranha ABS | `exports/stl/01_aranha_ABS.stl` | 1 |
| Painel LED ABS | `exports/stl/02_painel_LED_ABS_1x.stl` | 3 |
| Três painéis na mesma mesa | `exports/stl/02_painel_LED_ABS_3x_mesma_mesa.stl` | 1 lote |
| Tampa da baia ABS | `exports/stl/03_tampa_baia_ABS.stl` | 1 |
| Base + torre integradas ABS | `exports/stl/04_05_base_torre_ABS_integradas.stl` | 1 |
| Poste do ímã ABS (parte fixa) | `exports/stl/06_poste_ima_ABS.stl` | 1 |
| Tampa do cilindro de contenção ABS (parte fixa) | `exports/stl/07_tampa_contencao_ABS.stl` | 1 |
| Cupom da junta 11 × 6 | `exports/stl/C01_cupom_junta.stl` | imprimir primeiro |
| Cupom do canal 12,4 × 1,2 | `exports/stl/C02_cupom_canal_LED.stl` | imprimir primeiro |
| Chapa do motor (referência, NÃO imprimir) | `exports/stl/R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl` | — |
| Chapa do motor para corte 1:1 | `fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf` / `.svg` | alumínio 2 mm |
| Montagem editável | `exports/fonte/Hologram_Orbiter_v3_0.blend` | — |
| Renders de inspeção | `exports/preview/*.png` | — |
| Parâmetros (fonte de verdade) | `CAD/parameters.json` | — |
| Gerador | `CAD/generate.py` | Blender 5.x |
| Critérios de aceitação (§9) | `reports/ACEITACAO.md` | automático |
| Relatório geométrico | `reports/geometry_report.json` | automático |
| Validação independente dos STL | `reports/stl_validation.json` | automático |
| Relatório de validação | `reports/RELATORIO_VALIDACAO.md` | — |

## Como regenerar

Requer Blender 5.x (`brew install --cask blender`) e Python 3 com NumPy para a
validação independente (`pip3 install --user numpy`).

```bash
./scripts/build.sh
```

Gera STL, `.blend`, prévia, renders de inspeção, DXF/SVG e relatórios. Para
mudar qualquer cota, edite `CAD/parameters.json` e rode de novo. Nunca edite um
STL à mão. `./scripts/build.sh --no-render` pula a prévia da montagem.

## O que mudou em relação à v2.1

- Raio do plano médio 130 → **100 mm**; ombro em r = 74, espiga até r = 96.
- Canal do LED 13 × 1,8 → **12,4 × 1,2** (piso de 0,80 mm, 4 camadas).
- Torres dos parafusos Ø8 → **Ø10** (1,65 mm ao redor da porca).
- **Carenagem em gota** no boss (casca de 0,8 mm, corda 49 mm, finura 2,2),
  aberta em Z = ±18 para acesso aos parafusos; alma central no lugar dos
  gussets.
- Cubo com **furo Ø8 + rebaixo Ø13 × 2** para porca M6 baixa (a cônica não
  cabe com a bateria), mais 4 furos de provisão em PCD 19 para adaptador.
- **Berço da bateria** (57 × 30 × 13) sobre a porca, sensor **hall no rotor**
  e ímã num poste fixo (peça nova 06), rasgos de refrigeração do cubo entre os
  braços, alívios inferiores que dobram como bolsos de balanceamento.
- **Rota de fiação** sem furar a espiga: janela na baia, sulco no lado de fuga
  do braço, câmara da carenagem, cavidade do painel, bolso na ponta da fita.
  Ver [`docs/FIACAO_E_MONTAGEM.md`](docs/FIACAO_E_MONTAGEM.md).
- Base Ø300 → **Ø280** (limite da mesa com brim), ventilação **lateral** na
  baia, nada no piso; **canaleta de assento** do cilindro na pista externa;
  furos periféricos removidos (decisão de 02/09/2026: a canaleta ocupa o meio
  da pista e a base não precisa ser parafusada na bancada).
- **Tampa do cilindro** impressa (peça 07): placa Ø280 com anel de assento e
  a canaleta da base, 13 furos de ventilação de no máximo Ø28, porque com a
  base na mesa e o cilindro fechado ela é o único caminho de ar do conjunto.
- Datum B em **Z = 186** (chapa 156 + 30 do conjunto motor, a confirmar).
- Coxim TPU e anel de contenção removidos (montagem rígida; contenção
  pendente de medição).
- Correção de um bug da v2.1: rotações de caixas fora da origem giravam a peça
  em torno do próprio centro — as 8 nervuras da base estavam empilhadas numa
  estrela deslocada e não contavam na massa.

## Resultado geométrico (densidade maciça de ABS 1,04 g/cm³)

| Peça | Massa CAD | Limite/alvo |
|---|---:|---|
| Painel nu | 31,7 g | — |
| Painel montado (fita 6,2 + ferragens 4,0) | 41,9 g | ≤ 45 g ✅ |
| Aranha | 52,6 g | ≤ 55 g ✅ |
| Tampa | 7,7 g | ≤ 8 g ✅ |
| Rotor completo (com bateria 48 g e 15 g de eletrônica) | 251,9 g | ≤ 280 g ✅ |
| Base + torre | 310,2 g | peça estática, sem critério |
| Tampa do cilindro (placa de 3 mm) | 190,9 g | peça estática, sem critério |
| Poste do ímã | 1,5 g | peça estática, sem critério |

Os 28 critérios automáticos passam
([`reports/ACEITACAO.md`](reports/ACEITACAO.md)). Só o que gira tem orçamento
de massa. O cilindro encomendado termina 17 mm acima do topo do rotor e deixa
26,5 mm de folga radial após a deflexão; a placa da tampa fica acima da borda
do cilindro e não consome essa folga. Consulte
[`docs/GUIA_IMPRESSAO.md`](docs/GUIA_IMPRESSAO.md) antes de fatiar e
[`docs/MEDICOES_DE_ENTRADA.md`](docs/MEDICOES_DE_ENTRADA.md) para o que ainda
precisa ser medido.
