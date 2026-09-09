# Hologram Orbiter

Display por persistência de visão com três painéis de LEDs. Ponto de projeto:
raio médio 100 mm, 1800 RPM, 29 LEDs por painel e 180 colunas angulares.
A cinemática prevê 90 passagens por segundo; desempenho óptico ainda depende de firmware e ensaio.

**Versão vigente: v3.0, revisão local 3.0.4 de 08/09/2026.**

## Estado

**Não liberado para girar nem para a fabricação definitiva dos painéis.**
A revisão corrigiu a memória de flexão, as contas de partida e energia, os
procedimentos de instrumentação, a parametrização das folgas e as falhas do build.
O buck e suas guias foram recuados radialmente 1,2 mm para eliminar a colisão
com a aranha; o novo teste verifica os envelopes contra a malha final.

A seção do painel tem Iyy = **589,8846 mm⁴**, abaixo dos 910 usados antes.
O modelo uniforme dá **3,83–7,74 mm** de deflexão com 44,5 g; no teto de aceite
45 g, chega a **7,83 mm** e ~29,1 MPa. Esses resultados corrigem a aritmética,
mas exigem fechar a transferência de carga, as propriedades FDM e a fluência.

Os relatórios automáticos são a referência da execução atual:

- [Aceitação geométrica](Hologram_Orbiter_v3_0/reports/ACEITACAO.md).
- [Validação e valores atuais](Hologram_Orbiter_v3_0/reports/RELATORIO_VALIDACAO.md).
- [Cálculos reproduzíveis](Hologram_Orbiter_v3_0/reports/FISICA.json).
- [Revisão completa](revisoes/2026-09-08-REVISAO-COMPLETA.md) e [correções aplicadas](revisoes/2026-09-08-CORRECOES-APLICADAS.md).

Aprovação geométrica não substitui os bloqueadores físicos. Massas de catálogo,
chicotes, bateria, ferragens e contrapesos devem ser reconciliados na pesagem real;
o subtotal CAD não comprova a margem até 280 g.

## Números de projeto

| Grandeza | Valor e condição |
|---|---|
| Rotação / velocidade angular | 1800 RPM / 188,496 rad/s |
| Motor / acionamento | A2212 920KV / ESC LittleBee Spring 20A |
| Corrente de regime prevista | 4,95 A de fase; ~16,63 W / 2,38 A na fonte de 7 V, com eficiência ESC assumida de 95% |
| Temperatura prevista | ~46,4 °C, sob as hipóteses térmicas; limite de aceite <55 °C |
| Partida nominal | rampa de RPM ≥12 s; ~7,30 A de fase / 4,02 A na fonte; medir aceleração real |
| Esticada a 2000 RPM | ~6,11 A / 56,3 °C; não liberada |
| Carga radial de referência | 158,1 N por painel de 44,5 g; ~159,9 N a 45 g |
| Energia de projeto | ~27,5 J para J=1,55 g·m², hipótese conservadora não medida |
| Painel solto | ~7,9 J e 18,9 m/s na referência de 44,5 g / r=100 mm |
| Desbalanceamento de referência | 8,4 g·mm usando 252 g; recalcular com a massa final e medir em dois planos |

## Documentos

| Uso | Arquivo |
|---|---|
| Cotas e memória de cálculo | [01 — Especificação](01-ESPECIFICACAO-CAD-v3.0.md) |
| Fases e portões | [02 — Plano de projeto](02-PLANO-DE-PROJETO-v3.0.md) |
| Componentes e instrumentos | [03 — Lista de componentes](03-LISTA-DE-COMPONENTES-v3.0.md) |
| Critérios físicos de aceite | [04 — Plano de ensaios](04-PLANO-DE-ENSAIOS-v3.0.md) |
| Eletrônica e firmware planejado | [05 — Esquema elétrico](05-ESQUEMA-ELETRICO-v3.0.md) |
| O que ainda falta | [06 — Pendências](06-PENDENCIAS-ABERTAS-v3.0.md) |
| Medições e premissas | [07 — Glossário](07-GLOSSARIO-E-PREMISSAS.md) |
| CAD, STL e montagem | [Pacote CAD](Hologram_Orbiter_v3_0/README.md) |

Parâmetros do CAD governam cotas, a especificação governa requisitos e o plano
de ensaios governa aceite físico. Divergências devem ser corrigidas; não se deve
escolher o valor que favorece a aprovação. O legado permanece arquivado e as
revisões históricas descrevem os resultados da data indicada.

Sentido de giro: anti-horário visto de cima; bordo de ataque em +y local.
Balança de 0,01 g, contenção e operação remota são requisitos do ensaio.
