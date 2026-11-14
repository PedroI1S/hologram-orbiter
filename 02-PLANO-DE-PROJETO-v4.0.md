# Plano de projeto — Hologram Orbiter v4.0

**Versão vigente em 14/11/2026:** promove a arquitetura de **base suspensa em
paralelogramo travável (`3.1-P.2`)**, a **aranha reforçada em PETG** com baia
**Ø80/84 × 47 mm**, a topologia óptica **SPI Quad** e o novo motor
**AX-2810Q 750KV** a plano principal do projeto. A linha v3.0 (base rígida e
motor A2212 920KV) foi arquivada em [`legado/v3.0/`](legado/v3.0/).

**Provisório:** nenhuma peça do pacote v4.0 foi impressa na versão final nem
validada em ensaio com o rotor montado. Operação e fabricação definitiva dos
painéis dependem de fechar as medições de entrada e os bloqueadores do
[`04-PLANO-DE-ENSAIOS-v4.0.md`](04-PLANO-DE-ENSAIOS-v4.0.md).

---

## 1. O que o projeto entrega

Um display volumétrico por persistência de visão: três painéis de LEDs
endereçáveis girando a **1800 RPM** formam uma imagem cilíndrica de
**Ø208 × 201 mm**, com **29 × 180 pixels** e taxa de imagem de **90 Hz**.

Entregáveis finais:

1. protótipo mecânico balanceado sobre base suspensa em paralelogramo travável,
   operando de forma estável e contida;
2. cadeia óptica funcional em **SPI Quad** — fitas HD107S, buffer 74AHCT125,
   sensor Hall A3144 nu, imagem de teste validada em bancada e em giro;
3. os cinco bloqueadores (A a E, incluindo ensaio de impacto C0) aprovados com
   evidência registrada;
4. documentação de operação e memória de cálculo rastreáveis em
   [`Hologram_Orbiter_v4/`](Hologram_Orbiter_v4/README.md);
5. imagem enviada pelo celular: página hospedada na ESP32 da base transmitida
   por ESP-NOW ao ESP32-C3 do rotor ([`05-ESQUEMA-ELETRICO-v4.0.md`](05-ESQUEMA-ELETRICO-v4.0.md) §9).

## 2. Estado atual (14/11/2026)

| Bloco | Situação |
|---|---|
| Ponto de operação | ✅ congelado — `r = 100 mm`, `1800 RPM`, `90 Hz` |
| Acionamento | ✅ **AX-2810Q 750KV** (girando sem carga após refazer solda; falta sentido e tacômetro) · **ESC LittleBee Spring 20A** (`BLHeli_S 16.7`, gravado em 13/11 com `Brake on stop = On`, `Startup = 0,50`, `Demag = High`) · ESP32 da base (`firmware/esp32-base/`) |
| Cadeia óptica | 🔄 **SPI Quad** implementada em placa perfurada ponto-a-ponto ([`MONTAGEM-PONTO-A-PONTO.md`](eletronica/interface/MONTAGEM-PONTO-A-PONTO.md)) + firmware de bancada [`firmware/teste-fitas-c3/`](firmware/teste-fitas-c3/); falta integrar na baia do rotor |
| Imagem pelo celular | 🔄 planejada em `05 §9`; hardware em mãos, firmware de interface web a fazer |
| Especificação & CAD v4.0 | ✅ pacote [`Hologram_Orbiter_v4/`](Hologram_Orbiter_v4/README.md) buildado — **69/69 critérios geométricos** e **16 STLs** validados por traçado de raios (modelos numéricos ainda não ensaiados fisicamente) |
| Chapa provisória R01 | ✅ G-code PLA gerado ([`teste_impresso/`](Hologram_Orbiter_v4/teste_impresso/)) com furo central Ø11 + arruela provisória Ø20×Ø4,5; corte de alumínio 2 mm pendente |
| Medições pendentes | ⚠️ altura exata do corpo do motor (26 mm catálogo vs 29 mm medidos até o serrilhado), folga axial dos rolamentos, massa real dos chicotes 4 vias e peças em PETG/ABS |
| Ensaios de giro | ⛔ suspensos na v3.0 por ruptura de braço (27/10); retomada na v4.0 após imprimir base/palco/aranha PETG e concluir C0 + verificação estática |

## 3. Como a v4.0 resolve os problemas da v3.0

1. **Ruptura na raiz da aranha (27/10/2026):** a aranha antiga tinha braço
   de `15 × 6 mm` (`W = 103 mm³` na raiz). A aranha v4.0 acrescenta aleta em D +
   alma em asa invertida até o ombro (`r = 74 mm`, `W = 535,7 → 210,1 mm³`),
   baixando a tensão a 10° para `2,7–3,5 MPa` e transferindo o limite para a
   espiga dentro do painel (`9,7 MPa ≤ 12 MPa`), impressa em PETG.
2. **Transmissão de vibração e rigidez da base:** a base fixa cônica + palco
   em 8 hastes PETG de `1,5 mm` (`fn = 4,38 Hz`) reduz a força na mesa em 24–40×
   em regime, com opção de trava `4 + 4` para rodar rígido e bandeja para óleo
   de silicone (`10 000 cSt`).
3. **Motor com mais margem térmica e torque:** troca do A2212 920KV pelo
   **AX-2810Q 750KV** (`Kt = 12,73 mN·m/A`, +22% torque/A), reduzindo corrente
   de regime para **4,04 A** (`40,3 °C` estimados) e elevando o teto do rotor
   para **420 g**.
4. **Fiação óptica simplificada:** adoção do **SPI Quad** (4 condutores por
   painel em vez de 6), eliminando o retorno de ponta dos painéis e reduzindo o
   tempo de atualização SPI para 1/3, já testado em software com `teste-fitas-c3`.
5. **Freio regenerativo ligado na parada (`Brake on stop = On`):** necessário
   para cruzar a crítica de translação (~263 RPM) rapidamente (~1,5 s estimados)
   sem bater nos batentes dezenas de vezes na desaceleração; exige grampo ou
   resistor de descarga no barramento do ESC para conter a sobretensão.

---

## 4. Fases e portões

### Fase 0 — CAD e aquisição · em curso

| Atividade | Saída |
|---|---|
| Pacote CAD v4.0 (`Hologram_Orbiter_v4/`) | gerador, 16 STLs, blend, relatórios (`69/69`), DXF R01 Ø11 |
| Medições finais do AX-2810Q e eletrônica real | `parameters.json` atualizado, pesagem de módulos e chicote 4 fios |
| Compras pendentes | ferragens M3/M4 (`16×M3×10`, `4×M3×40`, porca `M4 DIN 985`, arruela `DIN 9021 M4`), chapa alumínio 2 mm, óleo silicone `10 000 cSt` (se adotar), buck qualificado |

**Portão G0:** CAD aprovado (69/69), altura do corpo AX-2810Q confirmada com
paquímetro antes de imprimir a torre, cupons `C01` e `C02` conferidos com a fita
HD107S real.

### Fase 1 — Fabricação

| Atividade | Saída |
|---|---|
| Cupons `C01` e `C02` (ABS) | folga espiga/socket e ponte do canal LED verificadas |
| Lote dos 3 painéis (ABS, mesma mesa) | 3 painéis pesados e medidos |
| Peças estruturais em PETG | `01_aranha`, `03_tampa_baia`, `04_base_fixa`, `05_palco_torre`, `06_suporte_ima`, `08_hastes` (2 lotes), `09_buchas_trava`, `10_bandeja` (opcional) |
| Chapa do motor `R01` | réplica PLA provisória para baixa rotação; **alumínio 2 mm (Ø11)** para ensaios até 1800 RPM |

**Portão G1:** massa ≤ 45 g/painel · `Δm ≤ 0,084 g` · Datum D `104 ± 0,2 mm` ·
raio `100 ± 0,1 mm` · `Δh ≤ ±0,5 mm` · aranha ≤ 135 g · tampa ≤ 14 g.

### Fase 2 — Montagem mecânica e bancada de acionamento

| Atividade | Saída |
|---|---|
| Montagem do paralelogramo | palco sobre calços de 4 mm, 8 hastes presas (apertar topo por último), 4 abas grampeadas à mesa, laçada frouxa dos 3 fios do motor |
| Verificação do motor + ESC + firmware base | confirmar sentido **anti-horário visto de +Z**, calibrar pulso/RPM do AX-2810Q no tacômetro, validar trava `4 + 4` e reaperto após 24 h |
| Revisão do perfil de partida na `firmware/controle-motor` | rampa ≥ 300 RPM/s na travessia 200–400 RPM (`≥ 50 µs/s` acima de 1200 µs), alvo mínimo 1200 µs (fora de 760–870 RPM), limite de potência/RPM no Bloqueador D |
| Contenção integral e grampo no barramento do ESC | caixa fechada (policarbonato para rádio), descarga de barramento entre 12,6 e 16,8 V |

**Portão G2:** conjunto montado girando livre à mão (e travado/solto conforme o
ensaio), centro do eixo dentro de 0,5 mm do círculo das hastes, contenção
fechada, parada suave/emergência e grampo de barramento validados na bancada.

### Fase 3 — Bloqueadores de rotação (A, B, C, D — sem LEDs)

Detalhe completo em [`04-PLANO-DE-ENSAIOS-v4.0.md`](04-PLANO-DE-ENSAIOS-v4.0.md):
- **C0 (antes de girar):** ensaio de impacto com massa representativa — palco
  solto (`4,0–5,0 Hz` translação, `12–15 Hz` giro, `Q ≤ 35`) e modo combinado
  `≥ 95–100 Hz` (se `80–95 Hz`, limitar a 1600 RPM).
- **A (potência/arrasto):** `P_entrada ≤ 20 W` a 1800 RPM.
- **B (térmica/fluência):** motor `< 55 °C`, estrutura `< 60 °C`, crescimento da
  ponta do painel `< 0,5 mm` em 1 h.
- **C (vibração/balanceamento 2 planos):** `≤ 0,20 g` (1×), `≤ 0,10 g` (2×),
  redução ≥ 10× na mesa solto vs. travado, sem toque nos batentes acima de
  600 RPM e giro ≤ 0,3 mm entre 760–870 RPM.
- **D (partida):** 10/10 partidas, `P_pico ≤ 36,1 W` (ref. 8 A no AX-2810Q),
  `RPM ≤ 1800`, barramento ESC `≤ 16,8 V`, orelha não encosta no batente rígido (3 mm).

**Portão G3:** A, B, C e D aprovados sem LEDs (usando lastro representativo).

### Fase 4 — Integração óptica e eletrônica de bordo

| Atividade | Saída |
|---|---|
| Fitas nos painéis e chicotes 4 vias SPI Quad | continuidade, isolação e pesagem real |
| Placa perfboard ponto-a-ponto + ESP32-C3 + buck + A3144 + LiFe 2S | checagem a frio e teste de polaridade/entreferro do Hall |
| Firmware completo do rotor (SPI Quad DMA + interrupção Hall + ESP-NOW) | imagem de teste + troca sincronizada no pulso |
| Rebalanceamento completo + repetição de A–D (incluindo B na bateria `< 45 °C`) | rotor completo ≤ 420 g |

**Portão G4:** imagem de teste estável a 1800 RPM, rotor final balanceado e
validado.

### Fase 5 — Validação visual e demonstração

Ensaio do enlace de imagem (tremor `< 46 µs` + alcance na contenção de
policarbonato), Bloqueador E (jitter imperceptível em sacada, sem imagem
dupla/tripla) e página web na ESP32 da base.

**Portão G5:** imagem enviada pelo celular estável em operação contínua.

---

## 5. Riscos principais (atualizados para v4.0)

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| Travessia lenta da crítica de ~263 RPM (bate nos batentes) | média | alto | rampa `≥ 300 RPM/s` (`≥ 50 µs/s`), `Brake on stop = On` no ESC |
| Estacionar no modo de giro (~760–870 RPM) | média | médio | não usar alvo entre 760–870 RPM (`≥ 1200 µs`); óleo 10 000 cSt amortece (`ζ ≈ 0,05`) ou travar `4 + 4` |
| 3º harmônico cruzar modo combinado (~1786 RPM) | média | alto | medir no ensaio de impacto C0; se `< 95 Hz`, limitar rotação a 1600 RPM |
| Sobretensão no barramento com `Brake on stop = On` | alta | alto | **obrigatório** grampo ou resistor de descarga no barramento (`12,6–16,8 V`) |
| Folga nos parafusos da trava após 24 h (fluência do PETG) | alta | médio | reapertar os 4+4 parafusos da trava após 24 h |
| Fluência / transferência de carga nos painéis ABS | média | crítico | validar seção FDM e ensaio de 1 h a quente antes de liberar operação contínua |
| Dropout do buck mini560 na descarga da LiFe (5,8–6,6 V) | média | alto | validar `V_in_min ≤ 5,5 V` no componente real antes de fechar a baia |

---

## 6. Documentos vigentes

| Documento | Papel |
|---|---|
| [`README.md`](README.md) | ponto de entrada e estado do projeto |
| [`01-ESPECIFICACAO-CAD-v4.0.md`](01-ESPECIFICACAO-CAD-v4.0.md) | **manda em toda cota e memória de cálculo** |
| [`02-PLANO-DE-PROJETO-v4.0.md`](02-PLANO-DE-PROJETO-v4.0.md) | fases, portões e riscos |
| [`03-LISTA-DE-COMPONENTES-v4.0.md`](03-LISTA-DE-COMPONENTES-v4.0.md) | peças impressas, motor, eletrônica e ferragens |
| [`04-PLANO-DE-ENSAIOS-v4.0.md`](04-PLANO-DE-ENSAIOS-v4.0.md) | bloqueadores C0 e A–E, critérios e segurança |
| [`05-ESQUEMA-ELETRICO-v4.0.md`](05-ESQUEMA-ELETRICO-v4.0.md) | SPI Quad no rotor, acionamento fixo e enlace ESP-NOW |
| [`06-PENDENCIAS-ABERTAS-v4.0.md`](06-PENDENCIAS-ABERTAS-v4.0.md) | bloqueadores e medições em aberto |
| [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) | vocabulário e rastreabilidade (medido vs. assumido) |
| [`Hologram_Orbiter_v4/README.md`](Hologram_Orbiter_v4/README.md) | pacote CAD, builds, STLs e guias de montagem |
| [`legado/LEIA-ME.md`](legado/LEIA-ME.md) | arquivo morto: `v2.0`, `v2.1` e `v3.0` |
