# Hologram Orbiter

Display volumétrico por persistência de visão (POV) com três painéis de LEDs.
Ponto de projeto: raio médio **100 mm**, **1800 RPM**, 29 LEDs por painel e 180
colunas angulares (90 passagens por segundo; desempenho óptico depende de
firmware e ensaio).

**Versão vigente: v4.0 (14/11/2026)** — promove a base suspensa em paralelogramo
travável + aranha reforçada (`3.1-P.2`) e o motor **`AX-2810Q 750KV`** ao plano
principal. Os documentos e o pacote CAD da `v3.0` (base rígida + `A2212 920KV`)
foram arquivados em [`legado/v3.0/`](legado/v3.0/).

## Estado em 14/11/2026

> **PROVISÓRIO — não liberado para girar o rotor completo nem para fabricação
> definitiva dos painéis.**

- **CAD e física v4.0 regenerados (`69/69` critérios de aceitação):**
  - **Base suspensa em paralelogramo travável (PETG):** palco pendurado em 8
    hastes de `1,5 × 1,5 mm` (translação prevista em `4,38 Hz` / crítica
    `~263 RPM`), trava reversível 4 + 4 para operar em modo rígido e bandeja
    provisória para amortecimento viscoso com óleo de silicone `10 000 cSt`.
  - **Aranha reforçada (PETG):** aleta vertical em **D** + alma em perfil de asa
    invertido até o ombro (`r = 74 mm`), baia ampliada para **`Ø80/84 × 47 mm`**
    com prateleira em `Z = 28 mm` para futura placa própria.
  - **Motor e fixação (`AX-2810Q 750KV`):** medidas de bancada de `13/11/2026`
    incorporadas (assento serrilhado `Ø13` a `29 mm` da base, trecho liso
    `Ø4 × 5 mm` com bucha `Ø6`, rosca `M4 × 10`, porca `DIN 985 M4` + arruela
    `DIN 9021 M4`, furos de base em cruz `16/19 mm`, fios `Ø3,0 mm` em ganchos na
    torre, chapa `R01` com alívio `Ø11`). Réplica provisória `R01P` em PLA
    disponível até o corte em alumínio 2 mm.
- **Eletrônica e acionamento em bancada:**
  - **SPI Quad** montada ponto a ponto em placa perfurada
    ([`MONTAGEM-PONTO-A-PONTO.md`](eletronica/interface/MONTAGEM-PONTO-A-PONTO.md)),
    4 condutores por painel (`+5 V`, `GND`, `CLK`, `DATA`), em teste de bancada
    com [`firmware/teste-fitas-c3/`](firmware/teste-fitas-c3/).
  - **ESC + `AX-2810Q`:** gravados em `13/11/2026` (`Startup Power = 0,50`,
    `Demag = High`, `Brake on stop = On`; ver
    [`esc_blheli_s_2026-11-13/`](esc_blheli_s_2026-11-13/registro.md)). Sentido
    de giro anti-horário, calibração do pulso por tacômetro, grampo/resistor de
    descarga no barramento do ESC e ajustes de rampa no firmware da base ainda
    pendentes antes de girar com rotor.
- **Pendências principais antes de girar:** fechar medição da altura do corpo do
  `AX-2810Q` (`26 mm` de catálogo), imprimir peças e executar o ensaio de
  impacto **`C0`** da suspensão (modo travado e modo solto), reconciliar massa
  real pesada até o teto provisório de **`420 g`** e cumprir os bloqueadores do
  plano 04.

Os relatórios automáticos são a referência da execução atual do CAD:

- [Aceitação geométrica (69/69)](Hologram_Orbiter_v4/reports/ACEITACAO.md)
- [Validação, massas CAD e acionamento](Hologram_Orbiter_v4/reports/RELATORIO_VALIDACAO.md)
- [Cálculos reproduzíveis](Hologram_Orbiter_v4/reports/FISICA.json)
- [Revisões históricas (v3.0)](revisoes/LEIA-ME.md)

## Números de projeto (v4.0)

| Grandeza | Valor e condição |
|---|---|
| Rotação / velocidade angular | **1800 RPM** / 188,496 rad/s (30 rps, 90 Hz de imagem) |
| Cilindro de imagem | **Ø208 × 201 mm**, 29 LEDs × 180 colunas |
| Motor / acionamento | **AX-2810Q 750KV** (`R_ef = 0,225 Ω`, `Kt = 12,73 mN·m/A`) / **ESC LittleBee Spring 20A** |
| Corrente de regime prevista | **4,04 A** de fase (**3,62 A** melhor caso); **14,81 W** na fonte (`1,48 A` a 10 V, `1,23 A` a 12 V, `η_ESC = 95%`) |
| Temperatura prevista | **40,3 °C** (`37,8 °C` melhor caso) sob `Rth = 3,5 K/W`; limite `< 55 °C` (medir no Bloqueador B) |
| Fonte do ESC | **10–12 V** com limite de **30 A**; **grampo ou resistor de descarga obrigatório** (`Brake on stop = On`) |
| Perfil de partida (chute legado, não aprovado) | Chute de `1400 µs`: no modelo médio para o `AX-2810Q`, `16,37–19,65 A` de fase parado e pico de `1680 RPM` (10 V) / `1959 RPM` (12 V); excede Bloqueador D e exige revisão + rampa `≥ 300 RPM/s` pela crítica `~263 RPM` |
| Esticada a 2000 RPM | `4,99 A` / `20,63 W` / `47,0 °C` estimados; **não liberada** (3× próximo do modo ~89 Hz e > 20 W) |
| Massa do rotor | Teto provisório **420 g**; subtotal nominal **352,14 g** (reconciliar chicotes 4 fios e pesar) |
| Carga radial no painel | **158,1 N** a `44,5 g` (`159,9 N` no teto de `45 g`) |
| Energia cinética | **27,5–27,6 J** no rotor (`J = 1,55 g·m²` assumido); **7,9 J** (`18,9 m/s`) por painel solto |
| Desbalanceamento de referência | **8,4 g·mm** (ref. G6.3 a 1800 RPM; recalcular com massa pesada e balancear em 2 planos) |
| Modos da suspensão (estimativa `E = 1900 MPa`) | Translação **4,38 Hz** (**263 RPM**); *yaw* **12,66 Hz** (**759 RPM**, evitar banda `760–870 RPM`); combinado balanço+torre **89,3 Hz** (3× em `~1786 RPM`); balanço **105,2 Hz**; flambagem `36,3 N` |

A PCB KiCad de interface `r0.2` está preservada em [`eletronica/interface/`](eletronica/interface/README.md)
como referência de projeto; para o protótipo atual sem PCB fabricada, seguir o
roteiro de soldagem em perfboard [`MONTAGEM-PONTO-A-PONTO.md`](eletronica/interface/MONTAGEM-PONTO-A-PONTO.md).

## Documentos vigentes (v4.0)

| Uso | Arquivo |
|---|---|
| Cotas, geometria e memória de cálculo | [`01-ESPECIFICACAO-CAD-v4.0.md`](01-ESPECIFICACAO-CAD-v4.0.md) |
| Fases e portões `G0`–`G5` | [`02-PLANO-DE-PROJETO-v4.0.md`](02-PLANO-DE-PROJETO-v4.0.md) |
| Componentes, ferragens e instrumentos | [`03-LISTA-DE-COMPONENTES-v4.0.md`](03-LISTA-DE-COMPONENTES-v4.0.md) |
| Critérios físicos de aceite (`C0`, `A`–`E`) | [`04-PLANO-DE-ENSAIOS-v4.0.md`](04-PLANO-DE-ENSAIOS-v4.0.md) |
| Eletrônica **SPI Quad**, ESC e firmware | [`05-ESQUEMA-ELETRICO-v4.0.md`](05-ESQUEMA-ELETRICO-v4.0.md) |
| O que ainda falta | [`06-PENDENCIAS-ABERTAS-v4.0.md`](06-PENDENCIAS-ABERTAS-v4.0.md) |
| Medições, vocabulário e premissas | [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) |
| CAD, 16 STLs, DXF e guias de impressão/montagem | [`Hologram_Orbiter_v4/README.md`](Hologram_Orbiter_v4/README.md) |
| Firmware (base ESC + bancada SPI Quad C3) | [`firmware/README.md`](firmware/README.md) |
| Interface SPI Quad (perfboard e KiCad ref.) | [`eletronica/interface/README.md`](eletronica/interface/README.md) |
| Arquivo morto (`v3.0` e `v2.1`) | [`legado/LEIA-ME.md`](legado/LEIA-ME.md) |

Parâmetros do CAD governam cotas, a especificação governa requisitos e o plano
de ensaios governa aceite físico. Divergências devem ser corrigidas na fonte,
nunca escolhendo o número mais favorável. A [proposta e suas apresentações](proposta/README.md)
conservam os números históricos da proposta inicial.

Sentido de giro: **anti-horário visto de cima**; bordo de ataque em `+y` local.
Balança de `0,01 g`, contenção física, grampo no barramento do ESC, base
grampeada e operação remota são obrigatórios em ensaio.
