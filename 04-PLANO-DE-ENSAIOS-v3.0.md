# Plano de ensaios — Hologram Orbiter v3.0

Cinco bloqueadores. Cada um tem critério numérico, método de medição, limiar de
aborto e caminho de contingência. Nenhum é opcional e nenhum depende de arquivo
que não exista.

> **Por que este plano é diferente do da v2.1.** O critério antigo era
> `I ≤ 5,8 A`, um número cuja derivação estava numa planilha que se perdeu, e que
> além disso não é medível: corrente de fase exige alicate amperímetro numa das
> três fases. Os critérios abaixo são todos lidos em instrumentos que já existem
> na bancada.

---

## Bloqueador A — potência e arrasto

**O que se está de fato verificando:** se o arrasto aerodinâmico real bate com o
estimado. É a maior incerteza do projeto e a entrada de todo o caso térmico.

**Método.** Rotor completo montado e balanceado, sem LEDs acesos. Subir em
patamares de 600, 1000, 1400 e 1800 RPM, 2 min em cada. Ler **tensão e corrente
na fonte de bancada** e calcular a potência de entrada.

| Corrente de fase | P entrada | I na fonte a 7,4 V | T motor prevista | |
|---:|---:|---:|---:|---|
| 3,0 A | 9,0 W | 1,21 A | 34 °C | |
| 4,0 A | 12,7 W | 1,71 A | 40 °C | |
| **4,44 A** | **14,4 W** | **1,95 A** | **43 °C** | ← ponto de projeto |
| 5,0 A | 16,8 W | 2,27 A | 47 °C | |
| 5,5 A | 19,1 W | 2,58 A | 51 °C | limite aceitável |
| 6,0 A | 21,4 W | 2,90 A | 55 °C | abortar |
| 8,0 A | 32,1 W | 4,34 A | 77 °C | parar imediatamente |

**Critério de aceite:** P_entrada **≤ 20 W** a 1800 RPM, em regime estável.

**Limiar de aborto:** P_entrada > 30 W, ou T_motor > 55 °C, o que vier primeiro.

**Se falhar:**
1. Verificar o **sentido de giro** — invertido, o arrasto sobe muito. Bordo de
   ataque deve apontar para o sentido do movimento.
2. Revisar a carenagem do boss: era 54% do arrasto no projeto sem carenagem.
3. Reduzir para 1500 RPM (75 Hz) e reavaliar.
4. Só então considerar reduzir raio ou altura do painel.

---

## Bloqueador B — térmica em regime contínuo

**Método.** Termopar tipo K preso ao corpo do motor com fita de kapton, na
carcaça entre as aletas. Operar 10 min contínuos a 1800 RPM. Registrar a curva
T × tempo a cada 30 s. Medir também a temperatura da baia da base e da chapa.

**Critérios de aceite:**

| Ponto | Limite |
|---|---|
| Corpo do motor | **< 55 °C** e curva estabilizando, sem subida contínua |
| Estrutura ABS próxima ao motor | < 60 °C |
| Bateria no rotor | < 45 °C |
| **Deflexão da ponta do painel** | **crescimento < 0,5 mm após 1 h a temperatura** |

**Limiar de aborto:** 60 °C no motor a qualquer momento.

**Meça a ponta do painel, não só a temperatura.** O ABS flui sob carga
sustentada a quente: com 12–14 MPa e 40–50 °C, o módulo cai a cerca de metade em
~100 h. Marque a posição radial da ponta de um painel com o rotor parado, opere
1 h em regime, pare e meça de novo. Crescimento acima de 0,5 mm indica que a
fluência vai comer a folga radial antes do fim do semestre.

**A curva importa tanto quanto o pico.** Se a temperatura ainda estiver subindo
aos 10 min, o ensaio não passou — repita com 20 min ou aceite que o regime
permanente está acima do limite.

**Se falhar:** o caminho é ventilação, não redução de rotação. A análise mostra
que a diferença entre 68 °C e 99 °C no pior caso de arrasto é **só o coeficiente
de troca térmica**. Verificar se as janelas laterais da baia estão desobstruídas
e se há caminho de ar passando pelo motor. Só depois reduzir RPM.

---

## Bloqueador C — vibração e balanceamento

**O que mudou:** a v2.1 media ζ do coxim. Como o isolador está indefinido e a
montagem inicial é rígida, o que importa agora é a **vibração residual da
estrutura**, que é consequência direta do balanceamento.

**Método, em duas partes.**

**C0 — ensaio de impacto, antes de montar o motor.** Com a base impressa na
bancada, MPU6050 colado junto à torre, dar um toque seco no topo da torre e
registrar o decaimento. FFT dá a primeira frequência natural da parte fixa.

O tubo Ø30 × 4 × 150 sozinho, com 322 g no topo, dá **k ≈ 50 N/mm e fn ≈ 63 Hz**
— confortável contra os 30 Hz de excitação. O que essa conta não cobre é o
**balanço da base sobre a mesa**: ela apoia, não é presa, e sem os furos
periféricos não há onde grampear a pista. Se a medição der **fn < 45 Hz**,
reforce antes de montar o motor: piso 100 % sólido num raio de 40 mm em torno da
torre e 4 a 8 gussets da torre para a parede da baia, que hoje não trabalha.

**C1 — varredura em rotação.** MPU6050 na base, junto à torre. Amostrar a 500 Hz
e **varrer de 600 a 1800 RPM em degraus de 200**, registrando amplitude × rotação.
Medir só a 1800 não distingue ressonância de desbalanceamento: desbalanceamento
cresce com ω², ressonância aparece como pico numa rotação específica. FFT em cada
patamar, lendo **30 Hz** (1× rotação) e 60 Hz (2×).

**Critérios de aceite:**

| Grandeza | Limite |
|---|---|
| Pico a 30 Hz | ≤ 0,20 g |
| Pico a 60 Hz | ≤ 0,10 g |
| Crescimento em 10 min | nenhum |
| Desbalanceamento residual | ≤ **8,4 g·mm** |

**Balanceamento, em duas etapas antes deste ensaio:**

1. **Estático, na bancada** — pesar os três painéis numa balança de **0,01 g** e
   casar em **≤ 0,084 g**. Se não casar, corrigir com massa adesiva antes de
   montar.
2. **Dinâmico, em rotação** — com o acelerômetro, método da massa de teste:
   medir a fase e a amplitude do pico de 30 Hz, adicionar massa conhecida numa
   posição angular conhecida, medir de novo, resolver o vetor de correção.
   Resolução necessária: **~90 mg em r = 90 mm**.

**Se falhar:** repetir o balanceamento em dois planos. Se persistir, procurar
excentricidade da bateria (48 g deslocados 1 mm já dão 48 g·mm, seis vezes o
admissível) ou empeno de painel.

---

## Bloqueador D — partida

**Bloqueador novo.** O rotor tem **1,55 g·m²**, cerca de **100 vezes** a inércia
de uma hélice 1045. ESCs sensorless são sintonizados para hélice, e partida com
inércia alta é o modo de falha clássico: o motor perde sincronismo e trava.

**Método.** Com o rotor completo, rampa configurada em **≥ 8 s**, executar 10
partidas consecutivas do repouso até 1800 RPM.

**Critérios de aceite:**
- 10 de 10 partidas bem-sucedidas, sem travamento nem ruído de dessincronismo;
- pico de corrente na fonte durante a rampa ≤ **4,5 A a 7,4 V** (equivale a 8,0 A
  de fase);
- nenhum evento de proteção do ESC.

**Se falhar:**
1. Alongar a rampa para 12 s (baixa o pico para 7,3 A de fase).
2. Reduzir a potência de partida nas configurações do ESC.
3. Ajustar a fonte para 6–7 V, o que faz o ESC operar em duty mais alto e melhora
   a resolução de comutação em baixa rotação.
4. Se nada resolver, o caminho é um ESC sensored ou um controlador FOC.

---

## Bloqueador E — qualidade visual

**Método.** Ambiente escuro, imagem de teste com padrões de alto contraste:
grade fina, texto pequeno e bordas verticais. Observar a 1, 2 e 3 m de distância,
parado e com movimento rápido dos olhos (sacada). Registrar com celular a 240 fps.

**Critérios de aceite:**
- imagem estável, sem jitter perceptível em sacada;
- as três varreduras coincidem — nada de imagem "tripla" ou borrada;
- sem cintilação perceptível em visão periférica.

**Se falhar, o diagnóstico vem antes da correção:**

| Sintoma | Causa provável | Correção |
|---|---|---|
| Imagem tripla ou fantasma | Δh ou raio diferentes entre painéis | remedir Datum D e o raio; reimprimir o painel fora |
| Deslocamento angular entre varreduras | folga na junta espiga/socket | apertar; verificar as porcas nyloc |
| Borda vertical serrilhada | jitter de fase do sensor de índice | verificar entreferro e histerese do hall |
| Imagem "respirando" ou cisalhada | rotação instável entre voltas | ativar o **modo governor** do ESC — ver abaixo |
| Cintilação periférica | 90 Hz insuficiente para o brilho usado | reduzir brilho, ou subir para 2000 RPM se A e B passarem |

---

**Sobre a imagem "respirando".** O sensor de índice zera a fase a cada volta, então
o erro não acumula — mas dentro de cada volta ele cresce proporcionalmente à
variação de rotação desde a volta anterior. Para manter o desvio abaixo de 1/4 de
coluna, a rotação precisa ser estável dentro de **~0,14 %** de uma volta para a
outra. Se falhar aqui, a correção é controle de rotação em malha fechada no ESC,
não ajuste mecânico.

---

## Sequência e portões

```
G0  CAD entregue e verificado contra os critérios do §9 da especificação
     └─ cupons impressos, junta e canal conferidos com a fita real

G1  Lote impresso e verificado
     └─ massa ≤ 45 g por painel · Δm ≤ 0,084 g · Datum D 104 ±0,2 · raio 100 ±0,1

G2  Montagem mecânica e balanceamento estático
     └─ rotor montado sem LEDs · painéis casados em massa

G3  Bloqueadores A, B, C, D   ← ensaios de rotação, sem LEDs
     └─ P ≤ 20 W · T < 55 °C · vibração ≤ 0,20 g · 10/10 partidas

G4  Integração óptica
     └─ fita, ESP32, sensor de índice, imagem de teste

G5  Bloqueador E e demonstração
```

**Nada de LEDs antes de G3.** Os ensaios de rotação são os de maior risco físico;
adicionar eletrônica de bordo antes deles só aumenta o que se perde numa falha.

---

## Regras de segurança em ensaio de rotação

Não são formalidade. O rotor guarda **26 J** e um painel solto sai a
**18,9 m/s** com 7,4 J.

- **Nunca girar sem o cilindro de policarbonato montado.** Se ele ainda não tiver
  chegado, use contenção externa provisória: caixa fechada, chapa ou tela de aço.
- **Operação remota.** Ninguém no plano do rotor durante a subida de rotação.
- **Parada de emergência** ao alcance, cortando a fonte.
- **Subir em patamares** com inspeção entre eles. Nunca ir direto a 1800.
- Após qualquer reimpressão ou remontagem, **refazer o balanceamento**.
- **Grampear a base à bancada** antes de qualquer ensaio de rotação. Ela tem
  310 g e não tem furos de fixação.
- Óculos de proteção, sempre.
