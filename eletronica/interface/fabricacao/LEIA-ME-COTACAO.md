# Interface Orbiter r0.2 — instruções para orçamento

Destinação: cotação de protótipos. Este projeto ainda não foi ensaiado com os módulos, os chicotes e as fitas reais. Os ensaios de SPI quad continuam pendentes; cotação não equivale à liberação de operação do rotor.

## Especificação da PCB

- Contorno: 15,00 × 20,00 mm, retangular; quatro furos não metalizados de 2,20 mm.
- Duas camadas, FR4, espessura de 1,6 mm, cobre de 1 oz, máscara verde e serigrafia branca.
- Trilhas/alívio: projeto com mínimo de 0,153 mm (6 mil); valores efetivos no relatório DRC.
- Vias: 0,60 mm de cobre / furo 0,30 mm. Pontos de fios: furo metalizado de 0,50 mm / pad de 1,00 mm.
- Acabamento: cotar HASL sem chumbo; ENIG pode ser alternativa se o processo de montagem exigir.
- Quantidade para comparar: 5 PCBs; montagem de 2 e de 5 unidades, se disponível.
- 17 componentes SMD no topo: 1 SOIC-14, 13 resistores 0603 e 3 capacitores 0603.
- Demais grupos J1 a J6 são pontos distribuídos para fios, não componentes a comprar ou montar.
- Bateria, buck, ESP32, Hall, capacitor de 1000uF, chave, fusível e fiação de potência são externos.

## Arquivos de entrada

- ZIP de Gerbers/furação: enviar como PCB para cotação. Gerbers já incluem contorno e máscara.
- `BOM.csv`: lista com fabricante e MPN. Quantidades são por placa.
- `BOM-JLCPCB.csv`: formato para correspondência dos componentes na JLCPCB. Os códigos são candidatos cadastrados, não reserva de estoque nem aprovação de substituições.
- `PickAndPlace.csv`: centros e rotação dos SMDs. Todos no topo. Origem no canto da placa (100,100 no CAD); unidade mm. Conferir a orientação de U1 no preview do montador antes de pagar.
- `mapa-fios.csv`: montagem posterior dos fios pelo usuário; não é Pick & Place.

A placa é pequena: o fornecedor deve confirmar necessidade/custo de painel, bordas de processo e fiduciais. Não aumentar a placa entregue individualmente nem colocar resíduos de abas fora do contorno sem confirmar o encaixe de 15 × 20 mm. Confirmar se as placas são entregues separadas e como serão removidas as abas.

Componentes devem ser fornecidos pelo montador. Cotar o conjunto com as peças indicadas; eventuais equivalentes exigem revisão de valor, tensão, encapsulamento e footprint. O CI precisa ser AHCT com entrada TTL e saída em 5 V; HC não é substituição direta.

## Ligação e montagem posterior

A serigrafia inferior numera os pontos 01 a 19. Consultar `mapa-fios.csv`; não ligar por posição aparente. Todos os pontos de fio estão na BOM fora de montagem. A alimentação dos painéis sai do buck em estrela externa; não passar os amperes dos LEDs pela interface.

Fixação: centros dos furos em (2,2), (13,2), (13,18), (2,18) mm. Cabeças de parafuso devem respeitar diâmetro máximo de 3,5 mm, sem arruela maior. Confirmar rosca/retensão com os pilares impressos existentes. Abaixo da placa há a passagem dos chicotes: fios e soldas nos furos não podem criar pontas compridas nem invadir a faixa útil abaixo dos apoios. Validar na peça real.

A placa fica ao lado da bateria, não acima dela. O molde 1:1 serve para testar contorno e furos, mas não comprova as alturas, os 19 fios nem o espaço para chave/fusível externos.

## Prazo e custo

Entrega necessária até 30/11/2026 em Santos/SP ou Pato Branco/PR; alvo de planejamento: 20/11 para integração. Obter confirmação do transporte para o CEP e da data de início de produção. Comparar custo total com componentes, montagem, painelização, transporte e tributos. Os arquivos não autorizam compra automática.

Atualização da BOM: utilizar a lista otimizada de 30/10/2026, também salva em `BOM-JLCPCB.csv`. Os capacitores selecionados têm tensão nominal maior que o mínimo de 16 V indicado no esquema. Consultar `reports/REVISAO-BOM-JLCPCB.md` no pacote completo.
