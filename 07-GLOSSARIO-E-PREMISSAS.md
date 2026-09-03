# Glossário e premissas — Hologram Orbiter v3.0

Duas coisas que faltavam: o vocabulário do projeto, e o registro honesto de
**o que foi medido, o que foi derivado e o que ainda é chute**.

---

## 1. Vocabulário

### Motor

**Campânula** *(bell)* — a parte **girante** do motor: a "sineta" de alumínio que
gira por fora, com os ímãs colados na face interna. É nela que a aranha se apoia
e dela que sai o eixo. **Não confundir com o cilindro de proteção.** Neste motor
ela é vazada, com 5 raios, e não tem furos roscados.

**Base do motor** — a parte **fixa**, onde saem os três fios de fase. É ela que
parafusa na chapa de alumínio, pelo padrão de 4 × M3 em retângulo 16 × 19 mm.

**Colar do eixo** — o trecho Ø8 × 5 mm do eixo entre a campânula e a rosca M6.
É ele que centra o cubo (furo Ø8 H8), e é por ele que a arruela precisa de furo
Ø8,5: uma arruela M6 assentaria no colar e a porca não apertaria o cubo.

**kv** — rotação por volt sem carga. 920 kv em 7 V dá 6440 RPM a vazio; a
1800 RPM o motor está a 26 % disso (base 7,4 V, como no resto do pacote; a 7 V daria 28 %).

**Kt** — constante de torque, `9,5493 / kv`. Diz quanto torque sai por ampère.

**ESC** — controlador do motor sem escovas. Recebe **sinal servo** (PWM de
1–2 ms), não tensão analógica.

**LVC** — corte por baixa tensão do ESC. Pode desligar o motor se ele achar que
a bateria acabou — problema real quando se opera a fonte em 6–7 V.

**Governor** — modo de malha fechada de rotação do ESC. É o que mantém a rotação
estável quando a carga varia.

### Rotor

**Aranha** — a peça central girante: cubo mais três braços radiais. Transmite o
torque do motor para os painéis.

**Longarina** — cada um dos três braços da aranha. Seção aerodinâmica de
15 × 6 mm.

**Espiga** *(tenon)* — a ponta retangular da longarina, 11 × 6 × 22 mm, que entra
no painel.

**Socket** — o encaixe correspondente dentro do painel, 11,2 × 6,2 × 22,5 mm.
A folga de 0,1 mm por lado e 0,5 mm de fundo é intencional: a carga radial vai
para os parafusos, não para o fundo da espiga.

**Boss** — a saliência do painel que envolve o socket e as torres dos parafusos.
Projeta-se para dentro, na direção do cubo.

**Carenagem** — a casca em gota que envolve o boss. Existe porque o boss nu
respondia por **mais da metade de todo o arrasto do rotor**.

**Baia de eletrônica** — o compartimento cilíndrico no cubo que abriga bateria,
controlador e conversores. Gira junto.

**Coxim** — isolador de vibração. **Não existe no projeto atual**: a peça herdada
tinha frequência natural de 400–620 Hz contra os ≤ 21 Hz que isolar 30 Hz exige.
A montagem é rígida.

**Contrapeso** — massa de correção do balanceamento, em dois planos: os
alívios da face inferior do cubo (r 17–36) e os copos da tampa (r = 34). O
layout da baia já pede 2,19 g de tungstênio no alívio de 180° e 0,87 g no
de 300°.

**Canal do LED** — o rebaixo de 12,4 × 2,0 mm na face externa do painel onde a
fita cola: PCB no fundo, LEDs rentes à face. Sob ele a parede engrossa de 2,0
para 2,8 mm numa faixa de 14,4, deixando o piso de 0,8.

### Geometria e fabricação

**Datum** — face ou eixo de referência a partir do qual outras cotas são medidas.
Datum D, por exemplo, é a altura do boss a partir da base do painel: 104 mm.

**Plano médio do painel** — o cilindro imaginário em **r = 100 mm** onde a lâmina
é centrada. É a cota que define quase toda a física do projeto.

**Cupom** — corpo de prova pequeno impresso antes do lote, para validar uma folga
específica. Custam minutos e evitam refazer painéis de 8 a 10 horas.

**Ponte** *(bridging)* — trecho que a impressora extruda no vazio, entre dois
apoios. O piso de 0,8 mm sob o canal do LED é uma ponte de 12,4 mm.

**Enrolamento** *(winding number)* — quantas vezes a superfície envolve um ponto.
Enrolamento **+1** é sólido normal; **−1** é uma casca invertida, que parece
válida em toda checagem topológica e imprime errado. Foi assim que os dois P0 do
painel passaram por três validadores.

**Watertight / não-manifold** — malha fechada, com cada aresta pertencendo a
exatamente duas faces. **Necessário, mas não suficiente**: uma casca invertida
passa nos dois testes.

### Dinâmica

**POV** — *persistence of vision*. O olho integra o que se move rápido; três
painéis a 30 rps varrem cada ponto do espaço 90 vezes por segundo.

**Índice / referência de fase** — o pulso, uma vez por volta, que diz ao ESP32
onde ele está apontando. Sem ele o firmware só conta tempo, e a imagem gira.

**Δm** — diferença de massa entre os três painéis. Limite atual: **0,084 g**.

**U** — desbalanceamento, em g·mm: massa desviada vezes o raio.

**G6.3** — grau de qualidade de balanceamento (ISO 1940). Define a excentricidade
admissível em função da rotação.

**A·Cd** — área frontal vezes coeficiente de arrasto. É o produto que importa;
encolher a área vale tanto quanto alisar a forma.

**Fluência** *(creep)* — deformação lenta sob carga **constante**. É o risco real
do painel: ABS a 12–14 MPa e 40–50 °C perde metade do módulo em ~100 h.

**Fadiga** — dano por carga **cíclica**. Aqui os ciclos são as partidas e paradas,
dezenas — não os 30 Hz de rotação. Num rotor de eixo vertical nem a força
centrífuga nem o peso mudam de direção em relação ao painel.

**Bloqueador** — critério que precisa passar antes de avançar de fase, com valor
numérico, método de medição e caminho de contingência.

### Elétrica

**Buck** — conversor abaixador. 6,6 V da bateria LiFePO4 para 5 V da fita.

**LiFePO4** *(LiFe)* — química de lítio-ferro-fosfato. 3,3 V por célula em vez
dos 3,7 do LiPo, curva de descarga plana, e não incha nem queima como LiPo.
**Carrega em modo LiFe, a 3,6 V/célula** — modo LiPo, a 4,2, destrói o pack.

**Nyloc** — porca com anel de nylon que trava por atrito. **Não cabe** no bolso
de 2,8 mm do painel (tem 4,0 mm); ali vai porca plana com trava química.

**Coletor aberto** *(open collector)* — saída que só puxa para o terra e precisa
de resistor de pull-up. É por isso que o A3144 pode ser alimentado em 5 V e ainda
entregar um sinal de 3,3 V seguro ao ESP32-C3.

**V_IH** — tensão mínima que uma entrada digital reconhece como nível alto. A
fita quer 3,5 V e o ESP32-C3 entrega 3,3 — daí o deslocador de nível.

---

## 2. Medido, derivado ou assumido

Nenhum número deste projeto deve ser usado sem saber de qual coluna ele veio.

| Grandeza | Valor | Origem | Estado |
|---|---|---|---|
| Motor, kv | A2212, 920 kv | datasheet | ✅ medido |
| Kt | 10,38 mN·m/A | `9,5493/kv` | ✅ derivado |
| Resistência efetiva | 0,221 Ω | ponto de catálogo com hélice | ⚠️ **envelope, não Rm** |
| Furação da base do motor | retângulo 16 × 19, 4 × M3 | datasheet | ✅ |
| Campânula | vazada, 5 raios, sem furos roscados | datasheet | ✅ |
| Eixo | colar Ø8 × 5 + rosca M6 × 7, sob cota total de 14 (a soma dá 12) | desenho cotado do datasheet | ⚠️ **medir topo do colar e ponta a partir da face de apoio** |
| Corpo do motor | 24 mm × Ø27,8 | medido | ✅ |
| **Chapa → Datum B** | **30 mm** (24 do corpo + 6 do cubo) | derivado | ✅ o cubo assenta nos raios da campânula; o colar entra no furo Ø8 |
| Arruela e porca do eixo | Ø20 × Ø8,5 × 2 em alumínio + M6 fina DIN 439B com trava química | projeto (o colar Ø8 não passa por arruela M6) | ⚠️ conferir espessura e altura reais |
| Fita HD107S | 12,0 × 2,0 mm, 144 LED/m | **medido** | ✅ |
| ESP32-C3 Super Mini | ~22 × 18 × 5 mm | em mãos | ✅ |
| ESC LittleBee Spring | **20 A contínuo, 25 A pico**, 25 × 13 mm, BLHeli_S em EFM8BB21 | datasheet | ✅ |
| ESC: governor | **não existe** em BLHeli_S | manual Rev16.x | ✅ |
| ESC: corte por baixa tensão | **não existe** em BLHeli_S — o LVC definido acima não se aplica a este ESC | manual Rev16.x | ✅ |
| ESC: tempo de rampa | **não existe** — só *startup power* (0,031–1,5) | manual Rev16.x | ✅ |
| Fonte de bancada | ajustável | em mãos | ✅ |
| Bateria LiFePO4 800 mAh | 58 × 30 × 17 mm, 50 g, **6,6 V nominal**, 2S, 20C | comprada | ✅ |
| Faixa útil da bateria | 7,2 V cheia · 6,6 no platô · **corte em 5,8** (dropout do buck) | derivado | ⚠️ |
| **Rth do motor** | **3,5 °C/W** | assumido | ❌ **o termopar decide** |
| **Cd da lâmina** | **0,35** | tabela de razão de finura | ❌ **o ensaio decide** |
| **A·Cd do boss** | **≤ 350 mm²** | estimativa por finura | ❌ |
| Módulo do ABS | 2 GPa | catálogo genérico | ❌ |
| Massa do painel montado | ~42,1 g | CAD (31,9 nu) + fita + ferragens | ⚠️ pesar |
| Massa do rotor | ~278,6 g | CAD + bateria medida + eletrônica de catálogo (15 g) + contrapeso planejado (3,1 g) | ⚠️ pesar; folga de 1,4 g |
| Eletrônica da baia | 5,5 + 3,0 + 2,0 + 2,5 + 2,0 g | catálogo | ❌ **pesar cada peça** |
| Sensor de índice | **A3144 nu**, TO-92, 0,2 g | dessoldado do módulo | ✅ |
| Gerador de sinal do ESC | Arduino ou gerador de bancada | em mãos | ✅ |

**Os três itens em negrito são o caso térmico inteiro.** Se o Rth real for 6 °C/W
em vez de 3,5, ou se o Cd vier em 0,50, os 43 °C viram 68 a 99. É por isso que o
Bloqueador B mede em vez de calcular, e por isso a ventilação é requisito e não
recomendação.

---

## 3. Duas coisas dos componentes que não podem passar batido

### Por que o sensor vai nu, e não na placa

Módulos de hall trazem pull-up próprio e conector. Dois motivos para não subirem
no rotor:

**Elétrico.** O pull-up do módulo vai para o VCC dele. Alimentado em 5 V, a saída
vai a 5 V — e o ESP32-C3 **não tolera 5 V** na entrada.

**Balanceamento.** Uma placa de 18 × 15 mm pesa 1,5 a 2,5 g. A r = 29 mm isso
vale 43 a 72 g·mm, contra os **8,4** admissíveis: **5 a 9 vezes fora**. O A3144 nu,
em TO-92, pesa 0,2 g e vale 5,8 g·mm.

O bolso do CAD tem 4,8 × 3,6 × 1,7 mm, dimensionado para o TO-92. Dessolde o
sensor e monte-o nu, com o pull-up de 10 kΩ para **3,3 V** do esquema.

### A rampa e o governor não vêm do ESC

O manual do BLHeli_S Rev16.x lista todos os parâmetros programáveis: *startup
power*, *commutation timing*, *demag compensation*, direção, beeps, *programming
by TX*, min/max/center throttle, proteção térmica, *low RPM power protect* e
*brake on stop*.

**Não há governor. Não há corte por baixa tensão. Não há tempo de rampa.**

Três consequências:

1. O corte por baixa tensão que estava como pendência **não existe** — item
   encerrado.
2. A **rampa de ≥ 8 s vem do gerador de sinal**, não do ESC. Isso torna o gerador
   ainda mais obrigatório.
3. Se a imagem "respirar", a correção **não** é modo governor — e provavelmente
   não será preciso: a inércia mantém a variação entre voltas em 0,03 a 0,11 %,
   contra 0,14 % de orçamento.

Dois ajustes que valem para o nosso caso, e que o manual descreve:

- **Low RPM power protect = desabilitado.** A 1800 RPM estamos a 26 % da rotação
  a vazio, exatamente o regime que essa proteção limita. O manual diz que
  desabilitá-la "pode ser necessário para atingir potência plena em motores de
  baixo kv com tensão de alimentação baixa". Em troca, aumenta o risco de perda
  de sincronismo — por isso é ajuste de bancada, não de projeto.
- **Brake on stop = desabilitado.** O BLHeli_S usa *damped light* sempre, com
  frenagem regenerativa. Frear um rotor de 27,6 J contra uma fonte de bancada,
  que não afunda corrente, empurra a tensão do barramento para cima.

---

## 4. Dúvidas que ficaram, e por que não travam

| Dúvida | Por que não bloqueia |
|---|---|
| Assento útil da campânula | O aperto está decidido: arruela Ø20 × Ø8,5 a 0,6 N·m dá 500 N contra os 22 N necessários. Mesmo assentando só nos raios, sobra atrito. O desenho mostra a face plana. |
| Altura do conjunto motor | Corpo medido em 24 mm; Datum B = chapa + 30. Um erro de ±2 mm desloca o rotor em Z **sem afetar nada estrutural — mas leva junto o entreferro do hall**, que é nominalmente 2,5 mm e tem só ~30 % de margem de campo. ±2 mm ali põem o entreferro entre 0,5 e 4,5 mm, e a 4,5 o A3144 não comuta. **Meça o entreferro montado antes de colar o ímã** (pendência C8). |
| Colar e rosca do eixo | O desenho não fecha a soma (5 + 7 ≠ 14). A fixação vale nas duas leituras: porca fina de 3 mm sobre arruela de 2, sobram 3 mm de rosca com a ponta em 14 e 1 mm com 12. Medir antes de comprar a porca. |
| Polaridade do ímã | O A3144 é unipolar. Se não pulsar, inverta o ímã antes de suspeitar do firmware. |
| Campo do motor no sensor hall | Estático em relação ao sensor. Verificar com o motor montado, antes de colar. |
| Frequência natural da parte fixa | Com a massa no topo do tubo daria 63 Hz, mas o CG fica 31 mm acima dele: a conta corrigida dá **≈ 46 Hz** (plano de ensaios, C0). O que não se sabe é o balanço da base sobre a mesa, e o ensaio de impacto resolve em uma tarde. |

---

## 5. Onde cada número mora

| Se você precisa de… | Vá para |
|---|---|
| Uma cota | [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md) |
| A origem de uma grandeza física | §10 da especificação, e a tabela §2 acima |
| Um critério de aceite | [`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md) |
| O que o CAD mede na malha | `Hologram_Orbiter_v3_0/reports/ACEITACAO.md` |
| O que ainda falta | [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md) |
| Por que a v2.1 foi refeita | [`legado/00-AUDITORIA-E-INTEGRACAO-v2.1.md`](legado/00-AUDITORIA-E-INTEGRACAO-v2.1.md), arquivada |

**Regra que vale para tudo:** se um número aparece em dois documentos com valores
diferentes, o da especificação vence — e o outro é um erro a corrigir, não uma
alternativa.
