# Relato de partida e falha da aranha na frenagem

Relato recebido de Pedro em **27/10/2026**. A data do ensaio não foi informada.

## Observações relatadas

- O motor partiu facilmente com a rampa.
- Durante a **frenagem automática dentro da rampa de partida**, o corpo entrou
  em oscilação, conforme esclarecimento posterior do usuário nesta sessão.
- Um braço da aranha quebrou durante os testes.
- A ruptura ocorreu **junto ao cubo central**, na raiz do braço.
- A versão foi informada como **V3.0**; a revisão específica do CAD e a versão
  do firmware ainda não foram identificadas.
- A oscilação **pareceu lateral** ao usuário. Pela aparência da quebra, ele
  considera que uma solicitação **vertical** possa ter causado a ruptura.
  Essa interpretação é uma hipótese do usuário, ainda sem inspeção da fratura.
- A base estava parafusada a uma **chapa de madeira em apenas dois pontos
  opostos**, por falta de espaço. O usuário considera que essa montagem possa
  ter intensificado a vibração. A participação da fixação na falha ainda não
  foi determinada.

A sequência foi informada pelo usuário; ainda não há medições ou inspeção da
fratura registradas. O relato não identifica a causa da oscilação nem da ruptura.

## Dados ainda necessários

- Instante da frenagem automática na sequência e comandos registrados no log.
- Tensão efetiva, corrente, pulso e rotação antes de frear; tempo de desaceleração.
- Versão do firmware, parâmetros da rampa e configurações do ESC no ensaio.
- Posição e extensão da fratura na raiz, orientação da superfície rompida e
  relação com camadas, cunha de reforço, janela e sulco de fiação; confirmar
  a direção dos movimentos com registros do ensaio, se disponíveis.
- Configuração do rotor e massas montadas; posição dos dois parafusos,
  arruelas, aperto, contato sob a base, dimensões/espessura da chapa de madeira
  e fixação dessa chapa à bancada.
- Material, orientação, perímetros, preenchimento e condições de impressão da
  peça rompida; correspondência entre a peça e a revisão CAD vigente.

## Efeito sobre o estado do projeto

No firmware atual, `controle-motor/src/controller.rs` encerra o chute pelo
tempo e reduz automaticamente o pulso até o alvo (`end_kick`). Os valores
padrão em `config.rs` são 1400 → 1200 µs, a 42 µs/s, após chute de 2 s.
Esse é o primeiro trecho a conferir contra o log do ensaio, pois a versão
gravada e os parâmetros efetivamente usados ainda não foram confirmados.
A base não mede rotação nem vibração: limitar a inclinação do comando não
constitui verificação da resposta mecânica durante essa transição.

A dificuldade de partida observada em 19/10 permanece como histórico. O novo
relato é evidência de partida bem-sucedida com rampa na configuração ensaiada.
Isso não confirma que o perfil foi o chute modelado, nem demonstra 10 de 10
partidas ou atendimento aos limites de potência e rotação do bloqueador D.

A falha estrutural durante a frenagem automática da partida passa a ser a prioridade para retomada
dos ensaios. A pendência R02 na lista 06 e o bloqueador C do plano 04 registram
a investigação. Novos giros ficam suspensos até tratar o dano, inspecionar o
restante do conjunto e revisar a resistência da aranha e o procedimento de parada.

A estimativa de tração radial da aranha na especificação 01 §5.2 não constitui
validação das cargas durante a frenagem e a oscilação. Não é possível escolher
um reforço ou atribuir a causa a ressonância, desbalanceamento, frenagem do ESC
ou falha de impressão somente a partir deste relato.

A região prioritária de inspeção é a **ligação braço–cubo**, incluindo a cunha
inferior prevista no CAD e a seção efetivamente impressa. O local da ruptura
está identificado; ainda é preciso distinguir os esforços que a produziram.
Não há evidência suficiente para concluir que a causa foi flexão vertical.

A fixação em dois pontos opostos difere da orientação vigente do plano 04
de prender a base em três ou quatro abas. Ela passa a ser uma condição de
montagem relevante à investigação. Verificar, com o conjunto desenergizado,
se existe balanço em torno da linha dos dois parafusos, perda de contato da
base ou movimento da chapa de madeira em relação à bancada. Esses são pontos
de inspeção, não movimentos comprovados no ensaio. O material da chapa, por
si só, não identifica sua rigidez nem explica a ruptura.

A revisão deve abranger toda a cadeia de apoio: base → parafusos → chapa de
madeira → bancada. Corrigir a fixação é necessário para retomar a configuração
de ensaio prevista, mas não demonstra que a aranha resistirá nem encerra a R02.

Preservar a peça rompida e as superfícies de fratura para inspeção. Este registro
atualiza documentos e comentários; preserva CAD, parâmetros de cálculo,
comportamento do firmware e configurações do ESC.
