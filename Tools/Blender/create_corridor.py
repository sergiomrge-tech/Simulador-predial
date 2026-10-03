"""Author the first compact service environment; export outside Unity until import."""
import argparse
import bpy
import math
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root = Path(args.root)
source = root / 'ArtSource' / 'Blender'
output = root / 'ArtSource' / 'Exports'
output.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = 'METRIC'

def material(name, rgb, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*rgb, 1)
    node.inputs['Roughness'].default_value = roughness
    return mat

plaster = material('Aurora_Plaster', (.72,.75,.71), .8)
tile_a = material('Aurora_FloorA', (.43,.49,.50), .44)
tile_b = material('Aurora_FloorB', (.47,.53,.53), .44)
grout = material('Aurora_Grout', (.13,.18,.20), .9)
dark = material('Aurora_Graphite', (.035,.055,.065), .5)
blue = material('Aurora_Blue', (.10,.30,.36), .4)
metal = material('Aurora_BrushedMetal', (.54,.60,.60), .3)
meshes = []

def box(name, unity_position, unity_size, mat, bevel=.008):
    x,y,z = unity_position
    sx,sy,sz = unity_size
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x,z,y))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (sx,sz,sy)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge highlights','BEVEL')
        mod.width = bevel
        mod.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    meshes.append(obj)
    return obj

box('Floor foundation',(0,-.15,7),(7,.3,14),grout)
for x in range(7):
    for z in range(14):
        box('Porcelain tile',(-3+x,.008,z+.5),(.988,.016,.988),tile_a if (x+z)%3 else tile_b,.003)
for side in (-1,1):
    box('Plaster wall',(side*3.5,1.6,7),(.2,3.2,14),plaster)
    box('Baseboard',(side*3.37,.16,7),(.055,.32,14),dark,.004)
    box('Blue dado',(side*3.38,1.12,7),(.025,.095,14),blue,.003)
    for z in range(2,14,3):
        box('Expansion joint',(side*3.385,1.8,z),(.018,2.65,.017),grout,.001)
    box('Upper wall cap',(side*3.33,3.02,7),(.14,.12,14),plaster)
box('Rear wall',(0,1.6,14),(7,3.2,.2),plaster)
box('Entrance wall',(0,1.6,0),(7,3.2,.2),plaster)
box('Ceiling',(0,3.3,7),(7,.2,14),plaster)
for z in (2,6,10,13.7):
    box('Ceiling beam',(0,3.14,z),(6.8,.14,.17),metal)
for side in (-1,1):
    box('Cable tray',(side*2.9,2.91,8),(.24,.065,11),dark)
    for z in range(3,14):
        box('Tray bracket',(side*3.1,2.96,z),(.58,.045,.055),metal)

# Apply UVs before joining by material to keep render batches modest.
for obj in meshes:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.01)
    bpy.ops.object.mode_set(mode='OBJECT')
for mat in (plaster,tile_a,tile_b,grout,dark,blue,metal):
    objects = [o for o in list(bpy.data.objects) if o.type == 'MESH' and o.data.materials and o.data.materials[0] == mat]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    bpy.context.object.name = mat.name
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(output/'AuroraCorridor.fbx'), use_selection=True, object_types={'MESH'}, axis_forward='-Z', axis_up='Y', bake_anim=False, apply_unit_scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'Aurora_Corridor.blend'))
(source/'corridor-catalog.json').write_text(json.dumps({'source':'Original project geometry', 'size_metres':[7,3.4,14], 'materials':7, 'export':'ArtSource/Exports/AuroraCorridor.fbx', 'uvs':True},indent=2),encoding='utf-8')
print('CORRIDOR ART SUCCESS')
