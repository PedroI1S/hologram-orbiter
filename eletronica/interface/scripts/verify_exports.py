"""Parse fabrication files with an independent Gerber/Excellon implementation."""
from pathlib import Path
import csv,json,warnings,xml.etree.ElementTree as ET
from collections import Counter
from gerbonara import LayerStack
import cairosvg
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'fabricacao'
with warnings.catch_warnings(record=True) as caught:
 s=LayerStack.open(out/'gerbers')
 layers=list(s.graphic_layers)
 assert len(layers)==8
 assert len(s.drill_pth.objects)==29 and len(s.drill_npth.objects)==4
 bounds=s.board_bounds();width=bounds[1][0]-bounds[0][0];height=bounds[1][1]-bounds[0][1]
 assert abs(width-15.05)<1e-5 and abs(height-20.05)<1e-5 # Edge line is 0.05 mm wide, centered on the 15x20 outline.
 # Plain per-layer plots avoid SVG filter limitations in CairoSVG.
 for side in ['top','bottom']:
  for use in ['copper','silk']:
   svg=s[(side,use)].instance.to_svg(force_bounds=bounds)
   fn=ROOT/f'reports/gerber-{side}-{use}.svg';fn.write_text(str(svg))
   cairosvg.svg2png(url=str(fn),write_to=str(fn.with_suffix('.png')),output_width=750,background_color="white")
 # Keep filter-based browser views too; raster previews use the plain plots above.
 for side in ['top','bottom']:(ROOT/f'reports/gerbers-{side}.svg').write_text(str(s.to_pretty_svg(side=side)))
 # Actual silk and copper files parsed successfully, not inferred from the board CAD.
 messages=sorted(set(str(w.message) for w in caught))
rows=list(csv.DictReader(open(out/'PickAndPlace-KiCad.csv')))
assert len(rows)==17 and len({r['Ref'] for r in rows})==17
with (out/'PickAndPlace.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for r in rows:
  assert 0<float(r['PosX'])<15 and -20<float(r['PosY'])<0 and r['Side']=='top'
  w.writerow([r['Ref'],r['PosX'],r['PosY'],'Top',r['Rot']])
bom=list(csv.DictReader(open(out/'BOM.csv')));refs={r for item in bom for r in item['Designator'].split(',')}
assert refs=={r['Ref'] for r in rows};assert sum(int(i['Quantity']) for i in bom)==17
cairosvg.svg2png(url=str(ROOT/'reports/esquema/interface.svg'),write_to=str(ROOT/'reports/esquema.png'),output_width=2200)
report={'gerber_layers':layers,'outline_centerline_size_mm':[15,20],'plated_drill_hits':29,'nonplated_drill_hits':4,'smd_positions':len(rows),'bom_matches_positions':True,'parser_notes':messages}
(ROOT/'reports/export-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
