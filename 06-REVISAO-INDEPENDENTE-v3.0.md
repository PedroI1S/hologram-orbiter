# Revisão independente — Hologram Orbiter v3.0

**Data:** 02/09/2026
**Escopo:** README, documentos 00–05, pacote `Hologram_Orbiter_v3_0/` (parâmetros,
gerador, 10 STL, DXF, relatórios, docs internos, renders). O `legado/` foi lido
apenas para contexto.
**Método:** releitura cruzada dos documentos; recálculo independente de cada
grandeza publicada; sondagem geométrica dos STL binários com leitor próprio em
NumPy (interseção raio–triângulo, seções rasterizadas, verificação de número de
enrolamento e de faces coincidentes). O Blender desta máquina não abre
(`libjsoncpp.so.26` ausente), então nada foi regenerado: tudo foi medido nos
STL entregues.

---

## 0. Veredito

O projeto v3.0 é, no geral, coerente: os números físicos publicados se
reproduzem, a geometria macro está certa e 7 dos 10 STL estão limpos. Mas há
**um bloqueador de fabricação que nenhum relatório do pacote detectou**, e um
conjunto de riscos de engenharia que os documentos tratam como resolvidos ou
não tratam.

| Sev. | Achado | Onde |
|---|---|---|
| **P0** | O STL do painel tem **cascas invertidas** (enrolamento −1) nos dois furos M3: um pino Ø3,2 × 2,8 dentro de cada bolso de porca e uma barra Ø3,2 × 6,2 **atravessando o socket** em r = 80 e r = 90. Nos STL `1x` e `3x`. O fatiador pode imprimir isso como sólido; o painel sairia sem furo útil e com o socket obstruído. | §2.1 |
| **P0** | **Membrana de espessura zero** cruzando o canal do LED em Z = −98,5 (junção bolso/canal), no painel e no cupom C02. Pode virar uma parede de 1 filete cruzando o canal, bloqueando o assento da fita. | §2.2 |
| **P1** | **Nenhuma análise modal**, e a estimativa aqui feita coloca o 1.º modo de flexão da torre + piso da baia em **~27–38 Hz**, em cima da excitação de 30 Hz. A fonte de flexibilidade é o piso de 4 mm da baia (com infill), não o tubo da torre. | §3.1 |
| **P1** | **Não existe fonte de sinal de acelerador para o ESC** em nenhum documento nem no BOM. A rampa de ≥ 8 s e o "modo governor" são atribuídos ao ESC; ESCs genéricos de 15 A não têm nem um nem outro. | §4.1 |
| **P1** | BOM pede **M3 × 20** para painel → longarina; a geometria exige **M3 × 40** (torre de 36 mm). BOM exige **nyloc em tudo que gira**; o bolso hexagonal tem 2,8 mm e uma nyloc M3 tem 4 mm. | §4.4 |
| **P1** | Fixação do rotor: com a porca M6 apertada sobre ABS, a pressão sob a arruela passa de **40 MPa** — ABS flui. A "arruela ou bucha metálica" precisa virar **bucha obrigatória**. | §3.6 |
| **P1** | Ombro da longarina modelado em **r = 74,2** (não 74,0). O painel assenta em r = 100,2 e o critério "100 ± 0,1 — por construção" está reprovado, não aprovado. | §2.3 |
| **P2** | O pacote CAD adota Δm ≤ 0,091 g e 9,1 g·mm (rotor de 273 g) e declara a spec desatualizada. A spec §2.1 diz o oposto, com razão: balancear pela massa real (252 g, 8,4 g·mm) é o lado seguro. | §5 |
| **P2** | 14 inconsistências numéricas entre documentos (energia do painel solto, potência na fonte, taxa de dados, raio do hall, cotas do tubo, PCD dos furos periféricos etc.). | §5 |

**Consequência prática:** não imprimir o lote de painéis com os STL atuais.
Corrigir `generate.py` (§2.1) e regenerar. Os demais STL (aranha, tampas, base,
poste, C01, chapa) podem ir para a impressora.

---

## 1. Checagem de valores

Todas as grandezas recalculadas a partir dos parâmetros, sem copiar dos
documentos. ✅ = reproduz; ⚠️ = reproduz com ressalva; ❌ = não reproduz.

| Grandeza | Publicado | Recalculado | |
|---|---:|---:|:-:|
| ω a 1800 RPM | 188,50 rad/s | 188,496 | ✅ |
| Taxa de imagem | 90 Hz | 3 × 30 = 90 | ✅ |
| F centrífuga, 44,5 g @ 100 mm | 158,1 N | 158,1 N (362 g) | ✅ |
| F centrífuga, 41,87 g | 148,8 N | 148,8 N | ✅ |
| Kt (920 KV) | 10,38 mN·m/A | 10,38 | ✅ |
| Torque de arrasto (Cd 0,35 / boss A·Cd 200) | 46,1 mN·m | 45,9 (lâmina 37,2 + boss 7,9 + braços 0,8) | ✅ |
| Corrente de fase | 4,44 A | 4,42 A | ✅ |
| Perda no cobre | 4,4 W | 4,3 W | ✅ |
| T motor, Rth 3,5 | 43 °C | 43 °C | ⚠️ ambiente de 25 °C **dentro do tubo** não está garantido (§3.3) |
| Potência na fonte | 14,4 W (README, ensaios) / 15,7 W (spec, auditoria) | 13,7 W sem ESC; 15,2 W com ESC a 90 % | ⚠️ dois números para a mesma grandeza |
| Deflexão da ponta | 2,48 mm | 2,3–2,8 mm (balanço 86–90 mm, I ≈ 970 mm⁴, E 2,3 GPa) | ✅ |
| Tensão de flexão | 13,9 MPa | 11,6–12,7 MPa | ✅ conservador |
| Inércia do rotor | 1,55 g·m² | 1,40–1,48 g·m² | ✅ conservador |
| Energia cinética | 27,6 J (spec) / 26,1 J (README) / 26 J (ensaios) | 25–26 J | ⚠️ três números |
| Painel solto | 7,9 J a 19,6 m/s (spec) / 7,4 J a 18,9 m/s (README, BOM, ensaios) / 7,4 J a 19,6 (tabela README) | 44,5 g: 7,3 J no CG (r = 95,8) a 18,1 m/s; 8,6 J na face externa | ⚠️ quatro combinações; nenhuma está errada por muito, mas o documento devia ter uma |
| U admissível G6.3, 252 g | 8,4 g·mm | 8,42 g·mm | ✅ |
| Δm entre painéis | 0,084 g | 0,084 g | ✅ (o pacote CAD usa 0,091 — ver §5) |
| Excentricidade da bateria | 0,17 mm | 0,175 mm | ✅ |
| Pico na rampa de 8 s | 8,0 A | 8,0 A (1,55 g·m²) · 7,5 A (1,33) | ✅ |
| Pulso do hall | 0,85 ms a r = 37,5 | 0,57 ms a r = 37,5 (Ø4 mm / 7,07 m/s); **0,73 ms a r = 29, que é onde o CAD colocou** | ⚠️ spec usa r = 37,5; CAD usa r = 29 |
| Erro de 5 µs em graus | 0,05° | 0,054° | ✅ |
| Bits por quadro / taxa | 2859 / 15,4 Mbit/s | 2860 / 15,4 Mbit/s | ✅ (spec §6.2 diz 17,2, que é o valor a 2000 RPM) |
| Ocupação do SPI a 20 MHz | — | 143 µs de 185 µs (77 %) | ✅ viável com DMA |
| Autonomia "850 mAh" | 14 / 42 / 74 min | 12 / 38 / 67 min com 850 mAh; 15 / 44 / 78 com 1000 | ❌ a tabela foi feita com 1000 mAh |
| Campo do ímã Ø4 × 2 N35 no sensor | "não é o elo fraco" | 430–800 G para entreferro de 2,5–3,5 mm (Bop máx. do A3144: 350 G) | ✅ folga de 1,2–2,3× |
| Engate da porca M6 | 6 mm | 6,0 mm, com 0,4 mm de rosca sobrando (se 5 + 7 confirmar) | ✅ apertado |
| Base + brim | 296 mm | 296 mm em mesa de 300 | ⚠️ 2 mm por lado; clipes/linha de purga costumam roubar mais |
| Massa CAD painel / aranha / tampa / base | 31,67 / 52,62 / 7,65 / 310,2 g | volumes conferem no STL (30,45 / 50,59 / 7,36 / 298,2 cm³) | ✅ |

**Onde a memória de cálculo está frágil, mesmo que os números fechem:**

- O modelo térmico é `T = 25 + Rth·(P_cu + 0,7)`. O 0,7 W de perdas no ferro é
  chute razoável; a resistência efetiva de 0,221 Ω foi derivada de um ponto de
  catálogo com hélice e engloba ESC + ferro + cobre — serve como envelope, não
  como Rm. Nada disso invalida o resultado, mas o único número que fecha a
  questão é o termopar.
- O Cd de 0,35 da lâmina é plausível para o perfil; o do boss carenado (0,30–0,40
  sobre 792 mm²) é otimista para uma casca **aberta em cima e embaixo** com duas
  torres dentro. Está coberto pela tabela de sensibilidade (§10.1 da spec).

---

## 2. CAD e STL

### 2.1 P0 — Cascas invertidas nos furos do painel

**O que foi medido.** Raios perpendiculares ao STL `02_painel_LED_ABS_1x.stl`
(orientação de impressão: X = altura do painel, Z_print = 4 − x_painel):

```
raio ao longo do eixo do furo r = 90 (Y = 0,3 · Z_print = 14):
   sólido em x = −18,0 … −15,2     ← dentro do bolso hexagonal da porca
   vazio  em x = −15,2 … −3,1      ← furo aberto
   sólido em x =  −3,1 …  3,1      ← atravessando o socket (altura 6,2)
   vazio  em x =   3,1 … 18,0      ← furo aberto

raio vertical no centro do socket (X = 0 · Y = 0,3), normais das faces:
   z = 12,43  n = (0, −0,16, +0,99)   ← duas normais +z consecutivas:
   z = 15,57  n = (0, −0,16, −0,99)      superfície de FURO flutuando no vazio
```

Seção rasterizada em X = 0 (centro do socket): dois círculos Ø3,2 preenchidos
em Z_print = 14 e 24, exatamente onde os parafusos atravessam a espiga. Seção em
X = −17 (bolso da porca): círculo Ø3,2 no centro do hexágono. O STL `3x` tem o
mesmo defeito nas três cópias. O render `painel_boss_face_contato.png` mostra
o cilindro dentro do socket; passou despercebido.

**Por que o validador não pegou.** As superfícies têm normais apontando para
dentro (número de enrolamento −1). Cada aresta continua com exatamente duas
faces, o sólido continua "watertight", e a contribuição de volume é −0,145 cm³,
invisível nos 30,45 cm³. `validate_stl.py` checa aresta, degeneração e sinal do
volume total — nenhum desses testes vê enrolamento negativo local.

**Causa no código.** `subtract_all()` em `CAD/generate.py` funde os cortadores
com `bpy.ops.object.join()` (concatenação de malhas, não união booleana) e faz
uma única DIFFERENCE com o solver Manifold. Onde dois cortadores se sobrepõem,
o operando tem enrolamento 2, e o resultado 1 − 2 = −1. No painel, os cilindros
dos furos (`panel_screw_hole_*`, altura 38,4) sobrepõem os bolsos hexagonais
(`panel_nut_pocket_*`) e o `socket_cut`. A aranha, a base e as tampas não têm o
problema porque os únicos cortadores que se sobrepunham ali (furo + rebaixo,
bolso + rasgo do hall, rota de fios) foram unidos com `union_all` antes.

**Correção.** Em `subtract_all`, trocar `join_cutters` por `union_all(cutters,
…)` — ou subtrair os cortadores um a um. Regenerar e reexportar `02_*`. Custo
de execução: alguns segundos a mais de booleanas.

**Como o fatiador reage.** PrusaSlicer/Cura com regra par-ímpar imprimem os
pinos e as barras; com regra de enrolamento positivo, ignoram e podem avisar
"malha auto-intersectante". Não dá para prever sem testar — e um lote de
painéis custa 8–10 h.

### 2.2 P0 — Membrana de espessura zero no canal (painel e C02)

Em `X_print = −98,5` (topo do bolso de fios, início do canal) o STL do painel
tem 7 faces coplanares cobrindo a seção do canal (12,4 × 1,2) e do batente,
com um raio ao longo de X registrando duas faces coincidentes de normais
opostas. É uma membrana: o cortador do bolso (`led_wire_pocket`, z até −98,5)
e o do canal (`led_channel_cut`, z a partir de −98,5) **se tocam numa face sem
se sobrepor**, e a junção deixou uma casca dupla. O cupom `C02` tem a mesma
membrana em z = 5,5.

Efeito: fatiadores com "detecção de paredes finas" podem extrudar um filete de
0,4 mm cruzando o canal, justamente no batente onde a fita precisa assentar. O
cupom C02, se impresso, revela isso — o que é a única coisa boa desta história.

**Correção.** Fazer o bolso invadir o canal por 0,2 mm (`channel_z0 + 0.2` no
limite superior do bolso) e, de novo, unir os cortadores antes da diferença.

**Recomendação para o validador.** Acrescentar a `validate_stl.py` um teste de
enrolamento por raios (grade de raios nos três eixos; as normais dos hits
devem alternar entrada/saída; hits coincidentes = membrana). O script usado
nesta revisão detectou os dois defeitos e deu zero falso positivo nos outros
sete STL.

### 2.3 P1 — Ombro da longarina em r = 74,2

`build_arm()` extruda o aerofólio de `root_radius` até `shoulder_radius + 0.2`
para fundir com a espiga. Mas a espiga já começa em `shoulder_radius − 0.2`; o
+0,2 sobrou para fora. Medido no STL: seção aerodinâmica sólida até
**r = 74,2** em y = ±6,5 (fora da espiga de ±5,5). A face de contato do painel
está em r = 74,0 (flanco da carenagem, y ±7,6): o painel encosta na ponta do
aerofólio, não no ombro nominal, e assenta em **r = 100,2**.

O critério de aceitação "raio 100 ± 0,1 — por construção" não é verificado
contra nada: `acceptance()` compara `assembly.panel_radius` (100) consigo
mesmo. A conta real é `74,2 + 26 = 100,2`, fora da tolerância.

**Correção.** `mesh_prism_x(..., a["root_radius"], a["shoulder_radius"])` e
deixar a sobreposição só pelo lado da espiga. Trocar o critério por um cálculo
`shoulder_real + |contact_face_x|`.

### 2.4 Critérios de aceitação que não verificam nada

Além do raio (§2.3): "Δh entre painéis = 0 (mesmo STL)", "perpendicularidade
= 0", "planeza = 0" e "menor parede estrutural" (que é `min()` de cinco
parâmetros escolhidos à mão, não uma medição na malha). Os 28/28 do
`ACEITACAO.md` incluem sete tautologias. Não é grave, mas o README apresenta
"28 critérios automáticos passam" como evidência, e três dos itens mais
importantes (raio, socket livre, furo livre) não estavam sendo medidos.

### 2.5 Sulco de fiação reduz a seção do braço

O sulco (y −4,4…0, piso em z = 2,3) está no lado de fuga do aerofólio, onde a
superfície inferior fica em z ≈ 0,4–1,0. Medido: em r = 55, y = −2, sobram
**1,66 mm** de material sob o sulco (não 2,3). A seção útil do braço cai de
~63 para ~47 mm² e fica assimétrica: o centróide desloca ~2 mm para o bordo de
ataque, e os 158 N radiais passam a gerar momento. Estimativa: 3,4 MPa axial +
~6 MPa de flexão ≈ 9 MPa, SF ≈ 3 sobre ABS impresso no plano. Aceitável, mas a
FIACAO_E_MONTAGEM descreve como se o braço mantivesse 6 mm. Anotar e, se
sobrar massa, mover o sulco para o meio da corda.

### 2.6 Furos da flange inferior atravessam o piso

`flange_hole_*` é cortado de z = −1 a `tower_top + 1`: os 4 furos Ø4 em PCD 40
atravessam também a flange inferior e o piso da baia (medido: vazio em
r = 20, 45°, de z = 0 a 154). Como a torre é integrada, a flange inferior não
parafusa em nada. São quatro furos inúteis no piso, sob o ponto mais carregado
da base. Limitar o cortador à flange superior.

### 2.7 Torre: sem análise modal (ver §3.1)

### 2.8 Planos de balanceamento

A spec §5.6 pede resolução de ~90 mg **em r = 90**. O CAD entregou copos na
tampa em r = 28 (6 × ~0,14 g) e alívios do cubo em r ≈ 24. Capacidade total dos
copos: ~24 g·mm num sentido; resolução equivalente exigida: ~0,3 g por
incremento (fácil com balança de 0,01 g). Funciona, mas a documentação devia
dizer que a resolução migrou para 0,3 g em r 24–28, e que a separação axial
dos dois planos (~25 mm) contra 208 mm de altura do rotor obriga a ~8× mais
massa para corrigir binário.

### 2.9 Poste do ímã com um único parafuso

O poste (`06`) é uma aba de 2,5 mm presa **sob a cabeça de um só M4** em
r = 20; o ímã fica em r = 29, azimute 30°. Nada impede a aba de girar em torno
do parafuso: o entreferro (Z) não muda, mas o azimute muda — e o azimute é a
referência de fase da imagem inteira. Acrescentar um pino ou segundo furo.

### 2.10 Grampos × tubo

O plano de ensaios manda grampear a base à bancada; a PENDENCIAS diz que a base
"não precisa ser parafusada". A pista de 10 mm tem a canaleta no meio: com o
tubo montado não há onde um grampo C pegar sem tocar o tubo. Prever 3 abas na
face externa da pista ou aceitar a fixação por massa (310 g + 1,2 kg do tubo).

### 2.11 O que confere no STL

Medido e coincidente com a spec/parâmetros: piso do canal **0,80 mm**; canal
12,4 × 1,2 aberto no topo; bolso 8 × 3,5 passante; nervuras de 1,0 mm em
±35/±70 com vão de fios; parede ao redor da porca 1,65 mm; socket 11,2 × 6,2 ×
22,5; espiga 11 × 6 × 22 com furos Ø3,2 em r = 80/90; furo do cubo Ø8 e rebaixo
Ø13 × 2; rasgos de refrigeração fora da baia e fora das raízes; bolso e rasgo
do hall em r = 29/30°; janela da baia fora do poste; berço da bateria; canaleta
4,4 × 3 em r 132,8–137,2 com piso em Z = 5; janelas laterais 12 × 12 entre as
nervuras; furo da torre Ø22 com janela para a baia; tampa `07` com 13 furos
(máx. Ø28) e canaleta espelhada; poste de 21,5 mm com bolso Ø4,3 × 2,2; chapa
DXF com 4 × Ø3,2 em ±8/±9,5, 4 × Ø4 em PCD 40 a 45° e Ø12 central; cupons
C01/C02 dimensionalmente corretos (C02 com a membrana de §2.2).

---

## 3. Fundamentação teórica e conceitos

### 3.1 P1 — Ressonância da torre é o risco não calculado

Nenhum documento estima a frequência natural da estrutura fixa. Estimativa de
primeira ordem (E ABS = 2 GPa, 322 g no topo = rotor + motor + chapa):

| Elemento | k (N/mm) | fn (Hz) |
|---|---:|---:|
| Tubo Ø30 × 4 × 150 mm sozinho | 50 | 63 |
| Tubo + piso da baia de 4 mm, maciço (flange Ø60 sobre placa) | 19 | 38 |
| Idem com o piso a 30 % de infill (E efetivo ~metade) | 9 | ~27 |

O elemento mole **é o piso de 4 mm da baia**, não a torre: a flange Ø60 apoia
numa placa de 92 mm de vão. Com o perfil de impressão sugerido (30 % giroide),
o 1.º modo cai para a vizinhança de 30 Hz = 1× rotação. E o 2× (60 Hz) fica
perto do modo do tubo. Há ainda o modo de tombamento do rotor sobre o eixo
Ø3,17 do motor (~47 Hz sem efeito giroscópico; o whirl reverso desce com a
rotação).

Consequências: amplificação de 5–20× do desbalanceamento residual, entreferro
do hall oscilando, e a partida sensorless atravessando a ressonância. O
Bloqueador C, medindo só a 1800 RPM, não distingue ressonância de
desbalanceamento.

**Ações baratas:** (1) ensaio de impacto com o MPU6050 na base impressa antes
de girar — dá a fn real em minutos; (2) na base, piso 100 % sólido num raio de
40 mm em torno da torre e 4–8 gussets ligando a torre à parede da baia (a
parede Ø100 × 80 mm está ali, sem uso estrutural); (3) no Bloqueador C, varrer
600–1800 RPM registrando amplitude × rotação, não só o ponto final.

### 3.2 "Fadiga" é, na verdade, fluência

O plano trata o SF de 2,5 como risco de fadiga a "108 mil ciclos por hora". A
carga centrífuga é **estática** durante a operação: não cicla a 30 Hz. O que
cicla são a gravidade (0,44 N contra 158 N) e a vibração. O risco real do ABS a
12–14 MPa e 40–50 °C é **fluência**: o módulo de fluência cai à metade em ~100 h,
a deflexão da ponta cresce (2,5 → 4–5 mm) e a junta relaxa. Ciclos de fadiga
verdadeiros são as partidas e paradas (dezenas, não milhares). Reescrever o
risco como fluência + partidas, e acrescentar ao Bloqueador B a medição da
posição da ponta do painel antes e depois de 1 h a temperatura.

### 3.3 Térmica: o ambiente não é a sala

- O modelo assume 25 °C ao redor do motor. Com o tubo fechado e a tampa, o motor
  (5–12 W) e os LEDs (5–27 W) aquecem o ar interno; a única troca é pelos 5 177
  mm² da tampa. Um ambiente interno de 35–40 °C empurra o caso central para
  53–58 °C — no limite do bloqueador. A PENDENCIAS 6a já sabe disso; o modelo
  térmico da spec não.
- A "ventilação da base ≥ 600 mm² para gerar fluxo passando pelo motor" (spec
  §5.4, critério de aceite) é um resquício: o motor está a Z = 156, em ar livre
  no topo da torre. O único caminho baia → motor é o furo Ø22 da torre e o Ø12
  da chapa (113 mm²). O critério de 1 152 mm² lateral está satisfeito e é quase
  irrelevante para a térmica do motor.
- **Espessura da fita.** A spec registra a HD107S com "1,0 mm" medido. Um
  encapsulamento 5050 tem 1,6 mm de altura sozinho; 1,0 mm só fecha se a medida
  foi do PCB sem LED. Se os LEDs sobressaírem ~1,4 mm da face externa, são 29
  cubos de 5 mm de frente por painel (A·Cd ≈ 200 mm² em r = 104): **+13 mN·m,
  +28 % no torque, 5,6 A e ~52 °C** no caso central. O cupom C02 com a fita real
  resolve a dúvida — fazer isso antes de qualquer conta de arrasto.

### 3.4 Balanceamento e a baia

- G6.3 e 8,4 g·mm são o grau e o valor certos para a massa real; a spec §2.1
  argumenta corretamente que balancear por 273 g afrouxa o critério. O pacote
  CAD fez o contrário (§5).
- A baia é intrinsecamente assimétrica: buck numa parede, MCU na oposta,
  capacitor eletrolítico de ~2,5 g num segmento lateral (**62 g·mm sozinho**, 7×
  o admissível). "Tudo centrado" não é atingível com peças diferentes em lados
  diferentes; a montagem precisa de um esboço de layout com massas e um
  contrapeso planejado, não só os copos da tampa.
- A eletrônica na baia sofre 90–120 g em r 25–33 mm; tudo (capacitor, módulos,
  chicote) precisa de fixação mecânica, não só solda.

### 3.5 POV, sensor de índice e dados

- 90 Hz, 180 colunas, 185 µs por coluna, 15,4 Mbit/s: tudo consistente. A
  HD107S tem PWM a ~27 kHz, ou seja ~5 ciclos por coluna — boa escolha frente à
  APA102.
- Hall: campo de 430–800 G no entreferro de 2,5–3,5 mm contra Bop ≤ 350 G do
  A3144 — funciona, com **polaridade obrigatória** (polo sul para a face marcada;
  o A3144 é unipolar). Faltou no documento.
- O sensor gira a 15 mm do rotor de ímãs do motor (campânula Ø27,8, 14 polos).
  Esse campo é estático em relação ao sensor e pode mantê-lo ligado ou
  desligado permanentemente. Verificar com o motor montado, antes de colar.
- O A3144 está descontinuado na Allegro; os "3144" à venda são clones. Não é
  problema; é só para não procurar o original.

### 3.6 Fixação do rotor

- Sob a arruela M6 (Ø12 externo, furo Ø8: 63 mm²), um aperto normal de ~3 N·m
  gera ~2,5 kN → **~40 MPa** sobre o ABS. Isso é a tensão de escoamento do
  material; a fluência é certa e o aperto relaxa em horas. A bucha metálica
  (Ø8 × Ø13 × 6 mm, alumínio) tem que ser item do BOM, não alternativa.
- O "eixo M6 com porca cônica" descrito é o **adaptador de hélice** do A2212,
  que se prende à campânula por 4 × M3. A campânula, portanto, **tem furos
  roscados**. Parafusar a aranha diretamente neles (os 4 furos de provisão em
  PCD 19 já existem no cubo) dá torque positivo, assento largo e elimina o
  problema do aperto sobre ABS. Medir o padrão da campânula (a spec diz que não
  há furos; provavelmente há).
- Parafusos motor → chapa: BOM pede **M3 × 8** através de 2 mm de chapa = 6 mm
  de penetração. A base do A2212 aceita ~4–5 mm antes de o parafuso tocar o
  enrolamento — falha clássica desse motor. Usar M3 × 6, ou medir.

### 3.7 Partida e ESC

- Pico de 8 A na rampa de 8 s confere. Mas quem gera a rampa? Ver §4.1.
- A 6–7 V, um ESC com detecção automática de células pode identificar 2S e
  cortar (LVC) em 6,0–6,6 V. Desabilitar o LVC ou operar em 7,4 V.
- 26 % da rotação a vazio é duty baixo para comutação sensorless; o documento
  já cita. Um ESC com governor (heli) ou FOC resolve rampa, governor e LVC de
  uma vez — e pode ser mais barato que iterar.

---

## 4. Eletrônica e BOM

### 4.1 P1 — Falta a fonte do sinal de acelerador

A parte fixa é "motor, ESC, fonte de bancada e um ímã". O ESC precisa de um
sinal servo (PWM 1–2 ms). Ninguém o gera: não há microcontrolador, servo-tester
nem rádio no BOM. A rampa de ≥ 8 s, o "reduzir potência de partida", a parada de
emergência por software e o "modo governor" citados no plano de ensaios são
todos funções desse gerador, não do ESC. Acrescentar um Arduino/ESP32 fixo
(ou servo-tester com rampa) ao esquema e ao BOM, com E-stop físico na fonte.

### 4.2 Divisor do ADC fora da faixa útil

100k/56k dá 3,02 V em 8,4 V. O ADC do ESP32-C3 com atenuação de 11 dB é linear
até ~2,5 V (máx. absoluto 3,1 V). Leituras de bateria cheia ficam na região não
linear. Usar 150k/47k (2,0 V a 8,4 V) e recalcular o corte.

### 4.3 Autonomia

A tabela do 05 foi calculada com 1000 mAh e rotulada 850 mAh (§1). Diferença de
15 %; corrigir o rótulo ou a bateria.

### 4.4 P1 — Parafusos e porcas do painel

| Item | BOM | Necessário |
|---|---|---|
| Parafuso painel → longarina | M3 × 20 | **M3 × 40** (torre 36 + porca 2,4; FIACAO_E_MONTAGEM já diz 40) |
| Porca no bolso hexagonal | nyloc ("não negociável") | bolso de 2,8 mm só aceita porca **plana** (2,4 mm); nyloc M3 tem 4,0 mm |

Decidir: aprofundar o bolso para 4,4 mm (a torre tem 36 mm, cabe) e manter a
nyloc; ou porca plana + trava química. Uma das duas, documentada.

### 4.5 O que está bem

74AHCT125 como conversor 3,3 → 5 V: correto. Pull-up do hall para 3V3 com
sensor em 5 V: correto. Fusível de 7,5 A para 4,3 A máximos: correto. Bulk de
1000 µF: correto. Corte em 3,3 V/célula: correto. Estrela de potência, cadeia
de dados e retorno no painel 3 "morto" para manter simetria: bem pensado.

---

## 5. Documentação — inconsistências

| # | Conflito | Fontes | Vale |
|---|---|---|---|
| 1 | Δm ≤ 0,084 g / 8,4 g·mm (252 g) × Δm ≤ 0,091 / 9,1 g·mm (273 g). A PENDENCIAS diz que a spec §5.6 "ainda cita" 8,4 e que "o vigente é 273 g"; a spec §2.1 explica por que 252 g é a base correta para balanceamento. | spec, README, plano, ensaios, BOM × parameters.json, GUIA_IMPRESSAO, FIACAO, PENDENCIAS | **spec (8,4 / 0,084)**; corrigir o pacote CAD |
| 2 | Painel solto: 7,9 J a 19,6 m/s × 7,4 J a 18,9 × 7,4 J a 19,6 | spec §2.1 e §10 × spec §5.8, README, BOM, ensaios × tabela README | adotar um par (7,9 J / 19,6 m/s é o conservador) |
| 3 | Energia do rotor 27,6 × 26,1 × 26 J | spec × README × ensaios | 27,6 (conservador) |
| 4 | Potência na fonte 15,7 W (2,1 A) × 14,4 W (1,95 A) | spec §10, auditoria × README, ensaios | unificar; 14,4 supõe ESC sem perdas |
| 5 | Taxa de dados "17,2 Mbit/s a 180 colunas" | spec §6.2 | 15,4 a 1800 RPM; 17,2 é a 2000 |
| 6 | Sensor hall em r ≈ 37,5 (7,1 m/s, 0,85 ms) × r = 29 no CAD | spec §6.3 × parameters, FIACAO | CAD (29); refazer a conta na spec |
| 7 | Tubo "Ø275 × 4 × 300" × "Ø274 ext × 4 × 305" | README, plano × BOM, parameters | Ø274 × 305 (é a encomenda) |
| 8 | "Furos periféricos 4 × Ø4 em PCD 290" numa base Ø280 | spec §5.4 | removidos; atualizar a spec |
| 9 | Massa da base ≤ 330 g × ≤ 300 g × 310 g sem critério | spec × BOM × PENDENCIAS | decidir e alinhar |
| 10 | "F-01 resolvido — 131,7 N em r = 100" | auditoria §2.0 | 131,7 era com 35 g; vigente 158,1 (a própria PENDENCIAS aponta) |
| 11 | Semana 1: "cilindro medido" | plano §5 | cilindro é encomendado, não medido |
| 12 | "Grampear a base" × "não precisa ser parafusada" | ensaios × PENDENCIAS 6b | ver §2.10 |
| 13 | Spec §6.3: lista "Requisitos que não têm peça…" termina no primeiro item, com ponto e vírgula | spec | texto truncado; faltam itens |
| 14 | Frase duplicada "**Por que 2S e não outra coisa:**" no BOM; "### 5.1" dentro do §6 no doc 05 | BOM, 05 | tipográfico |
| 15 | PENDENCIAS: "§5.1 batente inferior 2,0 mm — mantido como pele de 2 mm, apoio subiu para −98,5" — correto, mas a spec §5.1 e §7 continuam dizendo que a fita apoia no batente de 2 mm | spec | atualizar a spec |

O README declara "Modelo CAD ✅ v3.0 entregue e verificado — 19 de 20 critérios";
o `ACEITACAO.md` diz "28 de 28". Nenhum dos dois é o número certo depois desta
revisão.

---

## 6. O que está bem resolvido

Para que a lista de problemas não distorça o quadro:

- A decisão r = 100 mm @ 1800 RPM está bem fundamentada; a dependência ω³r³ e
  a comparação na mesma rotação são o argumento correto, e os números fecham.
- A auditoria da v2.1 é sólida; recalculei F-01, F-02, F-07, F-08, F-09, F-11,
  F-23 e todos se sustentam.
- Sentido de giro definido e coerente em lâmina, longarina e carenagem.
- CG do painel em ABS a −0,02 mm da junta: a regra 2 foi de fato atendida, e a
  correção de −1,1 mm com fita e fios está documentada com o momento parasita.
- Rota de fiação sem furar a espiga; retorno do painel 3 montado para simetria.
- Hall no rotor, ímã fixo: a única topologia que funciona sem anel coletor, e
  o documento explica por quê.
- Porca baixa em rebaixo para liberar altura para a bateria: bem resolvido.
- Canaleta de assento espelhada na tampa; furos da tampa menores que o
  círculo mínimo da seção do painel; furos dentro de r = 61.
- Cupons antes do lote; balança de 0,01 g como requisito; "nada de LEDs antes
  de G3"; operação remota.
- Malhas da aranha, tampas, base, poste, C01 e chapa: limpas em todos os
  testes, inclusive nos que o validador do pacote não faz.

---

## 7. Plano de ação

### Antes de imprimir os painéis

1. `generate.py`: unir os cortadores (`union_all`) em `subtract_all`; bolso de
   fios invadindo o canal 0,2 mm; ombro em 74,0; furos da flange só na flange
   superior. Regenerar (Blender funcional necessário — o desta máquina não abre).
2. `validate_stl.py`: teste de enrolamento por raios e de faces coincidentes.
3. Decidir nyloc + bolso de 4,4 mm **ou** porca plana + trava; corrigir o BOM
   para M3 × 40 e M3 × 6 (motor).
4. Cupom C02 **com a fita real**: confirmar espessura total da HD107S (5050).

### Antes de girar

5. Ensaio de impacto na base impressa (fn real); se < 45 Hz, reforçar piso e
   gussets antes de montar o motor.
6. Bucha metálica no cubo como item obrigatório; medir a campânula e, se houver
   furos roscados, parafusar a aranha neles.
7. Gerador de sinal do ESC com rampa e E-stop; ESC com LVC desabilitável (ou
   operar em 7,4 V).
8. Verificar o hall com o motor montado (campo da campânula) e a polaridade do
   ímã; travar a rotação do poste.
9. Layout da baia com massas reais e contrapeso planejado.

### Documental

10. Alinhar Δm/U com a spec (0,084 g / 8,4 g·mm) em `parameters.json`,
    GUIA_IMPRESSAO, FIACAO e PENDENCIAS.
11. Um único par (energia, velocidade) para o painel solto; uma única potência
    na fonte; taxa de dados a 1800; raio do hall = 29; cotas do tubo; PCD dos
    furos; massa da base; lista truncada da spec §6.3.
12. Reescrever o risco "fadiga" como fluência + partidas; acrescentar medição
    de ponta ao Bloqueador B e varredura de rotação ao Bloqueador C.

---

*Produzido a partir dos STL, do `parameters.json`, do `generate.py` (1588
linhas) e dos sete documentos raiz. Scripts de sondagem: leitor de STL binário
com interseção raio–triângulo (Möller–Trumbore), seções rasterizadas a 0,25 mm
e varredura de enrolamento em grade de 1–2 mm nos três eixos. Nenhum número foi
copiado dos documentos revisados.*
