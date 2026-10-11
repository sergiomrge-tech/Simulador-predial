import bpy,math,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);lib=Path('D:/ProjectResort_AssetLibrary/ProjectOwned/ResortUmbrella');lib.mkdir(parents=True,exist_ok=True)
out=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Props';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=[];faces=[];uv=[]
steps=96;rings=14
for side in range(2):
 start=len(verts)
 for j in range(rings+1):
  f=j/rings
  for i in range(steps+1):
   a=i/steps*math.tau;sag=math.sin(a*4)**2
   r=1.2*f*(1-.025*sag*f**4)
   z=.42*(1-f**1.4)-.065*sag*f**1.6-(.003 if side else 0)
   verts.append((r*math.cos(a),r*math.sin(a),z));uv.append((.5+math.cos(a)*f*.5,.5+math.sin(a)*f*.5))
 for j in range(rings):
  for i in range(steps):
   a=start+j*(steps+1)+i;b=a+1;c=a+steps+1;d=c+1
   faces.append((a,b,d,c) if side==0 else (a,c,d,b))
mesh=bpy.data.meshes.new('CommercialCanopy');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('CommercialCanopy',mesh);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
u=mesh.uv_layers.new(name='FabricUV')
for f in mesh.polygons:
 f.use_smooth=True
 for vi,li in zip(f.vertices,f.loop_indices):u.data[li].uv=uv[vi]
mat=bpy.data.materials.new('WovenOutdoorFabric');o.data.materials.append(mat)
bpy.ops.export_scene.fbx(filepath=str(out/'UmbrellaCanopy.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',add_leaf_bones=False)
bpy.ops.wm.save_as_mainfile(filepath=str(lib/'CommercialUmbrellaCanopy.blend'))
print('Canopy authored: 2.4m diameter, 0.42m crown, eight sewn panels, double fabric skin;',len(verts),'vertices')
(lib/'SOURCE.md').write_text('Project-owned authored canopy by Codex for Project Resort, 2026-10-07. No external model content. 2.4m curved 8-panel canopy, packed portable mesh source. Generated with Tools/Blender/prepare_asset_gate_umbrella.py. Final rib mechanism/pole detail still requires visual finishing.\n')
