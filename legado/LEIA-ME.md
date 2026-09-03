# Legado — versões v2.0 e v2.1

**Estes documentos estão arquivados e não devem ser usados como referência.**
A versão corrente é a **v3.0**; comece pelo [`../README.md`](../README.md).

Uma auditoria independente (01/09/2026) encontrou 24 não conformidades na
v2.1, incluindo:

- força centrífuga publicada **71× menor** que a real (2,26 N contra 161,7 N);
- caso térmico que **reprovava com os próprios dados** do documento;
- ensaio de amortecimento errado por **3×**, que aprovava peças fora de spec;
- massa de coxim publicada **10× maior** que a geométrica;
- limite de corrente de 5,8 A **sem derivação** — a planilha que o gerava se perdeu;
- referências a **8 arquivos que nunca existiram** neste diretório.

O registro completo, com o recálculo de cada grandeza, está em
[`00-AUDITORIA-E-INTEGRACAO-v2.1.md`](00-AUDITORIA-E-INTEGRACAO-v2.1.md),
arquivado aqui em 03/09/2026: a memória de cálculo vigente é o §10 da
especificação v3.0, e o que a auditoria ainda tem de útil é o histórico das
decisões. Os números dela sobre contenção, datum e coxim foram substituídos.

## Conteúdo

| Arquivo | O que era |
|---|---|
| `00-AUDITORIA-E-INTEGRACAO-v2.1.md` | auditoria da v2.1 e a decisão que gerou a v3.0 (r = 100 mm @ 1800 RPM); histórico |
| `README-v2.1.md` | índice da v2.1 — a maior parte dos números está errada |
| `Plano-de-Projeto-v2.1.md` | plano de fases; §2.3 tem força centrífuga 2× baixa |
| `Especificacao-CAD-v2.1.md` | especificação das 10 peças a r = 130 mm |
| `Revisao-Tecnica-e-Ajustes.md` | método dos bloqueadores — a estrutura era boa |
| `GUIA-Impressao-Coxim-TPU-v2.1.md` | procedimento TPU com três erros graves |
| `Hologram_Orbiter_v2_1/` e `.zip` | pacote CAD da v2.1 (gerador, STL, relatórios), inalterado |
