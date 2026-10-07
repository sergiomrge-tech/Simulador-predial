"""Read-only local source geometry audit. Never saves source blends or review images."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
LIB = Path('D:/ProjectResort_AssetLibrary')
records = []
sources = list((LIB / 'ProjectOwned/CoastalUrbanKit').glob('*.fbx'))
sources += list((LIB / 'PolyHaven_CC0/UrbanKit').glob('*/*.fbx'))
for path in sources:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    records.append(dict(source=str(path), min=low, max=high,
                        size=[high[i]-low[i] for i in range(3)],
                        polygons=sum(len(o.data.polygons) for o in meshes),
                        objects=[dict(name=o.name, materials=[m.name for m in o.data.materials if m],
                                      uv_layers=len(o.data.uv_layers)) for o in meshes]))
out = ROOT / 'Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass/source_geometry.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, indent=2), encoding='utf-8')
print('URBAN_SOURCE_AUDIT', len(records))
