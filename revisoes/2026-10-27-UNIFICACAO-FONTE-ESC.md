# Unificação documental da fonte do ESC — 27/10/2026

A premissa vigente já registrada em `../Hologram_Orbiter_v3_0/CAD/parameters.json`
é fonte em **10–12 V**, com limite de corrente de **30 A**. As instruções
operacionais que ainda diziam ~3 A foram alinhadas a essa premissa.

## Valores utilizados

Fonte: `../Hologram_Orbiter_v3_0/reports/FISICA.json`, campos `drive.steady`
e `drive.startup_kick`.

| Grandeza prevista | 10 V | 12 V |
|---|---:|---:|
| Potência de regime a 1800 RPM | 16,63 W | 16,63 W |
| Corrente na fonte em regime | 1,66 A | 1,39 A |
| Corrente de fase em regime | 4,95 A | 4,95 A |
| Corrente de fase, rotor parado no chute | 16,7 A | 20,0 A |
| Corrente na fonte, rotor parado no chute | 6,47 A | 7,76 A |
| Potência na fonte, rotor parado no chute | 64,7 W | 93,1 W |
| Pico de rotação na trajetória atual | 1692 RPM | 1964 RPM |

A trajetória usa subida de 3 s até 1400 µs, chute de 2 s e descida a
42 µs/s até **1200 µs**, o alvo inicial do firmware. Outro alvo exige novo
cálculo. A fonte não limita nos casos previstos. O modelo ignora o Startup
Power do ESC e a resistência da fonte e dos cabos; os valores não são medições.

## Efeito nos documentos

Foram alinhados o README, os documentos 01–07, os guias de montagem e
impressão, o README do firmware e os comentários junto à duração do chute.
O registro de decisões de 20/10 recebeu correção explícita do limite; as
condições anotadas nos ensaios de 19/10 foram preservadas como histórico.

O bloqueador D mantém os critérios de aceite. Seu método passa a exigir
revisão do perfil antes do ensaio com rotor, pois a previsão atual excede
os limites de fase/potência nas duas tensões e de rotação a 12 V. Também foi
retirada a recomendação automática de alongar o chute diante de qualquer
falha: esse ajuste pode elevar ainda mais a rotação.

Não houve alteração dos parâmetros de cálculo, dos pulsos ou dos tempos do
firmware. A proposta original e suas apresentações permanecem históricas,
com indicação da documentação operacional vigente em `../proposta/README.md`.

## Verificação

- `python3 -m unittest discover -s Hologram_Orbiter_v3_0/tests -p test_physics.py`:
  5 testes aprovados, incluindo regime, partida a 10/12 V e o cenário alternativo
  de limitação a 3 A.
- Conferência dos números publicados contra `FISICA.json` e busca por menções
  remanescentes ao limite antigo nos documentos operacionais.
- `git diff --check` sem erros de formatação.
