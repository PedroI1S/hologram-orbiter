# Lista de componentes — Hologram Orbiter v3.0

Revisada em 08/09/2026; pull-downs do 74AHCT125 acrescentados em 21/09/2026. Preços em BRL são **estimativas de ordem de grandeza**
para orçamento, não cotações.

Componentes em mãos não significam montagem validada. O buck e a instrumentação
de temperatura, fase e balanceamento continuam sem qualificação. As massas CAD
da tabela são referências anteriores à revisão 3.0.4; conferir o relatório
regenerado e pesar o conjunto com os seis condutores por painel.

Legenda: ✅ já temos · 🛒 comprar · ⚠️ decisão pendente

---

## 1. Peças impressas — ABS

Todas saem do gerador paramétrico. Ver [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md).

| # | Peça | Qtd | Volume (CAD) | Massa maciça (CAD) | Limite | Tempo |
|---|---|---:|---:|---:|---|---|
| 01 | Aranha (com pilares e guias da baia) | 1 | 68,3 cm³ | 71,06 g | ≤ 75 g (alvo) | 5–6 h |
| 02 | Painel LED | 3 | 30,7 cm³ ea. | 31,9 g nu | ≤ 45 g montado | 8–10 h (lote) |
| 03 | Tampa da baia Ø82 | 1 | 9,7 cm³ | 10,1 g | ≤ 12 g (alvo) | 30 min |
| 04/05 | Base + torre integradas, 4 abas | 1 | 307 cm³ | 320 g | ≤ 330 g (alvo) | 12–18 h |
| 06 | Suporte do ímã (dois parafusos) | 1 | 1,7 cm³ | 1,7 g | — | 15 min |
| C01 | Cupom da junta 11 × 6 | 1 | 9,7 cm³ | 10,1 g | — | 15 min |
| C02 | Cupom do canal do LED (fatia real de 30 mm do painel) | 1 | 3,4 cm³ | 3,5 g | — | 10 min |

**Total: ~490 cm³ ≈ 0,5 kg em densidade maciça** (menos com infill). Comprar
**1 kg** — o refugo em ABS é real e os painéis podem precisar de segunda
tiragem por massa fora de tolerância.

**Imprimir os cupons primeiro.** Custam 25 minutos e evitam refazer um lote de
painéis de 208 mm por causa de folga na junta ou no canal.

---

## 2. Acionamento

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Motor BLDC | **A2212 920KV**, 2–4S, 52 g, eixo M6, base 4×M3 em 16 × 19 mm | ✅ | — |
| ESC | **LittleBee Spring 20A**, BLHeli_S, 25 × 13 mm | ✅ | — |
| Fonte de bancada | ajustável; operar em **6–7 V**, ≥ 5 A | ✅ | — |
| Gerador do sinal do ESC | **Arduino em mãos**; firmware de rampa nominal **≥ 12 s** e botão de parada ainda a implementar — ver §8 do esquema | ✅ | — |
| **Arruela Ø20 × Ø8,5 × 2 mm, alumínio** | cortar da mesma chapa da R01 (a referência de corte traz o disco). O furo precisa passar pelo **colar Ø8 do eixo**, que sobe 5–7 mm acima da campânula: uma arruela M6 assentaria no colar e a porca não apertaria o cubo. Alternativa de prateleira: DIN 125 M8 em aço (Ø16; 3,4 MPa no ABS) | 🛒 | — |
| **Porca M6 fina DIN 439B** (3 mm) + Loctite 243 | **não** a cônica de 14 mm que veio com o motor, **nem** a autotravante baixa de 6 mm: com o colar até 5–7 mm e a rosca acabando em 12–14, a de 6 mm terminaria no fim do eixo. Apertar a **0,6 N·m** | 🛒 | 2 |


> **Aperte a 0,6 N·m, com arruela Ø20.** O atrito precisa transmitir 46 mN·m, o
> que exige só ~22 N. A 0,6 N·m a força é de 500 N — 23× de margem — e a tensão
> no ABS fica em 1,9 MPa. Com arruela M6 padrão e 3 N·m daria 40 MPa, a tensão de
> escoamento, e a junta relaxaria em horas.

---

## 3. Óptica e eletrônica de bordo

Tudo isto gira junto com o rotor.

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Fita LED | **HD107S 144 LED/m**, RGB, 1 m — medida em **12,0 × 2,0 mm** | ✅ | — |
| Microcontrolador | **ESP32-C3 Super Mini** (~22 × 18 mm) | ✅ | — |
| Regulador 5 V | módulo exato **pendente de qualificação** de entrada, corrente contínua e térmica. Mini560 (envelope estimado 22 × 17 × 6 mm, ~2 g) é candidato; **não comprar antes de C7**. Exatamente 5 A não cobre branco pleno; ver limite provisório abaixo | ⚠️ | 15 |
| Bateria | **LiFePO4 2S 800 mAh 20C**, 58 × 30 × 17 mm, 50 g, 6,6 V | ✅ | — |
| Conectores | **XT30 para potência** e **JST-XH de 3 vias para balanceamento**; verificar peças e contatos reais | 🛒 | 8 |
| Chave liga/desliga | componente miniatura com capacidade DC compatível com a corrente de entrada do buck; **curso tangencial** — confirmar datasheet e nota | ⚠️ | 5 |
| Sensor de índice | **A3144 nu**, dessoldado do módulo HW-477 — **no rotor** | ✅ | — |
| Resistor de pull-up | 10 kΩ, do sinal do hall para **3,3 V** | 🛒 | 1 |
| Resistores de pull-down | 2 × 10 kΩ, das entradas CLK e DATA do 74AHCT125 ao **GND** (esquema §2.2) | 🛒 | 1 |
| Deslocador de nível | **74AHCT125** para CLK e DATA, com `/OE` definidos e **100 nF cerâmico** junto ao CI; buck em 4,5 V não garante nível lógico | 🛒 | 5 |
| Divisor da bateria | 150 kΩ / 47 kΩ + 100 nF no ADC; tolerâncias e calibração a verificar | 🛒 | a cotar |
| Proteção da alimentação | fusível/polyfuse nominal 7,5 A do esquema: selecionar modelo, corrente de manutenção a quente e coordenação com fios/chave | ⚠️ | a cotar |
| Capacitor de bulk | 1000 µF / 10 V na entrada da fita | 🛒 | 3 |
| Ímã | neodímio Ø4 × 2 mm — **na parte fixa** | 🛒 | 2 |
| Fio de potência | **AWG 24**, 2 cores, ~3 m | 🛒 | 12 |
| Fio de sinal | AWG 28, 2 cores, ~3 m | 🛒 | 8 |
| Fita de poliéster transparente | 0,05–0,1 mm, retenção mecânica da fita LED | 🛒 | 15 |
| Carregador **modo LiFe** | 3,6 V/célula — modo LiPo (4,2 V) destrói o pack | ⚠️ | 60 |

> **Empacotamento — a baia foi ampliada por causa disto.** Bateria, MCU,
> **Tudo o que vai na baia sofre 98 a 114 g.** A aceleração centrífuga em
> r = 27–32 mm é `ω²r` = 960 a 1140 m/s². Duas consequências práticas na compra:
>
> - a **chave** precisa ter o curso **tangencial**, não radial: uma slide com o
>   curso apontando para fora se aciona sozinha sob 100 g;
> - o **capacitor** Ø10 × 20 em pé, com 2,5 g em r = 31,5, leva **2,8 N** de
>   lado no topo. Uma cerca de 3 mm no pé não segura: cole, ou use um polímero
>   SMD deitado. Confirme também que o pack é de **células rígidas** — as pontas
>   dele estão a r = 29.
>
> regulador, deslocador de nível, capacitor, chave e conector numa baia que era
> de Ø66 × 20 mm. Passou para **Ø78 × 29**, com 24 mm úteis acima da porca. Um
> DevKit ESP32 de 55 × 28 mm não caberia junto com a bateria; o C3 Super Mini
> (22 × 18) cabe. O esboço de layout está no CAD (`spider.bay_layout`) e é
> verificado pelo gerador: placa de interface em +x sob a janela da tampa,
> ESP32-C3 em −x, buck em pé na parede, capacitor em pé numa cerca. As massas
> são de catálogo e somam exatamente os 15 g de folga: **pesar cada peça real
> antes de fixar**.

> **Duas armadilhas elétricas que não são opcionais.**
>
> **O A3144 não funciona a 3,3 V** — opera de 4,5 a 24 V. Alimente-o em **5 V** e
> use o pull-up de 10 kΩ para **3,3 V**: como a saída é coletor aberto, o sinal
> oscila de 0 a 3,3 V e a entrada do ESP32-C3, que não tolera 5 V, fica protegida.
> Pull-up para 5 V queima a porta.
>
> **A fita quer V_IH ≥ 3,5 V**. O 74AHCT125 é a solução adotada. Reduzir o buck
> para 4,5 V não assegura compatibilidade: o limiar ~3,15 V ainda excede o
> V_OH mínimo garantido de 2,64 V do ESP32-C3. Ver §2 do esquema e seu datasheet.

> **O pack comprado cabe.** LiFePO4 2S de 58 × 30 × 17 mm deitado ao longo de
> y, sobre trilhos em Z = 9 que passam por cima da arruela e da porca fina (topo
> em Z = 5); o topo do pack fica em Z = 26, dentro dos 29 da baia, e a
> meia-diagonal do berço, 32,3 mm, dentro do raio útil de 39. Paredes laterais e
> abas de topo centram o pack; **a retenção é simples porque ele fica no eixo de
> rotação**: sendo simétrico em torno do centro, a resultante centrífuga sobre
> ele é praticamente nula. Uma espuma sob a tampa segura contra vibração.
>
> **O que decide, não o rótulo de aplicação:** taxa ≥ 15C (o pack tem 20C) e
> conector de balanceamento **JST-XH de 3 vias** além do de potência. Sem o
> balanceador não há carga célula a célula, e num pack que gira lacrado isso
> não é aceitável. Carregar sempre em **modo LiFe**.

**Base de energia:** a hipótese de 60 mA por LED dá **5,22 A / 26,1 W** em
branco pleno. Com ESP de 0,3 W e buck a 87,5%, seriam 4,57 A na bateria e
10,5 min teóricos. O cenário de conteúdo equivalente a 15% dá 0,730 A e
65,8 min teóricos; a autonomia útil depende de medição, não há promessa de
50 min. O pack guarda 6,6 × 0,8 = 5,28 Wh nominais.

**Limite provisório para planejar a integração:** soma RGB equivalente a no
máximo **80% do branco e corrente total medida na saída ≤ 4,25 A**, ou menos
se o buck real exigir. O módulo deve manter regulação de 7,2 até 5,8 V sob a
carga autorizada e passar em térmica. Esse teto não qualifica um mini560
genérico; firmware de limitação e ensaio ainda precisam existir. Branco pleno
requer capacidade contínua superior a 5,28 A. Ver esquema §5 e pendência C7.

---

## 4. Estrutura e fixação

| Item | Espec | Qtd | Sit. | ~R$ |
|---|---|---:|:--:|---:|
| Chapa de alumínio | 2 mm, 60 × 60 mm, cortada e furada | 1 | 🛒 | 10 |
| Parafuso **M3 × 40** + porca **plana** M3 | fixação painel → longarina | 6 + 6 | 🛒 | 10 |
| Trava química média (Loctite 243) | substitui o nyloc nas juntas do painel | 1 | 🛒 | 25 |
| Parafuso **M3 × 6** | motor → chapa (padrão 16 × 19 mm) | 4 | 🛒 | 3 |
| Parafuso M4 × 16 (2) e **M4 × 20** (2, sob a aba de 2,5 mm do suporte do ímã) + porca nylon | chapa → flange da torre | 4 + 4 | 🛒 | 5 |
| Parafuso M3 × 10 | tampa da baia | 2 | 🛒 | 2 |
| Massa de balanceamento | fita adesiva de chumbo ou tungstênio | — | 🛒 | 20 |
| Grampos tipo C | fixação da base à bancada nos ensaios | 2 | 🛒 | 20 |
| Abraçadeiras e fita kapton | fios no rotor, termopar | — | 🛒 | 15 |

> **Correção de 02/09 — o nyloc não cabe onde eu tinha mandado usar.** O bolso
> hexagonal do painel tem **2,8 mm** e uma porca nyloc M3 tem **4,0 mm**; só entra
> porca plana (2,4 mm). Nas juntas do painel, use **porca plana + trava química**.
> Nyloc segue valendo onde há espaço: chapa → flange da torre.
>
> **E o comprimento estava errado.** A torre do boss tem 36 mm e a porca fica no
> fundo dela: o parafuso precisa de **M3 × 40**, não × 20.
>
> **Motor → chapa: M3 × 6, não × 8.** Através de 2 mm de chapa, um M3 × 8 penetra
> 6 mm na base do A2212, que aceita ~4–5 mm antes de tocar o enrolamento.

---

## 5. Instrumentação para os ensaios

| Item | Espec | Por quê | Sit. | ~R$ |
|---|---|---|:--:|---:|
| **Balança de precisão** | **resolução 0,01 g** | Δm entre painéis ≤ 0,084 g | 🛒 | 60–100 |
| Termopar tipo K + leitor | sonda de 1,5 mm, **só em pontos fixos** | chapa/base e referência estática; não ligar cabo à campânula girante | 🛒 | 40 |
| Medição da temperatura do motor em giro | sistema sem contato qualificado ou sensor embarcado retido | método, emissividade/spot ou telemetria ainda pendentes — bloqueador B | ⚠️ | a cotar |
| Medição da bateria em giro | sensor calibrado embarcado com telemetria ou registro local | temperatura máxima durante G4, com massa/retensão a incorporar | ⚠️ | a cotar |
| Acelerometria | duas respostas independentes e aquisição sincronizada; MPU6050 é candidato | matriz de influência em dois planos, não apenas um pico na base | ⚠️ | a cotar |
| Referência angular fixa 1/rev | sensor óptico ou equivalente, marca no rotor e mesma base de tempo da vibração | fase em G3, quando não há Hall embarcado | ⚠️ | a cotar |
| Paquímetro digital | 0,01 mm | verificação dimensional | ⚠️ | 30–50 |
| Tacômetro | necessário até qualificar leitura alternativa de RPM; Bluejay exige novo gerador DShot bidirecional e não fornece a referência fixa de fase | ⚠️ | 0–40 |
| Analisador lógico / osciloscópio | resolução adequada a SPI de 20–26,67 MHz | verificar clock efetivo, transações e atraso óptico/índice | ⚠️ | a cotar |
| Câmera | celular a 240 fps serve | validação visual de jitter | ✅ | — |

> **A resolução da balança é requisito, não conforto.** As versões anteriores
> pediam 0,1 g. Com Δm admissível de 0,084 g entre painéis, uma balança de 0,1 g
> **não consegue verificar o critério** — ela mede exatamente o tamanho do erro
> que precisa detectar. Precisa ser 0,01 g.

---

## 6. Consumíveis

| Item | Qtd | ~R$ |
|---|---|---:|
| Filamento ABS | 1 kg | 90–130 |
| Isopropanol, cola de mesa, lixa | — | 30 |
| Termorretrátil e solda | — | 20 |

---

## 7. Resumo de compra

| Bloco | ~R$ |
|---|---:|
| Acionamento (porca fina; a arruela sai da chapa) | 2 |
| Eletrônica de bordo | 45–65 |
| Estrutura e fixação | 83 |
| Instrumentação | 75–155 |
| Consumíveis | 140–180 |
| **Subtotal do orçamento anterior** | **345–485**, sem instrumentação e itens novos a cotar |

Carregador **em modo LiFe** (R$ 60) e paquímetro (R$ 50) entram se ainda não
houver no laboratório. A instrumentação adicional acima e as proteções impedem
fechar um total atualizado. Bluejay só dispensa o tacômetro após implementar
DShot bidirecional no gerador e validar RPM; o sinal servo existente não funciona
com esse firmware. Nenhuma compra foi realizada por esta revisão.

### Prioridade de compra

1. **Antes de comprar** — qualificar buck, chave, proteções e instrumentação;
   conferir os itens já em mãos e os seis fios isolados por painel.
2. **Antes da Fase 3** — balança de 0,01 g, medição térmica qualificada,
   duas respostas de vibração independentes e referência fixa 1/rev.
3. **Depois de medir** — isolador de vibração, se o ensaio de vibração pedir.
