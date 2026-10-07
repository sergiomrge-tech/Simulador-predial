"""Pack the approved urban scans for URP; run in Blender background mode.

Source library stays untouched. Only promoted project copies receive 1K maps.
URP metallic mask: R=metalness, G=occlusion (1), B=0, A=1-roughness.
"""
from pathlib import Path
import json
import bpy
import numpy as np

ROOT = Path(r"D:\sergi\Documents\Simulador-predial")
DEST = ROOT / "FacilityOps/Assets/_Game/Resources/Art/Resort/UrbanProps"
EVIDENCE = ROOT / "Docs/PROJECT_RESORT_EXECUTION/Evidence/CODEX_2026-10-07/urban_pass"


def load_pixels(path):
    image = bpy.data.images.load(str(path), check_existing=False)
    image.colorspace_settings.name = 'Non-Color'
    image.scale(1024, 1024)
    values = np.empty(1024 * 1024 * 4, dtype=np.float32)
    image.pixels.foreach_get(values)
    bpy.data.images.remove(image)
    return values.reshape((1024, 1024, 4))


def save_map(path, values):
    image = bpy.data.images.new(path.stem, width=1024, height=1024, alpha=True)
    image.colorspace_settings.name = 'Non-Color'
    image.pixels.foreach_set(values.astype(np.float32).ravel())
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    bpy.data.images.remove(image)


records = []
for folder in sorted(DEST.iterdir()):
    if not folder.is_dir():
        continue
    textures = folder / 'textures'
    for diffuse in sorted(textures.glob('*_diff_2k.*')):
        stem = diffuse.name.split('_diff_2k')[0]
        normals = list(textures.glob(stem + '_nor_gl_2k.*'))
        rough = list(textures.glob(stem + '_rough_2k.*'))
        metal = list(textures.glob(stem + '_metal_2k.*'))
        if not normals or not rough:
            continue
        save_map(textures / (stem + '_Normal.png'), load_pixels(normals[0]))
        mask = np.ones((1024, 1024, 4), dtype=np.float32)
        mask[:, :, 0] = load_pixels(metal[0])[:, :, 0] if metal else 0
        mask[:, :, 2] = 0
        mask[:, :, 3] = 1 - np.clip(load_pixels(rough[0])[:, :, 0], 0, 1)
        save_map(textures / (stem + '_Mask.png'), mask)
        records.append({'asset': folder.name, 'stem': stem, 'size': 1024,
                        'normal_source': str(normals[0]), 'roughness_source': str(rough[0]),
                        'metal_source': str(metal[0]) if metal else None})
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / 'pbr_packing.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print('CODEX_URBAN_PACKED', len(records))
