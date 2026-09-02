# Guia de impressão e montagem preliminar

## Sequência recomendada

1. Imprima `C01_cupom_junta_11x6.stl` e `C02_cupom_canal_LED_13x1p8.stl`.
2. Confirme a espiga sem forçar e meça o canal com a fita real.
3. Atualize compensação/folga no arquivo de parâmetros e regenere, se preciso.
4. Imprima os três painéis no mesmo arquivo e no mesmo lote.
5. Pese e meça os painéis antes de imprimir/montar o restante do rotor.
6. Só então produza aranha, tampa e base/torre.

## Requisitos da máquina

- A base ocupa 300 × 300 mm; com skirt/brim, planeje mesa útil de pelo menos
  310 × 310 mm.
- A aranha ocupa aproximadamente 194 × 224 mm e tem 31 mm de altura.
- A base/torre tem 154 mm de altura e deve ser impressa em Z, sem inclinação.
- ABS exige gabinete fechado, mesa nivelada e controle térmico estável.

## Lote ABS — rotor

| Parâmetro | Aranha | Painéis | Tampa |
|---|---:|---:|---:|
| Nozzle | 0,4 mm | 0,4 mm | 0,4 mm |
| Camada inicial sugerida | 0,20 mm | 0,20 mm | 0,20 mm |
| Perímetros | 4 | 3 | 3 |
| Infill | 35% giroide | 35% giroide | 30% giroide |
| Câmara | fechada | fechada | fechada |

O arquivo de três painéis já os mantém paralelos e separados por 36 mm. Use o
mesmo material, perfil e impressão para reduzir diferença de massa e altura.
Não use correção automática diferente por objeto.

O painel foi exportado deitado com o boss voltado para cima. O canal fica contra
a mesa e forma uma ponte de 13 mm a 1,8 mm de altura; valide essa superfície com
o cupom e ajuste suporte/ponte conforme a impressora. Não altere a escala do STL.

## Lote ABS — base + torre

- 4 perímetros e 30% giroide;
- brim de 8–12 mm na região central e na pista externa;
- conferir perpendicularidade durante a impressão longa;
- não separar torre e base no fatiador: o arquivo é uma única malha integrada.

## Lote TPU opcional

Use TPU 95A apenas se os coxins comerciais não forem viáveis. Siga a ficha do
fabricante do filamento, mantendo os quatro no mesmo lote. Como ponto de partida
da especificação: 230–240 °C no hotend, 60–80 °C na mesa, 15–20 mm/s, 4–5
perímetros e 100% de preenchimento.

Não aplique acetona em TPU. Para ABS, qualquer alisamento deve ser feito somente
após a validação dimensional; vapor de acetona altera folgas críticas, é
inflamável e requer procedimento de laboratório apropriado. Proteja socket,
espiga, canal e furos contra alisamento.

## Critérios mínimos de aceite

- painel impresso: ≤35 g antes de aceitar o lote; depois repetir a pesagem com
  fita e ferragens e usar o limite de conjunto definido pela engenharia;
- Datum D: 104 ±0,3 mm a partir da base do painel;
- diferença de altura entre os três: <0,5 mm;
- canal: 13 × 1,8 mm dentro da tolerância acordada com a fita real;
- torre: perpendicularidade ≤1°;
- base: planeza dentro de ±2 mm;
- todas as porcas capturadas e parafusos com retenção adequada;
- balanceamento estático e dinâmico concluídos antes de elevar RPM.

Nunca ensaie o rotor sem contenção integral, parada de emergência e operação
remota. Comece em baixa rotação e estabeleça patamares de inspeção.
