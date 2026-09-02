# Pendências críticas antes da fabricação final

## 1. Medições físicas obrigatórias

Preencher [`MEDICOES_DE_ENTRADA.md`](MEDICOES_DE_ENTRADA.md) e transferir os
valores para `CAD/parameters.json`:

- campânula do motor 2212: quantidade de furos, PCD, diâmetro e rebaixo central;
- base do motor: padrão de furos e altura do conjunto até o Datum B;
- fita HD107S montada: largura, espessura máxima, comprimento e posição dos
  componentes;
- LiPo 2S: envelope, massa, conector e saída dos cabos;
- posições reais dos vents do motor.

Os STL atuais usam provisoriamente 4 furos Ø3,2 em PCD 19 mm. Esse padrão não é
universal entre motores “2212”.

## 2. Conflitos encontrados na especificação v2.1

### Contenção vertical insuficiente

Com o Datum B a 188 mm e o painel centrado 3 mm acima dele, o rotor ocupa
aproximadamente Z=87 a Z=295 mm. Um cilindro de 260 mm iniciado no solo termina
35 mm antes da ponta superior. É necessário definir uma destas soluções:

- aumentar a proteção para pelo menos 305 mm de altura, incluindo 10 mm de
  folga superior; ou
- baixar o Datum do rotor e revisar torre, motor, baia e visibilidade; ou
- elevar o cilindro com uma contenção estrutural fechando também a região
  inferior.

### Folga radial marginal

O raio estático é 134 mm. Com a deflexão prevista de 3,5 mm, chega a 137,5 mm;
o anel de Ø interno 280 mm deixa somente 2,5 mm radiais. Essa folga ainda precisa
absorver tolerância, empeno, batimento, erro de montagem e deformação transitória.
Revisar a contenção e validar dinamicamente em baixa rotação.

### Orçamento de massa incompatível

Os máximos publicados não fecham com o limite total: 3 painéis de 35 g, três
longarinas de 10 g e um cubo de 30 g somam 165 g antes da tampa. Portanto, o
limite “rotor ≤120 g” precisa ser redefinido ou os limites por peça precisam ser
reduzidos. O CAD não mascara essa divergência.

### Forças centrífugas publicadas

Para 1800 RPM, `ω = 188,50 rad/s` e `F = m·ω²·r`. Um painel de 35 g a 130 mm
resulta em aproximadamente 162 N, não ~80 N. Três painéis equivalem a cerca de
485 N, sem contar longarinas e demais massas. Recalcular todo o caso de carga
antes da FEA e do ensaio.

### Frequência da torre

A frase “8–10 Hz acima de 30 Hz” é matematicamente incorreta. A frequência pode
ser desejável por isolamento, mas não está acima de 30 Hz. Definir amortecimento,
condições de contorno e faixa operacional antes da análise modal.

### Massa declarada dos coxins

Um cilindro maciço Ø16 × 8 mm tem somente 1,61 cm³. Mesmo antes de descontar o
furo, isso corresponde a aproximadamente 1,9 g em TPU de 1,20 g/cm³, e não
18–22 g por unidade. O CAD resulta em cerca de 1,85 g. Corrigir a tabela de massa
e qualquer cálculo modal que tenha usado o valor dez vezes maior.

## 3. Verificações ainda não executadas

- FEA estática do painel, boss, espiga e raiz da longarina;
- análise modal da longarina, torre e conjunto montado;
- fadiga para ciclos de operação previstos;
- retenção dos parafusos e porcas a 1800 RPM;
- balanceamento dinâmico instrumentado;
- teste de overspeed dentro de contenção certificada;
- validação térmica do ABS, motor, ESC e bateria;
- certificação de que a proteção retém a energia de falha.

Até concluir esses itens, a montagem é um protótipo geométrico e não uma máquina
liberada para operação.
