# Hologram Orbiter v3.0 — pacote CAD, revisão 3.0.5

**PROVISÓRIO — operação e fabricação definitiva dos painéis não liberadas.**
Revisão local de 14/09/2026. Os cupons continuam úteis para calibração; lote
estrutural depende de fechar seção resistente, transferência de carga, ABS FDM,
fluência, massas/chicotes reais e os bloqueadores do plano de ensaios.

A seção da lâmina é integrada desde os parâmetros e conferida em três cortes
na malha. A folga radial usa a carga do teto de 45 g, com deflexão estimada
máxima de 7,83 mm. Nenhuma alteração de perfil estrutural foi adotada sem validação.
O buck permanece a 140°; o envelope e as guias recuaram 1,2 mm radialmente,
com wall_gap=1,5 mm, para livrar a raiz da aranha.

As raízes dos braços começam em r=39 mm, sem a saliência interna na baia.
O corte de entrada dos fios começa em x local=37 mm e atravessa toda a parede.
A prévia `aranha_entrada_fios.png` mostra o detalhe corrigido; dois critérios
novos sondam as raízes e as janelas na malha final dos três braços.

## Arquivos

| Uso | Arquivo | Qtd |
|---|---|---:|
| Aranha ABS (com pilares, guia do buck e cerca do capacitor) | `exports/stl/01_aranha_ABS.stl` | 1 |
| Painel LED ABS | `exports/stl/02_painel_LED_ABS_1x.stl` | 3 |
| Três painéis na mesma mesa | `exports/stl/02_painel_LED_ABS_3x_mesma_mesa.stl` | 1 lote |
| Tampa da baia ABS (Ø82) | `exports/stl/03_tampa_baia_ABS.stl` | 1 |
| Base + torre integradas ABS (com 4 abas de grampo) | `exports/stl/04_05_base_torre_ABS_integradas.stl` | 1 |
| Suporte do ímã ABS (parte fixa, dois parafusos) | `exports/stl/06_suporte_ima_ABS.stl` | 1 |
| Cupom da junta 11 × 6 | `exports/stl/C01_cupom_junta.stl` | imprimir primeiro |
| Cupom do canal do LED (fatia real de 30 mm do painel) | `exports/stl/C02_cupom_canal_LED.stl` | imprimir primeiro |
| Chapa do motor (referência, NÃO imprimir) | `exports/stl/R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl` | — |
| Chapa do motor **e disco da arruela do eixo** para corte 1:1 | `fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf` / `.svg` | alumínio 2 mm |
| Montagem editável (com envelopes da eletrônica da baia) | `exports/fonte/Hologram_Orbiter_v3_0.blend` | — |
| Renders de inspeção; `montagem_baia.png` mostra o layout da baia | `exports/preview/*.png` | — |
| Parâmetros (fonte de verdade) | `CAD/parameters.json` | — |
| Gerador | `CAD/generate.py` | Blender 5.x |
| Sondagem de malha por raios (gerador e validador) | `CAD/probe.py` | NumPy |
| Critérios de aceitação (§9), medidos na malha | `reports/ACEITACAO.md` | automático |
| Relatório geométrico | `reports/geometry_report.json` | automático |
| Validação independente dos STL (topologia + enrolamento) | `reports/stl_validation.json` | automático |
| Relatório de validação | `reports/RELATORIO_VALIDACAO.md` | — |

A tampa do cilindro de contenção (peça 07) saiu do pacote: o invólucro está
fora de escopo (06-PENDENCIAS B7, confirmado em 03/09). `containment_cap.enabled = true` a devolve.

## Como regenerar e verificar

Requer Blender 5.x e Python 3 com NumPy. Na raiz deste pacote:

```sh
./scripts/build.sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts/tests -v
blender -b --python-exit-code 1 --python tests/blender_bay_entries.py
```

O build usa staging, propaga erros Python/critério e valida o inventário completo
de nove STLs (dez se a tampa de contenção for habilitada). Só publica depois de
verificar geração, malhas, corte e renders. Falhas preservam os artefatos anteriores.
`reports/build_manifest.json` registra hashes de parâmetros, código e artefatos.

`./scripts/build.sh --no-render` omite todas as prévias e remove as antigas do
pacote publicado, para não misturar revisões. Use `--parameters caminho.json`
para uma configuração alternativa, ou `BLENDER=/caminho/blender`.
As folgas do socket e do cupom são derivadas pela função `CAD/parameters.py` da
espiga e de `quality.joint_xy_clearance_each_side` / `joint_bottom_clearance`.

## Resultados e montagem

[RELATORIO_VALIDACAO.md](reports/RELATORIO_VALIDACAO.md) é gerado na execução;
[ACEITACAO.md](reports/ACEITACAO.md) detalha os critérios e [FISICA.json](reports/FISICA.json)
separa cálculo geométrico, cargas aproximadas e premissas não validadas.
Consulte os relatórios para massas e contrapesos atuais: o subtotal nominal
inclui o Hall, mas os chicotes de seis condutores ainda precisam ser reconciliados
com ferragens reais. A aprovação do subtotal não é aceite da massa final.

A porca do eixo deve ser apertada antes de instalar a bateria e fechar a tampa.
Use [FIACAO_E_MONTAGEM.md](docs/FIACAO_E_MONTAGEM.md),
[GUIA_IMPRESSAO.md](docs/GUIA_IMPRESSAO.md) e
[MEDICOES_DE_ENTRADA.md](docs/MEDICOES_DE_ENTRADA.md).
