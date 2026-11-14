# Revisões (histórico `v3.0`)

Revisões independentes, relatos e ensaios do pacote **v3.0**, arquivados por
data. Cada documento preserva o estado e os números do projeto na data
indicada.

**Estes documentos não mandam em cota nem em requisito vigente.** O projeto foi
promovido para a **v4.0** (`14/11/2026`, ver [`../README.md`](../README.md)):
`Hologram_Orbiter_v4/CAD/parameters.json` manda em cota,
[`../01-ESPECIFICACAO-CAD-v4.0.md`](../01-ESPECIFICACAO-CAD-v4.0.md) em
requisito, [`../04-PLANO-DE-ENSAIOS-v4.0.md`](../04-PLANO-DE-ENSAIOS-v4.0.md)
em critério de aceite e
[`../07-GLOSSARIO-E-PREMISSAS.md`](../07-GLOSSARIO-E-PREMISSAS.md) no que foi
medido. Os documentos congelados da `v3.0` foram arquivados em
[`../legado/v3.0/`](../legado/v3.0/).

O que **falta** está sempre em
[`../06-PENDENCIAS-ABERTAS-v4.0.md`](../06-PENDENCIAS-ABERTAS-v4.0.md), não
aqui.

## Conteúdo

| Arquivo | Escopo histórico (`v3.0`) | Desdobramento na `v4.0` |
|---|---|---|
| [`2026-10-30-OSCILACAO-ALVO-1300US.md`](2026-10-30-OSCILACAO-ALVO-1300US.md) | relato de oscilação na aceleração até `1300 µs` (`A2212`, torre maciça) | motivou a suspensão em paralelogramo e o cuidado com bandas críticas na `v4.0` |
| [`2026-10-30-TORRE-MACICA-PETG.md`](2026-10-30-TORRE-MACICA-PETG.md) | torre maciça em PETG confirmada sem furo `Ø22` | adotada em definitivo na torre maciça `Ø40` da `v4.0` (fios por ganchos externos) |
| [`2026-10-30-TABELA-ROTACAO-VIBRACAO-PETG.md`](2026-10-30-TABELA-ROTACAO-VIBRACAO-PETG.md) | tabela calculada de pulso, RPM e harmônicos `1×/2×/3×` para torre rígida (`A2212`) | substituída pelo modelo da suspensão `v4.0` e pelo `AX-2810Q 750KV` (requer `C0`) |
| [`2026-10-27-RELATO-FALHA-ARANHA-FRENAGEM.md`](2026-10-27-RELATO-FALHA-ARANHA-FRENAGEM.md) | ruptura de braço da aranha v3.0 na frenagem automática | originou `R02` → aranha reforçada (aleta D + asa invertida) + base suspensa `v4.0` |
| [`2026-10-27-UNIFICACAO-FONTE-ESC.md`](2026-10-27-UNIFICACAO-FONTE-ESC.md) | fonte `10–12 V` com limite `30 A` e critérios do Bloqueador D | premissa mantida na `v4.0` com recálculo para `AX-2810Q` e grampo obrigatório |
| [`2026-09-21-PROPOSTA-SPI-QUAD.md`](2026-09-21-PROPOSTA-SPI-QUAD.md) | proposta SPI Quad (CLK comum + 3 DATA, 4 fios/painel) | **adotada como topologia ativa na `v4.0`** (perfboard + `teste-fitas-c3/`) |
| [`2026-09-14-CORRECAO-RAIZES-E-FIACAO.md`](2026-09-14-CORRECAO-RAIZES-E-FIACAO.md) | saliências internas e entradas de fios da aranha (`3.0.5`) | correções mantidas e validadas para baia `Ø80/84` na `v4.0` |
| [`2026-09-03-REVISAO-DAS-RATIFICACOES.md`](2026-09-03-REVISAO-DAS-RATIFICACOES.md) | revisão do pacote `3.0.3` | histórico incorporado |
| [`2026-09-08-REVISAO-COMPLETA.md`](2026-09-08-REVISAO-COMPLETA.md) e [`2026-09-08-CORRECOES-APLICADAS.md`](2026-09-08-CORRECOES-APLICADAS.md) | revisão geral e correções da `v3.0` (`3.0.4`) | histórico incorporado |
