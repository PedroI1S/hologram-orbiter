# Revisão Técnica e Ajustes — Hologram Orbiter v2.1

## 1. Bloqueadores críticos

Os quatro bloqueadores abaixo definem a linha de decisão do projeto. Eles devem ser tratados como critérios de aprovação antes de qualquer avanço em fabricação, montagem ou operação em regime contínuo.

### 1.1 Bloqueador A — CFD e corrente do motor

Parâmetro crítico: corrente em 1800 RPM.

Se o arrasto real do rotor for maior do que o previsto, a corrente do motor cresce e a operação deixa de ser segura. A incerteza principal não é a potência nominal do motor, mas a resistência aerodinâmica real do conjunto de painéis.

Critério de aceite:
- I ≤ 5,8 A em operação de validação;
- se I exceder esse valor, aplicar fallback para 1500 RPM.

### 1.2 Bloqueador B — termal em regime contínuo

O sistema usa motor e eletrônica em um ambiente que apresenta risco térmico. O principal teste é medir a temperatura em regime contínuo, durante 10 minutos, em 1800 RPM.

Critério de aceite:
- T_max < 55°C;
- se exceder esse limite, reduzir RPM ou reforçar dissipação.

### 1.3 Bloqueador C — amortecimento do coxim TPU

Sem um coxim adequado, o rotor vibra e o sistema perde estabilidade. A exigência mínima é relação de amortecimento ζ ≥ 0,08.

Critério de aceite:
- ζ ≥ 0,08;
- abaixo disso, substituir ou alterar a geometria do coxim.

### 1.4 Bloqueador D — qualidade visual e jitter

O projeto depende de percepção visual eficaz. A imagem não pode apresentar jitter perceptível durante a rotação e a saccade do observador. O impacto prático está na qualidade da imagem e não apenas na estética.

Critério de aceite:
- nada perceptível em movimento rápido;
- em caso de falha, reduzir tolerância ou reduzir velocidade.

## 2. Testes detalhados para cada bloqueador

### Teste A1 — CFD / arrasto do painel

Propósito:
- quantificar arrasto real em regime de 1800 RPM;
- estimar corrente do motor e potência dissipada.

Medida:
- simulação CFD da geometria do painel e do conjunto rotor;
- coleta de coeficiente de arrasto, distribuição de pressão e torque resistivo;
- comparação com a corrente esperada.

Critério:
- I ≤ 5,8 A; caso contrário, a operação em 1800 RPM é rejeitada.

Fallback:
- reduzir velocidade para 1500 RPM;
- reconfigurar geometria do painel ou aumentar a área de ventilação.

### Teste A2 — validação de massa e geometria do painel

Propósito:
- confirmar que cada painel não excede massa máxima e que o conjunto fica dentro do controle.

Medida:
- pesagem individual dos painéis;
- medição de Datum D e Δh;
- inspeção de simetria entre os três painéis.

Critério:
- massa ≤ 35 g por painel;
- Datum D em ±0,2 mm;
- Δh ≤ ±0,5 mm.

Fallback:
- reimpressão da peça fora de tolerância;
- ajuste de distribuição de massa ou balanceamento.

### Teste B1 — termopares em operação contínua

Propósito:
- verificar temperatura do motor em regime contínuo.

Medida:
- termopar em enrolamentos ou ponto crítico do motor;
- operação por 10 minutos em 1800 RPM;
- registro da curva T × tempo.

Critério:
- T_max < 55°C;
- tendência estável sem aquecimento progressivo.

Fallback:
- reduzir rotor para 1500 RPM;
- aumentar dissipação ou revisar fluxo de ar.

### Teste B2 — inspeção térmica do conjunto

Propósito:
- verificar que os componentes adjacentes não superem o limite do material ou da eletrônica.

Medida:
- medição de temperatura na estrutura, suporte e região de baia elétrica;
- checagem do comportamento após 5 e 10 minutos.

Critério:
- temperatura abaixo do limite do material e da eletrônica;
- sem deformação da base ou da torre.

Fallback:
- reorganizar dissipação;
- aumentar ventilação entre base e suporte;
- adicionar material ou separador térmico.

### Teste C1 — drop test do coxim

Propósito:
- medir resposta dinâmica e capacidade de amortecimento do TPU.

Medida:
- provocar deslocamento ou um pulso de vibração;
- observar decaimento da oscilação;
- calcular o coeficiente de amortecimento ζ.

Critério:
- ζ ≥ 0,08.

Fallback:
- substituir o coxim por material mais resistente;
- aumentar número de coxins ou alterar geometria;
- usar opção alternativa com estrutura de apoio.

### Teste C2 — inspeção de vibração em bancada

Propósito:
- confirmar que a estrutura não amplifica vibração em operação.

Medida:
- operar em velocidade de teste;
- observar vibração em base, torre e suporte;
- medir ruído e oscilação visual.

Critério:
- estabilidade observável em operação contínua;
- sem crescimento de vibração ao longo do tempo.

Fallback:
- alterar ajuste de coxim;
- revisar fixação e planicidade da base;
- balancear o rotor.

### Teste D1 — validação visual de jitter em saccade

Propósito:
- verificar se a imagem apresenta jitter perceptível em observação realista.

Medida:
- executar o sistema em velocidade nominal em ambiente escuro;
- observar com movimento rápido do observador e em diferentes distâncias;
- registrar presença ou ausência de instabilidade visual.

Critério:
- imagem estável e sem jitter perceptível.

Fallback:
- reduzir velocidade;
- reduzir tolerância de Δh;
- ajustar posicionamento de peças e borda do painel.

### Teste D2 — validação dimensional de alinhamento

Propósito:
- verificar se o conjunto mantém a referência de altura e alinhamento entre painéis.

Medida:
- aferir Datum D;
- medir diferença de altura e simultaneidade de rotação;
- verificar alinhamento da torre e do suporte.

Critério:
- tolerância de Datum D e Δh atendida;
- ausência de desvio de eixo de rotação.

Fallback:
- reimpressão ou re-alinhamento da peça crítica;
- ajuste da estrutura para compensar desvio de eixo.

## 3. Matriz de riscos

| Risco | Probabilidade | Impacto | Evidência esperada | Mitigação |
|---|---|---|---|---|
| Arrasto superior ao previsto | média | alto | corrente acima de 5,8 A | CFD e fallback para 1500 RPM |
| Aquecimento em operação contínua | média | alto | T > 55°C | termopar, ventilação e redução de RPM |
| Coxim com amortecimento insuficiente | baixa | médio | ζ < 0,08 | troca de material e ajuste de geometria |
| Jitter visual perceptível | baixa | alto | observador detecta instabilidade | reduzir tolerância e validar em saccade |
| Desalinhamento por impressão | média | médio | Δh fora do limite | reimpressão e controle de material |
| Falha de montagem | baixa | médio | estrutura instável | inspeção e ajuste |

## 4. Fallback paths

### Caminho A — falha em CFD / corrente
Se a corrente ultrapassar 5,8 A:
- reduzir operação para 1500 RPM;
- repetir medição e comparar com limite;
- revisar geometria do painel ou perfil aerodinâmico.

### Caminho B — falha térmica
Se a temperatura exceder 55°C:
- operar em menor RPM;
- revisar fluxo de ar e dissipação;
- aplicar dissipador ou aumentar área de troca térmica.

### Caminho C — falha do coxim
Se o coxim falhar em amortecimento:
- trocar por material alternativo;
- aumentar ou redistribuir coxins;
- ajustar geometria para reduzir vibração.

### Caminho D — falha visual
Se o jitter for perceptível:
- reduzir RPM;
- diminuir tolerância de Δh;
- revisar ajuste do rotor e da base.

## 5. Decisão final

O protótipo avança apenas se todos os quatro blocos críticos forem aprovados. A decisão não deve sofrer revisão subjetiva: a lógica operacional é clara, com critérios bem definidos e caminhos de contingência explícitos.

