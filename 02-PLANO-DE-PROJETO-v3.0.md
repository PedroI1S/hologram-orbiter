# Plano de projeto — Hologram Orbiter v3.0

**Atualização local 08/09, revisão 3.0.4:** fabricação definitiva dos painéis e giro dependem de fechar a revisão estrutural e qualificar a instrumentação do plano 04. O CAD é provisório.

**Atualização de 21/09:** a ESP32 da base substitui o Arduino, e o plano ganhou a imagem pelo celular: página hospedada na ESP32 da base e imagem transmitida por rádio ao rotor (esquema 05 §9).

---

## 1. O que o projeto entrega

Um display volumétrico por persistência de visão: três painéis de LEDs
endereçáveis girando a 1800 RPM formam uma imagem cilíndrica de **Ø208 × 201 mm**,
com **29 × 180 pixels** e taxa de imagem de **90 Hz**.

Entregáveis finais:

1. protótipo mecânico balanceado, operando de forma estável e contida;
2. cadeia óptica funcional — fita, controlador, índice angular, imagem de teste;
3. os cinco bloqueadores aprovados com evidência registrada;
4. documentação de operação, com memória de cálculo rastreável;
5. imagem enviada pelo celular: página hospedada na ESP32 da base e
   transmitida por rádio ao ESP32-C3 do rotor (esquema 05 §9).

## 2. Estado atual

| Bloco | Situação |
|---|---|
| Ponto de operação | ✅ congelado — r = 100 mm, 1800 RPM, 90 Hz |
| Cadeia de acionamento | ✅ A2212 920KV · ESC LittleBee Spring 20A · fonte de bancada · ESP32 da base (DevKit 30 pinos) |
| Cadeia óptica | ✅ HD107S 144/m · ESP32-C3 · A3144 nu no rotor |
| Imagem pelo celular | 🔄 planejada no esquema 05 §9; hardware em mãos, firmware a fazer |
| Especificação CAD | ✅ escrita, corrigida e alinhada ao CAD em 03/09 |
| Modelo CAD | ⚠️ rev. local 3.0.4: 56 critérios geométricos; resistência e ensaios continuam pendentes |
| Compras | 🔄 motor, ESC, fita, ESP32-C3, bateria LiFe e hall em mãos; faltam buck, shifter, ímã, ferragens, chapa e filamento |
| Medições | ⚠️ colar e ponta do eixo a partir da face de apoio; massa real da eletrônica |
| Isolamento de vibração | ⚠️ montagem rígida; o ensaio de impacto decide |

## 3. Como este plano difere do anterior

A versão anterior perseguia 90 Hz subindo a rotação com o raio fixo em 130 mm.
Como a potência aerodinâmica escala com **ω³r³**, isso exigia 9,76 A e levava o
motor a 101 °C — inviável com o A2212 920KV que temos, cujo limite prático é
térmico, em torno de 5,5 A.

Os mesmos 90 Hz, na **mesma** 1800 RPM, com o raio em 100 mm, custam **4,95 A e
46 °C** pela estimativa de arrasto do CAD (4,44 A e 43 °C no melhor caso). O
alvo estava certo desde o começo; a alavanca estava errada.

Três mudanças de método que vêm junto:

- **Nenhum número sem origem.** Toda grandeza é rastreável até um datasheet, uma
  medição ou uma linha de cálculo publicada. A versão anterior perdeu a planilha
  que gerava seus números e ficou sem como auditá-los.
- **Critérios medíveis.** Os bloqueadores são lidos em instrumentos que existem
  na bancada, não em grandezas que exigiriam instrumentação que não temos.
- **Pendência declarada em vez de valor inventado.** O que não foi medido fica
  marcado como não medido.

---

## 4. Fases

### Fase 0 — Projeto e aquisição · em curso

| Atividade | Saída |
|---|---|
| Modelagem CAD v3.0 | gerador paramétrico, STLs, montagem, relatórios |
| Verificação do CAD contra os critérios da especificação | relatório de conformidade |
| Compras do caminho crítico | bateria, ESP32-C3, regulador, hall, ímã, fio, filamento |
| Layout da baia de eletrônica | esboço verificado no CAD (envelope, interferências, contrapeso); pesar as peças reais |

**Portão G0:** CAD entregue e aprovado nos critérios do §9 da especificação;
cupons impressos e conferidos com a fita real.

### Fase 1 — Fabricação

| Atividade | Saída |
|---|---|
| Cupons C01 e C02 | folgas da junta e do canal validadas |
| Lote dos 3 painéis, mesma mesa e mesmo lote | 3 painéis medidos e pesados |
| Aranha, tampa, suporte do ímã | peças conferidas |
| Base + torre | perpendicularidade e planeza verificadas |
| Corte e furação da chapa de alumínio | suporte do motor |

**Portão G1:** massa ≤ 45 g por painel · **Δm ≤ 0,084 g** · Datum D 104 ±0,2 mm ·
raio 100 ±0,1 mm · Δh ≤ ±0,5 mm. Peça fora de tolerância é reimpressa, não ajustada.

### Fase 2 — Montagem mecânica

| Atividade | Saída |
|---|---|
| Motor na chapa, chapa na torre | conjunto fixo alinhado |
| Aranha no eixo, com a arruela Ø20 × Ø8,5 em alumínio e a porca M6 fina com trava química | rotor acoplado |
| Painéis nas longarinas, porcas planas com trava química | rotor completo, sem LEDs |
| Balanceamento estático | painéis casados em massa |
| Contenção de ensaio montada | caixa fechada, chapa ou tela; policarbonato se for usar o rádio (esquema 05 §9.4) |
| Firmware da rampa na ESP32 da base: armação, rampa ≥ 12 s, teto do pulso, watchdog e botões (esquema 05 §8.2) | sinal do ESC conferido na bancada, sem motor |

**Portão G2:** rotor montado, girando à mão sem rocamento perceptível,
contenção de ensaio montada, rampa da ESP32 da base conferida na bancada.

> **Pesar os painéis é necessário, não suficiente.** Δm ≤ 0,084 g casa as
> *massas*, não os *momentos*: dois painéis de massa idêntica com o CG em raios
> diferentes — infill que caiu mais no boss num deles e mais na lâmina no outro
> — continuam desbalanceando. 0,5 mm de diferença de CG em 42 g já vale
> 21 g·mm, duas vezes e meia o admissível. A pesagem tria os casos grosseiros;
> quem fecha a conta é o bloqueador C.

### Fase 3 — Bloqueadores de rotação

Ensaios A (potência), B (térmica), C (vibração) e D (partida). Detalhe em
[`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md).

**Portão G3:** P_entrada ≤ 20 W · T_motor < 55 °C · vibração ≤ 0,20 g a 30 Hz ·
10 de 10 partidas. **Sem LEDs até aqui.**

### Fase 4 — Integração óptica

| Atividade | Saída |
|---|---|
| Fita nos painéis, fiação pela carenagem e longarina | cadeia elétrica do rotor |
| ESP32-C3, regulador, bateria na baia | eletrônica de bordo |
| Sensor hall no rotor, ímã no suporte fixo | referência de fase |
| Firmware: SPI, índice, mapeamento de colunas | imagem de teste na tela |
| Enlace ESP-NOW: a base transmite, o rotor troca a imagem no índice | imagem enviada da base aparece na tela |
| Rebalanceamento com a eletrônica montada | rotor final balanceado |

**Portão G4:** imagem de teste estável a 1800 RPM, taxa de dados confirmada.

### Fase 5 — Validação visual e demonstração

Ensaio E, ajuste de brilho e contraste, documentação de operação.

Imagem pelo celular: página na ESP32 da base (QR code, desenho, galeria, fila e
aprovação) e ensaio do enlace de imagem do plano 04, antes de abrir ao público.

**Portão G5:** jitter imperceptível em sacada, operação contínua estável e,
depois do ensaio do enlace, imagem enviada pelo celular sem tremor.

---

## 5. Cronograma

Semanas relativas à entrega do CAD. Deslocam junto com ela.

| Semana | Fase | Marco |
|---|---|---|
| 1 | 0 | CAD regenerado · compras disparadas |
| 2 | 1 | cupons · lote dos painéis · aranha e tampa |
| 3 | 1 | base e torre (impressão longa) · chapa cortada |
| 4 | 2 | montagem · balanceamento estático · rampa na bancada · **G2** |
| 5 | 3 | ensaios A e B |
| 6 | 3 | ensaios C e D · **G3** |
| 7 | 4 | fiação, eletrônica, firmware, enlace de rádio |
| 8 | 4 | imagem de teste · rebalanceamento · **G4** |
| 9 | 5 | ensaio E · ajustes · **G5** |
| 10 | 5 | página na base · ensaio do enlace · demonstração com o celular |

**Caminho crítico:** a impressão da base leva 12–18 h numa única peça e não pode
ser paralelizada. Comece cedo, e só depois que os painéis passarem em G1 — se o
raio precisar mudar, a base muda junto.

**Folga real:** as compras (semana 1) e a impressão (semanas 2–3) correm em
paralelo. Se a bateria atrasar, as Fases 1 a 3 seguem sem ela: nada em G3 depende
da eletrônica de bordo.

---

## 6. Riscos

| Risco | Prob. | Impacto | Sinal antecipado | Mitigação |
|---|---|---|---|---|
| Arrasto acima do estimado | média | alto | P_entrada > 20 W em G3 | carenagem do boss; recuo para 1500 RPM |
| Motor aquece além do previsto | média | alto | curva térmica sem estabilizar | ventilação da baia; é o fator que decide |
| Partida sensorless falha | **média** | médio | travamento na rampa | rampa de 12 s; duty alto; ESC sensored |
| Δm entre painéis fora | média | médio | pesagem em G1 | massa adesiva; reimpressão |
| Eletrônica mais pesada que o catálogo | média | médio | pesagem das peças reais (massa completa e chicotes ainda não reconciliados) | mini560 em vez de XL4015; polyfuse em vez de porta-fusível; alívios mais fundos |
| Vibração acima do limite | baixa | médio | FFT em G3 | balanceamento em dois planos |
| Fluência do painel em operação | **média** | alto | ponta afastando entre medições | limitar tempo contínuo; medir deflexão a quente |
| Falha estrutural do painel | baixa | **crítico** | trinca na inspeção | SF 2,5 — inspecionar entre patamares |
| Ressonância da parte fixa | média | alto | pico fora de 1× na varredura | ensaio de impacto antes de montar o motor; grampear a base |
| Rádio atrasa as colunas do rotor | média | médio | tremor acima de 46 µs no ensaio do enlace | rotor só escuta; colunas acima do rádio; janelas de rádio |
| Rádio fraco no rotor | média | baixo | perda de pacotes no ensaio de alcance | 8,5 dBm na Super Mini; contenção de policarbonato; base mais perto |
| Página pública alcança o motor | baixa | **crítico** | qualquer rota de motor no servidor | página sem comando de motor; teto do pulso; watchdog; corte físico da fonte |

**O risco que mais mudou de posição:** a partida. Com inércia 100× a de uma
hélice e ESC sensorless, é agora um bloqueador próprio, não um detalhe de
configuração.

**O risco menos confortável — e mal nomeado até aqui.** Versões anteriores deste
plano falavam em "fadiga, 108 mil ciclos por hora". Está errado: **a carga
centrífuga é estática**. Num rotor de eixo vertical, nem a força centrífuga nem o
peso mudam de direção em relação ao painel — nenhum dos dois cicla a 30 Hz. Os
ciclos de fadiga reais são as **partidas e paradas**, que serão dezenas.

A **fluência** permanece um bloqueador: a seção revisada eleva a tensão do modelo uniforme a ~29,1 MPa no teto de 45 g. Não há lei medida deste ABS FDM que sustente a previsão anterior de perda de metade do módulo em 100 h. Primeiro fechar resistência e transferência de carga; depois executar o ensaio de crescimento sob carga do bloqueador B, sem presumir vida útil por extrapolação.

O que **de fato** cicla a 30 Hz é a vibração de desbalanceamento, e é por isso
que o Bloqueador C importa.

---

## 7. Definição de sucesso

O projeto é bem-sucedido quando, simultaneamente:

- a imagem se forma a 90 Hz, estável e sem jitter perceptível em sacada;
- P_entrada ≤ 20 W e o motor estabiliza abaixo de 55 °C em regime contínuo;
- a vibração a 30 Hz fica em ≤ 0,20 g, sem crescimento;
- o rotor parte de forma confiável, 10 vezes em 10;
- a imagem enviada pelo celular aparece sem tremor, e nada na página alcança o
  motor;
- toda cota e todo número do projeto são rastreáveis até um datasheet, uma
  medição ou uma linha de cálculo publicada.

Se algum critério não for atendido, a resposta correta não é forçar a operação.
É reduzir rotação, trocar a peça crítica ou revisar a geometria — cada caminho
já está escrito no plano de ensaios.

---

## 8. Documentos

| Documento | Papel |
|---|---|
| [`README.md`](README.md) | ponto de entrada e estado |
| [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md) | **manda em toda cota** |
| [`02-PLANO-DE-PROJETO-v3.0.md`](02-PLANO-DE-PROJETO-v3.0.md) | fases, portões, riscos |
| [`03-LISTA-DE-COMPONENTES-v3.0.md`](03-LISTA-DE-COMPONENTES-v3.0.md) | o que comprar e por quê |
| [`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md) | bloqueadores e critérios |
| [`05-ESQUEMA-ELETRICO-v3.0.md`](05-ESQUEMA-ELETRICO-v3.0.md) | eletrônica do rotor e da base, e o enlace de imagem |
| [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md) | o que ainda falta |
| [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) | vocabulário e origem de cada número |
| [`legado/`](legado/LEIA-ME.md) | v2.0, v2.1 e a auditoria que as reprovou — histórico, não referência |

## Condições atualizadas para os portões

Antes de G1: fechar a seção resistente e a transferência de carga/FDM/fluência; cupons de calibração não liberam o lote de painéis. Em G3 usar lastro representativo da distribuição final e referência angular fixa sincronizada, pois o Hall embarcado só entra em G4. Qualificar a medição térmica sem cabos em superfícies girantes e o método de dois planos antes de registrar aprovação. Repetir os ensaios aplicáveis em G4 com bateria, chicotes, sensores e retenções finais; reconciliar a massa completa contra 280 g. Antes de abrir a página ao público: ensaio do enlace de imagem (plano 04) e contenção fechada que deixe passar o rádio.
