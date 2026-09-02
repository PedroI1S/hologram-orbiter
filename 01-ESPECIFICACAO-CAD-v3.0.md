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
        ═══════════════════════════      base Ø300
```

O rotor carrega a própria energia e eletrônica: bateria LiPo 2S, ESP32 e as três
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
| Corrente de fase prevista | 4,44 A |
| Temperatura do motor prevista | 43 °C |

Esses seis primeiros números não são negociáveis pela modelagem. Se alguma
escolha geométrica os ameaçar, a escolha muda — não eles.

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
| Energia de um painel solto | 7,9 J a 19,6 m/s | idem |
| Inércia do rotor | 1,55 g·m² | rampa de partida ≥ 8 s |
| Desbalanceamento admissível | **8,4 g·mm** | contrapesos, berço da bateria, Δm |

**Duas bases de massa, de propósito.** As cargas estruturais (força, deflexão,
tensão) usam **44,5 g por painel** — o teto do limite de 45 g. Dimensionar pelo
pior caso é o certo. O modelo v3.0 saiu em 41,87 g, mas o canal de 2,2 mm com
parede local de 3,0 (§5.1) acrescenta 2,7 g: o painel real vai a **44,5 g** e a
carga de projeto passa a ser a real, sem folga.

Já o **balanceamento usa a massa real do rotor, 252 g**, porque ali a direção
segura é a oposta: rotor mais leve significa desbalanceamento admissível menor.
Usar 273 g afrouxaria o critério em 8 %. Não unifique as duas bases.

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

> Os 30 mm entre a chapa e o Datum B saem do datasheet: corpo do motor de 24 mm
> Os 30 mm entre a chapa e o Datum B saem do datasheet: corpo do motor de 24 mm
> mais 6 mm de cubo. Confirmar com paquímetro na montagem. Se o isolador (§5.7)
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
| Canal raso (PCB) | **12,4 × 0,6 mm** | PCB de ~0,4 mm assenta pelos ombros |
| Rasgo fundo (LEDs) | **5,4 × 1,4 mm** | encapsulamento 5050 de 5,0 × 5,0 × 1,6 |
| Profundidade total | **2,0 mm** | fita rente à superfície |
| Parede local sob o rasgo | **2,8 mm** | cavidade recua de x = 2,0 para x = 1,2, só na faixa de 5,4 mm |
| Batente inferior | 2,0 mm | apoio da ponta da fita |
| Comprimento útil | 206 mm | 29 LEDs a 6,944 mm de passo |
| **Piso remanescente** | **0,80 mm** | parede local de 2,8 menos rasgo de 2,0 |

> O piso de 0,80 mm é o número crítico desta peça. São 4 camadas, em ponte de
> 12,4 mm, e é a superfície onde a fita se apoia. **Nunca deixe cair abaixo de
> 0,6 mm.**
>
> **Canal em degrau, porque o PCB é fino e o LED é grosso.** O PCB tem ~0,4 mm
> e é contínuo; quem tem 1,6 mm é o encapsulamento 5050, que ocupa 5 mm de
> largura a cada 6,944 mm. Um canal reto de 2,2 mm romperia a parede de 2,0.
>
> Canal raso de 12,4 × 0,6 para o PCB, rasgo de 5,4 × 1,4 só para os LEDs, e a
> parede engrossada para 2,8 mm **apenas sob o rasgo**. Custa 0,9 g por painel
> contra 2,7 do canal reto, e a ponte de 0,8 mm passa a vencer **5,4 mm em vez
> de 12,4** — muito mais confiável. O PCB apoia nos ombros, que é onde o adesivo
> trabalha melhor.
>
> Engrossar a lâmina inteira de 8 para 10 mm também resolveria, mas com **+25 %
> de área frontal** e o mesmo aumento no arrasto. Não faça isso.
>
> Óptica: com o LED 1,4 mm abaixo num rasgo de 5,4, o corte fica em 63° — fora
> dos ±60° de abertura do 5050. Sem vinhetagem.
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
| **Furo central** | **Ø8 H8**, para o eixo M6 do motor — ver §6.1 |
| Rebaixo sob a porca | **Ø13 × 2 mm**, assento para arruela metálica — ver nota |
| Braços | 3 a 120°, seção aerodinâmica 15 (corda, Y) × 6 (altura, Z) |
| Raiz do braço | r = 38 mm, com concordância até r ≈ 51 |
| **Ombro (Datum C)** | **r = 74 mm** |
| **Ponta da espiga** | **r = 96 mm** |
| Espiga | 11,0 × 6,0 mm, 22 mm de comprimento |
| Furos dos parafusos | 2 por braço, Ø3,2 em **r = 80 e r = 90** |
| Baia de eletrônica | anel **Ø82 externo / Ø78 interno, 26 mm** de altura |
| Postes da tampa | 2, espaçados 58 mm, furo Ø2,8 |

**Perfil dos braços.** Espessura máxima a ~33% da corda a partir de +y, afilando
para a fuga em −y. Mesma lógica da lâmina. O braço útil tem só 58 mm (de r = 38
a r = 96), dos quais 22 são espiga — reproporcione a concordância da raiz para
não engolir o trecho aerodinâmico.

**Folga da junta:** espiga 11,0 × 6,0 contra socket 11,2 × 6,2 = **0,1 mm por
lado**. Comprimento 22,0 contra 22,5 = **0,5 mm de fundo**. A espiga não encosta
no fundo: a carga radial vai toda para os dois parafusos M3, por projeto.

**Ventilação — resolva com atenção.** O ar de refrigeração do motor precisa
subir pelo cubo, mas a baia de eletrônica ocupa de r = 33 a r = 35 e furos
dentro dela abririam o compartimento da bateria para o motor. Sobra o anel entre
o Ø da baia e a borda do cubo.

> **No CAD v3.0:** 3 rasgos em arco de 60°, entre a baia e a borda do cubo. Com
> o cubo em Ø92 e a baia em Ø82, eles migram para **r 41,5–45**. Requisito:
> **área livre ≥ 300 mm², sem abrir a baia da bateria**, e fora da raiz dos
> braços — 6 rasgos a 60° cairiam em cima delas.
>
> **⚠️ Fillet da raiz.** A concordância do braço termina em r = 46, que passa a
> ser a própria borda do cubo Ø92. Ela deixa de existir como transição e precisa
> ser refeita como fillet cubo→braço: é o ponto que carrega 158 N e sem
> concordância vira concentrador de tensão.

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
Use **porca M6 autotravante baixa em rebaixo de Ø13 × 2 mm**: o topo fica a 4 mm
do cubo e sobram 16 mm para a bateria.

Engate da rosca: o eixo tem ~5 mm de Ø8 liso e ~7 mm de rosca acima da campânula.
O cubo de 6 mm cobre os 5 lisos mais 1 de rosca, deixando **6 mm de rosca livre** —
menos os 2 do rebaixo, sobram 6 mm de engate útil (1 × D). Suficiente.

**Massa alvo:** ≤ 55 g.

### 5.3 Tampa da baia — 1 unidade, ABS

**Ø82** × 5 mm, pele de 1,6 mm, aba de 1,6 mm, 2 furos Ø3 espaçados 58 mm.

**Requisito novo:** acesso à chave liga/desliga e ao conector de carga da
bateria sem desmontar o rotor.

**Massa alvo:** ≤ 8 g.

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
| Furos das flanges | 4 × Ø4 em PCD 40, a 45° |
| Passagem de fiação | furo central da torre + janela lateral |
| Furos periféricos | 4 × Ø4 em PCD 290 |
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

**Três abas de fixação.** Na face externa do anel, a 120°, com furo Ø5 — fora da
canaleta e fora de qualquer caminho de carga. São o único ponto de grampo da
base: a pista de 10 mm tem a canaleta no meio e lábios de 2,8 mm, onde grampo
tipo C não pega.

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
**8,4 g·mm** (rotor de 252 g como construído). Nenhuma das duas maiores fontes
é atingível por posicionamento:

| Fonte | Limite implicado |
|---|---:|
| Δm entre os três painéis | ≤ 0,084 g |
| Excentricidade da bateria de 48 g | ≤ 0,175 mm |

**Requisito:** previsão de correção em **dois planos** (estático e binário), com
resolução de **~90 mg em r = 90 mm**. Furos roscados, rasgos para massa adesiva
ou postes com arruelas — a forma é livre, a resolução não.

**Berço da bateria:** alojamento que centre o pack de ~57 × 30 × 13 mm na baia
Ø66. Projete-o para centrar bem, mas **não conte com ele** para fechar o
balanceamento.

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
| Corpo | Ø27,8 × 24 mm |
| Massa | 52 g |
| Tensão | 7,4–14,8 V (2–4S) |
| **Furação da base** | **4 × M3 num retângulo de 16 × 19 mm** |
| **Eixo** | **M6, saliência de 14 mm** (≈5 mm de Ø8 liso + 7 mm de rosca) |
| Porca do eixo | cônica, M6, sextavado 12 mm, 14 mm de altura |
| Constante de torque | 10,38 mN·m/A |
| Resistência efetiva | 0,221 Ω |

> **Dois pontos onde é fácil errar.** A furação da base é um **retângulo de
> 16 × 19 mm**, não um círculo de furos — e ela fica na **base** do motor, onde
> saem os fios. A **campânula é vazada, com 5 raios, e não tem furos roscados**:
> o eixo M6 é o único caminho nativo de fixação. Os 4 furos em PCD 19 do cubo só
> servem com adaptador de hélice comprado à parte.
>
> O rotor se prende pelo **eixo M6** —
> cubo assentado contra a face do motor, porca baixa e arruela Ø20 a 0,6 N·m
> (§5.2). A porca cônica que acompanha o motor tem 14 mm e não serve: ocuparia
> a baia de eletrônica.

### 6.2 Fita LED: HD107S 144 LED/m, RGB

| | valor |
|---|---|
| Seção medida | **12,0 × 2,0 mm** |
| Passo | 6,944 mm |
| LEDs por painel | 29 (altura útil 201 mm) |
| Total | 87 LEDs, de 144 disponíveis no rolo de 1 m |
| Consumo | 5,1 W típico · 27 W em branco pleno |
| Taxa de dados | 17,2 Mbit/s a 180 colunas (limite da fita: 30 MHz) |

### 6.3 Restante da cadeia

ESC de 15 A com rampa configurável · fonte de bancada ajustável para o motor ·
ESP32 no rotor · sensor hall + ímã para o índice angular · bateria 2S de
850–1000 mAh, ≥20C, ~57 × 30 × 13 mm, ~48 g (a comprar) · impressora com câmara
fechada, volume 300 × 300 mm.

**Requisitos que não têm peça na versão anterior e precisam existir:**

- **canal de fiação** da baia até cada painel, por dentro da longarina — fio
  correndo por fora custa arrasto e desbalanceamento assimétrico;
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

**Margem de erro.** Ímã Ø4 mm com o sensor a r ≈ 37,5 mm dá velocidade de
passagem de 7,1 m/s e pulso de ~0,85 ms. A resposta do A3144 mais a latência de
interrupção somam ~5 µs, ou **0,05° — um trigésimo sétimo de uma coluna.** O
sensor não é o elo fraco.

**Consequência para o firmware e para o ESC.** Como a fase se corrige a cada
volta, o erro residual é uma deformação azimutal que cresce do início ao fim de
cada volta, proporcional à variação de rotação entre voltas. Para ficar abaixo de
1/4 de coluna, a rotação precisa ser estável dentro de **~0,14 % de uma volta
para a outra**. A inércia de 1,55 g·m² ajuda muito nisso. Se o ensaio E mostrar a
imagem "respirando", a causa é essa e a correção é o **modo governor do ESC**,
não o sensor.

#### Implantação

- **sensor hall no rotor e ímã na parte fixa** — nesta ordem, e não o contrário.
  Quem precisa do pulso de índice é o ESP32, que gira junto; sem anel coletor,
  um sensor na base não teria como entregar o pulso a ele. O sensor vai na face
  inferior do cubo e o ímã num poste sobre a chapa do motor, com entreferro de
  2–3 mm, em raio livre da campânula (r ≈ 35–40 mm). Posição angular cotada — é
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

O canal do LED forma uma ponte de 12,4 mm a 1,2 mm de altura quando o painel é
impresso deitado. É a superfície mais delicada do projeto — o piso de 0,80 mm
existe justamente para dar 4 camadas ali.

**Cupons de calibração.** Gerar dois corpos de prova pequenos antes do lote:
um da junta espiga/socket (11 × 6) e um do canal do LED (12,4 × 2,2). Custam
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
| Orientação dos STL | base em Z = 0, escala em mm, volume orientado positivo |

Cavidades internas seladas aparecem como componentes conexos extras com volume
negativo. Isso é **correto** para peça oca — o painel deve ter 1 casca externa
mais uma cavidade por vão entre nervuras.

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
   T = 46,1 mN·m   →   I = T/Kt = 4,44 A
   P_cobre = I²R = 4,4 W   →   T_motor = 25 + 3,5·(4,4+0,7) = 43 °C

Massa do painel nu = 26,9 (lâmina base)
                   + 1,8 (canal menor remove menos material)
                   + 2,1 (torres Ø8 → Ø10)
                   + 3,3 (carenagem, casca de 0,9 mm)  = 34,2 g
Massa do painel montado = 34,2 + 6,2 (fita) + 4,0 (ferragens) = 44,5 g
Força centrífuga  F = m·ω²·r = 0,0445 · 188,50² · 0,100 = 158,1 N
Deflexão 2,48 mm · Tensão 13,9 MPa · SF ≈ 2,5 (ABS ~35 MPa)
Inércia 1,55 g·m² · Energia 27,6 J · um painel solto 7,9 J a 19,6 m/s
Rotor completo, como construído = 252 g
Balanceamento: e = 6,3/188,50 = 33,4 µm → U = 0,252 · 33,4 = 8,4 g·mm
  (cargas pelo teto de 44,5 g; balanceamento pela massa real — ver §2.1)
Partida: rampa de 8 s → 8,0 A de pico (inércia é 100× a de uma hélice)
```

**Corrente de fase ≠ corrente da fonte.** Os 4,44 A são de fase — é deles que
sai o aquecimento. A fonte de bancada vê 15,7 W, ou seja **2,1 A em 7,4 V**.
Ajustar a fonte para 6–7 V para o ESC operar em duty alto: a 1800 RPM o motor
está a 26% da rotação a vazio em 2S, e duty baixo piora a comutação.

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
