# Teto de teste do motor sem aranha — 30/10/2026

Usuário pediu gravar a ESP32 com teto do ESC para testar o motor. Ajuste anterior de 2500 µs não compilava; substituído por PPM_MAX_US - 1 = 1831 µs, mantendo validação kick < ppm_max. Máximo configurado do ESC: 1832 µs; a calibração manual posterior não teve confirmação por releitura.

Teto de alvos e chute: 1831 µs. Alvo inicial 1200 µs, padrão linear, parada 1000 µs, watchdogs 500 ms. Como as inclinações derivam da amplitude até o chute, ajustes/parada suave passam a aproximadamente 56 µs/s e descida do overshoot a 113 µs/s. Teto destinado ao teste sem aranha; não validado para rotor completo.

39 testes passaram. Compilação release para ESP32 concluída. Gravação pelo espflash concluída às 21:08:30 UTC (18:08:30 São Paulo), ESP32 v3.1, porta /dev/cu.usbserial-A5069RR4. Banner confirmou faixa 1150–1831 µs. Conferidos pela serial: aceita 1831, recusa 1832; alvo restaurado para 1200. Estado final PARADO, perfil linear, zero partidas, saída próxima de 1000 µs. Nenhum comando de partida enviado. Porta serial fechada.

Log: teste-teto-esc-serial.txt. Alteração apenas no firmware ESP32; nenhuma configuração do ESC gravada nesta etapa.
