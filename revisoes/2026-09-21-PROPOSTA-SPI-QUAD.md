# Proposta: dados das três fitas em SPI quad — 21/09/2026

**Estado: em avaliação, não adotada.** Até a decisão, vale a cadeia do
[esquema 05](../05-ESQUEMA-ELETRICO-v3.0.md). A pendência é a
[06 C10](../06-PENDENCIAS-ABERTAS-v3.0.md). Como as revisões desta pasta,
este documento não manda em cota nem em requisito.

Versão visual, com os diagramas de ligação e de tempo:
**https://claude.ai/artifact/95PxXYRQa2de4GpkpRTkZ1**

## 1. O problema

O ESP32-C3 tem um único SPI livre para a aplicação, o SPI2 (SPI0 e SPI1 servem
à flash), e o rotor tem três fitas. O 05 resolve ligando as fitas em série:
uma cadeia de 87 LEDs numa saída só. Funciona, mas tem três custos:

- **Tempo.** O quadro da cadeia tem 2860 bits: 143 µs a 20 MHz, para uma
  janela de 185,19 µs por coluna. Descontados os ~20 µs de overhead por
  transação do driver, sobram **22 µs**. 256 colunas não cabem a 20 MHz; a
  26,67 MHz sobram 2,96 µs.
- **Defasagem entre painéis.** Se a HD107S atualiza cada LED ao receber seus
  32 bits, o painel 2 acende 46,4 µs depois do painel 1 (0,50° a 1800 RPM) e o
  painel 3, 92,8 µs depois (1,00°, meia coluna). O firmware precisa compensar,
  e no Bloqueador E isso é mais uma causa possível de "deslocamento angular
  entre varreduras".
- **Fiação.** Seis condutores por painel. O retorno sai do topo da fita,
  atravessa o painel por dentro e volta à baia para entrar no painel seguinte.
  Em cada elo, CLK e DATA percorrem 0,4 m ou mais de AWG 28, acionados pela
  saída do último LED, não pelo 74AHCT125. Uma solda ruim num retorno apaga
  todos os painéis seguintes. A rota do retorno também não está fechada: o
  05 §4 manda descer pela cavidade até o bolso inferior, e a
  [FIACAO §1](../Hologram_Orbiter_v3_0/docs/FIACAO_E_MONTAGEM.md), voltar à
  baia pela abertura da lâmina.

Os outros periféricos do C3 não oferecem uma segunda saída útil. O RMT tem só
dois canais de transmissão, 48 símbolos por canal e nenhum DMA. O I2S do C3 tem
uma única linha de dados, e bit-bang ocuparia a CPU a cada coluna. A saída tem
de vir do próprio SPI2.

## 2. A proposta

O SPI2 do C3 tem modo quad: **um clock e quatro linhas de dados**, com DMA,
em half-duplex. Como a fita só recebe, o half-duplex não atrapalha. Cada fita
fica numa linha de dados, e as três compartilham o clock:

```
ESP32-C3 (SPI2 quad)    74AHCT125      chicote               fita
GPIO 4   CLK  ───────►  canal 1  ──┬── R ── CLK ─────────►  painel 1
                                   ├── R ── CLK ─────────►  painel 2
                                   └── R ── CLK ─────────►  painel 3
GPIO 6   D0   ───────►  canal 2  ──────── DATA ─────────►  painel 1
GPIO 5   D1   ───────►  canal 3  ──────── DATA ─────────►  painel 2
GPIO 7   D2   ───────►  canal 4  ──────── DATA ─────────►  painel 3
GPIO 10  D3   reservado, sem ligação
5 V e GND em estrela, como hoje
```

A cada clock, cada fita recebe um bit, todas ao mesmo tempo. Assim cada fita
recebe seu próprio quadro de 29 LEDs: 32 bits de início + 29 × 32 + 16 de fim
= **976 clocks**. Os 16 bits de fim vêm da regra de pelo menos meio clock por
LED, arredondada para um byte; confirmar no lote real, como os 44 da cadeia.

| | Cadeia (05 atual) | Quad (proposta) |
|---|---|---|
| Linhas do SPI2 | CLK + 1 de dados | CLK comum + 3 de dados |
| Quadro por coluna | 2860 bits, 360 bytes | 976 clocks, 488 bytes |
| Transmissão a 20 MHz | 143,0 µs | **48,8 µs** |
| Folga a 1800 × 180 após o overhead | 22,2 µs | **116,4 µs** |
| 1800 × 256 a 20 MHz | não cabe (−32,8 µs) | cabe (+61,4 µs) |
| Defasagem entre painéis | 0,50° e 1,00° | **nenhuma** |
| Condutores por painel | 6 | **4** |
| Solda no topo da fita | sim, o retorno | não |
| Quem aciona os fios longos | 74AHCT125 no 1º trecho, o último LED de cada fita nos elos | 74AHCT125 em todos |
| Solda de dados ruim | apaga aquele painel e os seguintes | apaga só aquele painel |
| Canais do 74AHCT125 | 2 de 4 | 4 de 4 |
| GPIOs do SPI | 2 | 4, mais 1 reservado |
| Firmware | quadro na ordem da cadeia | transposição dos bits, tabela de 1 KB |

## 3. Tempo

Folga por coluna depois dos 20 µs de overhead por transação, mesma premissa
do 05 §5. Medir no analisador.

| Caso | Janela | Cadeia 20 MHz | Cadeia 26,67 MHz | Quad 10 MHz | Quad 20 MHz |
|---|---:|---:|---:|---:|---:|
| 1800 × 180 | 185,19 µs | +22,19 | +57,94 | +67,59 | **+116,39** |
| 2000 × 180, não liberado | 166,67 µs | +3,67 | +39,42 | +49,07 | +97,87 |
| 1800 × 256, experimental | 130,21 µs | −32,79 | +2,96 | +12,61 | +61,41 |

O quad libera ~94 µs por coluna a 20 MHz. Essa folga pode virar mais colunas
(256) ou um clock menor. A 10 MHz o quad ainda tem mais folga que a cadeia tem
hoje a 20 MHz, e clock menor alivia os fios longos e os três ramos de CLK.

O preço do clock menor é a inclinação dentro de cada fita: o LED 28 atualiza
44,8 µs depois do LED 0 a 20 MHz (0,48°) e 89,6 µs depois a 10 MHz (0,97°).
Isso vale igual nas duas opções, para o mesmo clock, e o firmware pode
compensar. Começar em 20 MHz, como o 05, e manter 10 MHz como recurso se os
ramos de CLK repicarem.

## 4. Hardware

- **74AHCT125 com os quatro canais em uso:** CLK, D0, D1 e D2. Os quatro
  `/OE` ao GND e 100 nF junto ao CI, como hoje. Não sobra entrada para fixar.
- **CLK em três ramos.** Uma saída do buffer alimenta três fios de ~0,2 m.
  Pôr um resistor série em cada ramo, na placa de interface. Começar com 33 Ω
  e ajustar na bancada, olhando a borda na ponta de cada ramo. Se não limpar,
  um segundo 74AHCT125 dá a cada painel seu próprio buffer de CLK.
- **Pull-down de 10 kΩ em cada entrada do buffer.** O 05 §2.2 já prevê nas
  entradas de CLK e DATA, para a fita não receber lixo no boot; no quad, vale
  também para D1 e D2.

Pinos sugeridos, pela matriz de GPIO, que a Espressif garante igual ao IO_MUX
até 80 MHz:

| Sinal | Pino | Nota |
|---|---|---|
| CLK | GPIO 4 | igual ao 05 |
| D0 → painel 1 | GPIO 6 | o MOSI do 05 |
| D1 → painel 2 | GPIO 5 | livre |
| D2 → painel 3 | GPIO 7 | livre |
| D3 | GPIO 10 | reservado, sem ligação: o modo quad configura as quatro linhas |
| Índice e V_BAT | GPIO 3 e GPIO 0 | sem mudança |

Evitar GPIO 2, 8 e 9, que são de strapping (na Super Mini, o 8 também é o LED
da placa e o 9 é o BOOT), e GPIO 20 e 21, que são da UART. GPIO 4 a 7 também
são os pinos de JTAG externo. O 05 já usa dois deles, e a gravação vai pelo USB.

## 5. Chicote e mecânica

- **Quatro condutores por painel:** 5 V e GND em AWG 24, CLK e DATA em AWG 28.
  Os três chicotes ficam iguais por construção, sem retorno e sem peso morto no
  painel 3.
- **Massa.** Saem os retornos, ~0,5 g por painel pela estimativa do 05 §4, ou
  ~1,5 g no total. O rotor está estimado em 278,7 g para um teto de 280 g, com
  a massa ainda não reconciliada (06 D3).
- **Montagem.** Deixam de existir a solda no topo da fita, a descida do retorno
  pela cavidade com Kapton a cada 50 mm e a validação desse processo em cupom
  (FIACAO §1). O feixe no sulco de 4,4 × 3 mm perde dois fios.
- **CAD.** Nenhuma geometria muda: sulco, janelas e cavidade continuam servindo
  à entrada. Mudam `unverified_interfaces.panel_wiring`, de 6 para 4 condutores
  e com o envelope do feixe a reestimar, e os relatórios regenerados.

## 6. Firmware

Usar o driver `spi_master` do ESP-IDF, o mesmo que o 05 referencia. A
biblioteca SPI do Arduino não tem modo quad; se o firmware for em Arduino,
chamar a API do ESP-IDF, que o núcleo Arduino-ESP32 também expõe. Esboço para
a decisão, não compilado: ainda não há projeto de firmware no repositório.

```c
spi_bus_config_t barramento = {
    .sclk_io_num  = 4,
    .data0_io_num = 6,    // D0 -> painel 1
    .data1_io_num = 5,    // D1 -> painel 2
    .data2_io_num = 7,    // D2 -> painel 3
    .data3_io_num = 10,   // D3, sem ligação
    .data4_io_num = -1, .data5_io_num = -1, .data6_io_num = -1, .data7_io_num = -1,
    .max_transfer_sz = 488,
    .flags = SPICOMMON_BUSFLAG_MASTER | SPICOMMON_BUSFLAG_QUAD,
};
spi_bus_initialize(SPI2_HOST, &barramento, SPI_DMA_CH_AUTO);

spi_device_interface_config_t fitas_cfg = {
    .mode = 0,
    .clock_speed_hz = 20 * 1000 * 1000,
    .spics_io_num = -1,
    .queue_size = 2,
    .flags = SPI_DEVICE_HALFDUPLEX,     // exigido para mais de uma linha de dados
};
spi_device_handle_t fitas;
spi_bus_add_device(SPI2_HOST, &fitas_cfg, &fitas);

spi_transaction_t t = {
    .flags = SPI_TRANS_MODE_QIO,
    .length = 976 * 4,                  // em bits: 4 por clock
    .tx_buffer = quadro,                // 488 bytes em memória com MALLOC_CAP_DMA
};
```

O firmware monta os quadros das três fitas como se fossem independentes, com
122 bytes cada, e os intercala:

```c
static uint32_t espalha[256];   // cada bit do byte vai para a posição 4 ou 0 de um byte de saída

static void monta_tabela(void)
{
    for (int v = 0; v < 256; v++) {
        uint32_t w = 0;
        for (int k = 0; k < 8; k++) {             // k = 0 é o bit 7: MSB primeiro
            uint32_t bit = (v >> (7 - k)) & 1;
            w |= bit << (8 * (k >> 1) + ((k & 1) ? 0 : 4));
        }
        espalha[v] = w;
    }
}

// p1, p2, p3: quadros de 122 bytes das fitas dos painéis 1, 2 e 3
// saida: 122 palavras = 488 bytes, prontas para o DMA
static void transpoe(const uint8_t *p1, const uint8_t *p2, const uint8_t *p3,
                     uint32_t *saida)
{
    for (int i = 0; i < 122; i++)
        saida[i] = espalha[p1[i]] | espalha[p2[i]] << 1 | espalha[p3[i]] << 2;
}
```

A rotina supõe a convenção QSPI: o primeiro clock de cada byte leva os bits
7 a 4 em D3 a D0, e o segundo, os bits 3 a 0. Ela foi conferida em Python
contra essa convenção com 200 quadros aleatórios: cada linha reproduz o quadro
da sua fita, e D3 fica sempre em zero. **A convenção em si precisa do ensaio A.**

- **Mapeamento.** Na coluna k, o painel 1 mostra a coluna k da imagem, o
  painel 2 a k + 60 e o painel 3 a k + 120 (120° = 60 colunas de 2°), sem
  correção entre painéis.
- **Custo.** A transposição são 122 iterações por coluna, alguns microssegundos.
  Também dá para pré-calcular as 180 colunas de uma imagem: 85,8 KiB, contra
  63,3 KiB na cadeia, dos 400 KB de SRAM do C3.
- **Sem mudança:** índice, disparo por coluna e limite de corrente.

## 7. Ensaio de bancada, antes de decidir

Com as três fitas já cortadas (3 × 29), o ESP32-C3, o 74AHCT125 e fios no
comprimento real (~0,2 m por ramo), na fonte de bancada com limite de
corrente. O analisador lógico e o osciloscópio são os mesmos que o 05 já exige
para a cadeia (lista 03).

| Ensaio | Como | Passa se |
|---|---|---|
| A. Ordem dos bits | fita 1 vermelha, 2 verde, 3 azul; depois um contador; analisador em D0 a D2 | cada linha leva o quadro da sua fita; se a ordem vier trocada, corrigir a tabela |
| B. CLK nos ramos | osciloscópio na entrada do primeiro LED de cada ramo, a 20 MHz; ajustar o resistor série | cada borda cruza os limiares uma vez só, sem repique |
| C. Taxa sustentada | timer a 5400 Hz (7680 Hz para 256 colunas) por 10 min, com padrão em movimento | nenhum LED errado; tempo do disparo ao fim do DMA medido e dentro da janela |
| D. Atualização da HD107S (opcional) | fotodiodo num LED do começo e noutro do fim da fita | confirma se cada LED acende ao receber seus bits; vale para as duas opções |

Se A falhar, basta corrigir a tabela. Se B falhar, primeiro o segundo buffer,
depois o clock de 10 MHz. Se C falhar, olhar o overhead do driver: buffers
pré-calculados ou transação por polling.

## 8. Recomendação

**Adotar o quad se os ensaios A a C passarem.** Ele triplica a folga de tempo
por coluna e elimina a defasagem entre painéis. Também tira dois fios de cada
chicote num rotor sem margem de massa e elimina a parte mais difícil da
montagem dos chicotes, que é o retorno por dentro do painel. E isola as falhas
por painel. Tudo isso sem peça nova e sem mudar o CAD.

**Quando decidir:** antes de montar os chicotes e antes do lastro do G3, que o
plano 04 manda representar fitas e chicotes. Depois disso, trocar custa refazer
chicotes, pesagem e balanceamento.

Se os ensaios reprovarem e nem o segundo buffer nem o clock menor resolverem,
a cadeia do 05 continua valendo como está.

## 9. O que muda se for adotada

| Documento | Mudança |
|---|---|
| 05 §1 | topologia: dados em estrela, CLK comum |
| 05 §2.2 | quatro canais do 74AHCT125, resistor série por ramo de CLK, pull-down também em D1 e D2 |
| 05 §3 | tabela de pinos |
| 05 §4 | chicote de 4 condutores; sai a nota do retorno do painel 3 |
| 05 §5 e §6 | quadro de 976 clocks, tabela de tempo, modo quad e transposição; sai a defasagem entre painéis |
| 01 §6.2 e §6.3 | taxa por linha (5,27 Mbit/s a 1800 × 180) e fiação de 4 condutores |
| 03 | menos fio AWG 28; 3 resistores série e mais 2 pull-downs; segundo 74AHCT125 como contingência |
| FIACAO §1 e §4 | rota de 4 condutores, sem retorno |
| `parameters.json` | `panel_wiring.conductors` 6 → 4 e envelope do feixe; regenerar os relatórios |
| 06 | fechar a C10; a D3 passa a pesar chicotes de 4 condutores |
| 04 | ensaios A a C antes de montar os chicotes |

## Referências

- [ESP-IDF, SPI Master para ESP32-C3 (v5.5)](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c3/api-reference/peripherals/spi_master.html):
  modo quad (`SPI_TRANS_MODE_QIO`) só em half-duplex, pinos IO_MUX do SPI2,
  matriz de GPIO equivalente até 80 MHz e custo de ~20 µs por transação.
- [Datasheet do ESP32-C3](https://documentation.espressif.com/esp32-c3_datasheet_en.html):
  GP-SPI2 com Quad SPI, RMT com dois canais de transmissão e dois de recepção,
  strapping em GPIO 2, 8 e 9.
- [`soc_caps.h` do ESP32-C3](https://github.com/espressif/esp-idf/blob/master/components/soc/esp32c3/include/soc/soc_caps.h):
  48 símbolos por canal de RMT e RMT sem DMA.
- [Datasheet do 74AHCT125, Texas Instruments](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf).
- [Especificação da HD107S, Rose Lighting](https://www.rose-lighting.com/wp-content/uploads/sites/53/2020/05/HD107S-5050-Specificaion-V1.0.1.pdf).
