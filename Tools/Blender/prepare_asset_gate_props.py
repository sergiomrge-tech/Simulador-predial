import bpy,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(sys.argv[sys.argv.index('--')+1]);src=Path('D:/ProjectResort_AssetLibrary/PolyHaven_CC0/WineBottles01_1K')
out=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Props';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'wine_bottles_01_1k.blend'))
ob=bpy.data.objects['wine_bottles_01_bordeaux']
for other in list(bpy.context.scene.objects):
 if other!=ob:bpy.data.objects.remove(other,do_unlink=True)
# Keep exterior, cork and paper; remove invisible liquid volume to reduce overdraw.
import bmesh
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==2],context='FACES');bm.to_mesh(ob.data);bm.free()
points=[ob.matrix_world@v.co for v in ob.data.vertices];lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);origin=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
ob.matrix_world=Matrix.Identity(4)
for v,p in zip(ob.data.vertices,points):v.co=p-origin
ob.name='WineBottle';bpy.context.view_layer.objects.active=ob;ob.select_set(True)
# Preserve original atlas UVs for source sampling; bake runtime atlas on a second layer.
original=ob.data.uv_layers.active.name
atlas=ob.data.uv_layers.new(name='RuntimeAtlas');ob.data.uv_layers.active=atlas
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1
scene.render.bake.margin=8
# Bake original colour and roughness to emission, with original UVs pinned explicitly.
for channel in ['BaseColor','Roughness']:
 image=bpy.data.images.new('Bottle_'+channel,512,512)
 for mat in ob.data.materials:
  if mat is None:continue
  nodes=mat.node_tree.nodes;links=mat.node_tree.links
  for n in list(nodes):
   if n.type=='TEX_IMAGE':
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map=original;links.new(uv.outputs['UV'],n.inputs['Vector'])
  bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
  output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
  emission=nodes.new('ShaderNodeEmission')
  inp=bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'] if bs else None
  if inp is not None and inp.is_linked:links.new(inp.links[0].from_socket,emission.inputs['Color'])
  elif inp is not None:emission.inputs['Color'].default_value=inp.default_value if channel=='BaseColor' else (*([inp.default_value]*3),1)
  else:emission.inputs['Color'].default_value=(.08,.035,.012,1) if channel=='BaseColor' else (.25,.25,.25,1)
  # Make the outer glass amber green rather than a colourless empty shell.
  if channel=='BaseColor' and 'glass' in mat.name:
   emission.inputs['Color'].default_value=(.045,.065,.015,1)
   for l in list(emission.inputs['Color'].links):links.remove(l)
  links.new(emission.outputs[0],output.inputs['Surface'])
  target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
 bpy.ops.object.bake(type='EMIT')
 image.filepath_raw=str(out/('bottle_'+channel+'.png'));image.file_format='PNG';image.save()
# Smooth geometry with atlas UVs; use one material (one draw per instance).
ob.data.uv_layers.remove(ob.data.uv_layers[original]);ob.data.uv_layers.active=ob.data.uv_layers['RuntimeAtlas']
mat=bpy.data.materials.new('BottlePBR');ob.data.materials.clear();ob.data.materials.append(mat)
for face in ob.data.polygons:face.material_index=0;face.use_smooth=True
bpy.ops.export_scene.fbx(filepath=str(out/'WineBottle.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',add_leaf_bones=False)
print('BOTTLE',tuple(hi-lo),len(ob.data.vertices),len(ob.data.polygons))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/'ArtSource/Blender/Resort/CC0_WineBottle_Runtime.blend'))
