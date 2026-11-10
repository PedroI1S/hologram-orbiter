"""Tie the main underside ground area to an existing GND trace, outside paste pads."""
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'cad/interface.kicad_pcb';b=pcbnew.LoadBoard(str(p));net=b.FindNet('/GND')
for x,y,px,py in [(103.6,113.75,102.825,113.75)]:
 if any(isinstance(t,pcbnew.PCB_VIA) and abs(pcbnew.ToMM(t.GetPosition().x)-x)<1e-5 and abs(pcbnew.ToMM(t.GetPosition().y)-y)<1e-5 for t in b.GetTracks()):continue
 v=pcbnew.PCB_VIA(b);v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)));v.SetWidth(pcbnew.FromMM(.6));v.SetDrill(pcbnew.FromMM(.3));v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetViaType(pcbnew.VIATYPE_THROUGH);v.SetNet(net);b.Add(v)
 t=pcbnew.PCB_TRACK(b);t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(px),pcbnew.FromMM(py)));t.SetEnd(v.GetPosition());t.SetWidth(pcbnew.FromMM(.2));t.SetLayer(pcbnew.F_Cu);t.SetNet(net);b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(p),b)
