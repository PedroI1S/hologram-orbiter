import bpy, bmesh, json, itertools
from pathlib import Path
from mathutils import Vector

import tempfile
out = Path(tempfile.mkdtemp(prefix='orbiter-assembly-audit-'))
root = Path(__file__).resolve().parents[3]
bpy.ops.wm.open_mainfile(filepath=str(root/'Hologram_Orbiter_v3_0/exports/fonte/Hologram_Orbiter_v3_0.blend'))
bpy.context.view_layer.update()
objects = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('MONTAGEM_')]
def bounds(o):
    v = [o.matrix_world @ Vector(x) for x in o.bound_box]
    return [[min(p[k] for p in v) for k in range(3)], [max(p[k] for p in v) for k in range(3)]]
inventory = [{'name': o.name, 'bounds': bounds(o), 'location': list(o.location)} for o in objects]
collisions = []
for a,b in itertools.combinations(objects, 2):
    ba,bb=bounds(a),bounds(b)
    if any(min(ba[1][i],bb[1][i])-max(ba[0][i],bb[0][i]) < 0.01 for i in range(3)):
        continue
    c=a.copy(); c.data=a.data.copy(); bpy.context.collection.objects.link(c)
    c.hide_viewport=False; c.hide_set(False)
    bpy.context.view_layer.objects.active=c
    m=c.modifiers.new('audit_intersection', 'BOOLEAN'); m.operation='INTERSECT'; m.solver='EXACT'; m.object=b
    bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new(); bm.from_mesh(c.data); bm.transform(c.matrix_world)
    vol=abs(bm.calc_volume(signed=True)); bm.free()
    if vol > 0.001:
        row={'a':a.name,'b':b.name,'intersection_mm3':vol,'bounds': bounds(c)}
        collisions.append(row); print('INTERSECTION',json.dumps(row),flush=True)
    bpy.data.objects.remove(c,do_unlink=True)
result={'objects':inventory,'positive_intersections':collisions}
(out/'assembly_intersections.json').write_text(json.dumps(result,indent=2))
print('ASSEMBLY_AUDIT_COMPLETE',len(objects),len(collisions),flush=True)

print('AUDIT_OUTPUT_DIR',str(out))
