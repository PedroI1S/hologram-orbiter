# Legado — versões `v2.0`, `v2.1` e `v3.0`

**Estes documentos e pacotes estão arquivados e não devem ser usados como
referência vigente.**  
A versão corrente do projeto é a **v4.0** (`14/11/2026`): comece pelo
[`../README.md`](../README.md).

---

## v3.0 (arquivada em 14/11/2026 em `v3.0/`)

A `v3.0` utilizava **base rígida** integrada, **aranha sem reforço de aleta/alma**,
**motor `A2212 920KV`**, baia `Ø78/82 × 29 mm` e cabeamento em **6 condutores**
(com retorno nas fitas). Foi substituída pela **v4.0**, que promoveu a base
suspensa em paralelogramo travável + aranha reforçada (`3.1-P.2`), o motor
**`AX-2810Q 750KV`** e a topologia **SPI Quad** de 4 condutores por painel.

| Item em `v3.0/` | O que era |
|---|---|
| `v3.0/README-v3.0.md` e `01`–`07` (`*-v3.0.md`) | Documentação completa da revisão `v3.0` (`3.0.5`) |
| `v3.0/Hologram_Orbiter_v3_0/` | Pacote CAD `v3.0` + histórico da variante experimental em `variantes/paralelogramo/` (antes da promoção a `Hologram_Orbiter_v4/`) |
| `v3.0/teste-fitas-esp32-base.rs` | Código de teste antigo das fitas na ESP32 da base (substituído por `../firmware/teste-fitas-c3/`) |

---

## v2.0 e v2.1 (arquivadas na raiz de `legado/` em 03/09/2026)

Uma auditoria independente (`01/09/2026`) encontrou 24 não conformidades na
`v2.1`, incluindo força centrífuga publicada **71× menor** que a real (`2,26 N`
contra `161,7 N`), caso térmico inválido, ensaio de amortecimento errado por
**3×**, massa de coxim publicada **10× maior** que a geométrica, limite de
corrente de `5,8 A` sem derivação e referências a 8 arquivos inexistentes.

| Arquivo | O que era |
|---|---|
| `00-AUDITORIA-E-INTEGRACAO-v2.1.md` | Auditoria da `v2.1` e decisões que originaram o ponto de operação `r = 100 mm @ 1800 RPM` |
| `README-v2.1.md` | Índice antigo da `v2.1` |
| `Plano-de-Projeto-v2.1.md` | Plano de fases antigo |
| `Especificacao-CAD-v2.1.md` | Especificação das 10 peças a `r = 130 mm` |
| `Revisao-Tecnica-e-Ajustes.md` | Estrutura inicial dos bloqueadores |
| `GUIA-Impressao-Coxim-TPU-v2.1.md` | Procedimento TPU antigo com três erros graves |
| `Hologram_Orbiter_v2_1/` e `.zip` | Pacote CAD da `v2.1`, inalterado |
