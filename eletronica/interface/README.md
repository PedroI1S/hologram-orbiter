# PCB de interface do rotor — r0.2

Placa de sinais em 15 × 20 mm, duas camadas, com montagem SMD no topo. Esta revisão implementa a arquitetura da proposta SPI quad lembrada pelo usuário: CLK comum, três DATA independentes e alimentação dos painéis em estrela externa. É um protótipo para orçamento e posterior ensaio, não uma eletrônica já qualificada em bancada.

## Arquivos para orçamento e revisão

- `fabricacao/gerbers/`: cobre, máscaras, serigrafias, pasta e furação exportados pelo KiCad.
- `fabricacao/Gerbers_Orbiter_r02.zip`: enviar ao campo de Gerber do fornecedor.
- `fabricacao/BOM.csv`: lista de compra e montagem, com MPN e quantidade por placa.
- `fabricacao/BOM-JLCPCB.csv`: correspondência de componentes para a JLCPCB.
- `fabricacao/PickAndPlace.csv`: coordenadas e rotações dos 17 SMDs.
- `fabricacao/mapa-fios.csv`: correspondência dos 19 pontos numerados com os sinais.
- `fabricacao/LEIA-ME-COTACAO.md`: requisitos para a fabricante, incluindo painelização e montagem.
- `fabricacao/Pacote_Orbiter_r02.zip`: conjunto para compartilhar com o fornecedor, incluindo fonte CAD e relatórios.
- `cad/interface.kicad_pro`, `cad/interface.kicad_sch`, `cad/interface.kicad_pcb`: projeto editável e bibliotecas locais.
- `reports/`: verificações, esquema exportado em SVG, PCB e molde físico 1:1.

A placa nua é cotada pelo Gerber; a montagem exige também BOM e Pick & Place. Conferir o preview do fornecedor, especialmente o pino 1 de U1 e as rotações. Códigos de componentes cadastrados não significam estoque reservado ou ausência de taxas adicionais.

## Circuito

| Função | Ligação |
|---|---|
| CLK comum | GPIO4 → U1 entrada 2 / saída 3 → R6, R10, R11 de 33 Ω → CLK de cada painel |
| DATA painel 1 | GPIO6 → U1 entrada 5 / saída 6 → R7 de 0 Ω → painel 1 |
| DATA painel 2 | GPIO5 → U1 entrada 9 / saída 8 → R12 de 0 Ω → painel 2 |
| DATA painel 3 | GPIO7 → U1 entrada 12 / saída 11 → R13 de 0 Ω → painel 3 |
| Habilitação do buffer | U1 pinos 1, 4, 10 e 13 ao GND |
| Repouso no reset | R1, R2, R8, R9: 10 kΩ de cada entrada digital ao GND |
| Alimentação de U1 | pino 14 em 5 V, pino 7 em GND; C1 100 nF junto ao CI e C2 1 µF local |
| Hall | A3144 externo em 5 V; R3 10 kΩ da saída a 3V3; leitura em GPIO3 |
| Bateria | R4 150 kΩ de VBAT_SW ao ADC; R5 47 kΩ ao GND; C3 100 nF ao GND; leitura em GPIO0 |

U1: SN74AHCT125DR, SOIC-14, entrada TTL e saída em 5 V. Não substituir por HC. Quatro canais usados; não sobram canais para clocks independentes. Um clock aciona três ramos com resistores série individuais, como na proposta local. Os resistores de DATA em 0 Ω permitem ajuste em bancada.

GPIO10 fica reservado para a quarta linha do periférico quad, sem fio na interface. As linhas DATA **não são unidas entre si**; cada painel recebe seus próprios bits. Saídas superiores das fitas ficam sem retorno à interface.

O ADC nominal vale 1,384 V a 5,8 V e 1,718 V a 7,2 V. Calibrar no firmware. O filtro deve permanecer próximo ao ADC eletricamente; manter o fio curto e acrescentar/reposicionar o capacitor junto ao C3 se a integração exigir. Este divisor mede a tensão e não desconecta a bateria.

## Fiação e alimentação

| Grupo funcional | Pinos |
|---|---|
| J1 — C3 | 1:5V; 2:GND; 3:3V3 vindo do C3; 4:GPIO4; 5:GPIO6; 6:GPIO3; 7:GPIO0; 8:GPIO5; 9:GPIO7 |
| J2 — Hall | 1:5V; 2:GND; 3:saída Hall |
| J3 — painel 1 | 1:CLK; 2:DATA painel 1 |
| J5 — painel 2 | 1:CLK; 2:DATA painel 2 |
| J6 — painel 3 | 1:CLK; 2:DATA painel 3 |
| J4 — bateria | 1:VBAT_SW, após chave/fusível e antes do buck |

Os grupos J representam pontos **distribuídos** pela placa, não headers comerciais contíguos. A numeração física 01–19 está na serigrafia inferior e no `mapa-fios.csv`. Os fios entram em furos metalizados de 0,5 mm; usar AWG28 nos sinais e na pequena alimentação da interface, conferindo o fio real. Fazer alívio mecânico. A ordem de J2 não representa a ordem dos terminais do sensor TO-92: conferir o componente real.

```
bateria + → fusível → chave → VBAT_SW → buck IN+
bateria - → GND comum / buck IN-
buck OUT+ → estrela 5V → painel 1+, painel 2+, painel 3+, C3 5V, interface 5V
buck OUT- → estrela GND → painel 1-, painel 2-, painel 3-, C3 GND, interface GND
1000 µF externo entre 5V e GND, no cubo
```

Cada painel recebe quatro fios: 5 V e GND pela distribuição de potência; CLK e seu DATA pela interface. Não passar os amperes dos LEDs pelas trilhas desta placa ou pelo fio fino de referência GND. O 5V do C3 recebe uma derivação externa própria; J1.1 não é um caminho de potência em série para o C3.

Chave, fusível, conector de balanceamento, buck e capacitor de 1000 µF continuam externos. É uma mudança de divisão física em relação à reserva antiga, que listava esses itens dentro de 15 × 20 sem modelos definidos. A acomodação e retenção desses componentes precisam ser verificadas no conjunto. Selecionar chave/fusível pela corrente DC real; não usar chave de sinal sem capacidade adequada para alimentar o buck. O buck real ainda precisa de qualificação ao longo da descarga da bateria.

> **Sem PCB:** a placa r0.2 não será fabricada. Para a montagem soldada à mão,
> com apenas o U1 já fixado, seguir [MONTAGEM-PONTO-A-PONTO.md](MONTAGEM-PONTO-A-PONTO.md)
> (mesmo circuito, com o envelope, o peso e a sequência de solda revistos).

## Encaixe

Centro no rotor `(27; 5) mm`, com cantos `(19,5; -5)` a `(34,5; 15)`. Na **v4.0**, a baia foi ampliada para **`Ø80` interno (`r = 40 mm`) / `Ø84` externo × `47 mm`**, deixando folga radial nominal de **`2,38 mm`** até o canto mais externo (`r = 37,62 mm`). *(Nos relatórios preservados da revisão `r0.2` / `v3.0`, como `reports/geometry.json`, a referência anterior era `r = 39 mm` / `1,38 mm`; o diagrama `reports/encaixe-baia.svg` já foi atualizado para `Ø80 mm`. Acima do berço da bateria, a prateleira em `Z = 28 mm` reserva espaço para uma eventual placa própria futura.)*

Furos de `2,2 mm` em `(2; 2)`, `(13; 2)`, `(13; 18)`, `(2; 18)` relativos ao canto da PCB. São os centros dos quatro pilares existentes no CAD. Cabeças até `Ø3,5 mm`, sem arruelas maiores; confirmar rosca e retenção nos pilares reais. A área das cabeças foi reservada também contra cobre/trilhas.

Face inferior da PCB a `Z = 6 mm`. Com FR4 de `1,6 mm` e SOIC de até aproximadamente `1,75 mm`, a pilha eletrônica fica abaixo do envelope anterior de `8 mm`. Fios e soldas não estão incluídos nessa comprovação nominal. Manter as pontas inferiores curtas para não obstruir chicotes sob a placa. O molde `reports/molde-1-para-1.svg` deve ser impresso a 100%; conferir a barra de `50 mm` antes de testar.

## Verificação e limites

Os resultados da revisão `r0.2` ficam em [`reports/VALIDACAO.md`](reports/VALIDACAO.md): zero violações ERC/DRC, zero conexões abertas e zero divergências de paridade no KiCad 10.0.7. Há conferência independente de geometria, continuidade entre camadas, folgas de cobre e equivalência de pinos entre tabela elétrica, esquemático e PCB. O DRC/ERC do KiCad e os arquivos exportados são verificados antes do empacotamento.

Isso não demonstra integridade dos sinais nos fios reais. Com rotor parado, verificar três padrões independentes, ordem de bits do SPI quad, clock na entrada das três fitas, funcionamento do Hall e leitura da bateria (ver [`firmware/teste-fitas-c3/`](../../firmware/teste-fitas-c3/)). Começar com alimentação limitada e obedecer ao teto provisório de corrente/brilho do esquema 05. Se um driver de clock para três ramos não bastar, será necessário rever hardware/clock; esta placa não reserva um segundo CI.

Ao programar o C3, confirmar o circuito da Super Mini real antes de alimentar simultaneamente por USB e buck; evitar realimentar fontes. Mudanças de massa/fiação exigem nova pesagem e balanceamento. Nenhuma pendência mecânica do rotor é encerrada pela interface.

## Reprodução

Os scripts em `scripts/` geram e verificam o projeto KiCad; as ferramentas são KiCad CLI, Python com `sexpdata`/`shapely` e Freerouting 2.1.0 em Java 21. O gerador de posicionamento não preserva edições manuais: usar o CAD final (`Hologram_Orbiter_v4/CAD/parameters.json`) como fonte ao alterar a placa e regenerar as saídas da revisão modificada.

## Referências

- [Esquema vigente (v4.0)](../../05-ESQUEMA-ELETRICO-v4.0.md): topologia SPI Quad vigente (4 fios por painel), alimentação, pinagem e requisitos de ensaio.
- [Montagem ponto a ponto (perfboard ativa)](MONTAGEM-PONTO-A-PONTO.md): roteiro prático em execução para o protótipo sem PCB fabricada.
- [Proposta SPI quad](../../revisoes/2026-09-21-PROPOSTA-SPI-QUAD.md): proposta original adotada na revisão e promovida na v4.0.
- [TI — SN74AHCT125](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf): pinagem, níveis e encapsulamento.
- [Espressif — checklist C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html): recomendação de filtro no ADC.

Para reexportar o CAD final sem regenerar o posicionamento: `python scripts/export_manufacturing.py --kicad-cli /caminho/kicad-cli` (KiCad 10 e dependências de `scripts/requirements.txt`).

Revisão de compra em 30/10: [BOM otimizada para JLCPCB](fabricacao/BOM-JLCPCB-otimizada.csv), com seis grupos Basic e substituto X7R 25 V para C2. Ver [substituições e consulta de estoque](reports/REVISAO-BOM-JLCPCB.md). Gerbers e Pick & Place permanecem os da PCB r0.2.
