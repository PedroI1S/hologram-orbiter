# Hologram Orbiter v4.0 — pacote CAD

**PROVISÓRIO — operação completa do rotor e fabricação definitiva dos painéis
ainda não liberadas.**  
A promoção para **v4.0** (14/11/2026) torna o conjunto **base suspensa em
paralelogramo travável + aranha reforçada** (`3.1-P.2`) e o motor
**`AX-2810Q 750KV`** o pacote principal do projeto. A versão `v3.0` (base rígida
+ `A2212 920KV`) foi arquivada em [`../legado/v3.0/`](../legado/v3.0/).

Principais alterações estruturais e mecânicas incorporadas nesta revisão:
- **Aranha em PETG (`Ø92` / baia `Ø80/84 × 47 mm`):** aleta vertical em **D** +
  alma inferior em **perfil de asa invertido** da raiz até o ombro (`r = 74 mm`),
  passando a espiga (`11 × 6 mm`, `r = 77 mm`) a ser a seção crítica (`9,7 MPa`
  a 10°). Baia ampliada em `+1 mm` de raio para folga dos cabos, com
  **prateleira em `Z = 28 mm`** reservando espaço para uma futura placa própria.
- **Base suspensa em paralelogramo travável em PETG:** palco + torre maciça
  `Ø40` (`05_palco_torre_PETG.stl`) pendurado em 8 hastes verticais PETG
  `1,5 × 1,5 mm` (`4,38 Hz` em translação, crítica `~263 RPM`), com trava
  reversível `4 + 4` para modo rígido (`09_buchas_trava_4x.stl`) e bandeja
  provisória para amortecimento viscoso com óleo de silicone `10 000 cSt`
  (`10_bandeja_amortecedor.stl`).
- **Motor `AX-2810Q 750KV` (`13/11/2026`):** assento na base serrilhada `Ø13`
  (`29 mm` sobre a chapa `R01`), bucha `Ø6` sobre eixo liso `Ø4 × 5`, porca
  `M4 DIN 985` + arruela `DIN 9021 M4`, alívio central `Ø11` na chapa `R01`,
  suporte do ímã afastado (`2,1 mm` da campânula `Ø35`), ganchos na torre para
  fios `Ø3,0 mm` (`Z = 82..113 mm`) e saída do cabo pela pista da base.
- **Fiação SPI Quad (4 condutores/painel):** `+5 V`, `GND`, `CLK` e `DATA` sem
  retorno na ponta dos painéis, entradas pela parede da baia `Ø80` em `r = 38..43`.

## Arquivos

| Uso | Arquivo | Qtd |
|---|---|---:|
| Aranha PETG reforçada (aleta D + asa invertida, baia `Ø80/84×47`, prateleira `Z=28`) | `exports/stl/01_aranha_PETG.stl` | 1 |
| Painel LED ABS | `exports/stl/02_painel_LED_ABS_1x.stl` | 3 |
| Três painéis ABS na mesma mesa | `exports/stl/02_painel_LED_ABS_3x_mesma_mesa.stl` | 1 lote |
| Tampa da baia PETG (`Ø84 × 5 mm`, 6 copos de balanceamento) | `exports/stl/03_tampa_baia_PETG.stl` | 1 |
| Base fixa PETG (`Ø280 mm`, batentes/EVA, abas de grampo; **imprimir invertida**) | `exports/stl/04_base_fixa_PETG_imprimir_invertida.stl` | 1 |
| Palco suspenso + 8 aletas + torre maciça `Ø40` + ganchos + pás amortecedor (PETG) | `exports/stl/05_palco_torre_PETG.stl` | 1 |
| Suporte do ímã PETG (arco afastado `r_int 19,6` p/ `Ø35`, dois `M4×20`) | `exports/stl/06_suporte_ima_PETG.stl` | 1 |
| Haste flexível PETG `1,5 × 1,5 mm` (avulsa / reposição) | `exports/stl/08_haste_flexivel_macia_1p5_1x.stl` | reposição |
| Lote de 8 hastes flexíveis PETG `1,5 × 1,5 mm` | `exports/stl/08_hastes_flexiveis_macia_1p5_8x.stl` | 1 lote |
| 4 buchas da trava radial (`M3 × 40`) em PETG | `exports/stl/09_buchas_trava_4x.stl` | 1 lote |
| Bandeja única de 4 cubas para amortecedor a óleo `10 000 cSt` (PETG, opcional) | `exports/stl/10_bandeja_amortecedor.stl` | 1 |
| Cupom da junta `11 × 6` | `exports/stl/C01_cupom_junta.stl` | imprimir primeiro |
| Cupom do canal do LED (fatia real de 30 mm do painel) | `exports/stl/C02_cupom_canal_LED.stl` | imprimir primeiro |
| Chapa do motor (referência em alumínio 2 mm, **NÃO imprimir como peça final**) | `exports/stl/R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl` | — |
| Réplica provisória da chapa `R01` em PLA 2 mm (alívio central `Ø11`) | `exports/stl/R01P_suporte_motor_PLA_provisorio.stl` | 1 provisório |
| Arruela provisória do eixo `M4` em PLA 2 mm (`Ø20 × Ø4,5`) | `exports/stl/R01P_arruela_eixo_M4_PLA_provisoria.stl` | 1 provisório |
| Chapa do motor e disco de referência para corte 1:1 | `fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf` / `.svg` | alumínio 2 mm |
| Placa de ensaio PLA (`scripts/r01_placa_teste.py`, G-code Creality) | `teste_impresso/R01T_placa_teste_PLA_2mm.*` | PLA 2 mm |
| Montagem editável (com envelopes da eletrônica + reserva da placa própria) | `exports/fonte/Hologram_Orbiter_v4.blend` | — |
| Renders de inspeção (31 vistas incluindo suspensão, hastes e baia) | `exports/preview/*.png` | — |
| Parâmetros (fonte de verdade única) | `CAD/parameters.json` | — |
| Gerador e sondagem / física | `CAD/generate.py`, `CAD/probe.py`, `CAD/physics.py` | Blender 5.x + NumPy |
| Critérios de aceitação (`69/69`), medidos na malha | `reports/ACEITACAO.md` | automático |
| Relatórios e validação independente STL | `reports/{RELATORIO_VALIDACAO.md,FISICA.json,geometry_report.json,stl_validation.json}` | automático |

A tampa do cilindro de contenção (antiga peça 07) continua desativada
(`containment_cap.enabled = false`). A canaleta periférica também fica desligada
na base fixa porque a casca cônica da suspensão nasce sobre a pista.

## Como regenerar e verificar

Requer Blender 5.x e Python 3 com NumPy. Na raiz deste pacote:

```sh
./scripts/build.sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts/tests -v
blender -b --python-exit-code 1 --python tests/blender_bay_entries.py
```

O build usa staging, propaga erros Python/critério e valida o inventário
completo dos **16 STLs** publicados (mais DXF/SVG, `.blend`, 31 previews e
relatórios). Falhas preservam os artefatos anteriores; `reports/build_manifest.json`
registra hashes de parâmetros, código e artefatos.

`./scripts/build.sh --no-render` omite as prévias e remove as antigas do pacote
publicado. Use `--parameters caminho.json` para testar variações, ou
`BLENDER=/caminho/blender`.

## Resultados e montagem

- [`reports/RELATORIO_VALIDACAO.md`](reports/RELATORIO_VALIDACAO.md): massas CAD,
  seções dos braços da aranha, dinâmica da suspensão, acionamento `AX-2810Q` e
  cotas Z globais.
- [`reports/ACEITACAO.md`](reports/ACEITACAO.md): 69/69 critérios geométricos e
  de sondagem por raios.
- [`reports/FISICA.json`](reports/FISICA.json): memória numérica reproduzível
  (cargas, frequências da suspensão, amortecedor a óleo, corrente/temperatura e
  partida).

O subtotal nominal do rotor é **352,14 g** contra o teto provisório de **420 g**
para o `AX-2810Q`, porém os chicotes reais de 4 condutores, a perfboard montada
e as peças impressas ainda precisam ser pesados e reconciliados.

A porca `M4 DIN 985` do eixo deve ser apertada sobre a arruela `DIN 9021 M4`
antes de instalar a bateria e fechar a tampa. Consulte:
- [`docs/FIACAO_E_MONTAGEM.md`](docs/FIACAO_E_MONTAGEM.md)
- [`docs/GUIA_IMPRESSAO.md`](docs/GUIA_IMPRESSAO.md)
- [`docs/MEDICOES_DE_ENTRADA.md`](docs/MEDICOES_DE_ENTRADA.md)
- [`docs/PENDENCIAS.md`](docs/PENDENCIAS.md)
