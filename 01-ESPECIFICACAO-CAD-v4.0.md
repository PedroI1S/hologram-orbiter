# Especificação CAD — Hologram Orbiter v4.0

**Documento de construção provisório. As cotas permitem reproduzir o CAD; a
resistência do painel e da aranha, as propriedades em PETG/ABS FDM, a fluência e
a resposta dinâmica da suspensão ainda dependem de validação em bancada (§10.0).
Não liberar a impressão definitiva dos painéis nem a operação com base apenas
na aprovação geométrica (69/69 critérios).**

Toda cota aqui é absoluta e tem origem nomeada em [`Hologram_Orbiter_v4/CAD/parameters.json`](Hologram_Orbiter_v4/CAD/parameters.json).

---

## 1. O que é a máquina

Um display volumétrico por persistência de visão. Três painéis verticais, cada
um com uma fita de LEDs endereçáveis apontando para fora, giram em torno de um
eixo vertical sobre uma **base suspensa em paralelogramo travável**. A 30
rotações por segundo, cada ponto do espaço é varrido por um painel três vezes
por volta: o olho integra e vê uma imagem cilíndrica suspensa.

```
                   ┌─ invólucro (fora de escopo)
        ▐  ╭───────┴──────────────╮  ▌
        ▐  │   painel  ●          │  ▌      3 painéis a 120° em ABS
        ▐  │      ╲   ╱           │  ▌      girando a 1800 RPM (r = 100 mm)
        ▐  │       ╲ ╱            │  ▌      imagem: Ø208 × 201 mm · 90 Hz
        ▐  │    ────●────         │  ▌
        ▐  │       ╱ ╲            │  ▌      Aranha PETG reforçada + baia Ø80/84×47
        ▐  │      ╱   ╲           │  ▌      Motor AX-2810Q 750KV + chapa R01 (Ø11)
        ▐  ╰───────┬──────────────╯  ▌
              torre Ø40 maciça + 8 aletas   Palco suspenso (Z 4..149 mm)
            ┌──┴───┴───┴──┐                 8 hastes PETG 1,5 mm + trava (4+4)
            │ base fixa   │                 + bandeja opcional p/ óleo 10 000 cSt
        ════╧═════════════╧═════════        Ø280 mm com 4 abas de grampo
```

O rotor carrega a própria energia e eletrônica: bateria LiFePO4 2S, ESP32-C3,
regulador buck, placa de interface **SPI Quad** (ou placa própria futura na
prateleira em `Z = 28 mm`) e as três fitas viajam com ele. A parte fixa tem o
palco suspenso, a base fixa, o motor, o ESC, a fonte, o módulo ESP32 da base e o
ímã de índice angular; o sensor Hall A3144 nu acompanha o rotor. Nada de anel
coletor.

**A grandeza que governa tudo é a taxa de imagem**: 3 painéis × 30 rps = 90 Hz.
A v4.0 substitui a base rígida e o motor A2212 da v3.0 (arquivados em
[`legado/v3.0/`](legado/v3.0/)) pela arquitetura da variante `3.1-P.2`:

- **Base suspensa em paralelogramo travável (PETG):** palco pendurado em 8
  hastes verticais de `1,5 × 1,5 mm` (`4,38 Hz` em translação, crítica ~263 RPM)
  para reduzir de 24× a 40× a força transmitida à bancada, com trava reversível
  4 + 4 para operar também em modo rígido e bandeja provisória para amortecimento
  viscoso em óleo de silicone (`10 000 cSt`).
- **Aranha reforçada (PETG):** aleta vertical em D + alma em perfil de asa
  invertido da raiz até o ombro (`r = 74 mm`), baia ampliada para **Ø80/84 × 47 mm**
  com prateleira em `Z = 28 mm`.
- **Motor AX-2810Q 750KV:** mais torque por ampère (`Kt = 12,73 mN·m/A`),
  teto provisório de massa do rotor elevado para **420 g**, assentamento pela
  base serrilhada `Ø13` com bucha `Ø6` e porca autotravante `M4 DIN 985`.

---

## 2. Ponto de operação — congelado

| Grandeza | Valor |
|---|---:|
| Raio do plano médio do painel | **100 mm** |
| Rotação nominal | **1800 RPM** = 188,50 rad/s = 30 rps |
| Taxa de imagem | **90 Hz** |
| Cilindro de imagem | **Ø208 × 201 mm** |
| Resolução | 29 px vertical × 180 colunas |
| Torque de arrasto de projeto (`Cd_boss = 0,35`) | **51,4 mN·m** (mesmo perfil de arrasto da v3.0) |
| Corrente de fase prevista (`AX-2810Q 750KV`) | **4,04 A** (melhor caso `Cd_boss = 0,20`: **3,62 A**) |
| Potência elétrica prevista na fonte (`η_ESC = 95%`) | **14,81 W** (**1,48 A a 10 V** · **1,23 A a 12 V**) |
| Temperatura do motor prevista (`R_ef = 0,225 Ω`, `Rth = 3,5 K/W`) | **40,3 °C** (melhor caso **37,8 °C**) |

Os seis primeiros parâmetros não são negociáveis pela modelagem. O recálculo de
corrente e temperatura usa o ponto médio da resistência medida entre pares de
fase em 13/11/2026 (`~0,20–0,25 Ω/fase`, `R_ef = 0,225 Ω`) e `Kv = 750` e
`Rth = 3,5 K/W` de catálogo. O reforço em aleta em D e alma em asa invertida soma
~1 W estimado a 1800 RPM (não incluído nos 51,4 mN·m nominais do painel/boss; o
Bloqueador A mede a potência real do conjunto completo).

**2000 RPM não está liberado.** Com o `AX-2810Q`, o escalonamento de torque com
ω² prevê `4,99 A` de fase, `20,63 W` na fonte e `47,0 °C` com `Rth = 3,5 K/W`;
embora a estimativa térmica nominal fique abaixo de 55 °C, o modo 100 Hz não
foi validado estruturalmente nem dinamicamente (terceiro harmônico a 100 Hz /
excitação perto do modo combinado ~89 Hz) e ultrapassa o limite de 20 W do
Bloqueador A. Exige nova qualificação completa antes de ser ensaiado.

### 2.1 O que o ponto de operação impõe

| Consequência | Valor | Onde aparece na geometria |
|---|---:|---|
| Força centrífuga por painel (`44,5 g` ref.) | **158,1 N** (159,9 N a 45 g) | junta espiga/socket, longarina, parafusos M3 |
| Deflexão da ponta do painel (viga uniforme) | 3,83–7,74 mm (7,83 mm a 45 g) | estimativa de envelope; validar engaste e FDM (§10.0) |
| Tensão de flexão no painel (viga uniforme) | 21,7–28,8 MPa (29,1 MPa a 45 g) | resistência não certificada; razão nominal a 30 MPa: 1,38–1,03 |
| Energia cinética do rotor (`J = 1,55 g·m²`) | **27,5–27,6 J** | energia armazenada em operação (premissa não medida) |
| Energia de um painel solto (`44,5 g`, `r = 100`) | **7,9 J** a 18,9 m/s | contenção de ensaio obrigatória |
| Teto provisório de massa do rotor | **420 g** (subtotal nominal **352,14 g**) | folga ampliada para AX-2810Q + placa própria |
| Desbalanceamento admissível (ref. G6.3) | **8,4 g·mm** (recalcular pela massa pesada) | contrapesos, berço da bateria, Δm |

**Duas bases de massa, de propósito:**

- **Cargas estruturais do painel** usam a referência de **44,5 g** (e o teto de
  aceite de **45,0 g**). O painel estimado está em `~42,14 g` (`31,94 g` ABS
  maciço + `6,2 g` fita + `4,0 g` ferragens/chicote a reconciliar).
- **Balanceamento** usa a fórmula `U_adm = m_rotor × 33,4 µm` e `Δm ≤ U_adm / 100 mm`.
  Embora um rotor de ~352 g leve o cálculo G6.3 a `11,8 g·mm`, o projeto mantém
  **`8,4 g·mm`** e **`Δm ≤ 0,084 g`** como critério conservador de referência
  até a pesagem real e o balanceamento dinâmico em dois planos (Bloqueador C).

---

## 3. Coordenadas, datums e convenções

**Origem:** eixo de rota do rotor. **Z para cima.** `Z = 0` é a face de apoio da
base fixa na mesa. Unidades em milímetros, sempre.

**Sentido de giro: anti-horário visto de +Z.** Todo bordo de ataque (lâmina do
painel, longarina, aleta em D, alma em asa invertida e carenagem do boss)
aponta para **+y** local. Inverter o sentido multiplica o arrasto e solicita a
aleta pelo lado aberto do sulco.

**Datums:**

| Datum | Referência |
|---|---|
| A | Face de assentamento do cubo na base serrilhada do eixo (`Z = 180 mm`) |
| B | Face superior do cubo, no plano do rotor — **Z = 186 mm** |
| C | Ombro da longarina, onde o painel encosta — **r = 74 mm** |
| D | Altura do boss do painel a partir da base do painel — **104 mm** |
| E | Eixo vertical da torre estrutural |

**Cadeia de cotas em Z (v4.0):**

```
Z =   0    face de apoio da base fixa na mesa
Z =   4    piso do palco suspenso (folga de 4 mm sobre a mesa)
Z =  12    topo do disco do palco (espessura 8 mm)
Z =  79    topo da base fixa (hanger ring e teto da casca; 6 mm abaixo do painel)
Z = 149    topo da torre maciça + flange superior (12 + 137 mm)
Z = 151    face superior da chapa do motor R01 (chapa de 2 mm)
Z = 180    Datum A — topo da base serrilhada do AX-2810Q (151 + 29 mm MEDIDOS em 13/11)
Z = 186    Datum B — face superior do cubo (180 + 6 mm do cubo)
Z = 189    plano médio do painel (Datum B + 3 mm)
Z =  85    base do painel (189 − 104 mm) → folga de 6,0 mm acima de Z = 79
Z = 293    topo do painel (189 + 104 mm)
```

> Os **29 mm** entre a face superior da chapa R01 (`Z = 151`) e o Datum A (`Z = 180`)
> foram medidos por Pedro em 13/11/2026 com o motor apoiado na base. A divisão
> interna campânula/base serrilhada não foi medida separadamente: modela-se o
> caso de menor folga ao cubo (`26 mm` de corpo de catálogo + `3 mm` de base
> serrilhada). Como `26 + 3 = 29 mm` e o cubo tem `6 mm`, `plate_top_to_datum_b = 35 mm`
> e a torre é ajustada para `137 mm` sobre o palco, preservando `Datum B = 186 mm`.

---

## 4. Regras invioláveis

1. **Bordo de ataque em +y**, em tudo que corta ar: lâmina, longarina, aleta em D, alma e carenagem.
2. **A resultante centrífuga do painel passa pelo centro da espiga** (`Z` local = 0).
3. **Nada de parede abaixo de 0,8 mm** em peça estrutural (4 camadas de 0,2 mm com bico 0,4).
4. **O arquivo [`CAD/parameters.json`](Hologram_Orbiter_v4/CAD/parameters.json) é a fonte de verdade.** STL nunca é editado à mão.
5. **Os três painéis são idênticos e intercambiáveis.** Nenhuma feature assimétrica por posição.

---

## 5. Peças

### 5.1 Painel LED — 3 unidades, ABS

Inalterado em geometria externa em relação à v3.0, mantendo intercambiabilidade
sobre a mesma espiga `11 × 6 mm` e Datum D = 104 mm.

- **Envelope:** `208 × 30 × 8 mm` (mais boss com carenagem em gota, `A × Cd = 237,6–316,8 mm² ≤ 350 mm²`).
- **Posição:** plano médio `r = 100 mm`, face dos LEDs `r = 104 mm`.
- **Nervuras internas:** 5 diafragmas de `1,0 mm` (`Z = −70, −35, 0, +35, +70`), com vão central de `4 mm` (`y = −1,5..+2,5`) para descida dos fios.
- **Canal do LED:** canal único `12,4 × 2,0 mm` na face `+x` com parede local de `2,8 mm` numa faixa de `14,4 mm`, deixando piso de **`0,80 mm`** em ponte de `12,4 mm`. Bolso passante `8,0 × 3,5 mm` sob `Z = −98,5 mm`.
- **Boss e junta:** face de contato em `r = 74 mm` (Datum C), socket `11,2 × 6,2 × 22,5 mm`, torres `2 × Ø10 mm` (`Z = ±18 mm`) para parafusos `M3 × 40` em `r = 80` e `r = 90 mm`, bolsos hexagonais de `2,8 mm` de profundidade (porca M3 plana + Loctite 243; Nyloc não cabe).
- **Massa:** `31,94 g` CAD maciço nu; subtotal nominal montado `42,14 g`; limite **`≤ 45,0 g`**.

### 5.2 Aranha — 1 unidade, PETG

Substitui a peça ABS da v3.0 com reforço completo contra flexão vertical de
braço/raiz (R02), baia ampliada para placa própria e adaptação ao eixo do
**AX-2810Q 750KV**.

| Feature | Cota |
|---|---|
| Disco do cubo | **Ø92 × 6 mm**, assentado na base serrilhada Ø13 do adaptador |
| Furo central | **Ø6,0 mm**, para a bucha de 6 mm que acompanha o AX-2810Q sobre o eixo Ø4 |
| Rebaixo sob a porca | **nenhum** (`0 mm`); arruela **DIN 9021 M4 (12 × 4,3 × 1,0)** assenta direto no topo do cubo (`Z = +6` local) |
| Porca do eixo | **M4 autotravante DIN 985** (`5 mm` de altura) a `1,0 N·m` (~1250 N estimados); ponta do eixo termina `3 mm` acima da porca (`Z = +9 mm` acima do cubo) |
| Baia de eletrônica | anel **Ø84 externo / Ø80 interno, 47 mm de altura**, postes da tampa em `y = ±36 mm` (`72 mm` entre centros), furo Ø2,8 |
| Prateleira para placa própria | 4 mísulas em `r = 36,5 mm` (`50°, 110°, 230°, 290°`, retângulo `63,2 × 36,5`), topo em `Z = 28 mm` (`2 mm` acima da bateria) |
| Berço da bateria | trilhos a **`Z = +10 mm`** (`1,0 mm` livre sobre a ponta do eixo em `+9,0`); bateria `58 × 30 × 17 mm` até `Z = 27 mm` |
| Raiz e reforço do braço | raiz em `r = 40..42 mm`, alargamento em planta até `r = 46 mm`, cunha 45° (`r = 46..52`), **aleta superior em D** (`y = 0,6..5,6`, nariz `y = 7,3`, `Z_top = 22→12 mm` de `r = 41,5` a `74`) e **alma em asa invertida** por baixo (`Z_bot = −6→−3 mm` de `r = 45` a `74`) |
| Espiga | `11,0 × 6,0 × 22,0 mm` (`r = 74..96`), **furos M3** em `r = 80` e `r = 90` |
| Sulco e janela de fiação | janela `r = 38..43 mm`, `y = −10..−5,5`, `Z = 0,8..5,8`; bolso `r = 42,3..48`; sulco `r = 48..70` (`y = −4,4..0`, piso `Z = 2,3`) para **4 condutores SPI Quad** |
| Ventilação do cubo | 3 rasgos de 60° entre braços em `r = 42,5..45,0 mm` (**343,6 mm²** livre ≥ 300 mm², sem abrir a baia) |
| Alívios inferiores / Hall | 3 bolsos inferiores `r = 17..36 mm`, `4 mm` prof. (plano 1 de balanceamento); bolso Hall TO-92 nu em `r = 29 mm`, azimute `20°` |
| Massa CAD maciça | **116,53 g** (alvo `≤ 135 g`) |

> **Seção resistente dos braços reforçados (estimativa a 10° de inclinação, 1800 RPM, painel 45 g):**
> módulos verticais medidos na malha: `535,7 mm³` (`r = 47,5`) → `359,1 mm³` (`r = 60`) → `210,1 mm³` (`r = 73,5`), mantendo tensões em `2,7–3,5 MPa` até o ombro. A espiga `11 × 6 mm` (`r = 77 mm`, `W = 66 mm³`) atinge `9,7 MPa ≤ 12 MPa` e passa a ser a seção limite (dentro do painel).

### 5.3 Tampa da baia — 1 unidade, PETG

- **Ø84 × 5 mm**, pele `1,6 mm`, aba `1,6 mm`, 2 furos Ø3 em `y = ±36 mm` (`72 mm`), 6 copos de balanceamento em `r = 34 mm` (plano 2), janela de acesso `x = 19..29 mm, y = ±12 mm` sobre a chave e JST-XH da placa de interface.
- **Massa CAD maciça:** **12,94 g** (alvo `≤ 14 g`).

### 5.4 Base suspensa em paralelogramo e palco — PETG

Substitui a base + torre rígida da v3.0 por um **conjunto modular impresso em PETG** (`1,27 g/cm³`) com dois modos de operação reversíveis pelas mesmas peças:

1. **Base fixa (`04_base_fixa_PETG_imprimir_invertida.stl`, `425,75 g` CAD):**
   - Ø280 mm externo × 79 mm de altura (imprime invertida, teto em `Z = 0` da mesa, sem suporte).
   - Casca cônica contínua ligando a pista inferior ao anel superior (`r = 103,2..110,9`, `Z = 67..79`), 8 janelas superiores de `16 mm` para apertar os blocos das hastes, 8 furos radiais Ø7 na pista para reapertar os parafusos inferiores.
   - **4 abas externas de grampo** a `45°, 135°, 225°, 315°` (furo Ø5 em `r = 149 mm`; envelope `296 × 296 mm` com brim de 8 mm — cabe na mesa `300 × 300`).
   - **4 blocos de batente** (`22,5°, 112,5°, 202,5°, 292,5°`): curso radial livre de `3,0 mm` até o batente impresso (`r = 123`), bolso para calço opcional de EVA firme (`14 × 6 × 6 mm`, folga livre `1,5 mm` — **nunca encostar o EVA no palco em repouso**), limitador vertical de inclinação (`0,5 mm` sobre as orelhas, travando qualquer flambagem/ruptura em `≤ 0,338°`), folga de yaw de `3,0 mm` de cada lado.
   - **Entalhe de saída do cabo** do motor em `168,75°` (`14 × 10 mm`).
   - Canaleta do cilindro de contenção **removida** nesta casca cônica (invólucro continua fora de escopo).

2. **Palco + torre maciça (`05_palco_torre_PETG.stl`, `494,40 g` CAD):**
   - Disco do palco em `Z = 4..12 mm`, aro externo `r = 103,2..110,9 mm`, 4 orelhas de batente até `r = 120,0 mm`, 4 pás invertidas internas para o amortecedor viscoso, 8 aletas radiais de `4 mm` de espessura subindo de `r = 104, Z = 14` até `r = 17, Z = 80` na torre.
   - **Torre maciça Ø40 mm** (`137 mm` acima do palco, `Z = 12..149`), sem furo central (cabo sai por fora), cone de 45° sob a flange superior (`Ø60 × 8 mm`), rebaixo `Ø32 × 3,5 mm` para as cabeças M3 do motor e 4 furos `M4` (PCD 40 em `0°, 90°, 180°, 270°`, só na flange).
   - **3 ganchos alternados com farpão** ao longo da torre (`Z = 82..113`, em `157,5°`, acima das aletas) para reter os 3 fios `Ø3,0 mm` do AX-2810Q com laçada frouxa até o entalhe da pista (`168,75°`).

3. **8 hastes flexíveis (`08_hastes_flexiveis_macia_1p5_8x.stl`, `1,33 g` cada) + reserva:**
   - Seção quadrada `1,5 × 1,5 mm`, comprimento livre `55 mm` (`75 mm` totais entre centros de blocos `12 × 10 × 4 mm`), furo `Ø3,2 mm` justo para `16 × M3 × 10` + `16 porcas M3`.

4. **Trava reversível 4 + 4 (`09_buchas_trava_4x.stl`, `1,45 g` cada):**
   - **Radial:** 4 buchas com flange `Ø12 × 2 mm` inseridas por fora pelos furos `Ø8,4` (`67,5°, 157,5°, 247,5°, 337,5°`) com `4 × M3 × 40 + 4 porcas M3`.
   - **Vertical:** `4 × M3 × 10` rosqueados pelo teto dos 4 batentes (acesso pelos furos superiores Ø7) encostando nas orelhas (+1/4 de volta) para tracionar as 8 hastes e travar o palco em modo rígido.

5. **Bandeja do amortecedor viscoso — opcional (`10_bandeja_amortecedor.stl`, `30,92 g` CAD):**
   - Apoia na mesa sob o palco com 4 cubas em setor de anel centradas por 4 linguetas nos batentes. Recebe `~4,14 mL` por cuba (`~17 mL` totais) de óleo de silicone `10 000 cSt`. Seca, não adiciona rigidez nem amortecimento.

### 5.5 Suporte do motor R01 — Alumínio 2 mm (e réplica provisória em PLA)

Chapa de `60 × 60 × 2 mm`.

| Furação | Padrão |
|---|---|
| Motor (`AX-2810Q`) | **4 × Ø3,2 em cruz, diagonais 16 e 19 mm** `(±8, 0)` e `(0, ±9,5)` |
| Flange da torre | 4 × Ø4 em PCD 40 (`0°, 90°, 180°, 270°`) |
| Alívio central | **Ø11 mm** (ampliado de Ø8 para livrar o fundo do AX-2810Q; `0,8 mm` de alma até furos M3 impressos em Ø3,4) |

Os desenhos 1:1 estão em [`Hologram_Orbiter_v4/fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf`](Hologram_Orbiter_v4/fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf) e `.svg` (incluindo o disco da arruela de referência `Ø20 × Ø4,3`). Para bancada inicial em baixa rotação, existe a réplica provisória impressa em PLA 2 mm (`exports/stl/R01P_suporte_motor_PLA_provisorio.stl`, `R01P_arruela_eixo_M4_PLA_provisoria.stl` e [`teste_impresso/R01T_placa_teste_PLA_2mm_Creality.gcode`](Hologram_Orbiter_v4/teste_impresso/R01T_placa_teste_PLA_2mm_Creality.gcode)); ela **não substitui o alumínio de 2 mm na operação a 1800 RPM**.

### 5.6 Contrapesos

Sem mudança conceitual: correção em **dois planos** — Plano 1 nos 3 alívios
inferiores do cubo (`r = 17..36 mm`, até `~13,9 g` cada) e Plano 2 nos 6 copos
da tampa (`r = 34 mm`). O layout nominal da baia (`5` envelopes catalogados =
`29,0 g`, Hall `0,2 g`, aranha e tampa) produz `58,9 g·mm` a `28,6°`, corrigidos
em relatório para **`2,06 g` a `180°`** + **`0,99 g` a `300°`** (resíduo nominal
`0,14 g·mm`). Recalcular sempre após pesar os componentes reais e validar no
Bloqueador C em dois planos.

### 5.7 Isolamento de vibração — resolvido pela arquitetura em paralelogramo

O antigo conceito de coxim em TPU (`v2.1`) foi definitivamente descartado. Na
v4.0 o isolamento acontece por translação horizontal do palco nas **8 hastes
PETG de 1,5 mm** (`fn_translação = 4,38 Hz`, abaixo da faixa 10–30 Hz), com
opção de travamento rígido (`4 + 4`) caso a bancada indique vantagem ou
necessidade de isolar ressonâncias de partida.

---

## 6. Interfaces de hardware — medidas vs. assumidas

### 6.1 Motor: AX-2810Q 750KV

| Parâmetro | Valor | Origem |
|---|---|---|
| Corpo (lata / altura) | **Ø35 mm** × `26 mm` (corpo `26 mm` de catálogo HobbyKing) | Ø medido 13/11; altura **a medir** |
| Massa | `72 g` | catálogo |
| **Furação da base** | **4 × M3 em cruz: diagonais de 16 e 19 mm** `(±8, 0)` e `(0, ±9,5)` | **medido em 13/11/2026** |
| **Base → topo do serrilhado** | **29 mm** | **medido em 13/11/2026** |
| **Eixo / adaptador** | Base serrilhada `Ø13` (`3 mm` deduzidos) + trecho liso **`Ø4 × 5 mm`** (com bucha `Ø6 mm`) + rosca **`M4 × 10 mm`** | **medido em 13/11/2026** |
| Fixação do cubo | Cubo assenta na base serrilhada Ø13; furo `Ø6` na bucha; arruela **DIN 9021 M4** (`12 × 4,3 × 1,0`) + porca autotravante **M4 DIN 985** (`5 mm`) a `1,0 N·m` | **escolhido em 13/11/2026** |
| Fios de fase | 3 fios de **`Ø3,0 mm`** | **medido em 13/11/2026** |
| `Kv` / `Kt` | `750 KV` / **12,73 mN·m/A** | catálogo / derivado |
| **Resistência efetiva (`R_ef`)** | **0,225 Ω/fase** (`~0,20–0,25 Ω/fase`, ±25% resolução 0,1 Ω) | **medido em 13/11/2026** (pares 5,3–5,4 Ω menos pontas 4,9 Ω) |

### 6.2 Fita LED: HD107S 144 LED/m, RGB

| Parâmetro | Valor |
|---|---|
| Seção medida | **12,0 × 2,0 mm** (PCB 0,4 + 5050 1,6 mm) |
| Passo / quantidade | 6,944 mm · **29 LEDs/painel** (87 totais, 201,4 mm/painel) |
| Topologia de dados (v4.0) | **SPI Quad** — `CLK` compartilhado (`GPIO4` + resistores 33 Ω) e 3 linhas `DATA` independentes (`GPIO6, GPIO5, GPIO7`), sem retorno |
| Fiação por longarina | **4 condutores idênticos** por painel: `+5 V` e `GND` (AWG 24 em estrela) + `CLK` e `DATA` (AWG 28) |
| Taxa de quadro (SPI Quad) | `32 + 29 × 32 + 32 ≈ 992 bits` por painel em paralelo (~`1/3` do tempo da cadeia serial v3.0) |

### 6.3 Restante da cadeia

- **ESC:** LittleBee Spring 20A (`BLHeli_S 16.7`, gravado em 13/11/2026: `Startup Power = 0,50`, `Demag = High`, `Brake on stop = On`, `LRPP = Off`, `PPM = 1148–1832 µs`).
- **Fonte do ESC:** bancada 10–12 V, limite 30 A, com grampo/resistor de descarga no barramento.
- **Controlador fixo:** ESP32 DevKit 30 pinos (`firmware/esp32-base/`).
- **Controlador do rotor:** ESP32-C3 Super Mini + `74AHCT125` + `A3144` TO-92 nu em `r = 29 mm, az = 20°` (ímã `Ø4 × 2` no suporte `06_suporte_ima_PETG`, `26,5 mm` de altura, entreferro `2,5 mm`, folga `2,1 mm` para a lata Ø35 do AX-2810Q) + bateria LiFePO4 2S 800 mAh 20C (`58 × 30 × 17 mm, 50 g`).

---

## 7. Regras de fabricação FDM

Bico 0,4 mm, camada 0,2 mm, mesa 300 × 300 mm: **painéis em ABS** em câmara
fechada; **aranha, tampa, base fixa, palco/torre, suporte do ímã, hastes,
buchas e bandeja em PETG**. Ver orientações, suportes e perfis em
[`Hologram_Orbiter_v4/docs/GUIA_IMPRESSAO.md`](Hologram_Orbiter_v4/docs/GUIA_IMPRESSAO.md).

---

## 8. Entregáveis do pacote CAD

```
Hologram_Orbiter_v4/
├── CAD/parameters.json          fonte de verdade das cotas
├── CAD/generate.py              gerador paramétrico (Blender 5.x)
├── CAD/physics.py · probe.py    cálculos e sondagem por raios (NumPy)
├── exports/stl/                 16 STLs validados (mm, base Z = 0)
├── exports/fonte/               Hologram_Orbiter_v4.blend
├── exports/preview/             31 renders de inspeção
├── fabricacao/                  R01_suporte_motor_60x60_aluminio_2mm.{dxf,svg}
├── teste_impresso/              réplica PLA provisória da R01 (.stl e .gcode)
└── reports/                     ACEITACAO.md, RELATORIO_VALIDACAO.md, FISICA.json,
                                 geometry_report.json, stl_validation.json, build_manifest.json
```

---

## 9. Critérios de aceitação geométrica e dinâmica

**69 critérios** autoverificados por `CAD/generate.py` em [`reports/ACEITACAO.md`](Hologram_Orbiter_v4/reports/ACEITACAO.md), incluindo todas as checagens da v3.0 (enrolamento por raios, seção `Iyy`, janela de fios na baia Ø80, interseção booleana 0 mm³ da eletrônica + placa própria) acrescidas das verificações da suspensão e reforço:

- Curso radial `3,0 ± 0,1 mm`, folga até EVA `1,5 ± 0,1 mm`, limitador de inclinação `0,5 ± 0,1 mm` (`≤ 0,338°`), folga de yaw `3,0 ± 0,1 mm`;
- Canais dos 16 assentos `12,4 ± 0,15 mm` e furos M3 livres (`8 + 8`);
- Folga vertical painel → topo da base fixa `6,0 mm ≥ 5 mm`;
- Base fixa + brim `296 × 296 mm ≤ 300 × 300 mm`;
- Translação estimada `4,38 Hz ≤ 5,0 Hz` (`~263 RPM`), rocking `105,2 Hz ≥ 39 Hz`, modo combinado `89,3 Hz ≥ 66 Hz`, flambagem primeira haste `36,3 N ≥ 25 N`, tensão haste no batente `9,1 MPa ≤ 12 MPa`;
- Flexão do braço a 10° com painel de 45 g em 4 seções (`r = 47,5; 60; 73,5; 77 mm`): `[2,7; 3,1; 3,5; 9,7] MPa ≤ 12 MPa`.

---

## 10. Memória de cálculo

```
ω = 1800 · 2π/60 = 188,496 rad/s
Kt = 9,5493 / 750 = 12,7324 mN·m/A
R_efetiva = 0,225 Ω  (ponto médio de 0,20–0,25 Ω/fase medido em 13/11/2026)

Arrasto nominal do rotor (Cd lâmina 0,35 · boss carenado, sem somar reforço em asa):
  PONTO DE PROJETO (Cd_boss = 0,35, A·Cd ≈ 277 mm²):
    T = 51,44 mN·m  →  I_fase = T/Kt = 4,04 A
    P_cobre = I²R = 3,67 W  →  T_motor = 25 + 3,5·(3,67 + 0,7) = 40,3 °C
    P_fonte = (Kt·ω·I + I²R + 0,7)/0,95 = 14,81 W  (1,48 A @ 10 V · 1,23 A @ 12 V)
  MELHOR CASO (Cd_boss = 0,20, A·Cd = 158 mm²):
    T = 46,1 mN·m  →  I_fase = 3,62 A  →  T_motor = 37,8 °C
  ESTIRAMENTO 2000 RPM (não liberado):
    I_fase = 4,99 A  ·  P_fonte = 20,63 W  ·  T_motor = 47,0 °C

Massas CAD maciças:
  Painel nu = 31,94 g (+ 6,2 fita + 4,0 ferragens/chicote = 42,14 g subtotal nominal)
  Aranha PETG = 116,53 g · Tampa PETG = 12,94 g
  Rotor nominal = 352,14 g (inclui 40 g folga eletrônica, 50 g bateria, 3 g M4, 0,2 g Hall, 3,05 g contrapeso)
  Massa móvel suspensão = 352,14 (rotor) + 494,40 (palco+torre) + 105,0 (motor+chapa+paraf.) = 951,54 g

Aperto do eixo (M4 DIN 985 a 1,0 N·m, K = 0,2, d = 4 mm, μ = 0,3, r = 7 mm):
  Pré-carga estimada = 1,0 / (0,2 · 0,004) = 1250 N
  Força necessária em regime (51,44 mN·m) = 24,5 N (margem 51,0×)
  Força necessária no teto de 8 A (101,9 mN·m) = 48,5 N (margem 25,8×)
  Força necessária no pico de chute 12 V (250,2 mN·m) = 119,1 N (margem 10,5×)

Partida no chute de 1400 µs (duty = 252/684 = 0,3684, fonte 10–12 V limite 30 A):
  10 V parado: 16,37 A fase · 63,5 W (6,35 A) fonte · 208,5 mN·m · pico 1680 RPM
  12 V parado: 19,65 A fase · 91,4 W (7,62 A) fonte · 250,2 mN·m · pico 1959 RPM
```

### 10.0 Flexão do painel e sensibilidade térmica

A seção do painel (`Iyy = 589,885 mm⁴`, `cx = −0,531 mm`, `A = 106,500 mm²`)
permanece idêntica à conferida na revisão anterior (`CAD/physics.py` e 3 cortes
independentes de STL), com deflexão estimada de `3,83–7,83 mm` e tensão de
`21,7–29,1 MPa` sob carga uniforme de `44,5–45,0 g`. Continua exigindo validação
experimental da transferência de carga lâmina → boss, propriedades do ABS FDM e
fluência antes da liberação do lote definitivo.

| `Cd` lâmina | `Cd` boss | `I_fase` (AX-2810Q) | `T_motor` (`Rth=3,5`) | `T_motor` (`Rth=6,0`) |
|---:|---:|---:|---:|---:|
| 0,35 | 0,20 | **3,62 A** | **37,8 °C** | ~47 °C |
| **0,35** | **0,35** | **4,04 A** | **40,3 °C** | **~51 °C** |
| 0,50 | 0,50 | ~5,92 A | ~55 °C | **~76 °C** |
