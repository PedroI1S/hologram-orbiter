# Testes breves do motor sem aranha — 30/10/2026

Autorização explícita de Pedro para testes pela ESP32 conectada, motor
energizado e sem aranha ou carga acoplada. O motor foi informado como
mecanicamente livre, sem raspagem ao girar à mão.

## Procedimento e dados

Foi encerrado com SIGINT o monitor espflash que ocupava a serial. Controle
por pyserial a 115200 baud na porta `/dev/cu.usbserial-A5069RR4`.
Cada abertura da serial provocou um boot inicial observado; aguardou-se o fim
da armação e confirmou-se `PARADO` antes de configurar e enviar a partida.
Perfil linear, rampa de 3 s, sem mudança no firmware ou parâmetros do ESC.
O último registro de leitura do ESC informa Startup Power 0,75.

Duas tentativas, cada uma com 6 s desde o comando de partida, incluindo os
3 s de rampa e aproximadamente 3 s com pulso no alvo. Parada por `p` ao fim
de cada tentativa, repetida na saída do script; alvo restaurado para 1200 µs.
O script local possuía bloco `finally` para enviar parada e fechar a serial.

| Alvo | Evidência da ESP32 | Observação física de Pedro |
|---|---|---|
| 1160 µs | Rampa até 1160 µs em ~3 s; pulso de regime estável; sem reinício durante a tentativa | Giro intermitente |
| 1200 µs | Rampa até 1200 µs em ~3 s; pulso de regime estável; sem reinício durante a tentativa | Giro contínuo e regular |

Logs completos: [1160 µs](motor-sem-aranha-1160us.log) e
[1200 µs](motor-sem-aranha-1200us.log).
`REGIME`, `giro_s` e `pulso_us` são estados/estimativas do firmware, não
medidas da velocidade ou da forma de onda no pino. Não há retorno de RPM,
corrente, temperatura ou ruído. O giro físico foi confirmado pelo operador.

## Conclusão limitada

A intermitência em 1160 µs, com comando estável e funcionamento regular em
1200 µs, é compatível com comando insuficiente para sustentar o giro/sincronismo
nessa região. 1160 µs ficam 12 µs acima do PPM mínimo de 1148 µs, ~1,75% da
faixa de comando; 1200 µs representam ~7,60%. Não são porcentagens de RPM
nem de potência.

Não há evidência nestes testes para condenar o motor ou afirmar que o Startup
Power 0,75 é excessivo. O teste não exclui defeito intermitente, aquecimento,
perda de fase sob carga ou problema de rolamento em outras condições. Também
não qualifica o motor com o rotor de 179,5 g nem explica a oscilação anterior
na aceleração a 1300 µs. As RPM da tabela com carga não se aplicam ao motor nu.

Ao terminar: parada confirmada na serial, pulso de parada de aproximadamente
1000 µs, perfil linear e alvo de 1200 µs. Porta serial fechada, sem retomada
automática. Nenhuma tentativa acima de 1200 µs foi executada.

## Teste adicional: transição de 1200 para 1300 µs

Após solicitação de continuar o diagnóstico, foi executado um teste adicional
sem a aranha, sem alterar Startup Power ou firmware. Partida linear em 1200 µs,
6 s desde a partida (3 s de rampa e ~3 s no alvo), seguida de alvo de 1300 µs.
A inclinação de ajuste vigente levou ~5,9 s nessa transição. O comando ficou
em 1300 µs por ~3 s, e a parada por `p` foi enviada 15 s após a partida.
Alvo restaurado para 1200 µs, `PARADO` confirmado e serial fechada.

A serial não registrou reinício durante o acionamento. Isso não mede giro nem
integridade elétrica do motor/ESC. Pedro confirmou giro regular até 1300 µs, porém com ruído adicional ao
barulho comum do motor. A natureza e a origem desse ruído não foram medidas.

Log: [transição 1200–1300 µs](motor-sem-aranha-transicao-1200-1300us.log).
A frase anterior “Nenhuma tentativa acima de 1200 µs” descreve somente os dois
primeiros testes e foi superada por esta tentativa adicional.

A ausência de parada sem carga favorece uma falha dependente de carga ou de
condições do ensaio anterior, mas não exclui motor/ESC com defeito que só
apareça sob esforço. Ruído adicional ainda requer inspeção; não se qualificou
o motor nem se autorizou remontagem por este resultado. Não foram executados
novos testes acima de 1300 µs ou alterados parâmetros do ESC.
