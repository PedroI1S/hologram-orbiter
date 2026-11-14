# Relatório de validação CAD — v4.0.0

Gerado por CAD/generate.py na mesma execução de geometry_report.json e FISICA.json.
**PROVISÓRIO: não libera operação nem fabricação definitiva dos painéis.**

## Geometria

Critérios: 69/69. Ver ACEITACAO.md para requisitos e cobertura.
A validação dos STL exportados aparece em stl_validation.json; o build só publica se ela também passar.

| Peça | Massa CAD (g) | Dimensões (mm) | Triângulos |
|---|---:|---|---:|
| spider | 116.53 | [148.763, 171.777, 53.0] | 11798 |
| panel_each | 31.94 | [30.0, 50.0, 208.0] | 3988 |
| lid | 12.94 | [84.0, 84.0, 5.0] | 6548 |
| base_tower | 494.4 | [225.4, 225.4, 145.0] | 7924 |
| magnet_bracket | 2.55 | [38.926, 31.233, 26.5] | 1578 |
| base_frame | 425.75 | [280.0, 280.0, 79.0] | 9974 |
| flexure_macia_1p5 | 1.33 | [4.0, 12.0, 75.0] | 280 |
| lock_spacer | 1.45 | [12.0, 12.0, 24.8] | 512 |
| oil_cup | 30.92 | [231.312, 231.312, 9.5] | 2890 |
| joint_coupon | 10.07 | [58.0, 24.0, 12.0] | 60 |
| led_coupon | 3.53 | [8.0, 30.0, 30.0] | 154 |
| motor_plate_reference_aluminium | 18.48 | [60.0, 60.0, 2.0] | 3520 |

## Física

Iyy da seção = 589.8846 mm⁴; centroide x = -0.53095 mm.
As integrais são comparadas com três cortes da malha. Propriedades FDM e engaste não certificados.

| Massa usada | L (mm) | E (MPa) | Deflexão (mm) | Tensão máxima (MPa) |
|---:|---:|---:|---:|---:|
| 44.5 | 86.0 | 2300.0 | 3.832 | 21.724 |
| 44.5 | 86.0 | 2000.0 | 4.407 | 21.724 |
| 44.5 | 99.0 | 2000.0 | 7.739 | 28.788 |
| 45.0 | 86.0 | 2300.0 | 3.875 | 21.968 |
| 45.0 | 86.0 | 2000.0 | 4.457 | 21.968 |
| 45.0 | 99.0 | 2000.0 | 7.826 | 29.111 |

Folga radial calculada com o teto de massa: 21.17 mm.
Carga uniforme simplificada: não representa certificação de resistência ou fluência.

## Acionamento

Regime: 4.04 A de fase, 14.81 W na fonte (1.48 A a 10 V / 1.23 A a 12 V).
Partida com chute (05 §8.2): 1148→1400 µs em 3 s, chute de 2 s, descida a 42 µs/s até 1200 µs; fonte em 10–12 V com limite de 30 A.
Teto de 8 A de fase: 36.11 W na fonte (3.61 A a 10 V / 3.01 A a 12 V), 101.9 mN·m.
- Fonte em 10 V: parado no chute, 16.37 A de fase e 63.5 W / 6.35 A na fonte, 208.5 mN·m; pico de 1680 RPM a 1355 µs; fase até 16.37 A e fonte até 63.5 W; 514 RPM no alvo. **No modelo, passa do teto de fase e passa dos 36.11 W do bloqueador D.**
- Fonte em 12 V: parado no chute, 19.65 A de fase e 91.4 W / 7.62 A na fonte, 250.2 mN·m; pico de 1959 RPM a 1358 µs; fase até 19.65 A e fonte até 91.4 W; 607 RPM no alvo. **No modelo, passa do teto de fase e passa dos 36.11 W do bloqueador D e passa de 1800 RPM.**
Aperto do eixo (μ 0.3, r 7 mm, pré-carga estimada 1250 N): 24.5 N em regime, 48.5 N (25.8×) no teto de fase, 99.3 N (12.6×) no pico da partida a 10 V, 119.1 N (10.5×) no pico da partida a 12 V.
Modelo médio, sem o Startup Power do ESC nem a resistência da fonte e dos cabos; não é medição: conferir RPM, corrente e tensão reais no bloqueador D.

## Montagem e orçamento nominal

Interseções da eletrônica com aranha: [{'component': 'interface', 'intersection_mm3': 0.0}, {'component': 'esp32c3', 'intersection_mm3': 0.0}, {'component': 'buck', 'intersection_mm3': 0.0}, {'component': 'capacitor', 'intersection_mm3': 0.0}, {'component': 'placa_principal', 'intersection_mm3': 0.0}].
Contrapesos nominais: [{'pocket_center_deg': 180.0, 'mass_g': 2.06, 'radius_mm': 33.0}, {'pocket_center_deg': 300.0, 'mass_g': 0.99, 'radius_mm': 33.0}].
Subtotal do rotor: 352.14 g, limite 420 g.
Ferragens por painel (4 g) e chicote SPI Quad de quatro condutores (5 V, GND, CLK, DATA) precisam ser pesados e reconciliados antes de declarar massa final do rotor (teto provisorio 420 g).

| Referência global | Z (mm) |
|---|---:|
| Datum B, topo do cubo | 186.0 |
| Trilhos/fundo da bateria | 196.0 |
| Topo da bateria | 213.0 |
| Ponta do eixo | 195.0 |

## Ainda não verificado

Resistência e fluência do painel e aranha impressos, caminho de carga, massas/chicotes reais, instrumento de fase e térmica, dropout do buck, polaridade/entreferro reais, ensaio de impacto da suspensão e contenção. Ver ../../06-PENDENCIAS-ABERTAS-v4.0.md.
