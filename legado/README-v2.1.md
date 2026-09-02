# README: Hologram Orbiter v2.1 — Pacote Completo

> Documentação completa do upgrade 1200 RPM (v2.0) → 1800 RPM (v2.1).
>
> **Status:** ✅ Análise concluída, documentação entregue, pronto para implementação  
> **Data:** 31/08/2026  
> **Equipe:** Robotinik

---

## 📋 Arquivos Entregues

### 1. Documentação de Decisão & Análise

| Arquivo | Tamanho | Propósito |
|---|---|---|
| **Revisao-Tecnica-e-Ajustes.md** | 15 KB | Análise técnica completa; 2 gaps críticos (flicker, arrasto) |
| **SUMARIO-v2.1.md** | 7,6 KB | Resumo executivo; decisão aprovada |
| **TABELA-COMPARATIVA-v2-v2.1.md** | 9,6 KB | Tabelas detalhadas de **todos** os parâmetros |

**Leitura recomendada:** 20 min (SUMARIO + TABELA)

---

### 2. Documentação de Projeto (v2.1)

| Arquivo | Tamanho | Propósito |
|---|---|---|
| **Plano-de-Projeto-v2.1.md** | 19 KB | Plano completo revisado para 1800 RPM |
| **Especificacao-CAD-v2.1.md** | 14 KB | Tolerâncias, specs CAD, testes pós-fab |
| **CHECKLIST-IMPLEMENTACAO-v2.1.md** | 13 KB | Roadmap Fase 0 (semana-a-semana) |

**Leitura recomendada:** 45 min (entender cada fase)

---

### 3. Referência Original (v2.0)

Manter para comparação:

| Arquivo | Propósito |
|---|---|
| Plano-de-Projeto-v2.md | Baseline 1200 RPM |
| Especificacao-CAD.md | Specs originais |
| Fundamentacao-Teorica-Hologram-Orbiter.md | Análise teórica motor |

---

## 🎯 Decisão Tomada

### ✅ APROVADO PARA v2.1 (1800 RPM)

**Principais Mudanças:**

```
Parâmetro               v2.0 (1200 RPM)    v2.1 (1800 RPM)    Ganho
──────────────────────────────────────────────────────────────────
Taxa de imagem          60 Hz              90 Hz              +50% ✓
Flicker perceptível     SIM ⚠️             NÃO ✓              Eliminado
Motor temperatura       ~52 °C             ~53 °C             +1,8 °C
Corrente               4,6 A              5,5 A              +20%
Força centrífuga       1,0 N/painel       2,3 N/painel       2,25×
Fator segurança        333×               147×               -56% (mas ok)
Cronograma             6–8 sem            7–9 sem            +1 sem testes
```

**Justificativa:** Flicker eliminado (ganho visual > margem térmica reduzida)

---

## 🔴 Testes Críticos Obrigatórios (Fase 0)

**Não pule estes testes. São bloqueadores para Fase 1.**

| Teste | Prazo | Critério | Status |
|---|---|---|---|
| **CFD / Arrasto** | Semana 1 | I ≤ 5,8 A @ 1800 RPM | 🔴 Crítico |
| **Termopar 10 min** | Semana 3 | T < 55 °C contínuos | 🔴 Crítico |
| **Validação corrente** | Semana 3 | I_real ≤ 5,8 A | 🔴 Crítico |
| Vibração (acelerômetro) | Semana 3 | Pico 30 Hz < 0,2 g | 🟡 Complementar |
| Junta (ciclo cíclico) | Semana 3 | Afrouxamento < 0,1 mm | 🟡 Complementar |

**Se CFD OU termopar falhar:** Fallback para 1500 RPM (75 Hz, flicker marginal)

---

## 📅 Cronograma Realista

```
SEMANA 1 (01–05/09)
├─ CAD v2.1 + Datum D ±0,2 mm
├─ CFD iniciado (3–5 dias)
└─ Impressão encomendada

SEMANA 2 (08–12/09)
├─ Peças prontas (18–24 h impressão)
├─ Montagem base + rotor
└─ Balanceamento estático/binário

SEMANA 3 (15–19/09) 🔴 TESTES CRÍTICOS
├─ Teste corrente (1800 RPM)
├─ Teste termopar (10 min)
├─ Teste vibração (acelerômetro)
└─ Teste junta (ciclo cíclico)

SEMANA 4 (22–26/09)
├─ Malha PI sintonizada (1800 RPM)
└─ Preparação Fase 1 (LEDs)

FASE 1 (29/09–...)
└─ Integração HD107S
```

**Total:** ~1 semana adicional vs v2.0 (testes em paralelo com impressão)

---

## 💡 Pontos-Chave para Sucesso

### ✅ Fazer

- [x] Ler SUMARIO-v2.1.md (decisão)
- [x] Ler TABELA-COMPARATIVA-v2-v2.1.md (números)
- [ ] Revisar Plano-de-Projeto-v2.1.md com equipe (45 min)
- [ ] **Iniciar CFD Semana 1** (bloqueador crítico)
- [ ] **Encomendador termopar K-type + acelerômetro** (R$ 30 total)
- [ ] Confirmar impressora com câmara fechada
- [ ] Confirmar ESC com rampa configurável (2–3 seg)

### ❌ Não Fazer

- Pular CFD; arrasto real pode invalidar corrente estimada
- Usar coxims diferentes em cada painel (usar mesmo lote, mesma posição mesa)
- Aceitar pesso > 35,5 g (rejeitar e reimprimir)
- Usar porca padrão nas juntas (risco de afrouxamento; usar porca nylon)
- Rodar a 1800 RPM sem rampa de partida ESC (travamento garantido)

---

## 🎓 Lições Aprendidas

### O que funcionou bem em v2.0

✓ Conceito cilíndrico (vs disco horizontal em Proposta)  
✓ Balanceamento em 2 planos (estático + binário)  
✓ Orçamento de massa e força centrífuga  
✓ Análise térmica de motor em carga  

### O que precisava de melhoria (agora em v2.1)

⚠️ Flicker em 60 Hz era perceptível → **eliminado com 90 Hz**  
⚠️ Tolerância de altura Δh ±1 mm era marginal → **reduzida para ±0,5 mm**  
⚠️ Testes críticos faltavam → **adicionados (CFD, termopar, vibração)**  

### Inovações em v2.1

🆕 Validação de arrasto por CFD (não estimativa)  
🆕 Teste térmico de 10 min (não cálculo)  
🆕 Validação dinâmica com acelerômetro  
🆕 Tolerâncias manufaturáveis (fabricação + CAD refinados)  

---

## 🔧 Requisitos de Equipamento

### Obrigatório

| Item | Custo | Tempo |
|---|---|---|
| Impressora 3D (câmara fechada) | ~R$ 5–10k | — |
| Filamento ABS | R$ 20–30/kg | — |
| Balança de precisão (0,1 g) | R$ 30–50 | — |
| Paquímetro digital | R$ 20–50 | — |
| Termopar K-type 1,5 mm | R$ 15–30 | Encomendar |
| Acelerômetro MPU6050 | R$ 10–20 | Encomendar |
| Osciloscópio/data logger | ~R$ 500 | Existente? |

### Software

| Ferramenta | Custo | Necessidade |
|---|---|---|
| CAD (FreeCAD/SolidWorks) | Livre/pago | Existente |
| CFD (OpenFOAM ou FLUENT) | Livre/pago | ⚠️ Crítico |
| Python + scipy (FFT) | Livre | Análise opcional |

---

## 📊 Sumário de Números

### Operação em 1800 RPM

| Parâmetro | Valor | Margem |
|---|---|---|
| Rotação | 1800 RPM | +50% vs 1200 |
| Taxa imagem | 90 Hz | Acima do limiar (~60 Hz) |
| Corrente motor | 5,5 A | 1,7× fator segurança |
| Temperatura motor | ~53,4 °C | 6,6 °C até limiar (60 °C) |
| Força centrífuga | 2,26 N/painel | 147× fator segurança parafuso |
| Deflexão painel | 3,5 mm | 1,7% da altura (aceitável) |
| Energia partida | 21,3 J | Rampa 2–3 seg obrigatória |

### Tolerâncias

| Parâmetro | Alvo | Aceitável | Rejeição |
|---|---|---|---|
| Massa painel | ≤ 35 g | ≤ 35,3 g | > 35,5 g |
| Datum D (altura) | 104 mm | ±0,3 mm (print) | > ±0,3 mm |
| Δh entre painéis | — | ±0,5 mm máx | > ±0,5 mm |

---

## 🚀 Próximos Passos

### Imediato (próximas 24 h)

1. Revisar SUMARIO-v2.1.md + TABELA-COMPARATIVA (20 min)
2. Reunião com equipe sobre viabilidade (30 min)
3. Decisão final: v2.1 (1800 RPM) ou fallback 1500 RPM
4. Se v2.1 aprovado: Iniciar Semana 1 (CFD + CAD)

### Semana 1 (01–05/09)

1. Finalizar CAD v2.1 (Datum D ±0,2 mm)
2. Iniciar CFD (ou comissionar teste empírico)
3. Encomendar equipamento (termopar, acelerômetro)
4. Enviar para impressão (3 painéis + aranha)

### Semana 2–3 (08–19/09)

1. Executar testes críticos (CFD, termopar, vibração, junta)
2. Finalizar balanceamento
3. Preparar para Fase 1 (LEDs)

---

## ❓ FAQ

### P: Por que 1800 RPM e não 1500 RPM ou 2000 RPM?

**R:** 1800 RPM é o equilibrio ideal:
- **1500 RPM:** 75 Hz imagem, flicker ainda percepível em visão periférica
- **1800 RPM:** 90 Hz imagem, flicker imperceptível ✓, margem térmica aceitável
- **2000 RPM:** 100 Hz imagem, mas corrente sobe para ~6 A+ (risco térmico alto)

### P: E se o teste termopar falhar?

**R:** Três opções:
1. **Recuar para 1500 RPM** (recomendado; sem delay)
2. Adicionar dissipador térmico (copper heat pipe; +2 dias)
3. Alisamento acetona mais agressivo (efeito marginal, não recomendado)

### P: CFD é realmente necessário?

**R:** SIM. Estimativa de arrasto têm 3× incerteza. CFD reduz para <10% erro. Se recusar CFD, margem térmica desaparece.

### P: Posso rodar a 1800 RPM com ESC "padrão"?

**R:** Não. ESC DEVE ter rampa de 2–3 seg configurável. Sem rampa → sobrecorrente na partida → travamento.

### P: Qual é o fallback se tudo falhar?

**R:** **Manter v2.0 a 1200 RPM.** Projeto ainda funciona; qualidade visual com flicker perceptível mas aceitável em uso casual. Sem risco.

---

## 📞 Contatos & Dúvidas

Para questões técnicas específicas, consulte:

- **Flicker / POV:** Seção 2.2 Plano-de-Projeto-v2.1.md
- **Térmica:** Seção 2.3 Plano-de-Projeto-v2.1.md + Fundamentacao-Teorica
- **Tolerâncias CAD:** Especificacao-CAD-v2.1.md
- **Testes:** CHECKLIST-Implementacao-v2.1.md
- **Cálculos:** TABELA-COMPARATIVA-v2-v2.1.md

---

## 📄 Versão & Histórico

| Versão | Data | Status | Notas |
|---|---|---|---|
| v2.0 | ~ago/26 | Baseline | 1200 RPM, 60 Hz, flicker perceptível |
| v2.1 | 31/ago/26 | **ATUAL** | 1800 RPM, 90 Hz, flicker eliminado |

**Próxima versão:** v3.0 (pós-validação Fase 1, possível otimização para 2000+ RPM com dissipador)

---

## ✅ Checklist de Conformidade

Antes de iniciar Fase 0:

- [x] Todos os 6 documentos v2.1 criados e revisados
- [x] Cálculos validados (Python + análise manual)
- [x] Comparação com v2.0 completa
- [x] Riscos identificados e mitigações propostas
- [x] Cronograma realista (Semanas 1–4)
- [x] Testes críticos definidos (CFD, termopar, vibração, junta)
- [x] Fallback scenarios planejados
- [ ] Aprovação executiva final (próximo passo do usuário)

---

**Data de Liberação:** 31/08/2026 17:00  
**Status de Implementação:** ✅ DOCUMENTAÇÃO COMPLETA, PRONTO PARA FASE 0

