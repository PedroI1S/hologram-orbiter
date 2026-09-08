# -*- coding: utf-8 -*-
"""Figuras analiticas da proposta de projeto (saida em PDF vetorial)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 8,
    'axes.linewidth': 0.7,
    'axes.labelsize': 8,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 7,
    'lines.linewidth': 1.4,
})

AZUL = '#1f4e79'
LARANJA = '#c55a11'
VERDE = '#2e7d32'
CINZA = '#888888'

OUT = '/Users/pedro/Documents/8_Semestre/OficinaDeIntegracao/proposta/figs/'

# ---------------------------------------------------------------
# Figura: escolha do ponto de operacao
#   (a) taxa de imagem x rotacao para 1, 2 e 3 paineis
#   (b) corrente de fase x raio, com I ~ r^3 a rotacao constante
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.65))

# ---- (a) ----
rpm = np.linspace(400, 2400, 400)
for n, cor, ls in [(1, CINZA, ':'), (2, LARANJA, '--'), (3, AZUL, '-')]:
    ax1.plot(rpm, n * rpm / 60.0, color=cor, linestyle=ls,
             label=r'$N_p = %d$' % n)

ax1.axhspan(60, 90, color=VERDE, alpha=0.10, lw=0)
ax1.axhline(90, color=VERDE, lw=0.9, ls='-.')
ax1.text(450, 79, 'limiar de fus\u00e3o de cintila\u00e7\u00e3o\nna vis\u00e3o perif\u00e9rica (~90 Hz)',
         fontsize=6.5, color=VERDE, va='center', ha='left')
ax1.plot([1800], [90], 'o', color=AZUL, ms=5, zorder=5)
ax1.annotate('ponto de projeto\n1800 rpm, 3 pain\u00e9is',
             xy=(1800, 90), xytext=(1520, 7), fontsize=6.8, ha='center',
             arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))
ax1.plot([1200], [60], 's', color=CINZA, ms=4.2, zorder=5)
ax1.annotate('v2.0', xy=(1200, 60), xytext=(1245, 63), fontsize=6.8, color='black')

ax1.set_xlabel('Rota\u00e7\u00e3o [rpm]')
ax1.set_ylabel(r'Taxa de imagem $f_{\rm img}$ [Hz]')
ax1.set_xlim(400, 2400)
ax1.set_ylim(0, 125)
ax1.legend(loc='upper left', frameon=False)
ax1.set_title('(a) taxa de imagem', fontsize=8)
ax1.grid(alpha=0.25, lw=0.5)

# ---- (b) ----
r = np.linspace(60, 145, 400)
I = 4.95 * (r / 100.0) ** 3          # I proporcional a r^3, w constante
ax2.plot(r, I, color=AZUL)

ax2.add_patch(Rectangle((60, 5.5), 85, 20, color=LARANJA, alpha=0.09, lw=0))
ax2.axhline(5.5, color=LARANJA, lw=0.9, ls='--')
ax2.text(62, 5.75, 'limite t\u00e9rmico do A2212 (5,5 A)',
         fontsize=6.5, color=LARANJA, va='bottom', ha='left')

ax2.plot([100], [4.95], 'o', color=AZUL, ms=5, zorder=5)
ax2.annotate('v3.0: $r=100$ mm\n4,95 A / 46 $^\\circ$C',
             xy=(100, 4.95), xytext=(107, 1.3), fontsize=6.8, ha='left',
             arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))
ax2.plot([130], [10.87], 'x', color=LARANJA, ms=6, mew=1.6, zorder=5)
ax2.annotate('v2.1: $r=130$ mm\n9,8\u201310,9 A / 101 $^\\circ$C',
             xy=(130, 10.87), xytext=(74, 11.4), fontsize=6.8,
             arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))

ax2.set_xlabel('Raio do plano m\u00e9dio do painel $r$ [mm]')
ax2.set_ylabel('Corrente de fase $I$ [A]')
ax2.set_xlim(60, 145)
ax2.set_ylim(0, 14)
ax2.set_title(r'(b) custo do raio a 1800 rpm ($I \propto r^3$)', fontsize=8)
ax2.grid(alpha=0.25, lw=0.5)

fig.tight_layout(pad=0.5)
fig.savefig(OUT + 'analise.pdf')
plt.close(fig)

# ---------------------------------------------------------------
# Figura: cronograma (Gantt)
# ---------------------------------------------------------------
TAREFAS = [
    ('Documentação e relatório final', 9, 1, 'F5'),
    ('Bloqueador E, ajustes e demonstração (G5)', 9, 1, 'F5'),
    ('Imagem de teste e rebalanceamento (G4)', 8, 1, 'F4'),
    ('Firmware: SPI, índice angular, colunas', 7, 1, 'F4'),
    ('Fiação e eletrônica de bordo', 7, 1, 'F4'),
    ('Bloqueadores C e D: vibração e partida (G3)', 6, 1, 'F3'),
    ('Bloqueador B: térmica em regime contínuo', 5, 1, 'F3'),
    ('Bloqueador A: potência e arrasto', 5, 1, 'F3'),
    ('Ensaio de impacto C0 e contenção', 4, 1, 'F2'),
    ('Montagem e balanceamento estático (G2)', 4, 1, 'F2'),
    ('Verificação dimensional e pesagem (G1)', 3, 1, 'F1'),
    ('Corte e furação da chapa R01', 3, 1, 'F1'),
    ('Base e torre integradas (12–18 h)', 3, 1, 'F1'),
    ('Aranha, tampa e suporte do ímã', 2, 1, 'F1'),
    ('Lote dos três painéis', 2, 1, 'F1'),
    ('Cupons C01 e C02', 1, 1, 'F1'),
    ('Compras do caminho crítico', 1, 2, 'F0'),
]
CORES = {'F0': '#9dc3e6', 'F1': '#5b9bd5', 'F2': '#2e75b6',
         'F3': '#1f4e79', 'F4': '#c55a11', 'F5': '#2e7d32'}

fig, ax = plt.subplots(figsize=(7.0, 3.45))
for i, (nome, ini, dur, fase) in enumerate(TAREFAS):
    ax.barh(i, dur, left=ini - 1, height=0.62,
            color=CORES[fase], edgecolor='white', linewidth=0.6)

ax.set_yticks(range(len(TAREFAS)))
ax.set_yticklabels([t[0] for t in TAREFAS], fontsize=7)
ax.set_ylim(-0.7, len(TAREFAS) - 0.3)

ax.set_xticks(np.arange(0, 10, 1))
ax.set_xticklabels(['', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
ax.set_xlim(0, 9)
ax.set_xlabel('Semana  (semana 1 inicia em 08/09/2026; semana 9 encerra em 09/11/2026)')
ax.xaxis.grid(True, alpha=0.3, lw=0.5)
ax.set_axisbelow(True)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)

# marcacao dos portoes
for semana, rotulo in [(3, 'G1'), (4, 'G2'), (6, 'G3'), (8, 'G4'), (9, 'G5')]:
    ax.axvline(semana, color='#b00020', lw=0.8, ls='--', alpha=0.75)
    ax.text(semana, len(TAREFAS) - 0.55, rotulo, color='#b00020',
            fontsize=7, ha='center', va='bottom', fontweight='bold')

handles = [plt.Rectangle((0, 0), 1, 1, color=CORES[k]) for k in
           ['F0', 'F1', 'F2', 'F3', 'F4', 'F5']]
ax.legend(handles,
          ['Fase 0 — aquisição', 'Fase 1 — fabricação', 'Fase 2 — montagem',
           'Fase 3 — ensaios de rotação', 'Fase 4 — integração óptica',
           'Fase 5 — validação'],
          loc='upper center', frameon=False, ncol=3, fontsize=6.8,
          bbox_to_anchor=(0.5, -0.145), handlelength=1.5, columnspacing=1.4)

fig.tight_layout(pad=0.4)
fig.savefig(OUT + 'cronograma.pdf')
plt.close(fig)

print('figuras geradas em', OUT)
