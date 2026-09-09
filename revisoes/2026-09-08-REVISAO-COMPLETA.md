# Revisão técnica do Hologram Orbiter v3.0 — 08/09/2026

**Registro anterior às correções locais.** A aplicação posterior e o estado atual
estão em [CORRECOES-APLICADAS](2026-09-08-CORRECOES-APLICADAS.md). As evidências
abaixo descrevem a revisão 3.0.3 auditada e foram preservadas.

**Resultado: a revisão digital encontrou erros relevantes de cálculo, montagem e validação. Os 54 critérios aprovados não sustentam uma liberação mecânica ou elétrica. Manter o conjunto sem liberação para girar e revisar os itens P1 antes de fabricar o lote definitivo de painéis.**

Base revisada: commit `9347b9a0296119603d80bb390ca7b250b1907293`, CAD 3.0.3. Escopo: documentos 01–07, READMEs, parâmetros, gerador, sondagem, scripts, relatórios, montagem Blender e nove STLs vigentes. Legado e revisões anteriores foram usados como histórico, não como requisitos atuais.

Esta é uma revisão, sem alterações nas peças, especificações ou parâmetros. Foram acrescentados somente este relatório e suas evidências. Não houve ensaio físico, FEA, CFD, fatiamento completo ou teste de firmware em hardware; não existe implementação de firmware versionada neste pacote para executar. Propriedades de ABS, arrasto, perdas elétricas e massas de catálogo continuam sendo hipóteses, mesmo quando a aritmética fecha.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| Blender instalado | 5.2.1 LTS, execução por Python funcional |
| Regeneração em cópia temporária | concluída; 54/54 critérios atuais passam |
| Nove STLs originais revalidados | 9/9; resultado JSON idêntico ao versionado |
| Nove STLs regenerados revalidados | 9/9; volumes, envelopes e aceitação preservados |
| Reprodutibilidade | a triangulação da tampa mudou de 6538 para 6552 triângulos; volume e critérios iguais. Não há identidade binária geral dos STLs |
| Interseções da montagem Blender | 20 objetos de montagem examinados; colisão aranha × envelope do buck encontrada |
| Seção resistente do painel | integrada a partir dos polígonos e confirmada em três cortes independentes do STL |
| Massas e balanceamento nominal | soma de aproximadamente 278,6 g reproduzida; contrapesos 2,19 + 0,87 g coerentes com as hipóteses do CAD |
| Cinemática básica | 1800 RPM = 30 rps = 188,496 rad/s; três painéis dão 90 passagens/s |
| Força/energia de projeto | painel de 44,5 g em r=100 mm: 158,1 N e 7,906 J; 1,55 g·m² a 1800 RPM: 27,54 J |
| Balanceamento G6,3 publicado | e=33,42 µm; usando 252 g, U=8,42 g·mm |

Os testes de malha foram repetidos com o validador existente. Portanto, sua repetição confirma os resultados, mas não constitui uma segunda implementação independente de topologia. A integração da seção e a busca de interseções acrescentam verificações que o gerador não fazia.

## Achados prioritários

P1: corrigir antes de usar o resultado para fabricação definitiva, montagem operacional ou aceite de ensaio. P2: defeito concreto de documentação, parametrização ou procedimento que precisa ser corrigido no fechamento da revisão.

### R01 — P1 — A rigidez usada na flexão não corresponde à seção do painel

**Referência:** `01-ESPECIFICACAO-CAD-v3.0.md:751–790`; `CAD/parameters.json`, perfis e canal do painel.

A especificação usa **I=910 mm⁴**, menciona uma redução de apenas ~30 mm⁴ pelo canal atual e usa c=4 mm. A seção real fora do boss e dos diafragmas resulta em:

- área: 106,49985 mm²;
- centroide radial: x=−0,53095 mm;
- Iyy no centroide: **589,8846 mm⁴**;
- distância à fibra externa: **4,53095 mm**;
- I efetivo considerando o pequeno produto de inércia: aproximadamente 589,70 mm⁴.

Os cortes do STL em z=20,23; 50,23; 90,23 mm confirmam Iyy=589,8846 mm⁴. O valor efetivo é cerca de **35% inferior** ao publicado. Mantendo a mesma carga distribuída, condições de apoio e módulos usados no documento:

| Balanço L | E | Deflexão publicada | Recalculada | Tensão externa pela aproximação de flexão simples | SF usando 30 MPa |
|---:|---:|---:|---:|---:|---:|
| 86 mm | 2,3 GPa | 2,5 mm | **3,83 mm** | ~21,6 MPa | ~1,39 |
| 86 mm | 2,0 GPa | 2,9 mm | **4,41 mm** | ~21,6 MPa | ~1,39 |
| 99 mm | 2,0 GPa | 5,0 mm | **7,74 mm** | ~28,6 MPa | ~1,05 |

Isso **não prova ruptura do painel**: a distribuição uniforme de toda a massa montada é simplificada e inclui massa concentrada no boss. Prova que a afirmação de SF ~2 e a faixa de 3–5 mm não resultam da seção vigente. O infill real, a anisotropia, os engastes e a fluência ainda precisam entrar na análise. A folga do cilindro permanece positiva nesse recálculo simples: 133−(104+7,74)≈21,3 mm, antes de outras tolerâncias; essa folga não substitui resistência suficiente.

**Correção:** calcular a seção a partir da malha/parâmetros, distribuir as massas por posição, verificar a transferência de carga e atualizar flexão, resistência, fluência e raio dinâmico em todos os documentos. Reavaliar o painel antes de congelar sua fabricação.

### R02 — P1 — A rampa nominal de 8 s reprova o próprio limite de corrente previsto

**Referência:** `04-PLANO-DE-ENSAIOS-v3.0.md:175–187`; `01-ESPECIFICACAO-CAD-v3.0.md:719–739`.

O caso vigente usa torque de arrasto de 51,4 mN·m, mas o cálculo de contingência ainda usa 46,1 mN·m do melhor caso. Com a inércia publicada:

`I_fase=(J·ω/t + T_arrasto)/Kt`, com J=0,00155 kg·m² e Kt=0,0103797 N·m/A.

| Rampa | Aceleração | Pico de fase |
|---:|---:|---:|
| 8 s | 36,52 mN·m | **8,47 A**, não 8,0 A |
| 12 s | 24,35 mN·m | **7,30 A**, não 6,8 A |

Adotando a eficiência de ESC de 95% que reproduz as demais linhas da tabela, a rampa de 8 s chega a ~34,9 W / **4,98 A na fonte de 7 V**, acima do aceite de 4,6 A. Para limitar a 8 A de fase, a rampa linear calculada seria aproximadamente **9,23 s**, ainda sem margem. Rampa de pulso servo não garante rampa linear de RPM: medir a aceleração real.

**Correção:** unificar o caso de arrasto e atualizar rampa, corrente prevista, fonte e critério. Não afrouxar o limite apenas para fazer a tabela passar.

### R03 — P1 — A previsão da esticada a 2000 RPM continua sendo a do melhor caso

**Referência:** `01-ESPECIFICACAO-CAD-v3.0.md:67–69`.

O texto promete 5,49 A e 51 °C. Mantendo o modelo de arrasto do projeto, I varia com RPM²: `4,95×(2000/1800)²=6,11 A`. Com R=0,221 Ω, Rth=3,5 K/W e perdas adicionais de 0,7 W, a temperatura calculada é **56,3 °C**, superior ao limite de 55 °C. Os 5,49 A derivam de 4,44 A, o melhor caso.

**Correção:** retirar a previsão de margem térmica a 2000 RPM ou recalculá-la usando o arrasto medido. O projeto já condiciona essa rotação a ensaio; a previsão numérica também deve refletir essa condição.

### R04 — P1 — O termopar foi especificado em uma superfície girante

**Referência:** `04-PLANO-DE-ENSAIOS-v3.0.md:50–70`.

O método manda prender termopar à carcaça entre as aletas do A2212. No outrunner, a campânula externa gira. Um cabo ligado a um leitor estacionário não pode permanecer preso ali durante o ensaio. A medição da bateria embarcada também não tem um método implementado.

**Correção:** definir um ponto fixo realmente acessível e sua relação com o limite térmico, ou instrumentação sem contato/embarcada adequada. Para a bateria, definir medição embarcada ou outro método validado. Resolver ainda o conflito entre aborto a 55 °C no bloqueador A e 60 °C no B.

### R05 — P1 — O método descrito não fecha o balanceamento em dois planos

**Referência:** `04-PLANO-DE-ENSAIOS-v3.0.md:143–165`; `02-PLANO-DE-PROJETO-v3.0.md`, fases G3/G4.

O plano pede fase e amplitude a 30 Hz e correção em dois planos, mas descreve um acelerômetro na base, sem referência angular fixa sincronizada e sem as medições/ensaios separados necessários para identificar os dois planos. Em G3 o Hall embarcado ainda não está disponível. Leitura de RPM sozinha não fornece referência de fase.

Uma resposta complexa em um ponto não determina dois vetores independentes de desbalanceamento. São necessários canais/condições independentes e massas de teste por plano, ou um método equivalente explicitamente definido. A literatura de instrumentação descreve a referência de fase e as medições necessárias no [guia de balanceamento da Brüel & Kjær](https://www.bksv.com/media/doc/17-227.pdf).

**Correção:** documentar instrumentação e método realizável, com referência 1/rev e identificação de cada plano. Enquanto isso, vibração baixa no MPU e massas iguais não comprovam U≤8,4 g·mm nem ausência de binário.

### R06 — P1 — O ensaio de polaridade alimenta o A3144 fora da faixa garantida

**Referência:** `06-PENDENCIAS-ABERTAS-v3.0.md:49–52`; `CAD/parameters.json`, `unverified_interfaces.magnet.polarity_note`.

O teste manda VCC=3,3 V e conclui que, se não comutar, a face do ímã está errada. A faixa operacional do A3144 original é **4,5–24 V**. O teste pode falhar por alimentação, sem provar polaridade incorreta. O esquema 05 já usa a separação correta: alimentação 5 V e pull-up da saída para 3,3 V. [Datasheet Allegro A3141–A3144](https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx?la=en).

**Correção:** usar VCC=5 V, GND comum local e pull-up de 10 kΩ para 3,3 V; identificar o componente real, pois a marcação genérica de um módulo não garante fabricante e curva.

### R07 — P1 — O build pode terminar com sucesso apesar de falha ou rejeição

**Referências:** `scripts/build.sh:16–19`; `CAD/generate.py:2573–2579`; `scripts/validate_stl.py:126–153`.

Três falhas independentes foram confirmadas:

1. O gerador imprime critérios reprovados, mas termina com `os._exit(0)`; o código de saída não representa a aceitação.
2. As chamadas Blender não usam `--python-exit-code`. Um script com `RuntimeError` foi executado e o processo terminou com código 0. `set -e` não impede que o build prossiga sobre arquivos antigos.
3. O validador aceita um diretório vazio: retorno 0 e `{"all_pass":true,"files":[]}`. Também não exige a lista completa de nove arquivos.

**Correção:** propagar falha de Python e aceitação; validar inventário obrigatório; gerar em diretório novo e promover os artefatos apenas após todas as verificações. Associar os relatórios aos hashes de parâmetros e arquivos da mesma execução.

### R08 — P2 — O buck interfere com a aranha apesar do critério de layout aprovado

**Referências:** `CAD/generate.py:684–712`, `740–766`; `CAD/parameters.json`, componente `buck`; `reports/ACEITACAO.md`, linha de layout da baia.

Interseção booleana EXACT entre os objetos da montagem original encontrou **0,9821 mm³** comuns entre `MONTAGEM_aranha` e `MONTAGEM_baia_buck`. Limites da interseção, no referencial global: x=−24,202…−23,144; y=29,905…30,785; z=186,631…191,369 mm.

O verificador usa uma lista simplificada de obstáculos que inclui berço e postes, mas não toda a malha da aranha. Portanto, a aprovação não equivale a ausência de colisões. O buck é um envelope estimado: a interseção prova incompatibilidade entre os modelos declarados, não que o módulo real necessariamente colidirá nessa região.

**Correção:** confrontar a placa real com o local e reposicionar/aliviar se necessário; incluir teste contra a malha final. A outra interseção encontrada, porca × rosca, é esperada porque a porca de referência foi modelada como sólido sem furo e não foi contada como defeito físico.

### R09 — P2 — O guia de montagem ensina quatro fios, mas o circuito exige seis

**Referências:** `docs/FIACAO_E_MONTAGEM.md:6–28`; `CAD/parameters.json`, `panel_wiring`; `05-ESQUEMA-ELETRICO-v3.0.md:89–106`.

A alimentação em estrela com cadeia DATA/CLK em série exige duas vias de potência, duas de entrada e duas de retorno nos painéis intermediários. O esquema exige chicotes iguais de seis fios nos três painéis por balanceamento; o guia e os parâmetros declaram quatro. Seguir o guia deixa a cadeia incompleta e invalida premissas de massa/CG do chicote.

**Correção:** unificar os seis condutores, verificar a rota completa e as bitolas com a isolação real, pesar chicotes e recalcular CG/balanceamento. Não concluir cabimento pela seção do cobre: importa o diâmetro externo dos fios e a passagem pelos diafragmas.

### R10 — P2 — A sequência fecha o acesso antes de apertar a porca do eixo

**Referência:** `docs/FIACAO_E_MONTAGEM.md:102–118`.

O procedimento instala a bateria, fecha a tampa e só depois manda montar cubo/arruela/porca no eixo. A porca fica sob a bateria central; a janela lateral da tampa não dá acesso axial ao aperto.

**Correção:** fixar e conferir o cubo enquanto a porca está acessível; instalar e reter a bateria e fechar a tampa depois. Adaptar a ordem das operações de balanceamento e inspeção a essa montagem realizável.

### R11 — P2 — O ajuste de folga recomendado não altera o cupom nem o socket

**Referências:** `docs/GUIA_IMPRESSAO.md:16–17`; `CAD/generate.py:1466–1483`; `CAD/parameters.json`, `quality.joint_xy_clearance_each_side` e `panel.boss.socket_*`.

O guia manda ajustar `quality.joint_xy_clearance_each_side`. Uma reprodução alterando 0,1 para 0,5 mm gerou o mesmo hash de triângulos no cupom: o código usa diretamente `socket_width` e `socket_height`, que permanecem 11,2 e 6,2 mm.

**Correção:** derivar socket e cupom de uma única folga ou corrigir a instrução para os parâmetros efetivamente usados, impedindo valores contraditórios.

### R12 — P2 — Parte dos critérios ignora os limites parametrizados

**Referência:** `CAD/generate.py`, função `acceptance()` a partir da linha 2249.

Executando a função com relatórios existentes, mudar a mesa para 250×250 mm e o limite de painel para 40 g manteve 54/54: as comparações continuaram usando os literais 300 e 45. Isso não reprova a geometria atual, cujo ponto é congelado, mas contradiz a orientação de editar parâmetros e regenerar como fonte de verdade.

**Correção:** distinguir requisitos fixos de parâmetros livres, rejeitar alterações incompatíveis ou consumir o valor configurado. Testar mudanças que devem reprovar, não somente o caso atual aprovado.

### R13 — P2 — O orçamento da bateria aplica perdas só em uma das três linhas

**Referência:** `05-ESQUEMA-ELETRICO-v3.0.md:111–125`.

A nota diz que a coluna inclui rendimento de 85–90% e ESP32 de 0,3 W. A linha típica calcula assim, mas branco e 30% ainda dividem aproximadamente a potência por 6,6 V sem perdas. Aplicando a mesma convenção explicitada no texto, η=0,875:

| Potência da linha | Corrente publicada | `(P/0,875+0,3)/6,6` | Autonomia ideal de 0,8 Ah |
|---:|---:|---:|---:|
| 27,3 W | 4,1 A | **4,77 A** | **10,1 min** |
| 9,0 W | 1,4 A | **1,60 A** | **29,9 min** |
| 5,1 W | 0,93 A | **0,929 A** | **51,7 min** |

**Correção:** definir se cada potência é dos LEDs, da saída do buck ou da bateria e não contar ESP32 duas vezes. Recalcular dimensionamento e autonomia útil com o pack/buck reais. Além disso, 87×60 mA=5,22 A só de LEDs: um módulo de exatamente 5 A não cobre o branco nominal completo mais eletrônica; confirmar o consumo da fita real e impor teto de brilho/corrente ou redimensionar.

### R14 — P2 — A margem magnética publicada usa o limite de 25 °C

**Referência:** `06-PENDENCIAS-ABERTAS-v3.0.md:114–130`.

A margem compara 45 mT calculados com BOP máximo de 35 mT. No datasheet do A3144, 35 mT é o máximo a 25 °C; na faixa térmica especificada o máximo é **45 mT**. Assim, os ~30% anunciados não são margem garantida em temperatura. O campo nominal é estimado e depende de distância e ímã reais. [Tabela magnética do datasheet Allegro](https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx?la=en).

**Correção:** usar o envelope térmico aplicável ao componente identificado e ensaiar tolerância de distância, temperatura e campo do motor. A pendência de entreferro já existe; seu cálculo de margem precisa ser corrigido.

## Outras inconsistências e limitações a fechar

- **Cotas não propagadas:** a especificação ainda tem baia de 26 mm em `01:285`, contra 29 no CAD. O relatório manual ainda põe trilhos globais em Z=192 em sua cadeia, mas 186+9=**195 mm**; bateria correta em 195–212. Há texto residual de energia de 26 J no README e notas antigas de baia de 26 mm. Não usar o relatório manual como tabela de montagem sem reconciliar com parâmetros/Blender.
- **Potência de regime:** as linhas de 3, 4, 5, 5,5, 6 e 8 A do ensaio são reproduzidas aproximadamente por `(Kt·ω·I+0,221I²+0,7)/0,95`. A linha de 4,95 A daria ~**16,63 W/2,38 A**, e não 16,2/2,31. Tornar explícita a eficiência adotada e gerar todas as linhas pela mesma expressão.
- **Protocolo e orçamento de tempo:** `32+87×32+44=2860 bits`, não 2859 (`05:134–151`). A janela a 1800 RPM/180 colunas é 185,19 µs; 2860 bits a 20 MHz ocupam143 µs, sobrando42,19 µs antes de overhead. A 2000 RPM sobram23,67 µs. Isso é viabilidade de transporte, não garantia de jitter/fase. O plano ainda precisa validar atualização efetiva dos HD107S ao longo da cadeia, compensação temporal e clock real. A [documentação SPI do ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c3/api-reference/peripherals/spi_master.html) distingue a frequência solicitada e a realizada e descreve custos por transação. A recomendação de 30 MHz deve ser verificada no clock efetivo e no lote de fita; não considerar os modos de 256 colunas validados.
- **Inércia:** J=1,55 g·m² reproduz os 27,6 J e pode ser mantida como hipótese conservadora identificada. Uma estimativa pela massa distribuída das peças e acessórios dá ordem de 1,34 g·m², mas depende das posições de fios/ferragens e da campânula. Não substituir o valor de projeto por essa estimativa sem fechar o inventário girante.
- **Massa e balanceamento:** o volume maciço reproduz as massas, mas o perfil prescreve infill parcial. Isso pode reduzir massa e mudar centróides/rigidez. Contrapesos nominais não dispensam pesar e balancear o conjunto impresso real. A margem de 1,4 g também depende dos 15 g estimados de eletrônica.
- **Ensaios em fases diferentes:** G3 sem eletrônica e G4 com bateria/placas são rotores de massas e distribuição diferentes; usar lastro representativo e registrar a necessidade de repetição. Já existem pendências de buck em baixa tensão, medição do eixo, contenção, fluência e modos de vibração. Elas permanecem abertas; não foram tratadas como resolvidas por esta revisão.

## Ordem recomendada de fechamento

1. Corrigir a seção resistente e refazer o caso mecânico; decidir se o painel precisa de mudança.
2. Tornar geração/validação incapazes de publicar sucesso após falha, inventário incompleto ou critério reprovado.
3. Unificar chicotes, acesso à porca, layout do buck, cotas e massas; regenerar e repetir a inspeção.
4. Corrigir Hall, correntes, rampa e previsão de 2000 RPM; fechar o componente buck e seu desempenho real.
5. Especificar instrumentação realizável para térmica, fase, balanceamento e timing; então executar os bloqueadores físicos com contenção.

## Evidências e reprodução

Arquivos em `evidencias/2026-09-08/`: recálculo de física e saída, resultados de validação original/regenerada, relatório de interseções, logs de geração e provas de falhas dos validadores. O script de física usa NumPy e o leitor binário de STL do pacote; as fórmulas de seção e integração são implementadas no script de auditoria.

Comandos executados em cópia temporária do pacote, para não sobrescrever os relatórios vigentes:

```sh
blender -b --python CAD/generate.py -- --no-render
python3 scripts/validate_stl.py exports/stl --output stl_revalidated.json
python3 revisoes/evidencias/2026-09-08/recalculo_fisica.py
```

O último comando é executado na raiz do repositório. O script de interseções abre o `.blend` original, calcula interseções em memória e salva apenas JSON; não salva alterações no modelo.
