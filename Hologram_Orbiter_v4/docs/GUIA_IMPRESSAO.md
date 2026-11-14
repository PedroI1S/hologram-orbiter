# Guia de impressão — Hologram Orbiter v4.0

Bico `0,4 mm`, camada `0,2 mm`, câmara fechada recomendada. Mesa de
`300 × 300 mm`. **Não altere a escala nem "repare" os STLs no fatiador:** todos
passam por validação topológica, orientação positiva e enrolamento por raios;
qualquer cota muda em `CAD/parameters.json`.

**Materiais na v4.0:**
- **PETG (`1,27 g/cm³`)** para toda a estrutura (aranha `01`, tampa `03`, base
  fixa `04`, palco/torre `05`, suporte do ímã `06`, hastes `08`, buchas `09` e
  bandeja `10`).
- **ABS (`1,04 g/cm³`)** para os três painéis (`02`) e cupons (`C01`, `C02`).
- **PLA (`100 % maciço`)** apenas para as peças provisórias de bancada (`R01P_*`),
  até cortar a chapa `R01` em alumínio `2 mm` e adquirir a arruela `DIN 9021 M4`.

> **Lote definitivo dos painéis e operação em rotação não liberados:** imprimir
> primeiro os cupons, as peças da suspensão para o **ensaio de impacto `C0`**, e
> calibrar massas/folgas reais antes de liberar ensaios dinâmicos.

---

## Sequência sugerida

1. **`C01_cupom_junta.stl` e `C02_cupom_canal_LED.stl` (ABS):** conferir encaixe
   espiga `11 × 6` × socket `11,2 × 6,2`, ponte de `12,4 mm` do piso de `0,8 mm`
   sob o canal da fita `HD107S` e abertura do bolso de fios `8 × 3,5 mm`. Ajustar
   `quality.joint_xy_clearance_each_side` se necessário.
2. **Base suspensa para ensaio `C0` (PETG):**
   - `04_base_fixa_PETG_imprimir_invertida.stl` (**inverter 180° ou usar já
     orientada** — o STL já sai invertido com o anel superior na mesa, verificar
     no fatiador!).
   - `05_palco_torre_PETG.stl`
   - `08_hastes_flexiveis_macia_1p5_8x.stl` (imprimir **deitadas**, 100 % maciço)
   - `09_buchas_trava_4x.stl` e `10_bandeja_amortecedor.stl`
3. **Conjunto rotor e motor:**
   - `01_aranha_PETG.stl`, `03_tampa_baia_PETG.stl`, `06_suporte_ima_PETG.stl`
   - `R01P_suporte_motor_PLA_provisorio.stl` e
     `R01P_arruela_eixo_M4_PLA_provisoria.stl` (provisórios para bancada)
   - `02_painel_LED_ABS_3x_mesma_mesa.stl` (pesar os três: `Δm ≤ 0,084 g`).

---

## Orientação e suportes por peça

| Peça | Material | Orientação no STL | Suporte necessário |
|---|:---:|---|---|
| `01_aranha_PETG.stl` | PETG | plana, face inferior do cubo na mesa (`Z = −6` deslocado para `Z = 0`) | **Sim, sob os braços** (`Z = 6` acima do fundo, `r ≈ 52..96 mm`, árvore com `0,2 mm` de folga). Aleta em D, alma inferior em asa invertida e cunha de 45°, pilares de `6 mm`, guia do buck, cerca do capacitor e prateleira `Z = 28` não precisam de suporte interno na baia (mísulas da prateleira a 45°). |
| `02_painel_LED_ABS_*` | ABS | deitado, `208 mm` em X, canal do LED contra a mesa | **Sim, em duas regiões:** quebra-fácil na fuga da lâmina (`73°`, `~2100 mm²`) e árvore dentro da casca na cauda da carenagem (`58–65°`, `1873 mm²`). Bolsos das porcas imprimem sem suporte. |
| `03_tampa_baia_PETG.stl` | PETG | plana, pele na mesa, 6 copos para cima | Nenhum. |
| `04_base_fixa_PETG_imprimir_invertida.stl` | PETG | **já exportada invertida:** anel superior (`Z = 79` global) apoiado na mesa; pista `Ø280` e abas no topo | **Nenhum.** A casca cônica sobe a ~45° e as mãos-francesas das 4 abas são a 45°. Com brim de `8 mm` ocupa **`296 × 296 mm`** (cabe justo na mesa `300 × 300`). |
| `05_palco_torre_PETG.stl` | PETG | disco do palco na mesa (`Z = 4` → `0`), torre vertical | **Sim, sob a flange superior (`Z = 141`, anel `r 16–30`, 90°):** árvore apoiada no disco do palco/aletas até a face inferior da flange. Ganchos de cabo sobem a 45° em X/Y sem suporte; verificar folga das 4 pás em L invertido do amortecedor. |
| `06_suporte_ima_PETG.stl` | PETG | arco na mesa, poste para cima (`26,5 mm`) | Nenhum. |
| `08_hastes_flexiveis_macia_1p5_8x.stl` | PETG | **deitadas** na mesa (blocos e haste de `1,5 × 1,5 mm` na horizontal) | Nenhum. **Crítico:** fatiar de forma que os perímetros corram **longitudinalmente** ao longo das hastes (`100 %` preenchimento / 4+ perímetros). |
| `09_buchas_trava_4x.stl` | PETG | em pé sobre a flange `Ø12 × 2 mm` | Nenhum (`100 %` maciço). |
| `10_bandeja_amortecedor.stl` | PETG | fundo da bandeja na mesa, cubas abertas para cima | Nenhum. Se for testar com óleo de silicone `10 000 cSt`, garantir estanqueidade das paredes de `1,6 mm` (sobreposição de perímetros / temperatura PETG adequada). |
| `C01_cupom_junta.stl` | ABS | como exportado | Nenhum. |
| `C02_cupom_canal_LED.stl` | ABS | canal contra a mesa (igual ao painel) | **Sim, sob a fuga** (`73°`). |
| `R01P_*` (provisórios) | PLA | planos na mesa | Nenhum (**`100 %` maciço**, nunca usar para giro com carga a alta RPM). |

---

## Perfis sugeridos

| Parâmetro | Painéis (`02`) | Aranha (`01`) | Tampa (`03`) | Base fixa (`04`) e Palco (`05`) | Hastes (`08`) e Buchas (`09`) | Suporte ímã (`06`) e Bandeja (`10`) |
|---|---:|---:|---:|---:|---:|---:|
| Material | ABS | PETG | PETG | PETG | PETG | PETG |
| Perímetros | 3 | 4 | 3 | 4 | **4+ (todo preenchido)** | 4 |
| Infill | 35 % giroide | 40 % giroide | 30 % | 35–40 % giroide | **100 % longitudinal** | 100 % (`06`) / 40 % (`10`) |
| Topo / Base | 5 | 5 | 4 | 5 | — | 5 |
| Brim | 5 mm | 5 mm | — | **8 mm** na base fixa (`296×296`); 5 mm no palco | 4 mm (orelhas de brim ajudam) | 3 mm |

**Atenção ao furo `Ø6` do cubo (`01`):** imprimir sem compensação agressiva de
expansão de furo. Se ficar apertado para a **bucha `Ø6 mm`** do `AX-2810Q`,
alargar cuidadosamente com broca/alargador de `6,0 mm`; **nunca folgar além da
bucha**, pois desloca o centro de massa de todo o rotor.

---

## Ferragens, chapa e critérios mínimos pós-impressão

- **Chapa `R01`:** alumínio `2 mm` cortado por
  `fabricacao/R01_suporte_motor_60x60_aluminio_2mm.dxf`/`.svg` (furos em cruz
  `16/19`, alívio central **`Ø11`**). `R01P` PLA serve apenas para montagem de
  bancada / baixa rotação sem rotor completo.
- **Eixo do rotor:** bucha `Ø6` + **arruela `DIN 9021 M4` (`12 × 4,3 × 1,0 mm`)**
  + **porca autotravante `M4 DIN 985`** a `1,0 N·m`.
- **Paralelogramo:** `16 × M3 × 10` + porcas M3 nas 8 hastes; para travar em
  modo rígido, `4 × M3 × 40` + porcas nas buchas `09` e `4 × M3 × 10` verticais
  nos batentes (reapertar 24 h após montar PETG).
- **Suporte do ímã:** `2 × M4 × 20` sob a aba (`0°` e `90°`), `2 × M4 × 16` nos
  demais furos da flange; conferir entreferro real de `2–3 mm`.
- **Painéis:** massa nua CAD `≈ 31,9 g`; manter `Δm ≤ 0,084 g` montados,
  `Datum D = 104 ± 0,2 mm` e passar um parafuso `M3` livre por cada torre antes
  de montar.
- **Paralelogramo impresso:** conferir ausência de empeno na base fixa (`≤ 0,2 mm`),
  perpendicularidade da torre (`≤ 1°`), curso livre até `3,0 mm` por eixo nos 4
  batentes sem enroscar e encaixe livre da bandeja `10` nos rasgos.

Nunca ensaiar sem contenção física, base grampeada pelas 4 abas, grampo no
barramento do ESC e acionamento remoto.
