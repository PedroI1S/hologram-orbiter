# Plano de ensaios — Hologram Orbiter v4.0

Cinco bloqueadores (A a E), precedidos pelo ensaio estático/impacto **C0**, mais
o ensaio do enlace de imagem (`05 §9`). **Atualizado em 14/11/2026 para o
Hologram Orbiter v4.0 (base suspensa em paralelogramo travável + aranha PETG
reforçada + motor AX-2810Q 750KV + ESC `Brake on stop = On`). Nenhum ensaio
físico com a montagem v4.0 foi executado ainda.**

> **Sobre a falha da v3.0 (27/10/2026):** a ruptura de um braço da aranha
> anterior na frenagem motivou o reforço da aranha (aleta em D + alma em asa),
> a troca da base pela suspensão em paralelogramo PETG com trava `4 + 4` e o
> novo motor `AX-2810Q 750KV`. Os ensaios abaixo começam do zero sobre a
> montagem v4.0; nunca reutilizar peças danificadas ou repetir o ensaio
> sem os quatro grampos da base fixa.

---

## Pré-requisito C0 — impacto e inspeção estática (antes de energizar)

Com a **base fixa grampeada pelas quatro abas** à bancada, palco montado com
as **8 hastes PETG de 1,5 mm**, motor `AX-2810Q`, chapa `R01` (alumínio 2 mm),
aranha reforçada e lastro representativo do rotor (ou rotor montado parado):

1. **Alinhamento das hastes:** verificar que o eixo do rotor está dentro de
   `≤ 0,5 mm` do centro do círculo das hastes e que o palco apoia livre sem
   tocar os batentes (`3,0 mm` radial; se houver EVA de `6 mm`, folga livre de
   `1,5 ± 0,1 mm` sem contato em repouso).
2. **Rigidez estática em inclinação:** puxar `10 N` laterais no CG do rotor com
   relógio comparador/laser — conferir inclinação `≤ 0,06°` (modelo prevê
   `0,044°`).
3. **Impacto com palco solto (MPU6050 no palco e na torre):**
   - **Translação do palco:** esperado `4,0–5,0 Hz` (modelo `4,38 Hz`, crítica
     `~263 RPM`).
   - **Giro (yaw) do palco:** esperado `12–15 Hz` (`~759 RPM`); fator de qualidade
     `Q ≤ 35` (com óleo 10 000 cSt na bandeja: `ζ ≈ 0,05` estimado).
   - **Flexão / balanço combinado (impacto no rotor, solto e travado):**
     esperado **≥ 95–100 Hz** (modelo combinado `89,3 Hz`, rocking `105,2 Hz`,
     travado `~100–138 Hz`). Se medir entre **80 e 95 Hz**, **limitar a
     rotação máxima de ensaio a 1600 RPM** para não excitar o modo pelo 3º
     harmônico (que cruza `~89 Hz` perto de `1786 RPM`). Abaixo de 80 Hz, não
     girar — investigar fixação ou reforçar.
4. **Trava `4 + 4`:** ao testar travado, apertar as 4 buchas + `M3 × 40` radiais
   e os `4 × M3 × 10` verticais por igual e **reapertar após 24 h** (fluência do
   PETG).

---

## Bloqueador A — potência e arrasto

**O que se verifica:** se o arrasto aerodinâmico real (incluindo o reforço em
aleta em D + alma em asa) bate com o estimado com o `AX-2810Q 750KV`.

**Método.** Rotor completo montado com lastro representativo e balanceado, sem
LEDs acesos. Subir em patamares de **600, 1000, 1400 e 1800 RPM** (2 min cada,
evitando estacionar entre `760` e `870 RPM`), lendo **tensão e corrente na fonte
de bancada**.

| `I_fase` (AX-2810Q) | `P_entrada` (`η=95%`) | `I_fonte` @ 10 V | `I_fonte` @ 12 V | `T_motor` prev. (`Rth=3,5`) | Nota |
|---:|---:|---:|---:|---:|---|
| 3,0 A | 10,6 W | 1,06 A | 0,88 A | 34,5 °C | |
| **3,62 A** | **13,1 W** | **1,31 A** | **1,09 A** | **37,8 °C** | melhor caso (`Cd_boss = 0,20`) |
| **4,04 A** | **14,81 W** | **1,48 A** | **1,23 A** | **40,3 °C** | ← **ponto de projeto** (`Cd_boss = 0,35`) |
| 4,99 A | 20,63 W | 2,06 A | 1,72 A | 47,0 °C | referência 2000 RPM (não liberado) |
| 5,5 A | 21,5 W | 2,15 A | 1,79 A | 51,3 °C | acima de 20 W |
| **8,0 A** | **36,11 W** | **3,61 A** | **3,01 A** | **77,9 °C** | **parar imediatamente (teto de fase)** |

*(Equações: `P_entrada = (0,012732·188,496·I + 0,225·I² + 0,7)/0,95` e
`T_motor = 25 + 3,5·(0,225·I² + 0,7)`. Nota: o modelo nominal não soma ~1 W
estimado das aletas em D dos braços; a leitura real da fonte inclui esse valor.)*

**Critério de aceite:** **`P_entrada ≤ 20 W`** a 1800 RPM em regime estável.
**Aborto:** `P_entrada > 30 W` em regime ou `T_motor ≥ 55 °C`.

---

## Bloqueador B — térmica em regime contínuo e fluência

**Instrumentação:** nunca prender termopar com fio na campânula girante do
`AX-2810Q`. Usar medição sem contato validada (emissividade/spot corrigidos
contra referência com motor parado) ou sensor embarcado qualificado.

**Método:** operar **10 min contínuos a 1800 RPM** registrando temperaturas a
cada 30 s; medir também o **crescimento radial da ponta do painel** antes e
após **1 h em regime** (fluência do ABS sob carga centrífuga e calor — somente
após liberar a seção/transferência de carga).

| Ponto | Limite |
|---|---|
| Motor `AX-2810Q` (método qualificado) | **`< 55 °C`** e curva estabilizando |
| Estrutura PETG próxima ao motor (flange / R01) | `< 60 °C` |
| Bateria LiFePO4 na baia (somente na repetição em **G4**) | `< 45 °C` |
| Crescimento da ponta do painel (após 1 h em regime) | **`< 0,5 mm`** |

---

## Bloqueador C — vibração, resposta da suspensão e balanceamento

**C1 — Varredura 0–1800 RPM (filmando as orelhas dos batentes + acelerometria):**

- **Subida 0 → 1800 RPM** em patamares (`600, 1000, 1400, 1800 RPM`, cruzando
  `200–400 RPM` rapidamente a `≥ 300 RPM/s` e sem estacionar em `760–870 RPM`).
- **Acompanhamento de amplitude:**
  - **Mesa (palco solto vs. travado a 1800 RPM):** redução de aceleração na mesa
    **`≥ 10×`** (modelo prevê `24–40×`).
  - **Orelhas dos batentes:** sem toque nos batentes acima de 600 RPM; giro
    (yaw) `≤ 0,3 mm` entre 760 e 870 RPM.
  - **Vibração na base/palco (pico FFT em 1× e 2×):** `1× ≤ 0,20 g` e
    `2× ≤ 0,10 g` sem crescimento em 10 min.

**Balanceamento em dois planos (antes de validar C1):**
1. **Estático:** pesar os três painéis em balança de **`0,01 g`** e casar em
   **`Δm ≤ 0,084 g`**.
2. **Dinâmico em dois planos:** usar referência fixa **1 pulso/volta** sincronizada
   com duas respostas independentes de vibração (Plano 1 = alívios inferiores do
   cubo `r = 17..36 mm`; Plano 2 = copos da tampa `r = 34 mm`). Manter critério
   conservador **`|U_1| + |U_2| ≤ 8,4 g·mm`** (ou recalcular formalmente após
   pesagem do rotor completo até 420 g).

---

## Bloqueador D — partida com o AX-2810Q e suspensão

**Particularidade da v4.0:** a suspensão tem translação crítica em **`~263 RPM`**
(`4,38 Hz`) e modo de giro em **`~759 RPM`**. Portanto:
- A partida precisa atravessar `200–400 RPM` a **`≥ 300 RPM/s`** (`≥ 50 µs/s` acima
  de `1200 µs`), mantendo o chute em torque conservador (`≤ 0,1 N·m` ou partir
  travado caso necessário).
- Alvo mínimo de regime **`≥ 1200 µs`** (evitar `1170 µs` ou alvos que
  estacionem na crítica ou em `760–870 RPM`).
- **ESC com `Brake on stop = On`** (gravado em 13/11/2026) para que a parada
  atravesse a crítica em `~1,5 s` sem bater nos batentes — **exige grampo ou
  resistor de descarga no barramento do ESC (`12,6–16,8 V`)**.

> **Nota sobre o firmware atual (`0.3.0` / `config.rs`):** o perfil linear
> padrão sobe de `1148 µs` ao alvo em 3 s (`≥ 3 s`), enquanto o overshoot
> opcional usa chute de `1400 µs` (que no modelo `AX-2810Q`, `R = 0,225 Ω`,
> prevê `16,4 A / 63,5 W` a 10 V e `19,6 A / 91,4 W / 1959 RPM` a 12 V). Antes
> do Bloqueador D com o rotor completo, **revisar os parâmetros de rampa/chute**
> na `firmware/controle-motor` e calibrar `CEILING_US` com tacômetro.

**Critérios de aceite:**
- **10 de 10 partidas** consecutivas do repouso até 1800 RPM sem perda de sincronismo;
- orelha do palco **não chega ao batente rígido (`3,0 mm`)** durante o chute;
- pico de potência na fonte na partida **`≤ 36,1 W`** (referência calculada para
  `8,0 A` de fase no AX-2810Q; `3,61 A @ 10 V`, `3,01 A @ 12 V`);
- rotação durante toda a partida **`≤ 1800 RPM`** (tacômetro);
- tensão no barramento do ESC **`≤ 16,8 V`** em todas as partidas e paradas.

---

## Bloqueador E — qualidade visual e enlace de imagem

Idêntico em critérios visuais (`90 Hz`, 180 colunas × 29 px, câmera 240 fps,
sacada ocular sem imagem dupla/tripla nem jitter > 1/4 de coluna `46 µs`), mas
beneficiado pela arquitetura **SPI Quad** da v4.0 (zero defasagem de cadeia
entre painéis e folga triplicada de tempo SPI por coluna). Incluir também o
ensaio do **enlace ESP-NOW** (`05 §9`):
1. **Bancada (rotor parado, índice simulado a 30 Hz no GPIO3):** atraso com
   rádio recebendo 180 × 29 a cada 5 s abaixo de **`46 µs`**.
2. **Alcance girando (1800 RPM, contenção em policarbonato, tampa fechada):**
   100 imagens seguidas recebidas com CRC válido.
3. **Visual em movimento:** repetir E com imagens enviadas pela ESP32 da base.

---

## Regras de segurança em ensaio de rota

- **Contenção integral obrigatória** (`27,6 J` no rotor; painel solto `7,9 J` a `18,9 m/s`). Usar policarbonato quando o enlace 2,4 GHz estiver ativo.
- **Chapa do motor em alumínio 2 mm (`Ø11`)** para qualquer giro acima de baixa rotação de bancada (réplica PLA `R01P` é apenas para checagem estática / baixa rotação sem carga de rotor completo).
- **Quatro abas grampeadas à mesa** sempre antes de energizar; verificar folga livre dos fios do motor (`laçada frouxa`) para não travar a suspensão.
- **Grampo/resistor de descarga conectado ao barramento do ESC** em todos os giros com `Brake on stop = On`.
- **Operação remota e óculos de proteção** sempre; nunca abrir a contenção antes da parada total observada.
