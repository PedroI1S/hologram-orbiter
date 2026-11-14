# Fiação, sensor de índice e montagem — Hologram Orbiter v4.0

Complementa a [`01-ESPECIFICACAO-CAD-v4.0.md`](../../01-ESPECIFICACAO-CAD-v4.0.md)
e o [`05-ESQUEMA-ELETRICO-v4.0.md`](../../05-ESQUEMA-ELETRICO-v4.0.md) com as
rotas físicas e a sequência de montagem do pacote **v4.0**. Cotas em mm.

---

## 1. Rota dos quatro condutores por painel (SPI Quad)

Com a arquitetura **SPI Quad**, cada painel recebe **quatro condutores** a
partir do cubo: **`+5 V`** e **`GND`** em **AWG 24** (estrela de potência do
buck) e **`CLK`** + **`DATA`** dedicado em **AWG 28** (saídas da placa de
interface). **Não há fios de retorno** na ponta superior das fitas. A espiga
**não é furada**: ela carrega os ~158 N centrífugos.

| Trecho | Peça | Feature no CAD | Cota |
|---|---|---|---:|
| 1. Saída da baia `Ø80/84` | aranha (`01`) | janela na parede da baia (`r = 40..42`), lado de fuga do braço | `r 38–43 · y −10…−5,5 · Z 0,8–5,8` |
| 2. Topo da raiz | aranha (`01`) | bolso largo na face superior do alargamento da raiz | `r 42,3–48 · y −10…0 · piso Z 2,3` |
| 3. Braço | aranha (`01`) | sulco no lado de fuga (`y < 0`, livre da aleta em D em `y ≥ 0,6`) | `r 48–70 · y −4,4…0 · piso Z 2,3` |
| 4. Ombro | — | os fios sobem 3 mm em ar livre nos 4 mm finais e passam sobre a luva (`Z = 5,1`) | `r 70–74` |
| 5. Entrada na carenagem | painel (`02`) | janela no flanco plano da carenagem, acima da luva | `y −7,4…−2,6 · z 5,4–10` (painel) |
| 6. Câmara traseira | painel (`02`) | espaço livre atrás das torres, entre a alma central (`y = 0`) e a cauda | `y < −1,2` |
| 7. Entrada na cavidade | painel (`02`) | furo na parede interna da lâmina, ao lado da torre externa | `y −6,2…−2,6 · z 6–9,5` |
| 8. Descida | painel (`02`) | cavidade oca; cada diafragma tem vão de 4 mm (`y −1,5…2,5`) | `z +6 → −98,5` |
| 9. Saída para a fita | painel (`02`) | bolso passante `8 × 3,5 mm` abaixo do batente da fita | `z −102…−98,3` |

Fixação dos fios no sulco do braço: adesivo (CA/epóxi) ou fita Kapton. A força
centrífuga puxa o feixe ao longo do sulco.

**Montagem da fita:** inserir pelo topo do canal (`12,4 × 2,0 mm`), colar o PCB
no fundo com os LEDs rentes à face externa, soldar os **4 pads inferiores**
(`+5 V`, `GND`, `CLK`, `DATA`), dobrar com alívio de tensão e encaixar no bolso
em `Z = −98,5`. Isolar a ponta superior da fita (sem retorno). Pesar os três
chicotes e os três painéis montados (`Δm ≤ 0,084 g`).

---

## 2. Sensor de índice angular (`A3144` nu)

| Item | Onde | Cota |
|---|---|---|
| Sensor Hall `A3144` **nu** (TO-92 dessoldado do `HW-477`) | face inferior do cubo, face marcada para baixo | `r = 29`, azimute **`20°`** do rotor (braço 1 = `0°`) |
| Terminais | rasgo `4,8 × 1,4 mm` subindo até a baia, sob a placa de interface | `r ≈ 27,3–28,7`, azimute `20°` |
| Ímã `Ø4 × 2` (`N35`) | topo do poste do `06_suporte_ima_PETG` (`h = 26,5 mm`) | `r = 29`, azimute **`20°`** da base (`+x = 0°`) |
| Entreferro nominal | entre `Z_poste` e face inferior do cubo (`Z = 180` global) | **`2,5 mm`** (confirmar com altura real do `AX-2810Q`) |
| Suporte `06` | arco afastado (`r_int = 19,6 mm`, folga `2,1 mm` à campânula `Ø35`) sob **dois M4×20** (`0°` e `90°`), centrado em `45°` | aba `2,5 mm`, poste `26,5 mm` sobre a chapa |

Alimentar o `A3144` com `5 V` e ligar o pull-up de `10 kΩ` **exclusivamente a
`3V3`** na placa de interface. Validar polaridade do ímã e ausência de disparo
espúrio pelo campo do `AX-2810Q` em bancada **antes de colar**.

---

## 3. Fixação do rotor no eixo do `AX-2810Q`

O `AX-2810Q 750KV` (medido em `13/11/2026`) usa **adaptador de hélice**:
- base serrilhada **`Ø13`** a **`29 mm`** acima da chapa `R01` (cubo assenta
  diretamente nela);
- trecho liso **`Ø4 × 5 mm`** onde entra a **bucha de `Ø6 mm`** que acompanha o
  motor (furo do cubo em **`Ø6,00 mm`**);
- rosca **`M4 × 10 mm`** acima do trecho liso.

Sequência da pilha sobre o cubo (sem rebaixo):
1. Cubo em PETG (`6,0 mm`) com a **bucha `Ø6`** inserida até assentar na base
   serrilhada `Ø13`. Se o furo fechar na impressão, alargar com broca de `6,0 mm`
   (nunca folgar além da bucha).
2. **Arruela larga de aço `DIN 9021 M4` (`Ø12 × Ø4,3 × 1,0 mm`)** direto no topo
   do cubo *(provisoriamente `R01P_arruela_eixo_M4_PLA_provisoria.stl` apenas em
   bancada de baixa rotação até adquirir a `DIN 9021`)*.
3. **Porca autotravante `M4 DIN 985`** (`5 mm` de altura, anel de nylon) apertada
   a **`1,0 N·m`** (sobram **`3 mm`** de rosca acima da porca; ponta do eixo
   em `Z = +9 mm` acima do cubo, `1 mm` abaixo dos trilhos da bateria em `Z = 10`).

---

## 4. Passagem dos fios do motor (`Ø3,0 mm`) e montagem da base suspensa

1. **Chapa `R01` + motor:** prender o `AX-2810Q` à chapa `R01` (alumínio `2 mm`
   com alívio central **`Ø11`**, ou réplica `R01P` PLA provisória só para testes
   sem carga/baixa rotação) pelos `4 × M3` em cruz (`16/19 mm`), orientando os
   **3 fios de fase `Ø3,0 mm`** para o azimute **`157,5°`** (entre as aletas de
   `135°` e `180°`).
2. **Suporte do ímã + flange:** parafusar a chapa `R01` e o suporte `06` nos
   `4 × M4` da flange (`0°` e `90°` levam `M4 × 20` sob a aba de `2,5 mm`; `180°`
   e `270°` levam `M4 × 16`).
3. **Roteamento dos fios do motor na torre (`05`):**
   - Abaixo de `Z = 80 mm`, os fios descem no vão de `45°` entre as aletas de
     `135°` e `180°`.
   - De `Z = 82` a `113 mm`, encaixar os três fios nos **ganchos alternados**
     (`cable_hooks` em `157,5°`), estalando o farpão de PETG sem esmagar a capa.
   - Na saída pelo entalhe da pista da base fixa (`168,75°`, largura `14 × 10 mm`),
     deixar uma **laçada frouxa** entre o palco e a casca para não adicionar
     rigidez paralela às hastes flexíveis.
4. **Montagem do paralelogramo:**
   - Prender as **8 hastes `1,5 × 1,5 mm` (`08`)** primeiro nos assentos do
     palco (`05`) e depois no anel superior da base fixa (`04`) usando
     `16 × M3 × 10` e porcas M3 (acesso pelas janelas superiores e furos `Ø7` na
     pista inferior). Todas as hastes devem entrar sem torção ou pré-flambagem
     antes do aperto final.
   - Se usar **modo travado** (ou para ensaio comparativo rígido): encaixar as
     4 buchas `09_buchas_trava_4x.stl` com `4 × M3 × 40` + porcas pela pista
     lateral e apertar os `4 × M3 × 10` verticais no teto dos batentes pelos
     furos `Ø7` superiores. **Reapertar após 24 h** devido à fluência do PETG.
   - **Bandeja amortecedora (`10`):** se utilizar óleo de silicone `10 000 cSt`
     (`~2–4 mL/cuba`), encaixar as linguetas nos rasgos inferiores dos batentes
     antes de prender os últimos parafusos ou posicionando sob a base fixa.
   - **Calços de EVA (opcional):** `14 × 6 × 6 mm` no fundo dos 4 bolsos dos
     batentes, mantendo folga nominal de `1,5 mm` (nunca em contato permanente
     em repouso).

---

## 5. Sequência de montagem do rotor (SPI Quad)

1. Confirmar Hall `A3144` nu em bancada (`VCC = 5 V`, pull-up `10 kΩ → 3V3`),
   instalar no bolso inferior (`r = 29, 20°`) e passar os terminais pelo rasgo.
2. Preparar e pesar os três painéis e os três chicotes **SPI Quad** de **4 vias**.
   Passar pelos canais dos braços sem furar a espiga e fixar com `2 × M3 × 40`
   e porcas planas com trava química nos bolsos de `2,8 mm`.
3. Montar a eletrônica na baia **`Ø80/84 × 47 mm`** segundo `spider.bay_layout`:
   - **Perfboard de interface** ([`MONTAGEM-PONTO-A-PONTO.md`](../../eletronica/interface/MONTAGEM-PONTO-A-PONTO.md))
     sobre os pilares em `(27; 5)`, `Z = 6 mm`.
   - **ESP32-C3 Super Mini** em `(-27; 0)`, `Z = 6 mm` (USB-C para `-y`).
   - **Buck `mini560`** em pé na ranhura da parede a `140°` (indutor para dentro).
   - **Capacitor `1000 µF / 10 V`** em `(22,5; -22)` na cerca da base.
   - *Futuro:* a **prateleira `Z = 28 mm`** (4 mísulas em `50°, 110°, 230°, 290°`,
     parafusos M2 em `r = 36,5`) reserva `Z = 28..44 mm` acima da bateria para uma
     placa própria.
4. Executar pré-balanceamento estático nos alívios inferiores (`r = 17..36 mm`,
   valores nominais em `reports/geometry_report.json` ajustados após pesagem).
5. Instalar o cubo no eixo do `AX-2810Q` com a bucha `Ø6`, arruela `DIN 9021 M4`
   e porca `DIN 985 M4` (`1,0 N·m`) **antes** de colocar a bateria. Conferir
   entreferro real do Hall e giro livre sem atrito.
6. Instalar a bateria LiFePO4 2S no berço (`Z = 10..27 mm`, folga de `1 mm` sobre
   a ponta do eixo), conectar proteção/chave e fechar a tampa `03_tampa_baia_PETG.stl`
   (`Ø84 × 5 mm`) nos postes `y = ±36 mm` (`2 × M3`).
7. Pesar o conjunto completo, reconciliar contra o teto de **`420 g`** e fazer o
   balanceamento fino nos 6 copos da tampa antes de qualquer giro fora da
   bancada estática.
