# Configuração do ESC para o AX-2810Q 750KV — plano de 13/11/2026

Gravado em 13/11 — ver `registro.md`. Este arquivo é o plano;
releitura e hashes em `verificacao-gravacao.json`.

## Onde foi feita a configuração anterior

Neste Mac. O log do ESC Configurator de 19/10 registra "Chrome on Mac OS"; o
Arduino Uno R3 (passthrough BLHeli, identifica-se como BTFL 4.3.0 / ARDU) estava
em `/dev/cu.usbserial-10` (16 e 19/10) e em `/dev/cu.usbmodem101` (30/10). A
ESP32 (`/dev/cu.usbserial-A5069RR4`) só gera o sinal; não configura o ESC.

Caminho: Arduino Uno com o passthrough → ESC Configurator no Chrome
(esc-configurator.com) → Read Settings. Em 13/11 nenhum dos dois está ligado ao USB.

## Estado gravado conhecido (30/10/2026)

BLHeli_S 16.7, A-H-25. Startup Power 0,75; Low RPM Power Protection desligada;
Brake on stop desligado; Demag Low; Timing Medium; temperatura 140 °C; direção
Reversed; PPM 1148–1832 µs. A calibração manual de 30/10 nunca foi confirmada por
releitura: ler antes de gravar.

## O que muda com o motor novo

| | A2212 920KV | AX-2810Q 750KV |
|---|---|---|
| Torque por ampère | 10,4 mN·m/A | 12,7 mN·m/A (+22 %) |
| Resistência de fase | 0,221 Ω (efetiva, ajustada) | **desconhecida** (0,15 é palpite) |
| Inércia do rotor | ~1,55 g·m² | igual (mesma aranha e painéis) |
| Rotação no mesmo pulso | — | ~18 % menor |

## Configuração proposta

| Parâmetro | Atual | Proposto | Por quê |
|---|---|---|---|
| Startup Power | 0,75 | **0,50** | 22 % mais torque por ampère e resistência provavelmente menor: o mesmo ajuste dá mais corrente. Com 0,75 o A2212 já guinchou sem girar uma vez. Subir para 0,75 só se o AX apenas tremer. |
| Demag Compensation | Low | **High** | Rotor de alta inércia com motor de baixo Kv: dessincronizar em mudança de acelerador é o risco principal; High é o recomendado para carga pesada. |
| Motor Timing | Medium | Medium | Padrão para 12N14P de baixo Kv; Medium-High só se dessincronizar em regime. |
| Low RPM Power Protection | Off | Off | Com ela ligada o ESC corta potência em baixa rotação e o rotor pesado não parte. Os watchdogs da ESP32 cobrem o travamento. |
| Brake on stop | Off | **On** (aprovado pelo Pedro em 13/11/2026) | Pedido da variante 3.1-P: sem freio a parada cruza a rotação crítica a 11–20 RPM/s. Estimativa: freio em curto dá ~0,2 N·m, para em ~1,5 s, e a carga tangencial no braço é ~0,5 N por painel, contra 160 N centrífugos: desprezível para a raiz. |
| Direção | Reversed | **ler e verificar** | Depende da ordem dos três fios no motor novo. Gravar Normal, girar sem aranha, e inverter (ou trocar dois fios) se não for anti-horário visto de cima. |
| PPM Min/Max | 1148/1832 | manter | Não depende do motor; conferir se a calibração de 30/10 mudou. |
| Temperatura, beeps, beacon | — | manter | — |

## Medir antes (multímetro, 1 minuto)

Resistência entre cada par de fios do motor, ponta a ponta. Fase ≈ metade da
leitura. Muda a corrente do chute no modelo (hoje 25–29 A no motor travado, com
Startup Power ignorado) e confirma se 0,50 é conservador.

## Fora do ESC, para depois

O alvo do firmware (1200 µs) dá só ~530–630 RPM com o AX no modelo; 1800 RPM pede
~1350 µs a 10 V, encostado no teto atual de 1350 µs. Recalcular o alvo e o teto do
firmware depois do primeiro giro medido com tacômetro.

## Medições de 13/11/2026

- Resistência medida pelo Pedro com o multímetro: 5,3 / 5,4 / 5,4 / 4,9 Ω. Lida
  como três pares de fios (5,3; 5,4; 5,4) e as pontas em curto (4,9): descontadas
  as pontas, ~0,4–0,5 Ω entre fios, **~0,2–0,25 Ω por fase**. A resolução de
  0,1 Ω do multímetro deixa ±25 %. É da ordem do A2212 (0,221 Ω efetivos), acima
  do palpite de 0,15 Ω: a corrente do chute no modelo cai cerca de um terço, e
  Startup Power 0,50 continua conservador. Os três pares iguais indicam
  enrolamentos sem fase aberta nem em curto.
- Arduino Uno em `/dev/cu.usbserial-10`, a mesma porta de 16 e 19/10.
