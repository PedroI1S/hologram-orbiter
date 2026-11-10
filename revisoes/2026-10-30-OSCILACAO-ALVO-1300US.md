# Relato de oscilação na aceleração até 1300 µs

Relato de Pedro em 30/10/2026, após gravação da faixa 1150–1350 µs:

- Em alvo de 1200 µs, o motor girou bem, basicamente sem oscilação percebida.
- Ao tentar 1300 µs, surgiu oscilação durante a aceleração e ela não cessou
  no intervalo observado, obrigando a interromper o ensaio.
- O operador suspeita de passagem por ressonância; a hipótese não foi confirmada.

Condições herdadas da sessão: rotor de 179,5 g sem circuito, torre maciça em
PETG sem furo Ø22 e fonte ajustada a 10,4 V. Não foram informados RPM medidos,
amplitudes, frequência da oscilação, tensão efetiva durante o giro, duração da
observação, perfil selecionado ou pulso exato no início da oscilação. Ainda
não foi confirmado se o alvo de 1300 µs chegou a ser atingido e mantido.

O registro `esc_blheli_s_2026-10-30/registro.md` documenta Startup Power de
0,75 e direção Reversed gravados no ESC; a configuração antiga de 0,25 não
deve ser tomada como leitura atual. O sentido físico depois da alteração
continuava pendente nesse registro.

## Interpretação provisória

O modelo médio dá cerca de 611 RPM em 1200 µs e 1462 RPM em 1300 µs.
Na hipótese intermediária estrutural, a coincidência em 3× fica em cerca de
1176 RPM / 1263 µs. O trajeto até 1300 µs pode atravessá-la, mas a relação
pulso–RPM e a frequência natural são estimadas, não medidas.

A persistência relatada não comprova uma vibração livre gerada apenas na
travessia: a excitação pode continuar no alvo, pode haver outro modo ou
banda de resposta, folga, contato, movimento da fixação ou desbalanceamento.
Apenas para comparar a excitação de um mesmo desbalanceamento, se as RPM do
modelo forem corretas, a força em 1300 µs seria (1462/611)² ≈ 5,7 vezes a de
1200 µs. Isso não é uma previsão da amplitude de oscilação nem uma diagnose.

1200 µs é um ponto observado com baixa oscilação visual, não uma condição
qualificada por medição. A coluna sem marcação da tabela teórica não significa
faixa sem ressonância. Não concluir que aumentar a velocidade ou acelerar mais
rápido resolverá o problema. Preservar a inspeção estrutural e medir a resposta
a impacto com o motor desenergizado antes de novas tentativas de travessia.

## Correção posterior: ruído agudo sem rotação

Pedro corrigiu o relato de possível falha interna: **as bobinas não giraram**.
O episódio foi de **ruído agudo sem rotação do motor**. A conclusão anterior,
na conversa, de estator solto e necessidade de substituição não está sustentada
por esse relato corrigido. Não há confirmação de dano mecânico nem de motor
intacto; inspecionar antes de energizar novamente.

O operador questionou se Startup Power 0,75 seria excessivo. É uma hipótese,
não uma causa identificada. Esse parâmetro é uma escala relativa de potência
de partida e não porcentagem direta da potência nominal nem duração. A potência
real depende também do acelerador e da lógica do ESC. A ausência de giro com
ruído pode corresponder a partida sem sincronismo; conexão de fase deficiente,
restrição mecânica ou alimentação inadequada também precisam ser verificadas.
Não alterar várias configurações nem repetir partidas prolongadas para tentar
identificar a causa pelo som. O episódio anterior de oscilação em giro permanece
registrado separadamente e não teve sua causa determinada.
