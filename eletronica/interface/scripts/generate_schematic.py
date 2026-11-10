"""Capture a self-contained KiCad schematic from the reviewed pin/net table."""
from pathlib import Path
import json,uuid
ROOT=Path(__file__).resolve().parents[1]
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s),ensure_ascii=False)
c=json.loads((ROOT/'circuito.json').read_text())
# Revision r0.2 uses machine-assembled 0603 passives.
for ref,item in c.items():
 if ref[0] in 'RC': item['footprint']=item['footprint'].replace('0805_2012','0603_1608')
(ROOT/'circuito.json').write_text(json.dumps(c,indent=2)+'\n')
rootuuid=uid();libs=[];instances=[];wires=[];symids={}
placements={'U1':(40,55),'J1':(120,50),'J2':(200,45),'J3':(280,40),'J5':(280,65),'J6':(280,90),'J4':(200,80)}
for i,r in enumerate([k for k in c if k[0] in 'RC']):placements[r]=(35+(i%4)*85,135+(i//4)*38)
for ref,item in c.items():
 pins=item['pins']; x,y=placements[ref]; x=round(round(x/1.27)*1.27,6); y=round(round(y/1.27)*1.27,6); name='Orbiter:'+ref;short=ref
 if ref=='U1':
  pinpos={str(i):(-10.16, (4-i)*2.54,0) for i in range(1,8)}
  pinpos.update({str(i):(10.16,(i-11)*2.54,180) for i in range(8,15)})
  body='(rectangle (start -7.62 10.16) (end 7.62 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))'
 elif ref[0] in 'RC':
  pinpos={'1':(-5.08,0,0),'2':(5.08,0,180)}
  if ref[0]=='R':body='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'
  else:body='(polyline (pts (xy -0.508 -1.778) (xy -0.508 1.778)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.508 -1.778) (xy 0.508 1.778)) (stroke (width 0.254) (type default)) (fill (type none)))'
 else:
  pinpos={str(i):(10.16,(1-i)*2.54,180) for i in range(1,len(pins)+1)}
  body=f'(rectangle (start -5.08 2.54) (end 7.62 {-len(pins)*2.54}) (stroke (width 0.254) (type default)) (fill (type background)))'
 syms=[]
 for pin,(px,py,angle) in pinpos.items():
  net=pins[pin];typ='passive';length=2.54 if ref[0] not in 'RC' else (2.54 if ref[0]=='R' else 4.572)
  if ref=='U1':typ='power_in' if pin in ['7','14'] else ('output' if pin in ['3','6','8','11'] else 'input')
  if ref=='J1':typ='power_out' if pin in ['1','2','3'] else ('input' if pin in ['6','7'] else 'output')
  if ref=='J2' and pin=='3':typ='output'
  if ref=='J4':typ='power_out'
  syms.append(f'(pin {typ} line (at {px} {py} {angle}) (length {length}) (name {q(net)} (effects (font (size 0.9 0.9)))) (number {q(pin)} (effects (font (size 0.9 0.9)))))')
 libs.append(f'''(symbol {q(name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes)
 (property "Reference" {q(ref[0])} (at 0 12.7 0) (effects (font (size 1.27 1.27))))
 (property "Value" {q(item['value'])} (at 0 15.24 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" {q(item['footprint'])} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (symbol {q(short+'_0_1')} {body}) (symbol {q(short+'_1_1')} {' '.join(syms)}))''')
 symids[ref]=uid()
 instances.append(f'''(symbol (lib_id {q(name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {symids[ref]})
 (property "Reference" {q(ref)} (at {x} {y-12.7 if ref=='U1' else y-5.08} 0) (effects (font (size 1.27 1.27))))
 (property "Value" {q(item['value'])} (at {x} {y-15.24 if ref=='U1' else y-7.62} 0) (effects (font (size 1.0 1.0))))
 (property "Footprint" {q(item['footprint'])} (at {x} {y} 0) (effects (font (size 1.0 1.0)) (hide yes)))
 {' '.join(f'(pin {q(pin)} (uuid {uid()}))' for pin in pins)}
 (instances (project "interface" (path "/{rootuuid}" (reference {q(ref)}) (unit 1)))))''')
 for pin,(px,py,a) in pinpos.items():
  sx,sy=x+px,y-py;ex=sx+(-7.62 if px<0 else 7.62)
  wires.append(f'(wire (pts (xy {sx} {sy}) (xy {ex} {sy})) (stroke (width 0) (type default)) (uuid {uid()}))')
  wires.append(f'(label {q(pins[pin])} (at {ex} {sy} 0) (effects (font (size 0.9 0.9)) (justify left bottom)) (uuid {uid()}))')
text=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid {rootuuid}) (paper "A3")
(title_block (title "Orbiter - interface SPI quad r0.2") (date "2026-10-30") (rev "r0.2 - cotacao") (comment 1 "5V/GND dos paineis em estrela externa; sinais CLK comum, DATA independentes"))
(lib_symbols {' '.join(libs)})
{' '.join(wires)} {' '.join(instances)}
(text "INTERFACE DE SINAIS - POTENCIA DOS LEDS EXTERNA\nGPIO4 CLK / GPIO6 D0 / GPIO5 D1 / GPIO7 D2 / GPIO10 reservado\nJ1: 5V GND 3V3 CLK D0 HALL ADC D1 D2\nJ2: 5V GND HALL; J3/J5/J6: CLK DATA; J4: VBAT apos chave e fusivel\nTodos os grupos J representam pontos de solda, nao conectores comerciais." (at 325 140 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid {uid()}))
(embedded_fonts no))'''
(ROOT/'cad/interface.kicad_sch').write_text(text)
(ROOT/'cad/symbol_ids.json').write_text(json.dumps(symids,indent=2)+'\n')
print('Schematic generated')
