import bpy,bmesh,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(sys.argv[sys.argv.index('--')+1]);src=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/E2-7_quiosque.fbx'
lib=Path('D:/ProjectResort_AssetLibrary/ProjectOwned/KioskDeckF02');lib.mkdir(parents=True,exist_ok=True)
out=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Props'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(src))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');world=[o.matrix_world@v.co for v in o.data.vertices]
# Infer the deck origin from the largest horizontal face, preserving existing frame.
f=max(o.data.polygons,key=lambda f:f.area);p=[world[i] for i in f.vertices]
origin=Vector(((min(v.x for v in p)+max(v.x for v in p))/2,max(v.y for v in p)-3.4,min(v.z for v in p)-.14))
for v,w in zip(o.data.vertices,world):v.co=w-origin
o.matrix_world=Matrix.Identity(4)
bm=bmesh.new();bm.from_mesh(o.data);drop=[]
for f in bm.faces:
 c=f.calc_center_median()
 for side in (-1,1):
  for k in range(3):
   if side==-1 and k==2:continue # existing toilet volume; never cut building walls
   dx,dy=abs(c.x-side*7),abs(c.y+(1+3*k))
   if (.145<c.z<1.4 and dx<1.22 and dy<.65) or (1.4<=c.z<3.16 and dx*dx+dy*dy<4.01):
    drop.append(f);break
  if f in drop:break
bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free();o.name='KioskShellF02'
bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'KioskShellF02.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',add_leaf_bones=False)
bpy.ops.wm.save_as_mainfile(filepath=str(lib/'KioskShellF02.blend'))
(lib/'SOURCE.md').write_text(f'Project-owned source: {src}\nSHA256 original: {hashlib.sha256(src.read_bytes()).hexdigest()}\nOriginal remains untouched. Normalized origin {tuple(origin)}. Removed {len(drop)} table/stool/umbrella faces at the five existing customer tables; retained deck, kitchen, structure, roof and toilet. Runtime uses approved CC0 furniture; separate licenses. No added land, capacity or progression.\n')
print('ORIGIN',tuple(origin),'REMOVED',len(drop),'REMAINING',len(o.data.polygons))
