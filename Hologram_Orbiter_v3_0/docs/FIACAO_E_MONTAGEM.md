# Fiação, sensor de índice e montagem — Hologram Orbiter v3.0

Complementa a especificação (§6.3) com a rota física que o CAD implementa.
Cotas em mm; referenciais da spec §3.

## 1. Rota dos quatro condutores por painel

Condutores por painel: 5 V e GND em AWG 24, DATA e CLK em AWG 28 (feixe de
~4,6 × 3,2 mm). A espiga **não é furada**: ela carrega os 158 N.

| Trecho | Peça | Feature no CAD | Cota |
|---|---|---|---|
| 1. Saída da baia | aranha | janela na parede do anel Ø70, lado de fuga do braço, fora do poste da tampa | r 32,5–36 · y −9,5…−5 · Z 0,8–5,8 |
| 2. Topo da raiz | aranha | bolso largo na face superior da concordância | r 35,3–42 · y −9,5…0 · piso Z 2,3 |
| 3. Braço | aranha | sulco na face superior, lado de fuga | r 42–70 · y −4,4…0 · piso Z 2,3 (≈3 mm de profundidade) |
| 4. Ombro | — | os fios sobem 3 mm em ar livre nos 4 mm finais do braço e passam sobre o topo da luva (Z 5,1) | r 70–74 |
| 5. Entrada na carenagem | painel | janela no flanco plano da carenagem, acima da luva | y −7,4…−2,6 · z 5,4–10 (referencial do painel) |
| 6. Câmara traseira | painel | espaço livre atrás das torres, entre a alma central (y = 0) e a cauda | y < −1,2 |
| 7. Entrada na cavidade | painel | furo na parede interna da lâmina, ao lado da torre externa | y −6,2…−2,6 · z 6–9,5 |
| 8. Descida | painel | cavidade oca; cada diafragma tem um vão de 4 mm (y −1,5…2,5) | z +6 → −98,5 |
| 9. Saída para a fita | painel | bolso passante 8 × 3,5 mm abaixo do batente da fita | z −102…−98,5 |

Fixação dos fios no sulco do braço: adesivo (CA ou epóxi) ou fita Kapton. A
força centrífuga puxa o feixe **ao longo** do sulco, não para fora dele.

**Montagem da fita.** Inserir a fita pelo topo do canal (aberto) e deslizar
até os ombros do bolso em Z = −98,5. Os pads de entrada ficam na ponta
inferior, para cima; soldar os quatro fios, dobrar sobre a ponta da fita e
mergulhar no bolso. Passar o feixe pela cavidade com um guia rígido de 1 mm a
partir do furo do item 7 (gravidade ajuda: o painel fica de pé).

**Consequência no CG do painel.** A peça em ABS tem CG em z = −0,02 mm (regra 2
da spec atendida). Com fita (6,2 g) e ~1,2 g de fios descendo até a ponta, o CG
do conjunto cai ~1,1 mm abaixo do centro da junta, o que dá um momento
parasita de ~0,16 N·m sobre os dois M3 (separados 10 mm): ~16 N de diferença
entre eles. Aceitável; anotar.

## 2. Sensor de índice angular

| Item | Onde | Cota |
|---|---|---|
| Sensor hall (TO-92) | face inferior do cubo, face sensível para baixo | r = 29, azimute 30° do rotor (braço 1 = 0°) |
| Terminais | rasgo 4,8 × 1,4 subindo até a baia | r ≈ 27,3–28,7 |
| Ímã Ø4 × 2 | topo do poste `06_poste_ima_ABS` | r = 29, azimute 30° da base (+x = 0°) |
| Entreferro | | 2,5 mm (poste termina em Z = 177,5; Datum A em Z = 180) |
| Poste | aba presa sob o parafuso M4 da flange em r = 20, 45° | altura 21,5 mm sobre a chapa |

**Fase:** o pulso ocorre quando o **braço 1 está alinhado com +x da base**
(mesmo azimute do poste). Como o giro é anti-horário visto de cima, o braço 1
passa pelo azimute 30° da base 1/12 de volta depois do pulso.

O sensor alimenta o ESP32 do rotor diretamente. Nada de sinal cruzando o
entreferro além do campo do ímã.

## 3. Fixação do rotor no eixo

1. Arruela M6 DIN 125 (1,6 mm) no rebaixo Ø13 × 2 do cubo.
2. Porca M6 autotravante baixa (DIN 985, 6 mm). **Não usar a porca cônica.**
3. Topo da porca em Z = +5,6 sobre a face superior do cubo; os trilhos do berço
   ficam em Z = +6, a bateria em Z = 6…19 dentro dos 20 mm da baia.
4. Furos de provisão 4 × Ø3,2 em PCD 19 (a confirmar) para parafusar a aranha
   com arruela Ø20 e torque de 0,6 N·m; os furos em PCD 19 ficam de reserva se
   vazado.

## 4. Sequência de montagem do rotor

1. Sensor hall no bolso inferior, terminais pelo rasgo; fixar com epóxi.
2. Fios dos três painéis: passar pelas janelas da baia, bolsos das raízes e
   sulcos dos braços; deixar 60 mm de sobra na ponta do braço.
3. Bateria no berço (deitada ao longo de y), ESP32 e regulador nas faixas
   laterais (x = 17…25). Chave e conector de carga sob a janela da tampa.
4. Painéis: encaixar a espiga no socket (0,1 mm/lado, 0,5 mm de fundo), passar
   os fios pela janela da carenagem, furo da lâmina e cavidade, soldar na fita.
   Parafusar 2 × M3 × 40 com porca no bolso hexagonal da base da torre.
5. Pesar os três painéis montados: Δm ≤ 0,091 g. Corrigir com massa adesiva nos
   alívios inferiores do cubo (plano 1) e nos copos da tampa (plano 2).
6. Tampa: 2 × M3 autoatarraxantes nos postes Ø2,8.
7. Cubo no eixo com arruela + porca baixa; conferir o giro livre e o
   entreferro do hall (2–3 mm) com o poste do ímã montado.
8. Cilindro na canaleta da base (entra 3 mm, 0,2 mm de folga por lado) e a
   tampa `07` por cima, com a canaleta dela recebendo a borda superior. Só
   girar com a tampa colocada: ela é a contenção axial e o único caminho de ar.
