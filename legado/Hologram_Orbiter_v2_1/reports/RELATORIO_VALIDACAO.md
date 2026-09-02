# Relatório de validação CAD — Hologram Orbiter v2.1

Data da geração: 01/09/2026. Unidade de exportação: milímetro.

## Resultado

Todos os 11 STL exportados passaram na validação independente:

- zero triângulos degenerados;
- zero arestas abertas ou com incidência diferente de duas faces;
- volume orientado positivo;
- base de impressão normalizada em Z=0;
- envelopes principais coerentes com o modelo paramétrico.

O resultado detalhado e legível por máquina está em
[`stl_validation.json`](stl_validation.json). O relatório de volumes e
parâmetros está em [`geometry_report.json`](geometry_report.json).

## Dimensões e massas geométricas

As massas abaixo usam volume CAD × densidade nominal (ABS 1,04 g/cm³; TPU
1,20 g/cm³). Para peças espessas, o valor real depende do fatiamento; para
paredes finas, a estimativa fica mais próxima da peça impressa.

| Peça | Envelope exportado (mm) | Massa geométrica |
|---|---:|---:|
| Aranha | 193,76 × 223,74 × 30,95 | 57,55 g |
| Painel, cada | 208 × 30 × 30¹ | 26,89 g |
| Tampa | 70 × 70 × 5 | 7,58 g |
| Base + torre | 300 × 300 × 154 | 306,42 g |
| Coxim TPU, cada | 16 × 16 × 8 | 1,85 g |
| Anel TPU de referência | 300 × 300 × 10 | 109,15 g |

¹ O painel está deitado no STL: 208 mm ficam em X. Os 30 mm em Z incluem a
profundidade radial do boss; a lâmina continua com espessura máxima de 8 mm. O
boss tem extensão vertical de 36 mm no sistema de montagem, contida dentro dos
208 mm de altura total do painel.

## Checagens contra a especificação

| Requisito | Resultado CAD | Situação |
|---|---:|---|
| Painel impresso ≤35 g | 26,89 g | passa para a peça nua |
| Datum D | 104 mm da base | passa nominalmente |
| Lâmina | 208 × 30 × 8 mm | passa |
| Canal LED | 13 × 1,8 mm | passa nominalmente; medir fita |
| Espiga | 11 × 6 × 22 mm | passa |
| Socket | 11,2 × 6,2 × 22,5 mm útil | passa; 0,1 mm/lado e 0,5 mm no fundo |
| Ombro da longarina | r=104 mm | passa |
| Plano médio do painel | r=130 mm | passa na montagem |
| Base | Ø300 mm | passa |
| Baia central | Ø100 × 80 mm | passa |
| Torre | Ø30, parede 4 mm | passa |
| Topo da torre | Z=154 mm | fecha Z=188 com motor provisório de 34 mm |
| Coxim | Ø16 × 8, furo Ø3,2 | passa |

## Itens reprovados ou não verificáveis

- Massa geométrica do rotor impresso (aranha + 3 painéis + tampa): **145,80 g**,
  acima do total publicado de 120 g. O valor real com infill pode cair, mas o
  próprio orçamento de máximos da especificação soma mais de 120 g; é necessária
  uma revisão formal do requisito e pesagem física.
- Proteção de 260 mm: insuficiente para o envelope vertical calculado até
  Z=295 mm quando iniciada no solo.
- Folga radial após a deflexão prevista: somente 2,5 mm até o anel Ø280 interno.
- Furação do motor, fita LED, bateria e altura do conjunto não foram medidas.
- FEA, análise modal, fadiga e contenção de falha não foram executadas.

## Conclusão de liberação

Os arquivos estão tecnicamente válidos como malhas de prototipagem e como base
paramétrica para a revisão. Estão liberados os **cupons de calibração**. As peças
grandes podem ser impressas para verificação dimensional estática, assumindo o
custo do retrabalho, mas o conjunto não está liberado para operar a 1800 RPM.
