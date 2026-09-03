# Especificação CAD — Hologram Orbiter v3.0

**Documento de construção. Autossuficiente: contém tudo o que é preciso para
modelar o projeto do zero, sem nenhum outro arquivo e sem contexto prévio.**

Toda cota aqui é absoluta. Nenhuma é "a mesma de antes" nem "a que mudou".

---

## 1. O que é a máquina

Um display volumétrico por persistência de visão. Três painéis verticais, cada
um com uma fita de LEDs endereçáveis apontando para fora, giram em torno de um
eixo vertical. A 30 rotações por segundo, cada ponto do espaço é varrido por um
painel três vezes por volta: o olho integra e vê uma imagem cilíndrica suspensa.

```
                   ┌─ invólucro (fora de escopo)
        ▐  ╭────────────────────╮  ▌
        ▐  │   painel  ●        │  ▌      3 painéis a 120°
        ▐  │      ╲   ╱         │  ▌      girando a 1800 RPM
        ▐  │       ╲ ╱          │  ▌      raio do plano médio: 100 mm
        ▐  │    ────●────       │  ▌      imagem: Ø208 × 201 mm
        ▐  │       ╱ ╲          │  ▌
        ▐  │      ╱   ╲         │  ▌
        ▐  ╰────────┬───────────╯  ▌
                 torre + motor
        ═══════════════════════════      base Ø280
```

O rotor carrega a própria energia e eletrônica: bateria LiFePO4 2S, ESP32 e as três
fitas viajam com ele. A parte fixa tem o motor, o ESC, a fonte e o sensor de
índice angular. Nada de anel coletor.

**A grandeza que governa tudo é a taxa de imagem**: 3 painéis × 30 rps = 90 Hz.
É por isso que a rotação existe. Todo o resto — estrutura, térmica, tolerâncias —
é consequência de sustentar 90 Hz sem quebrar e sem cozinhar o motor.

---

## 2. Ponto de operação — congelado

| | valor |
|---|---:|
| Raio do plano médio do painel | **100 mm** |
| Rotação nominal | **1800 RPM** = 188,50 rad/s = 30 rps |
| Taxa de imagem | **90 Hz** |
| Cilindro de imagem | **Ø208 × 201 mm** |
| Resolução | 29 px vertical × 180 colunas |
| Corrente de fase prevista | **4,95 A** (melhor caso 4,44 A) |
| Temperatura do motor prevista | **46 °C** com Rth 3,5 (melhor caso 43 °C; 62 °C se o Rth vier 6,0) |

Esses seis primeiros números não são negociáveis pela modelagem. Se alguma
escolha geométrica os ameaçar, a escolha muda — não eles.

> **Por que 4,95 A e não 4,44.** O par 4,44 A / 43 °C é a linha **Cd do boss =
> 0,20** da tabela de sensibilidade em §10.1. O próprio CAD estima o boss em
> Cd 0,30–0,40 (razão de finura 2,23, tabela de Hoerner) e o relatório publica
> A × Cd = 238–317 mm²; o critério de aceite admite até 350 mm². Publicar a
> linha de 0,20 como previsão anunciava uma margem térmica maior do que a
> estimativa do próprio modelo sustenta. O ponto de projeto passa a ser a linha
> **Cd do boss = 0,35** — 4,95 A / 46 °C — e 4,44 A / 43 °C fica registrado como
> melhor caso. Nada muda em P ≤ 20 W nem no limite de 55 °C do bloqueador B; o
> que muda é quanto de folga os documentos prometem. Uma carenagem que **passa**
> no critério de 350 mm² dá 5,0 A e 47 °C, e 63 °C se o Rth vier em 6,0.

**Esticada disponível, não alvo:** 2000 RPM = 100 Hz, a 5,49 A e 51 °C. Só é
liberada depois que o arrasto real for medido. Não projete para ela; apenas não
a impeça.

### 2.1 O que o ponto de operação impõe

| Consequência | Valor | Onde aparece na geometria |
|---|---:|---|
| Força centrífuga por painel | 158,1 N | junta espiga/socket, longarina, parafusos |
| Deflexão da ponta do painel | 2,48 mm | raio dinâmico do rotor: 106,5 mm |
| Tensão de flexão no painel | 13,9 MPa (SF ≈ 2,5) | seção da lâmina, parede de 2 mm |
| Energia cinética do rotor | 27,6 J | energia armazenada em operação |
| Energia de um painel solto | 7,4 J a 18,9 m/s (velocidade no CG, r = 100) | idem |
| Inércia do rotor | 1,55 g·m² | rampa de partida ≥ 8 s |
| Desbalanceamento admissível | **8,4 g·mm** | contrapesos, berço da bateria, Δm |

**Duas bases de massa, de propósito.**

As **cargas estruturais** (força, deflexão, tensão) usam o **teto do limite,
44,5 g por painel**. Dimensionar pelo pior caso é o certo, e o painel real fica
em ~42,1 g — 31,9 g do modelo (canal de 12,4 × 2,0 com parede local), mais fita
e ferragens.

O **balanceamento usa a massa real do rotor**, porque ali a direção segura é a
oposta: rotor mais leve significa desbalanceamento admissível menor.

```
U_adm = m_rotor × 33,4 µm        Δm entre painéis = U_adm / 100 mm
```

Com os **252 g** da v3.0 original: U_adm = 8,4 g·mm e Δm ≤ 0,084 g. O CAD atual
estima ~279 g **supondo ABS maciço** (eletrônica de catálogo e contrapeso
incluídos), o que afrouxaria para 0,093 g.

**Não antecipe nada: recalcule.** O afrouxamento não é o único desfecho. As
peças impressas saem com 35 % de infill e os 173 g de CAD são de sólido maciço,
então o rotor real tende a ficar **abaixo** dos 279 g — e possivelmente abaixo
dos 252. A 240 g o limite **aperta** para U_adm = 8,0 g·mm e Δm ≤ 0,080 g. Use
8,4 g·mm até pesar o rotor montado, e depois recalcule pela massa medida, para
cima ou para baixo.

---

## 3. Coordenadas, datums e convenções

**Origem:** eixo de rotação do rotor. **Z para cima.** Z = 0 é a face de apoio da
base na mesa. Unidades em milímetros, sempre.

**Sentido de giro: anti-horário visto de +Z.** Consequência prática: um corpo
que esteja em +x se move na direção **+y**, e portanto **todo bordo de ataque
aponta para +y**. Isso vale para a lâmina do painel, para a longarina e para
qualquer carenagem. Inverter o sentido multiplica o arrasto.

**Datums:**

| | Referência |
|---|---|
| A | Face de assentamento do cubo contra a campânula do motor |
| B | Face superior do cubo, no plano do rotor — **Z = 186 mm** |
| C | Ombro da longarina, onde o painel encosta — **r = 74 mm** |
| D | Altura do boss do painel a partir da base do painel — **104 mm** |
| E | Eixo vertical da torre estrutural |

**Cadeia de cotas em Z:**

```
Z =   0    face de apoio da base
Z =   4    piso da baia central
Z = 154    topo da torre                     (4 + 150)
Z = 156    face superior da chapa do motor   (chapa de 2 mm)
Z = 186    Datum B — plano do rotor          (156 + 30 do conjunto motor)
Z = 189    plano médio do painel             (Datum B + 3)
Z =  85    base do painel                    (189 − 104)
Z = 293    topo do painel                    (189 + 104)
```

> Os 30 mm entre a chapa e o Datum B: corpo do motor de 24 mm (**medido com
> paquímetro em 02/09/2026**, Ø27,8) mais 6 mm de cubo. Se o isolador (§5.7)
> entrar neste caminho de carga, some a altura dele aqui.

---

## 4. Regras invioláveis

Cinco coisas que, se quebradas, invalidam o projeto mesmo que o modelo feche.

1. **Bordo de ataque em +y**, em tudo que corta ar: lâmina, longarina, carenagem.
2. **A resultante centrífuga do painel passa pelo centro da espiga.** O centro de
   massa do painel em Z tem que coincidir com o centro da junta. Assim a junta
   recebe força pura, sem momento parasita. É um acerto barato e fácil de perder.
3. **Nada de parede abaixo de 0,8 mm** em peça estrutural — são 4 camadas de
   0,2 mm com bico de 0,4. Ver §7.
4. **O arquivo de parâmetros é a fonte de verdade.** STL nunca é editado à mão;
   toda cota sai de uma variável nomeada.
5. **Os três painéis são idênticos e intercambiáveis.** Nenhuma feature
   assimétrica que obrigue a montar em posição específica.

---

## 5. Peças

### 5.1 Painel LED — 3 unidades, ABS

A peça que forma a imagem. Uma lâmina vertical oca com perfil aerodinâmico, com
a fita de LEDs num canal na face externa e um boss central que a prende à
longarina.

**Envelope:** 208 (altura, Z) × 30 (corda, Y) × 8 (espessura radial, X), mais o
boss que se projeta para dentro.

**Posição no rotor:** plano médio em r = 100 mm. Face interna em r = 96, face
externa (a dos LEDs) em r = 104.

**Perfil da lâmina.** Prisma reto — a "corda de 30 mm" é literalmente reta, a
lâmina **não é curva**. Coordenadas validadas, em (x radial, y corda), com
x = +4 sendo a face externa e y = +15 o bordo de ataque:

```
externo:  (-1,-15) (1,-15) (4,-5) (4,11) (3.696,12.531) (2.828,13.828)
          (1.531,14.696) (0,15) (-1.531,14.696) (-2.828,13.828)
          (-3.696,12.531) (-4,11) (-4,-5)

cavidade: (0,-11) (2,-5) (2,11) (1.848,11.765) (1.414,12.414) (0.765,12.848)
          (0,13) (-0.765,12.848) (-1.414,12.414) (-1.848,11.765) (-2,11) (-2,-5)
```

Isso dá bordo de ataque R4 em +y, espessura máxima de 8 mm entre y = −5 e
y = +11, e fuga afilando para 2 mm em y = −15. Parede resultante: **2,0 mm**.
A cavidade vai de Z = −102 a +102 (2 mm de pele em cima e embaixo).

**Nervuras internas:** 5 diafragmas de 1,0 mm em Z = −70, −35, 0, +35, +70,
com o contorno da cavidade escalado em (1,08 · 1,015) para cravar 0,2 mm na
parede. Elas impedem o colapso da seção, não contribuem para rigidez de flexão.

**Canal da fita LED** — cortado na face externa (+x):

| | valor | por quê |
|---|---:|---|
| Canal | **12,4 × 2,0 mm** | PCB de ~0,4 mm colado no fundo; LEDs 5050 (1,5–1,6 mm) rentes à face externa |
| Parede local sob o canal | **2,8 mm** | cavidade recua de x = 2,0 para x = 1,2 numa faixa de **14,4 mm** (canal + 1,0 de cada lado) |
| Batente inferior | 2,0 mm | apoio da ponta da fita |
| Comprimento útil | 206 mm | 29 LEDs a 6,944 mm de passo |
| **Piso remanescente** | **0,80 mm** | parede local de 2,8 menos canal de 2,0, em ponte de 12,4 mm |

> O piso de 0,80 mm é o número crítico desta peça. São 4 camadas, em ponte de
> 12,4 mm, e é a superfície onde a fita se apoia. **Nunca deixe cair abaixo de
> 0,6 mm.**
>
> **Por que não um canal em degrau.** A versão de 02/09 desta seção previa um
> canal raso de 12,4 × 0,6 para o PCB e um rasgo de 5,4 × 1,4 só para os
> LEDs. A fita é um PCB plano com os LEDs **em cima**: o degrau só funcionaria
> com a fita montada de cabeça para baixo, e com os LEDs para fora eles
> sobressairiam 1,4 mm da face — o caso proibido abaixo. Apontado por Pedro em
> 03/09/2026.
>
> Com os LEDs para fora, o PCB é o elemento mais fundo e a única forma de deixar
> a fita rente é um canal de **12,4 × 2,0** com a parede engrossada em toda a
> largura, mais 1,0 mm de terra de cada lado para ligar o piso à parede de 2,0
> por uma área e não por uma linha. Custa **+0,3 g por painel** contra o canal
> original de 1,2 (o canal mais fundo devolve quase tudo o que a parede
> engrossada acrescenta). A ponte é de 12,4 mm a 0,8 mm, **a mesma do canal
> original**, validada no cupom C02, que é uma fatia real do painel.
>
> Engrossar a lâmina inteira de 8 para 10 mm também resolveria, mas com **+25 %
> de área frontal** e o mesmo aumento no arrasto. Não faça isso.
>
> Óptica: LED rente à face, sem paredes ao lado — sem vinhetagem.
>
> Deixar a fita saliente 0,8 mm custa **+12 mN·m de torque, +1,1 A e +9 °C** no
> motor. Não é opção.

**Boss e junta.** O boss se projeta radialmente para dentro, de r = 98 até
r = 74 (24 mm). A face de contato fica no **Datum C, r = 74**, encostando na
ponta do trecho aerodinâmico da longarina; o socket abre dali para fora, na
direção da lâmina. Abriga:

| Feature | Cota |
|---|---|
| Socket para a espiga | 11,2 × 6,2 mm, 22,5 mm a partir da face de contato → fundo em r = 96,5 |
| Face de contato com o ombro | **r = 74 mm (Datum C)** |
| Torres dos parafusos | 2 × Ø10 mm, 36 mm de altura (Z = ±18) |
| Furos dos parafusos | Ø3,2, eixo em Z |
| Posição dos parafusos | 6 e 16 mm para fora da face de contato → **r = 80 e r = 90** |
| Bolso de porca M3 | circunraio 3,35 mm, 2,8 mm de profundidade, na base da torre |
| Gussets | ligam a luva às torres, Z = ±4,8 até ±18 |

> As torres são **Ø10, não Ø8**. Com bolso de porca de circunraio 3,35, um Ø8
> deixaria 0,65 mm de parede ao redor da porca capturada — não sustenta
> pré-carga. Ø10 dá 1,65 mm.

**Carenagem do boss — requisito de primeira ordem.** Nu, o boss apresenta cerca
de 1000 mm² frontais com Cd ≈ 1,0, o que responde por **mais da metade de todo o
arrasto do rotor**. É o item que mais pesa na conta térmica.

Alvo: **A_frontal × Cd ≤ 350 mm²**, desejável ≤ 250. Vale qualquer combinação de
encolher e carenar — reduzir a área é tão válido quanto alisar. Restrições:
bordo de ataque em +y, acesso mantido aos dois parafusos M3, e a carenagem não
pode aumentar a área frontal.

**Massa:** ≤ 45 g montado, com fita e ferragens. **Δm entre os três painéis
≤ 0,084 g** — ver §5.6.

### 5.2 Aranha — 1 unidade, ABS

O cubo central com três braços radiais. Transmite o torque do motor, sustenta os
painéis contra 158,1 N cada um, e abriga a eletrônica de bordo.

| Feature | Cota |
|---|---|
| Disco do cubo | **Ø92** × 6 mm |
| **Furo central** | **Ø8 H8**, para o colar Ø8 do eixo — ver §6.1 |
| Rebaixo sob a porca | **nenhum** — a arruela assenta no topo do cubo; ver a nota sobre o colar do eixo |
| Braços | 3 a 120°, seção aerodinâmica 15 (corda, Y) × 6 (altura, Z) |
| Raiz do braço | r = 38 mm (dentro do cubo); alargamento em planta de r 39 a 46 e cunha a 45° sob o braço de r 46 a 53 (fillet cubo→braço) |
| **Ombro (Datum C)** | **r = 74 mm** |
| **Ponta da espiga** | **r = 96 mm** |
| Espiga | 11,0 × 6,0 mm, 22 mm de comprimento |
| Furos dos parafusos | 2 por braço, Ø3,2 em **r = 80 e r = 90** |
| Baia de eletrônica | anel **Ø82 externo / Ø78 interno, 26 mm** de altura |
| Postes da tampa | 2, espaçados **70 mm** no eixo y (encostados na parede da baia, entre os braços), furo Ø2,8 |

**Perfil dos braços.** Espessura máxima a ~33% da corda a partir de +y, afilando
para a fuga em −y. Mesma lógica da lâmina. O braço útil tem só 58 mm (de r = 38
a r = 96), dos quais 22 são espiga — reproporcione a concordância da raiz para
não engolir o trecho aerodinâmico.

**Sulco de fiação.** O sulco de 4,4 × ~3 mm no lado de fuga (r 48–70, §6.3)
reduz a seção do braço de ~63 para ~47 mm² e desloca o centróide ~2 mm: sob
158 N dá ~9 MPa e SF ≈ 3 em tração. Aceitável; fica registrado.

**Folga da junta:** espiga 11,0 × 6,0 contra socket 11,2 × 6,2 = **0,1 mm por
lado**. Comprimento 22,0 contra 22,5 = **0,5 mm de fundo**. A espiga não encosta
no fundo: a carga radial vai toda para os dois parafusos M3, por projeto.

**Ventilação — resolva com atenção.** O ar de refrigeração do motor precisa
subir pelo cubo, mas a parede da baia de eletrônica ocupa de r = 39 a r = 41 e furos
dentro dela abririam o compartimento da bateria para o motor. Sobra o anel entre
o Ø da baia e a borda do cubo.

> **No CAD v3.0:** 3 rasgos em arco de 60°, entre a baia e a borda do cubo. Com
> o cubo em Ø92 e a baia em Ø82, eles migram para **r 41,5–45**. Requisito:
> **área livre ≥ 300 mm², sem abrir a baia da bateria**, e fora da raiz dos
> braços — 6 rasgos a 60° cairiam em cima delas.
>
> **Fillet da raiz.** Com o cubo Ø92 a concordância antiga (até r = 46) ficava
> inteira sobre o disco. O CAD a substitui por duas coisas: o alargamento em
> planta da raiz, da parede da baia (r 39) à borda do disco (r 46), e uma
> **cunha a 45° sob o braço**, da borda inferior do disco até r ≈ 53, 11 mm de
> largura, que remove o canto reentrante no ponto que carrega 158 N e imprime
> sem suporte.

**Alívios de massa** no lado inferior do disco, deixando 2 mm de pele superior.
Não coincidir com a raiz dos braços nem com os rasgos de ventilação.

**Aperto do eixo — decidido, sem medição pendente.** O torque vai da campânula
ao cubo por atrito. Ele precisa de **46 mN·m**, e isso exige apenas ~22 N de
aperto. O risco de fluência do ABS aparece só se alguém apertar demais:

| Torque | Força | Arruela M6 padrão (Ø12) | **Arruela larga (Ø20)** |
|---:|---:|---:|---:|
| 0,6 N·m | 500 N | 8,0 MPa | **1,9 MPa** |
| 3,0 N·m | 2500 N | 39,8 MPa — escoa | 9,5 MPa |

**Especificado: arruela Ø20 e torque de 0,6 N·m.** Dá 23× de margem na
transmissão de torque e 1,9 MPa no ABS, longe de qualquer fluência. Prever
assento plano de Ø20 no rebaixo do cubo.

**Não use a porca cônica que acompanha o motor.** Ela tem 14 mm de altura e
ocuparia 14 dos 20 mm internos da baia, sobrando 6 mm para uma bateria de 13 mm.
**O colar do eixo muda a fixação.** O desenho do motor (§6.1) mostra um colar
Ø8 × 5 sob a rosca, dentro de uma saliência total cotada em 14: o colar sobe
5 mm acima da campânula, ou 7 se os 2 mm que faltam na soma forem um ressalto
sob ele. O cubo tem 6 mm. Logo o colar termina acima do fundo de qualquer
rebaixo, e uma arruela M6 (furo 6,4) assentaria no aço do colar, não no ABS:
a porca apertaria o colar e o cubo ficaria solto.

Fixação válida nas duas leituras: **sem rebaixo; arruela Ø20 × Ø8,5 × 2 mm em
alumínio** (cortada da chapa da R01; o furo passa pelo colar) sobre o topo do
cubo; **porca M6 fina DIN 439B (3 mm) com trava química** Loctite 243, a
0,6 N·m. Pilha sobre o topo do cubo: arruela 0–2, porca 2–5, ponta do eixo em
+8 (ou +6 na leitura de 12 mm) — sobram 3 mm (ou 1) de rosca, e o topo da
porca fica 1 mm abaixo dos trilhos da bateria (Z = 6). Pressão no ABS:
500 N / 259 mm² = 1,9 MPa. A porca autotravante baixa de 6 mm não cabe em
nenhuma leitura: terminaria em +8, no fim do eixo. **Medir no motor, a partir
da face em que o cubo assenta: topo do colar e ponta do eixo.**

**Massa alvo:** ≤ 75 g (o cubo Ø92 com a baia de 26 mm dá 66 g em ABS maciço;
os 55 g eram do cubo Ø80). O limite que vale é o do rotor, 280 g.

### 5.3 Tampa da baia — 1 unidade, ABS

**Ø82** × 5 mm, pele de 1,6 mm, aba de 1,6 mm, 2 furos Ø3 espaçados 70 mm (eixo
y), 6 copos de balanceamento em r = 34.

**Requisito novo:** acesso à chave liga/desliga e ao conector de carga da
bateria sem desmontar o rotor.

**Massa alvo:** ≤ 12 g (só a pele de 1,6 mm em Ø82 tem 8,8 g; o CAD dá 10,1).

### 5.4 Base e torre — peça única, ABS

Impressa integrada, sem separar no fatiador.

| Feature | Cota |
|---|---|
| Diâmetro externo | **280 mm** — definitivo, limitado pela mesa |
| Pista externa | anel de Ø260 a Ø280, 8 mm de altura |
| Baia central | Ø100 externo, parede 4 mm, 80 mm de altura, piso 4 mm |
| Nervuras radiais | 8 unidades, 8 × 8 mm, da baia até a pista |
| Torre | Ø30 externo, parede 4 mm, 150 mm a partir do piso |
| Flange inferior e superior | Ø60 × 8 mm |
| Furos das flanges | 4 × Ø4 em PCD 40, a 45°, **só na flange superior** |
| Passagem de fiação | furo central da torre + janela lateral |
| Furos periféricos | removidos — as abas de grampo fazem a fixação |
| **Contato com a mesa** | sem balanço; folga ≤ 0,2 mm em 3 pontos a 120° na pista |
| Perpendicularidade da torre | ≤ 1° |

**Apoio na mesa — critério de contato, não de planeza.** A base apoia em toda a
face inferior: fundo da baia, nervuras e pista. Isso é **melhor** que três pés —
a carga da torre desce direto para a mesa e as nervuras ficam integralmente
respaldadas. Mas só vale se a peça sair plana, e ABS de Ø280 empena com a
periferia subindo, o que concentraria o contato num disco de Ø100.

Por isso o aceite é **contato**, não planeza: sobre superfície plana, a base não
balança e um calibrador acusa ≤ 0,2 mm em três pontos a 120° na pista externa.
Fora disso, lixar os pontos altos.

> Não converta em três pés sem antes medir. Fazê-lo transforma a nervura em
> elemento estrutural — o caminho vira torre → piso → nervura → pé — e a seção
> atual de 8 × 8 mm num vão de 90 mm dá 2,8 N/mm, contra os ~66 N/mm que um modo
> de balanço em 60 Hz exigiria. A nervura teria que ir a ~8 × 20 mm. Só reabra
> isso se o ensaio de impacto (§Bloqueador C) voltar abaixo de 45 Hz, e aí o que
> cresce é a **nervura**, não o pé.

**Quatro abas de fixação.** Na face externa do anel, a 90° (45°, 135°, 225°,
315°), 16 mm radiais × 20 mm × 8 mm, furo Ø5 em r = 149 — fora da canaleta e
fora de qualquer caminho de carga. São o único ponto de grampo da base: a pista
de 10 mm tem a canaleta no meio e lábios de 2,8 mm, onde grampo tipo C não pega.
São quatro a 90° e não três a 120° porque só os cantos da mesa de 300 × 300 têm
lugar: uma aba a 165° chegaria a x = −151 mm e não caberia nem sem brim; nos
cantos ela termina em |x| = |y| = 110 e o brim em 118. Três delas bastam.

**Ventilação — requisito, não detalhe.** As aberturas de ar da baia central
**têm que sair pela parede lateral**. Furos no piso da baia ficam vedados assim
que a base é apoiada numa mesa. Alvo de área livre: ≥ 600 mm².

> **Não confunda o propósito.** Esta ventilação serve à baia — eletrônica de
> base, cabos, calor por condução pela torre. **Ela não refrigera o motor**, que
> fica em Z = 156, acima e fora da baia: o único caminho baia → motor é o furo da
> torre e o Ø12 da chapa, cerca de 113 mm². A temperatura do motor é definida
> pelo ar ao redor dele e se resolve por medição, no Bloqueador B.

> **O diâmetro de Ø280 é definitivo, e quem manda nele é a impressora.** A mesa
> tem 300 × 300 mm e o §7 pede brim de 8–12 mm, então 280 + 2 × 8 = 296 mm é o
> limite.
>
> A pista externa traz uma canaleta de 4,4 × 3 mm centrada em r = 135, prevista
> para um invólucro futuro. **Não é item deste escopo** — está lá porque custa
> nada e não pode ser acrescentada depois de imprimir.

**Massa alvo:** ≤ 330 g. A base não gira — massa extra ali só ajuda na
estabilidade. O custo real é tempo de impressão. Se precisar cortar, corte na
parede da baia (4 → 3 mm), nunca na torre, que carrega o rotor.

### 5.5 Suporte do motor — 1 unidade, alumínio 2 mm

Chapa de 60 × 60 × 2 mm. **Não imprimir.** Gerar como referência de corte.

| Furação | Padrão |
|---|---|
| Motor | **4 × Ø3,2 num retângulo de 16 × 19 mm** — ver §6.1 |
| Flange da torre | 4 × Ø4 em PCD 40, a 45° |

Os dois padrões não colidem: raio máximo do padrão do motor ≈ 12,4 mm contra
20 mm do padrão da flange.

### 5.6 Contrapesos

Não são acessório. São o que fecha o balanceamento, e têm alvo numérico.

Com rotor de 251 g a 30 rps em grau G6.3, o desbalanceamento admissível é
**8,4 g·mm** (rotor de 252 g como construído — ver a fórmula em §2.1). Nenhuma das duas maiores fontes
é atingível por posicionamento:

| Fonte | Limite implicado |
|---|---:|
| Δm entre os três painéis | ≤ 0,084 g |
| Excentricidade da bateria de 50 g | ≤ 0,17 mm |

**Requisito:** previsão de correção em **dois planos** (estático e binário), com
resolução de **~90 mg em r = 90 mm**. Furos roscados, rasgos para massa adesiva
ou postes com arruelas — a forma é livre, a resolução não.

**Berço da bateria:** alojamento que centre o pack LiFePO4 de 58 × 30 × 17 mm na
baia Ø78: trilhos a Z = 6 sobre a arruela e a porca fina, paredes laterais e
abas de topo. Ainda assim **não conte com ele** para fechar o balanceamento.

> **No CAD:** plano 1 = três alívios na face inferior do cubo (r 17–36, 4 mm de
> fundo, até ~13 g de tungstênio cada); plano 2 = seis copos na tampa em r = 34
> (~1 g de tungstênio por copo, 34 g·mm). Separação axial de ~30 mm contra
> 208 mm de rotor: o binário se corrige mal, e a resolução fina fica em r = 34
> (0,1 g = 3,4 g·mm, o equivalente aos 90 mg em r = 90), não em r = 90. O
> layout da baia já pede ~2,2 g no alívio de 180°; o Bloqueador C decide o resto.

### 5.7 Isolador de vibração — EM ABERTO

**Não modele um coxim Ø16 × 8 em TPU 95A.** Essa peça, que a versão anterior
especificava, tem rigidez de 540 a 1270 kN/m; com quatro deles sob ~330 g, a
frequência natural do conjunto fica entre **400 e 620 Hz**. Para isolar a
excitação de 30 Hz seria preciso fn ≤ 21 Hz, ou seja **400 a 900 vezes mais
mole**. Aquela peça é um espaçador rígido, não um isolador.

Duas saídas, e a decisão é de engenharia, não de modelagem:

- **assumir montagem rígida** — o motor parafusa direto na flange, e a vibração
  é tratada só por balanceamento; ou
- **redimensionar** o isolador (mais alto, mais mole, menor área, ou elemento
  comercial de silicone), com o critério escrito em **fn**, não em ζ.

Até a decisão sair, modele a montagem **rígida** e deixe a interface preparada:
os 4 furos Ø4 em PCD 40 já servem aos dois caminhos.

## 6. Interfaces de hardware — medidas, não estimadas

### 6.1 Motor: A2212 920KV

| | valor |
|---|---|
| Corpo | Ø27,8 × 24 mm (**medido** em 02/09/2026) |
| Massa | 52 g |
| Tensão | 7,4–14,8 V (2–4S) |
| **Furação da base** | **4 × M3 num retângulo de 16 × 19 mm** |
| **Eixo** | desenho cotado: **colar Ø8 × 5 + rosca M6 × 7** dentro de uma saliência total de **14** (a soma dá 12; os 2 mm restantes devem ser um ressalto Ø6,9 sob o colar) — **medir topo do colar e ponta a partir da face de apoio** |
| Porca do eixo | cônica, M6, sextavado 12 mm, 14 mm de altura |
| Constante de torque | 10,38 mN·m/A |
| Resistência efetiva | 0,221 Ω |

> **Dois pontos onde é fácil errar.** A furação da base é um **retângulo de
> 16 × 19 mm**, não um círculo de furos — e ela fica na **base** do motor, onde
> saem os fios. A **campânula é vazada, com 5 raios, e não tem furos roscados**:
> o eixo M6 é o único caminho nativo de fixação. Os 4 furos em PCD 19 do cubo só
> servem com adaptador de hélice comprado à parte.
>
> O rotor se prende pelo **eixo M6**: cubo assentado nos raios da campânula e
> centrado pelo colar Ø8, arruela Ø20 × Ø8,5 em alumínio e porca M6 fina com
> trava química a 0,6 N·m (§5.2). A porca cônica que acompanha o motor tem
> 14 mm e não serve: ocuparia a baia de eletrônica. A autotravante baixa de
> 6 mm terminaria no fim do eixo.

### 6.2 Fita LED: HD107S 144 LED/m, RGB

| | valor |
|---|---|
| Seção medida | **12,0 × 2,0 mm** |
| Passo | 6,944 mm |
| LEDs por painel | 29 (altura útil 201 mm) |
| Total | 87 LEDs, de 144 disponíveis no rolo de 1 m |
| Consumo | 5,1 W típico · 27 W em branco pleno |
| Taxa de dados | 15,4 Mbit/s a 1800 RPM e 180 colunas; 17,2 a 2000 RPM (limite da fita: 30 MHz) |

### 6.3 Restante da cadeia

ESC LittleBee Spring 20A (BLHeli_S) · fonte de bancada ajustável para o motor ·
ESP32-C3 no rotor · sensor hall + ímã para o índice angular · bateria LiFePO4 2S
de 800 mAh, 20C, 58 × 30 × 17 mm, 50 g (comprada) · impressora com câmara
fechada, volume 300 × 300 mm.

**Requisitos que não têm peça na versão anterior e precisam existir:**

- **canal de fiação** da baia até cada painel, por dentro da longarina — fio
  correndo por fora custa arrasto e desbalanceamento assimétrico;
- **sensor de índice** no rotor e ímã na parte fixa — ver abaixo;
- **berço da bateria e layout da baia** com contrapeso planejado (§5.6);
- **suporte do ímã** com dois pontos de fixação, porque o azimute dele é a
  referência de fase da imagem inteira.

#### Referência de fase — por que existe um sensor hall

O ESP32 gira junto com o rotor e **não sabe para onde está apontando**. Para a
imagem se formar, cada coluna de pixels precisa acender numa posição angular fixa
*do espaço*, a mesma a cada volta. Contando só tempo, qualquer diferença entre a
rotação real e a suposta acumula sem limite: 0,5 % de erro já são 1,8° por volta,
e a imagem sai girando.

O sensor passa pelo ímã uma vez por volta e gera um pulso que diz duas coisas:

- **"ângulo zero, agora"** — zera a fase, e o erro deixa de acumular;
- **"a volta anterior levou X ms"** — é também o tacômetro, e é dele que sai a
  divisão do intervalo em 180 colunas.

```
1800 RPM → 1 volta = 33,33 ms → 180 colunas → 185 µs por coluna

      pulso                                        pulso
        │                                            │
 ───────●────────────────────────────────────────────●───────
        θ=0°       interpolação de 180 colunas       θ=360°
```

Um único pulso serve aos três painéis: sabendo θ, o firmware calcula que o painel
A está em θ, o B em θ+120° e o C em θ+240°.

**Margem de erro.** Ímã Ø4 mm com o sensor a r = 29 mm (onde o CAD o coloca)
dá velocidade de passagem de 5,5 m/s e pulso de ~1,1 ms. A resposta do A3144 mais a latência de
interrupção somam ~5 µs, ou **0,05° — um trigésimo sétimo de uma coluna.** O
sensor não é o elo fraco.

**Consequência para o firmware.** Como a fase se corrige a cada volta, o erro
residual é uma deformação azimutal que cresce do início ao fim de cada volta,
proporcional à variação de rotação entre voltas. Para ficar abaixo de 1/4 de
coluna, a rotação precisa ser estável dentro de **~0,14 % de uma volta para a
outra**.

A inércia de 1,55 g·m² resolve isso sozinha: cogging de 3 mN·m dá 0,034 %,
ripple de comutação de 10 mN·m dá 0,114 %, e só uma perda quase total do torque
de arrasto por uma volta inteira sairia do orçamento. **Não é preciso controle de
rotação em malha fechada** — e o BLHeli_S não o oferece.

#### Implantação

- **sensor hall no rotor e ímã na parte fixa** — nesta ordem, e não o contrário.
  Quem precisa do pulso de índice é o ESP32, que gira junto; sem anel coletor,
  um sensor na base não teria como entregar o pulso a ele. O sensor vai na face
  inferior do cubo e o ímã num poste sobre a chapa do motor, com entreferro de
  2–3 mm, em raio livre da campânula (r = 29 mm no CAD: 15 mm além da campânula
  de Ø27,8; azimute 20° nos dois, rotor e base). Posição angular cotada — é
  a referência de fase da imagem inteira.
- **fiação dos painéis:** 4 condutores por painel (5 V, GND, DATA, CLK). Cada
  painel puxa **1,74 A** em branco pleno, então **AWG 24 para 5 V e GND** e
  AWG 28 para DATA e CLK. Os quatro lado a lado ocupam ~4,6 mm: um canal de
  3 × 2 mm não serve. Prefira **rota pela cavidade da carenagem e por um sulco
  no lado de fuga da longarina** a furar a espiga — a espiga carrega os 158 N.

---

## 7. Regras de fabricação FDM

Bico de 0,4 mm, camada de 0,2 mm, ABS em câmara fechada.

| Regra | Valor |
|---|---|
| Parede mínima estrutural | **0,8 mm** (4 camadas / 2 perímetros) |
| Feature mínima em qualquer direção | 1,2 mm |
| Furo mínimo confiável | Ø2,0 mm |
| Ponte máxima sem suporte | ~15 mm |
| Ângulo máximo em balanço | 45° |

**Orientações de impressão previstas:**

| Peça | Orientação |
|---|---|
| Painel | deitado, 208 mm em X, boss para cima, canal contra a mesa |
| Aranha | plana, cubo na mesa |
| Base + torre | torre em Z, sem inclinação, brim de 8–12 mm |
| Tampa | plana |

O canal do LED forma uma ponte de 12,4 mm a 2,0 mm de altura quando o painel é
impresso deitado. É a superfície mais delicada do projeto — o piso de 0,80 mm
existe justamente para dar 4 camadas ali.

**Cupons de calibração.** Gerar dois corpos de prova pequenos antes do lote:
um da junta espiga/socket (11 × 6) e uma fatia real de 30 mm da ponta do painel
com o canal de 12,4 × 2,0, na orientação de impressão do lote. Custam
minutos e evitam reimprimir painéis de 208 mm.

---

## 8. Entregáveis

**Estrutura:**

```
CAD/parameters.json      toda cota, nomeada — fonte de verdade
CAD/generate.py          gerador paramétrico
exports/stl/             malhas em mm
exports/fonte/           montagem editável
reports/                 validação de malha e relatório geométrico
```

**STL esperados**, todos em mm, com a base normalizada em Z = 0:

| Arquivo | Qtd |
|---|---:|
| `01_aranha_ABS.stl` | 1 |
| `02_painel_LED_ABS_1x.stl` | 3 |
| `02_painel_LED_ABS_3x_mesma_mesa.stl` | 1 lote |
| `03_tampa_baia_ABS.stl` | 1 |
| `04_05_base_torre_ABS_integradas.stl` | 1 |
| `06_suporte_ima_ABS.stl` | 1 |
| `C01_cupom_junta.stl` | cupom |
| `C02_cupom_canal_LED.stl` | cupom |
| `R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl` | referência de corte |

**Montagem.** Ao posicionar os três painéis a 120°, lembre que a rotação de um
objeto é aplicada em torno da própria origem **antes** da translação. É preciso
rotacionar também o vetor de posição:

```python
angle = math.radians(i * 120.0)
panel.rotation_euler[2] = angle
panel.location = (100.0*math.cos(angle), 100.0*math.sin(angle), rotor_z + 3.0)
```

Só definir a rotação e deixar a posição fixa empilha os três painéis no mesmo
ponto, e a montagem deixa de servir para checar interferência.

---

## 9. Critérios de aceitação

Autoverificáveis a partir do modelo, sem medir peça física.

| Grandeza | Critério |
|---|---|
| Raio do plano médio do painel | 100 ±0,1 mm |
| Datum D | 104 ±0,2 mm |
| Δh entre painéis | ≤ ±0,5 mm |
| Piso sob o canal do LED | ≥ 0,6 mm |
| Parede ao redor do bolso de porca | ≥ 1,5 mm |
| Menor parede estrutural do modelo | ≥ 0,8 mm |
| Área livre de ventilação do cubo | ≥ 300 mm², sem abrir a baia, fora da raiz dos braços |
| Área livre de ventilação da base | ≥ 600 mm², **na lateral** (serve à baia, não ao motor) |
| A × Cd do boss carenado | ≤ 350 mm² |
| Massa por painel montado | ≤ 45 g |
| Massa do rotor completo | ≤ 280 g |
| Perpendicularidade torre/base | ≤ 1° |
| **Contato da base** | sem balanço; ≤ 0,2 mm em 3 pontos a 120° |
| Malhas | watertight, 0 arestas não-manifold, 0 triângulos degenerados |
| **Enrolamento por raios** | 0 trechos com enrolamento fora de {0, 1} e 0 membranas, em varredura de ≤ 1,5 mm nos três eixos — watertight não basta: uma casca invertida passa nele |
| Furos M3, socket e bolso da porca | medidos na malha: livres de ponta a ponta, profundidades ±0,1 mm |
| Orientação dos STL | base em Z = 0, escala em mm, volume orientado positivo |

A cavidade do painel é aberta por projeto (vãos nos diafragmas, furo na lâmina e
bolso na ponta): o STL tem **1 componente**. Cavidades seladas apareceriam como
componentes conexos extras com volume negativo.

---

## 10. Memória de cálculo

Para que qualquer número acima possa ser auditado isolado.

```
ω = 1800 · 2π/60 = 188,50 rad/s
Kt = 9,5493/920 = 10,38 mN·m/A
R_efetiva = 0,221 Ω
   derivada do datasheet: hélice 1045 @ 11,1 V, 100% → 10 A, 111 W, 680 gf;
   a hélice absorve ~89 W, logo 22 W de perda a 10 A

Arrasto (Cd lâmina 0,35 · boss carenado):
   PONTO DE PROJETO, Cd do boss 0,35 (estimativa do CAD, A×Cd ≈ 277 mm²):
   T = 51,4 mN·m   →   I = T/Kt = 4,95 A
   P_cobre = I²R = 5,4 W   →   T_motor = 25 + 3,5·(5,4+0,7) = 46 °C
   MELHOR CASO, Cd do boss 0,20 (A×Cd = 158 mm²):
   T = 46,1 mN·m   →   I = T/Kt = 4,44 A
   P_cobre = I²R = 4,4 W   →   T_motor = 25 + 3,5·(4,4+0,7) = 43 °C

Massa do painel nu, medida no STL v3.0 = 31,67 g
                   + 0,3 (canal 12,4 × 2,0 com parede local de 2,8)     = 31,9 g
Massa do painel montado = 31,9 + 6,2 (fita) + 4,0 (ferragens) ≈ 42,1 g

CARGA DE PROJETO usa o teto do limite, 44,5 g — ver §2.1:
Força centrífuga  F = m·ω²·r = 0,0445 · 188,50² · 0,100 = 158,1 N
Deflexão 2,5 a 5,0 mm · Tensão 12 a 16 MPa · SF ≈ 2,0 a 2,8 — derivação abaixo
Inércia 1,55 g·m² · Energia 27,6 J · um painel solto 7,9 J a 18,9 m/s
  (0,5 × 0,0445 × 18,85² — pelo teto de 44,5 g, como as demais cargas; os
   7,4 J publicados antes usavam os 42,1 g estimados)
Rotor completo: ~274 g com a baia ampliada, o layout da eletrônica (15 g de
  catálogo) e o contrapeso de 2,2 g — pesar e recalcular
Balanceamento: e = 6,3/188,50 = 33,4 µm → U = 0,252 · 33,4 = 8,4 g·mm
  (cargas pelo teto de 44,5 g; balanceamento pela massa real — ver §2.1)
Partida: rampa de 8 s → 8,0 A de pico (inércia é 100× a de uma hélice)
```

**Corrente de fase ≠ corrente da fonte.** Os 4,95 A são de fase — é deles que
sai o aquecimento. No ponto de projeto a fonte de bancada vê **16,2 W**, ou seja
**~2,3 A em 7 V**; no melhor caso, **14,4 W** e **~2,1 A em 7 V**. Toda tabela
de corrente na fonte neste pacote usa **7 V** como base: uma linha em 7,4 V dá
um número 6 % menor e não é comparável.
Ajustar a fonte para 6–7 V para o ESC operar em duty alto: a 1800 RPM o motor
está a 26% da rotação a vazio em 2S, e duty baixo piora a comutação.

### 10.0 Flexão do painel — hipóteses explícitas e faixa

Os números de flexão vinham publicados como um trio fechado (2,48 mm · 13,9 MPa
· SF 2,5) sem as hipóteses que os produzem. Elas são:

```
carga distribuída  w = F/L = 158,1 N / 208 mm = 0,76 N/mm
balanço            L = 86 mm      (engaste na ponta das torres, z = 18)
segundo momento    I = 910 mm⁴    (seção da lâmina, herdada da v2.1)
módulo             E = 2,3 GPa

δ = wL⁴/(8EI)          σ = (wL²/2)·c/I,  c = 4 mm (meia espessura)
```

Reproduzindo, e variando só o que é legitimamente incerto:

| L (mm) | E (GPa) | δ (mm) | σ (MPa) | SF (35 MPa) | SF (ABS FDM ~30 MPa) |
|---:|---:|---:|---:|---:|---:|
| 86 (engaste na torre) | 2,3 | 2,5 | 12,3 | 2,8 | 2,4 |
| 86 | 2,0 (glossário) | 2,9 | 12,3 | 2,8 | 2,4 |
| 99 (engaste na luva, z = 5) | 2,0 | 5,0 | 16,4 | 2,1 | 1,8 |

Quatro ressalvas que a faixa acima incorpora:

1. O glossário lista **E = 2,0 GPa**; a conta original usava 2,3. A faixa cobre
   os dois.
2. O engaste em z = 18 supõe que as torres Ø10, ligadas à lâmina só pela alma de
   2,4 mm e pela casca de 0,8, engastam a lâmina. O engaste **seguro** é a luva
   (±5,1), o que alonga o balanço para 99 mm.
3. O I = 910 mm⁴ é da v2.1, com canal de 1,2. Com o piso atual em x 1,2–2,0 ele
   cai ~30 mm⁴.
4. **35 MPa é ABS injetado.** ABS por FDM, no plano das camadas, fica em
   25–30 MPa.

O painel não falha em nenhuma linha da tabela, mas o SF realista é **~2, não
2,5**, e a deflexão é de **3 a 5 mm, não 2,5**. O raio dinâmico vai de 106,5 para
~109 mm — ainda folgado contra o cilindro Ø266. A consequência que importa é a
**fluência**, que o plano de projeto já chama de risco maior: ela é bem mais
provável a 16 MPa do que a 12. É por isso que o bloqueador B mede o crescimento
da ponta, e não só a temperatura.

A orientação de impressão está correta e deve ser mantida: a lâmina deitada põe
a flexão no plano das camadas, que é onde o ABS FDM é forte.

### 10.1 Sensibilidade — por que a ventilação é requisito

| Cd lâmina | Cd boss | I de fase | T com Rth 3,5 | T com Rth 6,0 |
|---:|---:|---:|---:|---:|
| 0,25 | 0,20 | 3,4 A | 36 °C | 40 °C |
| **0,35** | **0,20** | **4,44 A** | **43 °C** | 55 °C |
| 0,35 | 0,35 | 4,95 A | 46 °C | 62 °C |
| 0,50 | 0,50 | 7,26 A | 68 °C | **99 °C** |

O projeto passa no caso central com folga e **depende de ventilação** no pior
caso. Por isso os requisitos de área livre em §5.2 e §5.4 são critérios de
aceitação, e não sugestões.
