"""Remove embedded cuboid AC placeholders from project-owned building copies.
Original editable blends/FBXs and all review PNGs stay untouched. UVs and material
groups are preserved; scanned condensers are placed by CoastalUrbanProps.
"""
from pathlib import Path
import hashlib
import json
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('D:/ProjectResort_AssetLibrary/ProjectOwned/CoastalUrbanKit')
DEST = ROOT / 'FacilityOps/Assets/_Game/Resources/Art/Resort/Urban'
DEFS = {
    'casa_terrea': (9,13,[],(3.2,3.15)),
    'sobrado': (9,14,[1.8,4.75],(3.1,5.2)),
    'loja': (10,12,[],None),
    'misto': (10,15,[1.8,4.9],(3.4,5.25)),
    'apartamento': (11,16,[1.75,4.75,7.75],(0,6.45)),
    'hotel': (12,16,[1.75,4.8,7.8],None),
    'townhouse': (6.4,14,[1.8,4.8],(1.8,5.4)),
    'residencial_sacadas': (12,15,[1.8,4.8],None),
}
records = []
for name,(width,depth,rear,facing) in DEFS.items():
    source = SOURCE / (name + '.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    targets = []
    if facing:
        x,y = facing
        targets.append(Vector((x,-depth/2-.34,y)))
        targets += [Vector((x+k*.09,-depth/2-.50,y)) for k in range(-3,4)]
    if rear:
        x,y = width*.30,rear[-1]+.25
        targets.append(Vector((x,depth/2+.22,y)))
        targets += [Vector((x+k*.10,depth/2+.39,y)) for k in range(-2,3)]
    removed = []
    for obj in list(bpy.context.scene.objects):
        if obj.type != 'MESH' or not (obj.name.startswith('MAT_Trim') or obj.name.startswith('MAT_Metal')): continue
        bm = bmesh.new(); bm.from_mesh(obj.data)
        unseen = set(bm.verts); delete = []
        while unseen:
            start = unseen.pop(); connected = {start}; pending = [start]
            while pending:
                v = pending.pop()
                for edge in v.link_edges:
                    other = edge.other_vert(v)
                    if other in unseen:
                        unseen.remove(other); connected.add(other); pending.append(other)
            points = [obj.matrix_world @ v.co for v in connected]
            low = Vector([min(p[i] for p in points) for i in range(3)])
            high = Vector([max(p[i] for p in points) for i in range(3)])
            centre = (low+high)/2
            if any((centre-target).length < .015 for target in targets):
                delete.extend(connected); removed.append(list(centre))
        if delete:
            bmesh.ops.delete(bm, geom=delete, context='VERTS')
            bm.to_mesh(obj.data); obj.data.update()
        bm.free()
    if len(removed) != len(targets): raise RuntimeError((name, 'unexpected AC component count', len(removed), len(targets)))
    output = DEST / (name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=str(output), use_selection=False, object_types={'MESH'},
                             apply_unit_scale=True, bake_space_transform=False, add_leaf_bones=False,
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, bake_anim=False)
    records.append(dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        output=str(output.relative_to(ROOT)), removed_ac_components=removed))
out = ROOT / 'Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass/building_refinement.json'
out.write_text(json.dumps(records, indent=2), encoding='utf-8')
print('URBAN_BUILDINGS_REFINED', len(records), 'removed_parts', sum(len(r['removed_ac_components']) for r in records))
