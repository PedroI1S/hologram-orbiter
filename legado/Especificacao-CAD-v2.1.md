# Especificação CAD — Hologram Orbiter v2.1

## 0. Por que 10 peças? Por que ±0,2 mm? Por que validações?

O projeto foi organizado em 10 itens principais porque cada um deles cumpre uma função distinta dentro do sistema: rotor, estrutura, bloqueio de vibração, referência visual e suporte de montagem. A divisão em blocos ajuda a controlar variáveis críticas e a separar o que é funcional do que é apenas ornamental.

A tolerância de ±0,2 mm para Datum D foi escolhida porque a altura do painel em relação ao eixo de rotação define diretamente a relação entre ponto visual e centro de rotação. Qualquer desvio moderado pode transformar um movimento suave em um fenômeno sensorial perceptível, especialmente em saccade. O mesmo raciocínio vale para Δh entre painéis: a diferença de altura gera binário e vibração, além de modificar a distância entre os elementos visuais.

As validações são obrigatórias porque o projeto combina geometria precisa, movimento rápido e dissipação térmica. Em outras palavras, a parte visual não pode ser tratada isoladamente da parte mecânica. O sistema inteiro precisa ser validado em massa, alinhamento, temperatura, vibração e percepção.

## 1. Teoria e rationale do sistema

### 1.1 Referência geométrica

O sistema usa origem no centro de rotação do rotor, com eixo Z orientado verticalmente. A referência de altura e de centro radial são fundamentais para a estabilidade da imagem e para a consistência visual. Os principais elementos controlados são:
- datum A: face de montagem da campânula do motor;
- datum B: face superior do cubo, no plano rotor;
- datum C: ombro de encaixe da longarina;
- datum D: altura do boss/painel, com tolerância crítica;
- datum E: eixo vertical da torre estrutural.

### 1.2 Requisito de operação

A operação em 1800 RPM gera 90 Hz de taxa de imagem, ou 30 Hz por painel. O sistema trabalha com o princípio de persistência visual e movimento contínuo, mas o acoplamento da geometria com a percepção exige rigor dimensional. O objetivo da CAD não é apenas definir volumes, mas garantir que todos os painéis e a estrutura permaneçam em um alinhamento consistente durante a rotação.

### 1.3 Requisitos de tolerância

As tolerâncias críticas do projeto são:
- Datum D = 104 ±0,2 mm;
- Δh entre painéis = ±0,5 mm;
- massa do painel ≤ 35 g;
- perpendicularidade da torre relativa à base ≤ 1°;
- base com planicidade ±2 mm.

Essas especificações limitam três efeitos principais: jitter visual, vibração e desbalanceamento.

## 2. 10 peças e seus requisitos

### Peça 1 — Aranha

Descrição: cubo central com 3 longarinas em arranjo radial.

Geometria e tolerância:
- disco principal Ø 80 mm × 6 mm, tolerância ±0,5 mm;
- folga de montagem da campânula: 3–4 mm;
- 6 furos de admissão de ar Ø 8 mm;
- longarinas de seção 15 × 6 mm;
- furos de parafuso 2 × Ø 3,2 mm;
- filete de raiz R ≥ 5 mm.

Justificativa:
- a aranha define a estrutura do rotor e transmite a força centrífuga para o conjunto mantendo simetria radial.

### Peça 2 — Painel LED (3 unidades)

Descrição: painéis idênticos, montados em 120°.

Geometria e tolerância:
- altura 208 mm, tolerância ±0,5 mm;
- corda 30 mm, tolerância ±0,5 mm;
- espessura 8 mm, tolerância ±0,3 mm;
- canal da fita 13 × 1,8 mm, tolerância ±0,1 mm;
- boss com envelope 28 × 36 × 24 mm;
- Datum D = 104 ±0,2 mm;
- face de contato com o cubo em referência a C;
- massa por painel ≤ 35 g.

Justificativa:
- é a peça principal da imagem; sua geometria e posicionamento afetam diretamente a qualidade visual.

### Peça 3 — Tampa da baia de eletrônica

Descrição: tampa para a região de apoio eletrônico do cubo.

Geometria e tolerância:
- envelope Ø 70 mm × 5 mm;
- fixação com 2 furos de Ø 3 mm;
- vedação opcional com manta fina.

Justificativa:
- dá proteção ao conjunto eletrônico e mantém área funcional acessível.

### Peça 4 — Torre estrutural ABS

Descrição: suporte vertical do motor e do rotor.

Geometria e tolerância:
- tubo Ø 30 mm OD, parede 4 mm;
- comprimento 150 mm, tolerância ±2 mm;
- flanges inferior e superior Ø 60 mm × 8 mm;
- 4 furos de fixação Ø 4 mm;
- perpendicularidade da torre em relação à base ≤ 1°.

Justificativa:
- a torre fixa a referência Z do sistema e reduz variações estruturais em operação.

### Peça 5 — Base estrutural

Descrição: base de suporte do sistema, integrada à estrutura.

Geometria e tolerância:
- diâmetro ≥ 300 mm;
- altura 80–100 mm, tolerância ±2 mm;
- parede lateral 4 mm;
- planeza da base ±2 mm;
- baia para eletrônica Ø 100 mm × 20 mm;
- aberturas de ventilação 4 × Ø 10 mm.

Justificativa:
- a base garante estabilidade, fixa a torre e sustenta a distribuição térmica do conjunto.

### Peça 6 — Suporte do motor

Descrição: suporte em alumínio 2 mm para o motor.

Geometria e tolerância:
- chapa 60 × 60 mm;
- reforço térmico e fixação por parafusos M3/M4;
- alinhamento com a torre e o rotor.

Justificativa:
- mantém a montagem do motor em posição estável e reduz movimento relativo entre motor e estrutura.

### Peça 7 — Coxim

Descrição: amortecedor em TPU 95A.

Geometria e tolerância:
- Ø 16 × 8 mm;
- 4 unidades;
- material com relaxação controlada e ζ ≥ 0,08.

Justificativa:
- reduz vibração transmitida da estrutura para o rotor e vice-versa.

### Peça 8 — Anel de contenção

Descrição: anel interno ao cilindro acrílico.

Geometria e tolerância:
- material TPU 95A;
- ajuste eficiente ao cilindro, sem causar tensão excessiva;
- função de contenção e proteção.

Justificativa:
- protege a região física do rotor sem criar ruído significativo de contato.

### Peça 9 — Cilindro acrílico

Descrição: cilindro de proteção do rotor.

Geometria e tolerância:
- material acrílico de 4 mm;
- diâmetro mínimo compatível com base e rotor;
- espessura e simetria monitoradas.

Justificativa:
- garante segurança física e reduz interferência visual externa.

### Peça 10 — Contrapesos

Descrição: ajuste final de balanceamento.

Geometria e tolerância:
- massa aditiva ajustada por pequeno valor;
- posição radial e angular controlada;
- massa total e distribuição final ajustados por validação.

Justificativa:
- corrige residual de desbalanceamento e reduz vibração em operação.

## 3. BOM resumido

| Item | Componente | Material | Qtd | Observação |
|---|---|---|---:|---|
| 1 | Aranha | ABS | 1 | rotor principal |
| 2 | Painel LED | ABS | 3 | idênticos e simétricos |
| 3 | Tampa da baia | ABS | 1 | proteção da eletrônica |
| 4 | Torre estrutural | ABS | 1 | suporte vertical |
| 5 | Base estrutural | ABS | 1 | apoio e baia |
| 6 | Suporte do motor | Alumínio | 1 | estrutura de fixação |
| 7 | Coxim | TPU 95A | 4 | amortecimento |
| 8 | Anel | TPU 95A | 1 | contenção |
| 9 | Cilindro acrílico | Acrílico 4 mm | 1 | proteção |
| 10 | Contrapesos | cobre/fita ou massa ajustável | variável | balanceamento final |

## 4. Checklists de fabricação e validação

### 4.1 Checklist de fabricação
- [ ] Verificar materiais e lotes de impressão antes da produção.
- [ ] Configurar mesma posição na mesa para os 3 painéis.
- [ ] Manter temperatura e ambiente controlados para reduzir variação dimensional.
- [ ] Registrar massa individual de cada painel.
- [ ] Mensurar Datum D em cada peça antes da montagem.
- [ ] Medir Δh entre painéis e rejeitar fora de tolerância.
- [ ] Verificar orientação da torre e alinhamento da base.
- [ ] Confirmar fixação do motor e da estrutura sem folga estrutural.

### 4.2 Checklist de validação visual
- [ ] Operar em 1800 RPM e observar a imagem em ambiente controlado.
- [ ] Verificar se há jitter em movimento rápido do observador.
- [ ] Confirmar consistência de imagem entre os 3 painéis.
- [ ] Confirmar que o sistema mantém imagem estável sem micro-oscilações visíveis.

### 4.3 Checklist de validação estrutural
- [ ] Confirmar massa ≤ 35 g por painel.
- [ ] Confirmar Datum D = 104 ±0,2 mm.
- [ ] Confirmar Δh ≤ ±0,5 mm.
- [ ] Confirmar perpendicularidade torre/base ≤ 1°.
- [ ] Confirmar estabilidade da base e ausência de torção visível.

### 4.4 Checklist térmico e vibratório
- [ ] Rodar 10 minutos em 1800 RPM.
- [ ] Verificar T_max < 55°C.
- [ ] Medir vibração em bancada e estrutura.
- [ ] Validar ζ ≥ 0,08 do coxim.
- [ ] Repetir a operação e confirmar estabilidade sem crescimento de vibração.

## 5. Critério final de aprovação

O CAD é aceito quando a geometria, tolerâncias e montagem atendem a todos os requisitos descritos acima. Se qualquer peça exceder tolerância, a decisão correta é reimpressão ou ajuste, não compensação subjetiva. O projeto depende de precisão dimensional em pontos críticos e de validação operacional em cada bloco funcional.

