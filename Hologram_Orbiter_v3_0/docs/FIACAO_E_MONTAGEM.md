# Fiação, sensor de índice e montagem — Hologram Orbiter v3.0

Complementa a especificação (§6.3) com a rota física que o CAD implementa.
Cotas em mm; referenciais da spec §3. Atualizado para o cubo Ø92 e a baia
Ø82/Ø78 × 26 (regeneração de 03/09/2026).

## 1. Rota dos quatro condutores por painel

Condutores por painel: 5 V e GND em AWG 24, DATA e CLK em AWG 28 (feixe de
~4,6 × 3,2 mm). A espiga **não é furada**: ela carrega os 158 N.

| Trecho | Peça | Feature no CAD | Cota |
|---|---|---|---|
| 1. Saída da baia | aranha | janela na parede do anel Ø82/Ø78, lado de fuga do braço, longe dos postes da tampa (que ficam em y = ±35) | r 38,5–42 · y −10…−5,5 · Z 0,8–5,8 |
| 2. Topo da raiz | aranha | bolso largo na face superior do alargamento da raiz | r 41,3–48 · y −10…0 · piso Z 2,3 |
| 3. Braço | aranha | sulco na face superior, lado de fuga | r 48–70 · y −4,4…0 · piso Z 2,3 (≈3 mm de profundidade) |
| 4. Ombro | — | os fios sobem 3 mm em ar livre nos 4 mm finais do braço e passam sobre o topo da luva (Z 5,1) | r 70–74 |
| 5. Entrada na carenagem | painel | janela no flanco plano da carenagem, acima da luva | y −7,4…−2,6 · z 5,4–10 (referencial do painel) |
| 6. Câmara traseira | painel | espaço livre atrás das torres, entre a alma central (y = 0) e a cauda | y < −1,2 |
| 7. Entrada na cavidade | painel | furo na parede interna da lâmina, ao lado da torre externa | y −6,2…−2,6 · z 6–9,5 |
| 8. Descida | painel | cavidade oca; cada diafragma tem um vão de 4 mm (y −1,5…2,5) | z +6 → −98,5 |
| 9. Saída para a fita | painel | bolso passante 8 × 3,5 mm abaixo do batente da fita | z −102…−98,3 |

A cunha de 45° sob a raiz do braço (r 46–53) fica **abaixo** do sulco: não
interfere na rota. Fixação dos fios no sulco: adesivo (CA ou epóxi) ou fita
Kapton. A força centrífuga puxa o feixe **ao longo** do sulco, não para fora dele.

**Montagem da fita.** Inserir a fita pelo topo do canal (aberto) e deslizar
até os ombros do bolso em Z = −98,5, com o adesivo do PCB colado no fundo do
canal de 12,4 × 2,0; os LEDs ficam rentes à face externa. Os pads de
entrada ficam na ponta inferior, para cima; soldar os quatro fios, dobrar sobre
a ponta da fita e mergulhar no bolso. Passar o feixe pela cavidade com um guia
rígido de 1 mm a partir do furo do item 7 (gravidade ajuda: o painel fica de pé).

**Consequência no CG do painel.** A peça em ABS tem CG em z = −0,15 mm (regra 2
da spec atendida). Com fita (6,2 g) e ~1,2 g de fios descendo até a ponta, o CG
do conjunto cai ~1,2 mm abaixo do centro da junta, o que dá um momento
parasita de ~0,18 N·m sobre os dois M3 (separados 10 mm): ~18 N de diferença
entre eles. Aceitável; anotar.

## 2. Sensor de índice angular

| Item | Onde | Cota |
|---|---|---|
| Sensor hall A3144 **nu** (TO-92, dessoldado do módulo HW-477 — 06-PENDENCIAS C3) | face inferior do cubo, face sensível para baixo | r = 29, azimute **20°** do rotor (braço 1 = 0°) |
| Terminais | rasgo 4,8 × 1,4 subindo até a baia, debaixo da placa de interface (onde está o pull-up) | r ≈ 27,3–28,7, azimute 20° |
| Ímã Ø4 × 2 | topo do poste do `06_suporte_ima_ABS` | r = 29, azimute **20°** da base (+x = 0°) |
| Entreferro | | 2,5 mm (poste termina em Z = 177,5; Datum A em Z = 180) |
| Suporte | arco sob **dois** parafusos M4 da flange (r = 20, −45° e +45°), garfo aberto para dentro, braço radial até o poste | aba de 2,5 mm; poste de 21,5 mm sobre a chapa; arco a 4,6 mm da campânula |

**Fase:** o pulso ocorre quando o **braço 1 está alinhado com +x da base**
(sensor e ímã no mesmo azimute, 20°). Como o giro é anti-horário visto de cima,
o braço 1 passa pelo azimute 20° da base 1/18 de volta depois do pulso. Com dois
parafusos a aba não gira: a referência de fase não depende do aperto de um
único M4.

Os fios de fase do motor devem sair pelo lado **oposto** ao arco do suporte
(−x): o arco cobre 116° em torno de +x, a 2,5 mm de altura sobre a chapa.

O sensor alimenta o ESP32 do rotor diretamente (5 V, pull-up de 10 kΩ para
3,3 V). Nada de sinal cruzando o entreferro além do campo do ímã.

## 3. Fixação do rotor no eixo

O desenho do motor mostra um **colar Ø8 × 5 mm** sob a rosca (7 mm acima da
campânula se o ressalto de 2 mm existir). O cubo tem 6 mm: o colar termina
acima do fundo de qualquer rebaixo, e uma arruela M6 assentaria no aço do
colar — a porca apertaria o colar, não o cubo. Daí a pilha abaixo, válida nas
duas leituras do desenho.

1. O cubo desce pelo colar (furo Ø8 H8) e assenta nos raios da campânula.
2. **Arruela Ø20 × Ø8,5 × 2 mm em alumínio** (cortada da chapa da R01; o furo
   passa pelo colar) direto no topo do cubo, sem rebaixo. 1,9 MPa no ABS a
   0,6 N·m.
3. **Porca M6 fina DIN 439B (3 mm) com Loctite 243**, a 0,6 N·m. **Não usar a
   porca cônica nem a autotravante baixa de 6 mm**: com a rosca acabando em
   12–14 mm, a de 6 mm terminaria no fim do eixo.
4. Pilha sobre o topo do cubo: arruela 0–2, porca 2–5, ponta do eixo em +8 (ou
   +6 na leitura de 12 mm). Os trilhos do berço ficam em Z = +6, a bateria em
   Z = 6…23 dentro dos 26 mm da baia.
5. Furos de provisão 4 × Ø3,2 em PCD 19 ficam sob a arruela: só servem com
   adaptador de hélice e com a arruela removida.

**Antes de comprar a porca, medir no motor**, a partir da face em que o cubo
assenta: altura do topo do colar e da ponta do eixo.

## 4. Sequência de montagem do rotor

1. Sensor hall nu no bolso inferior, terminais pelo rasgo; fixar com epóxi.
   Conferir a polaridade do ímã antes de colar (06-PENDENCIAS C4).
2. Fios dos três painéis: passar pelas janelas da baia, bolsos das raízes e
   sulcos dos braços; deixar 60 mm de sobra na ponta do braço.
3. Eletrônica conforme o layout `spider.bay_layout` (render
   `exports/preview/montagem_baia.png`), tudo elevado em pilares de 6 mm para
   deixar o piso livre aos feixes:
   - **placa de interface** (74AHCT125, pull-up 10 k, divisor 150k/47k,
     polyfuse, chave slide, JST-XH) em +x, x 19,5…34,5 · y −5…15, sob a janela
     da tampa; os terminais do hall sobem debaixo dela;
   - **ESP32-C3** em −x, x −36…−18 · y ±11,25, USB-C para −y;
   - **buck mini560** em pé na ranhura da parede a 140°, indutor para dentro;
   - **capacitor 1000 µF** em pé na cerca em (22,5, −22);
   - bateria LiFe (58 × 30 × 17, 50 g) no berço, deitada ao longo de y, por
     último.
   Desbalanceamento nominal do conjunto: ~73 g·mm a ~13°. **Antes de fechar a
   tampa**, colar ~2,2 g de massa de tungstênio na ponta externa do alívio de
   180° (face inferior do cubo, r ≈ 33) e refinar na pesagem.
4. Painéis: encaixar a espiga no socket (0,1 mm/lado, 0,5 mm de fundo), passar
   os fios pela janela da carenagem, furo da lâmina e cavidade, soldar na fita.
   Parafusar 2 × M3 × 40 com porca plana no bolso hexagonal da base da torre e
   trava química.
5. Pesar os três painéis montados: Δm ≤ 0,084 g. Corrigir com massa adesiva nos
   alívios inferiores do cubo (plano 1, r 17–36) e nos copos da tampa (plano 2,
   r = 34).
6. Tampa: 2 × M3 autoatarraxantes nos postes Ø2,8, em y = ±35.
7. Cubo no eixo com a arruela Ø20 × Ø8,5 e a porca fina com Loctite (§3);
   conferir o giro livre e o entreferro do hall (2–3 mm) com o suporte do ímã
   montado.
8. **Contenção de ensaio** (caixa fechada, chapa ou tela) e base grampeada pelas
   abas antes de girar. O invólucro definitivo está fora de escopo; o cilindro
   encomendado, se usado, assenta na canaleta de provisão da base.
