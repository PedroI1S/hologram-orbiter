# Revisão das ratificações de 03/09/2026

Revisão independente do pacote **v3.0, revisão de CAD 3.0.3**, feita depois das
três ratificações de Pedro (B'3, C2 e C9) registradas no commit `54cdc67`.
Escopo: documentos 01 a 07, o README, o pacote `Hologram_Orbiter_v3_0/` e os
STL exportados.

**Método.** Releitura cruzada dos documentos contra `CAD/parameters.json` e
`reports/`, recálculo independente das massas e do balanceamento, e execução do
validador de malhas `scripts/validate_stl.py` a partir dos STL versionados, com
comparação campo a campo contra `reports/stl_validation.json`.

**Estado desta revisão:** aplicada em 03/09/2026. A tabela de propagação da §5
foi corrigida arquivo a arquivo; o que continua aberto está na §7.

---

## 1. Veredito

O CAD, o arquivo de parâmetros e a lista de pendências estão coerentes entre si,
e as três ratificações são tecnicamente bem fundamentadas.

O defeito encontrado foi de **propagação**, não de projeto: a revisão 3.0.3
mudou massa do rotor, altura da baia, posição dos trilhos e contrapeso, e só a
lista de pendências e o gerador acompanharam. Catorze arquivos continuavam
publicando os números da 3.0.2. Somaram-se a isso um erro factual no texto de C9
e três referências cruzadas quebradas.

| Verificação | Resultado |
|---|---|
| STL revalidados (topologia, enrolamento, faces coincidentes) | 9 de 9 |
| Critérios do gerador contra as malhas exportadas | 54 de 54 |
| Arquivos com números da revisão 3.0.2 ainda publicados | 14 |

---

## 2. O que está bom

**Malhas.** O validador rodado do zero devolve os nove STL passando, e o
resultado coincide campo a campo com o relatório versionado. Os volumes
multiplicados pela densidade do ABS batem com o relatório de aceitação: a aranha
dá 68,26 cm³ → 71,0 g e a base 307,50 cm³ → 319,8 g.

**Contrapeso repartido.** A soma vetorial refeita confirma a decisão: 2,19 g a
180° mais 0,87 g a 300°, em r = 33, cancelam os 63,0 g·mm a 23,3° e deixam
0,06 g·mm de resíduo. Repartir entre os dois alívios que cercam a direção, em vez
de arredondar para o mais próximo, é o que evita os ~17 g·mm que o arranjo
anterior deixaria. O gerador mede o resíduo de volta a partir das massas
propostas, que é a forma honesta de fechar a conta.

**Orçamento do rotor.** 3 × 31,94 de painel, mais 71,0 de aranha e 10,1 de tampa,
mais fitas, ferragens, bateria, ferragem do eixo, folga de eletrônica e 3,06 g de
contrapeso fecham em 278,59 g. A conta é reproduzível a partir dos parâmetros.

**B'3, canal único.** O argumento físico está certo: a fita é um PCB plano com os
LEDs em cima, e um canal em degrau só funcionaria com ela de cabeça para baixo. A
especificação §5.1, os parâmetros, o cupom C02 e o relatório de aceitação contam
a mesma história, com o piso de 0,8 mm medido na malha.

**C2, polaridade.** O alerta está tecnicamente correto: a família A314x comuta
com o polo sul apresentado à face marcada do TO-92, e "face positiva" não é
convenção de datasheet. Registrar a decisão com `polarity_bench_confirmed = false`
e um ensaio de bancada de um minuto é a forma certa de impedir que a ambiguidade
vire uma falha diagnosticada como firmware.

**C9, ESC.** Recortar a pendência ao que de fato continua aberto — margem do
regulador interno e do gate driver a 6 V, e a saída dos fios de fase — e
recomendar começar os ensaios em 7,0 V é uma decisão prudente e barata.

**Rastreabilidade.** Cada desvio de especificação tem nota em `parameters.json`
apontando para a tabela de disposição da revisão. A observação de que corrigir os
trilhos invalidou a sondagem de outro critério, que continuava passando medindo a
coisa errada, é o tipo de aviso que poupa o próximo revisor.

---

## 3. O que está coerente

- Lista de pendências, `parameters.json`, `geometry_report.json` e `ACEITACAO.md`
  falam todos de revisão 3.0.3, baia de 29, trilhos em Z = 9, aranha de 71,0 g,
  rotor de 278,6 g e contrapeso repartido.
- A §2.1 da especificação já reescreveu o admissível como "recalcule", em vez de
  só contemplar o afrouxamento.
- A conta de 46 Hz com braço rígido é consistente entre o plano de ensaios e a
  pendência D2.
- O esquema elétrico §8 e a especificação §10 concordam com C9: ESC na parte
  fixa, fonte de bancada em 6–7 V, tabelas de corrente unificadas em 7 V.
- O glossário registra que o BLHeli_S não tem corte por baixa tensão, e C9 se
  apoia nesse registro.

---

## 4. Pontos negativos das três ratificações

### C9 · ESC e alimentação

**Erro factual, corrigido em 03/09.** O texto afirmava que as duas linhas de
energia não se encontram "só o GND, que precisa ser comum". Não existe terra
comum entre rotor e parte fixa: o rotor é eletricamente isolado, não há anel
deslizante nem escova em lugar nenhum do projeto, e o guia de montagem afirma que
nada cruza o entreferro além do campo do ímã. O terra comum exigido é entre
Arduino, ESC e fonte de bancada, como diz o §8.3 do esquema elétrico. A frase foi
removida.

Continuam abertos:

- A citação de "glossário §7" para o corte por baixa tensão. O glossário tem
  cinco seções; o registro está na tabela da §2 e na §3.
- A recomendação de começar em 7,0 V ficou só na lista de pendências. O plano de
  ensaios, no passo 3 do bloqueador A, ainda manda ajustar a fonte para 6–7 V sem
  a ressalva, e é ele que se lê na bancada.
- A saída dos fios de fase. O único lugar que fixa o lado, −x, oposto ao arco do
  suporte do ímã, é a nota do `magnet_bracket` e a própria pendência. O DXF da
  chapa não traz marcação de provisão.

### C2 · Polaridade do ímã

- **Referências quebradas, corrigidas em 03/09.** O guia de montagem mandava
  conferir a polaridade em "C4" e registrava a decisão do sensor nu em "C3", mas
  os códigos certos são C2 e C1. Os códigos da lista foram renumerados sem que as
  referências acompanhassem.
- A decisão continua registrada em vocabulário ambíguo. O campo `magnet.polarity`
  deveria guardar a resposta do ensaio em termos de polo, norte ou sul voltado ao
  sensor, e o ensaio ainda não foi feito.
- O bolso do cubo diz "face sensível para baixo", e só a lista de pendências
  explica que a face sensível é a marcada. O guia de montagem deveria dizer
  "face serigrafada do TO-92 para baixo", porque é ali que o erro acontece.
- O glossário ainda trata a polaridade como "se não pulsar, inverta o ímã", sem
  apontar para o ensaio que resolve antes de colar. As medições de entrada também
  não registram a decisão.

### B'3 · Canal único

- A ratificação está limpa. O que falta é fechar a duplicidade: a tabela de
  fechadas tem B9 e B'3 para o mesmo assunto, com B9 remetendo a B'3. Fundir as
  duas linhas evita que o próximo leitor procure diferença onde não há.
- **Corrigido em 03/09:** a §5.2 da especificação mandava prever assento no
  rebaixo do cubo três linhas antes de dizer que não há rebaixo. Não é B'3, mas é
  a mesma família de desvio ratificado com resíduo no texto.

---

## 5. Números da revisão 3.0.2 ainda publicados

Todas as linhas abaixo foram conferidas por busca e **corrigidas em 03/09/2026**.
A tabela fica como registro do que mudou e de onde procurar se algo reaparecer.

| Arquivo | Dizia | Passou a dizer |
|---|---|---|
| `README.md` | 274,3 g · folga 5,7 g · Ø78 × 26 · 7,4 J | 278,6 g · 1,4 g · Ø78 × 29 · 7,9 J |
| `Hologram_Orbiter_v3_0/README.md` | rev. 3.0.2 · baia 26 · aranha 67,5 · rotor 274,3 · base 321,3 · 2,2 g a 180° · layout "D2" | 3.0.3 · 29 · 71,0 · 278,6 · 319,8 · 2,19 + 0,87 · D1 |
| `01-ESPECIFICACAO` §2.1 | 7,4 J · 173 g de CAD | 7,9 J · 177 g (o §10 já dizia 7,9: a spec se contradizia) |
| `01-ESPECIFICACAO` §5.2, §5.6, §10 | trilhos Z = 6 · baia 26 · "rebaixo do cubo" · 2,2 g a 180° · rotor ~274 g | Z = 9 · 29 · sem rebaixo · repartido · 278,6 g |
| `02-PLANO` riscos | folga 5,7 g | 1,4 g |
| `03-LISTA` | aranha 67,5 g / 65 cm³ · base 321 g · Z = 6 · topo 23 · baia 26 · ~60 min | 71,0 / 68,3 · 320 · 9 · 26 · 29 · ~50 min |
| `04-PLANO-DE-ENSAIOS` | 2,2 g a 180° · 7,4 J · rotor 274 g na conta da torre | repartido · 7,9 J · 279 g (344 → 349 g; fn continua 46 Hz) |
| `05-ESQUEMA` §7 | Z = 6 · Ø78 × 26 · 21 mm úteis · 73 g·mm a 14° · 2,2 g | Z = 9 · 29 · 24 mm · 63 g·mm a 23° · repartido |
| `07-GLOSSARIO` §2, §4 | rotor ~274 g · folga 5,7 · contrapeso 2,2 · "o tubo dá 63 Hz" | 278,6 · 1,4 · 3,1 · ≈ 46 Hz |
| `docs/PENDENCIAS.md` | arquivo inteiro em 3.0.2, duplicando a lista 06 | reduzido a ponteiro para a 06 |
| `docs/FIACAO_E_MONTAGEM.md` | Z = 6 · 6…23 · 26 mm · 73 g·mm · 2,2 g · C3 · C4 | 9 · 9…26 · 29 · 63 · repartido · C1 · C2 |
| `docs/MEDICOES_DE_ENTRADA.md` | trilhos Z = 6 · "folga do rotor (2,5 g)" | Z = 9 · 1,4 g |
| `docs/GUIA_IMPRESSAO.md` | rev. 3.0.2 · "274 g do centro" | 3.0.3 · 279 g |
| `reports/RELATORIO_VALIDACAO.md` | rev. 3.0.2 · aranha 11 230 tri / 64,93 cm³ / envelope Z 32 · CAD 173,5 g · 274,3 · 2,2 g | 3.0.3 · 11 238 / 68,26 / 35 · 176,9 · 278,6 · repartido |
| `06-PENDENCIAS` D1 e D3 | "173 g de CAD" | 177 g |

**Por que importava.** A folga de massa caiu de 5,7 para 1,4 g. Quem lesse apenas
o README ou o plano de projeto acreditaria ter quatro vezes a margem real, e
"nada entra no rotor sem sair outra coisa" é a regra que a pendência D3 criou
justamente por causa disso. E o relatório de validação, que é o documento que
alguém abre para decidir se confia no pacote, descrevia uma malha diferente da
que está no STL.

---

## 6. O que dá para melhorar

### Um lugar só para cada número derivado

A causa raiz é que massa do rotor, altura da baia, folga e contrapeso apareciam à
mão em catorze arquivos. O gerador já calcula todos e escreve
`geometry_report.json`. Dois caminhos baratos:

1. O gerador passa a escrever o bloco "Resultado geométrico" dos dois READMEs e a
   tabela de massas do glossário entre marcadores, e o `build.sh` os substitui.
   Um número derivado nunca mais é digitado.
2. Se não valer gerar prosa, um verificador no `build.sh` que busca os valores
   antigos (274,3; 5,7 g; Z = 6; baia de 26; 2,2 g; 7,4 J; 63 Hz) e falha o build
   enquanto algum sobreviver. É tosco, mas teria pego tudo o que está na §5.

### Wording e referências pequenas

- A pendência D1 e o docstring de `bay_balance()` dizem que cada fonte de
  desbalanceamento "sozinha passa dos 8,4 g·mm". O sensor hall dá 5,8 g·mm e não
  passa; só a aranha e a tampa passam.
- A tabela da §2.1 da especificação publica um único valor de deflexão, 2,48 mm
  com raio dinâmico de 106,5, enquanto a §10.0 e o critério de folga usam a faixa
  de 2,5 a 5,0 e raio 109. A tabela deveria trazer a faixa, ou ao menos o topo
  dela, já que é o topo que governa a folga até o cilindro.
- O relatório de validação é escrito à mão e já ficou para trás duas vezes. Ou
  passa a ser gerado, ou ganha um cabeçalho de revisão que o gerador confere.

---

## 7. O que continua aberto depois desta revisão

| # | Item | Onde |
|---|---|---|
| 1 | Citação de "glossário §7" em C9 | `06-PENDENCIAS-ABERTAS-v3.0.md`, C9 |
| 2 | Ressalva dos 7,0 V ausente no bloqueador A | `04-PLANO-DE-ENSAIOS-v3.0.md` |
| 3 | Ensaio de bancada da polaridade, e o campo `magnet.polarity` em termos de polo | bancada · `CAD/parameters.json` |
| 4 | "Face serigrafada para baixo" no guia de montagem | `docs/FIACAO_E_MONTAGEM.md` |
| 5 | Duplicidade B9 / B'3 na tabela de fechadas | `06-PENDENCIAS-ABERTAS-v3.0.md` |
| 6 | "Cada fonte sozinha passa dos 8,4 g·mm" | `06-PENDENCIAS` D1 · `CAD/generate.py` |
| 7 | Deflexão única na tabela da §2.1 contra a faixa da §10.0 | `01-ESPECIFICACAO-CAD-v3.0.md` |
| 8 | Nota "baia de 26" no `ACEITACAO.md` | sai numa regeneração do pacote |
| 9 | Fonte única para os números derivados | `CAD/generate.py` · `scripts/build.sh` |
