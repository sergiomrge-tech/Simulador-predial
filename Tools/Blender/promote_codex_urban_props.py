"""Stage selected CC0 scan variants and URP maps. Library files are read-only.
Run with Blender --background --factory-startup --python this_file.
The modular kit is exported as individual pieces, never as a parts catalogue in-world.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import uuid
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('D:/ProjectResort_AssetLibrary/PolyHaven_CC0/UrbanKit')
DEST = ROOT / 'FacilityOps/Assets/_Game/Resources/Art/Resort/UrbanProps'
EVIDENCE = ROOT / 'Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass'
MODEL_META = (DEST / 'utility_box_01_2K/utility_box_01_2k.fbx.meta').read_text()
TEXTURE_ROOT = ROOT / 'FacilityOps/Assets/_Game/Resources/Art/Resort/Textures'
NORMAL_META = (TEXTURE_ROOT / 'urban_asphalt_Normal.jpg.meta').read_text()
MASK_META = (TEXTURE_ROOT / 'urban_asphalt_Mask.png.meta').read_text()
COLOR_META = (TEXTURE_ROOT / 'urban_asphalt_BaseColor.jpg.meta').read_text()
SELECTIONS = {
    'exterior_aircon_unit_2K': [('exterior_aircon_unit_2k', ['exterior_aircon_unit'])],
    'fire_hydrant_2K': [('fire_hydrant_2k', ['fire_hydrant', 'fire_hydrant_cap_01', 'fire_hydrant_cap_02', 'fire_hydrant_cap_03', 'fire_hydrant_chain'])],
    'painted_wooden_bench_2K': [('painted_wooden_bench_2k', None)],
    'planter_box_01_2K': [('planter_box_01_2k', None)],
    'rollershutter_door_2K': [('rollershutter_door_2k', ['rollershutter_door'])],
    'rollershutter_window_01_2K': [('rollershutter_window_01_2k', ['rollershutter_window_01'])],
    'standing_chalkboard_01_2K': [('standing_chalkboard_01_2k', None)],
    'street_lamp_01_2K': [('street_lamp_01_2k', None)],
    'street_lamp_02_2K': [('street_lamp_02_2k', None)],
    'utility_box_01_2K': [('utility_box_01_2k', None)],
    'water_manhole_cover_2K': [('water_manhole_cover_2k', None)],
    'modular_metal_gutter_2K': [('gutter_section', ['modular_metal_gutter']),
                                ('downpipe', ['modular_metal_gutter_section'])],
}

def meta(path, template):
    file = Path(str(path) + '.meta')
    guid = re.search(r'^guid: (.+)$', file.read_text(), re.M).group(1) if file.exists() else uuid.uuid4().hex
    text = re.sub(r'^guid: .+$', 'guid: ' + guid, template, flags=re.M)
    if path.suffix == '.fbx':
        text = text.replace('importAnimation: 1', 'importAnimation: 0').replace('importCameras: 1', 'importCameras: 0').replace('importLights: 1', 'importLights: 0')
    file.write_text(text, encoding='utf-8')

def pixels(path, color=False):
    im = bpy.data.images.load(str(path), check_existing=False)
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    im.scale(1024, 1024)
    data = np.empty(1024 * 1024 * 4, dtype=np.float32)
    im.pixels.foreach_get(data); bpy.data.images.remove(im)
    return data.reshape(1024, 1024, 4)

def save(path, data, color=False):
    im = bpy.data.images.new(path.stem, width=1024, height=1024, alpha=True)
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    im.pixels.foreach_set(data.astype(np.float32).ravel())
    im.filepath_raw = str(path); im.file_format = 'PNG'; im.save(); bpy.data.images.remove(im)
    meta(path, COLOR_META if color else NORMAL_META if '_Normal' in path.stem else MASK_META)

records = []
for folder, exports in SELECTIONS.items():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    source = next((SOURCE / folder).glob('*.fbx'))
    bpy.ops.import_scene.fbx(filepath=str(source))
    all_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    target = DEST / folder; target.mkdir(parents=True, exist_ok=True)
    textures = target / 'textures'; textures.mkdir(exist_ok=True)
    used_materials = set()
    for filename, names in exports:
        objects = [o for o in all_objects if names is None or o.name in names]
        if names is not None and len(objects) != len(names): raise RuntimeError((folder, names))
        points = [o.matrix_world @ Vector(p) for o in objects for p in o.bound_box]
        low = Vector([min(p[i] for p in points) for i in range(3)])
        high = Vector([max(p[i] for p in points) for i in range(3)])
        # Canonical centre in XY, feet at Z=0; keep metre scale and source UVs.
        shift = Vector(((low.x + high.x)/2, (low.y + high.y)/2, low.z))
        bpy.ops.object.select_all(action='DESELECT')
        original_matrices = {o: o.matrix_world.copy() for o in objects}
        for o in objects:
            o.matrix_world.translation -= shift; o.select_set(True)
            used_materials.update(m.name.split('.')[0] for m in o.data.materials if m)
        output = target / (filename + '.fbx')
        bpy.ops.export_scene.fbx(filepath=str(output), use_selection=True, object_types={'MESH'},
                                 add_leaf_bones=False, bake_anim=False, use_mesh_modifiers=True)
        meta(output, MODEL_META)
        records.append(dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            output=str(output.relative_to(ROOT)), selected=[o.name for o in objects],
                            size=list(high-low), polygons=sum(len(o.data.polygons) for o in objects)))
        for o, matrix in original_matrices.items(): o.matrix_world = matrix
    for stem in sorted(used_materials):
        library_maps = SOURCE / folder / 'textures'
        diffuse = list(library_maps.glob(stem + '_diff_2k.*'))
        if not diffuse: continue  # glass/bulb use explicit URP material constants
        save(textures / (stem + '_BaseColor.png'), pixels(diffuse[0], color=True), color=True)
        normals = list(library_maps.glob(stem + '_nor_gl_2k.*'))
        if normals: save(textures / (stem + '_Normal.png'), pixels(normals[0]))
        rough = list(library_maps.glob(stem + '_rough_2k.*'))
        metal = list(library_maps.glob(stem + '_metal_2k.*'))
        ao = list(library_maps.glob(stem + '_ao_2k.*'))
        mask = np.ones((1024, 1024, 4), dtype=np.float32)
        mask[:,:,0] = pixels(metal[0])[:,:,0] if metal else 0
        mask[:,:,1] = pixels(ao[0])[:,:,0] if ao else 1
        mask[:,:,2] = 0
        mask[:,:,3] = 1-np.clip(pixels(rough[0])[:,:,0],0,1) if rough else .25
        save(textures / (stem + '_Mask.png'), mask)
    license_file = SOURCE / folder / 'LICENSE.txt'
    if license_file.exists(): shutil.copy2(license_file, target / 'LICENSE.txt')
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / 'promoted_assets.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print('URBAN_PROMOTED', len(records))
