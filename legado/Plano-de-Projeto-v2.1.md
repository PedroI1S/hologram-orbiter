# Plano de Projeto — Hologram Orbiter v2.1

## 1. Objetivos

Este plano define a execução do protótipo de holograma orbital em regime de operação de 1800 RPM, com taxa de atualização de 90 Hz e arquitetura de 3 painéis. O objetivo principal é transformar a proposta conceitual em uma solução fabricável, testável e verificável em quatro fases: validação de bloqueadores, fabricação, integração e preparação para operação inicial.

Os entregáveis do projeto são:
- protótipo mecânico estável e alinhado;
- rotor com 3 painéis LED e geometria controlada;
- estrutura de suporte e isolamento vibratório adequados;
- validação de corrente, temperatura, amortecimento e qualidade visual;
- gate de decisão final para avanço ou fallback em 1500 RPM.

A execução prioriza critério objetivo e controle de risco. Em vez de comparar versões, o projeto define requisitos de aceitação e caminhos de contingência claros.

## 2. Fundação teórica

### 2.1 Visual e percepção do movimento

A taxa de atualização do projeto é 90 Hz para a rotação completa e 30 Hz por painel. A taxa por painel é relevante porque cada painel é apresentado em sequência, e a percepção do movimento depende da integração temporal do olho e do movimento do objeto.

Com 1800 RPM:
- 1 revolução = 33,33 ms
- 90 Hz = 11,11 ms por atualização
- 1800 RPM = 30 rps
- velocidade angular = 188,5 rad/s

A condição relevante aqui é a limiar de fusão perceptual: a atualização em 11,1 ms está abaixo do limiar de aproximadamente 40 ms e é compatível com a sensação de movimento contínuo em visão periférica, especialmente quando o objeto se move rápido e o observador acompanha o movimento. O cenário exige validação visual empírica, mas a base teórica aponta para viabilidade.

### 2.2 Tolerâncias críticas e acoplamento visual

O principal risco não é a resistência estrutural, mas o acoplamento entre desalinhamento geométrico e percepção visual. A altura do painel em relação ao eixo de rotação altera o ponto de montagem do LED e introduz jitter de imagem durante a rotação. A tolerância de datum D de ±0,2 mm é necessária porque o deslocamento do ponto de montado do painel em relação ao eixo muda a linha de visão e a imagem percebida em movimento rápido.

| Parâmetro | Valor alvo | Justificativa técnica |
|---|---:|---|
| Datum D | ±0,2 mm | Acoplamento visual: deslocamento de altura corta a relação entre eixo de rotação e ponto de referência do painel; maior desvio produz jitter perceptível em saccade. |
| Δh entre painéis | ±0,5 mm | O binário gerado por diferença de altura altera a força de centrífuga e a fase de cada painel; tolerância apertada limita oscilação e desbalanceamento. |
| Massa por painel | ≤ 35 g | Cada 10 g extras na borda aumenta a carga de borda e a força centrífuga, elevando tensão e vibração. |
| Perpendicularidade torre/base | ≤ 1° | Desalinhamento em eixo vertical quebra a referência de montagem do rotor. |
| Plano da base | ±2 mm | Garante apoio estável e reforça senso de alinhamento do rotor. |

### 2.3 Força centrífuga e rigidez

A força centrífuga é dominante na borda do painel. Com raio efetivo de 130 mm e painel de 35 g, a força centrífuga em 1800 RPM é aproximadamente 80 N por painel. Com 3 painéis, a carga total no rotor é elevada, mas o conjunto ainda é tratável com geometria adequada e material apropriado.

Do ponto de vista de projeto, a análise de massa, rigidez e coordenadas de montagem importa mais do que a estética. O rotor deve ser distribuído para evitar diferenças de fase, e a estrutura estacionária deve sustentar e isolar o conjunto sem introduzir vibração residual.

### 2.4 Arrasto e corrente do motor

O bloco crítico de potência é o arrasto do painel em rotação. O torque resistivo depende da forma do painel, do ângulo de ataque e da resistência do ar. Se o coeficiente de arrasto real for superior ao previsto, a corrente do motor excede o limite da referência de projeto. Essa é a principal incerteza do projeto e deve ser resolvida em fase 0 por validação experimental ou CFD.

Critério de projeto:
- corrente do motor ≤ 5,8 A;
- se exceder esse limiar, a solução prudente é reduzir a rotação para 1500 RPM.

### 2.5 Térmica e amortecimento

O motor operando em regime contínuo precisa manter temperatura abaixo do limite seguro. O regime de operação em 1800 RPM gera aquecimento significativo, e a dissipação depende do fluxo de ar, do acoplamento do motor e da estrutura. O termopar e a validação térmica são obrigatórios antes de avanço.

A outra grande variável é o amortecimento do coxim. O material TPU deve alcançar relação de amortecimento ζ ≥ 0,08 para reduzir vibração e manter o movimento estável. Se o valor cair abaixo do limite, a opção é trocar o material ou usar a solução de coxim alternativo.

## 3. Escopo da Fase 0

A Fase 0 é a fase de bloqueadores. Seu propósito é confirmar que os quatro riscos críticos são controláveis antes do avanço para fabricação e montagem do protótipo. A fase deve ser tratada como uma validação decisória e não como preparação genérica.

Escopo da fase 0:
- validar CFD/arrasto e corrente em 1800 RPM;
- medir temperatura em operação contínua;
- validar amortecimento do coxim TPU;
- avaliar jitter visual e tolerâncias por inspeção e observação;
- confirmar que a geometria estrutural satisfaz alinhamento e massa.

Gate principal da Fase 0:
- todas as quatro validações passam;
- se qualquer bloqueador falha, o projeto entra em fallback apoiado por decisão explícita.

## 4. Cronograma semana-a-semana

### Semana 1 — CAD e bloqueador 1
- modelagem final da estrutura e rotor;
- revisão dos datums e da referência de altura;
- CFD inicial para arrasto e corrente;
- medição preliminar de massa por painel;
- gate G0: corrente estimada ≤ 5,8 A e massa por painel ≤ 35 g.

### Semana 2 — Fabricação do lote 1
- impressão do rotor: aranha, 3 painéis e tampa;
- medição de Datum D, Δh e alinhamento dos painéis;
- avaliação dimensional das peças impressas;
- gate G1: Datum D dentro de ±0,2 mm; Δh ≤ ±0,5 mm; ausência de falhamento estrutural.

### Semana 3 — Fabricação do lote 2 e teste térmico
- impressão da torre ABS e base estrutural;
- montagem inicial sem LED para inspeção de alinhamento;
- teste termopal em operação contínua;
- gate G2: temperatura máxima < 55°C por 10 min e ausência de desalinhamento estrutural.

### Semana 4 — Montagem e visual
- montagem final do rotor e estrutura;
- validação vibração/amortecimento do coxim;
- teste visual em movimento e saccade;
- gate G3: jitter imperceptível e operação estável.

### Gate final de decisão
- G4: decisão de avanço para Fase 1 ou fallback para 1500 RPM;
- caso o projeto passe nos testes, inicia-se o ciclo de integração e ajustes finais;
- se falhar em qualquer bloqueador, segue-se com ação corretiva documentada.

## 5. Bloqueadores

| Bloqueador | Critério de aceite | Risco | Resposta |
|---|---|---|---|
| CFD / corrente | I ≤ 5,8 A | arrasto excedente e sobreaquecimento | reduzir RPM para 1500 se necessário |
| Térmico | T < 55°C em 10 min | operação instável e degradação | ventilação, dissipador, redução de carga |
| TPU / vibração | ζ ≥ 0,08 | vibração residual e ruído | trocar coxim ou aumentar amortecimento |
| Visual / jitter | imperceptível em saccade | qualidade de imagem insuficiente | reduzir tolerância ou alterar RPM |

Esses 4 bloqueadores formam a linha de decisão do projeto. Nenhum deles pode ser tratado como “opcional” ou como atividade de acompanhamento: cada um deve manter um critério explícito e um fallback definido.

## 6. Fases 1 a 3

### Fase 1 — Fabricação e ajuste dimensional
- validado o lote principal de peças;
- reimpressão de peças fora de tolerância;
- ajustes em pontos de fixação, boss e toda geometria crítica;
- confirmação da montagem do rotor sem empenamento.

Entregável: conjunto mecânico pronto para integração funcional.

### Fase 2 — Integração e validação elétrica
- montagem do motor, suporte, base e estrutura;
- instalação do sistema de LED e eletrônica;
- validação de alinhamento, torque de fixação e dissipação térmica;
- execução de testes de operação em curta duração.

Entregável: protótipo funcional de bancada.

### Fase 3 — Operação e preparação para demonstração
- teste contínuo em regime de operação;
- validação visual em ambiente realista;
- ajustes finos de balanceamento e contraste;
- preparação de documentação de operação, checkpoints e contingências.

Entregável: protótipo aprovado para operação ou preparação documental para melhoria de próxima geração.

## 7. Referências

1. Pöppel, E. (1978). Time perception. In: Handbook of Sensory Physiology.
2. Broca, A.; Sulzer, D. (estudos clássicos sobre persistência visual e fusão temporal).
3. Boff, K. R.; Lincoln, J. E. (engineering psychophysics aplicados a percepção de movimento).
4. Mecanismos de fluxo de ar e arrasto: referência bibliográfica em aerodinâmica básica e CFD de corpos girantes.
5. Materiais de engenharia: ABS, TPU 95A, acrílico e desempenho estrutural em alta rotação.
6. Manuais do motor BLDC e especificações térmicas de operação contínua.

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Arrasto superior ao estimado | média | alto | CFD e teste de corrente |
| Temperatura alta em regime contínuo | média | alto | termopar e ventilação |
| Damping insuficiente do coxim | baixa | médio | troca de material ou reforço de coxim |
| Jitter perceptível em saccade | baixa | alto | revisão de tolerância e ajuste de RPM |
| Falha de impressão dimensional | média | médio | reimpressão local e controle de lote |
| Desalinhamento estrutural | baixa | médio | inspeção dimensional e ajuste de montagem |

## 9. Sucesso

O projeto será considerado bem-sucedido quando:
- a operação em 1800 RPM for estável;
- a corrente do motor estiver abaixo do limite de risco;
- a temperatura permanecer abaixo de 55°C em operação contínua;
- o coxim absorver vibração de forma adequada;
- o jitter visual não for perceptível;
- a geometria e as tolerâncias estiverem dentro dos critérios declarados.

Se alguma destas condições não for atendida, a resposta correta não é “forçar a operação”. O projeto deve reduzir a rotação, trocar a peça crítica ou ajustar a geometria de acordo com o gate validado.

Arquivo: Revisao-Tecnica-e-Ajustes-NOVO.md