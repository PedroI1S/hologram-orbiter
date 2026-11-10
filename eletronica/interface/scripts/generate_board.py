"""Generate an editable initial placement; routing is imported separately."""
from pathlib import Path
import json,math,uuid
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'circuito.json').read_text())
def q(s):return json.dumps(str(s))
def uid():return str(uuid.uuid4())
names=sorted({n for i in c.values() for n in i['pins'].values() if n});nets={n:i+1 for i,n in enumerate(names)}
def ndef(n):return f'(net {nets[n]} {q(n)})'
parts=[]
symids=json.loads((ROOT/'cad/symbol_ids.json').read_text()) if (ROOT/'cad/symbol_ids.json').exists() else {}
# Positions and rotation, relative to lower-left corner of enclosure-layout drawing.
place={'U1':(7.5,10,0),
'R1':(2,6.25,0),'R2':(2,8.75,0),'R8':(13,11.25,0),'R9':(13,8.75,0),
'R6':(4.6,3.75,90),'R10':(6.55,3.75,90),'R11':(8.5,3.75,90),'R7':(2,11.25,0),
'R12':(13,13.75,0),'R13':(13,6.25,0),
'R3':(10.45,16.25,90),'R4':(4.6,16.25,90),'R5':(6.55,16.25,90),
'C1':(10.45,3.75,90),'C2':(2,13.75,0),'C3':(8.5,16.25,90)}
# Distributed small solder eyelets; actual pin map is exported as CSV.
wire={
'J1':{'1':(.85,15),'2':(4.2,19.15),'3':(10.8,19.15),'4':(.85,5),'5':(.85,7.5),'6':(8.6,19.15),'7':(6.4,19.15),'8':(14.15,10),'9':(14.15,7.5)},
'J2':{'1':(10.8,.8),'2':(14.15,15),'3':(14.15,12.5)},
'J3':{'1':(4.2,.8),'2':(.85,10)},
'J5':{'1':(5.85,.8),'2':(.85,12.5)},
'J6':{'1':(7.5,.8),'2':(14.15,5)},
'J4':{'1':(9.15,.8)}}
def rect(x1,y1,x2,y2,layer,width=.05):return f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type solid)) (fill none) (layer {q(layer)}))'
for ref,(x,y,a) in place.items():
 item=c[ref];pins=item['pins'];geom=[]
 if ref=='U1':
  fp='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm';padpos={str(i):(-2.7,(i-4)*1.27) for i in range(1,8)}
  padpos.update({str(i):(2.7,(11-i)*1.27) for i in range(8,15)})
  for pin,(px,py) in padpos.items():geom.append(f'(pad {q(pin)} smd roundrect (at {px} {py}) (size 1.55 0.6) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) {ndef(pins[pin])})')
  geom.extend([rect(-3.73,-4.6,3.73,4.6,'F.CrtYd'),rect(-1.95,-4.35,1.95,4.35,'F.Fab',.1),f'(fp_circle (center -1.8 -4.7) (end -1.65 -4.7) (stroke (width 0.1) (type solid)) (fill none) (layer "F.SilkS"))'])
 else:
  fp=item['footprint'];padpos={'1':(-.825,0),'2':(.825,0)}
  for pin,(px,py) in padpos.items():geom.append(f'(pad {q(pin)} smd roundrect (at {px} {py} {a}) (size 0.9 0.95) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) {ndef(pins[pin])})')
  geom.extend([rect(-1.55,-.73,1.55,.73,'F.CrtYd'),rect(-.8,-.4,.8,.4,'F.Fab',.1)])
 geom.append(f'(fp_text reference {q(ref)} (at 0 0 {a}) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))')
 geom.append(f'(fp_text value {q(item["value"])} (at 0 0 {a}) (layer "F.Fab") hide (effects (font (size 0.6 0.6) (thickness 0.1))))')
 parts.append(f'(footprint {q(fp)} (layer "F.Cu") (at {100+x} {100+y} {a}) (attr smd) (path "/{symids.get(ref,uid())}") (uuid {uid()}) {" ".join(geom)})')
for ref,pads in wire.items():
 geom=[]
 for pin,(x,y) in pads.items():
  geom.append(f'(pad {q(pin)} thru_hole circle (at {x} {y}) (size 1.0 1.0) (drill 0.5) (layers "*.Cu" "*.Mask") {ndef(c[ref]["pins"][pin])})')
 parts.append(f'(footprint "Orbiter:DistributedWirePads" (layer "F.Cu") (at 100 100) (path "/{symids.get(ref,uid())}") (attr through_hole exclude_from_pos_files exclude_from_bom) (fp_text reference {q(ref)} (at 7.5 10) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.1)))) {" ".join(geom)})')
 c[ref]['footprint']='Orbiter:DistributedWirePads'
for i,(x,y) in enumerate([(2,2),(13,2),(13,18),(2,18)],1):
 parts.append(f'''(footprint "Orbiter:MountingHole_2.2mm_Head3.5mm" (layer "F.Cu") (at {100+x} {100+y}) (attr board_only exclude_from_pos_files exclude_from_bom)
 (fp_text reference "H{i}" (at 0 0) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.1))))
 (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))
 (fp_circle (center 0 0) (end 1.75 0) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd")))''')
 # Screw-head copper keepout on both layers.
 pts=' '.join(f'(xy {100+x+1.78*math.cos(t*math.pi/8):.5f} {100+y+1.78*math.sin(t*math.pi/8):.5f})' for t in range(16))
 parts.append(f'(zone (net 0) (net_name "") (layers "F.Cu" "B.Cu") (hatch edge 0.5) (connect_pads (clearance .2)) (min_thickness .15) (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints allowed)) (fill (thermal_gap .3) (thermal_bridge_width .3)) (polygon (pts {pts})))')
# Unique 01..19 wire identifiers, printed on underside to keep top assembly clear.
serial=0
for ref,pads in wire.items():
 for pin,(x,y) in pads.items():
  serial+=1
  if x<1: tx,ty,a=2.2,y,0
  elif x>14: tx,ty,a=12.8,y,0
  elif y<1: tx,ty,a=x,2.0,90
  else: tx,ty,a=x,17.8,90
  parts.append(f'(gr_text "{serial:02}" (at {100+tx} {100+ty} {a}) (layer "B.SilkS") (effects (font (size .6 .6) (thickness .1)) (justify mirror)))')
parts.append('(gr_text "ORB r02" (at 107.5 110) (layer "B.SilkS") (effects (font (size .7 .7) (thickness .12)) (justify mirror)))')
edge=[]
for x1,y1,x2,y2 in [(100,100,115,100),(115,100,115,120),(115,120,100,120),(100,120,100,100)]:edge.append(f'(gr_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width .05) (type default)) (layer "Edge.Cuts"))')
board=f'''(kicad_pcb (version 20240108) (generator "pcbnew")
(general (thickness 1.6)) (paper "A4")
(layers (0 "F.Cu" signal) (31 "B.Cu" signal) (34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (46 "B.CrtYd" user "b.courtyard") (47 "F.CrtYd" user "f.courtyard") (48 "B.Fab" user) (49 "F.Fab" user))
(setup (pad_to_mask_clearance .05) (allow_soldermask_bridges_in_footprints no) (aux_axis_origin 100 100))
(net 0 "") {' '.join(ndef(n) for n in names)}
{' '.join(parts)} {' '.join(edge)})'''
(ROOT/'cad/interface-unrouted.kicad_pcb').write_text(board)
(ROOT/'cad/wire_positions.json').write_text(json.dumps(wire,indent=2)+'\n')
# Project's explicit manufacturing constraints.
project={'board':{'design_settings':{'rules':{'min_clearance':.153,'min_track_width':.153,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_via_annular_width':.15,'min_hole_clearance':.25,'min_copper_edge_clearance':.25},'defaults':{'board_outline_line_width':.05,'copper_line_width':.2},'track_widths':[0,.2,.25],'via_dimensions':[{'diameter':.6,'drill':.3}]}},'net_settings':{'classes':[{'name':'Default','clearance':.18,'track_width':.2,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25,'bus_width':12,'line_style':0,'wire_width':6,'priority':2147483647}],'netclass_assignments':{},'netclass_patterns':[]},'meta':{'filename':'interface.kicad_pro','version':1}}
for name in ['interface','interface-unrouted']:(ROOT/f'cad/{name}.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
# Board-specific keepouts are above; all fabrication calculations use this net table.
(ROOT/'circuito.json').write_text(json.dumps(c,indent=2)+'\n')
print('Placed 17 SMD parts, 19 wire eyelets, 4 mounting holes on 15 x 20 mm')
