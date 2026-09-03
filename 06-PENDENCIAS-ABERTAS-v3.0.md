# Pendências abertas — Hologram Orbiter v3.0

O que **falta**, depois da regeneração do CAD de 03/09/2026 (rev. 3.0.3) e da
incorporação da **revisão independente** do mesmo dia. Os códigos (B'1, C2,
D1…) são os da revisão de 02/09 e continuam valendo; o que fechou está resumido
no fim.

A revisão independente de 03/09 circulou como documento 08 solto; ela foi
**incorporada aqui** e o documento apagado. As notas "REVISAO 03/09 item N" em
`parameters.json`, no gerador e nos documentos apontam para a tabela de
disposição no fim deste arquivo.

**Última atualização:** 03/09/2026

---

## Abertas

### B'1 · Eixo do motor — medir antes de comprar a porca

O desenho cotado do A2212 mostra um **colar Ø8 × 5** sob a rosca M6 × 7, dentro
de uma saliência total de 14 (a soma dá 12: os 2 mm restantes devem ser um
ressalto sob o colar). O colar sobe acima do fundo de qualquer rebaixo do cubo
de 6 mm, e a arruela M6 Ø20 da spec assentaria nele — a porca não apertaria o
cubo. A fixação foi refeita sem rebaixo, com **arruela Ø20 × Ø8,5 × 2 em
alumínio** (disco na referência de corte da chapa) e **porca M6 fina DIN 439B
com Loctite 243**, e vale nas duas leituras do desenho: sobram 3 mm de rosca
com a ponta em 14, 1 mm com 12.

**Medir no motor, a partir da face em que o cubo assenta:** altura do topo do
colar e da ponta do eixo. Campos `unverified_interfaces.shaft.*`.

### B'3 · Canal do LED — ratificar a correção da spec §5.1

A spec previa um canal em degrau (PCB num canal raso de 0,6, LEDs num rasgo
1,4 mais fundo). Os LEDs ficam **em cima** do PCB: o degrau só funcionaria com
a fita de cabeça para baixo, e com os LEDs para fora eles sobressairiam 1,4 mm.
Apontado por Pedro em 03/09; §5.1 corrigida para **canal único 12,4 × 2,0**,
parede local 2,8 numa faixa de 14,4 mm, piso 0,8 em ponte de 12,4 (a mesma do
canal original). Falta o revisor ratificar.

### C2 · Polaridade do ímã

O A3144 é **unipolar**: comuta com um polo só. Se o ímã for colado invertido não
há pulso de índice, e o sintoma parece falha de firmware. Definir e cotar qual
face do ímã aponta para o sensor (campo `unverified_interfaces.magnet`).

### C3 · Campo do motor sobre o sensor

O sensor gira a ~15 mm do rotor de ímãs do motor. Esse campo é estático em
relação ao sensor e pode mantê-lo permanentemente ligado ou desligado.
**Verificar com o motor montado, antes de colar.**

### D1 · Layout da baia — pesar as peças reais

O esboço está em `spider.bay_layout` e o gerador o verifica: envelope,
interferência com berço, postes, porca e rasgo do hall, faixas livres no piso
para os feixes, soma de massas contra a folga de 15 g e desbalanceamento
nominal. Placa de interface (5,5 g) em +x sob a janela da tampa, ESP32-C3 (3 g)
em −x, buck mini560 (2 g) em pé na parede a 140°, capacitor (2,5 g) em pé numa
cerca em (22,5, −22), 2 g de fios. Total 15,0 g, exatamente a folga.
O vetor de desbalanceamento **não é mais só o da eletrônica** (revisão de 03/09,
item 11). O gerador agora soma também os centróides que ele próprio mede nas
malhas, cada um dos quais já passa sozinho dos 8,4 g·mm admissíveis:

| Fonte | U | Azimute |
|---|---:|---:|
| eletrônica da baia | 72,6 g·mm | 13,7° |
| aranha (malha) | 10,2 g·mm | 145,8° |
| tampa (malha) | 9,6 g·mm | 180,0° |
| sensor hall nu (0,2 g em r = 29) | 5,8 g·mm | 20,0° |
| **soma vetorial** | **63,0 g·mm** | **23,3°** |

A correção pedida cai a 203,3°, que **não está dentro de nenhum alívio** (eles
ficam a 60/180/300° com ±18°). Por isso o contrapeso agora é **repartido entre
os dois alívios que cercam a direção**: **2,19 g a 180° + 0,87 g a 300°**, em
r = 33, deixando resíduo de **0,06 g·mm**. Pôr tudo no centro do alívio de 180°,
como estava planejado, deixaria ~17 g·mm — o dobro do admissível. O rotor fecha
em **278,6 g**, 1,4 g abaixo do limite.

**Falta:** pesar cada componente real e atualizar `mass_g`; as posições são
parâmetros. Um XL4015 (~18 g) no lugar do mini560 não fecha. **Atenção à margem
de massa:** 1,4 g é pouco. Ela é conservadora — os 173 g de CAD supõem ABS
maciço e as peças saem com 35 % de infill —, mas pese a aranha e os painéis
antes de acrescentar qualquer coisa ao rotor.

### C7 · Buck mini560 — tensão mínima de entrada · **comprar só depois**

A maioria dos módulos "mini560 5 V" anuncia entrada de **7 a 20 V** (ou
V_out + 1,5 V). O pack é LiFe 2S: 7,2 V cheio, **6,6 no platô**, corte em 5,8.
Se o mínimo real for 7 V, o conversor passa quase toda a descarga em *dropout*,
entrega V_in menos a queda e cai abaixo dos **4,5 V que garantem o V_IH da
fita** — e o "corte em 5,8 V pelo dropout do buck" que o esquema 05 usa é
premissa, não datasheet.

**Fechar assim:** obter o datasheet do módulo exato que for comprado. Aceitável
se V_in mínima ≤ 5,5 V. Caso contrário, trocar por um buck síncrono de entrada
baixa ou um **buck-boost** — o que muda a linha de potência inteira do rotor.
É a pendência de maior alcance ainda aberta, e é anterior à compra.

### C8 · Entreferro do sensor hall — medir antes de colar

Cotas do CAD: bolso do sensor 1,7 mm para um TO-92 de 1,5; bolso do ímã 2,2 para
um ímã de 2,0; entreferro nominal 2,5. **Face a face dá 2,9 mm**, e a pastilha
do A3144 fica ~0,5 mm dentro do encapsulamento: **~3,4 mm efetivos**.

Campo axial de um disco N35 Ø4 × 2 (Br 1,2 T) no eixo:

| distância | B |
|---:|---:|
| 2,5 mm | 80 mT |
| **3,4 mm** | **45 mT** |
| 4,0 mm | 33 mT |
| 4,5 mm | 25 mT |

O A3144 tem **B_OP máximo de 35 mT**. A margem no nominal é de ~30 %, e **+1 mm
de erro no entreferro e o sensor pode não comutar** nas peças de pior caso. Pior:
o entreferro é a única cota da máquina que depende da altura real do conjunto
motor (`motor_stack.plate_top_to_bell_face`, medida mas com
`seat_assumption_verified: false`) — ±2 mm ali levam o entreferro de 0,5 a
4,5 mm.

**Fechar assim:** medir o entreferro com o motor e o rotor montados, **antes de
colar o ímã**. Se passar de 3,0 mm, usar calços sob o poste, ou um ímã **Ø5 × 3
N52** (~2× o campo). Ver também C2 (polaridade) e C3 (campo do motor).

### C9 · ESC LittleBee a 6 V · saída dos fios de fase

Dois itens que só o hardware em mãos fecha:

- **ESC a 6 V.** O LittleBee é 2–4S; 6 V está **abaixo** dos 7,4 V nominais de
  2S. Verificar se o regulador interno e o *gate driver* funcionam em 6 V antes
  de contar com a faixa de ajuste 6–7 V da fonte.
- **Fios de fase.** O motor assenta plano na chapa R01 e os fios saem pela
  lateral do estator. Para descerem pelo alívio central Ø12 e pela torre eles
  precisam de um rasgo na chapa ou de um caminho pela borda —
  `motor_plate.center_clearance_verified` já é `false`. Confirmar com o motor em
  mãos e anotar no DXF antes de cortar a chapa. Lembrar que o arco do suporte do
  ímã ocupa o lado +x: os fios saem por −x.

### D3 · Margem de massa do rotor — 1,4 g

A correção das três colisões de montagem subiu a baia de 26 para 29 mm e os
trilhos de 6 para 9. A aranha passou de 67,5 para **71,0 g** e o rotor de 274,3
para **278,6 g**, contra o limite de **280 g**: sobram **1,4 g**, onde antes
sobravam 5,7.

A margem é conservadora — os 173 g de CAD supõem ABS maciço e as peças saem com
35 % de infill, então o rotor real deve ficar abaixo disso —, mas ela não
suporta mais nenhum acréscimo às cegas.

**Fechar assim:** pesar aranha, painéis e tampa impressos e substituir as
estimativas. Enquanto isso, **nada entra no rotor sem sair outra coisa**. Se a
pesagem confirmar folga, o caminho mais barato para recuperar altura é voltar a
baia para 28 mm (o pack precisa de 26 e a tampa de 1 de folga). Ver também D1,
que depende da mesma pesagem, e a §2.1 da spec: rotor mais leve **aperta** o
desbalanceamento admissível, não afrouxa.

### D2 · Ensaio de impacto na base

Antes de montar o motor: base impressa na bancada, MPU6050 junto à torre, toque
seco no topo, FFT do decaimento. Medir grampeada pelas abas e solta.

**Ensaie com massa na ponta.** A torre nua ressoa em centenas de hertz e o
gatilho de 45 Hz nunca dispararia: prenda ~280 g no eixo na altura do plano dos
painéis, ou monte o rotor parado.

O tubo Ø30 × 4 × 150 dá k ≈ 50 N/mm, e **63 Hz é a conta para massa no topo do
tubo**. A massa real são **344 g** (rotor 274 + motor 52 + chapa 18 — os 322 g
que se lia antes são a massa da própria base, outra peça) com CG **31 mm acima
do topo da torre**. Corrigindo pelo braço rígido, `k_eff = k/(1 + 3a/L + 3a²/L²)
≈ 29 N/mm` e **fn ≈ 46 Hz** — em cima do limiar, e ainda otimista porque ignora
a inércia de rotação do rotor e a flexibilidade da flange e dos rolamentos. A
conta também não cobre o **balanço da base sobre a mesa**. Se vier **abaixo de
45 Hz**, o que cresce é a **nervura**, não o pé: piso 100 % sólido num raio de
40 mm em torno da torre e 4 a 8 gussets da torre para a parede da baia, que hoje
não trabalha.

---

## Fora de escopo

**Invólucro.** A pista externa mantém a canaleta de 4,4 × 3 mm em r = 135 porque
custa nada e não pode ser acrescentada depois de imprimir. A tampa impressa 07
saiu do pacote (`containment_cap.enabled` a devolve). Não é item deste projeto.

**Fixação do rotor.** Decidida: arruela Ø20 a 0,6 N·m, que dá 500 N contra os
22 N necessários e 1,9 MPa no ABS. Não depende de medir a campânula. Ajuste de
03/09: a arruela é Ø20 × **Ø8,5** × 2 em alumínio, porque o colar Ø8 do eixo
sobe 5–7 mm e uma arruela M6 assentaria nele; a porca é a M6 fina DIN 439B com
trava química, sem rebaixo no cubo. O que resta é a medição de B'1.

**Governor do ESC.** Não existe no BLHeli_S, e a conta de estabilidade mostra que
não é preciso: a inércia mantém a variação entre voltas em 0,03 a 0,11 %, contra
0,14 % de orçamento.

---

## Revisão independente de 03/09/2026 — disposição dos 30 achados

Revisão externa sobre os documentos 01 a 07, o README e o pacote
`Hologram_Orbiter_v3_0/`, com recálculo independente do §10 da spec, sondagem
por raios nas malhas exportadas e leitura do gerador. Circulou como documento
08 e foi incorporada aqui; as notas "REVISÃO 08 item N" espalhadas pelo pacote
apontam para esta tabela.

**Três colisões de montagem que nenhum dos 51 critérios cobria** foram
confirmadas na malha e corrigidas; os critérios passaram a **54**. Nove itens
viraram correção de documento, três continuam abertos porque dependem de
datasheet ou do componente em mãos, e três decisões de imprimibilidade foram
tomadas a favor de **manter a geometria e declarar o suporte**.

| # | Achado | Onde parou |
|---|---|---|
| 1 | Ponta do eixo M6 entra 2 mm no envelope da bateria | **CAD** · trilhos Z 6 → 9, baia 26 → 29; critério novo "Fundo da bateria acima da ponta do eixo" (folga 1,0 mm na leitura de 14, 3,0 na de 12) |
| 2 | Trilhos do berço invadem 0,5 mm o assento da arruela Ø20 | **CAD** · `rail_x_positions` ±11 → ±12; critério novo "Assento da arruela livre acima do cubo" |
| 3 | Cabeças dos 4 × M3 do motor assentam na face da flange | **CAD** · rebaixo Ø32 × 3,5 no topo da flange; critério novo. Os M4 em PCD 40 ficam fora do rebaixo e seguem definindo o Datum B |
| 4 | Fuga da lâmina: balanço de 73° ao longo dos 208 mm | **Decidido** · geometria mantida, **suporte declarado** no guia. Alternativa registrada e descartada: perfil de fundo plano |
| 5 | Cauda da carenagem: 58–65° em casca de 0,8 mm | **Decidido** · geometria mantida, **suporte em árvore declarado**. Encurtar a cauda para y = −27 daria 45°, mas derruba a finura de 2,23 para 1,86 e leva o A × Cd para ~277–356 mm² contra o critério de ≤ 350 |
| 6 | Face inferior da flange superior: balanço de 90°, anel de 15 mm | **Decidido** · geometria mantida, **suporte em árvore declarado**. Alternativa registrada e descartada: cone a 45° sob a flange |
| 7 | Ponto de projeto (4,44 A / 43 °C) usa Cd do boss 0,20; o CAD estima 0,30–0,40 | **Documentos** · ponto de projeto passa a **4,95 A / 46 °C** (linha Cd 0,35 da própria §10.1); 4,44 / 43 vira melhor caso. README, 01, 02, 04 e parâmetros |
| 8 | fn da torre é ~46 Hz, não 63; e o ensaio C0 sem massa não a mede | **Documentos** · método do C0 reescrito com massa fictícia de ~280 g; derivação do braço rígido no 04 e em D2 |
| 9 | Flexão do painel sem hipóteses publicadas | **Documentos + CAD** · derivação com L, I e E na spec **§10.0**, faixa 2,5–5,0 mm e 12–16 MPa; a folga do cilindro passa a ser conferida pelo **topo** da faixa |
| 10 | Entreferro do hall: margem de campo ~30 %, dependente da altura do motor | **Aberta → C8** · glossário §4 corrigido: o ±2 mm não é inócuo |
| 11 | Desbalanceamento nominal ignora aranha, tampa e hall | **CAD** · `bay_balance()` soma os centróides medidos na malha (72,6 → 63,0 g·mm a 23,3°) e **reparte o contrapeso entre dois alívios** (2,19 g a 180° + 0,87 g a 300°, resíduo 0,06 g·mm) |
| 12 | Parada de emergência não para o rotor: coast-down de ~1 min | **Documentos** · regra de segurança no 04: contenção fechada por no mínimo 90 s após o corte |
| 13 | Buck mini560: tensão mínima de entrada pode ser > 6,6 V | **Aberta → C7** · é a de maior alcance, e é anterior à compra |
| 14 | Autonomia sem rendimento do buck nem o ESP32-C3 | **Documentos** · 60 → **~50 min** no 05 |
| 15 | Bloqueador B pede bateria < 45 °C, mas G3 roda sem eletrônica | **Documentos** · nota no 04: em G3 é "não aplicável"; o critério vale na repetição em G4 |
| 16 | 256 colunas a 22,0 Mbit/s não cabem em SPI a 20 MHz | **Documentos** · 05 corrigido para **30 MHz** nesse caso |
| 17 | Chave e capacitor a 98–114 g | **Documentos** · nota na lista 03: curso da chave **tangencial**, capacitor colado |
| 18 | Divisor do ADC com 36 kΩ de impedância de fonte | **Documentos** · **100 nF** no pino, no 05 |
| 19 | ESC LittleBee a 6 V, abaixo do nominal de 2S | **Aberta → C9** |
| 20 | Saída dos fios de fase pela chapa | **Aberta → C9** · `motor_plate.center_clearance_verified` já era `false` |
| 21 | Corrente na fonte de 1,95 A na linha do ponto de projeto | **Documentos** · a tabela misturava 7,4 V com 7 V; unificada em **7 V** |
| 22 | Rampa de 12 s dando 7,3 A | **Documentos** · **6,8 A**: (24,3 + 46,1)/10,38 |
| 23 | "322 g no topo" da torre | **Documentos** · 322 g é a massa da **base**; a torre carrega **344 g** |
| 24 | Admissível de 9,1 g·mm em 05 e 07 | **Documentos** · **8,4 g·mm**, como manda a §2.1 |
| 25 | 28 % vs 26 % da rotação a vazio | **Documentos** · unificado na base 7,4 V |
| 26 | Painel solto de 7,4 J calculado com 42,1 g | **Documentos** · **7,9 J** pelo teto de 44,5 g |
| 27 | 4,8 A vs 4,59 A na fonte para os mesmos 8 A de fase | **Documentos** · **4,6 A**, coerente com a tabela do bloqueador A |
| 28 | §2.1 só contempla "afrouxar" o U_adm | **Documentos** · reescrito para **"recalcule"**: com 35 % de infill o rotor tende a ficar abaixo de 252 g, e aí o limite **aperta** |
| 29 | Pesar os painéis "casa" os painéis | **Documentos** · nota em G2: é necessário, não suficiente — massa igual com CG em raio diferente ainda desbalanceia |
| 30 | Notas obsoletas em `parameters.json` | **Corrigido** · `led_strip.source` e `battery.note` |

**Duas observações de quem aplicou a revisão**, para o próximo revisor:

- O item 5 vinha com a sugestão de encurtar a cauda tratando o custo como "um
  pouco de Cd". Não é: a razão de finura cai de 2,23 para 1,86 e o A × Cd
  estimado encosta no critério de 350 mm², justamente a grandeza de que a
  margem térmica do item 7 depende. Por isso a cauda ficou e o suporte entrou.
- Corrigir o item 2 (trilhos para ±12) pôs material acima do ponto onde o
  gerador sondava a pele dos alívios, e a medida passou a somar trilho: o
  critério continuava **passando**, medindo a coisa errada. A sondagem agora
  mede do **teto do alívio**, não pelo comprimento da corrida. Vale como aviso
  geral: mexer numa cota pode invalidar a medição de outra.

---

## Fechadas em 03/09/2026

| # | Item | Como fechou |
|---|---|---|
| A1 | Cascas invertidas nos furos M3 | reproduzido com traçado de raios (enrolamento −1 em x −18…−15,2 e −3,1…+3,1, 132 trechos ruins); `subtract_each()` subtrai um cortador por vez; agora 0 trechos ruins em todas as peças |
| A2 | Membrana no canal | não reproduzida; corrigida por construção (bolso invade o canal em 0,2) |
| B1 | Ombro da longarina | aerofólio termina em 74,0; raio medido na malha: 100,0 |
| B2 | Critérios de aceitação | 54 critérios, os geométricos medidos por traçado de raios no STL final |
| B3 | Cortador da flange | furos só na flange superior; piso sólido de Z = 0 a 12 sob eles |
| B4 | Poste do ímã | suporte sob os dois M4 de ±45°, garfo aberto para dentro, poste em r = 29, 20°; dois M4 passam a × 20 |
| B5 | Abas de grampo | 4 a 90° nos cantos da mesa (3 a 120° não cabem); furo Ø5 em r = 149 |
| B6 | `mass_limit_g` da base | 330; modelo com abas dá 321 |
| B7 | Tampa de invólucro | removida (fora de escopo, confirmado em 03/09) |
| B8 | `validate_stl.py` | enrolamento por raios, faces coincidentes e membranas, nos 9 STL |
| B9 | Canal do LED | canal único 12,4 × 2,0, piso 0,80 medido — ver B'3 para a ratificação |
| B10 | Baia de eletrônica | cubo Ø92, baia Ø82/Ø78; rasgos r 41,5–45; alívios r 17–36; berço do pack LiFe. **Altura 26 → 29 e aranha 67,5 → 71,0 g pela revisão de 03/09, item 1** |
| B11 | Fillet da raiz do braço | cunha a 45° sob o braço (r 46–53) + alargamento em planta r 39–46 |
| B'2 | Face de apoio da campânula | desenho: plana com 5 raios; só o colar no centro, que entra no furo Ø8 |
| B'4 | Rebaixo Ø13 × 2 × arruela Ø20 | sem rebaixo; arruela Ø20 × Ø8,5 (ratificado) |
| B'5 | Postes da tampa a 58 mm | y = ±35, encostados na parede (ratificado) |
| B'6 | Alvos de massa da aranha e da tampa | 75 g e 12 g (ratificado) |
| B'7 | Lâmina de ar de 0,05 mm sob a flange inferior | achada pelo traçado de raios; corrigida |
| B'8 | Eletrônica para LiFe | esquema 05 e glossário atualizados: corte em 5,8 V pelo buck, carregador em modo LiFe |
| C1 | Módulo hall HW-477 no rotor | decidido: A3144 nu no bolso do cubo, pull-up para 3,3 V |
| E1 | Sulco de fiação reduz a seção do braço | anotado na spec §5.2 |
| E2 | Planos de balanceamento reais | anotados na spec §5.6 e no plano de ensaios (C) |
| E3 | Energia do painel solto | um par só, na spec, no README e nos parâmetros. **7,4 → 7,9 J pela revisão de 03/09, item 26** (o teto de massa é 44,5 g, não os 42,1 estimados) |
| E4 | Potência na fonte | unificada em 14,4 W na spec §10 |
| E5 | Taxa de dados | 15,4 Mbit/s a 1800 RPM na spec §6.2 |
| E6 | Raio do hall no §6.3 | r = 29, azimute 20°; pulso refeito |
| E7 | Lista truncada no §6.3 | completada |
