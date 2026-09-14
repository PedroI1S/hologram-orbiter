# Correção das raízes dos braços e entradas de fios — 14/09/2026

Revisão CAD 3.0.5. O perfil dos braços avançava para dentro da baia:
a raiz começava em x local=38 mm, enquanto a parede interna tem raio 39 mm.
O corte dos fios começava em x=38,5 mm e deixava uma película de 0,5 mm
na extremidade do braço. Nas laterais da janela, a curvatura da parede
também colocava sua face interna antes de x=38,5 mm.

## Correção

- Raiz em x=39 mm, sem a saliência interna. Conserva a união à parede,
  o alargamento de raiz, a cunha inferior e as cotas do ombro e da espiga.
- Corte da janela em x=37–42 mm, y=−10 a −5,5 mm, z=0,8–5,8 mm:
  atravessa toda a parede e encontra o bolso externo acima do piso z=2,3 mm.
- Parâmetros incompatíveis são rejeitados antes da geração.
- Dois critérios de aceite sondam a malha final: a faixa central das raízes
  e a abertura das janelas, incluindo a transição ao bolso. As guias laterais
  da eletrônica não fazem parte da faixa que se exige vazia.

## Evidência

Cada braço recebe 81 raios na faixa central da raiz e 121 na entrada de fios.
No STL anterior, 67 e 108, respectivamente, atravessavam material indevido;
no corrigido, as duas contagens são zero em todos os três braços.
Veja [medições antes/depois](evidencias/2026-09-14/bay_entries_before_after.json).

O teste `tests/blender_bay_entries.py` reconstrói a aranha em quatro cenários:
corrigido, raiz antiga, corte antigo e ambos antigos. Cada defeito reintroduzido
reprova seu critério, mesmo quando a outra parte está corrigida.

[Antes](evidencias/2026-09-14/aranha_entrada_fios_antes.png) ·
[Depois](../Hologram_Orbiter_v3_0/exports/preview/aranha_entrada_fios.png)

Os relatórios automáticos e o manifesto do build identificam os artefatos
regenerados: **58/58 critérios**, **9/9 STLs**, 10 testes unitários,
7 testes do pipeline e o teste Blender com quatro cenários aprovados.
Os hashes dos 43 artefatos do manifesto foram conferidos após a publicação.
Esta correção geométrica não altera os bloqueadores existentes
de operação e fabricação definitiva dos painéis.

Neste ambiente Linux, o encerramento do Blender travava no backend de áudio.
A execução foi feita com `ALSOFT_DRIVERS=null`, apenas para o processo do
build e do teste Blender, sem modificar a configuração de áudio do sistema.
