# Lista de componentes — Hologram Orbiter v3.0

Estado em 01/09/2026. Preços em BRL são **estimativas de ordem de grandeza**
para orçamento, não cotações.

Legenda: ✅ já temos · 🛒 comprar · ⚠️ decisão pendente

---

## 1. Peças impressas — ABS

Todas saem do gerador paramétrico. Ver [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md).

| # | Peça | Qtd | Volume | Massa | Tempo |
|---|---|---:|---:|---:|---|
| 01 | Aranha | 1 | 52 cm³ | ≤ 55 g | 4–5 h |
| 02 | Painel LED | 3 | 33 cm³ ea. | ≤ 34,2 g nu | 8–10 h (lote) |
| 03 | Tampa da baia | 1 | 7 cm³ | ≤ 8 g | 30 min |
| 04/05 | Base + torre integradas | 1 | 250 cm³ | ≤ 300 g | 12–18 h |
| 06 | Suporte do ímã de índice | 1 | 8 cm³ | — | 30 min |
| C01 | Cupom da junta 11 × 6 | 1 | 10 cm³ | — | 15 min |
| C02 | Cupom do canal 12,4 × 1,2 | 1 | 6 cm³ | — | 10 min |

**Total: ~432 cm³ ≈ 0,45 kg.** Comprar **1 kg** — o refugo em ABS é real e os
painéis podem precisar de segunda tiragem por massa fora de tolerância.

**Imprimir os cupons primeiro.** Custam 25 minutos e evitam refazer um lote de
painéis de 208 mm por causa de folga na junta ou no canal.

---

## 2. Acionamento

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Motor BLDC | **A2212 920KV**, 2–4S, 52 g, eixo M6, base 4×M3 em 16 × 19 mm | ✅ | — |
| ESC | 15 A com **rampa configurável** (mínimo 8 s) | ✅ | — |
| Fonte de bancada | ajustável; operar em **6–7 V**, ≥ 5 A | ✅ | — |
| Adaptador de hélice | alumínio, flange Ø25–30, furo Ø8 | ⚠️ | 15 |
| Porca M6 autotravante **baixa** | ~6 mm de altura — **não** a cônica de 14 mm que veio com o motor | 🛒 | 2 |
| Arruela M6 aço | assento no rebaixo Ø13 × 2 do cubo | 🛒 | 1 |

> **⚠️ O adaptador de hélice depende de uma medição.** Se a face superior da
> campânula for vazada (o desenho sugere que sim, com raios), o cubo assentaria
> num ressalto pequeno demais para um rotor de Ø208. Medir o diâmetro útil de
> assento: **abaixo de ~Ø20, o adaptador deixa de ser opcional.**

---

## 3. Óptica e eletrônica de bordo

Tudo isto gira junto com o rotor.

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Fita LED | **HD107S 144 LED/m**, RGB, 1 m (usa 87 de 144) | ✅ | — |
| Microcontrolador | **ESP32-C3 Super Mini** ou XIAO ESP32-C3 (~22 × 18 mm) | 🛒 | 25–40 |
| Regulador 5 V | buck **5 V / ≥ 5 A** (mini560 ou XL4015) | 🛒 | 15 |
| Bateria | **LiPo 2S 850 mAh**, **55 × 30 × 13 mm**, ~47 g | 🛒 | 60–90 |
| Conector | XT30 ou JST-XH para carga e balanceamento | 🛒 | 8 |
| Chave liga/desliga | slide ou toggle miniatura, acesso pela tampa | 🛒 | 5 |
| Sensor de índice | **A3144** (digital, TO-92, coletor aberto) — **no rotor** | 🛒 | 3 |
| Resistor de pull-up | 10 kΩ, do sinal do hall para **3,3 V** | 🛒 | 1 |
| Deslocador de nível | **74AHCT125** para CLK e DATA — ou buck em 4,5 V | 🛒 | 5 |
| Capacitor de bulk | 1000 µF / 10 V na entrada da fita | 🛒 | 3 |
| Ímã | neodímio Ø4 × 2 mm — **na parte fixa** | 🛒 | 2 |
| Fio de potência | **AWG 24**, 2 cores, ~3 m | 🛒 | 12 |
| Fio de sinal | AWG 28, 2 cores, ~3 m | 🛒 | 8 |
| Fita de poliéster transparente | 0,05–0,1 mm, retenção mecânica da fita LED | 🛒 | 15 |
| Carregador LiPo 2S | balanceador | ⚠️ | 60 |

> **Risco de empacotamento — verificar antes de congelar o cubo.** Bateria
> 57 × 30 × 13, mais MCU, regulador, chave e conector, tudo dentro de uma baia
> de Ø66 × 20 mm. Um DevKit ESP32 de 55 × 28 mm **não cabe** junto com a bateria;
> por isso a espec pede um C3 Super Mini. O regulador de 5 V não estava previsto
> em nenhuma versão anterior. Vale um esboço de layout da baia antes do CAD fechar.

> **Duas armadilhas elétricas que não são opcionais.**
>
> **O A3144 não funciona a 3,3 V** — opera de 4,5 a 24 V. Alimente-o em **5 V** e
> use o pull-up de 10 kΩ para **3,3 V**: como a saída é coletor aberto, o sinal
> oscila de 0 a 3,3 V e a entrada do ESP32-C3, que não tolera 5 V, fica protegida.
> Pull-up para 5 V queima a porta.
>
> **A fita quer V_IH ≥ 3,5 V** e o ESP32-C3 entrega 3,3 V. A 17 Mbit/s isso não é
> margem. Ou entra o 74AHCT125, ou ajuste o buck para **4,5 V**, o que baixa o
> limiar para ~3,15 V e resolve sem componente — ao custo de um pouco de brilho.

> **Envelope máximo do pack — o que realmente manda.** A baia tem Ø66 × 20 mm e a
> porca M6 ocupa até Z = 5,6, então sobram **14,4 mm de altura**. No plano, o
> limite não é o comprimento sozinho: é a **meia-diagonal ≤ 33 mm**.
>
> | Pack | Meia-diagonal | Altura sobre a porca | |
> |---|---:|---:|---|
> | **55 × 30 × 13** | **31,3 mm** | **18,6 mm** | **adotado** |
> | 57 × 30 × 13 | 32,2 mm | 18,6 mm | no limite |
> | 58 × 30 × 17 | 32,7 mm | 22,6 mm | reprova na altura |
>
> **O berço não pode ser caixa fechada.** Uma parede de 1,5 mm em volta levaria a
> meia-diagonal a 33,4 e estouraria. Use **quatro apoios**, longe dos cantos:
> batentes em x = ±28,5 (y de −10 a +10) e pastilhas em y = ±16 (x de −15 a +15),
> 8 mm de altura. Nos cantos sobram 1,7 mm; nas pontas 5,5; no meio dos lados 18.
>
> A retenção é simples porque **o pack fica no eixo de rotação**: sendo simétrico
> em torno do centro, a resultante centrífuga sobre ele é praticamente nula. Uma
> espuma sob a tampa segura contra vibração.

**Por que 2S e não outra coisa:****Por que 2S e não outra coisa:** a fita é 5 V e puxa **27 W em branco pleno**
(87 LEDs × 60 mA), com 5,1 W típico em conteúdo POV. Um pack de 850 mAh dá
~70 min de conteúdo típico. 2S com buck é o arranjo padrão; 1S com boost seria
pior em eficiência e corrente.

---

## 4. Estrutura e fixação

| Item | Espec | Qtd | Sit. | ~R$ |
|---|---|---:|:--:|---:|
| Chapa de alumínio | 2 mm, 60 × 60 mm, cortada e furada | 1 | 🛒 | 10 |
| Parafuso **M3 × 40** + porca **plana** M3 | fixação painel → longarina | 6 + 6 | 🛒 | 10 |
| Trava química média (Loctite 243) | substitui o nyloc nas juntas do painel | 1 | 🛒 | 25 |
| Parafuso **M3 × 6** | motor → chapa (padrão 16 × 19 mm) | 4 | 🛒 | 3 |
| Parafuso M4 × 16 + porca nylon | chapa → flange da torre | 4 + 4 | 🛒 | 5 |
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

## 5. Contenção

| Item | Espec | Sit. | ~R$ |
|---|---|:--:|---:|
| Cilindro de proteção | **tubo policarbonato Ø274 ext. × 4 mm de parede × 305 mm**, sem fundo | 🛒 | 120–200 |
| Tampa superior | disco ou anel removível — **⚠️ decidir: peça impressa ou comprada** | ⚠️ | 20 |
| Retenção do cilindro | silicone na canaleta ou 3 clipes — **⚠️ sem definição** | ⚠️ | 10 |
| Isolador de vibração | ⚠️ decisão pendente — ver §5.7 da espec | ⚠️ | — |

Ø interno 266 mm, escolhido para centrar a parede em r = 135, no meio da pista
Ø260–280 da base. Assentado numa canaleta de 3 mm (Z = 5), o topo fica em
**Z = 310: 17 mm de folga acima do rotor e 26,7 mm de folga radial.**

Encomendar pelo Ø externo e pela parede, que é como o fornecedor cota.

**Policarbonato, não acrílico.** Um painel solto carrega 7,4 J a 18,9 m/s. PMMA é
frágil e estilhaça; PC deforma e retém.

**Não compre isolador ainda.** A peça da versão anterior (coxim Ø16 × 8 em
TPU 95A) tem frequência natural de 400–620 Hz contra os ≤ 21 Hz necessários para
isolar 30 Hz — é espaçador, não isolador. A montagem inicial é rígida.

## 6. Instrumentação para os ensaios

| Item | Espec | Por quê | Sit. | ~R$ |
|---|---|---|:--:|---:|
| **Balança de precisão** | **resolução 0,01 g** | Δm entre painéis ≤ 0,084 g | 🛒 | 60–100 |
| Termopar tipo K + leitor | sonda de 1,5 mm | bloqueador térmico | 🛒 | 40 |
| Acelerômetro | MPU6050 | vibração e balanceamento | 🛒 | 15 |
| Paquímetro digital | 0,01 mm | verificação dimensional | ⚠️ | 30–50 |
| Tacômetro | óptico, ou usar o próprio hall | confirmar 1800 RPM | ⚠️ | 40 |
| Câmera | celular a 240 fps serve | validação visual de jitter | ✅ | — |

> **A resolução da balança é requisito, não conforto.** As versões anteriores
> pediam 0,1 g. Com Δm admissível de 0,084 g entre painéis, uma balança de 0,1 g
> **não consegue verificar o critério** — ela mede exatamente o tamanho do erro
> que precisa detectar. Precisa ser 0,01 g.

---

## 7. Consumíveis

| Item | Qtd | ~R$ |
|---|---|---:|
| Filamento ABS | 1 kg | 90–130 |
| Isopropanol, cola de mesa, lixa | — | 30 |
| Termorretrátil e solda | — | 20 |

---

## 8. Resumo de compra

| Bloco | ~R$ |
|---|---:|
| Contenção | 120–200 |
| Acionamento (adaptador, porcas) | 18 |
| Eletrônica de bordo | 165–220 |
| Estrutura e fixação | 83 |
| Instrumentação | 115–195 |
| Consumíveis | 140–180 |
| **Total estimado** | **640–890** |

Carregador LiPo (R$ 60), paquímetro (R$ 50) e tacômetro (R$ 40) entram se ainda
não houver no laboratório.

### Prioridade de compra

1. **Agora** — bateria, ESP32-C3, regulador, sensor hall, ímã, fio, filamento.
   São o caminho crítico: sem eles não há como montar nem pesar de verdade.
2. **Antes da Fase 3** — balança de 0,01 g, termopar, acelerômetro.
3. **Depois de medir** — adaptador de hélice, isolador, contenção definitiva.
