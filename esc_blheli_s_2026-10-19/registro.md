# Registro da configuração do ESC e da partida com a peça — 19/10/2026

**Resultado:** Startup Power subiu de 0,125 para **0,25**, gravado e confirmado por releitura. Dos 112 bytes de configuração, só o de Startup Power mudou. Com a peça impressa no motor, a partida **não** saiu a 7,0 V com alvo de 1200 µs. Ela saiu com a fonte em **10,4 V e alvo de 1400 µs**; segundo o usuário, abaixo de 1400 µs não há partida. Em rotação plena a fonte caiu para **8,4 V a 2,48 A**. Na parada, a tensão do barramento subiu a **quase 20 V**.

## Motivo

Em 19/10, depois do primeiro giro sem rotor, a peça foi montada (gira livre à mão e embala). Com alvo de 1300 µs, 7,0 V e limite de 3 A, o motor só tremeu e zumbiu, com pico de 0,3 A na fonte. Sem a peça, o mesmo conjunto parte, então sinal, ESC e fases estão bons. É a falha de partida do bloqueador D do 04; a seção 8.3 do 05 manda o Startup Power "começar baixo e subir". O valor era 0,125 desde 16/10 (original 0,50).

## Alteração no ESC

| Parâmetro | Antes (gravado em 16/10) | Gravado e relido em 19/10 |
|---|---|---|
| Startup Power | 0,125 | **0,25** |

Os demais parâmetros foram relidos sem alteração: Motor Direction **Normal**, PPM Min/Max **1148/1832 µs**, Brake on stop desligado, Low RPM Power Protection desligado, Demag Low, Timing Medium, Temperature Protection 140 °C, Programming by TX ligado, Beep 40, Beacon 80, Beacon Delay 10 min.

- Leitura antes da escrita (18:31:13): os 112 bytes em 0x1A00 são idênticos à releitura de 16/10 (SHA-256 `0528d8f4…`).
- Write Settings: "Updating ESC 1 - finished" às 18:32:54. Bytes escritos: só o offset 9 (0x1A09) muda, **5 → 7**. A tabela do próprio configurador dá 0,25 = 7.
- Releituras: duas logo após a escrita (18:32:54 e 18:32:55) e um Read Settings novo (18:33:07). Nas três, só o offset 9 difere; os outros 111 bytes são idênticos. SHA-256 depois: `9c6244b3…`.
- Firmware e layout mantidos; nenhum firmware foi gravado no ESC; a aba de motores do configurador não foi usada.

## Montagem e procedimento da configuração

- A fonte de bancada estava indisponível nesse momento. O ESC foi alimentado pela bateria LiFePO4 2S 800 mAh, 6,5 V medidos em vazio, pelo cabo principal (o de balanceamento ficou de fora). Sem limite de corrente; na configuração o ESC consome poucos mA.
- As fases do motor estão soldadas no ESC. No lugar de desconectá-las, a peça impressa foi retirada do motor. Ao ligar a bateria, o ESC tocou os tons de inicialização pelo motor, sem giro.
- Arduino Uno R3 em `/dev/cu.usbserial-10`, com o passthrough corrigido de 16/10. Verificado antes por consultas MSP só de leitura (`msp-probe.json`): identidade simulada BTFL 4.3.0 / ARDU, comando 104 com 8 bytes (1000 µs nos quatro canais), comando 36 com 4 bytes, checksums válidos. Não foi regravado.
- Sinal do ESC no D3 do Uno, GND comum, Uno só pela USB, ESP32 desconectada.
- O navegador integrado do app bloqueou o script do ESC Configurator (`ERR_BLOCKED_BY_CLIENT`). Usado o Chrome com o ESC Configurator 0.32.1, operado pelo Claude in Chrome; a escrita foi feita depois da autorização explícita do usuário.
- A opção "Extended debugging" ficou ligada durante a sessão, para registrar os bytes, e foi desligada no fim. Porta fechada às 18:34:33.
- Sinal devolvido ao D25 da ESP32, com GND comum; Uno desconectado.

## Ensaio de partida com a peça

Condições: fonte de bancada de volta, partindo de 7,0 V com limite de 3 A. Peça montada, girando livre à mão. Contenção fechada, base presa, óculos. Firmware da ESP32 sem alteração (`3232a10`): alvo inicial 1200 µs, rampa de 12 s a partir de 1148 µs, teto de 1400 µs (estimado).

**Tentativa sem console.** O primeiro cabo USB só alimentava a ESP32, sem dados, então valeu o alvo padrão de 1200 µs, a 7,0 V. Houve três tentativas de cerca de 1 s com pausas de cerca de 1 s, cada uma mais forte que a anterior, porque a rampa sobe 4,3 µs/s. A terceira quase girou; depois o ESC bipou e parou de tentar. Pico abaixo de 1 A.

**Série com console** (`monitor-esp32-partidas.log`, `espflash monitor`; o monitor deixou a placa no carregador da ROM e foi preciso Ctrl+R). O tempo `t` é contado desde o reinício da placa. A coluna `giro_s` do registro conta o tempo desde o comando de partida, não a rotação: só o relato do usuário diz se a peça girou.

| Partida | t (s) | Alvo | Fim | Resultado (relato do usuário) |
|---|---|---|---|---|
| 1 | 16,6 | 1200 µs | parada pelo botão em 1200 µs, 27,4 s após o comando | sem partida |
| 2 | 71,5 | 1200 µs | parada pelo botão em 1200 µs, 34,8 s | sem partida |
| 3 | 133,5 | 1200 µs | parada pelo botão em 1200 µs, 12,4 s | sem partida |
| 4 | 163,2 | 1300 µs | parada pelo botão na rampa, em 1259 µs, 8,7 s | sem partida |
| 5 | 185,2 | 1400 µs | parada pelo botão na rampa, em 1344 µs, 9,3 s | sem partida |
| 6 | 210,1 | 1400 µs | parada pelo botão na rampa, em 1283 µs, 6,4 s | sem partida |
| 7 | 267,1 | 1400 µs | parada pelo botão na rampa, em 1318 µs, 8,0 s | sem partida |
| 8 | 292,0 | 1400 µs | regime em 1400 µs; parada pelo botão após 23,3 s | **girou** |

Ao longo da série, a fonte foi elevada de 7,0 V para 10,4 V; a tensão de cada partida de 1 a 7 não foi registrada. O usuário informou:

- partida com a fonte ajustada em **10,4 V** e alvo de **1400 µs**; abaixo de 1400 µs não parte;
- em rotação plena, a fonte **estabiliza em 8,4 V e 2,48 A** (cerca de 21 W); a queda de 10,4 para 8,4 V indica a fonte em limitação de corrente;
- na parada, a tensão **sobe a quase 20 V**.

Não informados: pulso exato em que a peça arrancou na partida 8, pico de corrente na partida, sentido de giro com a peça e temperatura depois do giro. A rotação não foi medida (sem tacômetro).

## Leitura dos resultados

**Sobretensão na parada.** É a regeneração prevista no 04 (bloqueador D, item 5, e regras de segurança): o BLHeli_S desacelera o motor devolvendo energia ao barramento, e a fonte de bancada não absorve corrente. Isso acontece mesmo com Brake on stop desligado, porque a parada do firmware leva o pulso a 1000 µs de uma vez. Quase 20 V passa do máximo de 4S (16,8 V) para o qual o ESC é vendido. O 04 já determina: "se for preciso frear de fato, use um resistor de descarga no barramento do ESC; nunca a fonte". **Antes de novas paradas a partir da rotação plena**, é preciso um grampo ou resistor de descarga no barramento do ESC, ou outra forma de absorver essa energia.

**Rotação.** Sem governor, o mesmo pulso gira mais rápido com mais tensão; o teto de 1400 µs foi estimado para 7,0 V. A estimativa abaixo usa o modelo do comentário do `CEILING_US` (`firmware/controle-motor/src/config.rs`): 1,96 V de força contraeletromotriz mais 4,95 A × 0,221 Ω a 1800 RPM, com corrente proporcional a ω² e o arrasto do rotor completo. Por ela, 1400 µs dão cerca de **1800 RPM a 8,4 V** e cerca de 2100 RPM se a fonte sustentasse 10,4 V. É só estimativa: não foi medida, e a peça montada pode ter arrasto diferente do rotor completo. Com limite de corrente maior, a rotação passaria de 1800 RPM.

**Faixa de tensão.** 10,4 V está fora da faixa de 6–7 V do 05 §8 e dos critérios do 04, que fixam o teto de 4,6 A a 7 V.

**Bloqueador D.** Continua aberto. Com 0,25, a peça não partiu a 7,0 V até 1200 µs. Partiu só com tensão mais alta e 1400 µs, e não foram feitas as 10 partidas de 12 s com medição de corrente. O item 2 do "Se falhar" do 04 manda reduzir a potência de partida; o que se observou aqui foi potência insuficiente (tremor, menos de 1 A), não perda de sincronismo por excesso.

## Próximos passos possíveis (não decididos)

- Resistor de descarga ou grampo de tensão no barramento do ESC antes de qualquer nova parada a partir da rotação plena.
- Voltar a 7,0 V e subir o Startup Power para 0,38 e, se preciso, 0,50 (o original).
- Medir a rotação com tacômetro antes de girar acima de 7,0 V ou acima de 1400 µs.

## Decisões de 20/10/2026

Tomadas pelo usuário a partir deste ensaio:

- **Fonte do ESC em 10–12 V**, com limite de corrente de ~3 A, no lugar de 6–7 V. Documentos 01 a 07 atualizados.
- **Partida com chute** no firmware da ESP32 da base (versão 0.2.0): subida de 1148 a 1400 µs em 3 s, chute de 2 s (0 a 5 s pelo console; a tecla `k` o encerra ao ver o rotor girar) e descida ao alvo, 1200 µs ao ligar, a 42 µs/s. A base não mede rotação, por isso o chute acaba pelo tempo ou pela tecla.
- **Teto de regime em 1320 µs**, estimado para 10–12 V (~1790 RPM a 12 V pelo modelo do `config.rs`); 1400 µs ficam só no chute, por tempo limitado. Medir com tacômetro.
- **Parada suave** (`d`): desce ao acelerador zero a 21 µs/s antes do pulso de parada. Espaço, `p` e o botão D33 continuam parando na hora.
- **Grampo ou resistor de descarga no barramento do ESC** obrigatório antes de novas paradas a partir da rotação plena (05 §8.2; 03; 04).

O firmware 0.2.0 passou nos testes da lógica no Mac e compila para a placa, mas ainda não foi gravado nem conferido na bancada.

**Vibração.** O usuário informou que o ensaio de vibração passou. Método, instrumento, rotação e amplitudes não foram registrados; o bloqueador C do 04 (picos a 1× e 2× da rotação, varredura de 600 a 1800 RPM) segue sem aprovação formal até esses dados entrarem.

## Arquivos

- `parametros-gravados.json`: parâmetros após a releitura.
- `esc1-config-antes-0x1a00.bin` e `.hex.txt`: 112 bytes lidos antes da escrita, iguais aos gravados em 16/10.
- `esc1-config-gravada-0x1a00.bin` e `.hex.txt`: 112 bytes confirmados após a escrita.
- `verificacao-gravacao.json`: comparação dos bytes, hashes e horários.
- `esc-configurator-log.txt`: log de depuração exportado pelo configurador (Save Debug Log), com leitura, escrita e releituras. Inclui as linhas de 16/10 que ainda estavam no navegador e uma conexão do usuário às 18:22, sem leitura do ESC.
- `msp-probe.json`: consultas MSP só de leitura ao Uno.
- `monitor-esp32-partidas.log`: sessão do `espflash monitor` da série de partidas, sem códigos de cor.
