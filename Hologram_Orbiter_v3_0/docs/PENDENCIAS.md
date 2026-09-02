# Pendências e decisões em aberto — v3.0

Estado em 02/09/2026. Nada aqui impede imprimir cupons, painéis, aranha,
tampa, poste ou a base; os itens P0 impedem operar o rotor.

## P0 — antes de girar

2. **Altura do conjunto motor (30 mm)** derivada do datasheet, não medida.

## P1 — antes de liberar o projeto

4. **Isolador de vibração (spec §5.7).** Modelado como montagem rígida; os 4
   furos Ø4 em PCD 40 servem aos dois caminhos.
5. **Eletrônica embarcada.** Placa ESP32, regulador 5 V, chave e conector de
   carga sem dimensões: a janela da tampa é placeholder e os 15 g de folga no
   orçamento do rotor são estimativa.
6. **Massa de peças estáticas — resolvido em 02/09/2026.** Base + torre
   (310 g) e tampa do cilindro (191 g com placa de 3 mm) não têm critério de
   massa: só o rotor tem orçamento (≤ 280 g). O alvo de 300 g da spec para a
   base fica registrado como histórico; o 306 g da v2.1 era artefato do bug
   das nervuras sobrepostas.
6a. **Ventilação com o cilindro fechado.** Com a base apoiada na mesa (pista
   e nervuras de 8 mm encostadas) e a tampa fechada, o interior do cilindro
   só troca ar pelos 13 furos da tampa (5 177 mm²). As janelas laterais da
   baia (§5.4) passam a circular ar dentro do cilindro, não com a sala. Se a
   térmica do motor pedir mais (spec §10.1, pior caso 99 °C), a saída barata
   é dar pés à base (4 calços de ~10 mm sob a pista) para criar chaminé:
   entra ar por baixo do anel, sai pela tampa. Não está modelado; é decisão.
6b. **Furos periféricos removidos** (decisão de 02/09/2026). Com a canaleta
   em r = 132,8–137,2 sobram 2,8 mm de cada lado da pista, sem lugar para
   furo Ø4, e uma base de 310 g com 280 mm de apoio não precisa ser
   parafusada na bancada. `base_tower.peripheral_holes.enabled = true` os
   devolve, atravessando as nervuras em PCD 240.
7. **Δm entre painéis ≤ 0,091 g** e **excentricidade da bateria ≤ 0,17 mm**
   não são atingíveis por posicionamento: balancear em dois planos (alívios do
   cubo e copos da tampa).

## Conflitos documentais encontrados na spec v3.0

- §5.4: "furos periféricos 4 × Ø4 em PCD 290" com base de Ø280. O meio da
  pista (PCD 270) é onde fica a canaleta; os furos foram removidos, ver
  item 6b.
- §5.2 ainda cita 131,7 N por painel; o valor vigente é 158,1 N (§2.1 e §10).
- §5.6 ainda cita rotor de 251 g e 8,4 g·mm; o vigente é 273 g e 9,1 g·mm.
- §5.8 ainda cita deflexão de 2,07 mm; o vigente é 2,48 mm.
- §5.1 "batente inferior 2,0 mm": mantido como pele de 2 mm, mas o apoio da
  fita subiu para Z = −98,5 por causa do bolso de fios de 3,5 mm (a fita de
  201,4 mm termina em Z = +102,9, dentro dos 104 do topo).
- §7 "feature mínima 1,2 mm" versus §5.1 "nervuras de 1,0 mm": mantido 1,0
  conforme §5.1.
- §9 "cavidades internas seladas aparecem como componentes extras": na v3.0 a
  cavidade do painel é **aberta** (vão nos diafragmas, furo na lâmina e bolso
  na ponta), logo o STL tem 1 componente. É intencional: sem volume preso.

## Verificações não executadas (herdadas da v2.1)

FEA do painel/boss/espiga; análise modal; fadiga do painel (SF 2,5 em flexão);
retenção dos parafusos a 1800 RPM; balanceamento instrumentado; ensaio de
sobrevelocidade em contenção certificada; térmica do motor com termopar; CFD
ou ensaio de arrasto do boss carenado (A×Cd hoje é estimativa por finura).
