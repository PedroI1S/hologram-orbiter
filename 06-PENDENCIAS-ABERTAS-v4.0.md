# Pendências abertas — Hologram Orbiter v4.0

Lista unificada do que **falta medir, decidir ou validar em bancada** para o
**Hologram Orbiter v4.0** (atualizada em 14/11/2026 após promoção da base em
paralelogramo + aranha reforçada + motor `AX-2810Q 750KV` + `SPI Quad`).
Pendências exclusivas da v3.0/A2212 permanecem arquivadas em
[`legado/v3.0/`](legado/v3.0/).

---

## Abertas — críticas antes de imprimir/girar

### M1 · Altura exata do corpo do `AX-2810Q 750KV` e folga de rolamentos
Pedro mediu em 13/11/2026 **`29 mm`** da base do motor ao topo da base
serrilhada (`eixo liso Ø4 × 5`, `rosca M4 × 10`, `fios Ø3,0 mm`, `cruz 16/19`,
`R ≈ 0,20–0,25 Ω/fase`), mas a altura isolada do corpo até a campânula
(`26 mm`) ainda vem de catálogo HobbyKing.
- **Fechar assim:** antes de imprimir o palco/torre (`05_palco_torre_PETG.stl`),
  confirmar no paquímetro a altura do corpo até a face da campânula e inspecionar
  manualmente a folga axial/radial dos rolamentos do eixo.

### M2 · Impressão e ensaio de impacto da suspensão (`C0`)
Nenhuma peça da arquitetura v4.0 foi impressa na versão final ainda (`base fixa`,
`palco + torre`, `8 hastes`, `aranha reforçada PETG`, `trava 4 + 4`, `bandeja`).
- **Fechar assim:** imprimir as peças em PETG, montar sobre calços de 4 mm,
  apertar os blocos superiores por último, executar o **ensaio C0** (`04-PLANO-DE-ENSAIOS-v4.0.md`):
  confirmar translação em `4,0–5,0 Hz`, giro em `12–15 Hz` (`Q ≤ 35`) e modo
  combinado **`≥ 95–100 Hz`** (se ficar entre `80` e `95 Hz`, limitar operação
  a `1600 RPM`). Verificar também necessidade de óleo silicone `10 000 cSt` na
  bandeja e reaperto da trava `4 + 4` após 24 h.

### M3 · Sentido de giro, tacômetro e revisão do perfil de partida (`firmware/controle-motor`)
Em 13/11/2026 o `AX-2810Q` girou sem carga após refazer uma solda de fase, com
`ESC BLHeli_S 16.7` gravado (`Startup = 0,50`, `Demag = High`, `Brake on stop = On`).
- **Fechar assim:**
  1. Confirmar com o motor preso (sem aranha) que gira **anti-horário visto de +Z**;
     se inverter, trocar dois fios de fase ou regravar `offset 11 = 2`.
  2. Instalar **grampo ou resistor de descarga (`12,6–16,8 V`) no barramento do ESC**
     (indispensável com `Brake on stop = On`).
  3. Atualizar [`firmware/controle-motor/`](firmware/controle-motor/) para
     atravessar `200–400 RPM` a `≥ 300 RPM/s` (`≥ 50 µs/s`), manter alvo `≥ 1200 µs`
     (fora de `760–870 RPM`), adequar o chute aos limites do Bloqueador D (`≤ 36,1 W`,
     `≤ 1800 RPM`) e calibrar `CEILING_US` com tacômetro no `AX-2810Q`.
  4. Cortar a **chapa `R01` em alumínio 2 mm (furo central Ø11)** antes dos ensaios
     de rotação com rotor completo (a réplica PLA `teste_impresso/` é apenas
     provisória para bancada em baixa rotação).

---

## Abertas — estrutura, massa e instrumentação

### R01 · Resistência, carga FDM e fluência dos painéis (bloqueia lote definitivo)
Seção conferida (`Iyy = 589,885 mm⁴`), estimativa uniforme `3,83–7,83 mm` /
`21,7–29,1 MPa` (`44,5–45 g`). Imprimir os cupons `C01` e `C02` primeiro e
validar transferência de carga, módulo real em ABS/PETG FDM e crescimento de
ponta (`< 0,5 mm` em 1 h no Bloqueador B) antes de liberar operação contínua.
A espiga `11 × 6 mm` (`9,7 MPa` estimados a 10° na aranha reforçada) também não
foi ensaiada com fadiga de partidas/paradas em PETG.

### R04/R05 · Instrumentação de temperatura, fase e 2 planos
- Medição térmica sem contato validada ou sensor embarcado na campânula do
  `AX-2810Q` (nunca termopar com fio girando) e medição embarcada da bateria em G4.
- Referência fixa **1 pulso/volta** sincronizada com duas respostas de
  acelerometria independentes para o balanceamento dinâmico em dois planos (C1).

### D1 / D3 · Pesagem real, SPI Quad na baia e teto de massa (`420 g`)
- Pesar as peças reais impressas em PETG/ABS (infill), placa perfurada ponto-a-ponto
  (`≤ 5,5 g`), ESP32-C3, buck, capacitor, 3 fitas e os **chicotes 4 vias SPI Quad**
  idênticos nos 3 painéis (`+5V`, `GND`, `CLK`, `DATA`).
- Atualizar `CAD/parameters.json` com as massas reais, regenerar contrapesos e
  verificar o envelope disponível para eventual placa própria futura na prateleira
  `Z = 28 mm`.

---

## Abertas — eletrônica de bordo e firmware óptico

### C2 / C3 / C8 · Polaridade, campo do motor e entreferro do A3144
Testar em bancada antes de colar o Hall nu (VCC **5 V**, pull-up `10 kΩ` → **3,3 V**):
- confirmar qual face do ímã leva a saída a **nível baixo** diante da face
  marcada do TO-92 a ~3 mm (C2);
- verificar se o campo estático da campânula `Ø35` do `AX-2810Q` interfere no
  sensor a `r = 29 mm` (C3);
- medir entreferro montado antes de colar o ímã (nominal `2,5 mm`, tolera até
  `3,0 mm` com N35; se passar, calçar ou usar `Ø5 × 3 N52`) (C8).

### C7 · Buck `mini560` — tensão mínima de entrada (`V_in_min ≤ 5,5 V`)
Confirmar no módulo real em carga (`≤ 4,25 A` provisórios) entre `7,2 V` e
`5,8 V` (LiFe 2S) se não entra em dropout abaixo de `4,5 V` na saída, garantindo
`V_IH` do `74AHCT125`/fitas e limite térmico dentro da baia fechada.

### C10 / C11 · Firmware final SPI Quad + enlace ESP-NOW + página web
- Migrar o teste de bancada (`firmware/teste-fitas-c3/`, atualmente em bit-bang
  lento ~250 kHz) para driver **SPI DMA em velocidade nominal** compatível com
  180 colunas a 1800 RPM + interrupção de índice no `GPIO3` + medição de sinal
  no osciloscópio através dos `33 Ω` e chicotes reais (C10).
- Implementar e testar o enlace **ESP-NOW** e portal cativo na `ESP32` da base
  (`tremor < 46 µs`, 100 quadros com CRC na contenção de policarbonato) (C11).

---

## Resolvidas na promoção para v4.0 (histórico recente)

- **R02 (ruptura da aranha v3.0):** tratada estruturalmente na aranha v4.0
  (aleta em D + alma em asa + PETG) e na base em paralelogramo com `Brake on stop = On`.
- **C10 (decisão cadeia vs. SPI Quad):** **SPI Quad adotado** como arquitetura
  principal na placa perfurada ponto-a-ponto e em [`firmware/teste-fitas-c3/`](firmware/teste-fitas-c3/).
- **B'1 / C9 (eixo, alívio chapa e ajuste ESC):** eixo/base serrilhada do
  `AX-2810Q` medidos (`29 mm`, `M4`), chapa `R01` ampliada para **Ø11 mm**
  (com réplica PLA provisória em `teste_impresso/`), `R_ef` medida (`0,225 Ω`
  médio) e ESC gravado em 13/11/2026 (`Startup = 0,50`, `Demag = High`,
  `Brake on stop = On`).
- **Baia pequena para fiação:** ampliada para **Ø80/84 × 47 mm** em 13/11/2026.
