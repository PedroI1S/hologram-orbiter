# Pendências e decisões em aberto — v3.0

Estado em 03/09/2026 (revisão 3.0.2), depois da regeneração que fechou A1, A2
e B1 a B11 de `../../06-PENDENCIAS-ABERTAS-v3.0.md` e dos desvios de spec
ratificados pelo revisor. Nada aqui impede imprimir cupons, painéis, aranha,
tampa, suporte do ímã ou base; os itens P0 impedem operar o rotor.

## P0 — antes de girar

1. **Medir o eixo a partir da face em que o cubo assenta:** altura do topo do
   colar Ø8 e da ponta da rosca. O desenho cotado diz colar 5 + rosca 7 numa
   saliência total de 14 (a soma dá 12: os 2 mm restantes devem ser um ressalto
   sob o colar). A fixação foi refeita para valer nas duas leituras — arruela
   Ø20 × Ø8,5 × 2 em alumínio sobre o topo do cubo, porca M6 fina DIN 439B
   com Loctite 243 — e sobram 3 mm de rosca (1 mm na leitura de 12). O número
   real fecha a compra da porca e confirma que o colar não ultrapassa o topo da
   arruela (+2 sobre o cubo; o colar chega a +1).
2. **Pesar a eletrônica da baia.** O layout (`spider.bay_layout`) usa massas de
   catálogo: placa de interface 5,5 g, ESP32-C3 3,0, buck mini560 2,0,
   capacitor 2,5, fios 2,0 = 15,0 g, exatamente a folga. O rotor fecha em
   274,3 g com o contrapeso de 2,2 g: **5,7 g de folga**. Um XL4015 (~18 g) no
   lugar do mini560 estoura tudo.

## P1 — antes de liberar o projeto

3. **Isolador de vibração (spec §5.7).** Modelado como montagem rígida; os 4
   furos Ø4 em PCD 40 (só na flange superior) servem aos dois caminhos.
4. **Layout da baia — refinar com as peças reais.** Posições e envelopes são
   parâmetros; o gerador refaz interferências, faixas dos feixes, massa e o
   contrapeso. Nominal: desbalanceamento 73 g·mm a 14°, contrapeso 2,2 g de
   tungstênio na ponta externa do alívio de 180° (r ≈ 33). Cada copo da tampa
   (plano 2) leva ~1 g de tungstênio (34 g·mm em r = 34) para o ajuste fino.
5. **Eletrônica para LiFe (06-PENDENCIAS C).** O pack comprado é LiFePO4 2S:
   6,6 V nominal, 7,2 de carga, corte prático em ~5,8 V pelo dropout do buck.
   Carregador em modo LiFe.
6. **Δm entre painéis ≤ 0,084 g** e **excentricidade da bateria ≤ 0,17 mm**
   não são atingíveis por posicionamento: balancear em dois planos (alívios do
   cubo em r 17–36 e copos da tampa em r = 34).
7. **Massa das peças estáticas.** Base + torre com abas 321 g (alvo da spec
   330); suporte do ímã 1,7 g. Só o rotor tem orçamento duro (≤ 280 g).

## Desvios da especificação — ratificados pelo revisor em 03/09/2026

- §5.1 canal em degrau: **abandonado** (apontado por Pedro em 03/09). Os LEDs
  ficam em cima do PCB, então o PCB num canal raso e os LEDs num rasgo mais
  fundo só funcionaria com a fita de cabeça para baixo. CAD: canal único
  12,4 × 2,0, parede local 2,8 numa faixa de 14,4 mm, piso 0,8 em ponte de
  12,4 (a mesma do canal original); +0,3 g por painel. Spec §5.1 corrigida.
- §5.2 rebaixo Ø13 × 2 para arruela Ø20: **sem rebaixo**, arruela Ø20 × Ø8,5 em
  alumínio e porca fina — o colar Ø8 do eixo não passava por nenhuma arruela
  M6 nem cabia sob um rebaixo.
- §5.2 postes da tampa a 58 mm: **y = ±35**, encostados na parede.
- §5.2 / §5.3 alvos de massa: aranha 75 g (CAD 67,5), tampa 12 g (CAD 10,1).
- §5.4 três abas a 120°: **quatro a 90°**, nos cantos da mesa.
- §6.3 sensor a r ≈ 37,5 e azimute 30°: **r = 29, azimute 20°**, sensor e ímã.
- Tampa 07 do invólucro: **removida** (fora de escopo).
- §9 "cavidades seladas aparecem como componentes extras": a cavidade do painel
  é aberta por projeto; o STL tem 1 componente.

## Verificações não executadas (herdadas)

FEA do painel/boss/espiga; análise modal; fluência do painel sob 12–14 MPa a
quente; retenção dos parafusos a 1800 RPM; balanceamento instrumentado; ensaio
de sobrevelocidade em contenção; térmica do motor com termopar; CFD ou ensaio
de arrasto do boss carenado (A × Cd hoje é estimativa por finura); ensaio de
impacto da base (06-PENDENCIAS D).
