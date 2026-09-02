# Auditoria técnica e integração — Hologram Orbiter v2.1

Documento único de consolidação do pacote v2.1: os cinco documentos soltos
(escritos à mão), a pasta `Hologram_Orbiter_v2_1/` (gerada por IA) e o modelo
CAD paramétrico. Todos os números abaixo foram recalculados de forma
independente a partir dos parâmetros e dos STL, não copiados dos documentos.

**Data da auditoria:** 01/09/2026
**Escopo:** 5 documentos raiz + 12 arquivos da pasta gerada + 11 STL + `generate.py` (1098 linhas)
**Método:** releitura cruzada; recálculo simbólico; leitor de STL binário próprio
(topologia, volume orientado, componentes conexos); inspeção do gerador linha a linha.

---

## 0. Veredito

> ### ⬛ Estado em 01/09/2026 — decisão tomada
>
> **Ponto de operação congelado: raio de 100 mm @ 1800 RPM = 90 Hz.**
> O CAD v3.0 será modelado a partir de
> [`01-ESPECIFICACAO-CAD-v3.0.md`](01-ESPECIFICACAO-CAD-v3.0.md), que é uma
> especificação de construção autossuficiente — escrita do zero, sem referência
> a esta versão. Esta auditoria passa a ser o **registro histórico**
> do que estava errado na v2.1 e a memória de cálculo que sustenta a decisão.
>
> A v2.1 queria 90 Hz e tentou consegui-los subindo a rotação com o raio fixo em
> 130 mm. Como a potência aerodinâmica escala com **ω³r³**, esse é o caminho
> caro: exigia 9,76 A e levava o motor a 101 °C. Os mesmos 90 Hz, na **mesma**
> 1800 RPM, com o raio em 100 mm, custam **4,44 A e 43 °C**. O alvo estava
> certo; a alavanca estava errada.
>
> Situação dos 24 achados: **12 resolvidos**, 12 abertos. Detalhe em §2.0.



O pacote **não está pronto para fabricar o rotor nem para operar a 1800 RPM**, e
a decisão que dá nome à versão ("subir de 1200 para 1800 RPM porque a margem
térmica aguenta") **não se sustenta com os próprios números publicados**.

Três blocos independentes de problema:

1. **Aritmética.** A força centrífuga publicada está errada por 2× (Plano) e por
   71× (README). O caso térmico, refeito com os dados do próprio README, dá
   ~64 °C e reprova o bloqueador de 55 °C.
2. **CAD.** A geometria é boa e as malhas são limpas, mas há um defeito de
   fabricação real (membrana de 0,20 mm sob o canal do LED), um bug de montagem
   (os três painéis sobrepostos), e o isolador de vibração é ~500× rígido demais
   para a função declarada.
3. **Integração.** Não existe nenhuma especificação elétrica no projeto — nem
   tensão, nem motor, nem ESC, nem caminho de sinal para o rotor. Os critérios
   de aceite em ampere são, hoje, inverificáveis.

**Atualização de 01/09/2026 (informação da equipe):**

- A `TABELA-COMPARATIVA` **não existe** — confirmado. A memória de cálculo do
  projeto está perdida em definitivo. Consequência séria: o limite de 5,8 A, que
  é critério de aceite de um bloqueador e do gate G0, ficou **sem derivação** e
  precisa ser re-derivado (§3.3).
- O cilindro de contenção **já existe fisicamente**, possivelmente em
  policarbonato. Isso não fecha F-06 — inverte a direção da correção: a guarda
  vira restrição fixa e quem se ajusta é o rotor, baixando o datum (§3.1). O
  material continua a exigir ensaio, porque toda a documentação do projeto,
  inclusive o BOM, diz "acrílico" (§3.2).

**Ranking de confiabilidade do material existente:**

| Fonte | Confiabilidade | Comentário |
|---|---|---|
| `Hologram_Orbiter_v2_1/` (IA) | **alta** | Reprova o próprio pacote e acerta os erros que checa. Confirmei cada um. |
| `Especificacao-CAD-v2.1.md` | média | Coerente; falta cota radial e specs elétricas. |
| `Plano-de-Projeto-v2.1.md` | média | Estrutura boa; §2.3 tem erro de 2× na força. |
| `Revisao-Tecnica-e-Ajustes.md` | média | Método de bloqueadores é sólido; sem memória de cálculo. |
| `GUIA-Impressao-Coxim-TPU-v2.1.md` | **baixa** | Teste de ζ errado por 3×, massa errada por 10×, erros factuais de impressão. |
| `README-v2.1.md` | **baixa** | Tabela-resumo com vários números errados; referencia 8 arquivos inexistentes. |

---

## 1. Mapa da documentação

### 1.1 O que existe

```
OficinaDeIntegracao/
├── README-v2.1.md                        índice/resumo executivo   [P2: números errados]
├── Plano-de-Projeto-v2.1.md              plano de fases            [P0: F-01]
├── Especificacao-CAD-v2.1.md             10 peças + tolerâncias    [fonte de requisitos do CAD]
├── Revisao-Tecnica-e-Ajustes.md          4 bloqueadores + testes   [método OK]
├── GUIA-Impressao-Coxim-TPU-v2.1.md      procedimento TPU          [P1: F-08, F-09, F-20]
└── Hologram_Orbiter_v2_1/                pacote CAD (gerado por IA)
    ├── CAD/parameters.json               FONTE DE VERDADE dimensional
    ├── CAD/generate.py                   gerador Blender           [P0: F-05]
    ├── exports/stl/  (11 arquivos)       malhas limpas             [P0: F-04 no painel]
    ├── exports/fonte/*.blend             montagem                  [inválida: F-05]
    ├── exports/preview/montagem.png      render                    [inválido: F-05]
    ├── docs/PENDENCIAS_CRITICAS.md       autocrítica correta
    ├── docs/MEDICOES_DE_ENTRADA.md       folha de medição em branco
    ├── docs/GUIA_IMPRESSAO.md            perfis de fatiamento
    └── reports/                          validação de malha + geometria
```

### 1.2 O que falta (referenciado mas inexistente) — F-14

`SUMARIO-v2.1.md` · `TABELA-COMPARATIVA-v2-v2.1.md` · `CHECKLIST-IMPLEMENTACAO-v2.1.md`
· `Plano-de-Projeto-v2.md` · `Especificacao-CAD.md` ·
`Fundamentacao-Teorica-Hologram-Orbiter.md` · `Revisao-Tecnica-e-Ajustes-NOVO.md`

Consequência prática: o README manda buscar **a memória de cálculo** na
`TABELA-COMPARATIVA-v2-v2.1.md`. É por isso que os números 2,26 N, 21,3 J, 147×
e 53,4 °C não têm como ser auditados — a planilha que os gerou não está aqui.
Ou ela aparece, ou esses números devem ser tratados como não existentes.

O README ainda afirma `[x] Todos os 6 documentos v2.1 criados e revisados`.
Três dos seis não estão no diretório.

### 1.3 Hierarquia de autoridade (proposta, para acabar com os conflitos)

1. `CAD/parameters.json` — manda em **toda** cota. O STL nunca é editado à mão.
2. `Especificacao-CAD-v2.1.md` — manda em requisito funcional e tolerância de aceite.
3. `Revisao-Tecnica-e-Ajustes.md` — manda em critério de bloqueador e fallback.
4. `Plano-de-Projeto-v2.1.md` — manda em fase e cronograma.
5. Este documento — manda em **número físico** até que a memória de cálculo reapareça.
6. `README-v2.1.md` — apenas índice. **Nenhum número dele é normativo.**

---

## 2. Flags

Severidade: **P0** impede imprimir ou operar · **P1** impede liberar, corrigível
em documento/parâmetro · **P2** inconsistência documental.

### 2.0 Situação dos achados após a decisão v3.0

| | Achado | Situação |
|---|---|---|
| F-01 | Força centrífuga errada | ✅ **resolvido** — 131,7 N em r=100; números antigos aposentados |
| F-02 | Caso térmico reprova | ✅ **resolvido pelo projeto** — 43 °C em r=100 (condicionado a §7.2 do briefing) |
| F-03 | Sem especificação elétrica | ✅ **resolvido** — A2212 920KV, ESC 15 A, fonte de bancada, 2S para os LEDs |
| F-04 | Membrana de 0,20 mm no canal | ✅ **resolvido pela medição** — fita 12 × 1 → canal 12,4 × 1,2 → piso 0,8 mm |
| F-05 | Painéis sobrepostos na montagem | ✅ **corrigido** em `generate.py` |
| F-06 | Contenção | 🟡 **parcial** — folga radial resolvida (9,5 → 39,4 mm); altura e material seguem abertos |
| F-07 | Coxim não isola | 🔴 **aberto** — decisão pendente entre montagem rígida e redimensionamento |
| F-08 | Ensaio de ζ errado por 3× | 🔴 **aberto** — correção documental |
| F-09 | Massa do coxim 10× | 🔴 **aberto** — correção documental |
| F-10 | Orçamento de massa | ✅ **resolvido** — 251 g reais; limite passa de 120 para 260 g |
| F-11 | Sem Δm casada | ✅ **resolvido** — Δm ≤ 0,084 g |
| F-12 | Tolerância radial não controlada | ✅ **resolvido** — nova cota 100 ±0,1 mm |
| F-13 | Arrasto do boss ignorado | ✅ **resolvido** — carenagem virou requisito; era 54% do arrasto |
| F-14…F-20 | Documentais | 🔴 **abertos** |
| **F-21** | **Furação do motor errada** | 🔴 **novo, P0** — ver abaixo |
| **F-22** | **Fixação do rotor é eixo M6** | 🔴 **novo, P0** — ver abaixo |
| **F-23** | **Rampa de partida impossível** | 🔴 **novo, P1** — ver abaixo |
| **F-24** | **Refrigeração virou o gargalo** | 🔴 **novo, P0** — ver abaixo |

### Achados novos (do datasheet e das medições)

#### F-21 — O padrão de furação do motor está errado no CAD · P0

O datasheet do A2212 920KV mostra `4-M3` num **retângulo de 16 × 19 mm**.
O `parameters.json` assume `motor_base_mount: pcd 19.0` — um **círculo de Ø19**.
São posições completamente diferentes: a chapa de alumínio da v2.1 não parafusa
neste motor. O mesmo vale para `motor_bell_mount`.

#### F-22 — A fixação do rotor não é por parafusos na campânula · P0

O datasheet mostra **eixo M6 com saliência de 14 mm** (≈5 mm de Ø8 liso + 7 mm
de rosca) e **porca cônica** de sextavado 12 mm. O CAD prevê 4 furos em PCD 19
mais clareira central Ø12. O cubo precisa virar **furo Ø8 H8 com aperto axial**.

Consequência: o torque passa a ser transmitido **só por atrito** contra a face
da campânula. O atrito sobra (≈4,5 N·m contra os 0,16 N·m necessários), mas ABS
flui sob aperto sustentado — exige arruela ou bucha metálica. E a cota não fecha:
7 mm de rosca contra cubo de 6 mm deixam ~1 mm de engate; o cubo precisa de
rebaixo.

#### F-23 — A rampa de partida de 2–3 s é impossível · P1

O rotor tem 1,327 g·m² — **135× a inércia de uma hélice 1045**, para a qual os
ESCs sensorless são sintonizados.

| Rampa | Corrente de pico |
|---:|---:|
| 3 s | 14,4 A |
| 5 s | 9,3 A |
| **8 s** | **7,5 A** |
| 12 s | 6,5 A |

O README manda 2–3 s. O correto é **≥ 8 s**, e ainda há risco real de
dessincronização na partida sensorless com essa inércia.

#### F-24 — A refrigeração do motor virou o item que decide · P0

Com o ponto de operação novo, o motor fica a 43 °C no caso central. No pior caso
de arrasto vai a **68 °C com Rth = 3,5 °C/W e a 99 °C com Rth = 6,0**. A
diferença entre passar e reprovar é **só ventilação**.

Isso promove a lacuna 05 (os 4 vents Ø10 atravessam a face que apoia na mesa e
ficam vedados) de nota de rodapé a **bloqueador**. Alvo: Rth ≤ 3,5 °C/W.

### P0

#### F-01 — Força centrífuga errada em dois documentos

| Fonte | Valor publicado | Erro |
|---|---:|---|
| `Plano-de-Projeto-v2.1.md` §2.3 | ~80 N/painel | 2,0× baixo |
| `README-v2.1.md` (2 tabelas) | 2,26 N/painel | 71× baixo |
| **Correto** | **161,7 N/painel** | — |

```
ω = 1800 · 2π/60 = 188,50 rad/s
F = m·ω²·r = 0,035 · 188,50² · 0,130 = 161,7 N   (471 g de aceleração)
3 painéis: 485 N
```

Todo fator de segurança publicado ("333× em v2.0", "147× em v2.1") deriva do
valor errado e é inválido. Note que o README se contradiz sozinho: publica
2,26 N **e** 3,5 mm de deflexão do painel na mesma tabela — 2,26 N produziriam
~0,05 mm. Os 3,5 mm só fecham com ~160 N.

A pasta gerada por IA já apontou isto (`docs/PENDENCIAS_CRITICAS.md`, "≈162 N").
Confirmado.

#### F-02 — O caso térmico que justifica a v2.1 reprova no papel

O README publica: 1200 RPM → 52 °C @ 4,6 A; 1800 RPM → 53,4 °C @ 5,5 A ("+1,8 °C").

Perda no cobre ∝ I². Com ambiente 25 °C:

```
ΔT(1200) = 52 − 25 = 27 °C
ΔT(1800) = 27 · (5,5/4,6)² = 38,6 °C
T(1800)  ≈ 63,6 °C
```

Isso **reprova o bloqueador B (< 55 °C)** e passa do limite de projeto de 60 °C —
antes de qualquer ensaio. A frase "margem térmica reduzida, mas ok" do README
não se sustenta com os dados do próprio README.

Agravante: a potência aerodinâmica escala com ω³, então 1200 → 1800 RPM
multiplica o arrasto por **3,375**. Um aumento de corrente de apenas +20% só
seria possível se as perdas fixas do motor dominassem completamente — o que
contradiz a narrativa térmica do mesmo documento.

**Ação:** o gate térmico precisa de um modelo explícito (Rth do motor, ambiente,
regime de ar) ou o ensaio de termopar vira o único critério — e nesse caso o
1800 RPM entra como hipótese a testar, não como decisão aprovada.

#### F-03 — Não existe especificação elétrica nenhuma no projeto

Busca em todos os documentos: **zero** ocorrências de tensão de barramento,
modelo de motor, kv, resistência, modelo de ESC, capacidade de bateria ou
orçamento de potência. O único identificador de motor ("2212") aparece somente
em `CAD/parameters.json` e está marcado `verified: false`.

Consequência: o critério de aceite do bloqueador A e do gate G0 é
"I ≤ 5,8 A" — e 5,5 A em 2S (7,4 V) são 41 W, enquanto 5,5 A em 3S (11,1 V) são
61 W. São conclusões opostas sobre o mesmo número.

**Ação:** antes de qualquer CFD, fixar motor (modelo/kv/Rm/Kt), fonte (S, mAh),
ESC (modelo, rampa) e reescrever o critério em **torque e potência**, com a
corrente como consequência.

#### F-04 — Membrana de 0,20 mm sob o canal do LED (defeito de fabricação)

Verificado direto no STL do painel: existem níveis em Z = 1,800 (teto do canal)
e Z = 2,000 (piso da cavidade interna).

```
parede da lâmina:  x = 2,0 → 4,0   (2,0 mm)
canal do LED:      cortado até x = 2,2
piso remanescente: 0,20 mm × 13 mm × 206 mm
```

Com bico 0,4 mm e camada 0,20 mm isso é **uma única camada**, em ponte de 13 mm,
e é exatamente a superfície onde a fita HD107S se apoia. Ou cede em serviço, ou
o fatiador a descarta e abre o canal para dentro do painel. Também derruba ~20%
da inércia de flexão da lâmina (I: 1141 → 910 mm⁴).

**Correção:** engrossar a parede local ou reduzir `led_channel_depth`. Mínimo de
3 camadas (0,6 mm) no piso, preferível 1,2 mm. Regenerar o STL — não editar a malha.

#### F-05 — Os três painéis estão sobrepostos na montagem (bug de código)

`CAD/generate.py`, `assemble_and_save()`:

```python
panel.location = (130.0, 0.0, rotor_z + 3.0)
panel.rotation_euler[2] = math.radians(i * 120.0)
```

No Blender a rotação é aplicada em torno da origem do objeto e **depois** a
translação. Os três painéis giram sobre si mesmos e vão todos parar em
(130, 0, z). Confirmado no render `exports/preview/montagem.png`: só um painel
aparece.

Efeito: o `.blend` entregue como "montagem editável" **não representa o rotor** e
não serve para checagem de interferência ou de balanceamento visual.
(As longarinas estão certas — usam `rotate_about_z`, que aplica a transformação
na malha.)

**Correção aplicada** neste repositório (`generate.py`); a regeneração exige
Blender 5.x, que não está instalado nesta máquina.

#### F-06 — Contenção: o invólucro existe, então o rotor é que precisa ceder

**Atualização (01/09):** a equipe informa que o cilindro **já existe fisicamente**
e acredita que seja policarbonato. Isso muda a natureza do problema: a guarda
deixa de ser variável de projeto e vira **restrição fixa**. Ver §3.1.

- **Altura:** o rotor ocupa Z = 87…295 mm; uma guarda de 260 mm a partir do solo
  termina 35 mm antes. Com o cilindro já comprado, a correção **não** é comprar
  outro — é **baixar o datum do rotor**, que é uma mudança de um parâmetro na
  torre. Ver a janela de datum em §3.1.
- **Material — a ser confirmado, não presumido:** um painel solto carrega
  **10,5 J a 24,5 m/s** (13,5 J se o painel sair em 45 g); o rotor inteiro guarda
  ~36 J. Acrílico (PMMA) 4 mm é frágil e estilhaça; policarbonato 4 mm deforma e
  retém. **Toda a documentação do projeto diz "acrílico"** — Especificação Peça 9,
  o BOM (`Acrílico 4 mm`) e o próprio nome do parâmetro
  `reference_parts.acrylic_guard_*`. Tubo de acrílico é o produto barato e padrão
  do mercado; tubo de policarbonato é item de especialidade e custa 2–4× mais.
  A crença de que seja PC contradiz o BOM do próprio projeto, então **exige
  ensaio**, não memória. Procedimento em §3.2.
- **Conflito geométrico:** `containment_ring` (Ø280 int./Ø300 ext.) e
  `acrylic_guard` (Ø292 int./Ø300 ext.) disputam o mesmo anel da base
  (r = 140…150 mm). Os dois não cabem — e agora o diâmetro real do cilindro é
  que manda nos dois.

### P1

#### F-07 — Os coxins Ø16×8 em TPU 95A não isolam nada a 30 Hz

Disco Ø16 × 8 mm com furo Ø3,2; área útil 193 mm²; fator de forma S = 0,50;
E(TPU 95A) ≈ 15–35 MPa; Ec = E(1 + 2S²).

| | valor |
|---|---:|
| Rigidez por coxim | 540 – 1270 kN/m |
| fn com 4 coxins e ~0,33 kg | **400 – 620 Hz** |
| Deflexão estática | ~0,001 mm |
| fn necessária para isolar 30 Hz | ≤ 21 Hz |
| Rigidez necessária por coxim | **~1,4 kN/m** (400–900× mais mole) |
| Deflexão estática necessária | ~0,6 mm |

O coxim especificado é um **espaçador rígido**, não um isolador. Isso torna o
bloqueador C mal formulado: ζ ≥ 0,08 mede a propriedade certa na peça errada —
o amortecimento é irrelevante quando a frequência natural está 20× acima da
excitação.

**Decidir:** (a) assumir montagem rígida, remover o bloqueador C e tratar
vibração só por balanceamento; ou (b) redimensionar o isolador (mais alto, mais
mole, menor área, ou coxim comercial de silicone) e reescrever o critério em
**fn**, não em ζ.

Nem os documentos manuais nem a pasta gerada apanharam isto.

#### F-08 — O teste de ζ do guia TPU aprova coxins com 1/3 do amortecimento

`GUIA-Impressao-Coxim-TPU-v2.1.md` §6.2, Teste 4:
*"Se N = 3 ciclos → ζ ≈ 0,11 ✅ / Se N > 5 ciclos → ζ < 0,08 ❌"*

Decremento logarítmico, δ = ln(2)/N, ζ = δ/√(4π² + δ²):

| Ciclos até 50% da amplitude | ζ real | Guia afirma |
|---:|---:|---|
| 1 | 0,110 | — |
| **1,38** | **0,080** | ← este é o critério correto |
| 2 | 0,055 | — |
| 3 | 0,037 | "≈ 0,11 ✅" |
| 5 | 0,022 | "< 0,08 ❌" |

O critério correto para ζ ≥ 0,08 é **cair a 50% em ≤ 1,4 ciclo**. Como está, o
procedimento aprova lotes com um terço do amortecimento exigido.

Também: a massa de ensaio de 200 g não representa a massa realmente suspensa
(~330–600 g), o que muda fn e a leitura; e "pressão manual de ~2 N" é pequena
demais para medir deformação permanente num disco de Ø16.

#### F-09 — Massa do coxim publicada 10× maior

```
V = π·8²·8 − π·1,6²·8 = 1,544 cm³ → 1,85 g em TPU 1,20 g/cm³
```

O guia manda rejeitar o lote fora de "18–22 g" — ou seja, **rejeita qualquer
coxim correto**. (Já apontado pela pasta IA; confirmado, inclusive contra o
volume real do STL: 1,5417 cm³.)

#### F-10 — Orçamento de massa não fecha e ignora o que gira de verdade

| | massa |
|---|---:|
| Aranha (CAD, densidade maciça) | 57,6 g |
| 3 painéis nus | 80,7 g |
| Tampa | 7,6 g |
| **Subtotal impresso** | **145,8 g** |
| Limite publicado | 120 g |

E o rotor real ainda carrega: LiPo 2S (envelope Ø62 × 18 mm previsto na baia:
40–80 g), 3 fitas HD107S, eletrônica de bordo, parafusos/porcas e contrapesos.
Realista: **250–350 g**. Nenhum documento tem esse orçamento — e ele é entrada
de F-01 (força), F-06 (energia de contenção) e F-07 (isolamento).

#### F-11 — Falta tolerância de massa *casada* entre os painéis

Todos os documentos dizem "≤ 35 g". Nenhum diz "Δm entre painéis ≤ X".

Para grau **G6.3** a 30 rps num rotor de 330 g, o desbalanceamento admissível é
**11 g·mm**:

| Δm entre painéis | Desbalanceamento (r=130) | Força rotativa a 30 Hz |
|---:|---:|---:|
| 0,1 g | 13 g·mm | 0,46 N |
| 0,5 g | 65 g·mm (6× o limite) | 2,3 N |
| 1,0 g | 130 g·mm (12×) | 4,6 N |

Ou se casa a massa em ±0,1 g, ou o balanceamento por contrapesos precisa de
resolução equivalente. Especificar explicitamente.

#### F-12 — A tolerância radial não é controlada, e pesa tanto quanto o Δh

O projeto inteiro se organiza em torno de Datum D (±0,2 mm) e Δh (±0,5 mm), que
são **verticais**. Mas a junta tem, **por projeto**, `joint_bottom_clearance`
= 0,5 mm, e o furo Ø3,2 para parafuso M3 dá mais 0,2 mm de folga.

Ou seja: o raio de assentamento de cada painel tem ~±0,35 mm de folga não
especificada. Os três painéis podem escrever em cilindros de raios diferentes —
o que borra a imagem exatamente como o Δh que o projeto controla a ±0,2 mm.

**Falta a cota:** "raio do plano médio do painel = 130 ±0,1 mm", ou um batente
radial na junta que force o assentamento.

#### F-13 — O arrasto do boss não foi contabilizado e provavelmente iguala o da lâmina

A lâmina é aerodinâmica (bordo de ataque R4, fuga afilada a 2 mm) — bom projeto.
Mas o boss é um corpo rombudo exposto: 2 torres Ø8 × 36 mm + luva 24 × 10,2 mm +
2 gussets ≈ 1000 mm² de área frontal por painel, a 21,7 m/s.

| Fonte | Potência a 1800 RPM (3 painéis) |
|---|---:|
| Lâmina (Cd 0,25 – 0,8) | 11 – 35 W |
| **Boss / torres / gussets (Cd ≈ 1,0)** | **~18 W** |

Um CFD que modele só a lâmina subestima o arrasto pela metade. O domínio precisa
incluir boss, longarina e o efeito de ar confinado dentro do cilindro.

### P2 — documental

| ID | Problema |
|---|---|
| **F-14** | 8 arquivos referenciados não existem (§1.2). O README declara "6 de 6 documentos criados"; 3 faltam. **Confirmado em 01/09: a `TABELA-COMPARATIVA` não existe em lugar nenhum.** A memória de cálculo do projeto está perdida — ver §3.3, números aposentados. |
| **F-15** | Tamanhos de arquivo do README errados: Revisão "15 KB" (real 7,4), Plano "19 KB" (real 10,5), Especificação "14 KB" (real 8,8). O README descreve outro conjunto. |
| **F-16** | Datum D: ±0,2 mm (Especificação, Plano, Revisão, e o próprio cronograma da Semana 1 do README) vs ±0,3 mm (tabela do README e `docs/GUIA_IMPRESSAO.md`). O README se contradiz internamente. |
| **F-17** | Referências cruzadas erradas: README manda a "§2.2 do Plano" para flicker (é §2.1) e "§2.3" para térmica (é §2.5); o guia do coxim aponta "Especificação §7, Peça 8" (o coxim é a Peça 7, §2); o Plano termina com a linha órfã `Arquivo: Revisao-Tecnica-e-Ajustes-NOVO.md`. |
| **F-18** | Cronograma incoerente: README diz "6–8 → 7–9 semanas", mas os dois cronogramas detalhados cobrem 4 semanas, e alocam a montagem em semanas diferentes. |
| **F-19** | Limiar de fusão mal citado: Plano §2.1 usa "~40 ms" (= 25 Hz). A frequência crítica de fusão real depende de luminância e excentricidade (Ferry–Porter) e passa de 60–90 Hz em campo claro e visão periférica; sob sacada (*phantom array*) a detecção vai a centenas de Hz. 90 Hz melhora muito sobre 60 Hz, mas "flicker eliminado ✓" é forte demais — e é justamente por isso que o bloqueador D existe. Trocar por "reduz substancialmente; a validar empiricamente". |
| **F-20** | Erros factuais no guia do TPU: lista CR-10S Pro, Prusa MK3S+ e Ultimaker S5 como "câmara fechada" (nenhuma é, de fábrica) enquanto desqualifica a Ender 3 pelo mesmo motivo; TPU **não** precisa de câmara aquecida (o §3.1 "CRÍTICO" é requisito de ABS); hotend *hardened* é desnecessário (TPU não é abrasivo); "graxa de silicone na entrada do hotend" não é prática recomendada; §4.1 diz "deitado (Z = 8 mm)" **e** "eixo perpendicular à mesa" — contraditório, e a orientação decide se o coxim comprime ao longo ou através das camadas; tempo de impressão 30–45 min (§4.3) vs 40 min (§5.2) vs 3 h (§9); "dureza baixa = câmara quente demais" — a dureza Shore do TPU não é função da temperatura de câmara. |

---

## 3. Adequação ao invólucro existente e números aposentados

*Seção acrescentada em 01/09/2026, após a equipe informar que (a) o cilindro de
contenção já existe fisicamente e (b) a `TABELA-COMPARATIVA` não existe.*

### 3.1 A guarda virou restrição fixa: baixar o rotor

Com o cilindro já comprado, a altura dele deixa de ser variável. A geometria do
painel trava as duas cotas que importam:

```
topo do rotor = datum + 107 mm      (painel centrado em datum+3, meia-altura 104)
base do rotor = datum − 101 mm
datum         = altura_da_torre + 38 mm    (piso 4 + torre + 34 do conjunto motor)
```

Impondo 10 mm de folga no topo e 15 mm sobre as nervuras da base (z = 8 mm), a
janela admissível do datum é:

| Guarda | Apoio | Datum mín. | Datum máx. | Torre máx. | Situação vs. projeto atual (datum 188 / torre 150) |
|---:|---:|---:|---:|---:|---|
| 240 mm | solo | 124 | **123** | 85 | **impossível** — a janela fecha |
| 240 mm | z=8 | 124 | 131 | 93 | baixar 57 mm |
| **260 mm** | **solo** | 124 | **143** | **105** | **baixar 45 mm** |
| 260 mm | z=8 | 124 | 151 | 113 | baixar 37 mm |
| 280 mm | solo | 124 | 163 | 125 | baixar 25 mm |
| 300 mm | z=8 | 124 | 191 | 153 | cabe sem mudar nada |
| 305 mm | solo | 124 | 188 | 150 | cabe, no limite exato |

Se o cilindro for mesmo de 260 mm apoiado no solo, o alvo é
**datum = 140 mm → `tower_total_height_from_floor` = 102 mm** (hoje 150). Se o
coxim de 8 mm entrar no caminho de carga (lacuna 08), passa a 94 mm.

Isso **é uma melhora**, não um remendo: torre 32 % mais curta é mais rígida em
flexão, o centro de massa desce, e o balanço sobre o mancal diminui. O único
custo é estético — a imagem passa a ocupar Z = 39…243 mm em vez de 87…295, ou
seja, fica mais perto da base. E o custo prático é zero **se a base/torre ainda
não tiver sido impressa**: é a alteração de um número em `parameters.json` antes
do maior print do projeto (154 mm de altura, ~306 g).

**Folga radial** — depende do diâmetro interno real. Raio estático do rotor
134 mm, deflexão prevista 2,5–5,4 mm (§6.3):

| Ø interno | Folga estática | Após 2,5 mm | Após 5,4 mm |
|---:|---:|---:|---:|
| 280 mm | 6,0 mm | 3,5 mm | **0,6 mm** |
| 290 mm | 11,0 mm | 8,5 mm | 5,6 mm |
| 292 mm | 12,0 mm | 9,5 mm | 6,6 mm |
| 300 mm | 16,0 mm | 13,5 mm | 10,6 mm |
| 310 mm | 21,0 mm | 18,5 mm | 15,6 mm |

Mínimo saudável: **≥ 10 mm depois da deflexão máxima**, para ainda absorver
tolerância de impressão, empeno, batimento e erro de montagem. Ou seja, o
cilindro precisa de **Ø interno ≥ 300 mm** — ou o raio do rotor precisa cair.

### 3.2 Folha de medição do invólucro

Antes de qualquer decisão de datum, medir a peça que existe:

| Item | Medida | Por quê |
|---|---|---|
| Altura total | mm | Entra direto na tabela de §3.1 |
| Ø interno | mm | Folga radial; manda no conflito com o anel (F-06) |
| Ø externo / parede | mm | Confirma os 4 mm assumidos |
| Como apoia na base | z₀ = 0 ou 8 mm | Muda a janela de datum em 8 mm |
| Planeza da borda de apoio | mm | Assento sem tensão no anel |
| Tem fundo/tampa? | sim/não | Contenção axial: o painel também pode subir |

**Identificação do material** (fazer numa sobra, nunca na peça inteira):

1. **Ensaio de dobra — o mais decisivo.** Segure uma tira de sobra e force.
   PMMA trinca cedo, com fratura limpa e estalo seco. PC dobra muito além do
   escoamento, embranquece na dobra e **não quebra**. Se dobrar 90° sem partir,
   é PC.
2. **Borda cortada.** PMMA tem aresta azulada, "água clara". PC em seção grossa
   tem leve tom amarelo/âmbar.
3. **Risco.** PMMA é mais duro; PC sem coating risca com facilidade.
4. **Chama, em local ventilado, numa lasca.** PMMA queima limpo, com chama
   crepitante e cheiro adocicado/frutado (monômero). PC solta fumaça preta e
   fuliginosa e tende a se autoextinguir.
5. **Procedência.** Nota fiscal ou o próprio fornecedor resolve em um minuto.
   Se foi vendido como "tubo de acrílico", é PMMA — que é exatamente o que a
   Especificação Peça 9 e o BOM deste projeto pedem.

**Se der PMMA:** não use como contenção de ensaio. Ele serve como *invólucro
óptico* (é opticamente melhor que PC, inclusive), com uma contenção real por
fora ou ao redor durante os ensaios de rotação — chapa metálica, tela de aço,
ou simplesmente ensaiar o rotor dentro de uma caixa fechada com operação remota.

### 3.3 Números aposentados

A `TABELA-COMPARATIVA-v2-v2.1.md` não existe e não será recuperada. Ela era a
única memória de cálculo citada pelo projeto. Os valores abaixo **não têm origem
auditável** e devem ser retirados de circulação — não porque estejam
necessariamente errados, mas porque ninguém consegue mais dizer de onde vieram:

| Número aposentado | Onde aparece | Substituto |
|---|---|---|
| 2,26 N e 1,0 N / painel | README | **161,7 N** (§6.2) |
| 80 N / painel | Plano §2.3 | **161,7 N** (§6.2) |
| 21,3 J de energia de partida | README | **≈36 J** de energia armazenada (§6.4) |
| 147× e 333× de fator de segurança | README | **≈2,5** na flexão do painel (§6.3) |
| 52 °C @ 4,6 A e 53,4 °C @ 5,5 A | README | **sem substituto** — ver abaixo |
| 4,6 A → 5,5 A (+20 %) | README | **sem substituto** — ver abaixo |
| **I ≤ 5,8 A** (critério do bloqueador A) | Revisão §1.1, Plano §2.4, §5 | **precisa ser re-derivado** |

O item mais sério é o último. **O limite de 5,8 A era o critério de aceite de um
bloqueador e do gate G0, e agora não tem derivação nenhuma.** Ele não pode ser
mantido por inércia. Re-derivar assim, depois de fechar F-03:

1. `I_limite` = o **menor** entre a corrente contínua do motor, a do ESC e a
   que a bateria entrega no C declarado — todos valores de catálogo, não de
   estimativa.
2. O critério térmico passa a ser **medido**, não calculado: o termopar já está
   previsto e é a única evidência que sobrou. A corrente vira **limiar de aborto
   em tempo real**, não critério de aprovação.
3. O CFD deixa de ter alvo em ampere e passa a ter alvo em **torque resistivo**,
   que é o que ele de fato calcula — e aí a conversão para corrente usa o Kt do
   motor real.

Isso, na prática, **transforma o bloqueador A de "calculado" em "medido"** — o
que é mais defensável do que era antes, e não depende de nenhum arquivo perdido.

---

## 4. O que está correto (não é só flag)

- **Malhas.** Verifiquei os 11 STL de forma independente, com leitor binário
  próprio: todos *watertight*, zero arestas não-manifold, zero triângulos
  degenerados, volume orientado positivo, base normalizada em Z = 0, escala em
  mm. Os "7 componentes conexos" do painel são **1 casca + 6 cavidades internas
  seladas** — topologia correta de peça oca, não defeito.
- **Junta espiga/socket.** Espiga 11,0 × 6,0 × 22,2 contra socket
  11,2 × 6,2 × 22,7: 0,1 mm por lado e 0,5 mm de fundo, exatamente o que
  `parameters.json` declara. Dimensionalmente consistente.
- **Perfis aerodinâmicos coerentes.** Lâmina com bordo de ataque R4 e fuga
  afilada; longarina com espessura máxima a ~33% da corda. Ambos apontam para o
  mesmo sentido de giro. Bem feito.
- **Resultante centrífuga alinhada com a junta.** O CG do painel em Z coincide
  com o centro da espiga — a junta recebe força pura, sem momento parasita.
  Detalhe bem resolvido.
- **Cupons de calibração** (junta e canal) antes do lote grande: prática correta
  e barata.
- **A pasta gerada por IA não maquiou nada.** Ela mesma reprova o pacote
  (`PROVISÓRIO — NÃO LIBERADO PARA GIRO A 1800 RPM`) e já tinha apanhado os
  162 N, os 35 mm de contenção, a massa do coxim e o orçamento de massa.
  Recalculei todos por conta própria: **estão certos**. É o material mais
  confiável do conjunto, e é o que deve virar a linha de base.

---

## 5. Lacunas de integração (nenhum documento cobre)

1. **Cadeia elétrica e de sinal.** Como a imagem chega ao rotor? A baia de
   eletrônica no cubo sugere bateria + eletrônica embarcadas, mas isso não está
   escrito. Não há slip ring, não há rádio, e **não há sensor de índice/hall no
   CAD da base** — sem referência angular não existe imagem estável.
2. **Roteamento de fios no rotor.** As longarinas são maciças e aerodinâmicas,
   sem canal. Os fios da baia até os 3 painéis teriam de ser colados por fora,
   adicionando arrasto e desbalanceamento assimétrico.
3. **Resolução da imagem.** 30 px verticais (206 mm a 144 LED/m) × N colunas.
   Nenhum documento define N, taxa de dados nem orçamento de energia: 90 LEDs
   HD107S em branco pleno ≈ 25–27 W, saindo da bateria que gira junto.
4. **Sentido de rotação.** Está determinado pelo CAD (**anti-horário visto de
   cima** — bordo de ataque em +y na lâmina e na longarina), mas não está escrito
   em lugar nenhum. Se o ESC girar ao contrário, o arrasto sobe muito.
5. **Ventilação da base bloqueada.** Os 4 furos Ø10 (`vent_hole_pcd` 76)
   atravessam o piso da baia em Z = 0…4 mm — a face que apoia na mesa. Com a base
   assentada, estão vedados. Precisam sair pela lateral, ou a base precisa de pés.
6. **Teia de 0,72 mm no cubo.** Entre o furo do parafuso da campânula (PCD 19,
   Ø3,2) e o furo de refrigeração vizinho (PCD 30, Ø8) sobram **0,72 mm** de
   ABS — cerca de 2 filetes de 0,4 mm — e é por ali que passa todo o torque do
   motor. Rever PCD ou diâmetro dos furos de refrigeração.
7. **Parede de 0,65 mm no bolso da porca.** Torre Ø8 com bolso hexagonal de
   circunraio 3,35 mm deixa 0,65 mm de ABS ao redor da porca capturada. Não
   sustenta pré-carga de M3.
8. **Sem folga em Z para o coxim.** A cadeia 154 (topo da torre) + 34
   (motor+suporte, não medido) = 188 mm **não inclui os 8 mm do coxim**. Ou o
   coxim não está nesse caminho de carga, ou a cota está 8 mm errada — e nesse
   caso os 35 mm que faltam de contenção viram 43 mm.
9. **Acesso à bateria.** A tampa tem 2 furos de parafuso e nenhum acesso a
   chave liga/desliga ou conector de carga.

---

## 6. Caderno de números corrigido

### 6.0 Ponto de operação v3.0 — r = 100 mm @ 1800 RPM

Comparação na **mesma rotação**, que é o que revela a alavanca real.

| | unid. | r = 130 | **r = 100** | |
|---|---:|---:|---:|---:|
| Taxa de imagem | Hz | 90 | **90** | — |
| Corrente de fase | A | 9,76 | **4,44** | −54% |
| Torque aerodinâmico | mN·m | 101,3 | 46,1 | −54% |
| Perda no cobre | W | 21,1 | 4,4 | −79% |
| **Temperatura do motor** | °C | **101** | **43** | −58% |
| Potência da fonte | W | 42,8 | 15,7 | −63% |
| Força centrífuga/painel | N | 171,2 | 131,7 | −23% |
| Deflexão da ponta | mm | 2,69 | 2,07 | −23% |
| SF na flexão | — | 2,3 | **3,0** | +30% |
| Inércia do rotor | g·m² | 2,227 | 1,327 | −40% |
| Energia de 1 painel solto | J | 11,1 | 6,6 | −41% |
| Raio estático do rotor | mm | 134 | 104 | −22% |
| Ø do cilindro de imagem | mm | 268 | 208 | −22% |

**Por que 1800 e não 2000.** Com Cd pessimista (lâmina 0,50 / boss 0,50),
r=100 @ 1800 dá 68 °C enquanto r=100 @ 2000 dá 90 °C e r=110 @ 1800 dá 100 °C.
É o único candidato que não colapsa quando o arrasto vem pior que o estimado.
Os 100 Hz seguem disponíveis como esticada, **após** medir o arrasto.

**O que não melhora, e é preciso dizer:** a massa praticamente não muda
(256 → 251 g), a força ainda é de 132 N por painel sem análise de fadiga, e o
painel montado dá 37,1 g — acima do limite de 35 g, que é o limite que estava
errado, não o painel.

### 6.0.1 Balanceamento no ponto v3.0

G6.3 a 30 rps com rotor de 251 g → **U admissível = 8,4 g·mm**.

| Fonte | Limite |
|---|---:|
| Δm entre os três painéis | ≤ **0,084 g** |
| Excentricidade da bateria de 48 g | ≤ **0,17 mm** |
| Resolução do contrapeso em r = 90 mm | ~93 mg |

Nenhum dos dois primeiros é atingível por posicionamento: exigem balanceamento
de correção em dois planos.

### 6.0.2 Corrente de fase ≠ corrente da fonte

Os 4,44 A são **de fase** — é deles que sai o aquecimento. A fonte de bancada vê
15,7 W, ou seja **2,1 A em 7,4 V**. Confundir os dois foi provavelmente o que
produziu o "5,8 A" órfão da v2.1. Ajustar a fonte para **6–7 V** para o ESC
operar em duty alto: a 1800 RPM o motor está a 26% da rotação a vazio em 2S, e
duty baixo piora a comutação.

---

## 6.1 Caderno da v2.1 (histórico)

Substitui as tabelas do `README-v2.1.md` até que a memória de cálculo reapareça.

### 6.1 Cinemática e POV

| RPM | ω (rad/s) | rps | Taxa (3 painéis) | v @ r=130 mm |
|---:|---:|---:|---:|---:|
| 1200 | 125,66 | 20 | 60 Hz | 16,3 m/s |
| 1500 | 157,08 | 25 | 75 Hz | 20,4 m/s |
| **1800** | **188,50** | **30** | **90 Hz** | **24,5 m/s** |

Taxa por painel = rps = 30 Hz. As duas taxas do Plano §2.1 estão corretas.

### 6.2 Cargas (m = 35 g, r = 130 mm)

| RPM | F por painel | 3 painéis | Aceleração |
|---:|---:|---:|---:|
| 1200 | 71,9 N | 216 N | 209 g |
| 1500 | 112,3 N | 337 N | 327 g |
| **1800** | **161,7 N** | **485 N** | **471 g** |

### 6.3 Flexão do painel a 1800 RPM

Carga distribuída 777 N/m; balanço de 86–104 mm; I = 910 mm⁴ (já com o canal do LED).

| | valor |
|---|---:|
| Deflexão da ponta | **2,5 – 5,4 mm** (E = 2,3 GPa) · 3,2 – 6,9 mm (E = 1,8 GPa) |
| Momento na saída do boss | 2,87 N·m |
| Tensão de flexão | **14,2 MPa** |
| Fator de segurança (ABS ~35 MPa) | **≈ 2,5** — e sem análise de fadiga |

Os 3,5 mm publicados ficam dentro da faixa. Mas o SF de 2,5 é baixo para peça
rotativa e **não aparece em nenhum documento**.

### 6.4 Energia

| | valor |
|---|---:|
| Inércia do rotor | ≈ 2,03 × 10⁻³ kg·m² |
| **Energia cinética a 1800 RPM** | **≈ 36 J** (README publica 21,3 J) |
| Só os painéis | 31,5 J |
| **Um painel solto** | **10,5 J a 24,5 m/s** ← dimensiona a contenção |

### 6.5 Aerodinâmica (ar livre; estimativa, não substitui CFD)

| Fonte | Potência (3 painéis) |
|---|---:|
| Lâmina, Cd 0,25 | 11,0 W |
| Lâmina, Cd 0,50 | 22,0 W |
| Lâmina, Cd 0,80 | 35,3 W |
| Boss/torres/gussets, Cd 1,0 | 18,3 W |
| **Total plausível** | **30 – 55 W** |

O confinamento dentro do cilindro reduz esse valor em regime (o ar co-rotaciona),
o que é mais um motivo para o CFD modelar o volume fechado, e não a pá isolada.

### 6.6 Isolamento de vibração

| | especificado | necessário |
|---|---:|---:|
| Rigidez por coxim | 540 – 1270 kN/m | ~1,4 kN/m |
| fn do conjunto | 400 – 620 Hz | ≤ 21 Hz |
| Deflexão estática | ~0,001 mm | ~0,6 mm |

### 6.7 Balanceamento

| | valor |
|---|---:|
| Grau alvo sugerido | G6.3 |
| Excentricidade admissível a 30 rps | 33,4 µm |
| **Desbalanceamento admissível (rotor 330 g)** | **11 g·mm** |
| Equivalente em Δm entre painéis | **± 0,085 g** |

### 6.8 Cadeia de cotas em Z

```
0      solo / face de apoio
4      piso da baia da base
154    topo da torre  (4 + 150)
156    face superior da chapa de alumínio 2 mm
[+8]   coxim, SE estiver neste caminho — não está na cadeia atual (F-07/lacuna 8)
188    Datum do rotor  ( = 154 + 34, motor+suporte NÃO MEDIDO )
191    plano médio do painel
 87    base do painel        ─┐ envelope do rotor
295    topo do painel        ─┘
260    topo da guarda de 260 mm a partir do solo
       → FALTAM 35 mm  (43 mm se o coxim entrar na cadeia)
```

---

## 7. Plano de ação

### Antes de imprimir qualquer coisa que não seja cupom

| # | Ação | Fecha |
|---|---|---|
| 0 | **Medir o cilindro que já existe** (altura, Ø interno, apoio) e **identificar o material** por ensaio de dobra numa sobra | §3.1, §3.2, F-06 |
| 1 | Preencher `docs/MEDICOES_DE_ENTRADA.md` (campânula, base do motor, altura do conjunto, fita, LiPo) | as 5 interfaces `verified: false` |
| 2 | Especificar motor, tensão, ESC e bateria; **re-derivar o limite de corrente** (o 5,8 A ficou órfão) e reescrever o critério A em torque/potência | F-03, F-14, §3.3 |
| 2b | **Baixar `tower_total_height_from_floor`** para caber na guarda real, antes de imprimir a base | §3.1 |
| 3 | Corrigir o piso do canal do LED para ≥ 0,6 mm e regenerar os STL | F-04 |
| 4 | Rever furos de refrigeração (teia de 0,72 mm) e bolso da porca (0,65 mm) | lacunas 6 e 7 |
| 5 | Aplicar o patch da montagem e regerar o `.blend` para checagem de interferência | F-05 |

### Antes de girar

| # | Ação | Fecha |
|---|---|---|
| 6 | Refazer o orçamento de massa com bateria, fitas e ferragens | F-10 |
| 7 | Refazer força, energia e contenção com a massa real | F-01, F-06 |
| 8 | Confirmar PC por ensaio; se for PMMA, ensaiar dentro de contenção externa. Resolver o conflito anel × cilindro com o Ø interno real | F-06, §3.2 |
| 9 | Decidir o isolamento: montagem rígida assumida, ou isolador redimensionado com critério em fn | F-07 |
| 10 | Reescrever o Teste 4 do guia TPU (≤ 1,4 ciclo para 50%) e a massa de aceite (1,85 g) | F-08, F-09 |
| 11 | Acrescentar Δm ≤ ±0,085 g entre painéis e cota radial 130 ±0,1 mm | F-11, F-12 |
| 12 | Documentar sentido de giro, sensor de índice, caminho de sinal e roteamento de fios | lacunas 1–4 |

### Documental

| # | Ação | Fecha |
|---|---|---|
| 13 | ~~Recuperar a `TABELA-COMPARATIVA`~~ — **impossível, confirmado**. Aposentar formalmente os números órfãos e adotar §6 como memória de cálculo | F-14, §3.3 |
| 14 | Corrigir o README: números, tamanhos, referências cruzadas, Datum D, cronograma | F-15…F-18 |
| 15 | Suavizar a afirmação sobre flicker no Plano §2.1 | F-19 |
| 16 | Corrigir os erros factuais do guia TPU (impressoras, câmara, hotend, orientação, tempo) | F-20 |

### Sobre a decisão 1200 → 1800 RPM

Ela foi tomada com base numa margem térmica que, refeita com os números do
próprio documento, **não existe** (F-02), e com uma força centrífuga 71× menor
que a real (F-01). Isso não significa que 1800 RPM seja inviável — significa que
**a decisão ainda não foi tomada com dados válidos**. O caminho honesto é tratar
1800 RPM como hipótese, manter 1500 RPM como fallback declarado, e deixar o
termopar e o CFD decidirem.

---

*Auditoria produzida por releitura cruzada dos 5 documentos raiz, dos 12 arquivos
da pasta gerada, dos 11 STL e das 1098 linhas do gerador. Nenhum número foi
copiado dos documentos auditados: todos foram recalculados a partir de
`CAD/parameters.json` e da geometria exportada.*
