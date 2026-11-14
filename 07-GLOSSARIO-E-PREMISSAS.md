# Glossário e premissas — Hologram Orbiter v4.0

O vocabulário vigente do projeto e o registro explícito de **o que foi medido,
o que foi derivado e o que ainda depende de ensaio** após a promoção da
arquitetura em paralelogramo + motor `AX-2810Q 750KV` para **v4.0** (14/11/2026).

---

## 1. Vocabulário

### Motor

**Campânula** *(bell)* — a parte **girante** externa do motor (`Ø35 mm` no
`AX-2810Q`). Dela sai o eixo e sobre ela monta-se o adaptador de hélice onde a
aranha assenta. **Não confundir com cilindro de proteção.**

**Base do motor** — a parte **fixa**, onde saem os três fios de fase (`Ø3,0 mm`
medidos no `AX-2810Q`). Parafusa na chapa de alumínio `R01` pelo padrão de
4 × M3 em cruz: diagonais **16 e 19 mm**, com furos em (±8, 0) e (0, ±9,5).

**Base serrilhada e bucha do eixo** — no adaptador de hélice do `AX-2810Q`, o
cubo assenta sobre uma **base serrilhada `Ø13 mm`** (como uma hélice), e não
diretamente nos raios da campânula como no antigo A2212. Acima dela há um trecho
liso `Ø4 × 5 mm`, onde entra a **bucha `Ø6 mm`** que centra o cubo (`furo Ø6`),
seguida de rosca **M4 × 10 mm**.

**kv** — rotação por volt sem carga. `750 kv` dá 7500 RPM a vazio a 10 V e
9000 RPM a 12 V; a 1800 RPM o motor opera a **20–24 %** da rotação a vazio (mais
torque específico que o antigo 920 kv).

**Kt** — constante de torque, `9,5493 / kv` = **12,73 mN·m/A** no `AX-2810Q`.

**ESC** — controlador do motor sem escovas (*LittleBee Spring 20A*, `BLHeli_S`
16.7). Recebe **sinal servo** (PWM de 1–2 ms a 50 Hz), não tensão analógica.

**LVC** — corte por baixa tensão. **Não existe** no firmware `BLHeli_S`.

**Governor** — controle em malha fechada de rotação. **Não existe** no
`BLHeli_S`.

### Rotor e base suspensa

**Aranha** — a peça central girante em **PETG**: cubo `Ø92`, baia **`Ø80/84 × 47 mm`**
com **prateleira em `Z = 28 mm`** e três braços radiais reforçados (aleta
vertical em **D** + alma inferior em **perfil de asa invertido** até `r = 74 mm`).

**Longarina** — cada um dos três braços da aranha (`15 × 6 mm` no núcleo,
reforçados da raiz até o ombro).

**Espiga** *(tenon)* — a ponta retangular da longarina, `11 × 6 × 22 mm`, que
entra no painel. Na v4.0 passa a ser o limite de seção resistente (`r = 77 mm`,
9,7 MPa a 10° de inclinação).

**Socket** — o encaixe correspondente dentro do painel, `11,2 × 6,2 × 22,5 mm`.
Folga de 0,1 mm por lado e 0,5 mm de fundo para a carga radial ir aos
parafusos M3.

**Boss** — a saliência do painel que envolve o socket e as torres dos parafusos.

**Carenagem** — a casca em gota (`0,8 mm`) que envolve o boss para reduzir o
arrasto aerodinâmico.

**Baia de eletrônica** — compartimento cilíndrico no cubo (**`Ø80` interno /
`Ø84` externo × `47 mm` de altura**). Abriga bateria LiFe, ESP32-C3, buck,
capacitor de saída e placa de interface no piso/pilares (`Z = 0..27 mm`), além
de reservar uma **prateleira em `Z = 28 mm`** para a futura placa própria
(`Z = 28..44 mm`).

**Palco suspenso** — conjunto móvel em **PETG** (`05_palco_torre_PETG.stl`):
disco inferior, 8 aletas radiais, aro externo e torre maciça `Ø40` que sustenta
o motor e o rotor (`~0,95 kg` móveis no total).

**Hastes flexíveis** — 8 barras verticais em **PETG** de seção quadrada
**`1,5 × 1,5 mm`** (`55 mm` livres, `08_hastes_flexiveis_macia_1p5_8x.stl`) que
penduram o palco ao anel superior da base fixa. Dobram em **S** para transladar
horizontalmente sem inclinar (`4,38 Hz`, rotação crítica **~263 RPM**),
isolando de 24× a 40× a força transmitida à bancada a 1800 RPM.

**Trava 4 + 4** — mecanismo reversível que converte a base suspensa em modo
rígido usando as mesmas peças impressas: 4 parafusos radiais `M3 × 40` em
buchas `09_buchas_trava_4x.stl` + 4 parafusos verticais `M3 × 10` no teto dos
batentes.

**Amortecedor viscoso** — bandeja única opcional (`10_bandeja_amortecedor.stl`)
sob o palco com 4 cubas em setor de anel onde mergulham 4 pás em L do palco.
Com **óleo de silicone `10 000 cSt`** (`~4,14 mL/cuba` até a cota nominal, ou
`~2 mL` mínimo) amortece translação (`ζ ≈ 0,12`) e giro (`ζ ≈ 0,049`) sem
adicionar rigidez; seco, não atua.

**Coxim** — isolador elastomérico heredado da v2.1. **Não existe no projeto:**
foi descartado na v3.0 (frequência natural de 400–620 Hz); na v4.0 o isolamento
é feito exclusivamente pela suspensão em paralelogramo na base.

**Contrapeso** — massa de correção do balanceamento em dois planos: alívios da
face inferior do cubo (`r = 17..36 mm`, plano 1) e os 6 copos no topo da tampa
(`r = 34 mm`, plano 2). Os valores nominais são recalculados a cada build em
`reports/geometry_report.json` e devem ser ajustados após a pesagem real.

**Canal do LED** — rebaixo de `12,4 × 2,0 mm` na face externa do painel onde a
fita HD107S cola com os LEDs rentes à face, deixando piso em ponte de `0,8 mm`
sobre parede local engrossada para `2,8 mm`.

### Geometria e fabricação

**Datum** — face ou eixo de referência. **`Datum B = 186 mm`** é o topo do cubo
a partir do piso da base fixa (`palco 12 + torre 137 + chapa 2 + motor_stack 35`);
**`Datum D = 104 mm`** é a meia-altura do painel a partir da base do painel.

**Plano médio do painel** — cilindro em **`r = 100 mm`** onde a lâmina é centrada.

**Cupom** — corpo de prova pequeno (`C01_cupom_junta.stl`,
`C02_cupom_canal_LED.stl`) impresso antes do lote para validar folga da junta e
ponte do canal do LED.

**Ponte** *(bridging)* — trecho extrudado no vazio entre dois apoios (ex.: piso
de `0,8 mm` sob o canal de `12,4 mm` no painel).

**Enrolamento** *(winding number)* — quantas vezes a superfície envolve um ponto.
**+1** é sólido normal; **−1** é casca invertida. Todos os STLs publicados pelo
pipeline passam em sondagem por raios (`CAD/probe.py`) e validação independente
(`scripts/validate_stl.py`).

**Watertight / não-manifold** — malha fechada com exatamente duas faces por aresta.

### Dinâmica

**POV** — *persistence of vision*. Três painéis a 30 rps varrem cada ponto do
espaço 90 vezes por segundo.

**Índice / referência de fase** — pulso 1× por volta gerado pelo sensor Hall
`A3144` nu ao cruzar o ímã fixo (`r = 29 mm`, azimute `20°`).

**Δm** — diferença de massa entre os três painéis montados. Limite atual: **`0,084 g`**.

**U** — desbalanceamento estático, em `g·mm` (massa × raio). Referência
nominal de G6.3 a 1800 RPM: **`8,4 g·mm`** (recalcular com a massa real medida
do rotor até o teto provisório de `420 g`).

**G6.3** — grau de qualidade de balanceamento (ISO 1940).

**A·Cd** — área frontal vezes coeficiente de arrasto. Critério do boss carenado:
`≤ 350 mm²`.

**Fluência** *(creep)* — deformação lenta sob carga constante em plásticos FDM
(painel sob 158 N centrífugos, hastes e apoios da aranha sob pré-carga/carga).

**Fadiga** — dano por carga cíclica (partidas, paradas e cruzamento da crítica
de `~263 RPM` ou vibração de giro).

**Bloqueador** — critério objetivo (`C0` e `A`–`E` do plano 04) com método de
medição e contingência antes de avançar de fase.

### Elétrica

**SPI Quad** — topologia adotada para os dados dos painéis: 1 linha `CLK` comum
(com 3 resistores série de `33 Ω`) + 3 linhas `DATA` independentes, saindo do
buffer `74AHCT125`. Reduz o chicote de 6 para **4 condutores por painel** (`+5 V`,
`GND`, `CLK`, `DATA`, sem retorno) e elimina o atraso serial entre painéis.

**Buck** — conversor abaixador (`mini560`, 6,6 V nominal da bateria LiFePO4 para
5,0 V das fitas e lógica).

**LiFePO4** *(LiFe)* — 2S 800 mAh (`6,6 V` nominal, `7,2 V` cheia, corte `5,8 V`).
**Carregar sempre em modo LiFe a `3,6 V/célula`** — modo LiPo (4,2 V) destrói o pack.

**Porca autotravante DIN 985 M4 e arruela DIN 9021 M4** — fixação do cubo no
eixo do `AX-2810Q` (`1,0 N·m`). A arruela larga de aço (`12 × 4,3 × 1,0 mm`)
distribui a carga no PETG acima do furo `Ø6`. **Nos painéis** (junta `2 × M3 × 40`),
o bolso de `2,8 mm` continua usando porca plana M3 com trava química (Nyloc não
cabe ali).

**Coletor aberto** *(open collector)* — saída do `A3144` que só puxa ao GND,
permitindo alimentar o sensor em 5 V e entregar sinal seguro de `3,3 V` ao
ESP32-C3 via pull-up `10 kΩ → 3V3`.

**V_IH** — tensão mínima de nível alto (`≥ 3,5 V` na HD107S em 5 V), atendida pelo
`74AHCT125`.

**ESP-NOW** — enlace sem fio (pacotes até 250 bytes) entre a ESP32 da base e o
ESP32-C3 do rotor (somente dados de imagem, nunca comando de motor).

**Portal cativo** — página servida pela ESP32 da base via Wi-Fi AP para desenho.

**Tremor** *(jitter)* — variação no instante de atualização de coluna (`≤ 46 µs`,
1/4 de coluna a 1800 RPM).

---

## 2. Medido, derivado ou assumido

Nenhum número deste projeto deve ser usado sem saber de qual coluna ele veio.

| Grandeza | Valor | Origem | Estado |
|---|---|---|---|
| Motor, kv e massa | `AX-2810Q`, `750 kv`, `72 g` (catálogo) | HobbyKing datasheet | ⚠️ **kv/massa de catálogo; pesagem e tacômetro pendentes** |
| Kt | `12,73 mN·m/A` | `9,5493 / kv` | ✅ derivado do kv de catálogo |
| Resistência efetiva por fase | **`0,225 Ω`** (`~0,20–0,25 Ω/fase`) | medida linha-linha em `13/11/2026` (`5,3–5,4 Ω` menos `4,9 Ω` das pontas = `0,4–0,5 Ω`) | ⚠️ **±25 % pela resolução de 0,1 Ω do multímetro** |
| Furação da base do motor | cruz, diagonais `16` e `19 mm`, `4 × M3` | **medido** por Pedro em `13/11/2026` | ✅ medido |
| Fios de fase do motor | `3 fios Ø3,0 mm` | **medido** por Pedro em `13/11/2026` | ✅ medido |
| Campânula | `Ø35 mm` | **medido** por Pedro em `13/11/2026` | ✅ medido |
| Corpo do motor | `26 mm` (catálogo B) | HobbyKing datasheet | ❌ **medir altura real do corpo (e divisão campânula/serrilhado)** |
| **Chapa → assento do cubo** | **`29 mm`** (topo da base serrilhada `Ø13`) | **medido** por Pedro em `13/11/2026` | ✅ cota total medida; divisão `26 + 3` assumida |
| Eixo e adaptador de hélice | base serrilhada `Ø13`, trecho liso `Ø4 × 5` (c/ bucha `Ø6`), rosca `M4 × 10` | **medido** por Pedro em `13/11/2026` | ✅ medido (cubo assenta no `Ø13`) |
| **Chapa → Datum B** | **`35 mm`** (`29` assento + `6` cubo) | derivado | ✅ `Datum B = 186 mm` (`12 palco + 137 torre + 2 R01 + 35`) |
| Chapa R01 e arruela do eixo | chapa alumínio `60×60×2 mm` alívio **`Ø11`**, arruela aço `DIN 9021 M4` (`12×4,3×1,0`) + porca `DIN 985 M4` (5 mm) | projeto v4 (`R01P_*_PLA` provisórias até cortar alumínio e comprar DIN 9021/985) | ⚠️ conferir espessura real e folga até M3 em `r = 8` |
| Fita HD107S | `12,0 × 2,0 mm`, 144 LED/m | **medido** (`02/09/2026`) | ✅ |
| ESP32-C3 Super Mini | `~22,5 × 18 × 5 mm` | em mãos | ✅ |
| ESC LittleBee Spring | `20 A` contínuo / `25 A` pico, `BLHeli_S 16.7` | datasheet + leitura `4-way` (`13/11/2026`) | ✅ |
| ESC: configuração gravada | **Startup Power `0,50`**, **Demag `High`**, **Brake on stop `On`**, Normal, PPM `1148–1832 µs` | gravado e verificado por releitura em `13/11/2026` | ✅ gravado (`SHA-256 4f456a62…a119`) |
| ESC: governor / LVC / rampa | **não existem** em `BLHeli_S` | manual Rev16.x | ✅ |
| Fonte de bancada | `10–12 V`, limite `30 A` | em mãos (`20/10/2026`) | ✅ |
| Bateria LiFePO4 800 mAh | `58 × 30 × 17 mm`, `50 g`, `6,6 V` nominal, 2S, 20C | comprada e medida (`02/09/2026`) | ✅ |
| **Rth do motor** | **`3,5 °C/W`** | assumido (catálogo) | ❌ **termopar decide (Bloqueador B)** |
| **Cd da lâmina / A·Cd do boss** | `0,35` / `≤ 350 mm²` | estimativa geométrica/tabela | ❌ **ensaio decide (Bloqueador A)** |
| Módulo e resistência PETG / ABS FDM | ABS `2,0–2,3 GPa` / PETG `1,9 GPa` (`1,27 g/cm³`) | catálogo genérico | ❌ **cupom, impacto `C0` e ensaio decidem** |
| Massas CAD (sólido maciço) | aranha `116,53 g`, painel nu `31,94 g`, tampa `12,94 g`, palco+torre `494,4 g`, base fixa `425,75 g`, haste `1,33 g` | `geometry_report.json` | ⚠️ pesar peças impressas reais |
| Subtotal do rotor vs teto v4 | **`352,14 g`** nominais contra teto provisório **`420 g`** | CAD + `40 g` eletrônica + bateria + Hall + contrapeso | ❌ **reconciliar chicotes 4 fios, placa e pesar** |
| Suspensão em paralelogramo | translação `4,38 Hz` (`263 RPM`), yaw `12,66 Hz` (`759 RPM`), balanço combinado `89,3 Hz`, `0,952 kg` móveis | `FISICA.json` (`E = 1900 MPa`, sem óleo/cabos) | ❌ **ensaio de impacto `C0` e travamento decidem** |
| Sensor de índice | `A3144` **nu**, TO-92, `0,2 g` | dessoldado do `HW-477` | ✅ (polaridade/entreferro em bancada pendentes) |
| Placa de interface SPI Quad | montada em perfboard ponto a ponto (`MONTAGEM-PONTO-A-PONTO.md`); `r0.2` em KiCad não fabricada | `eletronica/interface/` + `firmware/teste-fitas-c3/` | ⚠️ **pesar, medir e validar 3 fitas + Hall + ADC** |

**Os itens térmicos e estruturais com ❌ continuam mandando nos bloqueadores.**
Mesmo com o `AX-2810Q` reduzindo a corrente prevista de regime para `4,04 A`
(`40,3 °C` a `Rth = 3,5 K/W`), o arrasto adicional da aleta/alma da aranha e o
`Rth` real só são conhecidos no **Bloqueador B**, e a rigidez real da suspensão
em PETG só é conhecida no **ensaio `C0`**.

---

## 3. Pontos críticos de componentes e acionamento

### Por que o sensor A3144 vai nu, e não na placa HW-477
1. **Elétrico:** o pull-up do módulo `HW-477` vai para o próprio `VCC` (5 V), o que
   destruiria o `GPIO3` (3,3 V) do `ESP32-C3`. O `A3144` nu é alimentado em 5 V
   com pull-up de `10 kΩ` ligado exclusivamente à linha `3V3`.
2. **Balanceamento e bolso CAD:** o módulo pesa `1,5–2,5 g` (`43–72 g·mm` em
   `r = 29`); o `A3144` nu pesa `0,2 g` (`5,8 g·mm`) e encaixa no bolso inferior
   do cubo (`4,8 × 3,6 × 1,7 mm`). Confirmar polaridade e entreferro (`2,5 mm`)
   em bancada antes de colar.

### ESC `BLHeli_S`, suspensão em paralelogramo e frenagem regenerativa
Na v4.0, a gravação de `13/11/2026` no ESC manteve **`LPow Protect = Off`**,
**`Startup Power = 0,50`**, **`Demag = High`** e ligou **`Brake on stop = On`**:
- **Por que `Brake on stop = On`:** o rotor precisa atravessar rapidamente a
  ressonância de translação da suspensão (**`~263 RPM`**) também na **desaceleração**,
  evitando excitar o curso de `3 mm` até os batentes durante parada longa por inércia.
- **Consequência obrigatória na fonte:** a frenagem regenerativa (*damped light*
  + freio ativo na parada) devolve energia para a fonte de bancada (que não
  afunda corrente) e eleva a tensão do barramento. **Grampo ou resistor de
  descarga no barramento do ESC é obrigatório** antes de girar o rotor completo.
- **Solicitações ao firmware da base:** sem *governor* nem tempo de rampa no
  ESC, a rampa de subida (`≥ 300 RPM/s` na zona crítica), a faixa de operação
  (`≥ 1200 µs` mínimo e evitar regime contínuo em `760–870 RPM` pelo modo de
  *yaw* a `12,7 Hz`), e a calibração de `CEILING_US` com tacômetro para o
  `AX-2810Q` dependem do firmware em [`firmware/`](firmware/README.md).

---

## 4. Verificações físicas pendentes

| Interface | Verificação |
|---|---|
| Altura real do corpo do `AX-2810Q` | O assento serrilhado foi medido em `29 mm` da base do motor, mas a altura do corpo (`26 mm` de catálogo) ainda não foi medida. Se o corpo for mais baixo ou mais alto, a distância relativa da campânula ao suporte `06` muda — **conferir o entreferro do Hall (~2,5 mm) montado antes de colar o ímã**. |
| Bucha `Ø6` no cubo e assento `Ø13` | Conferir o ajuste da bucha de `6 mm` sobre o trecho liso `Ø4 × 5` no furo `Ø6` do cubo, mais arruela `DIN 9021 M4` (`Ø12`) e porca `DIN 985 M4` a `1,0 N·m`. |
| Alívio `Ø11` na `R01` de alumínio | Conferir folga dos fios de fase e das cabeças `M3` (`r = 8` e `9,5 mm`) após cortar a `R01` definitiva em alumínio `2 mm`. |
| Polaridade do ímã e campo do motor | Validar em bancada o `A3144` com `VCC = 5 V`, pull-up `10 kΩ → 3,3 V` e verificar se o campo estático do `AX-2810Q` interfere no sensor antes de colar. |
| Ensaio de impacto `C0` da suspensão | Medir frequências reais do palco suspenso (translação `< 5 Hz`, *yaw*, balanço combinado `> 66 Hz` — se `< 95 Hz`, limitar 3× abaixo de `1643 RPM`) e repetir com o rotor real (travado e solto). |
| Reconciliação de massa e balanceamento | Pesar todas as peças impressas (PETG + ABS), chicotes de 4 fios, perfboard e ferragens contra o teto provisório de **`420 g`** e ajustar contrapesos nos dois planos. |

---

## 5. Onde cada número mora

| Se você precisa de… | Vá para |
|---|---|
| Uma cota ou memória de cálculo | [`01-ESPECIFICACAO-CAD-v4.0.md`](01-ESPECIFICACAO-CAD-v4.0.md) |
| Fases e portões `G0`–`G5` | [`02-PLANO-DE-PROJETO-v4.0.md`](02-PLANO-DE-PROJETO-v4.0.md) |
| Lista de peças, ferragens e massas | [`03-LISTA-DE-COMPONENTES-v4.0.md`](03-LISTA-DE-COMPONENTES-v4.0.md) |
| Um critério físico de aceite (`C0`, `A`–`E`) | [`04-PLANO-DE-ENSAIOS-v4.0.md`](04-PLANO-DE-ENSAIOS-v4.0.md) |
| Eletrônica **SPI Quad**, ESC e firmware | [`05-ESQUEMA-ELETRICO-v4.0.md`](05-ESQUEMA-ELETRICO-v4.0.md) |
| O que o CAD mede na malha (`69/69`) | [`Hologram_Orbiter_v4/reports/ACEITACAO.md`](Hologram_Orbiter_v4/reports/ACEITACAO.md) |
| O que ainda falta | [`06-PENDENCIAS-ABERTAS-v4.0.md`](06-PENDENCIAS-ABERTAS-v4.0.md) |
| Documentação arquivada (`v3.0`, `v2.1`) | [`legado/LEIA-ME.md`](legado/LEIA-ME.md) |

**Regra:** se um número aparecer em dois documentos com valores diferentes, o da
especificação v4.0 (e de `Hologram_Orbiter_v4/CAD/parameters.json`) prevalece,
e o outro é um erro a corrigir.
