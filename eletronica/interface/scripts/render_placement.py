"""Readable top placement and true-scale fit coupon; no copper representation."""
from pathlib import Path
import json,html,math
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
a=sx.load(open(ROOT/'cad/interface-unrouted.kicad_pcb'))
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="750" height="1000" viewBox="0 0 15 20">','<rect width="15" height="20" fill="#195840"/>']
for fp in ch(a,'footprint'):
 at=one(fp,'at');x,y=at[1]-100,at[2]-100;angle=at[3] if len(at)>3 else 0
 ref=next(str(i[2]) for i in ch(fp,'fp_text') if str(i[1])=='reference')
 if ref.startswith('H'):
  svg.append(f'<circle cx="{x}" cy="{y}" r="1.75" fill="none" stroke="#9eb6a7" stroke-width=".05"/><circle cx="{x}" cy="{y}" r="1.1" fill="#eee"/>');continue
 if ref.startswith('J'):
  for pad in ch(fp,'pad'):
   p=one(pad,'at');net=one(pad,'net')[2]
   svg.append(f'<circle cx="{p[1]}" cy="{p[2]}" r=".5" fill="#ddc08c"/><circle cx="{p[1]}" cy="{p[2]}" r=".25" fill="#eee"/>')
  continue
 svg.append(f'<g transform="translate({x} {y}) rotate({-angle})">')
 for pad in ch(fp,'pad'):
  p=one(pad,'at');s=one(pad,'size');svg.append(f'<rect x="{p[1]-s[1]/2}" y="{p[2]-s[2]/2}" width="{s[1]}" height="{s[2]}" rx=".08" fill="#ddc08c"/>')
 if ref=='U1':svg.append('<rect x="-1.95" y="-4.35" width="3.9" height="8.7" rx=".2" fill="#25282b"/><circle cx="-1" cy="-3.5" r=".25" fill="#eee"/>')
 else:svg.append(f'<rect x="-.8" y="-.4" width="1.6" height=".8" fill="{"#a77742" if ref.startswith("C") else "#29292c"}"/>')
 svg.append('</g>')
 svg.append(f'<text x="{x}" y="{y+.15}" text-anchor="middle" font-family="sans-serif" font-size=".45" fill="white">{ref}</text>')
wire=json.loads((ROOT/'cad/wire_positions.json').read_text());n=0
for ref,pads in wire.items():
 for pin,(x,y) in pads.items():
  n+=1;tx=x;ty=y
  if x<1:tx=1.6
  elif x>14:tx=13.4
  elif y<1:ty=1.8
  else:ty=18.3
  svg.append(f'<text x="{tx}" y="{ty+.15}" text-anchor="middle" font-family="sans-serif" font-size=".45" fill="white">{n:02}</text>')
svg.append('</svg>');(ROOT/'reports/posicionamento.svg').write_text(''.join(svg))
# True-size print page with separate 50 mm calibration bar.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="70mm" viewBox="0 0 100 70">','<rect width="100" height="70" fill="white"/>','<g transform="translate(20 15)" fill="none" stroke="black" stroke-width=".15"><rect width="15" height="20"/>']
for x,y in [(2,2),(13,2),(13,18),(2,18)]:svg.append(f'<circle cx="{x}" cy="{y}" r="1.1"/><circle cx="{x}" cy="{y}" r="1.75" stroke-dasharray=".4 .3"/>')
svg.extend(['</g>','<path d="M20 50 H70 M20 48 V52 M70 48 V52" fill="none" stroke="black" stroke-width=".2"/>','<g font-family="sans-serif" font-size="3"><text x="20" y="10">PCB 15 x 20 mm - imprimir 100%</text><text x="20" y="43">4 furos 2,2 mm; cabecas ate 3,5 mm</text><text x="20" y="57">Conferir esta barra: 50 mm</text><text x="20" y="63">Molde nao representa fios ou altura de componentes.</text></g></svg>'])
(ROOT/'reports/molde-1-para-1.svg').write_text(''.join(svg))
print('Placement SVG and true-size fit coupon generated')
