# Variante 3.1-P.2 — base suspensa em paralelogramo, com trava

Desenvolvida em 11/11/2026, em paralelo ao pacote 3.0.5, que **não foi alterado**
(os nove STL do 3.0.5 regeneram com o mesmo hash). Fonte de verdade desta
variante: `CAD/parameters_paralelogramo.json`.

**Provisório. Nada aqui foi impresso nem medido.** As frequências e tensões são
estimativas com módulo de PETG de catálogo.

## O que as revisões independentes concluíram

A variante foi revista em duas rodadas por seis análises separadas (dinâmica de
rotores, conceitos alternativos, modos de falha, amortecimento e, depois das
correções, nova verificação da geometria nas malhas e da dinâmica). Veredito da
segunda rodada: **dentro das restrições (PETG impresso, M3, EVA opcional), palco
pendurado travável sobre torre maciça contraventada é o melhor projeto
disponível; nenhuma outra arquitetura ganha nos dois critérios.** Elas concordam em:

1. **Quem impede a inclinação é a torre contraventada, o braço reforçado e o
   balanceamento do rotor — não a suspensão.** Com 5 g de desbalanceamento a
   1800 RPM a estimativa é 0,05° tanto suspenso quanto travado (diferença
   menor que 0,01°); a tensão que isso põe na espiga é menor que 0,06 MPa.
2. **A suspensão compra outra coisa:** 24 a 40 vezes menos força na mesa.
   O preço é cruzar uma rotação crítica baixa em toda partida e parada.
3. **Por isso o palco agora pode ser travado.** Com as mesmas peças o conjunto
   roda rígido (travado) ou suspenso (solto), e a bancada decide.
4. Mola espiral com disco deslizante, apoio só em espuma, hastes em pé e
   amortecedor sintonizado ficaram atrás nos dois critérios.

Pontos que nenhuma base resolve: folga do eixo e dos rolamentos do motor
(provavelmente o elo mais mole para inclinação) e a flexão centrífuga dos
próprios painéis (22–29 MPa em `reports/FISICA.json`).

## Como regenerar

```sh
V=variantes/paralelogramo
python3 scripts/build.py --parameters CAD/parameters_paralelogramo.json \
  --output-dir $V/exports --report-dir $V/reports --fabrication-dir $V/fabricacao
```

Correção de 12/11/2026 (base fixa): as mãos-francesas das abas e os blocos dos
batentes eram prismas planos que aforavam na casca (espigão com entalhe em V em
45°+90°n; retângulo plano em 22,5°+90°n). Agora seguem o perfil do chanfro e do
cone, enterrados 0,6 mm na parede; nada fica saliente fora das abas.

Mudanças de 13/11/2026: (1) a calha em C dos fios foi trocada por três ganchos
alternados com farpão (a calha ficava sob a flange e a fenda de 3,5 mm não segurava
fio nenhum); a base a 45° dispensa suporte. Com os fios medidos (3 × Ø3) os ganchos
ficam acima das aletas do palco (Z 82–127): entre as aletas não sobraria espaço para
passar o fio de lado. Abaixo de Z ≈ 80 o vão de 45° entre as aletas guia os fios. (2) O reforço do braço
foi carenado: aleta em D (nariz arredondado no bordo de ataque, costas retas junto
ao sulco dos fios) e alma em perfil de asa em toda a corda. O arrasto estimado do
reforço cai de ~2,2 W para ~1 W a 1800 RPM, com resistência igual ou maior
(módulos 526/355/210 mm³ contra 498/339/205).

Motor AX-2810Q (medidas do Pedro, 13/11/2026): base serrilhada Ø13 × ~5, trecho
liso Ø4 × 5, rosca M4 × 10, furação em cruz 16/19 (a chapa R01 não muda), 3 fios Ø3.
O cubo assenta na base serrilhada, como uma hélice. Da chapa ao Datum B são agora
37 mm (26 do corpo, de catálogo, + 5 + 6 do cubo), então a torre ficou 7 mm mais
baixa e o Datum B continua em 186; o poste do ímã cresceu para 28,5 mm.
**Ainda de catálogo:** a altura de 26 mm da chapa à campânula e os ~5 mm da base
serrilhada (deduzida). Medir as duas antes de imprimir a torre.

Requer Blender 5.x e NumPy. Resultado atual: 69 de 69 critérios e validação
independente dos STL aprovada (`reports/ACEITACAO.md`, `reports/stl_validation.json`).
Além disso, teste de colisão booleano nas malhas: palco contra base fixa e
contra a bandeja, em todo o curso, sem nenhuma interferência.

## O que mudou em relação ao 3.0.5

| Item | 3.0.5 | 3.1-P.2 |
|---|---|---|
| Base | base + torre numa peça | base fixa (casca cônica) + palco pendurado em 8 hastes, travável |
| Torre | Ø30, livre em 150 mm | Ø40 maciça, 8 aletas até Z = 80, cone a 45° sob a flange, 3 ganchos alternados para os fios; 7 mm mais baixa (motor mais alto) |
| Braço da aranha | 15 × 6 mm, 103 mm³ na raiz | aleta + alma da raiz até o ombro (r = 74); 498 mm³ na raiz |
| Tensão a 10° de inclinação, 1800 RPM | 14,2 MPa na raiz | 2,9 MPa na raiz; 9,7 MPa na espiga 11 × 6, que passa a ser o limite |
| Inclinação máxima possível do palco | sem limite | 0,24° a 0,34° conforme o eixo (limitador sobre as orelhas) |
| Baia da aranha | 29 mm | 47 mm, com prateleira em Z = 28 para a placa própria |
| Material das peças grandes | ABS | PETG (painéis continuam ABS) |
| Motor | A2212 920KV, cubo na campânula, colar Ø8 + M6 | AX-2810Q 750KV medido em 13/11: cubo na base serrilhada Ø13 do adaptador, furo Ø6 com a bucha de 6 mm do motor, M4; mesma cruz 16/19 na chapa R01 |

Datum B continua em Z = 186: os painéis e a espiga 11 × 6 são os mesmos.

## Peças a imprimir

| Arquivo (`exports/stl/`) | Qtd | Material | Massa maciça | Orientação |
|---|---:|---|---:|---|
| `04_base_fixa_PETG_imprimir_invertida.stl` | 1 | PETG | 426 g | já vem invertida: teto na mesa, sem suporte (oito pontes de 16 mm nas janelas) |
| `05_palco_torre_PETG.stl` | 1 | PETG | 509 g | em pé, aro na mesa, sem suporte |
| `08_hastes_flexiveis_macia_1p5_8x.stl` | 2 mesas (uma de reserva) | ABS ou PETG | 11 g | deitadas, 100% de preenchimento |
| `09_buchas_trava_4x.stl` | 1 | qualquer | 6 g | em pé, flange na mesa |
| `10_bandeja_amortecedor.stl` | 1 (opcional) | PETG | 31 g | deitada, como exportada |
| `01_aranha_PETG.stl` | 1 | PETG | 113 g | fundo do cubo na mesa; suporte sob os braços |
| `03_tampa_baia_PETG.stl` | 1 | PETG | 12 g | como no 3.0.5 |
| `06_suporte_ima_PETG.stl` | 1 | PETG | 2 g | como no 3.0.5 |

## Ferragens e material extra

- 16 parafusos M3 × 10 e 16 porcas M3 (hastes).
- **Fixação da aranha no AX-2810Q:** a bucha de 6 mm que vem com o motor, uma
  arruela larga DIN 9021 M4 (12 × 4,3 × 1,0) e uma porca M4 autotravante DIN 985
  (5 mm). Não use a porca-ogiva do motor: a ponta do eixo já fica 9 mm acima do
  cubo, 1 mm abaixo dos trilhos da bateria (que subiram para Z = 10).
- **Trava:** 4 parafusos M3 × 40 e 4 porcas M3 (aprovado em 11/11/2026), mais
  4 parafusos M3 × 10 para a trava vertical.
- **Amortecedor viscoso (provisão, decidir depois):** cerca de 17 mL de óleo de
  silicone 10 000 cSt (óleo de diferencial de automodelo). Seco, não faz nada.
- Opcional: 4 calços de EVA **firme** de 14 × 6 × 6 mm.

## Montagem

1. Cole os calços de EVA no fundo dos quatro bolsos (se houver). Eles ficam a
   1,5 mm da orelha. **Não deixe o EVA encostado no palco:** em contato
   permanente ele leva a ressonância para dentro da faixa de giro.
2. Solte uma porca em cada rasgo do aro do palco e prenda os blocos de baixo
   das oito hastes, entre as guias, com a haste para cima. Aperte de leve.
3. Apoie o palco em calços de 4,0 mm sobre a mesa. Desça a base fixa sobre
   ele com as quatro orelhas alinhadas aos rasgos (22,5°, 112,5°, 202,5°, 292,5°).
4. Solte as porcas nos rasgos do anel superior e aparafuse os blocos de cima
   pelas janelas da casca. **Aperte os de cima por último**, com o rotor já
   montado, e só então tire os calços. Oito hastes são hiperestáticas:
   0,17 mm de diferença de comprimento flamba uma haste.
5. Reaperte os parafusos de baixo pelos furos Ø7 da pista.
6. Fixe a base à mesa pelas **quatro** abas.
7. Desça os três fios do motor pela borda da chapa R01 em 157,5° e estale um a
   um nos três ganchos da torre (abrem para lados alternados; o farpão da ponta
   segura cada fio). Abaixo do último gancho, leve-os por cima do disco do palco
   ao entalhe da pista (168,75°) com uma laçada frouxa.
   **Fio esticado anula a suspensão.**

**Para travar (4 + 4):**
- Radial: enfie por fora uma bucha com flange em cada furo Ø8,4 da pista
  (67,5°, 157,5°, 247,5°, 337,5°), passe o M3 × 40 por dentro e aperte na porca
  do ressalto do aro. Aperte os quatro por igual.
- Vertical: pelo furo Ø7 no teto da casca, sobre cada batente, rosqueie um
  M3 × 10 no teto do batente até encostar na orelha e dê mais um quarto de
  volta. Ele empurra a orelha para baixo e deixa as hastes tracionadas.
- Reaperte depois de 24 h (o PETG cede).

Travado, o modo mais baixo estimado é ~100 Hz; a torre presa numa base ideal
daria ~138 Hz. Para soltar, tire os oito parafusos e as buchas.

**Amortecedor (se for usar óleo):** antes de montar o palco, ponha a bandeja
na mesa. Suas quatro linguetas entram por baixo nos rasgos dos batentes quando
a base fixa desce, e a centram. As quatro pás penduradas para dentro do aro do
palco ficam no meio das cubas. Cerca de 4 mL de óleo por cuba, até 1 mm abaixo
da borda. Folgas conferidas por teste de colisão nas malhas: nenhum contato
mesmo com os batentes folgados em 4 mm.

## O que esperar (estimativas, haste de 1,5 mm, palco solto)

Números do gerador; entre parênteses, o modelo independente da segunda rodada.

| Grandeza | Valor |
|---|---:|
| Massa móvel (rotor 345 g + palco 509 g + motor e chapa 105 g) | 0,96 kg |
| Translação do palco | 4,4 Hz, crítica em 262 RPM (4,55 Hz) |
| Giro (yaw) do palco | 12,7 Hz, 760 RPM (13,5 Hz) — dentro da faixa |
| Balanço (rocking) do palco | 103 Hz (94 Hz) |
| Modo combinado balanço + torre | 86 Hz (84–88 Hz) |
| Flexão da torre acima das aletas | 158 Hz (138 Hz) |
| Inclinação estática por 10 N no rotor, palco + torre | 0,046° (0,050°) |
| Força lateral no rotor que flamba a primeira haste | 35 N (32 N); 5 g a 100 mm e 1800 RPM dão 18 N |
| Amortecimento com óleo (ordem de grandeza, fator 3) | ζ ≈ 0,12 em translação, 0,05 em giro |
| Tensão de flexão da haste no batente (3 mm) | 9,1 MPa |

**O terceiro harmônico cruza o modo combinado perto de 1700 RPM.** Se o ensaio
de impacto der menos de 95 Hz, limitar a 1600 RPM.

## Medições que fecham o projeto (só a bancada responde)

| # | Ensaio | Passa se |
|---|---|---|
| 1 | Impacto com o palco solto | translação 4,0–5,0 Hz; giro 12–15 Hz; fator Q do giro ≤ 35 |
| 2 | Impacto no rotor, solto e travado | modo mais baixo de flexão/balanço acima de 100 Hz (80–95 Hz: limitar a 1600 RPM) |
| 3 | Puxar 10 N no CG do rotor, com relógio comparador ou laser | inclinação ≤ 0,06° |
| 4 | Subida 0–1800 RPM filmando as orelhas | sem toque nos batentes acima de 600 RPM; giro ≤ 0,3 mm entre 760 e 870 RPM |
| 5 | Chute de partida | orelha não chega ao batente rígido (3 mm) |
| 6 | Acelerômetro do celular na mesa, travado × solto a 1800 RPM | redução de pelo menos 10× |
| 7 | Eixo do rotor em relação ao centro do círculo das hastes | dentro de 0,5 mm |
| 8 | Parafusos da trava depois de 24 h | ainda apertados |

## Pedidos ao firmware (não alterado por esta variante)

- Cruzar 200–400 RPM a **300 RPM/s ou mais** (subir a ≥ 50 µs/s até passar de 1200 µs).
- Alvo mínimo de **1200 µs**: um alvo de 1170 µs estaciona na ressonância.
- **Não estacionar entre 760 e 870 RPM** (modo de giro do palco) e manter o
  chute de partida em 0,1 N·m ou menos, ou partir travado.
- Ligar **Brake on Stop** no ESC: sem freio o rotor cruza a crítica a 11–20 RPM/s
  na parada e o palco bate nos batentes dezenas de vezes.

## Verificação independente final (12/11/2026)

As malhas publicadas foram conferidas por um revisor independente: guias dos
16 assentos, batentes, limitador de inclinação, trava, saída de cabo, caminho
de montagem e bandeja do amortecedor. Resultado: **pronto para imprimir**.
Menor folga palco–bandeja em todo o curso: 1,0 mm (ponte da pá sobre a borda da
cuba, com o palco 0,5 mm abaixo). Notas de bancada, sem reexportar:

- **Parafusos verticais da trava:** o furo de acesso de 6 mm deixa 0,2 mm por
  lado para a cabeça do M3. Passe uma broca de 6 mm, ou rosqueie o M3 × 10 por
  dentro antes de descer a base fixa, para só a chave passar pelo furo.
- **Parafusos radiais da trava:** M3 × 35 ou × 40; o × 30 fica 0,2 mm curto.
- **Janelas da base fixa:** oito pontes de 16 mm; imprimir com ventilação de ponte.

## Limites e pendências

- **Balancear o rotor** a 2 g em r = 100 mm ou melhor. Com o palco solto ele serve
  de balanceadora: cerca de 0,1 mm de órbita por grama.
- **Modo de giro a ~760–810 RPM.** A geometria não deixa tirá-lo da faixa. A
  análise o classificou como incômodo, não como risco de inclinação (acopla
  ~0,004° em regime): bate nos batentes na partida e se o rotor estiver mal
  centrado e parado nessa rotação. O óleo o amortece; travar o elimina.
- **Reapertar os quatro parafusos de baixo dos azimutes 45°, 135°, 225° e 315°
  antes de grampear a base:** o furo de acesso sai sobre a aba de grampo.
- **Canto vivo no ombro do braço** (r = 74), onde a seção cai para a espiga.
- **Espiga 11 × 6.** É a seção mais fraca do braço e fica dentro do painel; não
  dá para reforçar sem refazer os painéis.
- **Motor.** Furação, altura da pilha e eixo do AX-2810Q não foram modelados;
  medir também a folga do eixo.
- **Placa própria.** Envelope máximo reservado: disco Ø74 com dois retos em
  y = ±30, 16 mm de altura, quatro furos M2 em r = 35,5 a 50°, 110°, 230° e 290°.
- **Invólucro.** A canaleta do cilindro não existe nesta variante.
- **Medir antes de girar:** frequência por impacto montado, massa real do palco
  e balanceamento.

## 13/11/2026 — chapa do motor provisória em PLA

O furo central da chapa R01 enganchava no fundo do AX-2810Q. Na variante ele passou de
Ø8 para **Ø11**, o maior que ainda deixa alma (0,8 mm) até os furos M3 do motor em r = 8.
A 3.0.5 mantém Ø8. Até a chapa de alumínio ser cortada (o DXF já sai com Ø11), usar a
réplica impressa em PLA: `teste_impresso/R01T_placa_teste_PLA_2mm.stl` e `_Creality.gcode`
(210/60 °C, 100 % maciço, ~30 min, 7,5 g), gerada com
`python3 scripts/r01_placa_teste.py --material PLA --parameters CAD/parameters_paralelogramo.json`.

## 13/11/2026 — altura do assento medida

Pedro mediu **29 mm** da base do motor ao topo da base serrilhada (o modelo tinha 31).
Modelado como campânula 26 (catálogo) + serrilhado 3, o caso de menor folga entre cubo e
campânula; eixo liso e rosca acima do assento não dependem dessa divisão. Datum B na
chapa: 37 → 35; torre 135 → 137 para manter o Datum B em 186. 69/69.

Arruela do eixo: o disco Ø20 da chapa tinha furo Ø8,5 (A2212), largo o bastante para a
porca M4 passar; agora Ø4,3 (alumínio) e Ø4,5 na réplica em PLA, que sai no mesmo G-code
da chapa. A de PLA (2 mm) é provisória: aperto leve, sobra ~2 mm de rosca acima da porca.

STLs separados no próprio build (`motor_plate.printed_replica`): `exports/stl/R01P_suporte_motor_PLA_provisorio.stl`
e `exports/stl/R01P_arruela_eixo_M4_PLA_provisoria.stl`, validados com as demais peças. A 3.0.5 não os gera.
