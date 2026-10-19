# 8.3 — Configuração do ESC

Em 16/10/2026, o ESC LittleBee Spring 20A foi configurado no Mac pelo ESC Configurator 0.32.1, usando um Arduino Uno R3 com ATmega328P como interface MSP/BLHeli 4-way. O sinal do ESC foi conectado ao pino D3 do Uno, com GND comum entre ESC, Uno e fonte. O Uno foi alimentado pela USB; o ESC, por fonte de bancada a 6,0 V com limite de corrente. O consumo informado durante a sessão foi de 0,005 A.

O configurador identificou o ESC como **A-H-25 — BLHeli_S, 16.7**, no canal **ESC 1**. Os valores originais foram salvos e registrados pelo usuário antes das alterações. A gravação foi feita exclusivamente pelo comando **Write Settings**, seguida por **Read Settings** para confirmação.

| Parâmetro | Valor original | Valor gravado e confirmado por releitura |
|---|---|---|
| Motor Direction | Normal | Normal — preservado |
| Brake on stop | Desligado | Desligado |
| Low RPM Power Protection | Ligado | Desligado |
| Startup Power | 0,50 | 0,125 |

Como não havia um mapeamento prévio entre Normal/Reversed e a ordem das fases, o usuário solicitou preservar Normal, e o sentido ficou para o primeiro giro. Em 19/10/2026, com o sinal gerado pela ESP32 da base e o motor sem rotor a 7,0 V, o giro foi **anti-horário visto de cima**, o sentido exigido pela especificação, sem alterar a configuração. O valor de partida 0,125 deu partida no motor sem rotor; com o rotor, a partida ainda será ensaiada.

A comparação dos 112 bytes de configuração antes e depois confirmou alterações somente nos campos Startup Power e Low RPM Power Protection; os outros 110 bytes permaneceram idênticos. O firmware BLHeli_S 16.7 e o layout A-H-25 foram mantidos. As três fases do motor permaneceram desconectadas, sem ensaio de rotação. Ao final, o configurador foi desconectado da porta USB.
