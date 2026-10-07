"""Prepare the already downloaded CC0 Poly Haven furniture with the Resort FBX conventions.
Run in Blender: --background --factory-startup --python this_file -- SOURCE_DIRECTORY PROJECT_ROOT
Original downloaded FBX/textures remain unchanged. A normalized editable blend is saved.
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector, Matrix
source, root = map(Path, sys.argv[sys.argv.index('--')+1:])
out=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Furniture'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(source/'outdoor_table_chair_set_01_2k.fbx'))
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.name.endswith('_02'):
  bpy.data.objects.remove(ob,do_unlink=True); continue
 kind='Table' if ob.name.endswith('_table') else 'Chair'
 # Remove the layout rotation/offset, retaining the actual mesh and UVs.
 rot=Matrix.Rotation(-ob.rotation_euler.z,4,'Z')
 points=[rot @ (ob.matrix_world @ v.co) for v in ob.data.vertices]
 lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
 hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
 center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 points=[p-center for p in points]
 # The tall back must face -Y: the normalized chair looks +Y (+Z in Unity).
 if kind=='Chair':
  back=[p.y for p in points if p.z>0.65]
  if sum(back)/len(back)>0: points=[Vector((-p.x,-p.y,p.z)) for p in points]
 ob.matrix_world=Matrix.Identity(4)
 for v,p in zip(ob.data.vertices,points): v.co=p
 ob.name='S1_Realistic'+kind
 bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
 bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(out/(kind+'.fbx')),use_selection=True,object_types={'MESH'},global_scale=1.0,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,path_mode='AUTO',add_leaf_bones=False)
 print('PREPARED',kind,'bounds',tuple(hi-lo),'vertices',len(points))
# Embed the original texture sources in the editable source file.
for kind in ('chair','table'):
 mat=bpy.data.materials.get('outdoor_table_chair_set_01_'+kind)
 if mat:
  mat.use_nodes=True
  for channel in ('diff','nor_gl','rough','metal'):
   image=bpy.data.images.load(str(source/'Textures'/('outdoor_table_chair_set_01_'+kind+'_'+channel+'_2k.png')))
   node=mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image; node.label=channel
bpy.ops.file.pack_all()
blend=root/'ArtSource/Blender/Resort/CC0_Furniture_Normalized.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))