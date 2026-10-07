"""Remove windows intersecting entrance doors in current project FBX copies.

Run after the existing AC refinement. Library sources are never saved. Preserve
all other project geometry, UVs and material slots; retain the door lintel.
"""
from pathlib import Path
import hashlib
import json
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'FacilityOps/Assets/_Game/Resources/Art/Resort/Urban'
EVIDENCE = ROOT / 'Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_live'

def components(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    unseen = set(bm.verts)
    result = []
    while unseen:
        start = unseen.pop()
        connected, pending = {start}, [start]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other)
                    connected.add(other)
                    pending.append(other)
        points = [obj.matrix_world @ v.co for v in connected]
        low = Vector([min(p[i] for p in points) for i in range(3)])
        high = Vector([max(p[i] for p in points) for i in range(3)])
        result.append((connected, low, high))
    return bm, result

records = []
for name in ('apartamento', 'residencial_sacadas', 'sobrado'):
    path = DEST / (name + '.fbx')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    doors, windows = [], []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(('MAT_Wood', 'MAT_Glass')):
            continue
        bm, parts = components(obj)
        for verts, low, high in parts:
            if obj.name.startswith('MAT_Wood') and low.z < .1 and 2 < high.z < 2.5:
                doors.append((low.copy(), high.copy()))
            if obj.name.startswith('MAT_Glass') and high.z < 2.8 and high.y - low.y < .1:
                windows.append((low.copy(), high.copy()))
        bm.free()
    conflicts = [(lo, hi) for lo, hi in windows if any(
        min(hi.x, dhi.x) - max(lo.x, dlo.x) > .1 and
        min(hi.z, dhi.z) - max(lo.z, dlo.z) > .1 and
        abs((lo.y + hi.y - dlo.y - dhi.y) / 2) < .1
        for dlo, dhi in doors)]
    if len(conflicts) != 1:
        raise RuntimeError((name, 'expected exactly one entrance/window conflict', len(conflicts)))
    removed = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(('MAT_Glass', 'MAT_Trim')):
            continue
        bm, parts = components(obj)
        delete = []
        for verts, low, high in parts:
            centre, size = (low + high) / 2, high - low
            for wlo, whi in conflicts:
                wc, ws = (wlo + whi) / 2, whi - wlo
                glass = obj.name.startswith('MAT_Glass') and (centre - wc).length < .01
                # The four detached window-frame bars; do not remove the door lintel.
                frame = obj.name.startswith('MAT_Trim') and abs(centre.y - wc.y) < .05 and (
                    (abs(abs(centre.x - wc.x) - (ws.x / 2 + .07)) < .015 and abs(centre.z - wc.z) < .015) or
                    (abs(centre.x - wc.x) < .015 and abs(abs(centre.z - wc.z) - (ws.z / 2 + .08)) < .015))
                if glass or frame:
                    delete.extend(verts)
                    removed.append(dict(part=obj.name, centre=list(centre), size=list(size)))
        if delete:
            bmesh.ops.delete(bm, geom=delete, context='VERTS')
            bm.to_mesh(obj.data)
            obj.data.update()
        bm.free()
    if len(removed) != 5:
        raise RuntimeError((name, 'expected glass and four frame bars', len(removed)))
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=False, object_types={'MESH'},
        apply_unit_scale=True, bake_space_transform=False, add_leaf_bones=False,
        mesh_smooth_type='FACE', use_mesh_modifiers=True, bake_anim=False)
    records.append(dict(asset=name, before_sha256=before,
        after_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), removed=removed))
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / 'entrance_correction.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print('URBAN_ENTRANCES_CORRECTED', len(records))
