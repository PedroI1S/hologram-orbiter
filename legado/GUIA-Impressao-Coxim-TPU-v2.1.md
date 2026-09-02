# Guia Prático: Impressão de Coxim em TPU 95A

> Procedimento detalhado para impressão e validação de coxim de isolamento vibração (Peça 7) em TPU 95A, usando impressora 3D universitária com câmara fechada.
>
> **Versão:** v2.1 (Opção B — Impresso)  
> **Data:** 01/09/2026  
> **Aplicação:** Hologram Orbiter v2.1 (4 unidades)

---

## 1. Pré-requisitos

### Impressora 3D Obrigatória

| Requisito | Critério | Crítico? |
|---|---|---|
| **Câmara fechada** | Temperatura ambiente 35–40°C estável | ✅ SIM |
| **Mesa aquecida** | 60–80°C com controle PID (não manual) | ✅ SIM |
| **Hotend** | Ø 0,4 mm, material hardened ou TPU-específico | ✅ SIM |
| **Volume de impressão** | Mín. 60 × 60 × 50 mm | ⚠️ Recomendado |
| **Firmware** | Cálculo de fluxo calibrado para TPU | ⚠️ Recomendado |
| **Sensor de nível** | Auto-level de mesa (compensação Z) | ⚠️ Recomendado |

**Impressoras Conhecidas como Viáveis:**
- Creality CR-10S Pro (câmara opcional, hotend padrão)
- Anycubic i3 Mega-S (câmara upgradável)
- Prusa i3 MK3S+ (câmara fechada, firmware excelente)
- Ultimaker S5 (câmara integrada, software dedicado)

**Impressoras NÃO Recomendadas:**
- Ender 3 sem câmara (ventilação aberta)
- Máquinas sem controle de mesa aquecida
- Hotends padrão sem limpeza fácil (entupimento TPU)

---

## 2. Material: Seleção e Preparação

### Filamento TPU 95A

| Propriedade | Especificação |
|---|---|
| **Material** | TPU 95A Shore (poliuretano termoplástico) |
| **Diâmetro** | Ø 1,75 mm ±0,03 mm (padrão FDM) |
| **Fornecedores** | Ninjaflex, Flexfill 98A, ESUN e-TPU, Ultimaker TPU-95A |
| **Cor** | Qualquer (preferencialmente preto para durabilidade) |
| **Quantidade necessária** | ~10–20 g por lote de 4 coxims (bobina mínima ~0,5 kg) |

**Validação do Filamento:**

1. Inspecionar visualmente: sem fraturas, sem ressecamento
2. Testar flexibilidade: puxar 10 cm lentamente — deve voltar a forma original
3. Armazenar em local seco (dessecante) antes de imprimir
4. Se armazenado > 6 meses, secar em estufa 60°C / 4 h antes de usar

---

## 3. Configuração da Impressora

### 3.1 Preparação da Câmara (CRÍTICO)

| Passo | Detalhe |
|---|---|
| 1. Fechar câmara completamente | Sem fendas; vedação com fita de silicone se necessário |
| 2. Pré-aquecer câmara | Ligar impressora 30 min antes de começar; atingir 35–40°C |
| 3. Verificar sensor de temperatura | Termômetro independente na câmara (não confiar só no sensor da impressora) |
| 4. Garantir circulação ar lenta | Ventilador mínimo (15–20%) se necessário evitar pontos frios |
| 5. Teste: nenhuma condensação | Se houver gota, câmara muito quente ou úmida |

**Resultado esperado:** Temperatura câmara 35–40°C ±2°C, relativamente seca (não hidratada).

---

### 3.2 Calibração da Mesa

| Passo | Detalhe |
|---|---|
| 1. Aquecer mesa a 70°C | Deixar estabilizar 5 min |
| 2. Auto-level (se disponível) | Executar rotina automática de nivelamento |
| 3. Validar folga nozzle-mesa | Papel de teste em 4 pontos + centro |
| 4. Folga ideal para TPU | 0,15 mm (ligeiramente mais frio que ABS) |
| 5. Limpar mesa | Isopropanol para remover óleos e resíduos anteriores |

**Verificação final:** Nozzle deve deixar marca leve no papel, sem rasgar.

---

### 3.3 Preparação do Hotend

| Passo | Detalhe |
|---|---|
| 1. Limpar hotend | Desmontar e limpar resíduos TPU antigo (se houver) com pincel e álcool |
| 2. Verificar nozzle | Sem entupimento; trocar se danificado (Ø 0,4 mm) |
| 3. Verificar PTFE (tubo bowden) | Se desgastado, trocar (TPU danifica PTFE mais rápido que ABS) |
| 4. Aplicar graxa de silicone | Pequena quantidade na entrada do hotend (facilita fluxo TPU) |
| 5. Pré-aquecer hotend a 240°C | Deixar estabilizar 10 min antes de extrude |

**Teste de fluxo:** Extrude 10 cm de filamento manualmente; deve sair suave, sem bolhas.

---

## 4. Configuração de Impressão

### 4.1 Parâmetros CAD (Peça 7 — Coxim)

**Modelo:**
- Cilindro Ø 16 mm × 8 mm altura
- Furo passante Ø 3,2 mm, axial
- Sem suportes (se possível)

**Posição na mesa:**
- Deitado (altura Z = 8 mm)
- Eixo cilindro perpendicular a eixo mesa (não paralelo)
- Distância entre 4 coxims: mín. 20 mm
- Deixar espaço mínimo de 10 mm das laterais

---

### 4.2 Perfil de Impressão (Obrigatório Seguir Exatamente)

| Parâmetro | Valor | Comentário |
|---|---|---|
| **Temperatura Hotend** | 230–240°C | 230°C prudente; 240°C se fluxo muito viscoso |
| **Temperatura Mesa** | 60–80°C | 70°C é padrão; aumentar até 80°C se delaminação |
| **Velocidade Impressão** | 15–20 mm/s | **NÃO EXCEDER 20 mm/s** — TPU é frágil |
| **Velocidade Travel** | 30–40 mm/s | Sem aceleração brusca; jerk baixo |
| **Velocidade Primeira Camada** | 10 mm/s | Mais lento para aderência |
| **Jerk (aceleração)** | 5–10 mm/s | Mínimo possível (suavidade crítica) |
| **Retração** | 2 mm @ 20 mm/s | Muito curta; TPU se espica com retrações grandes |
| **Infill** | 100% sólido | NÃO usar 30% giroide — precisa de densidade |
| **Perímetros** | 4–5 | Resistência mecânica |
| **Altura Camada** | 0,2 mm | Padrão; 0,15 mm se precisar precisão |
| **Ventilador Ar-frio** | DESLIGADO | TPU precisa resfriar lentamente (não com ar) |
| **Ventilador Câmara** | Baixo (15%) | Apenas para circulação, não resfriamento |

**Arquivo Gcode (Cura/PrusaSlicer):**

```
; Perfil TPU 95A — Coxim Hologram
M140 S70       ; Mesa 70°C
M109 S240      ; Hotend 240°C
G28            ; Home
G29            ; Auto-level (se disponível)
G0 Z0.15       ; Primeira camada
; ...
G1 F1200       ; Velocidade impressão (20 mm/s) = 1200 mm/min
G1 F600        ; Velocidade travel (10 mm/s)
; ...
M104 S0        ; Desligar hotend ao fim
M140 S0        ; Desligar mesa
```

---

### 4.3 Slice e Preparação do Arquivo

**Software:** Cura (recomendado para TPU) ou PrusaSlicer

**Passos:**

1. Importar arquivo CAD (coxim.stl)
2. Criar 4 instâncias (para 4 coxims) com distância 20 mm entre centros
3. Selecionar perfil TPU95A (ou criar manualmente com tabela acima)
4. Visualizar preview: verificar que não há suportes desnecessários
5. Estimar tempo: deve ser ~30–45 min para 4 coxims
6. Exportar Gcode para SD

---

## 5. Procedimento de Impressão

### 5.1 Pré-impressão (30 min antes)

| Ação | Tempo |
|---|---|
| 1. Ligar impressora | t = -30 min |
| 2. Carregar filamento TPU na bobina | t = -25 min |
| 3. Aquecer câmara a 35–40°C | t = -20 min (deixar estabilizar) |
| 4. Aquecer mesa a 70°C | t = -10 min |
| 5. Aquecer hotend a 240°C | t = -5 min |
| 6. Nivelar mesa (auto ou manual) | t = -2 min |
| 7. Iniciar impressão | t = 0 |

### 5.2 Monitoramento (Durante Impressão)

**Primeiras 5 linhas (camada 1):**
- Observar aderência na mesa
- Nozzle deve deixar linha clara (não quebrada)
- Se não aderir: aumentar temperatura mesa em 5°C e re-tentar

**Camadas 2–5 (estabilização):**
- Verificar que não há bolhas ou vazios
- Filamento deve sair suave, sem hesitações
- Se entupimento (som de clique do extrusor): pausar e limpar hotend

**Resto da impressão:**
- Deixar rodar sem intervenção
- Não abrir câmara (mantém temperatura)
- Se necessário pausar, deixar câmara quente

**Tempo total:** ~40 min para 4 coxims

---

### 5.3 Pós-impressão (Imediato)

| Ação | Detalhe |
|---|---|
| 1. Desligar hotend e mesa | Deixar câmara em 25°C ambiente |
| 2. Remover peça após resfriamento completo | ~10 min |
| 3. Remover suportes (se houver) | TPU é frágil; usar pinça cuidadosa |
| 4. Limpeza leve | Álcool isopropílico (não acetona — enrijece) |
| 5. Deixar curar 24–48 h @ 25°C | **IMPORTANTE:** TPU precisa de relaxação após impressão |

---

## 6. Validação Pós-Impressão

### 6.1 Inspeção Visual

- [ ] Nenhuma bolha ou furo visível
- [ ] Superfície lisa (sem linhas grossas)
- [ ] Furo passante aberto (Ø 3,2 mm)
- [ ] Nenhuma deformação ou empenamento

### 6.2 Testes Críticos (OBRIGATÓRIO)

**Teste 1: Dureza Shore A**

- Equipamento: Durômetro Shore A
- Procedimento: Medir em 3 pontos do coxim
- Média esperada: 92–98A (±3 aceitável)
- ❌ Rejeitar se: < 92A ou > 98A

**Teste 2: Dimensionalidade**

- Equipamento: Paquímetro digital (0,01 mm precisão)
- **Ø Cilindro:** 6 medições (ao redor) — média esperada 16 ±0,4 mm
- **Altura:** 3 medições (3 posições) — média esperada 8 ±0,4 mm
- **Furo Ø:** Teste com broca Ø 3,2 mm (deve encaixar com folga leve)
- ❌ Rejeitar se: Ø > 16,4 mm ou < 15,6 mm; h > 8,4 ou < 7,6 mm

**Teste 3: Deformação Permanente**

- Procedimento: 
  1. Aplicar pressão manual de ~2 N por 10 s no topo do coxim
  2. Soltar
  3. Medir altura após 30 s de repouso
- Resultado esperado: Volta ≥ 80% da altura original
- ❌ Rejeitar se: Deformação permanente > 5% (altura < 7,6 mm)

**Teste 4: Damping Ratio ζ (Crítico)**

- Equipamento: Suporte temporário, massa de teste 200 g, cronômetro
- Procedimento:
  1. Montar 4 coxims sob suporte (em X, espaçados ~50 mm)
  2. Colocar massa 200 g no centro
  3. Provocar deflexão vertical ~10 mm (puxar para baixo)
  4. Soltar abruptamente
  5. Contar ciclos até oscilação cair para 50% da amplitude inicial
  6. Se N = 3 ciclos → ζ ≈ 0,11 ✅
  7. Se N > 5 ciclos → ζ < 0,08 ❌ (amortecimento ruim)

- ❌ Rejeitar se: ζ < 0,08 em qualquer um dos 4 coxims

**Teste 5: Comparação de Massa**

- Equipamento: Balança de precisão (0,1 g)
- Procedimento: Pesar cada um dos 4 coxims
- Resultado esperado: Δm < 0,5 g entre unidades (all 4 ~ 18–22 g)
- ❌ Rejeitar se: Δm ≥ 2 g (variação excessiva → diferentes ζ)

---

## 7. Critérios de Aceite / Rejeição

| Teste | Critério Aceite | Ação se Falhar |
|---|---|---|
| Dureza Shore A | 92–98A (todos 4) | Rejeitar lote; reimprender com hotend +5°C |
| Dimensional Ø | 16 ±0,4 mm (média 4) | Rejeitar lote; verificar calibração Z |
| Dimensional h | 8 ±0,4 mm (média 4) | Rejeitar lote; aumentar infill % se baixa |
| Furo Ø | 3,2 ±0,2 mm (pass/fail) | Rejeitar lote; aumentar diâmetro no CAD +0,1 mm |
| Deformação perm. | < 5% para todos 4 | Rejeitar lote; possível TPU foi ressecado |
| Damping ζ | ≥ 0,08 (todos 4) | Rejeitar lote; adicionar massa ao lote ou + coxins |
| Δm entre 4 | < 2 g | Rejeitar lote; variação térmica alta |

**Decisão Final:**
- ✅ Se TODOS testes passam: APROVAR lote → Usar em v2.1
- ❌ Se qualquer teste falha: REJEITAR lote → Reimprender OU fallback Opção A (comprado)
- ❌ Se 2ª rejeição: Desistir de impressão; comprar TPU 95A comercial

---

## 8. Troubleshooting Comum

| Problema | Causa | Solução |
|---|---|---|
| **Não adere à mesa** | Mesa muito fria ou suja | +5°C na mesa; limpar com isopropanol |
| **Filamento volta (retrações)** | Velocidade retração muito alta | Reduzir retração para 1–2 mm |
| **Borbulhas na impressão** | Temperatura hotend muito baixa | +5°C (até máx 245°C) |
| **Entupimento hotend** | Resíduo TPU anteriormente | Desmontar e limpar hotend completamente |
| **Deformação após impressão** | TPU ainda mole, não curado | Deixar 48 h curado; não forçar montagem |
| **Dureza baixa** | Câmara aquecida demais | Reduzir para 35°C; adicionar ventilação leve |
| **Dureza alta** | Câmara muito fria | +3°C até 38°C |
| **Peça pega-se à mesa** | Aderência excessiva | Reduzir temperatura mesa para 65°C |

---

## 9. Comparação: Impresso vs. Comercial

| Aspecto | Impresso | Comercial |
|---|---|---|
| **Tempo** | 3 h (impressão) + validação | 1–3 dias entrega |
| **Custo** | R$2–5 (filamento) + 3 h tempo | R$15/unidade (~R$60) |
| **Dureza** | 92–98A (variável, validar) | 95A ±2 (certificado) |
| **Dimensional** | ±0,4 mm (tolerância larga) | ±0,2 mm (preciso) |
| **Damping ζ** | 0,08–0,12 (variável, testar) | 0,10–0,12 (consistente) |
| **Relaxação** | Maior nos primeiros 7 dias | Mínima (pré-estabilizado) |
| **Complexidade** | Requer validação completa | Pronto para usar |

**Recomendação:** Se impressora universitária tem câmara fechada e hotend bom → **Opção B (impresso) viável e rápida**. Caso contrário → **Opção A (comprado) mais seguro**.

---

## 10. Checklist Implementação

### Pré-Impressão
- [ ] Impressora qualificada (câmara fechada ✅, mesa PID ✅, hotend ✅)
- [ ] Filamento TPU 95A disponível (~20 g)
- [ ] Arquivo CAD (4 coxims) sliced com perfil correto
- [ ] Câmara testada em 35–40°C (termômetro independente)
- [ ] Hotend limpo e nozzle novo Ø 0,4 mm

### Durante Impressão
- [ ] Câmara mantida 35–40°C (sem abrir)
- [ ] Primeira camada adere bem
- [ ] Nenhum entupimento detectado
- [ ] Impressão concluída sem erros

### Pós-Impressão
- [ ] Resfriamento completo em câmara
- [ ] Cura 24–48 h @ 25°C antes de usar
- [ ] Testes 1–5 executados: ✅ Dureza, ✅ Dimensional, ✅ Deformação, ✅ ζ, ✅ Δm
- [ ] **APROVADO ou REJEITADO** (documentar resultado)

---

## 11. Referências & Contato

**Documentação Relacionada:**
- Especificacao-CAD-v2.1.md (Seção 7 — Peça 8: Coxim)
- Revisao-Tecnica-e-Ajustes.md (bloqueador #3)

**Fornecedores de Filamento TPU 95A:**
- Ninjaflex (EUA, mas venda internacional)
- Flexfill (EU, Brasil via distribuidores)
- ESUN e-TPU (China, mas comum em Brasil)
- Ultimaker TPU-95A (premium, mas disponível)

---

**Data:** 01/09/2026  
**Versão:** 1.0  
**Status:** ✅ Pronto para implementação  
**Autor:** Equipe Hologram Orbiter v2.1
