# Torre construída: maciça em PETG

Registro de 30/10/2026, confirmado por Pedro: a torre da base usada nos
ensaios **já é maciça, em PETG, sem o furo central de Ø22 mm**. Não se trata
de uma alteração futura nem apenas de preencher a parede tubular a 100%.
A marca do PETG e os parâmetros de impressão ainda não foram informados.
Esta confirmação refere-se à torre; não comprova o material das demais peças.

A geometria de referência continua sendo Ø30 mm e 150 mm de altura, conforme
a documentação; essas cotas não foram novamente medidas neste registro.
O rotor ensaiado tem **179,5 g, sem circuito**, e a fonte está em **10,4 V**,
segundo o operador. Motor de 52 g e chapa de 18 g permanecem valores de projeto:
a massa concentrada de cálculo soma 249,5 g. O CG 31 mm acima da torre é uma
hipótese herdada, ainda não verificada para a montagem sem circuito.

## Diferença em relação ao CAD

`CAD/parameters.json` e `CAD/generate.py` ainda descrevem uma torre tubular
Ø30/Ø22 mm, parede de 4 mm; a especificação original previa ABS.
Esse CAD não representa a torre construída neste aspecto. O registro documental
não altera a malha, os parâmetros geométricos nem resolve a passagem de cabos
da montagem maciça, cujo trajeto não foi informado.

## Estimativa de vibração revisada

A conta anterior de aproximadamente 46 Hz usava a torre tubular e rotor de
279 g. A atualização intermediária para 54,3 Hz corrigia apenas a massa do
rotor, mantendo a rigidez tubular anterior. Nenhuma é uma medição da torre atual.

Para cilindro maciço: `I = π × 30⁴ / 64 = 39760,8 mm⁴`, contra
28261,8 mm⁴ do tubo Ø30/Ø22, aumento geométrico de 40,7%.
Mantendo L = 150 mm e a = 31 mm:

- `C = 1 + 3a/L + 3(a/L)² = 1,74813`;
- `k_eff = 3EI / (L³ × C)`;
- densidade assumida de 1,27 g/cm³: massa da torre cilíndrica ≈ 134,7 g;
- aproximação de Rayleigh com forma estática sob força no CG:
  `φ(t) = [3(1+a/L)t² − t³]/(2C)`, com `t = x/L`;
- contribuição modal da torre: `m_torre × integral_0^1 φ(t)² dt`,
  com integral ≈ 0,12738; massa efetiva total ≈ 0,26665 kg;
- `fn ≈ sqrt(k_eff × 1000 / m_efetiva)/(2π)`, com k_eff em N/mm.

| Módulo E assumido | fn estimada | RPM em 1× | RPM em 2× | Pulso em 2× | RPM em 3× | Pulso em 3× |
|---|---:|---:|---:|---:|---:|---:|
| 1,5 GPa | 53,7 Hz | 3220 | 1610 | 1321 µs | 1073 | 1250 µs |
| 1,8 GPa | 58,8 Hz | 3528 | 1764 | 1343 µs | 1176 | 1263 µs |
| 2,1 GPa | 63,5 Hz | 3810 | 1905 | 1365 µs | 1270 | 1275 µs |

São cenários de sensibilidade, não limites garantidos para PETG nem ressonâncias
confirmadas. A montagem real pode ter outros modos. Flexibilidade da base,
flange, chapa e rolamentos, inércia transversal e efeitos giroscópicos não
estão representados. A massa cilíndrica não inclui as flanges.
Confirmar fn por impacto com a montagem e fixação reais (plano 04, C0).

Os pulsos usam o modelo médio já documentado em `CAD/physics.py`, a 10,4 V:
`duty × V = Kt × ω + R × 4,95 × (ω/ω_1800)²`,
`duty = (pulso_us − 1148)/684`, `Kt = 60/(2π × 920)`, R = 0,221 Ω.
O arrasto ainda é o do rotor completo; retirar o circuito não permite
corrigi-lo proporcionalmente à massa. As coincidências em 2× e 3× só podem
excitar o modo se houver força e acoplamento correspondentes.

Referência ilustrativa de propriedades, sem identificar o filamento usado:
[ficha técnica de PETG do fabricante](https://store.bblcdn.com/fd2c725549734dcd9c14004fdca8a4d4.pdf).
O módulo efetivo depende da formulação, orientação, temperatura e impressão.
