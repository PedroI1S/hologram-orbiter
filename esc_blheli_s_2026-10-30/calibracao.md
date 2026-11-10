# Calibração — preparação em 30/10/2026

Operador confirmou ESP32 conectada ao ESC, motor sem aranha, fonte do ESC desligada e USB ligada.

Ferramenta temporária `firmware/esp32-base/src/bin/calibrar-esc.rs` compilada e gravada na ESP32 v3.1 pela porta `/dev/cu.usbserial-A5069RR4`. Conferida pela serial em modo 0: 1000 µs, máximo ainda não utilizado. **Calibração ainda não executada.**

A ferramenta inicia sempre em 1000 µs. H envia 1832 µs uma única vez por boot, por até 30 s; deve ser enviado somente com o ESC desligado. Após ligar o ESC e ouvir os tons de máximo, L envia 1136 µs durante 8 s e retorna a 1000 µs. O BLHeli_S acrescenta aproximadamente 12 µs ao mínimo medido, buscando manter a faixa anterior de 1148–1832 µs. A medição pelo clock do ESC pode mudar os valores: conferir por leitura dos parâmetros antes de declarar a faixa final.

p, espaço, Esc, Ctrl-C enviados à UART, botão D33 e timeout retornam a 1000 µs. Os dois watchdogs continuam ativos. A ferramenta não escuta os tons e não comprova a gravação interna do ESC. Não há partida normal nesta ferramenta.

Pendentes: sequência física com operador; confirmação dos tons; releitura dos parâmetros pelo Arduino se necessário; restaurar `esp32-base` normal antes de qualquer ensaio. O programa temporário foi substituído pelo firmware normal; ver restauração abaixo.


## Restauração às 20:34 UTC (17:34 São Paulo)

Por solicitação do usuário, recompilado e gravado `esp32-base` normal, versão 0.3.0, teto 1350 µs. Gravação concluída pelo espflash. Banner serial confirmou faixa PPM configurada no programa de 1148–1832 µs, alvo 1200 µs, perfil linear, zero partidas e estado PARADO em aproximadamente 1000 µs. Nenhuma partida enviada. Porta fechada após conferência.

O usuário preferiu executar a calibração manualmente; não forneceu confirmação dos tons nem releitura dos parâmetros do ESC. Portanto a conclusão da calibração e os limites efetivamente gravados no ESC seguem sem confirmação. Restaurar a ESP32 não desfaz parâmetros eventualmente alterados pela calibração no ESC.
