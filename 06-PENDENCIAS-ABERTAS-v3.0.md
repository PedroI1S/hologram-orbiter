# Pendências abertas — Hologram Orbiter v3.0

O que **falta**, depois da revisão independente de 02/09 e das correções já
aplicadas. Itens resolvidos foram removidos deste documento; a memória do que
mudou está no histórico do repositório.

**Última atualização:** 02/09/2026

---

## A. Bloqueia a impressão dos painéis

Dois defeitos de malha, confirmados por ray cast independente. Causa comum:
`subtract_all()` em `CAD/generate.py` concatena os cortadores com
`bpy.ops.object.join()` — concatenação, não união booleana — e faz uma única
DIFFERENCE. Onde dois cortadores se sobrepõem, o operando tem enrolamento 2 e o
resultado é 1 − 2 = **−1**.

### A1 · Cascas invertidas nos furos M3

Varredura ao longo do eixo do parafuso, em r = 80 e r = 90:

```
x = -18,0 … -15,2   enrolamento -1   pino dentro do bolso da porca
x = -15,2 …  -3,1   vazio            furo aberto (correto)
x =  -3,1 …  +3,1   enrolamento -1   barra atravessando o socket
```

O fatiador pode imprimir isso como sólido: painel sem furo útil e socket
obstruído. Está nos três exemplares do STL de lote.

**Por que passou:** a casca continua fechada, cada aresta continua com duas
faces e o volume negativo de −0,145 cm³ some dentro de 30,45 cm³. Nem o
validador do pacote nem o meu olham enrolamento local.

### A2 · Membrana de espessura zero no canal do LED

Em X = −98,5, na junção entre o bolso de fios e o canal, há um par de faces
coincidentes de normais opostas. Fatiador com detecção de paredes finas pode
extrudar um filete de 0,4 mm cruzando o canal, exatamente onde a fita assenta.

**Correção:** unir os cortadores antes da diferença, e fazer o bolso invadir o
canal em 0,2 mm em vez de tangenciá-lo.

---

## B. Entra na mesma regeneração

| # | Item | Situação atual | Alvo |
|---|---|---|---|
| B1 | Ombro da longarina | r = **74,2** — o painel assenta em 100,2 e o critério "100 ±0,1" reprova | extrudar o aerofólio até 74,0 e sobrepor só pelo lado da espiga |
| B2 | Critérios de aceitação | `acceptance()` compara `assembly.panel_radius` consigo mesmo; sete dos critérios são tautologia | medir na malha: raio, socket livre, furo livre, parede mínima |
| B3 | Cortador da flange | corta de z = −1 até o topo da torre e atravessa o piso da baia — 4 furos inúteis sob o ponto mais carregado | limitar à flange superior |
| B4 | Poste do ímã | preso sob a cabeça de **um único M4**; nada impede a aba de girar, e o azimute é a referência de fase da imagem inteira | pino de anti-rotação ou segundo furo |
| B5 | Abas de grampo | não existem; a pista de 10 mm tem a canaleta no meio e lábios de 2,8 mm | 3 abas na face externa do anel, furo Ø5, a 120° |
| B6 | `mass_limit_g` da base | 300, e o modelo dá 310 — único critério vermelho | 330 (a base não gira; massa ali só ajuda) |
| B7 | Tampa de invólucro | `07_tampa_contencao_ABS.stl` existe no pacote | **remover** — fora de escopo |
| B8 | `validate_stl.py` | checa aresta, degeneração e sinal do volume total | acrescentar **teste de enrolamento por raios** e **faces coincidentes** |

---

## C. Falta no esquema elétrico e na lista

### C1 · Não existe fonte do sinal de acelerador

O ESC precisa de sinal servo (PWM 1–2 ms) e **nada no projeto o gera**. A parte
fixa tem motor, ESC e fonte de bancada — nenhum microcontrolador, servo-tester
ou rádio.

Rampa ≥ 8 s, redução de potência de partida, parada por software e modo governor
são funções desse gerador, **não do ESC**. Acrescentar Arduino ou servo-tester
com rampa ao esquema e à lista, com parada de emergência física na fonte.

### C2 · LVC do ESC pode cortar na tensão de trabalho

O esquema manda operar a fonte em 6–7 V para o ESC trabalhar em duty alto. Um
ESC com detecção automática de células pode identificar 2S e cortar em 6,0–6,6 V.
**Desabilitar o LVC ou operar em 7,4 V.** Confirmar antes da Fase 3.

### C3 · Polaridade do ímã não está documentada

O A3144 é **unipolar**: comuta com um polo só. Se o ímã for colado invertido, não
há pulso de índice — e o sintoma parece falha de firmware. Definir e cotar qual
face do ímã aponta para o sensor.

### C4 · Campo do motor sobre o sensor

O sensor gira a ~15 mm do rotor de ímãs do motor. Esse campo é estático em
relação ao sensor e pode mantê-lo permanentemente ligado ou desligado.
**Verificar com o motor montado, antes de colar.**

---

## D. Depende de medição, não de projeto

### D1 · Espessura real da fita — pode mover a térmica em 28 %

A especificação registra a HD107S com **1,0 mm**. Um encapsulamento 5050 tem
1,6 mm só de LED: 1,0 mm só fecha se o que foi medido foi o PCB sem o
componente.

Se os LEDs sobressaírem ~1,4 mm, viram 29 cubos de 5 mm de frente por painel —
A·Cd ≈ 200 mm² a r = 104:

| | Estimativa atual | Com LEDs sobressaindo |
|---|---:|---:|
| Torque | 46,1 mN·m | ~60 mN·m |
| Corrente de fase | 4,44 A | ~5,6 A |
| Temperatura do motor | 43 °C | ~52 °C |

**O cupom C02 com a fita real resolve isso em 10 minutos**, antes de qualquer
conta de arrasto.

### D2 · Layout da baia com massas reais

A baia é **intrinsecamente assimétrica**: buck numa parede, MCU na oposta,
capacitor eletrolítico de ~2,5 g num segmento lateral. O capacitor sozinho, a
r ≈ 25 mm, vale **62 g·mm** — sete vezes o admissível de 8,4.

"Tudo centrado" não é atingível com peças diferentes em lados diferentes. Precisa
de esboço de layout com as massas e **contrapeso planejado**, não corrigido
depois. É o que decide se a baia precisa crescer.

### D3 · Ensaio de impacto na base

Antes de montar o motor: base impressa na bancada, MPU6050 junto à torre, toque
seco no topo, FFT do decaimento.

O tubo Ø30 × 4 × 150 com 322 g no topo dá k ≈ 50 N/mm e **fn ≈ 63 Hz** — folgado
contra os 30 Hz de excitação. O que essa conta não cobre é o **balanço da base
sobre a mesa**, que depende do contato e da fixação.

Se vier **abaixo de 45 Hz**, o que cresce é a **nervura**, não o pé: piso 100 %
sólido num raio de 40 mm em torno da torre e 4 a 8 gussets da torre para a parede
da baia, que hoje não trabalha.

---

## E. Documental

| # | Item | Ação |
|---|---|---|
| E1 | Sulco de fiação reduz a seção do braço de ~63 para ~47 mm² e desloca o centróide ~2 mm; ~9 MPa, SF ≈ 3 | anotar na especificação; é aceitável, não está registrado |
| E2 | Planos de balanceamento: a spec pede ~90 mg em r = 90; o CAD entregou copos em r = 28 e alívios em r ≈ 24, resolução equivalente **0,3 g** | documentar a resolução real e a separação axial de ~25 mm contra 208 mm de rotor |
| E3 | Energia do painel solto aparece como 7,9 J @ 19,6 m/s e 7,4 J @ 18,9 | adotar **um par só** — 7,4 J @ 18,9 (velocidade no CG, r = 100) |
| E4 | Potência na fonte aparece como 14,4 W e 15,7 W | unificar |
| E5 | "17,2 Mbit/s a 180 colunas" | são 15,4 a 1800 RPM; 17,2 é a 2000 |
| E6 | Raio do hall citado como 37,5 no §6.3 | o CAD usa **29**; refazer o pulso e o campo |
| E7 | Lista do §6.3 termina no primeiro item, com ponto e vírgula | texto truncado |

---

## Fora de escopo

Invólucro e seu assento, e a medição da campânula. O cubo já traz os dois
caminhos de fixação e o aperto está decidido — arruela Ø20 a 0,6 N·m, 1,9 MPa no
ABS. A pista externa mantém a canaleta de 4,4 × 3 mm em r = 135 porque custa nada
e não pode ser acrescentada depois de imprimir; não é item deste projeto.
