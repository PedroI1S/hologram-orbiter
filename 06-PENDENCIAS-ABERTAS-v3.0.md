# Pendências abertas — Hologram Orbiter v3.0

O que **falta**, depois da regeneração do CAD de 03/09/2026 (rev. 3.0.3) e da
incorporação da **revisão independente** do mesmo dia. Os códigos (B'1, C2,
D1…) são os da revisão de 02/09 e continuam valendo; o que fechou está resumido
no fim.

A revisão independente de 03/09 circulou como documento 08 solto; ela foi
**incorporada aqui** e o documento apagado. As notas "REVISAO 03/09 item N" em
`parameters.json`, no gerador e nos documentos apontam para a tabela de
disposição no fim deste arquivo.

**Última atualização:** 08/09/2026 — rev. local 3.0.4. As disposições de 03/09 no fim são históricas; os cálculos corrigidos em 08/09 prevalecem.

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

### C2 · Polaridade do ímã — decidida, confirmar na bancada antes de colar

**Decisão de Pedro, 03/09: a face positiva do ímã aponta para o sensor
(repulsão).** Registrada em `unverified_interfaces.magnet.polarity`.

**Um alerta antes de colar.** O A3144 é unipolar e comuta com o **polo sul**
apresentado à **face marcada** (serigrafada) do TO-92 — é assim que a família
A314x é especificada. "Face positiva" costuma designar o **norte** do ímã. Se as
duas convenções valerem como escritas, o ímã está invertido e **não haverá pulso
de índice** — exatamente a falha que esta pendência existe para evitar, e cujo
sintoma parece problema de firmware.

Como "positiva" e "repulsão" dependem de qual ímã de referência foi usado no
teste, a nomenclatura não resolve sozinha. **O ensaio de bancada resolve, e leva
um minuto:**

1. Alimentar o A3144 nu com **VCC=5 V**, GND comum local e **pull-up de 10 kΩ para 3,3 V**. A alimentação mínima garantida do A3144 original é 4,5 V.
2. Aproximar a face escolhida do ímã da **face marcada** do TO-92, a ~3 mm
   (o entreferro efetivo do projeto — ver C8).
3. A saída tem de ir a **nível baixo**. Se não for, é a outra face.

Só depois disso a cola entra. Fazer junto com C3 (campo do motor) e C8
(entreferro), que exigem a mesma montagem.

### C3 · Campo do motor sobre o sensor

O sensor gira a ~15 mm do rotor de ímãs do motor. Esse campo é estático em
relação ao sensor e pode mantê-lo permanentemente ligado ou desligado.
**Verificar com o motor montado, antes de colar.**

### D1 · Layout e massa real da eletrônica

O buck permanece a 140° com envelope/guia recuados 1,2 mm radialmente (wall_gap=1,5 mm). A colisão com a raiz é verificada por interseção contra a malha final. Medir o módulo real, principalmente indutor, soldas, fios e retenção.

Os cinco componentes da baia continuam com 15 g estimados. Consultar `reports/geometry_report.json` para o vetor e os contrapesos desta execução. Pesar componentes e peças impressas, pois infill e distribuição dos chicotes mudam centróides. O Hall entra tanto no vetor quanto no subtotal de massa.

### R01 · Resistência e fluência dos painéis — bloqueia o lote definitivo

A seção foi corrigida para Iyy=589,8846 mm⁴. O envelope de viga com 44,5 g dá 3,83–7,74 mm; com o teto de 45 g, chega a 7,83 mm / ~29,1 MPa. A aproximação não certifica engaste, transferência de carga, ABS FDM ou fluência. Fechar essas verificações e decidir eventuais mudanças de perfil antes de fabricar o lote definitivo. O cálculo distribuído parcial em `FISICA.json` não é um limite de aceite.

### R04/R05 · Instrumentação e método de ensaio — ainda não executados

Seguir o plano 04 corrigido: termopar somente em parte fixa com ponto validado, medição apropriada da campânula/bateria girantes e referência fixa 1/rev sincronizada. Balanceamento em dois planos exige observações independentes e massas de teste em cada plano. Equipamentos e métodos ainda precisam de qualificação; não registrar aprovação por ausência de medição.

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

O A3144 original tem **B_OP máximo de 35 mT a 25 °C e 45 mT na faixa térmica**. Portanto, 45 mT de campo nominal não dão margem térmica garantida; **+1 mm
de erro no entreferro e o sensor pode não comutar** nas peças de pior caso. Pior:
o entreferro é a única cota da máquina que depende da altura real do conjunto
motor (`motor_stack.plate_top_to_bell_face`, medida mas com
`seat_assumption_verified: false`) — ±2 mm ali levam o entreferro de 0,5 a
4,5 mm.

**Fechar assim:** medir o entreferro com o motor e o rotor montados, **antes de
colar o ímã**. Se passar de 3,0 mm, usar calços sob o poste, ou um ímã **Ø5 × 3
N52** (~2× o campo). Ver também C2 (polaridade) e C3 (campo do motor).

### C9 · ESC a 6 V · saída dos fios de fase

**O ESC não é alimentado pela bateria** (ratificado por Pedro, 03/09, e já era o
que o esquema 05 §8 descrevia): ele fica na **parte fixa**, alimentado pela
**fonte de bancada em 6–7 V, ≥ 5 A**. A bateria LiFe do rotor alimenta só a
fita, o ESP32-C3 e o sensor. As duas linhas de energia não se encontram.

Isso encerra a metade da pendência que dependia da origem da alimentação, e o
**LVC também já estava encerrado**: o glossário §2–3 registra, do manual Rev16.x,
que BLHeli_S **não tem corte por baixa tensão**. Sobra um resíduo estreito:

- **Margem do ESC em 6 V.** O LittleBee Spring é especificado para **2–4S**, ou
  seja 7,4 V nominais no piso da faixa, e o projeto o opera deliberadamente em
  **6–7 V** para manter o duty alto (spec §10). O que ainda não foi verificado
  não é o LVC nem a fonte, e sim se o **regulador interno** (que alimenta o
  EFM8BB21) e o **gate driver** têm margem em 6,0 V. Gate drive fraco não
  desliga o ESC: aumenta o RdsOn e aparece como calor no ESC e comutação suja.
  **Fechar assim:** operar o primeiro ensaio em **7,0 V**, não em 6,0, e só
  descer se o ESC ficar frio e a comutação limpa. Se houver instabilidade,
  suba a tensão antes de suspeitar do sinal.
- **Fios de fase.** O motor assenta plano na chapa R01 e os fios saem pela
  lateral do estator. Para descerem pelo alívio central Ø12 e pela torre eles
  precisam de um rasgo na chapa ou de um caminho pela borda —
  `motor_plate.center_clearance_verified` já é `false`. Confirmar com o motor em
  mãos e anotar no DXF antes de cortar a chapa. Lembrar que o arco do suporte do
  ímã ocupa o lado +x: os fios saem por −x.

### D3 · Orçamento completo de massa e chicotes

O teto do rotor permanece **280 g**. O relatório publica um subtotal nominal com eletrônica de catálogo, Hall e contrapesos; ainda é necessário reconciliar as ferragens de 4 g/painel com a massa real dos chicotes de seis condutores. A estimativa antiga de fios no CG não foi uma pesagem e não garante sua inclusão na soma.

Pesar todos os componentes e o rotor completo. Só então registrar margem, ajustar contrapesos e recalcular o desbalanceamento admissível. Não reduzir margens estruturais nem aumentar o teto para acomodar componentes não medidos.

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

## Histórico de 03/09/2026 — disposição dos 30 achados

**Registro histórico, não instrução vigente.** Os itens 9, 14 e 22 abaixo foram corrigidos novamente na revisão de 08/09; consultar especificação §10, esquema §5 e plano de ensaios D.

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
| B'3 | Canal do LED em degrau | **ratificado por Pedro em 03/09:** canal único 12,4 × 2,0, parede local 2,8 numa faixa de 14,4, piso 0,8 em ponte de 12,4. O degrau da spec §5.1 só funcionaria com a fita de cabeça para baixo |
| B'8 | Eletrônica para LiFe | esquema 05 e glossário atualizados: corte em 5,8 V pelo buck, carregador em modo LiFe |
| C1 | Módulo hall HW-477 no rotor | decidido: A3144 nu no bolso do cubo, pull-up para 3,3 V |
| E1 | Sulco de fiação reduz a seção do braço | anotado na spec §5.2 |
| E2 | Planos de balanceamento reais | anotados na spec §5.6 e no plano de ensaios (C) |
| E3 | Energia do painel solto | um par só, na spec, no README e nos parâmetros. **7,4 → 7,9 J pela revisão de 03/09, item 26** (o teto de massa é 44,5 g, não os 42,1 estimados) |
| E4 | Potência na fonte | unificada em 14,4 W na spec §10 |
| E5 | Taxa de dados | 15,4 Mbit/s a 1800 RPM na spec §6.2 |
| E6 | Raio do hall no §6.3 | r = 29, azimute 20°; pulso refeito |
| E7 | Lista truncada no §6.3 | completada |
