from pathlib import Path
import sexpdata as sx
p=Path(__file__).resolve().parents[1]/'cad'
for filename in ['interface.kicad_sch','Orbiter.kicad_sym']:
 f=p/filename;a=sx.load(open(f))
 def visit(x):
  if not isinstance(x,list):return
  if x and str(x[0])=='property':
   for ef in [v for v in x if isinstance(v,list) and v and str(v[0])=='effects']:
    h=[v for v in ef if isinstance(v,list) and v and str(v[0])=='hide']
    for v in h:ef.remove(v);x.append(v)
  for v in x:visit(v)
 visit(a)
 for v in a:
  if isinstance(v,list) and str(v[0])=='version':v[1]=20260101 if filename.endswith('kicad_sch') else 20241209
 if filename.endswith('kicad_sch'):
  def snap(v):return round(round(v/1.27)*1.27,6)
  for item in a:
   if not isinstance(item,list) or not item:continue
   if str(item[0]) in ['symbol','label']:
    at=next(v for v in item if isinstance(v,list) and str(v[0])=='at');dx=snap(at[1])-at[1];dy=snap(at[2])-at[2];at[1]=snap(at[1]);at[2]=snap(at[2])
    if str(item[0])=='symbol':
     for prop in [v for v in item if isinstance(v,list) and str(v[0])=='property']:
      pos=next(v for v in prop if isinstance(v,list) and str(v[0])=='at');pos[1]+=dx;pos[2]+=dy
   elif str(item[0])=='wire':
    pts=next(v for v in item if isinstance(v,list) and str(v[0])=='pts')
    for pt in pts[1:]:pt[1]=snap(pt[1]);pt[2]=snap(pt[2])
 f.write_text(sx.dumps(a)+'\n')
