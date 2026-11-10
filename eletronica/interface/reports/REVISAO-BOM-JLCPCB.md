# Revisão de compra da BOM — 30/10/2026

Motivo: na captura da cotação, C2 (C97890) apresentava falta de 20 unidades; todos os oito grupos estavam como Extended. A revisão mantém 17 SMDs, valores nominais e encapsulamentos. A PCB r0.2, o Gerber e o Pick & Place não foram alterados.

## Substituições de fornecimento

| Referências | Código anterior | Código atual | Modelo atual | Classe consultada |
|---|---|---|---|---|
| R1,R2,R3,R8,R9 | C98220 | C25804 | UNI-ROYAL 0603WAF1002T5E, 10k 1%, 0,1W, 0603 | Basic |
| R4 | C114660 | C22807 | UNI-ROYAL 0603WAF1503T5E, 150k 1%, 0,1W, 0603 | Basic |
| R5 | C105579 | C25819 | UNI-ROYAL 0603WAF4702T5E, 47k 1%, 0,1W, 0603 | Basic |
| R6,R10,R11 | C108661 | C23140 | UNI-ROYAL 0603WAF330JT5E, 33 ohms 1%, 0,1W, 0603 | Basic |
| R7,R12,R13 | C95177 | C21189 | UNI-ROYAL 0603WAF0000T5E, jumper 0 ohm, 0,1W, 0603 | Basic |
| C1,C3 | C45000 | C14663 | Yageo CC0603KRX7R9BB104, 100nF 50V X7R 10%, 0603 | Basic |
| C2 | C97890 | C5972986 | Yageo CS0603KRX7R8BB105, 1uF 25V X7R 10%, 0603 | Extended |
| U1 | C155176 | C155176 | TI SN74AHCT125DR, SOIC-14 | Extended, mantido |

Aumento da tensão nominal dos capacitores: de 16 V para 50 V em C1/C3 e para 25 V em C2. Capacitância, tolerância máxima de 10%, dielétrico X7R e tamanho 0603 foram preservados. Os valores do esquema de 16 V passam a representar o requisito mínimo de tensão, não o código exato adquirido. Não foi necessária mudança no cobre ou nas posições.

A página pública de C5972986, consultada nesta sessão, retornou `overseasStockCount=63`, `leastPatchNumber=20` e classe `expand`. É uma observação pontual do catálogo; não há reserva e o estoque do pedido deve ser confirmado no checkout. Cadastramento, classe e preço dos demais passivos foram consultados no catálogo público; a revisão não garante estoque reservado de todos eles.

No resultado esperado do novo processamento, seis grupos (15 componentes por placa) ficam Basic, e U1/C2 permanecem Extended. As taxas finais dependem da cotação, de promoções e da disponibilidade. Não trocar U1 por HC125 para reduzir preço.

## Uso

Em Upload BOM/CPL, enviar `BOM-JLCPCB-otimizada.csv` e o mesmo `PickAndPlace.csv`. O arquivo `BOM-JLCPCB.csv` também foi atualizado para a mesma lista. Conferir todos os oito grupos, os 17 componentes por placa e a inexistência de falta de estoque. Os números extras de compra/perdas de montagem são controlados pelo fornecedor.

## Fontes oficiais consultadas

- https://jlcpcb.com/partdetail/0603WAF1002T5E/C25804
- https://jlcpcb.com/partdetail/0603WAF1503T5E/C22807
- https://jlcpcb.com/partdetail/0603WAF4702T5E/C25819
- https://jlcpcb.com/partdetail/0603WAF330JT5E/C23140
- https://jlcpcb.com/partdetail/0603WAF0000T5E/C21189
- https://jlcpcb.com/partdetail/CC0603KRX7R9BB104/C14663
- https://jlcpcb.com/partdetail/YAGEO-CS0603KRX7R8BB105/C5972986

Verificação local: grupos de referências da BOM coincidem com as 17 posições; hashes do CAD, Gerber ZIP e Pick & Place foram comparados antes/depois desta revisão (`procurement-preserved-files.json`). Não se repetiu DRC/ERC, pois os arquivos elétricos e geométricos não foram modificados.
