# Plano de projeto — Hologram Orbiter v3.0

---

## 1. O que o projeto entrega

Um display volumétrico por persistência de visão: três painéis de LEDs
endereçáveis girando a 1800 RPM formam uma imagem cilíndrica de **Ø208 × 201 mm**,
com **29 × 180 pixels** e taxa de imagem de **90 Hz**.

Entregáveis finais:

1. protótipo mecânico balanceado, operando de forma estável e contida;
2. cadeia óptica funcional — fita, controlador, índice angular, imagem de teste;
3. os cinco bloqueadores aprovados com evidência registrada;
4. documentação de operação, com memória de cálculo rastreável.

## 2. Estado atual

| Bloco | Situação |
|---|---|
| Ponto de operação | ✅ congelado — r = 100 mm, 1800 RPM, 90 Hz |
| Cadeia de acionamento | ✅ definida — A2212 920KV, ESC 15 A, fonte de bancada |
| Cadeia óptica | ✅ definida — HD107S 144/m, ESP32-C3, hall no rotor |
| Especificação CAD | ✅ escrita e corrigida |
| Modelo CAD | ✅ v3.0 entregue e verificado independentemente |
| Compras | 🛒 não iniciadas |
| Contenção | ✅ especificada — tubo PC Ø275 × 4 × 300 mm, a encomendar |
| Isolamento de vibração | ⚠️ decisão pendente; montagem inicial rígida |

## 3. Como este plano difere do anterior

A versão anterior perseguia 90 Hz subindo a rotação com o raio fixo em 130 mm.
Como a potência aerodinâmica escala com **ω³r³**, isso exigia 9,76 A e levava o
motor a 101 °C — inviável com o A2212 920KV e o ESC de 15 A que temos.

Os mesmos 90 Hz, na **mesma** 1800 RPM, com o raio em 100 mm, custam **4,44 A e
43 °C**. O alvo estava certo desde o começo; a alavanca estava errada.

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
| Encomenda do cilindro de contenção | tubo PC Ø275 × 4 mm × 300 mm |
| Medição do assento da campânula | decide se o adaptador de hélice é necessário |
| Layout da baia de eletrônica | confirma que tudo cabe em Ø66 × 20 |

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
| Aranha no eixo, com arruela metálica e porca baixa | rotor acoplado |
| Painéis nas longarinas, porcas nyloc | rotor completo, sem LEDs |
| Balanceamento estático | painéis casados em massa |
| Cilindro de contenção montado na pista da base | contenção definitiva |

**Portão G2:** rotor montado, girando à mão sem rocamento perceptível,
contenção montada.

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
| Rebalanceamento com a eletrônica montada | rotor final balanceado |

**Portão G4:** imagem de teste estável a 1800 RPM, taxa de dados confirmada.

### Fase 5 — Validação visual e demonstração

Ensaio E, ajuste de brilho e contraste, documentação de operação.

**Portão G5:** jitter imperceptível em sacada, operação contínua estável.

---

## 5. Cronograma

Semanas relativas à entrega do CAD. Deslocam junto com ela.

| Semana | Fase | Marco |
|---|---|---|
| 1 | 0 | CAD entregue · compras disparadas · cilindro medido |
| 2 | 1 | cupons · lote dos painéis · aranha e tampa |
| 3 | 1 | base e torre (impressão longa) · chapa cortada |
| 4 | 2 | montagem · balanceamento estático · **G2** |
| 5 | 3 | ensaios A e B |
| 6 | 3 | ensaios C e D · **G3** |
| 7 | 4 | fiação, eletrônica, firmware |
| 8 | 4 | imagem de teste · rebalanceamento · **G4** |
| 9 | 5 | ensaio E · ajustes · **G5** |

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
| Assento da campânula pequeno demais | média | alto | medição na Fase 0 | adaptador de hélice em alumínio |
| Baia não comporta a eletrônica | média | médio | layout na Fase 0 | ESP32-C3; regulador menor; baia mais alta |
| Vibração acima do limite | baixa | médio | FFT em G3 | balanceamento em dois planos |
| Falha estrutural do painel | baixa | **crítico** | trinca na inspeção | SF 2,5 sem fadiga — inspecionar entre patamares |

**O risco que mais mudou de posição:** a partida. Com inércia 100× a de uma
hélice e ESC sensorless, é agora um bloqueador próprio, não um detalhe de
configuração.

**O risco menos confortável:** o fator de segurança de 2,5 na flexão do painel,
sem análise de fadiga. A 30 rps são 108 mil ciclos por hora. Não há FEA nem
ensaio de fadiga no escopo — a mitigação é inspeção visual entre patamares de
rotação e substituição preventiva se aparecer trinca.

---

## 7. Definição de sucesso

O projeto é bem-sucedido quando, simultaneamente:

- a imagem se forma a 90 Hz, estável e sem jitter perceptível em sacada;
- P_entrada ≤ 20 W e o motor estabiliza abaixo de 55 °C em regime contínuo;
- a vibração a 30 Hz fica em ≤ 0,20 g, sem crescimento;
- o rotor parte de forma confiável, 10 vezes em 10;
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
| [`05-ESQUEMA-ELETRICO-v3.0.md`](05-ESQUEMA-ELETRICO-v3.0.md) | eletrônica embarcada do rotor |
| [`00-AUDITORIA-E-INTEGRACAO-v2.1.md`](00-AUDITORIA-E-INTEGRACAO-v2.1.md) | memória de cálculo e histórico |
