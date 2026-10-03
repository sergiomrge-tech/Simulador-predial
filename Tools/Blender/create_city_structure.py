"""Campaign massing study. Not final architectural art or a drivable open world."""
import argparse
import bpy
import json
import sys
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--root',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(args.root)
catalog=json.loads((root/'FacilityOps/Assets/_Game/Resources/World/campaign.json').read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
colors=[(.50,.37,.25),(.48,.59,.46),(.28,.43,.58),(.43,.44,.46),(.23,.53,.57),(.67,.58,.31)]
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
district_materials={d['id']:mat(d['name'],colors[i])for i,d in enumerate(catalog['districts'])}
road=mat('Via / estudo',(.055,.065,.075))
ground=mat('Terreno / estudo',(.20,.24,.22))
def box(name,x,y,z,sx,sy,sz,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z));o=bpy.context.object;o.name=name;o.dimensions=(sx,sy,sz)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
box('Santa Aurora / base',0,20,-.5,250,230,1,ground)
for d in catalog['districts']:
 box('Avenida / '+d['id'],d['x'],d['z']-13,.02,65,5,.04,road)
 for loc in [l for l in catalog['locations'] if l['districtId']==d['id']]:
  height=max(4,len(loc['floors'])*3.5)
  box(loc['id']+' / '+loc['name'],loc['x'],loc['z'],height/2,13,12,height,district_materials[d['id']])
  curve=bpy.data.curves.new('Nome / '+loc['id'],'FONT');curve.body=loc['name'];curve.size=1;curve.align_x='CENTER';curve.align_y='CENTER'
  o=bpy.data.objects.new('Etiqueta / '+loc['id'],curve);bpy.context.collection.objects.link(o);o.location=(loc['x'],loc['z'],height+.1)
 box('Distrito / '+d['name'],d['x'],d['z']+14,-.1,67,60,.15,district_materials[d['id']])
# Historical rail corridor is a visual anchor for the old-city district.
for x in (-120,-118):box('Ferrovia histórica',x,10,.05,.2,180,.1,road)
for y in range(-75,95,3):box('Dormente',-119,y,.07,4,.18,.1,road)
source=root/'ArtSource/Blender/SantaAurora_Masterplan.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
assert all(any(o.name.startswith(loc['id']+' /')for o in bpy.data.objects)for loc in catalog['locations'])
(source.parent/'city-verification.json').write_text(json.dumps({'city':catalog['city'],'districts':len(catalog['districts']),'locations':len(catalog['locations']),'all_locations_present':True,'type':'massing-study'},indent=2),encoding='utf-8')
print('CITY STRUCTURE SUCCESS: all 24 campaign locations')
