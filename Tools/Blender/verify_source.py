import bpy
import json
import sys
from pathlib import Path

source = Path(bpy.data.filepath)
meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
report = {'blend': source.name, 'reopened': True, 'mesh_count': len(meshes)}
if source.stem == 'Aurora_TechnicalKit':
    assert len(meshes) >= 60, 'Missing kit geometry'
    assert all(len(obj.data.uv_layers) > 0 for obj in meshes), 'Missing UVs'
    assert all(name in bpy.data.objects for name in ('QD01', 'CT01', 'LM01')), 'Missing asset roots'
    paint = bpy.data.images.get('AuroraPaint_Albedo')
    assert paint and paint.packed_file, 'Paint must be packed in portable source'
    report.update(uvs=True, packed_paint=True, roots=['QD01','CT01','LM01'])
    filename='verification.json'
elif source.stem == 'Aurora_Corridor':
    assert len(meshes) == 7, 'Expected seven material groups'
    assert all(len(obj.data.uv_layers) > 0 for obj in meshes), 'Missing corridor UVs'
    report.update(uvs=True, material_groups=7)
    filename='corridor-verification.json'
else:
    catalog_path=source.parents[2]/'FacilityOps/Assets/_Game/Resources/World/campaign.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    assert all(any(o.name.startswith(loc['id']+' /') for o in meshes) for loc in catalog['locations']), 'Missing campaign site'
    report.update(city=catalog['city'], all_locations_present=True, locations=len(catalog['locations']), type='massing-study')
    filename='city-verification.json'
(source.parent / filename).write_text(json.dumps(report, indent=2), encoding='utf-8')
print('BLENDER SOURCE VERIFIED', report)
