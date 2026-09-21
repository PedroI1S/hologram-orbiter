# Apresentação Hologram Orbiter

Abra `apresentacao.html` no navegador. A pasta é independente de servidor e internet: fontes, imagens, estilos e scripts são locais. Para compartilhar a versão animada, envie a pasta inteira.

## Controles

- **F** ou **Apresentar**: entra ou sai do modo apresentação.
- **Setas**, **Page Up / Page Down**, **Espaço**: navegam durante a apresentação.
- **Home / End**: primeiro ou último slide. **Esc**: sai.
- **M** ou **Pausar animações**: pausa e retoma o movimento.
- Clique à esquerda para voltar ou à direita para avançar. No celular, deslize horizontalmente durante a apresentação.
- Mova o ponteiro para a parte inferior para mostrar os controles. Eles também aparecem ao receber foco pelo teclado.
- No slide **A imagem é escrita no ar, uma coluna por vez**, acompanhe os LEDs no instante atual, o rastro das colunas e a imagem formada. Arraste **Varredura por painel** para explorar de 0° a 120°. **Pausar sequência** interrompe a progressão e **Reiniciar** volta ao início. As setas do teclado ajustam o controle que estiver em foco.
- No slide **O rotor desloca o ar e sofre arrasto**, ajuste a **rotação** e o **raio** para observar o movimento dos três painéis, a imagem dos LEDs e a esteira de ar. As setas do teclado ajustam o controle que estiver em foco.
- **Ar e esteira** e **Imagem dos LEDs** mostram ou ocultam as camadas da animação. **Ver gráfico** alterna para o gráfico original de corrente versus raio. **Restaurar 1800 rpm / 100 mm** volta ao ponto de operação da proposta.

A preferência de movimento reduzido do sistema é respeitada. As entradas são automáticas e não acrescentam etapas à navegação. A varredura é uma ilustração em velocidade reduzida, não uma simulação da percepção visual nem um vídeo do protótipo funcionando.

A animação de arrasto também usa movimento desacelerado. As partículas representam o ar deslocado pelos painéis e uma vista superior mostra a força oposta ao movimento. O escoamento é ilustrativo, sem cálculo de CFD. Os indicadores usam `v = 2πrn/60`, `f = 3n/60` e `P/P₀ = (n/1800)³(r/100)³`, com `n` em rpm e `r` em mm (convertido para metros no cálculo da velocidade). A potência é relativa ao ponto de 1800 rpm e 100 mm, mantendo área e coeficiente de arrasto fixos. As previsões dependem de validação em bancada.

## Arquivos

- `apresentacao.html`: roteiro principal, reduzido de 18 para 11 slides.
- `apresentacao.css`: ajustes visuais, transições e regras de impressão.
- `apresentacao.js`: navegação e animação dos diagramas existentes.
- `orbiter-renderer.js`: desenho em perspectiva do rotor do slide 2, seguindo as formas e cores do slide 4.
- `principio.js`: sequência em três Canvas para mostrar o instante de escrita, o acúmulo das colunas e a imagem formada, com controle de progresso.
- `arrasto.js`: cena em Canvas com rotor, LEDs e escoamento ilustrativo, além dos controles do ponto de operação.
- `apresentacao.pdf`: versão estática dos 11 slides, incluindo um quadro da nova cena de arrasto. As animações e os controles funcionam no HTML.
- `apresentacao-completa-original.html` e `.pdf`: versão anterior preservada, com cálculos e explicações detalhadas. O botão **Detalhes técnicos** abre o HTML original.

As sete imagens PNG utilizadas são cópias dos renders do Blender em `Hologram_Orbiter_v3_0/exports/preview`. Os renders mostram o CAD, não peças já fabricadas. As estimativas e os critérios vêm da apresentação e da proposta originais. O estado provisório do CAD vem do README da revisão 3.0.5, de 14/09/2026.

Para atualizar o PDF após editar o HTML:

```sh
python3 gera_pdf.py
```

Também é possível imprimir pelo navegador, com gráficos de fundo habilitados. A impressão mostra todo o conteúdo, inclusive quando aberta a partir do modo apresentação.
