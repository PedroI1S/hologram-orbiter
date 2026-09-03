# Hologram Orbiter v3.0 — pacote CAD para fabricação

CAD paramétrico, STL em milímetros, montagem Blender, cupons de calibração,
referência de corte da chapa e relatórios de validação do Hologram Orbiter
v3.0. A fonte de requisitos é
[`../01-ESPECIFICACAO-CAD-v3.0.md`](../01-ESPECIFICACAO-CAD-v3.0.md).
Ponto de operação congelado: raio 100 mm @ 1800 RPM = 90 Hz.

A pasta `../legado/Hologram_Orbiter_v2_1/` é registro histórico e não foi alterada.

## Estado da liberação

**PROVISÓRIO — AGUARDANDO MEDIÇÕES. Não liberado para girar a 1800 RPM.**

Regenerado em 03/09/2026 (revisão 3.0.2) com a lista `06-PENDENCIAS-ABERTAS`
(A1, A2, B1 a B11), os desvios de spec ratificados pelo revisor, as medições do
glossário e o desenho cotado do motor. Liberados para impressão: os dois cupons
(`C01`, `C02`), os painéis, a aranha, a tampa da baia, o suporte do ímã e a
base. Os 54 critérios automáticos passam.

**Uma medição antes de comprar ferragem:** a partir da face da campânula em que
o cubo assenta, a altura do topo do **colar Ø8** do eixo e da ponta da rosca. O
desenho diz colar 5 + rosca 7 numa saliência total de 14; a fixação foi
refeita para valer nas duas leituras (ver abaixo), mas o número real decide se
sobram 3 mm ou 1 mm de rosca.

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

## Como regenerar

Requer Blender 5.x (`brew install --cask blender`) e Python 3 com NumPy para a
validação independente (`pip3 install --user numpy`).

```bash
./scripts/build.sh
```

Gera STL, `.blend`, prévias, renders de inspeção, DXF/SVG e relatórios. Para
mudar qualquer cota, edite `CAD/parameters.json` e rode de novo. Nunca edite um
STL à mão. `./scripts/build.sh --no-render` pula as prévias da montagem.

## O que mudou em 03/09/2026

- **Booleanas um cortador por vez.** `subtract_all()` concatenava os cortadores
  e fazia uma só diferença; onde dois se sobrepunham o resultado tinha
  enrolamento −1 (pino sólido no bolso da porca e barra no socket, nos dois
  furos M3 de cada painel — A1). Confirmado por traçado de raios antes da
  correção; depois dela o eixo de cada parafuso é vazio de ponta a ponta.
- **Canal do LED de 12,4 × 2,0** para a fita medida em 2,0 mm: o PCB cola no
  fundo e os LEDs ficam rentes à face; a parede engrossa para 2,8 numa faixa
  de 14,4 mm e o piso de **0,80 mm** (medido na malha) faz a mesma ponte de
  12,4 mm do canal original. O "canal em degrau" da spec, com o PCB num canal
  raso e os LEDs num rasgo mais fundo, foi abandonado: os LEDs ficam em cima
  do PCB, e com a fita montada para fora eles sobressairiam 1,4 mm.
- **Cubo Ø92, baia Ø82/Ø78 × 26** (B10), rasgos de refrigeração em r 41,5–45,
  alívios r 17–36, postes da tampa em y = ±35, berço para o pack LiFe
  58 × 30 × 17 (50 g).
- **Fixação do eixo refeita pelo desenho do motor.** O colar Ø8 × 5 (ou 7) sob
  a rosca sobe acima do fundo de qualquer rebaixo do cubo: uma arruela M6 Ø20
  assentaria no colar e a porca não apertaria o cubo. Agora: **sem rebaixo,
  arruela Ø20 × Ø8,5 × 2 em alumínio** (disco incluído na referência de corte
  da chapa) e **porca M6 fina DIN 439B com Loctite 243**. Três critérios novos
  conferem furo × colar, altura do colar × arruela e rosca sobrando (3 mm; 1 mm
  na leitura de 12).
- **Layout da baia (D2)** parametrizado e verificado: placa de interface em +x
  sob a janela da tampa, ESP32-C3 em −x, buck mini560 em pé numa ranhura na
  parede a 140°, capacitor em pé numa cerca, tudo elevado em pilares de 6 mm
  para deixar o piso livre aos feixes. Massas de catálogo somam 15,0 g, a
  folga exata. Desbalanceamento nominal 73 g·mm a 14°, corrigido com **2,2 g**
  de massa de tungstênio no alívio de 180°.
- **Fillet cubo→braço** (cunha a 45°), **ombro em 74,0** exato, **furos só na
  flange superior**, **quatro abas de grampo**, **suporte do ímã sob dois
  parafusos**, tampa 07 removida, cupom C02 como fatia real do painel.
- **Sensor hall e ímã a 20°** (eram 30°): o rasgo dos terminais passa a sair
  debaixo da placa de interface, onde está o pull-up, sem colidir com um pilar.
- **Critérios medidos na malha** por traçado de raios; validador com teste de
  enrolamento e faces coincidentes. O traçado achou e corrigiu uma lâmina de
  ar de 0,05 mm sob a flange da torre, herdada da v3.0 original.
- Datum B em **Z = 186** (chapa 156 + corpo do motor 24 mm **medido** + cubo 6).

## Resultado geométrico (densidade maciça de ABS 1,04 g/cm³)

| Peça | Massa CAD | Limite/alvo |
|---|---:|---|
| Painel nu | 31,9 g | — |
| Painel montado (fita 6,2 + ferragens 4,0) | 42,1 g | ≤ 45 g ✅ |
| Aranha (Ø92, baia de 26, pilares e guias) | 67,5 g | ≤ 75 g ✅ |
| Tampa da baia (Ø82) | 10,1 g | ≤ 12 g ✅ |
| Rotor completo (bateria 50, eletrônica 15, ferragem do eixo 3, contrapeso 2,2) | **274,3 g** | ≤ 280 g ✅ — folga de 5,7 g |
| Base + torre com abas | 321,3 g | ≤ 330 g ✅ |
| Suporte do ímã | 1,7 g | peça estática |

Os 54 critérios automáticos passam
([`reports/ACEITACAO.md`](reports/ACEITACAO.md)). A folga do rotor é de 5,7 g
com massas de catálogo para a eletrônica: **pesar cada componente** antes de
fixar, e não trocar o mini560 por um XL4015. Consulte
[`docs/GUIA_IMPRESSAO.md`](docs/GUIA_IMPRESSAO.md) antes de fatiar,
[`docs/FIACAO_E_MONTAGEM.md`](docs/FIACAO_E_MONTAGEM.md) para a montagem e
[`docs/MEDICOES_DE_ENTRADA.md`](docs/MEDICOES_DE_ENTRADA.md) para o que ainda
precisa ser medido.
