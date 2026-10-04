"""Export a flat W3 material contract for Unity URP.

Run against the final W3 slice:
blender -b ArtSource/Blender/World/OldTown/W3/SantaAurora_W3_VerticalSlice.blend \
  --python Tools/Blender/export_unity_w3_materials.py -- --root .

The script is read-only and does not save the source .blend.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np


def bake_leaf_alpha(material, root):
    """Bake the authored procedural cutout in a disposable material/plane."""
    copied = material.copy()
    nt = copied.node_tree
    output = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    cut = next((n for n in nt.nodes if n.type == 'MIX_SHADER' and n.inputs[0].is_linked
                and any(l.from_node.type == 'BSDF_TRANSPARENT' for l in n.inputs[1].links)), None)
    if cut is None:
        bpy.data.materials.remove(copied)
        return None
    emission = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(cut.inputs[0].links[0].from_socket, emission.inputs['Color'])
    nt.links.new(emission.outputs[0], output.inputs['Surface'])
    image = bpy.data.images.new('UNITY_ALPHA_' + material.name, width=256, height=256, alpha=True)
    image.colorspace_settings.name = 'Non-Color'
    target = nt.nodes.new('ShaderNodeTexImage')
    target.image = image
    nt.nodes.active = target
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.object
    plane.data.materials.append(copied)
    scene = bpy.context.scene
    original_engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    try:
        bpy.ops.object.bake(type='EMIT', margin=0)
        pixels = np.array(image.pixels[:], dtype=np.float32).reshape(-1, 4)
        pixels[:, 3] = pixels[:, 0]
        pixels[:, :3] = 1.0
        image.pixels.foreach_set(pixels.ravel())
        folder = root / 'ArtSource/Blender/World/UnityExport/Textures'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (material.name + '_BaseColorAlpha.png')
        image.filepath_raw = str(path)
        image.file_format = 'PNG'
        image.save()
        return path.relative_to(root).as_posix()
    finally:
        scene.render.engine = original_engine
        mesh = plane.data
        bpy.data.objects.remove(plane, do_unlink=True)
        bpy.data.meshes.remove(mesh)
        bpy.data.materials.remove(copied)
        bpy.data.images.remove(image)

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--output", default="")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

root = Path(opts.root).resolve()
tex_lib_path = root / "ArtSource" / "Textures" / "texture_library_w3.json"
tex_lib = json.loads(tex_lib_path.read_text(encoding="utf-8"))["sets"]

used = set()
# Geometry Nodes and linked collections reference materials that do not appear
# in the instancer's own slots. Include the material datablocks of those sources.
used.update(m.name for m in bpy.data.materials if m.users > 0)
for obj in bpy.data.objects:
    if obj.type != "MESH" or obj.data is None:
        continue
    for slot in obj.material_slots:
        if slot.material is not None:
            used.add(slot.material.name)

records = []
for name in sorted(used):
    mat = bpy.data.materials.get(name)
    if mat is None:
        continue

    base_name = name[:-5] if name.endswith("_hero") else name
    family = str(mat.get("sa_family", ""))
    texture_set = str(mat.get("sa_texture_set", ""))
    texture_mode = str(mat.get("sa_texture_mode", ""))
    tile_m = float(mat.get("sa_tile_m", 1.0))
    status = str(mat.get("sa_status", ""))

    rgba = [round(float(v), 6) for v in mat.diffuse_color]
    tint = [1.0, 1.0, 1.0, rgba[3]]
    if texture_mode == "tint":
        tint = [min(1.0, rgba[0] * 1.18), min(1.0, rgba[1] * 1.18), min(1.0, rgba[2] * 1.18), rgba[3]]

    maps = []
    normal_convention = None
    if texture_set and texture_set in tex_lib:
        info = tex_lib[texture_set]
        maps = [
            {"channel": channel, "path": path}
            for channel, path in sorted(info.get("maps", {}).items())
        ]
        tile_m = float(info.get("tile_m", tile_m))
        normal_convention = info.get("normal_convention")
    if not maps:
        tint = rgba[:]
    is_cutout = False
    if family == 'vegetacao' and name.startswith('folha_'):
        alpha_path = bake_leaf_alpha(mat, root)
        if alpha_path:
            maps = [{'channel': 'BaseColor', 'path': alpha_path}]
            tile_m = 1.0
            is_cutout = True

    principled = None
    if mat.use_nodes and mat.node_tree is not None:
        for node in mat.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                principled = node
                break

    metallic = 0.0
    roughness = 0.5
    alpha = rgba[3]
    ior = 1.5
    if principled is not None:
        if "Metallic" in principled.inputs:
            metallic = float(principled.inputs["Metallic"].default_value)
        if "Roughness" in principled.inputs:
            roughness = float(principled.inputs["Roughness"].default_value)
        if "Alpha" in principled.inputs:
            alpha = float(principled.inputs["Alpha"].default_value)
        if "IOR" in principled.inputs:
            ior = float(principled.inputs["IOR"].default_value)

    is_glass = family == "vidro" or base_name in {"vidro", "vidro_vitrine", "vidro_fachada"}
    if is_glass:
        # Blender drives glass alpha by Fresnel; Unity v0.1 uses this as its face-on baseline.
        alpha = {"vidro": 0.16, "vidro_vitrine": 0.12, "vidro_fachada": 0.86}.get(base_name, alpha)

    # W3.2: authored RGBA decals (cartazes, grafites, placas, marcas) are textured transparent quads; vehicle glass and lamp lenses are translucent
    # (the interior is modelled). Both reuse the transparent URP path: base map alpha x tint alpha.
    if name.startswith("decal_w31_"):
        png = root / "ArtSource" / "Textures" / "decals_w31" / (name[len("decal_w31_"):] + ".png")
        if png.is_file():
            maps = [{"channel": "BaseColor", "path": png.relative_to(root).as_posix()}]
            tile_m, is_glass, alpha, roughness = 1.0, True, 1.0, 0.9
            rgba = [1.0, 1.0, 1.0, 1.0]
            tint = rgba[:]
            status = "decal autoral W3.1 (RGBA, transparente)"
    elif family in ("vidro_veiculo", "lente_veiculo"):
        is_glass = True
        alpha = {"vidro_veiculo_claro": 0.28, "lente_farol": 0.25, "lente_lanterna": 0.45}.get(name, 0.3)
        status = "vidro/lente de veículo translúcido (interior modelado)"

    records.append({
        "name": name,
        "baseName": base_name,
        "family": family,
        "textureSet": texture_set,
        "textureMode": texture_mode,
        "tileMeters": tile_m,
        "tint": tint,
        "diffuseColor": rgba,
        "metallic": round(metallic, 6),
        "roughness": round(roughness, 6),
        "alpha": round(alpha, 6),
        "ior": round(ior, 6),
        "isGlass": is_glass,
        "isCutout": is_cutout,
        "maps": maps,
        "normalConvention": normal_convention,
        "status": status,
    })

out = Path(opts.output).resolve() if opts.output else (
    root / "ArtSource" / "Blender" / "World" / "UnityExport" / "w3_materials.json"
)
out.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "schemaVersion": 1,
    "stage": "W3",
    "sourceBlend": Path(bpy.data.filepath).as_posix(),
    "materialCount": len(records),
    "textureLibrary": "ArtSource/Textures/texture_library_w3.json",
    "materials": records,
}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "PASS", "materials": len(records), "output": str(out)}, ensure_ascii=False))
