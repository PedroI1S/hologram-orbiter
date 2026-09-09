# Fiação, sensor de índice e montagem — Hologram Orbiter v3.0

Complementa a especificação (§6.3) com a rota física que o CAD implementa.
Cotas em mm; referenciais da spec §3. Atualizado para o cubo Ø92 e a baia
Ø82/Ø78 × 29 (regeneração de 03/09/2026).

## 1. Rota dos seis condutores por painel

Condutores por painel: 5 V e GND em AWG 24; DATA/CLK de entrada e de retorno em AWG 28. Chicote idêntico de seis condutores nos três painéis, com retorno do painel 3 sem conexão. Feixe estimado em 3,7 × 2,35 mm: medir a isolação e validar passagem real. A espiga **não é furada**: ela carrega os 158 N.

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
entrada ficam na ponta inferior, para cima; soldar as quatro entradas, dobrar sobre
a ponta da fita e mergulhar no bolso. Passar o feixe pela cavidade com um guia
rígido de 1 mm a partir do furo do item 7 (gravidade ajuda: o painel fica de pé).

**CG e massa do painel.** A estimativa anterior usava 1,2 g de fios em uma rota de quatro condutores. Pesar os seis condutores, a fita e ferragens e medir a distribuição real antes de usar o momento parasita da junta. Os 42,1 g do relatório são um subtotal nominal, não confirmação da montagem completa.

O retorno DATA/CLK é soldado à ponta superior da fita e retorna à baia pela cavidade e abertura da lâmina. Prender durante a passagem com o acesso disponível; validar o processo em cupom/peça antes de montar. Não confundir quatro terminais de entrada da fita com o chicote completo de seis vias.

## 2. Sensor de índice angular

| Item | Onde | Cota |
|---|---|---|
| Sensor hall A3144 **nu** (TO-92, dessoldado do módulo HW-477 — 06-PENDENCIAS C1) | face inferior do cubo, face marcada (serigrafada) para baixo | r = 29, azimute **20°** do rotor (braço 1 = 0°) |
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
   +6 na leitura de 12 mm). Os trilhos do berço ficam em Z = +9, a bateria em
   Z = 9…26 dentro dos 29 mm da baia.
5. Furos de provisão 4 × Ø3,2 em PCD 19 ficam sob a arruela: só servem com
   adaptador de hélice e com a arruela removida.

**Antes de comprar a porca, medir no motor**, a partir da face em que o cubo
assenta: altura do topo do colar e da ponta do eixo.

## 4. Sequência de montagem do rotor

1. Confirmar Hall em bancada: VCC=5 V, pull-up de 10 kΩ para 3,3 V, face marcada voltada ao ímã. Testar polaridade/entreferro/campo do motor antes de colar. Montar o sensor no bolso inferior e passar os terminais pelo rasgo.
2. Preparar os chicotes idênticos de seis condutores e os painéis; validar continuidade, isolamento e massa. Passar entrada/retorno pelos canais, sem furar a espiga. Parafusar os painéis com 2 × M3 × 40 e porcas capturadas.
3. Posicionar a eletrônica conforme `spider.bay_layout`: interface em +x, ESP32 em −x, capacitor em (22,5; −22), buck a 140° com folga de parede de 1,5 mm. O envelope/guia recua 1,2 mm em relação à revisão anterior. Conferir o módulo real e fixar; manter a bateria fora do berço por enquanto.
4. Fazer a correção estática inicial enquanto os alívios inferiores estão acessíveis. Usar os contrapesos calculados no relatório atual como ponto inicial, ajustando às massas reais. Registrar posições; a correção em dois planos exige o método instrumentado do bloqueador C.
5. Montar o cubo no eixo, assentar a arruela Ø20 × Ø8,5 × 2 e apertar a porca fina M6 conforme §3. **A bateria e a tampa ainda devem estar removidas**, para acesso axial à porca. Conferir eixo, rosca, giro livre e entreferro.
6. Instalar, reter e conectar a bateria no berço em Z local 9…26 (global 195…212). Conferir proteção elétrica, chave, fios afastados do eixo e retenção de todos os componentes.
7. Fechar a tampa com 2 × M3 autoatarraxantes nos postes y=±35. Pesar e reconciliar o conjunto completo; repetir o balanceamento após qualquer abertura, correção ou troca de componente.
8. Operação somente após resolver as pendências estruturais e instrumentais. Ensaio com contenção, base grampeada e operação remota; rampa nominal de RPM ≥12 s, limites e bloqueadores conforme plano 04.
