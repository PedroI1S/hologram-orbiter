# Relatório de validação CAD — v3.0.5

Gerado por CAD/generate.py na mesma execução de geometry_report.json e FISICA.json.
**PROVISÓRIO: não libera operação nem fabricação definitiva dos painéis.**

## Geometria

Critérios: 59/59. Ver ACEITACAO.md para requisitos e cobertura.
A validação dos STL exportados aparece em stl_validation.json; o build só publica se ela também passar.

| Peça | Massa CAD (g) | Dimensões (mm) | Triângulos |
|---|---:|---|---:|
| spider | 70.88 | [148.763, 171.777, 35.0] | 10988 |
| panel_each | 31.94 | [30.0, 50.0, 208.0] | 3988 |
| lid | 10.12 | [82.0, 82.0, 5.0] | 6538 |
| base_tower | 319.8 | [280.0, 280.0, 154.0] | 8082 |
| magnet_bracket | 1.81 | [38.701, 30.008, 21.5] | 1736 |
| joint_coupon | 10.07 | [58.0, 24.0, 12.0] | 60 |
| led_coupon | 3.53 | [8.0, 30.0, 30.0] | 154 |
| motor_plate_reference_aluminium | 18.72 | [60.0, 60.0, 2.0] | 3512 |

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

Regime: 4.95 A de fase, 16.63 W na fonte (1.66 A a 10 V / 1.39 A a 12 V).
Partida com chute (05 §8.2): 1148→1400 µs em 3 s, chute de 2 s, descida a 42 µs/s até 1200 µs; fonte em 10–12 V com limite de 30 A.
Teto de 8 A de fase: 32.10 W na fonte (3.21 A a 10 V / 2.68 A a 12 V), 83.0 mN·m.
- Fonte em 10 V: parado no chute, 16.67 A de fase e 64.7 W / 6.47 A na fonte, 173.0 mN·m; pico de 1692 RPM a 1340 µs; fase até 16.67 A e fonte até 64.7 W; 591 RPM no alvo. **No modelo, passa do teto de fase e passa dos 32.10 W do bloqueador D.**
- Fonte em 12 V: parado no chute, 20.00 A de fase e 93.1 W / 7.76 A na fonte, 207.6 mN·m; pico de 1964 RPM a 1344 µs; fase até 20.00 A e fonte até 93.1 W; 691 RPM no alvo. **No modelo, passa do teto de fase e passa dos 32.10 W do bloqueador D e passa de 1800 RPM.**
Aperto do eixo (μ 0.3, r 7 mm, pré-carga estimada 500 N): 24.5 N em regime, 39.5 N (12.6×) no teto de fase, 82.4 N (6.1×) no pico da partida a 10 V, 98.9 N (5.1×) no pico da partida a 12 V.
Modelo médio, sem o Startup Power do ESC nem a resistência da fonte e dos cabos; não é medição: conferir RPM, corrente e tensão reais no bloqueador D.

## Montagem e orçamento nominal

Interseções da eletrônica com aranha: [{'component': 'interface', 'intersection_mm3': 0.0}, {'component': 'esp32c3', 'intersection_mm3': 0.0}, {'component': 'buck', 'intersection_mm3': 0.0}, {'component': 'capacitor', 'intersection_mm3': 0.0}].
Contrapesos nominais: [{'pocket_center_deg': 180.0, 'mass_g': 2.19, 'radius_mm': 33.0}, {'pocket_center_deg': 300.0, 'mass_g': 0.87, 'radius_mm': 33.0}].
Subtotal do rotor: 278.68 g, limite 280 g.
Ferragens por painel4g permanecem estimativa anterior. Chicote de seis condutores precisa ser pesado e reconciliado com estas ferragens antes de declarar massa total; o subtotal nominal nao garante o teto280g.

| Referência global | Z (mm) |
|---|---:|
| Datum B, topo do cubo | 186.0 |
| Trilhos/fundo da bateria | 195.0 |
| Topo da bateria | 212.0 |
| Ponta do eixo | 194.0 |

## Ainda não verificado

Resistência e fluência do painel impresso, caminho de carga, massas/chicotes reais, instrumento de fase e térmica, dropout do buck, polaridade/entreferro reais e contenção. Ver 06-PENDENCIAS-ABERTAS-v3.0.md.
