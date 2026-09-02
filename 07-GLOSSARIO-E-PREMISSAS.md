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

**kv** — rotação por volt sem carga. 920 kv em 7,4 V dá 6808 RPM a vazio.

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

**Contrapeso** — massa de correção do balanceamento, em dois planos.

### Geometria e fabricação

**Datum** — face ou eixo de referência a partir do qual outras cotas são medidas.
Datum D, por exemplo, é a altura do boss a partir da base do painel: 104 mm.

**Plano médio do painel** — o cilindro imaginário em **r = 100 mm** onde a lâmina
é centrada. É a cota que define quase toda a física do projeto.

**Cupom** — corpo de prova pequeno impresso antes do lote, para validar uma folga
específica. Custam minutos e evitam refazer painéis de 8 a 10 horas.

**Ponte** *(bridging)* — trecho que a impressora extruda no vazio, entre dois
apoios. O piso de 0,8 mm sob o rasgo dos LEDs é uma ponte de 5,4 mm.

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

**Buck** — conversor abaixador. 7,4 V da bateria para 5 V da fita.

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
| Eixo | M6, 14 mm de saliência | datasheet | ⚠️ conferir com paquímetro |
| Altura do conjunto motor | 30 mm (24 do corpo + 6 do cubo) | derivado do datasheet | ⚠️ |
| Fita HD107S | 12,0 × 2,0 mm, 144 LED/m | **medido** | ✅ |
| ESP32-C3 Super Mini | ~22 × 18 × 5 mm | em mãos | ✅ |
| ESC | 15 A, rampa configurável | declarado pelo fornecedor | ⚠️ governor e LVC a confirmar |
| Fonte de bancada | ajustável | em mãos | ✅ |
| Bateria | até 67 × 30 × 20 mm | envelope da baia | ❌ **a comprar** |
| **Rth do motor** | **3,5 °C/W** | assumido | ❌ **o termopar decide** |
| **Cd da lâmina** | **0,35** | tabela de razão de finura | ❌ **o ensaio decide** |
| **A·Cd do boss** | **≤ 350 mm²** | estimativa por finura | ❌ |
| Módulo do ABS | 2 GPa | catálogo genérico | ❌ |
| Massa do painel montado | ~42,8 g | CAD + fita + ferragens | ⚠️ pesar |
| Massa do rotor | ~273 g | soma do CAD e não-impressos | ⚠️ pesar |

**Os três itens em negrito são o caso térmico inteiro.** Se o Rth real for 6 °C/W
em vez de 3,5, ou se o Cd vier em 0,50, os 43 °C viram 68 a 99. É por isso que o
Bloqueador B mede em vez de calcular, e por isso a ventilação é requisito e não
recomendação.

---

## 3. Dúvidas que ficaram, e por que não travam

| Dúvida | Por que não bloqueia |
|---|---|
| Assento útil da campânula | O aperto está decidido: arruela Ø20 a 0,6 N·m dá 500 N contra os 22 N necessários. Mesmo assentando só nos raios, sobra atrito. |
| Altura do conjunto motor | Derivada do datasheet em 30 mm. Um erro de ±2 mm desloca o rotor em Z sem afetar nada estrutural. |
| Rosca do eixo | ~6 mm de engate livre acima do cubo, suficiente para M6. Conferir na montagem. |
| Polaridade do ímã | O A3144 é unipolar. Se não pulsar, inverta o ímã antes de suspeitar do firmware. |
| Campo do motor no sensor hall | Estático em relação ao sensor. Verificar com o motor montado, antes de colar. |
| Frequência natural da parte fixa | O tubo dá 63 Hz. O que não se sabe é o balanço da base sobre a mesa, e o ensaio de impacto resolve em uma tarde. |

---

## 4. Onde cada número mora

| Se você precisa de… | Vá para |
|---|---|
| Uma cota | [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md) |
| A origem de uma grandeza física | §10 da especificação, ou §6 da auditoria |
| Um critério de aceite | [`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md) |
| O que ainda falta | [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md) |
| Por que a v2.1 foi refeita | [`00-AUDITORIA-E-INTEGRACAO-v2.1.md`](00-AUDITORIA-E-INTEGRACAO-v2.1.md) |

**Regra que vale para tudo:** se um número aparece em dois documentos com valores
diferentes, o da especificação vence — e o outro é um erro a corrigir, não uma
alternativa.
