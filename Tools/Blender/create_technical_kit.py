"""Original technical props, metres, portable source and separate FBX exports.
Run: blender --background --factory-startup --python this.py -- --root PROJECT_ROOT
"""
import argparse
import bpy
import math
import json
import os
import random
import sys
from pathlib import Path
from mathutils import Vector

args = argparse.ArgumentParser()
args.add_argument('--root', required=True)
options = args.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
root = Path(options.root)
source = root / 'ArtSource' / 'Blender'
exports = root / 'FacilityOps' / 'Assets' / '_Game' / 'Resources' / 'Art'
source.mkdir(parents=True, exist_ok=True)
exports.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def material(name, color, metallic=0, roughness=.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    mat.diffuse_color = (*color, 1)
    return mat

steel = material('Aurora_PaintedSteel', (.27, .35, .39), .65, .36)
dark = material('Aurora_Graphite', (.035, .055, .065), .3)
metal = material('Aurora_BrushedMetal', (.58, .64, .65), .8, .25)
amber = material('Aurora_Amber', (.94, .55, .12), .15)
ivory = material('Aurora_Ivory', (.82, .84, .78))
blue = material('Aurora_Blue', (.10, .3, .36), .35)

# Small authored texture, packed in the blend and exported alongside the kit.
random.seed(41)
image = bpy.data.images.new('AuroraPaint_Albedo', width=256, height=256)
pixels = []
for y in range(256):
    for x in range(256):
        grain = random.uniform(-.018, .018)
        scratch = -.07 if (x * 13 + y * 47) % 997 < 2 else 0
        pixels.extend((.27 + grain + scratch, .35 + grain + scratch, .39 + grain + scratch, 1))
image.pixels.foreach_set(pixels)
image.filepath_raw = str(exports / 'AuroraPaint_Albedo.png')
image.file_format = 'PNG'
image.save()
image.pack()
tex = steel.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = image
steel.node_tree.links.new(tex.outputs['Color'], steel.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

groups = {}
active = None
def attach(obj, mat):
    obj.parent = active
    obj.data.materials.append(mat)
    groups[active.name].append(obj)
    return obj

def box(name, loc, size, mat, bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    attach(obj, mat)
    if bevel:
        modifier = obj.modifiers.new('Machined edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def screw(x, y, z):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.016, depth=.01, location=(x,y,z), rotation=(math.pi/2,0,0))
    obj = attach(bpy.context.object, metal)
    obj.name = 'Captive screw'
    box('Screw slot', (x,y-.006,z), (.019,.003,.003), dark, .001)

def label(text, loc, size=.06):
    curve = bpy.data.curves.new('Engraved text', 'FONT')
    curve.body = text
    curve.size = size
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = .0003
    obj = bpy.data.objects.new(text, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.pi/2, 0, 0)
    obj.parent = active
    curve.materials.append(ivory)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    groups[active.name].append(bpy.context.object)

def begin(name):
    global active
    active = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(active)
    groups[name] = [active]

begin('QD01')
box('Housing', (0,0,0), (1.15,.40,1.35), steel, .022)
box('Door gasket', (0,-.211,0), (1.10,.034,1.30), dark)
box('Door', (0,-.24,0), (1.06,.055,1.25), steel, .014)
for z in (-.42,.42):
    box('Hinge', (-.52,-.275,z), (.052,.055,.12), metal)
box('Lock handle', (.40,-.285,-.05), (.06,.044,.19), dark)
box('Label plate', (0,-.273,.39), (.76,.016,.27), dark)
label('QD-01', (0,-.287,.42), .085)
label('DISTRIBUICAO / AURORA', (0,-.287,.34), .035)
for i in range(7):
    box('Vent slot', (-.15,-.274,-.22-i*.032), (.48,.006,.012), dark, .003)
for i in range(3):
    box('Status bezel', (-.25+i*.25,-.281,.13), (.115,.025,.11), dark)
    box('Indicator', (-.25+i*.25,-.3,.13), (.06,.016,.05), amber if i==1 else blue)
for x in (-.46,.46):
    for z in (-.55,.55): screw(x,-.277,z)
box('Caution plate', (.3,-.278,-.4), (.22,.018,.16), amber)
label('VIRTUAL', (.3,-.293,-.4), .032)

begin('CT01')
box('Controller housing', (0,0,0), (.9,.34,.85), steel, .024)
box('Controller face', (0,-.19,0), (.84,.055,.78), dark, .014)
box('Diagnostic screen rim', (0,-.227,.04), (.58,.04,.32), metal)
box('Diagnostic screen', (0,-.251,.04), (.53,.018,.27), blue)
label('CT-01', (0,-.268,.10), .068)
label('COMMAND LINK', (0,-.268,.015), .028)
for x in (-.24,0,.24):
    box('Control button', (x,-.235,-.24), (.10,.04,.08), amber if x==0 else metal)
label('MODULO DE COMANDO', (0,-.23,.31), .035)
for x in (-.36,.36):
    for z in (-.32,.32): screw(x,-.23,z)

begin('LM01')
box('Driver enclosure', (0,0,0), (1.1,.3,.8), steel, .02)
box('Removable cover', (0,-.174,0), (1.04,.04,.74), metal, .009)
box('Access plate', (-.11,-.2,.05), (.65,.016,.4), dark)
label('LM-01', (-.11,-.217,.12), .078)
label('LIGHT DRIVER', (-.11,-.217,.01), .035)
for i in range(5): box('Cooling slot', (.35,-.198,-.17+i*.07), (.16,.014,.018), dark, .003)
for x in (-.44,.44):
    for z in (-.29,.29): screw(x,-.202,z)
box('Service tag', (-.18,-.205,-.25), (.43,.013,.11), amber)
label('SERVICE / 04', (-.18,-.22,-.25), .032)

manifest = {'source': 'Original geometry and paint generated for this project', 'units': 'metres', 'exports': []}
for name, objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=.02)
            bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = objects[0]
    path = exports / (name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'MESH','EMPTY'}, apply_unit_scale=True, axis_forward='-Z', axis_up='Y', bake_anim=False, path_mode='COPY', embed_textures=True)
    manifest['exports'].append({'id': name, 'file': str(path.relative_to(root)), 'mesh_objects': sum(obj.type == 'MESH' for obj in objects)})
for i, name in enumerate(groups):
    bpy.data.objects[name].location.x = (i-1)*1.7
bpy.ops.wm.save_as_mainfile(filepath=str(source / 'Aurora_TechnicalKit.blend'))
(source / 'catalog.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('FACILITY ART SUCCESS')
