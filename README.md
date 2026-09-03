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
| Acionamento | ✅ A2212 920KV · ESC LittleBee Spring 20A (BLHeli_S) · fonte de bancada |
| Óptica | ✅ HD107S 144 LED/m (12 × 2 mm) · ESP32-C3 · A3144 nu no rotor |
| Especificação CAD | ✅ escrita, corrigida e verificada |
| Modelo CAD | ✅ **regenerado em 03/09 (rev. 3.0.3)** — revisão independente 08 aplicada: três colisões de montagem corrigidas (ponta do eixo × bateria, trilhos × arruela, cabeças dos M3 × flange), balanceamento somando os centróides do CAD; **54 de 54 critérios** |
| Compras | 🔄 motor, ESC, fita, ESP32-C3, bateria LiFe e hall em mãos |
| Isolamento de vibração | ⚠️ montagem rígida; o ensaio de impacto decide |

Nenhum bloqueador foi ensaiado ainda. **O conjunto não está liberado para girar.**

---

## Por onde começar

> ### ✅ CAD regenerado em 03/09/2026 — imprimir; medir o eixo antes da ferragem
> As cascas invertidas dos furos M3 foram confirmadas por traçado de raios e
> corrigidas (cada cortador é subtraído sozinho); o eixo de cada parafuso é
> vazio de ponta a ponta. Entraram o canal de 12,4 × 2,0 para a fita de 2 mm, o cubo Ø92 com a baia
> Ø78 × 29, o fillet da raiz, as abas de grampo, o suporte do ímã com dois
> parafusos, o layout da baia com contrapeso planejado e os critérios medidos
> na malha. O traçado de raios ainda achou e corrigiu uma lâmina de ar de
> 0,05 mm sob a flange da torre.
>
> **O desenho do motor mudou a fixação do rotor.** O colar Ø8 do eixo sobe 5 a
> 7 mm acima da campânula: a arruela M6 Ø20 da spec assentaria nele e a porca
> não apertaria o cubo. Agora é arruela Ø20 × Ø8,5 em alumínio (cortada da
> chapa) e porca M6 fina com trava química. Falta medir, a partir da face de
> apoio, o topo do colar e a ponta do eixo. O rotor fecha em 278,6 g com
> massas de catálogo para a eletrônica: pesar tudo antes de fixar. Pacote em
> [`Hologram_Orbiter_v3_0/`](Hologram_Orbiter_v3_0/README.md); o que falta em
> [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md).

| Se você vai… | Leia |
|---|---|
| Modelar o CAD | [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md) — sozinho, basta |
| Entender fases e prazos | [`02-PLANO-DE-PROJETO-v3.0.md`](02-PLANO-DE-PROJETO-v3.0.md) |
| Comprar | [`03-LISTA-DE-COMPONENTES-v3.0.md`](03-LISTA-DE-COMPONENTES-v3.0.md) |
| Ensaiar | [`04-PLANO-DE-ENSAIOS-v3.0.md`](04-PLANO-DE-ENSAIOS-v3.0.md) |
| Montar a eletrônica | [`05-ESQUEMA-ELETRICO-v3.0.md`](05-ESQUEMA-ELETRICO-v3.0.md) |
| Saber de onde veio um número | §10 da especificação (memória de cálculo) e [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) §2; a auditoria da v2.1 está em [`legado/`](legado/LEIA-ME.md) |
| Ver o que ainda falta | [`06-PENDENCIAS-ABERTAS-v3.0.md`](06-PENDENCIAS-ABERTAS-v3.0.md) |
| Entender um termo, ou saber se um número foi medido | [`07-GLOSSARIO-E-PREMISSAS.md`](07-GLOSSARIO-E-PREMISSAS.md) |
| Saber o que já foi revisado, e como | [`revisoes/`](revisoes/LEIA-ME.md) |

**Hierarquia de autoridade.** Em caso de conflito: o arquivo de parâmetros do CAD
manda em cota; a especificação manda em requisito e, no §10, em grandeza física;
o plano de ensaios manda em critério de aceite; o glossário diz o que foi medido
e o que é premissa.

---

## Números que governam o projeto

| | valor | consequência |
|---|---:|---|
| Raio do plano médio do painel | 100 mm | define arrasto, força e imagem |
| Rotação | 1800 RPM | 188,50 rad/s · 30 rps |
| Taxa de imagem | 90 Hz | 3 painéis × 30 rps |
| Corrente de fase prevista | **4,95 A** | 16,2 W na fonte (melhor caso 4,44 A / 14,4 W) |
| Temperatura do motor prevista | **46 °C** | limite de aceite: 55 °C (melhor caso 43 °C) |
| Força centrífuga por painel | 149,7 N (massa CAD) · 158,1 N (projeto, 44,5 g) | SF ≈ 2,5 na flexão |
| Massa do painel montado | ~42,1 g | Δm entre os três ≤ **0,084 g** |
| Massa do rotor | ~278,6 g (CAD + catálogo + contrapeso; folga de 1,4 g até 280) | desbalanceamento admissível 8,4 g·mm (conservador, com 252 g) |
| Energia armazenada | 27,6 J | um painel solto: 7,9 J a 18,9 m/s |

---

## O que a v3.0 corrigiu

A v2.1 perseguia 90 Hz subindo a rotação com o raio fixo em 130 mm. Como a
potência aerodinâmica escala com **ω³r³**, esse é o caminho caro: exigia 9,76 A e
levava o motor a 101 °C — inviável com o motor e o ESC que temos.

Os mesmos 90 Hz, na **mesma** 1800 RPM, com o raio em 100 mm, custam **4,95 A e
46 °C** pela estimativa de arrasto do próprio CAD (4,44 A e 43 °C no melhor
caso). O alvo estava certo; a alavanca estava errada.

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
01-ESPECIFICACAO-CAD-v3.0.md       cotas, tolerâncias, requisitos de modelagem, memória de cálculo (§10)
02-PLANO-DE-PROJETO-v3.0.md        fases, portões, cronograma, riscos
03-LISTA-DE-COMPONENTES-v3.0.md    BOM, compras, instrumentação
04-PLANO-DE-ENSAIOS-v3.0.md        cinco bloqueadores e critérios
05-ESQUEMA-ELETRICO-v3.0.md        eletrônica embarcada do rotor
06-PENDENCIAS-ABERTAS-v3.0.md      o que ainda falta
07-GLOSSARIO-E-PREMISSAS.md        vocabulário e o que é medido × assumido
Hologram_Orbiter_v3_0/             CAD, STLs, montagem, relatórios
legado/                            v2.0, v2.1 e a auditoria da v2.1, arquivadas
revisoes/                          revisões independentes, arquivadas por data
```

---

## Histórico

| Versão | Data | O que foi |
|---|---|---|
| v2.0 | ago/2026 | 1200 RPM, 60 Hz, r = 130 mm. Flicker perceptível. |
| v2.1 | ago/2026 | Subiu para 1800 RPM mantendo r = 130. Reprovada em auditoria. |
| **v3.0** | **set/2026** | **1800 RPM com r = 100 mm. 90 Hz a 46 °C.** |

Os documentos das versões anteriores e a auditoria que as reprovou estão em
`legado/`, arquivados. Eles contêm números que a v3.0 substituiu — **não os use
como referência.**
