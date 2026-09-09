# Correções locais aplicadas — 08/09/2026, revisão 3.0.4

As correções digitais comprovadas na revisão foram aplicadas localmente, com
regeneração completa do pacote. Nenhum commit ou envio remoto foi realizado.

**Resultado da verificação:** 56/56 critérios geométricos, nove/nove STLs,
25 renders regenerados e 16 testes de regressão aprovados. Os hashes dos
artefatos, código e parâmetros coincidem com `reports/build_manifest.json`.
A vista da baia regenerada foi inspecionada visualmente.

## Disposição dos achados

| Achado | Alteração aplicada | O que ainda depende de trabalho físico |
|---|---|---|
| R01 — seção/flexão | Novo `CAD/physics.py`: integra a seção e confere três cortes do STL; inclui flexão assimétrica e separa carga uniforme de estimativa distribuída parcial. Folga radial usa o teto de 45 g. | Transferência de carga, rigidez/resistência FDM e fluência; lote definitivo de painéis não liberado. |
| R02 — partida | Rampa nominal de RPM ≥12 s, ~7,30 A de fase / 4,02 A na fonte de 7 V. Critérios de corrente preservados. | Firmware do gerador e aceleração real devem ser ensaiados. |
| R03 — 2000 RPM | Previsão corrigida para 6,11 A e 56,3 °C; retirada a indicação de margem térmica. | Esticada não liberada; arrasto/térmica reais. |
| R04 — térmica | Procedimento corrigido para não prender cabo a superfície girante; distinção entre ponto fixo e medição embarcada/sem contato. | Instrumentos, calibração e relação do ponto de medição com o limite. |
| R05 — balanceamento | Referência fixa 1/rev, medições independentes e massas de teste em cada plano especificadas. | Qualificar método e executar ensaio, inclusive em G3 sem Hall embarcado. |
| R06 — Hall | Teste usa VCC=5 V e pull-up para 3,3 V. | Identificar sensor e confirmar polaridade antes de colar. |
| R07 — build | Staging, propagação de erro Python e aceitação, inventário obrigatório, preservação dos artefatos anteriores em falhas, rollback da promoção e manifesto de hashes. | Nenhum ensaio físico é substituído por aprovação do build. |
| R08 — colisão | Buck e guias recuados 1,2 mm radialmente, mantendo 140°; `wall_gap` passa de 0,3 para 1,5 mm. Novo teste contra a malha final mostra zero interseção nos quatro envelopes. | Conferir módulos, fios, soldas e retenção reais. |
| R09 — chicotes | Guias e parâmetros alinhados em seis condutores por painel; estimativas de massa e envelope marcadas como não verificadas. | Pesar e testar passagem completa; reconciliar chicote/ferragens. |
| R10 — acesso à porca | Sequência aperta o cubo antes de instalar a bateria e fechar a tampa. | Conferir ferragens, colar, rosca e acesso reais. |
| R11 — folga inoperante | `CAD/parameters.py` deriva socket e cupom da espiga e folgas; cotas duplicadas conflitantes são rejeitadas. | Calibração do cupom na impressora. |
| R12 — limites ignorados | Aceite lê massa configurada, dimensões X/Y da mesa e requisitos de arrasto/parede amostrada. Testes negativos verificam a reprovação de mesa menor e limite de massa mais estrito. | Geometria paramétrica continua sujeita aos requisitos da especificação. |
| R13 — energia | Base explícita: 26,1 W nos LEDs em branco, carga adicional estimada de 0,3 W uma única vez e eficiência do buck de 87,5%. Teto inicial de corrente/brilho efetivo em 80%, condicionado à capacidade real. | Consumo, dropout, aquecimento e autonomia reais; não há firmware implementado neste pacote. |
| R14 — margem magnética | Diferenciados BOP máximo de 35 mT a 25 °C e 45 mT na faixa térmica. | Campo/entreferro/temperatura reais; margem nominal não é garantida. |

## Valores após regeneração

| Grandeza | Resultado |
|---|---:|
| Iyy da seção contínua | 589,8846 mm⁴ |
| Deflexão, referência 44,5 g | 3,83–7,74 mm |
| Deflexão máxima no teto de 45 g | 7,83 mm |
| Tensão máxima no modelo uniforme a 45 g | ~29,1 MPa |
| Folga radial calculada ao cilindro | 21,17 mm |
| Massa CAD da aranha | 71,06 g |
| Subtotal nominal do rotor | 278,85 g |
| Contrapesos nominais em r=33 mm | 2,19 g a 180° + 0,86 g a 300° |
| Resíduo estático nominal após correção | 0,13 g·mm |

O subtotal inclui o Hall de 0,2 g, antes omitido da soma embora presente no
vetor de balanceamento. **Não comprova margem de 1,15 g:** chicotes/ferragens
de cada painel ainda precisam ser reconciliados e pesados. Os contrapesos são
um ponto inicial de catálogo, não resultado de balanceamento físico.

O relatório de validação passou a ser gerado para eliminar a tabela manual
desatualizada. As referências globais corretas são Z=186 no topo do cubo,
Z=195 no fundo da bateria e Z=212 no topo da bateria. Quadros SPI têm 2860 bits;
a documentação distingue taxa de bits, overhead, clock real e atualização óptica.

## Verificações executadas

```sh
bash Hologram_Orbiter_v3_0/scripts/build.sh
python3 -m unittest discover -s Hologram_Orbiter_v3_0/tests -v
python3 -m unittest discover -s Hologram_Orbiter_v3_0/scripts/tests -v
git diff --check
```

Os nove testes de física/parâmetros incluem integração contra solução analítica,
seções do STL, rampa/energia, alteração de folgas e limites que devem reprovar.
Os sete testes de pipeline simulam geração para verificar falha Python, aceite
reprovado com exit zero, inventário ausente/vazio, falha de render, rollback e
publicação coerente com parâmetros externos/hashes. O build final usou o Blender
real, não o simulador dos testes.

Relatórios atuais em `Hologram_Orbiter_v3_0/reports/`; auditoria anterior e suas
evidências foram preservadas como histórico. **Giro e fabricação definitiva dos
painéis continuam bloqueados pelos itens físicos e estruturais acima.**
