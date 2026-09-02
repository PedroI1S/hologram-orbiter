# Hologram Orbiter

Display volumétrico por persistência de visão. Três painéis de LEDs
endereçáveis giram a 1800 RPM e formam uma imagem cilíndrica suspensa de
**Ø208 × 201 mm**, com **29 × 180 pixels** e taxa de imagem de **90 Hz**.

**Versão corrente: v3.0** · Equipe Robotinik · Oficina de Integração

---

## Estado

| Bloco | Situação |
|---|---|
| Ponto de operação | ✅ congelado — r = 100 mm · 1800 RPM · 90 Hz |
| Acionamento | ✅ A2212 920KV · ESC 15 A · fonte de bancada em 6–7 V |
| Óptica | ✅ HD107S 144 LED/m · ESP32-C3 · hall no rotor |
| Especificação CAD | ✅ escrita, corrigida e verificada |
| Modelo CAD | ⚠️ **regeneração pendente** — 12 itens, 2 deles P0 nos painéis |
| Compras | 🛒 não iniciadas |
| Isolamento de vibração | ⚠️ decisão pendente — montagem inicial rígida |

Nenhum bloqueador foi ensaiado ainda. **O conjunto não está liberado para girar.**

---

## Por onde começar

> ### ⛔ Aguardando regeneração do CAD
> Doze itens em fila, dois deles bloqueadores nos painéis: **cascas invertidas**
> (enrolamento −1) nos furos M3 e uma **membrana de espessura zero** no canal do
> LED, ambos confirmados por ray cast independente. Causa em `generate.py`:
> `subtract_all()` concatena os cortadores em vez de uni-los.
>
> Entram na mesma rodada o canal em degrau (a fita medida tem 2,0 mm, não 1,0) e
> a baia ampliada para Ø78 × 26. Lista completa em
> [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md).

| Se você vai… | Leia |
|---|---|
| Modelar o CAD | [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md) — sozinho, basta |
| Entender fases e prazos | [`02-PLANO-DE-PROJETO-v3.0.md`](02-PLANO-DE-PROJETO-v3.0.md) |
| Comprar | [`03-LISTA-DE-COMPONENTES-v3.0.md`](03-LISTA-DE-COMPONENTES-v3.0.md) |
| Ensaiar | [`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md) |
| Montar a eletrônica | [`05-ESQUEMA-ELETRICO-v3.0.md`](05-ESQUEMA-ELETRICO-v3.0.md) |
| Saber de onde veio um número | [`00-AUDITORIA-E-INTEGRACAO-v2.1.md`](00-AUDITORIA-E-INTEGRACAO-v2.1.md) |
| Ver o que ainda falta | [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md) |
| Entender um termo, ou saber se um número foi medido | [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) |

**Hierarquia de autoridade.** Em caso de conflito: o arquivo de parâmetros do CAD
manda em cota; a especificação manda em requisito; o plano de ensaios manda em
critério de aceite; a auditoria manda em grandeza física.

---

## Números que governam o projeto

| | valor | consequência |
|---|---:|---|
| Raio do plano médio do painel | 100 mm | define arrasto, força e imagem |
| Rotação | 1800 RPM | 188,50 rad/s · 30 rps |
| Taxa de imagem | 90 Hz | 3 painéis × 30 rps |
| Corrente de fase prevista | 4,44 A | 14,4 W na fonte |
| Temperatura do motor prevista | 43 °C | limite de aceite: 55 °C |
| Força centrífuga por painel | 148,8 N | SF de 2,7 na flexão |
| Massa do painel montado | ~42,8 g | Δm entre os três ≤ **0,084 g** |
| Massa do rotor | 252 g | desbalanceamento admissível 8,4 g·mm |
| Energia armazenada | 26,1 J | um painel solto: 7,4 J a 19,6 m/s |

---

## O que a v3.0 corrigiu

A v2.1 perseguia 90 Hz subindo a rotação com o raio fixo em 130 mm. Como a
potência aerodinâmica escala com **ω³r³**, esse é o caminho caro: exigia 9,76 A e
levava o motor a 101 °C — inviável com o motor e o ESC que temos.

Os mesmos 90 Hz, na **mesma** 1800 RPM, com o raio em 100 mm, custam **4,44 A e
43 °C**. O alvo estava certo; a alavanca estava errada.

Uma auditoria independente encontrou 24 não conformidades na v2.1, entre elas
força centrífuga publicada 71× menor que a real, um caso térmico que reprovava
com os próprios dados do documento, uma membrana de 0,20 mm sob o canal do LED,
os três painéis sobrepostos na montagem, e o padrão de furação do motor errado.
Doze foram resolvidas pela decisão de projeto e pelas medições de hardware.

---

## Três coisas fáceis de errar

**Sentido de giro: anti-horário visto de cima.** Todo bordo de ataque aponta para
+y. Invertido, o arrasto sobe muito e o bloqueador A reprova sem motivo aparente.

**A balança precisa de 0,01 g.** O Δm admissível entre painéis é 0,084 g. Uma
balança de 0,1 g mede exatamente o tamanho do erro que deveria detectar.

**Nada gira sem contenção.** O rotor guarda 26 J e um painel solto sai a
18,9 m/s. Operação remota e ninguém no plano do rotor durante a subida.

---

## Estrutura

```
README.md                          este arquivo
00-AUDITORIA-E-INTEGRACAO-v2.1.md  memória de cálculo e histórico
01-ESPECIFICACAO-CAD-v3.0.md       cotas, tolerâncias, requisitos de modelagem
02-PLANO-DE-PROJETO-v3.0.md        fases, portões, cronograma, riscos
03-LISTA-DE-COMPONENTES-v3.0.md    BOM, compras, instrumentação
04-PLANO-DE-ENSAIOS-v3.0.md        cinco bloqueadores e critérios
05-ESQUEMA-ELETRICO-v3.0.md        eletrônica embarcada do rotor
06-PENDENCIAS-ABERTAS-v3.0.md      o que ainda falta
07-GLOSSARIO-E-PREMISSAS.md        vocabulário e o que é medido × assumido
Hologram_Orbiter_v3_0/             CAD, STLs, montagem, relatórios
legado/                            versões anteriores, arquivadas
```

---

## Histórico

| Versão | Data | O que foi |
|---|---|---|
| v2.0 | ago/2026 | 1200 RPM, 60 Hz, r = 130 mm. Flicker perceptível. |
| v2.1 | ago/2026 | Subiu para 1800 RPM mantendo r = 130. Reprovada em auditoria. |
| **v3.0** | **set/2026** | **1800 RPM com r = 100 mm. 90 Hz a 43 °C.** |

Os documentos das versões anteriores estão em `legado/`, arquivados. Eles contêm
números que a auditoria invalidou — **não os use como referência.**
