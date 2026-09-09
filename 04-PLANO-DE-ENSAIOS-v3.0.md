# Plano de ensaios — Hologram Orbiter v3.0

Cinco bloqueadores. **Revisados em 08/09/2026; nenhum ensaio físico consta como
aprovado.** A instrumentação térmica, a referência angular e a identificação
em dois planos precisam ser fechadas antes dos ensaios correspondentes. As
correções digitais não liberam a estrutura para girar; resolver antes as
pendências mecânicas da revisão completa.

> **Por que este plano é diferente do da v2.1.** O critério antigo era
> `I ≤ 5,8 A`, um número cuja derivação estava numa planilha que se perdeu, e que
> além disso exige instrumentação apropriada à corrente comutada de fase. A
> leitura na fonte é realizável, mas não comprova diretamente corrente de fase;
> a conversão usada abaixo é uma estimativa com hipóteses explícitas.

---

## Bloqueador A — potência e arrasto

**O que se está de fato verificando:** se o arrasto aerodinâmico real bate com o
estimado. É a maior incerteza do projeto e a entrada de todo o caso térmico.

**Método.** Rotor completo montado e balanceado, sem LEDs acesos. Subir em
patamares de 600, 1000, 1400 e 1800 RPM, 2 min em cada. Ler **tensão e corrente
na fonte de bancada** e calcular a potência de entrada.

| Corrente de fase | P entrada | I na fonte a 7 V | T motor prevista | |
|---:|---:|---:|---:|---|
| 3,0 A | 9,0 W | 1,29 A | 34 °C | |
| 4,0 A | 12,7 W | 1,81 A | 40 °C | |
| 4,44 A | 14,47 W | **2,07 A** | 43 °C | melhor caso (Cd do boss 0,20) |
| **4,95 A** | **16,63 W** | **2,38 A** | **46 °C** | ← **ponto de projeto** (Cd do boss 0,35) |
| 5,0 A | 16,85 W | 2,41 A | 47 °C | |
| 5,5 A | 19,1 W | 2,73 A | 51 °C | limite aceitável |
| 6,0 A | 21,47 W | 3,07 A | 55,3 °C | previsão acima do limite térmico |
| 8,0 A | 32,1 W | 4,59 A | 77 °C | parar imediatamente |

**Critério de aceite:** P_entrada **≤ 20 W** a 1800 RPM, em regime estável.

Tabela derivada de `P_entrada = (Kt·ω·I + 0,221·I² + 0,7)/0,95`, com
Kt=0,0103797 N·m/A, ω=188,496 rad/s e eficiência de ESC assumida de 95%.
Temperatura prevista: `25 + 3,5·(0,221·I² + 0,7)` °C. R e Rth continuam
hipóteses; medir potência não identifica sozinho torque ou perdas do motor.

**Limiar de aborto:** P_entrada > 30 W, ou T_motor **≥ 55 °C**, o que vier
primeiro. Este limite de potência é de regime; o pico de partida tem o critério
próprio do bloqueador D.

**Se falhar:**
1. Verificar o **sentido de giro** — invertido, o arrasto sobe muito. Bordo de
   ataque deve apontar para o sentido do movimento.
2. Revisar a carenagem do boss: era 54% do arrasto no projeto sem carenagem.
3. Reduzir para 1500 RPM (75 Hz) e reavaliar.
4. Só então considerar reduzir raio ou altura do painel.

---

## Bloqueador B — térmica em regime contínuo

**Instrumentação — pendente.** A campânula do A2212 gira. **Não prender nela
um termopar com cabo ligado a leitor estacionário.** Para medir a superfície
girante, selecionar medição sem contato com emissividade, tamanho do ponto e
reflexões controlados, validada contra referência de contato com o motor parado,
ou um sensor embarcado com retenção e transmissão de dados qualificadas.
Termopar na chapa/assento fixo mede esse ponto, não automaticamente o motor;
só usar como substituto após estabelecer uma correlação térmica conservadora.
Registrar o ponto medido e a incerteza. Sem método qualificado, B permanece aberto.

**Método, após fechar a instrumentação.** Operar 10 min contínuos a 1800 RPM.
Registrar T × tempo a cada 30 s. Termopares estacionários podem medir a estrutura
ABS, a baia da base e a chapa. Na decisão de aceite/aborto, considerar a
incerteza da medição no sentido conservador.

**Critérios de aceite:**

| Ponto | Limite |
|---|---|
| Temperatura do motor pelo método qualificado | **< 55 °C** e curva estabilizando, sem subida contínua |
| Estrutura ABS próxima ao motor | < 60 °C |
| Bateria no rotor | < 45 °C — **só quando houver bateria embarcada**; ver nota |
| **Deflexão da ponta do painel** | **crescimento < 0,5 mm após 1 h a temperatura** |

**Limiar de aborto:** motor **≥ 55 °C**, ABS próximo ao motor ≥ 60 °C ou
bateria ≥ 45 °C, quando embarcada. Falha da medição também interrompe o ensaio.

**Sobre a linha da bateria.** O bloqueador B roda na fase 3, e a fase 3 é
explicitamente *sem LEDs e sem eletrônica de bordo* (portão G3). Nessa passagem
não há bateria no rotor para medir. A linha vale como critério **na repetição do
ensaio B em G4**, com a eletrônica montada — que é quando a bateria de fato gira
em torno do eixo, dentro de uma baia fechada. A bateria exige sensor embarcado
calibrado com telemetria ou registro local, cuja massa, retenção e montagem
ainda precisam ser definidas. Medir depois de parar não demonstra o pico em
operação. Em G3, registrar "não aplicável"; em G4, manter B aberto até existir
medição realizável e evidência da temperatura.

**Meça a ponta do painel, não só a temperatura.** O ABS flui sob carga
sustentada a quente. A revisão da seção elevou a tensão prevista para
~21,7–28,8 MPa (44,5 g), chegando a ~29,1 MPa com o teto de 45 g no modelo simplificado; a lei de fluência do material impresso
não foi medida. Antes do ensaio de 1 h é necessário liberar o caso estrutural
revisto. Marque a posição radial da ponta de um painel com o rotor parado, opere
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

**C0 — ensaio de impacto, antes de energizar o motor.** Com a base impressa na
bancada, MPU6050 colado junto à torre, dar um toque seco no topo da torre e
registrar o decaimento. FFT dá a primeira frequência natural da parte fixa.

**Ensaie com massa na ponta, ou o ensaio não mede nada.** A torre nua, batida
sem massa no topo, ressoa em centenas de hertz: o gatilho de 45 Hz abaixo nunca
dispararia e o ensaio passaria sempre. Fixe no eixo uma **massa fictícia de
~280 g** na altura do plano dos painéis (um disco de aço na porca M6 serve), ou
monte o rotor real parado, e só então bata na torre.

O tubo Ø30 × 4 × 150 dá **k ≈ 50 N/mm**. Com a massa concentrada **no topo do
tubo** isso daria fn ≈ 63 Hz, e é esse o número que os documentos vinham
publicando — mas a massa não está no topo. O CG do conjunto (rotor 279 g +
motor 52 + chapa 18 = **349 g**, e não os 322 g da base, que é outra peça) fica
em Z ≈ 185, **31 mm acima do topo da torre** (Z = 154). Para massa deslocada de
`a` por um trecho rígido:

```
k_eff = k / (1 + 3a/L + 3a²/L²) = 50 / (1 + 0,62 + 0,13) ≈ 29 N/mm
fn    ≈ (1/2π)·√(29 000 / 0,349) ≈ 46 Hz
```

e isso ainda ignora a inércia de rotação do rotor de 208 mm, a flexibilidade da
flange, da chapa e dos rolamentos do motor (todas abaixam) e o efeito
giroscópico a 1800 RPM (sobe o modo direto). **O número honesto é ≈ 45 Hz** — em
cima do próprio limiar de reforço, com transmissibilidade a 30 Hz de ~1,7 a 1,9
em vez dos 1,3 que 63 Hz prometia. Meça antes de acreditar em qualquer um dos
dois.

O que a conta também não cobre é o **balanço da base sobre a mesa**: ela apoia, e
é presa só pelas quatro abas de grampo nos cantos do anel. Medir grampeada e
solta. Se a medição der **fn < 45 Hz**, reforce antes de montar o motor: piso
100 % sólido num raio de 40 mm em torno da torre e 4 a 8 gussets da torre para a
parede da baia, que hoje não trabalha.

**C1 — varredura em rotação.** Acelerômetro na base, junto à torre. Amostrar a 500 Hz
e **varrer de 600 a 1800 RPM em degraus de 200**, registrando amplitude × rotação.
Medir só a 1800 não distingue ressonância de desbalanceamento: desbalanceamento
cresce com ω², ressonância aparece como pico numa rotação específica. FFT em cada
patamar, lendo **1× e 2× a rotação efetiva** (30 e 60 Hz somente a 1800 RPM).
Definir escala, filtro antialias, janela de FFT e calibração da amplitude;
os limites abaixo são amplitudes de pico, não valores RMS.

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
2. **Dinâmico em dois planos — instrumentação pendente.** Instalar uma
   referência **1 pulso/volta fixa**, observando uma marca no rotor e registrada
   na mesma base de tempo dos sinais de vibração. O Hall embarcado de G4 e uma
   leitura numérica de RPM não fornecem essa referência em G3. Usar duas
   respostas complexas independentes, por exemplo dois pontos de medição em
   alturas distintas da estrutura fixa; comprovar independência, não presumir
   que dois eixos do mesmo MPU bastam.

   Fazer três ensaios separados, na mesma rotação e condição de montagem:
   baseline sem massa de teste; massa conhecida somente no plano 1, medindo
   ambos os canais; retirar essa massa e testar somente o plano 2, novamente
   medindo ambos. Para cada plano, registrar massa, raio e fase. Montar a matriz
   complexa 2 × 2 de coeficientes de influência `A_ij = (V_ij − V_i0)/U_teste_j`
   e resolver `A·U_correcao = −V_0`. Se a matriz for singular ou mal condicionada,
   mudar os pontos/condições de medição; não emitir dois contrapesos de uma só
   resposta. Aplicar a correção e repetir uma medição independente do resíduo.

   Registrar o resíduo estimado em cada plano e a incerteza. Usar como teto
   conservador provisório `|U_1| + |U_2| ≤ 8,4 g·mm`, recalculado para a massa
   real conforme a spec §2.1; isso não substitui um limite qualificado de binário
   nem a avaliação dos modos. Vibração baixa sozinha não comprova esse U.
   [Método de balanceamento, Brüel & Kjær](https://www.bksv.com/media/doc/17-227.pdf).

   No CAD: plano 1 nos alívios inferiores do cubo (r 17–36); plano 2 nos copos
   da tampa (r = 34). A correção nominal de catálogo de 2,19 g a 180° e 0,86 g
   a 300° é apenas a compensação inicial do layout e pode mudar ao regenerar.
   Em r = 34, 0,1 g produz 3,4 g·mm; a balança de 0,01 g resolve incrementos
   de 0,34 g·mm nesse raio. Verificar retenção e capacidade dos alojamentos reais.

**Se falhar:** repetir o balanceamento em dois planos. Se persistir, procurar
excentricidade da bateria (50 g deslocados 1 mm já dão 50 g·mm, seis vezes o
admissível) ou empeno de painel.

---

## Bloqueador D — partida

**Bloqueador novo.** O rotor tem **1,55 g·m²**, cerca de **100 vezes** a inércia
de uma hélice 1045. ESCs sensorless são sintonizados para hélice, e partida com
inércia alta é o modo de falha clássico: o motor perde sincronismo e trava.

**Método.** Com o rotor completo, rampa nominal configurada em **≥ 12 s**, executar 10
partidas consecutivas do repouso até 1800 RPM.

Confirmar a curva de RPM: uma rampa linear de pulso servo não garante uma
rampa linear de velocidade. Com J=0,00155 kg·m² e arrasto de 51,4 mN·m, a
aceleração linear em 12 s exige 24,35 mN·m e prevê **7,30 A de fase**,
~28,17 W / **4,02 A na fonte de 7 V**, usando η_ESC=95%. Em 8 s seriam
**8,47 A de fase / 4,98 A na fonte**, fora do limite. O mínimo matemático para
8 A é ~9,23 s, sem margem; não é a rampa nominal.

**Critérios de aceite:**
- 10 de 10 partidas bem-sucedidas, sem travamento nem ruído de dessincronismo;
- pico de corrente na fonte durante a rampa ≤ **4,6 A a 7 V** (32,1 W / 7 V, a
  mesma linha da tabela do bloqueador A; estimativa equivalente a 8,0 A
  de fase nesse modelo, não uma medição de corrente de fase);
- nenhum evento de proteção do ESC.

**Se falhar:**
1. Alongar a rampa além dos 12 s nominais, medir a aceleração e recalcular
   `I_fase=(J·ω/t + 0,0514)/0,0103797`. Manter o teto de 4,6 A na fonte a 7 V.
2. Reduzir a potência de partida nas configurações do ESC.
3. Ajustar a fonte para 6–7 V, o que faz o ESC operar em duty mais alto e melhora
   a resolução de comutação em baixa rotação.
4. **Desabilitar o "Low RPM power protect"** do BLHeli_S. A 1800 RPM estamos a
   26 % da rotação a vazio, exatamente o regime que essa proteção limita; o
   manual indica desabilitá-la para motores de baixo kv em tensão baixa. Em
   troca, aumenta o risco de perda de sincronismo — ajuste de bancada.
5. **Desabilitar o "Brake on stop".** O BLHeli_S freia com regeneração, e uma
   fonte de bancada não afunda corrente: frear 27,6 J empurra o barramento para
   cima.
6. Se nada resolver, o caminho é um ESC sensored ou um controlador FOC.

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
| Deslocamento angular entre varreduras | atraso de atualização serial ou folga na junta | medir temporização/compensação por LED; conferir junta e fase mecânica |
| Borda vertical serrilhada | jitter de fase do sensor de índice | verificar entreferro e histerese do hall |
| Imagem "respirando" ou cisalhada | rotação instável entre voltas | **o BLHeli_S não tem governor** — ver abaixo |
| Cintilação periférica | 90 Hz insuficiente para o brilho usado | reduzir brilho; 2000 RPM não liberados pelo cálculo atual |

---

**2000 RPM não estão liberados.** No mesmo arrasto de projeto, a previsão é
`4,95·(2000/1800)² = 6,11 A` e **56,3 °C**, acima do limite de 55 °C.
Uma mudança de rotação exige novo caso mecânico/elétrico e repetição dos
bloqueadores aplicáveis; passar a 1800 RPM não autoriza essa extensão.

**Sobre a imagem "respirando".** O sensor de índice zera a fase a cada volta, então
o erro não acumula — mas dentro de cada volta ele cresce proporcionalmente à
variação de rotação desde a volta anterior. Para manter o desvio abaixo de 1/4 de
coluna, a rotação precisa ser estável dentro de **~0,14 %** de uma volta para a
outra. A inércia de 1,55 g·m² ajuda muito nisso.

Se falhar aqui, **não procure ajuste mecânico e não procure o modo governor**: o
BLHeli_S não tem malha fechada de rotação. Ou se aceita a variação, ou se troca
o firmware por um com telemetria de RPM.

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
     └─ instrumentação qualificada · P ≤ 20 W · T < 55 °C · C em dois planos · 10/10 partidas

G4  Integração óptica
     └─ fita, ESP32, sensor de índice, imagem de teste; repetir A–D no rotor final

G5  Bloqueador E e demonstração
```

**Nada de LEDs antes de G3.** Os ensaios de rotação são os de maior risco físico;
adicionar eletrônica de bordo antes deles só aumenta o que se perde numa falha.
Usar lastro retido que represente massas, posições e inércia dos itens ausentes,
inclusive fitas e chicotes; registrar a configuração de cada ensaio. Lastro
central de massa total igual não reproduz automaticamente o rotor final.
Após integrar os componentes reais em G4, repetir balanceamento e A–D; incluir
a medição da bateria em B e a qualificação de corrente/temperatura do buck.

---

## Regras de segurança em ensaio de rotação

Não são formalidade. O rotor guarda **27,6 J** e um painel solto sai a
**18,9 m/s** com 7,9 J.

- **Nunca girar sem contenção integral.** Caixa fechada, chapa ou tela de aço em
  torno do rotor. Não há exceção para "só um teste rápido".
- **Operação remota.** Ninguém no plano do rotor durante a subida de rotação.
- **Parada de emergência** ao alcance, cortando a fonte. Ela corta a
  alimentação, **não para o rotor**: com *brake on stop* desabilitado (decisão
  correta para a fonte de bancada) o rotor entra em roda livre e o arrasto cai
  com ω². A constante de tempo é `I·ω/T = 1,55e−3 × 188,5 / 0,046 ≈ 6 s` e a
  rotação decai como `ω₀/(1 + t/τ)`: metade em 6 s, um décimo em ~1 min, com os
  27,6 J ainda dentro da contenção nos primeiros segundos.
- **Ninguém abre a contenção antes de o rotor parar — no mínimo 90 s após o
  corte, e só com o rotor visivelmente imóvel.** Se for preciso frear de fato,
  use um resistor de descarga no barramento do ESC; nunca a fonte.
- **Subir em patamares** com inspeção entre eles. Nunca ir direto a 1800.
- Após qualquer reimpressão ou remontagem, **refazer o balanceamento**.
- **Grampear a base à bancada** pelas abas externas do anel (quatro, nos
  cantos; três bastam) antes de qualquer ensaio de rotação. Ela tem 321 g e
  caminha se o contato for ruim.
- Óculos de proteção, sempre.
