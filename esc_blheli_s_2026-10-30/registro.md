# Correção do sentido — 30/10/2026

Usuário relatou giro horário e solicitou corrigir para anti-horário visto de cima. Arduino conectado ao ESC alimentado; motor permaneceu conectado por instrução do usuário.

Leitura real: BLHeli_S 16.7, A-H-25, assinatura B2 E8, interface SiLabs BLB. Startup Power já em 0,75 (offset 9 = 10), direção Normal (offset 11 = 1). A leitura não confirma inversão acidental do parâmetro durante o ajuste anterior. A causa da diferença física em relação ao ensaio de 19/10 não foi determinada.

Gravada direção Reversed (offset 11 = 2) para inverter o giro físico relatado. Os outros 111 bytes foram preservados, incluindo Startup Power 0,75. Duas releituras idênticas ao desejado. Página de 512 bytes salva antes de apagar; 400 bytes após a configuração eram FF. Escrita apenas da configuração, sem troca de firmware.

Consultas MSP confirmaram BTFL e quatro canais em 1000 µs. Nenhum comando de partida ou ajuste de acelerador enviado. Ao terminar: DeviceReset, InterfaceExit e porta serial fechada. O ESC pode emitir tons pelo motor ao reiniciar. Fonte depende do desligamento físico pelo operador.

Sentido físico após alteração ainda não verificado. Antes de ensaio, desligar a fonte para transferir o sinal do Arduino para D25 da ESP32 e manter GND comum. Valem as restrições de bancada já registradas no projeto; esta sessão não autoriza ensaio com rotor.

Backups e hashes em `verificacao-gravacao.json` e nos arquivos `.bin` desta pasta.
