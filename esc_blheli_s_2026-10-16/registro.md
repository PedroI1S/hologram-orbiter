# Registro da configuração do ESC — 16/10/2026

**Resultado:** configurações gravadas e confirmadas por releitura no ESC Configurator. O sentido físico anti-horário está pendente, com Normal preservado por solicitação do usuário. Em 19/10, o primeiro giro confirmou o sentido anti-horário com Normal (ver a atualização no fim).

## Valores para a seção 8.3

Firmware: **BLHeli_S 16.7**. Target/layout: **A-H-25**. Canal: **ESC 1 / Arduino D3**.

| Parâmetro | Original | Gravado e relido |
|---|---|---|
| Motor Direction | Normal | Normal — preservado |
| Brake on stop | Desligado | Desligado |
| Low RPM Power Protection | Ligado | Desligado |
| Startup Power | 0,50 | 0,125 |

O usuário informou não conhecer a correspondência Normal/Reversed com a ordem das fases e pediu preservar a opção atual. O sentido anti-horário não foi validado nesta sessão. Startup Power 0,125 é um valor inicial, sem ensaio de partida.

## Montagem e procedimento

- Arduino Uno R3, ATmega328P, USB em `/dev/cu.usbserial-10`.
- Sinal do ESC em D3; GND comum entre ESC, Uno e fonte; alimentação do Uno somente pela USB.
- Fonte do ESC: 6,0 V, limite inicial orientado de 0,10 A; usuário informou tensão estável e consumo de 0,005 A.
- Três fases do motor desconectadas durante a configuração; sinal separado da ESP32.
- Chrome instalado de fonte oficial; ESC Configurator 0.32.1 controlado pela interface gráfica.
- Leitura original: ESC 1 identificado às 11:42:25. Os outros três canais não têm ESC conectado.
- Backup completo salvo antes de qualquer alteração; usuário confirmou que registrou os valores originais.
- `Write Settings`: término confirmado às 11:44:44.
- `Read Settings`: ESC 1 identificado novamente às 11:45:10; leitura dos canais terminada às 11:45:19.
- Verificação bruta: dos 112 bytes de configuração, apenas o byte de Startup Power (offset 9: 9 → 5) e o de Low RPM Power Protection (offset 36: 1 → 0) mudaram. Os demais 110 bytes são idênticos ao backup original.
- A versão e o layout foram mantidos; nenhum firmware novo foi gravado no ESC.
- Nenhum controle de motor foi habilitado e não houve ensaio de rotação.
- Opções temporárias de diagnóstico do configurador restauradas; porta USB fechada pela interface às 11:46:51.
- A fonte ainda depende do desligamento físico pelo usuário ao encerrar a bancada.

## Arquivos de documentação e backup

- `secao_8_3_configuracao_esc.md`: texto pronto para a seção 8.3.
- `parametros-originais.md` e `parametros-originais.json`: todos os 13 parâmetros mostrados na leitura original.
- `parametros-gravados.json`: parâmetros após a releitura.
- `esc1-config-original-0x1a00.bin` e `.hex.txt`: 112 bytes originais de configuração.
- `esc1-config-gravada-0x1a00.bin` e `.hex.txt`: 112 bytes confirmados após a escrita.
- `verificacao-gravacao.json`: comparação dos bytes e hashes SHA-256.
- `esc-configurator-antes.txt` e `esc-configurator-depois.txt`: logs exportados pelo configurador.
- `uno-antes-flash.hex` e `uno-antes-eeprom.hex`: cópias do estado anterior do Arduino.
- `blheli_passthrough.ino` e `uno-passthrough.hex`: sketch original e primeira compilação.
- `blheli_passthrough-corrigido.ino` e `uno-passthrough-corrigido.hex`: interface corrigida efetivamente usada no Uno.

Os arquivos de configuração do ESC são backups de parâmetros, não uma cópia integral do firmware do ESC.

## Correção necessária do passthrough no Uno

Origem do sketch: https://zff.dev/fluxin/blheli_passthrough ; espelho: https://codeberg.org/fluxin/blheli_passthrough . Blob Git original: `e1e8923ce053042c780323e652737263f78a2fbc`.

A versão original compilou com avisos de saltos sobre inicializações de variáveis em dois ramos do switch MSP. Consultas reais mostraram payloads vazios para MSP_MOTOR (104) e MSP_FEATURE_CONFIG (36), causando falha na negociação do site após a identificação do Uno. Foram acrescentadas chaves aos casos MSP_UID e MSP_BATTERY_STATE para limitar o escopo dessas variáveis, mantendo `MODE_NORMAL`.

A versão corrigida compilou para `arduino:avr:uno` com Arduino CLI 1.5.1, Arduino AVR Boards 1.8.8 e `compiler.cpp.extra_flags=-fno-permissive`, sem aqueles avisos: 9228 bytes de flash, 626 bytes de variáveis globais. A gravação foi verificada. As consultas MSP posteriores devolveram 8 bytes para o comando 104 e 4 bytes para o comando 36, ambos com checksum válido. O funcionamento completo foi confirmado pela leitura, escrita e releitura do ESC através do site.

SHA-256 do sketch corrigido: `a297fdc76cbb8ff868ebc9b4b0317d131d5ce0c84c5d6adee8fa1baf23eb0ff4`.

Houve também uma recusa do driver serial do macOS (`tcsetattr: Invalid argument`), resolvida ao desconectar e reconectar o cabo USB.

A identidade MSP BTFL 4.3.0 / ARDU e os dados de bateria 4S/16 V mostrados pelo sketch são simulados pela interface. Eles não correspondem à versão do ESC nem à tensão real da fonte. A identificação real do ESC foi obtida pela interface BLHeli 4-way.

## Atualização de 19/10/2026 — primeiro giro, motor sem rotor

Sinal gerado pela ESP32 da base com o firmware de `firmware/esp32-base` (commit `539675b`): D25 a 50 Hz, GND comum, placa alimentada pela USB. Fonte de bancada a 7,0 V. Motor A2212 preso, sem rotor e sem hélice, com as três fases ligadas ao ESC. Nenhuma configuração do ESC foi alterada.

- O ESC armou com o pulso de parada de 1000 µs.
- A placa contou seis partidas pela rampa de 12 s, que parte de 1148 µs; o alvo chegou a 1400 µs, o teto estimado do firmware. O motor partiu com Startup Power 0,125. Segundo o usuário, a corrente na fonte ficou abaixo de 1 A.
- **Sentido confirmado: anti-horário visto de cima**, com Motor Direction = Normal e a ordem atual das fases. É o sentido da especificação 01 §3: o bordo de ataque arredondado (R4, em +y) vai à frente e a fuga afilada fica atrás. Fecha a pendência de 16/10.
- O sentido depende da ordem dos três fios do motor nos pads do ESC: trocar quaisquer dois inverte o giro. Marcar fios e pads antes de desmontar.

Ainda sem ensaio: a parada e o watchdog com o motor girando, a partida com o rotor (inércia cerca de 100 vezes maior; bloqueador D do 04) e o teto medido com tacômetro.
