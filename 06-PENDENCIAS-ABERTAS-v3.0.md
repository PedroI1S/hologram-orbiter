# Pendências abertas — Hologram Orbiter v3.0

O que **falta**, depois da regeneração do CAD de 03/09/2026 (rev. 3.0.2) e da
rodada de higiene documental do mesmo dia. Os códigos (B'1, C2, D1…) são os da
revisão de 02/09 e continuam valendo; o que fechou está resumido no fim.

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
Desbalanceamento nominal **73 g·mm a 14°**, corrigido com **2,2 g de tungstênio
no alívio de 180°**; o rotor fecha em **274,3 g**, 5,7 g abaixo do limite.

**Falta:** pesar cada componente real e atualizar `mass_g`; as posições são
parâmetros. Um XL4015 (~18 g) no lugar do mini560 não fecha.

### D2 · Ensaio de impacto na base

Antes de montar o motor: base impressa na bancada, MPU6050 junto à torre, toque
seco no topo, FFT do decaimento. Medir grampeada pelas abas e solta.

O tubo Ø30 × 4 × 150 com 322 g no topo dá k ≈ 50 N/mm e **fn ≈ 63 Hz**, folgado
contra os 30 Hz de excitação. O que essa conta não cobre é o **balanço da base
sobre a mesa**. Se vier **abaixo de 45 Hz**, o que cresce é a **nervura**, não
o pé: piso 100 % sólido num raio de 40 mm em torno da torre e 4 a 8 gussets da
torre para a parede da baia, que hoje não trabalha.

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

## Fechadas em 03/09/2026

| # | Item | Como fechou |
|---|---|---|
| A1 | Cascas invertidas nos furos M3 | reproduzido com traçado de raios (enrolamento −1 em x −18…−15,2 e −3,1…+3,1, 132 trechos ruins); `subtract_each()` subtrai um cortador por vez; agora 0 trechos ruins em todas as peças |
| A2 | Membrana no canal | não reproduzida; corrigida por construção (bolso invade o canal em 0,2) |
| B1 | Ombro da longarina | aerofólio termina em 74,0; raio medido na malha: 100,0 |
| B2 | Critérios de aceitação | 51 critérios, os geométricos medidos por traçado de raios no STL final |
| B3 | Cortador da flange | furos só na flange superior; piso sólido de Z = 0 a 12 sob eles |
| B4 | Poste do ímã | suporte sob os dois M4 de ±45°, garfo aberto para dentro, poste em r = 29, 20°; dois M4 passam a × 20 |
| B5 | Abas de grampo | 4 a 90° nos cantos da mesa (3 a 120° não cabem); furo Ø5 em r = 149 |
| B6 | `mass_limit_g` da base | 330; modelo com abas dá 321 |
| B7 | Tampa de invólucro | removida (fora de escopo, confirmado em 03/09) |
| B8 | `validate_stl.py` | enrolamento por raios, faces coincidentes e membranas, nos 9 STL |
| B9 | Canal do LED | canal único 12,4 × 2,0, piso 0,80 medido — ver B'3 para a ratificação |
| B10 | Baia de eletrônica | cubo Ø92, baia Ø82/Ø78 × 26; rasgos r 41,5–45; alívios r 17–36; berço do pack LiFe; aranha 67,5 g |
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
| E3 | Energia do painel solto | um par só: 7,4 J a 18,9 m/s, na spec, no README e nos parâmetros |
| E4 | Potência na fonte | unificada em 14,4 W na spec §10 |
| E5 | Taxa de dados | 15,4 Mbit/s a 1800 RPM na spec §6.2 |
| E6 | Raio do hall no §6.3 | r = 29, azimute 20°; pulso refeito |
| E7 | Lista truncada no §6.3 | completada |
