"""Apply board presentation/keepout details and refill zones using KiCad."""
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'cad/interface.kicad_pcb';b=pcbnew.LoadBoard(str(p))
for z in b.Zones():
 if z.GetIsRuleArea():z.SetDoNotAllowPads(False) # NPTH mounting holes reside inside screw-head areas.
for t in b.GetDrawings():
 if isinstance(t,pcbnew.PCB_TEXT):
  t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
  pos=t.GetPosition();x,y=pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y)
  if y==102:y=102.2
  if y==117.8:y=117.5
  t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(p),b)
print('Applied 0.8mm silkscreen text and filled ground plane')
