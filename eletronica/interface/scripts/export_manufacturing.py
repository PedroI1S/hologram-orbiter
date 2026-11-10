"""Re-export and validate the FINAL editable CAD, without regenerating its placement."""
from pathlib import Path
import argparse,subprocess,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--kicad-cli',default=shutil.which('kicad-cli'));args=p.parse_args()
if not args.kicad_cli:p.error('Specify --kicad-cli /path/to/kicad-cli (KiCad 10)')
cli=args.kicad_cli;pcb=str(ROOT/'cad/interface.kicad_pcb');sch=str(ROOT/'cad/interface.kicad_sch');out=ROOT/'fabricacao';reports=ROOT/'reports';gerbers=out/'gerbers';gerbers.mkdir(exist_ok=True)
def run(*cmd):
 with (reports/'kicad-export.log').open('a') as log:subprocess.run([str(c) for c in cmd],stdout=log,stderr=log,check=True)
run(cli,'pcb','drc','--refill-zones','--save-board','--schematic-parity','--format','json','-o',reports/'drc-parity.json',pcb)
r=json.loads((reports/'drc-parity.json').read_text());assert not r['violations'] and not r['unconnected_items'] and not r['schematic_parity'],r
shutil.copyfile(reports/'drc-parity.json',reports/'drc.json')
run(cli,'sch','erc','--format','json','-o',reports/'erc.json',sch)
r=json.loads((reports/'erc.json').read_text());assert all(not s['violations'] for s in r['sheets']),r
run(cli,'sch','export','netlist','--format','kicadxml','-o',reports/'schematic.net',sch)
run(sys.executable,ROOT/'scripts/validate_pinmap.py')
run(cli,'pcb','export','gerbers','-o',str(gerbers)+'/', '-l','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,Edge.Cuts','--use-drill-file-origin','--subtract-soldermask','--disable-aperture-macros',pcb)
run(cli,'pcb','export','drill','--format','excellon','--drill-origin','plot','--excellon-units','mm','--excellon-separate-th','--generate-report','--report-path',reports/'drill-report.txt','-o',str(gerbers)+'/',pcb)
run(cli,'pcb','export','pos','--format','csv','--units','mm','--side','front','--smd-only','--exclude-fp-th','--use-drill-file-origin','-o',out/'PickAndPlace-KiCad.csv',pcb)
run(cli,'sch','export','svg','-o',str(reports/'esquema')+'/',sch)
for layers,name in [('F.Cu,F.SilkS,Edge.Cuts','pcb-top-kicad.svg'),('F.Fab,Edge.Cuts','montagem-top-kicad.svg')]:
 run(cli,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet','-o',reports/name,pcb)
run(sys.executable,ROOT/'scripts/check_copper.py')
run(sys.executable,ROOT/'scripts/verify_exports.py')
print('Export complete: zero ERC/DRC/parity/unconnected violations; Gerber, drill, BOM and 17 positions verified.')
