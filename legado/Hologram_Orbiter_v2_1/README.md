# Hologram Orbiter v2.1 — projeto CAD para fabricação

Este diretório contém o CAD paramétrico, os STL em milímetros, a montagem
Blender, cupons de calibração e os relatórios de validação do Hologram Orbiter
v2.1. A fonte de requisitos é
[`../Especificacao-CAD-v2.1.md`](../Especificacao-CAD-v2.1.md).

## Estado da liberação

**PROVISÓRIO — NÃO LIBERADO PARA GIRO A 1800 RPM.**

As malhas foram geradas e validadas para impressão, mas a especificação deixa
interfaces físicas sem medição e contém conflitos de segurança. É aceitável
imprimir os dois cupons de calibração. Não é aceitável operar o rotor em alta
rotação até fechar os itens de [`docs/PENDENCIAS_CRITICAS.md`](docs/PENDENCIAS_CRITICAS.md).

## Arquivos principais

| Uso | Arquivo | Quantidade |
|---|---|---:|
| Aranha ABS | [`exports/stl/01_aranha_ABS.stl`](exports/stl/01_aranha_ABS.stl) | 1 |
| Painel ABS | [`exports/stl/02_painel_LED_ABS_1x.stl`](exports/stl/02_painel_LED_ABS_1x.stl) | 3 |
| Três painéis na mesma mesa | [`exports/stl/02_painel_LED_ABS_3x_mesma_mesa.stl`](exports/stl/02_painel_LED_ABS_3x_mesma_mesa.stl) | 1 lote |
| Tampa ABS | [`exports/stl/03_tampa_baia_ABS.stl`](exports/stl/03_tampa_baia_ABS.stl) | 1 |
| Base + torre integradas ABS | [`exports/stl/04_05_base_torre_ABS_integradas.stl`](exports/stl/04_05_base_torre_ABS_integradas.stl) | 1 |
| Coxim TPU opcional | [`exports/stl/07_coxim_TPU95A_4x_mesma_mesa.stl`](exports/stl/07_coxim_TPU95A_4x_mesma_mesa.stl) | 4 |
| Cupom da junta | [`exports/stl/C01_cupom_junta_11x6.stl`](exports/stl/C01_cupom_junta_11x6.stl) | testar primeiro |
| Cupom do canal LED | [`exports/stl/C02_cupom_canal_LED_13x1p8.stl`](exports/stl/C02_cupom_canal_LED_13x1p8.stl) | testar primeiro |
| Montagem editável | [`exports/fonte/Hologram_Orbiter_v2_1.blend`](exports/fonte/Hologram_Orbiter_v2_1.blend) | — |
| Parâmetros | [`CAD/parameters.json`](CAD/parameters.json) | fonte de verdade |
| Gerador | [`CAD/generate.py`](CAD/generate.py) | Blender 5.x |

O anel TPU e o suporte de motor possuem STL apenas como **referência**. A
especificação classifica o anel como peça não impressa e exige o suporte em
alumínio de 2 mm; não os substitua por ABS.

## Como regenerar

Requer Blender 5.x e Python 3 com NumPy para a validação independente.

```bash
./scripts/build.sh
```

O comando recria os STL, o `.blend`, a prévia e os relatórios. Para alterar as
interfaces ainda não medidas, edite `CAD/parameters.json`; não edite o STL.

## Resultado geométrico

- Painel: 208 mm de altura; canal 13 × 1,8 mm; socket 11,2 × 6,2 mm; Datum D no
  centro, 104 mm da base.
- Aranha: cubo Ø80 × 6 mm, três braços a 120°, ombro em r=104 mm e espiga até
  r=126 mm.
- Base: footprint Ø300 mm; baia central de 80 mm; topo da torre em Z=154 mm.
- Datum do rotor assumido: Z=188 mm, usando altura provisória de 34 mm entre o
  suporte e o Datum B.
- Todos os STL estão orientados para começar em Z=0 e usam coordenadas em mm.

Consulte [`docs/GUIA_IMPRESSAO.md`](docs/GUIA_IMPRESSAO.md) antes de fatiar e
[`reports/RELATORIO_VALIDACAO.md`](reports/RELATORIO_VALIDACAO.md) para os
resultados dimensionais e de malha.
