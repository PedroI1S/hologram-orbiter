# Gravação do ESC para o AX-2810Q — 13/11/2026

**Método.** O ESC Configurator no navegador do Playwright fechou a página ao abrir o
seletor de porta WebSerial, que o Playwright não consegue responder. A gravação foi
feita pelo mesmo caminho de 30/10: `blheli4way.py` (pyserial) → Arduino Uno em
`/dev/cu.usbserial-10` (BTFL, MSP API 1.43) → MSP_SET_PASSTHROUGH (4 canais) →
interface 4-way `m4wFCIntf` 200.6 → ESC 1.

**ESC.** Respondeu normalmente: assinatura B2 E8, BLHeli_S 16.7, A-H-25, EFM8BB21.
O Pedro relatou que ao ligar não houve tons de inicialização (o ESC de 19/10 tocou); como o
ESC lê e grava, a causa provável está nas fases do motor (solda/contato com o AX novo),
não no ESC. Conferir se houve tons no DeviceReset ao fim de cada sessão.

**Outro ESC.** Esta unidade não é a de 16/10–30/10 (confirmado pelo Pedro em 13/11),
por isso o estado encontrado difere do gravado em 30/10: Startup Power 0,25 (offset
9 = 7) e direção Normal (offset 11 = 1); demais bytes iguais aos de 30/10, mesmo
firmware e layout. Bytes 112–511 da página FF. O SHA-256 lido (`9c6244b3…`) é
exatamente o gravado em 19/10 (`esc_blheli_s_2026-10-19/registro.md`): é a unidade de
19/10, que tocou os tons de inicialização naquele dia.

**Gravado** (aprovado em 13/11): Startup Power **0,50** (9), Demag **High** (31 = 3),
Brake on stop **On** (39 = 1). Direção mantida em **Normal**, como no plano. Timing
Medium, LRPP Off, PPM 1148–1832 µs, 140 °C (7), beeps 40/80/4 inalterados.

Página apagada (0x1A00, página 13) e só os 112 bytes de configuração regravados.
Duas releituras iguais ao desejado; terceira leitura em sessão nova, após DeviceReset,
idêntica (SHA-256 `4f456a62…a119`). Nenhum comando de acelerador enviado.

**Pendente.** Sentido físico com o AX não verificado: girar sem aranha (sinal na D25 da
ESP32, GND comum) e, se não for anti-horário visto de cima, regravar offset 11 = 2 ou
trocar dois fios de fase. Alvo e teto do firmware para o AX (ver `plano-ax2810q.md`).

## Primeira tentativa com o AX (13/11, vídeos do Pedro)

Sem nada no eixo, alvo padrão de 1200 µs: o sino só dá trancos curtos para os dois
lados e estala, sem girar — o mesmo sintoma do A2212 com a peça em 19/10. Hipóteses:
pulso baixo demais para o AX (1200 µs ≈ 7,6 % de acelerador) ou fase aberta entre ESC e
motor (sem tons ao energizar). Próximo: alvo 1300/1400 µs e conferir fonte e conexões.

Correção do Pedro: os tons faltaram porque o motor ainda não estava soldado; com ele
soldado o ESC apita. O segundo vídeo é a 1300 µs: vibra mais forte e continua sem girar.
Motor sem carga que tranca mais quanto mais acelerador recebe não é falta de pulso:
suspeita principal passa a ser uma das três soldas/fases (aberta, fria ou em ponte).

**Resolvido (13/11).** Solda de fase refeita pelo Pedro; o AX passou a girar sem carga.
Confirmou a causa: solda, não pulso nem configuração do ESC. Pendente: sentido de giro
(anti-horário visto de cima) e RPM por pulso medidos com tacômetro.
