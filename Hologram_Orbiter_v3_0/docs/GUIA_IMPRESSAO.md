# Guia de impressão — v3.0

Bico 0,4 mm, camada 0,2 mm, ABS em câmara fechada (spec §7). Mesa de
300 × 300 mm. Não altere a escala nem "conserte" os STL no fatiador: eles são
estanques e orientados; qualquer cota muda em `CAD/parameters.json`.

## Sequência

1. `C01_cupom_junta.stl` e `C02_cupom_canal_LED.stl`. Conferir: espiga
   11 × 6 entra no socket 11,2 × 6,2 sem forçar e sem folga sensível; fita
   HD107S real assenta no canal 12,4 × 1,2 com o piso de 0,8 mm íntegro (ponte
   de 12,4 mm) e o bolso 8 × 3,5 aberto.
2. Ajustar `quality.joint_xy_clearance_each_side` ou compensações se preciso e
   regenerar.
3. `02_painel_LED_ABS_3x_mesma_mesa.stl` — os três painéis no mesmo lote, mesmo
   filamento, mesmo perfil. Pesar os três: Δm ≤ 0,091 g é o alvo depois de
   montados; anotar.
4. `01_aranha_ABS.stl`, `03_tampa_baia_ABS.stl`, `06_poste_ima_ABS.stl`.
5. `04_05_base_torre_ABS_integradas.stl` — liberada. A canaleta de assento
   do cilindro (4,4 × 3 mm em r = 135) já está no STL; não há furos
   periféricos. Conferir o Ø interno do cilindro recebido antes de fatiar:
   se divergir de 266, ajustar `base_tower.containment_seat` e regenerar.
6. `07_tampa_contencao_ABS.stl` — tampa do cilindro, mesma canaleta da base.
   Espessura da placa em `containment_cap.plate_thickness` (3 mm ≈ 191 g;
   cada 1 mm a mais são ~62 g). Peça grande e chata em ABS: brim de 8 mm,
   câmara fechada, mesa bem nivelada, e se empenar considere 4 mm.

## Orientação (já embutida nos STL, base em Z = 0)

| Peça | Como está no STL | Suporte |
|---|---|---|
| Painel | deitado, 208 mm em X, boss e carenagem para cima, canal do LED contra a mesa | nenhum na lâmina; a carenagem é uma casca vertical aberta; os bolsos hexagonais das porcas ficam de lado (ponte de 6 mm, ok) |
| Aranha | plana, face inferior do cubo na mesa | **sim, sob os braços**: eles ficam 6 mm acima da mesa (Datum B + 3). Usar suporte em árvore com 0,2 mm de folga só sob os braços e o berço não precisa |
| Tampa | plana, pele na mesa; copos de balanceamento para cima | nenhum |
| Base + torre | torre em Z, sem inclinação | nenhum; as janelas laterais de 12 mm são pontes curtas |
| Poste do ímã | aba na mesa, poste para cima | nenhum |
| Tampa do cilindro | face plana na mesa, anel de assento e canaleta para cima | nenhum (a canaleta é um sulco aberto para cima) |
| Cupons | como exportados | nenhum |

O canal do LED forma uma ponte de 12,4 mm a 1,2 mm da mesa: é a superfície mais
delicada do projeto. Validar no cupom antes do lote de 208 mm.

## Perfis sugeridos

| Parâmetro | Painéis | Aranha | Tampa da baia | Base + torre | Poste | Tampa do cilindro |
|---|---:|---:|---:|---:|---:|---:|
| Perímetros | 3 | 4 | 3 | 4 | 3 | 4 |
| Infill | 35 % giroide | 35 % giroide | 30 % | 30 % giroide | 100 % | 25 % giroide |
| Camadas topo/base | 5 | 5 | 4 | 5 | 4 | 4 |
| Brim | 5 mm | 5 mm | — | **8 mm** (Ø280 + 16 = 296) | 3 mm | **8 mm** (Ø280 + 16 = 296) |

Faça o bolso da porca (hexágono de circunraio 3,35) e o furo Ø8 do cubo sem
"expansão de furo" automática. Se o Ø8 sair justo, alargar com broca de 8 mm;
o cubo assenta pela face, não pelo furo.

## Critérios mínimos de aceite da peça impressa

- painel nu ≈ 31,7 g em densidade maciça; com infill ficará abaixo. Registrar
  a massa real dos três e usar o limite de 45 g montado;
- Datum D = 104 ±0,2 mm a partir da base do painel; Δh entre os três ≤ 0,5 mm;
- canal 12,4 × 1,2 com a fita real; piso íntegro;
- espiga/socket com 0,1 mm por lado;
- torre perpendicular à base ≤ 1°; base plana em ±2 mm;
- todas as porcas capturadas; entreferro do hall 2–3 mm.

Nunca ensaie o rotor sem contenção, parada de emergência e operação remota.
Rampa de partida ≥ 8 s (pico previsto 8 A).
