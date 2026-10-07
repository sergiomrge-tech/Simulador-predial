from pathlib import Path
import bpy, bmesh, json
from mathutils import Vector
root=Path('D:/sergi/Documents/Simulador-predial')
records=[]
for path in (root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Urban').glob('*.fbx'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or not obj.name.startswith(('MAT_Wood','MAT_Glass','MAT_Trim')): continue
  bm=bmesh.new(); bm.from_mesh(obj.data); unseen=set(bm.verts)
  while unseen:
   v=unseen.pop(); component={v}; pending=[v]
   while pending:
    for edge in pending.pop().link_edges:
     other=edge.other_vert(next(v for v in edge.verts if v in component)) if False else None
     for other in edge.verts:
      if other in unseen: unseen.remove(other); component.add(other); pending.append(other)
   points=[obj.matrix_world@v.co for v in component]
   lo=Vector([min(p[i] for p in points) for i in range(3)]); hi=Vector([max(p[i] for p in points) for i in range(3)])
   if hi.z<2.8 and (lo.y+hi.y)/2<0:
    records.append(dict(asset=path.stem,part=obj.name,min=list(lo),max=list(hi),center=list((hi+lo)/2),size=list(hi-lo)))
  bm.free()
(root/'Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_live/openings_audit.json').write_text(json.dumps(records,indent=2))
print('OPENINGS_AUDIT',len(records))
