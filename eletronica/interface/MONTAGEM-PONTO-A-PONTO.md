# Guia de Montagem Ponto a Ponto da Interface (Sem PCB)

> **Contexto:** A PCB de interface r0.2 **não será fabricada**. Este documento é o roteiro prático e detalhado para a confecção da placa de interface soldada à mão em placa perfurada / placa-ilha (passo 2,54 mm). 
> O circuito elétrico implementa a arquitetura **SPI Quad** (CLK comum com resistores série individuais, 3 linhas DATA independentes, buffer 74AHCT125, pull-up do Hall em 3,3 V e divisor resistivo da bateria).

---

## 1. Restrições Críticas de Envelope, Altura e Peso

O CAD reserva uma baia estrita para a interface: **15 × 20 × 8 mm** (em $x: 19,5 \dots 34,5 \cdot y: -5 \dots 15$, sobre pilares de 6 mm). Uma montagem manual cresce com facilidade se não for planejada antes da primeira solda:

* **Altura livre máxima: 8,0 mm**
  * CI DIP-14 nu tem ~3,3 mm de altura e cabe. **NÃO use soquete**, pois ele eleva o conjunto para 8–10 mm e colide com a tampa.
  * Se for usar CI SOIC-14 em placa adaptadora (breakout SOP→DIP), solde fios finos rentes e corte as pontas inferiores dos pinos.
  * Monte todos os resistores de 1/8 W ou 1/4 W **em pé** (montagem vertical, um furo em cada terminal dobrado). Deitados, os 13 resistores não cabem na área de 300 mm² ($15 \times 20\text{ mm}$). Em pé, ocupam apenas $2 \times 2\text{ mm}$ por peça e ficam com ~6,5 mm de altura (dentro do limite).
* **Massa alvo: $\le 5,5\text{ g}$**
  * O rotor opera a 1800 RPM. A $r \approx 30\text{ mm}$, cada grama adicional gera $\sim 30\text{ g}\cdot\text{mm}$ de desbalanceamento estático (o limite admissível de projeto é de apenas $8,4\text{ g}\cdot\text{mm}$).
  * Pese a placa após a conclusão da montagem antes de integrá-la ao rotor.

> [!CAUTION]
> **Alimentação de Potência:** Os 5 V e GND de alta corrente dos LEDs vêm **direto da estrela do Buck**, NUNCA passe a corrente dos LEDs por esta placa perfurada nem pelo pino 5 V do ESP32-C3! Esta placa processa **exclusivamente sinais lógicos** e a medição de tensão.

---

## 2. Lista de Materiais e Componentes

### 2.1 Componentes Eletrônicos

| Ref. | Qtd. | Valor / Modelo | Função | Montagem sugerida |
|---|:---:|---|---|---|
| **U1** | 1 | **74AHCT125** (DIP-14 ou SOIC) | Conversor de nível 3,3 V → 5 V (TTL) | Centro da placa perfurada (sem soquete) |
| **R1, R2, R8, R9** | 4 | Resistor **10 kΩ** 1% | Pull-down das entradas SPI no boot | Em pé, entrada → barramento GND |
| **R3** | 1 | Resistor **10 kΩ** 1% | Pull-up da saída do sensor Hall | Em pé, nó HALL → linha +3V3 |
| **R4** | 1 | Resistor **150 kΩ** 1% | Braço superior do divisor de bateria | Em pé, nó VBAT_SW → nó ADC |
| **R5** | 1 | Resistor **47 kΩ** 1% | Braço inferior do divisor de bateria | Em pé, nó ADC → barramento GND |
| **R6, R10, R11** | 3 | Resistor **33 Ω** | Amortecimento série dos ramos de CLK | Em pé ou em leque a partir do pino 3 |
| **R7, R12, R13** | 3 | Ponte / Fio direto (0 Ω) | Conexão direta dos sinais DATA dos painéis | Jumpers de fio isolado ou direto nos chicotes |
| **C1** | 1 | Capacitor cerâmico **100 nF** | Desacoplamento rápido de U1 | Colado aos pinos 14 e 7 (ou barramento GND) |
| **C2** | 1 | Capacitor cerâmico **1 µF** | Desacoplamento local de 5 V | Junto ao pino 14 e GND |
| **C3** | 1 | Capacitor cerâmico **100 nF** | Filtro de ruído do ADC | Junto ao nó ADC e GND |

### 2.2 Insumos e Ferramentas de Oficina

* Placa perfurada de fenolite ou fibra de vidro (passo 2,54 mm), pré-cortada em no máximo $15 \times 20\text{ mm}$ (~$6 \times 8$ ilhas).
* Fio de cobre rígido nu (0,5 mm / ~AWG 24) para barramentos inferiores de GND e +5 V.
* Fio flexível fino (AWG 28 ou AWG 30) para interconexões e chicotes externos.
* Ferro de solda com ponta fina, solda estanho/chumbo de qualidade e fluxo.
* Tubo termorretrátil fino, fita Kapton e adesivo de fixação/alívio de tensão.
* Multímetro digital (continuidade com bip, resistência e tensão DC).
* Fonte de bancada regulável com ajuste fino de limite de corrente.

---

## 3. Pinagem e Lógica do Buffer U1 (74AHCT125)

O 74AHCT125 possui 4 buffers independentes de saída Tri-State com entradas ativas baixas (/OE). Todos os pinos /OE (1, 4, 10, 13) devem ser **aterrados permanentemente**.

```
                         74AHCT125 (DIP-14)
                           ┌──────∪──────┐
          (1/OE)    GND ───┤ 1        14 ├── +5V     (VCC)
       (GPIO4)  CLK_3V3 ───┤ 2        13 ├── GND     (4/OE)
  (R6,R10,R11)  CLK_BUF ───┤ 3        12 ├── D2_3V3  (GPIO7)   [R9: 10k → GND]
          (2/OE)    GND ───┤ 4        11 ├── D2_5V   (Painel 3 DATA)
       (GPIO6)   D0_3V3 ───┤ 5        10 ├── GND     (3/OE)
(Painel 1 DATA)   D0_5V ───┤ 6         9 ├── D1_3V3  (GPIO5)   [R8: 10k → GND]
                    GND ───┤ 7         8 ├── D1_5V   (Painel 2 DATA)
                           └─────────────┘
```

### Mapeamento dos 4 Canais:
1. **Canal 1 (CLK Comum):** Entrada pino 2 (GPIO4) $\rightarrow$ Saída pino 3 $\rightarrow$ Divide em 3 vias com $33\ \Omega$ cada (R6, R10, R11).
2. **Canal 2 (DATA Painel 1):** Entrada pino 5 (GPIO6) $\rightarrow$ Saída pino 6 $\rightarrow$ DATA Painel 1.
3. **Canal 3 (DATA Painel 2):** Entrada pino 9 (GPIO5) $\rightarrow$ Saída pino 8 $\rightarrow$ DATA Painel 2.
4. **Canal 4 (DATA Painel 3):** Entrada pino 12 (GPIO7) $\rightarrow$ Saída pino 11 $\rightarrow$ DATA Painel 3.

---

## 4. Mapa dos 19 Fios da Placa

Para organizar a fiação e evitar confusão, etiquete as pontas dos fios com código de cores ou fita adesiva numerada antes de soldar:

| Grupo | Fio | Nome do Sinal | Origem / Destino Externo | Ponto de Ligação na Placa |
|---|:---:|---|---|---|
| **Alimentação** | 1 | **+5V** | Barramento Estrela 5 V (Buck) | Barramento +5V (Pino 14) |
| | 2 | **GND** | Barramento Estrela GND (Buck) | Barramento GND Comum |
| **ESP32-C3** | 3 | **3V3_MCU** | Pino 3V3 do ESP32-C3 | Topo do resistor R3 (Pull-up Hall) |
| | 4 | **GPIO4** | Pino GPIO4 do ESP32-C3 | Pino 2 de U1 (CLK) |
| | 5 | **GPIO6** | Pino GPIO6 do ESP32-C3 | Pino 5 de U1 (D0) |
| | 6 | **GPIO5** | Pino GPIO5 do ESP32-C3 | Pino 9 de U1 (D1) |
| | 7 | **GPIO7** | Pino GPIO7 do ESP32-C3 | Pino 12 de U1 (D2) |
| | 8 | **GPIO3** | Pino GPIO3 do ESP32-C3 | Nó HALL (Pino 3 do A3144 / R3) |
| | 9 | **GPIO0** | Pino GPIO0 (ADC) do ESP32-C3 | Nó central do divisor (VBAT_ADC) |
| **Painel 1** | 10 | **P1_CLK** | Entrada CLK do Painel 1 | Saída do resistor R6 ($33\ \Omega$) |
| | 11 | **P1_DATA** | Entrada DATA do Painel 1 | Pino 6 de U1 |
| **Painel 2** | 12 | **P2_CLK** | Entrada CLK do Painel 2 | Saída do resistor R10 ($33\ \Omega$) |
| | 13 | **P2_DATA** | Entrada DATA do Painel 2 | Pino 8 de U1 |
| **Painel 3** | 14 | **P3_CLK** | Entrada CLK do Painel 3 | Saída do resistor R11 ($33\ \Omega$) |
| | 15 | **P3_DATA** | Entrada DATA do Painel 3 | Pino 11 de U1 |
| **Sensor Hall** | 16 | **HALL_VCC** | Pino 1 (VCC) do sensor A3144 | Barramento +5V |
| | 17 | **HALL_GND** | Pino 2 (GND) do sensor A3144 | Barramento GND |
| | 18 | **HALL_OUT** | Pino 3 (OUT) do sensor A3144 | Nó HALL (mesmo ponto de GPIO3) |
| **Bateria** | 19 | **VBAT_SW** | Após chave liga/desl. e fusível | Entrada do resistor R4 ($150\text{ k}\Omega$) |

> [!TIP]
> **Dica de Montagem:** Para a conexão com o ESP32-C3, você pode soldar uma barra de pinos fêmea (header 1×9) na lateral da placa perfurada e usar chicote destacável, facilitando ensaios e substituição rápida do microcontrolador.

---

## 5. Procedimento Passo a Passo de Montagem

### Passo 1: Preparação da Placa e Posicionamento de U1
1. Corte a placa perfurada no tamanho máximo de **$15 \times 20\text{ mm}$** (~6 furos de largura por 8 furos de comprimento).
2. Lixe as rebarbas externas para garantir que ela encaixe com folga entre os pilares do rotor.
3. Posicione U1 no centro. Se for CI DIP, dobre levemente as pontas dos terminais para travar na placa; se for adaptador SOIC, fixe-o rente.
4. Marque com caneta indelúvel o pino 1 e o pino 14 na face superior para orientação visual permanente.

### Passo 2: Barramento de GND e Habilitação (/OE)
1. Pelo lado inferior da placa, passe um fio rígido unindo os pinos de aterramento de um lado: **Pino 1 → Pino 4 → Pino 7**.
2. No outro lado, passe outro trecho de fio rígido unindo os pinos de aterramento: **Pino 10 → Pino 13**.
3. Faça a ponte entre os dois lados conectando o **Pino 13 ao Pino 7**.
4. Deixe uma ilha livre ou terminal de saída nesse barramento para a conexão do fio GND principal.
5. **Conferência com multímetro:** Verifique continuidade $0\ \Omega$ entre os pinos 1, 4, 7, 10 e 13.

### Passo 3: Linha de +5 V e Capacitores de Desacoplamento
1. Conecte o pino 14 ao ponto de entrada de +5 V.
2. Solde os capacitores **C1 (100 nF)** e **C2 (1 µF)** o mais próximo possível do pino 14, conectando o outro terminal diretamente ao barramento de GND (pino 7).
3. **Conferência com multímetro:** Certifique-se de que NÃO há curto-circuito entre pino 14 (+5V) e pino 7 (GND).

### Passo 4: Pull-downs das Entradas Lógicas (R1, R2, R8, R9)
Instale os 4 resistores de $10\text{ k}\Omega$ em posição vertical (em pé) entre os pinos de entrada e o barramento GND:
* **R1 ($10\text{ k}\Omega$):** do Pino 2 (CLK_3V3) para o GND.
* **R2 ($10\text{ k}\Omega$):** do Pino 5 (D0_3V3) para o GND.
* **R8 ($10\text{ k}\Omega$):** do Pino 9 (D1_3V3) para o GND.
* **R9 ($10\text{ k}\Omega$):** do Pino 12 (D2_3V3) para o GND.
* **Conferência com multímetro:** Meça a resistência de cada um dos pinos 2, 5, 9 e 12 em relação ao GND. O valor deve ser de aproximadamente $10\text{ k}\Omega$ em cada um.

### Passo 5: Saídas de Clock (R6, R10, R11) e Dados dos Painéis
1. Conecte um dos terminais dos 3 resistores de **$33\ \Omega$ (R6, R10, R11)** juntos no **Pino 3** (saída CLK_BUF). Abra os corpos em leque na placa para que os outros terminais fiquem isolados entre si.
2. Os terminais livres desses três resistores formam os nós **P1_CLK**, **P2_CLK** e **P3_CLK**.
3. As saídas de dados são obtidas diretamente dos pinos de U1:
   * **Pino 6** $\rightarrow$ Saída DATA do Painel 1 (P1_DATA).
   * **Pino 8** $\rightarrow$ Saída DATA do Painel 2 (P2_DATA).
   * **Pino 11** $\rightarrow$ Saída DATA do Painel 3 (P3_DATA).
4. Solde rabichos de fio AWG 28 de ~5 cm para cada um desses 6 nós, identificando as pontas com fita ou anilhas.

### Passo 6: Circuito do Sensor Hall A3144 (Nu, Sem Placa HW-477)
> [!IMPORTANT]
> **Atenção:** O sensor Hall A3144 opera com alimentação de 5 V, mas sua saída é coletor aberto. O resistor de pull-up **DEVE ser ligado obrigatoriamente à linha de 3,3 V** (vinda do MCU). Se for ligado em 5 V, o sinal injetará 5 V no pino GPIO3 do ESP32-C3, danificando a porta permanentemente.

1. Identifique os terminais do sensor A3144 (encapsulamento TO-92, face chanfrada/marcada para você e pernas para baixo):
   * **Pino 1 (Esquerda):** VCC (+5V)
   * **Pino 2 (Centro):** GND
   * **Pino 3 (Direita):** Saída (OUT / Coletor Aberto)
2. Na placa de interface, crie o nó **HALL**:
   * Solde o resistor **R3 ($10\text{ k}\Omega$)** entre o ponto de conexão de **3V3_MCU** e o nó **HALL**.
   * Conecte o fio que vai para o **GPIO3** do ESP32-C3 a esse nó **HALL**.
   * Traga os 3 fios do sensor Hall (passando pelo rasgo inferior do rotor) e solde: VCC no barramento +5V, GND no barramento GND e OUT no nó HALL.

### Passo 7: Circuito do Divisor da Bateria (ADC)
O divisor reduz a tensão de 2S LiFePO4 ($7,2\text{ V}$ cheia $\dots$ $5,8\text{ V}$ corte) para a faixa linear do conversor AD do ESP32-C3 ($< 2,5\text{ V}$):

$$\text{Relação do Divisor} = \frac{47\text{ k}\Omega}{150\text{ k}\Omega + 47\text{ k}\Omega} \approx 0,2386$$
*(7,2 V $\rightarrow$ ~1,718 V | 5,8 V $\rightarrow$ ~1,384 V)*

1. Crie o nó central **VBAT_ADC** em uma ilha isolada.
2. Solde o resistor **R4 ($150\text{ k}\Omega$)** entre o ponto de entrada **VBAT_SW** (fio que vem da chave geral após o fusível) e o nó **VBAT_ADC**.
3. Solde o resistor **R5 ($47\text{ k}\Omega$)** entre o nó **VBAT_ADC** e o barramento GND.
4. Solde o capacitor cerâmico **C3 (100 nF)** em paralelo com R5 (entre o nó **VBAT_ADC** e o GND).
5. Solde o fio que vai para o pino **GPIO0** do ESP32-C3 no nó **VBAT_ADC**.

---

## 6. Checklist de Testes a Frio (Sem Energia)

Com a placa montada na bancada e **totalmente desconectada** de baterias, fontes e ESP32-C3, execute com multímetro:

| # | Ponto de Teste | Ponta Vermelha | Ponta Preta | Valor Esperado | Concluído |
|:---:|---|---|---|:---:|:---:|
| 1 | Barramento de Terra | Pino 1 de U1 | Pinos 4, 7, 10, 13 e GND Hall | $\approx 0\ \Omega$ (continuidade total) | [ ] |
| 2 | Isolamento de Alimentação | Pino 14 (+5V) | Barramento GND | Aberto / Alta impedância ($> 100\text{ k}\Omega$) | [ ] |
| 3 | Pull-down CLK | Pino 2 de U1 | GND | $\approx 10\text{ k}\Omega$ | [ ] |
| 4 | Pull-down DATA D0 | Pino 5 de U1 | GND | $\approx 10\text{ k}\Omega$ | [ ] |
| 5 | Pull-down DATA D1 | Pino 9 de U1 | GND | $\approx 10\text{ k}\Omega$ | [ ] |
| 6 | Pull-down DATA D2 | Pino 12 de U1 | GND | $\approx 10\text{ k}\Omega$ | [ ] |
| 7 | Resistores série de CLK | Pino 3 de U1 | Cada saída P1_CLK, P2_CLK, P3_CLK | $\approx 33\ \Omega$ em cada | [ ] |
| 8 | Saídas de DATA | Pino 6, 8, 11 | P1_DATA, P2_DATA, P3_DATA | $\approx 0\ \Omega$ (linha direta correspondente) | [ ] |
| 9 | Pull-up do Hall | Nó HALL | Linha 3V3_MCU | $\approx 10\text{ k}\Omega$ | [ ] |
| 10 | Impedância Divisor Bateria | Ponto VBAT_SW | GND | $\approx 197\text{ k}\Omega$ ($150\text{ k} + 47\text{ k}$) | [ ] |
| 11 | Braço inferior Divisor | Nó VBAT_ADC | GND | $\approx 47\text{ k}\Omega$ | [ ] |

*(Nota: a leitura com multímetro nos nós com capacitores pode oscilar por alguns segundos até estabilizar).*

---

## 7. Roteiro de Energização Escalonada

Siga rigorosamente a ordem abaixo para validar o circuito sem risco aos componentes:

```
ETAPA 1: Só a interface na bancada (limite 100 mA)
   └── Validar consumo baixo (< 5 mA) e ausência de aquecimento.
ETAPA 2: Integração com ESP32-C3 via USB (bancada isolada)
   └── Testar comutação do sensor Hall com ímã e leitura analógica no ADC.
ETAPA 3: Alimentação 5 V via estrela com 1 fita de LED conectada
   └── Validar sinal de CLK e DATA no osciloscópio / acendimento com brilho mínimo.
ETAPA 4: Sistema completo (3 fitas conectadas)
   └── Respeitar teto de ensaio: corrente total <= 4,25 A e f <= 80%.
```

### Detalhamento das Etapas:
* **7.1 — Teste do Buffer Isolado:**
  Conecte a fonte de bancada ajustada em **$5,0\text{ V}$ com limite de corrente em $100\text{ mA}$** aos pinos +5V e GND da plaquinha (sem ESP32 e sem fitas). O consumo deve ser de apenas alguns miliamperes. Meça a tensão nas saídas lógicas (pinos 3, 6, 8, 11): todas devem estar estáveis em $\sim 0\text{ V}$ graças aos pull-downs.
* **7.2 — Teste dos Sensores e ADC:**
  Desconecte a fonte de bancada. Conecte os fios da placa ao ESP32-C3 e alimente o MCU pelo cabo USB. Meça a linha 3V3 no resistor R3: deve apresentar $3,3\text{ V}$. Aproxime o ímã neodímio da face do sensor Hall: a tensão no pino GPIO3 deve comutar entre $3,3\text{ V}$ e $0\text{ V}$. Injete tensão conhecida em VBAT_SW (ex: $7,2\text{ V}$) e confirme no multímetro e no firmware a leitura de $\approx 1,72\text{ V}$ no pino GPIO0.
* **7.3 — Teste de Carga de Dados e LEDs:**
  Alimente os 5 V e GND através do barramento em estrela do rotor (fonte de bancada ajustada em 5 V, limite $500\text{ mA}$). Desconecte o USB. Conecte primeiro apenas o Painel 1 e execute o firmware com padrão de teste em baixo brilho. Repita sucessivamente para os Painéis 2 e 3.
* **7.4 — Teste das Três Fitas Simultâneas:**
  Conecte os três painéis e certifique-se de que o limite de software do firmware esteja ativo ($f \le 80\%$ de brilho branco ou $I \le 4,25\text{ A}$).

---

## 8. Acabamento Mecânico e Instalação na Baia

1. **Alívio de Tensão:** Aplique uma gota de cola quente ou envolva com fita Kapton a saída de cada conjunto de fios a cerca de 5 mm dos pontos de solda na placa, prevenindo fadiga por vibração centrífuga.
2. **Corte de Terminais:** Verifique a face inferior da placa com lupa ou microscópio e apare todas as sobras de terminais rente à solda, garantindo que nada perfure os cabos que passam pelo vão inferior.
3. **Pesagem e Balanço:** Pese a placa finalizada em balança de precisão ($0,01\text{ g}$). Compare com a massa teórica de $5,5\text{ g}$. Anote a massa real para a reconciliação do balanceamento do rotor.
4. **Instalação:** Posicione a placa sobre os pilares dedicados da aranha ($x: 19,5 \dots 34,5\text{ mm}$), garantindo que os fios passem livres pelas guias sem prensar contra a tampa superior.
