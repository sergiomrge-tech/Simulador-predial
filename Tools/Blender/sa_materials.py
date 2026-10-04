"""Santa Aurora PBR material library, W1.5 base (requires bpy).

Every material is procedural (no flat colours): colour variation, roughness map, bump -> normal,
cavity grime (AO), ground dirt and optional per-instance tint. Each material also carries an unlinked
frame of named texture slots (Base Color / Normal / Roughness / Metallic / AO) that W3 will fill with
authored textures under ArtSource/Textures/<material>/. Slots have no image assigned, so they never
create missing data. Status is recorded on each material and in ArtSource/Materials/material_library_v1.json.
"""
import json
from pathlib import Path

import bpy

CHANNELS = ["BaseColor", "Normal", "Roughness", "Metallic", "AO"]

# pattern: noise | brick | tiles | wave | corrugated | none
LIB = {
    "concreto":             {"family": "concreto", "c1": (.56, .55, .52), "c2": (.42, .41, .39), "rough": (.78, .95), "scale": 1.8, "bump": .25, "pattern": "noise", "grime": .55, "dirt": .35, "texel": 512},
    "concreto_pintado":     {"family": "concreto", "c1": (.70, .69, .64), "c2": (.58, .57, .53), "rough": (.70, .88), "scale": 1.4, "bump": .15, "pattern": "noise", "grime": .5, "dirt": .45, "tint": (.03, .12), "texel": 512},
    "reboco_antigo":        {"family": "reboco", "c1": (.78, .68, .52), "c2": (.62, .52, .40), "rough": (.80, .95), "scale": 1.2, "bump": .35, "pattern": "noise", "grime": .7, "dirt": .55, "tint": (.18, .2), "sat": 1.1, "texel": 512},
    "reboco_pintado":       {"family": "reboco", "c1": (.80, .66, .48), "c2": (.70, .56, .40), "rough": (.72, .90), "scale": 1.0, "bump": .25, "pattern": "noise", "grime": .6, "dirt": .5, "tint": (.38, .22), "sat": 1.2, "texel": 512},
    "reboco_pastilha":      {"family": "reboco", "c1": (.74, .70, .62), "c2": (.62, .58, .52), "rough": (.45, .70), "scale": 1.0, "bump": .3, "pattern": "tiles", "tile": (.1, .1, .008), "grime": .55, "dirt": .4, "texel": 1024},
    "pedra_reboco_historico": {"family": "reboco", "c1": (.78, .74, .66), "c2": (.66, .62, .55), "rough": (.75, .92), "scale": 1.0, "bump": .4, "pattern": "tiles", "tile": (.9, .45, .012), "grime": .75, "dirt": .6, "texel": 512},
    "tijolo_aparente":      {"family": "tijolo", "c1": (.52, .24, .15), "c2": (.40, .17, .11), "rough": (.80, .95), "scale": 1.0, "bump": .6, "pattern": "brick", "tile": (.23, .075, .012), "mortar": (.62, .58, .52), "grime": .6, "dirt": .5, "texel": 512},
    "tijolo_pintado":       {"family": "tijolo", "c1": (.76, .70, .62), "c2": (.68, .62, .55), "rough": (.70, .88), "scale": 1.0, "bump": .45, "pattern": "brick", "tile": (.23, .075, .012), "mortar": (.60, .56, .50), "grime": .55, "dirt": .5, "tint": (.15, .15), "texel": 512},
    "asfalto":              {"family": "asfalto", "c1": (.10, .10, .105), "c2": (.06, .06, .065), "rough": (.82, .96), "scale": 4.0, "bump": .2, "pattern": "noise", "grime": .2, "dirt": 0.0, "texel": 256},
    "asfalto_gasto":        {"family": "asfalto", "c1": (.17, .17, .17), "c2": (.09, .09, .095), "rough": (.85, .98), "scale": 2.5, "bump": .25, "pattern": "noise", "patches": True, "grime": .2, "dirt": 0.0, "texel": 256},
    "calcada":              {"family": "concreto", "c1": (.60, .58, .55), "c2": (.48, .46, .44), "rough": (.80, .95), "scale": 1.0, "bump": .4, "pattern": "tiles", "tile": (.4, .4, .006), "grime": .5, "dirt": .3, "texel": 512},
    "meio_fio":             {"family": "concreto", "c1": (.66, .65, .62), "c2": (.52, .51, .49), "rough": (.70, .90), "scale": 2.0, "bump": .3, "pattern": "noise", "grime": .6, "dirt": .5, "texel": 512},
    "metal_galvanizado":    {"family": "metal", "c1": (.62, .63, .64), "c2": (.50, .51, .52), "rough": (.30, .55), "scale": 6.0, "bump": .05, "pattern": "noise", "metal": 1.0, "grime": .45, "dirt": .3, "texel": 1024},
    "aco_pintado_verde":    {"family": "aco_pintado", "c1": (.12, .28, .18), "c2": (.09, .22, .14), "rough": (.40, .65), "scale": 3.0, "bump": .08, "pattern": "noise", "chips": True, "grime": .5, "dirt": .4, "texel": 1024},
    "aco_pintado_cinza":    {"family": "aco_pintado", "c1": (.36, .38, .40), "c2": (.28, .30, .32), "rough": (.40, .65), "scale": 3.0, "bump": .08, "pattern": "noise", "chips": True, "grime": .5, "dirt": .4, "texel": 1024},
    "ferrugem":             {"family": "ferrugem", "c1": (.42, .20, .09), "c2": (.25, .11, .05), "rough": (.75, .95), "scale": 5.0, "bump": .5, "pattern": "noise", "metal": .3, "grime": .4, "dirt": .2, "texel": 1024},
    "aluminio":             {"family": "metal", "c1": (.72, .73, .74), "c2": (.62, .63, .64), "rough": (.28, .45), "scale": 8.0, "bump": .03, "pattern": "noise", "metal": .95, "grime": .4, "dirt": .2, "texel": 1024},
    "madeira_pintada":      {"family": "madeira", "c1": (.36, .20, .12), "c2": (.28, .15, .09), "rough": (.55, .80), "scale": 1.0, "bump": .25, "pattern": "wave", "chips": True, "grime": .55, "dirt": .35, "tint": (.12, .2), "texel": 1024},
    "madeira_crua":         {"family": "madeira", "c1": (.48, .34, .22), "c2": (.34, .23, .14), "rough": (.65, .85), "scale": 1.0, "bump": .35, "pattern": "wave", "grime": .5, "dirt": .3, "texel": 1024},
    "vidro":                {"family": "vidro", "c1": (.08, .10, .11), "c2": (.05, .07, .08), "rough": (.04, .12), "scale": 2.0, "bump": .0, "pattern": "noise", "grime": .3, "dirt": .1, "spec": .9, "texel": 512},
    "vidro_vitrine":        {"family": "vidro", "c1": (.16, .19, .20), "c2": (.11, .13, .14), "rough": (.03, .08), "scale": 2.0, "bump": .0, "pattern": "noise", "grime": .2, "dirt": .1, "spec": 1.0, "texel": 512},
    "ceramica_telha":       {"family": "ceramica", "c1": (.56, .26, .16), "c2": (.42, .18, .11), "rough": (.70, .92), "scale": 1.0, "bump": .7, "pattern": "tiles", "tile": (.22, .38, .02), "grime": .7, "dirt": 0.0, "tint": (.04, .12), "texel": 512},
    "ceramica_piso":        {"family": "ceramica", "c1": (.70, .66, .60), "c2": (.60, .56, .50), "rough": (.25, .45), "scale": 1.0, "bump": .3, "pattern": "tiles", "tile": (.3, .3, .004), "grime": .4, "dirt": .2, "texel": 512},
    "telha_fibrocimento":   {"family": "cobertura", "c1": (.58, .58, .56), "c2": (.44, .44, .43), "rough": (.80, .95), "scale": 1.0, "bump": .8, "pattern": "corrugated", "grime": .8, "dirt": 0.0, "texel": 512},
    "telha_metalica":       {"family": "cobertura", "c1": (.55, .57, .58), "c2": (.45, .46, .47), "rough": (.35, .60), "scale": 1.0, "bump": .6, "pattern": "corrugated", "metal": .9, "grime": .6, "dirt": 0.0, "texel": 512},
    "plastico":             {"family": "plastico", "c1": (.82, .82, .80), "c2": (.74, .74, .72), "rough": (.35, .55), "scale": 4.0, "bump": .02, "pattern": "noise", "grime": .4, "dirt": .2, "tint": (.4, .1), "texel": 512},
    "borracha":             {"family": "borracha", "c1": (.06, .06, .06), "c2": (.04, .04, .04), "rough": (.85, .97), "scale": 6.0, "bump": .1, "pattern": "noise", "grime": .2, "dirt": .1, "texel": 512},
    "pintura_industrial":   {"family": "pintura", "c1": (.85, .66, .08), "c2": (.70, .52, .05), "rough": (.45, .70), "scale": 3.0, "bump": .05, "pattern": "noise", "chips": True, "grime": .6, "dirt": .4, "texel": 512},
    "sinalizacao_viaria":   {"family": "pintura", "c1": (.86, .86, .82), "c2": (.70, .70, .66), "rough": (.55, .80), "scale": 6.0, "bump": .05, "pattern": "noise", "grime": .3, "dirt": 0.0, "texel": 256},
    "agua_canal":           {"family": "agua", "c1": (.05, .11, .12), "c2": (.03, .07, .08), "rough": (.03, .10), "scale": .08, "bump": .25, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "spec": .8, "texel": 256},
    "grama":                {"family": "terreno", "c1": (.20, .30, .11), "c2": (.13, .20, .07), "rough": (.85, .98), "scale": .6, "bump": .2, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 256},
    "terra":                {"family": "terreno", "c1": (.36, .28, .19), "c2": (.25, .19, .13), "rough": (.88, .98), "scale": .8, "bump": .3, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 256},
    "lastro_ferroviario":   {"family": "terreno", "c1": (.38, .35, .32), "c2": (.25, .23, .21), "rough": (.9, .99), "scale": 8.0, "bump": .6, "pattern": "noise", "grime": .3, "dirt": 0.0, "texel": 256},
    "trilho_aco":           {"family": "metal", "c1": (.40, .36, .33), "c2": (.30, .22, .17), "rough": (.35, .70), "scale": 3.0, "bump": .1, "pattern": "noise", "metal": .9, "grime": .3, "dirt": 0.0, "texel": 512},
    "folhagem":             {"family": "vegetacao", "c1": (.16, .27, .10), "c2": (.10, .18, .06), "rough": (.65, .85), "scale": .9, "bump": .4, "pattern": "noise", "grime": .3, "dirt": 0.0, "tint": (.06, .2), "texel": 512},
    "tronco":               {"family": "vegetacao", "c1": (.30, .23, .17), "c2": (.20, .15, .11), "rough": (.85, .97), "scale": 2.0, "bump": .5, "pattern": "noise", "grime": .4, "dirt": 0.0, "texel": 512},
}


def _n(nt, kind, x, y, **inputs):
    node = nt.nodes.new(kind)
    node.location = (x, y)
    for k, v in inputs.items():
        node.inputs[k].default_value = v
    return node


def build_material(name, spec):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 1500, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 1150, 0)
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = _n(nt, "ShaderNodeTexCoord", -1400, 0)
    mp = _n(nt, "ShaderNodeMapping", -1200, 0)
    mp.inputs["Scale"].default_value = (spec["scale"],) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    c1 = (*spec["c1"], 1.0)
    c2 = (*spec["c2"], 1.0)
    pat = spec["pattern"]
    noise = _n(nt, "ShaderNodeTexNoise", -950, 200, Scale=6.0, Detail=8.0, Roughness=.62)
    L.new(mp.outputs["Vector"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-700, 250)
    ramp.color_ramp.elements[0].color = c2
    ramp.color_ramp.elements[1].color = c1
    L.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    color = ramp.outputs["Color"]
    height = noise.outputs["Fac"]
    if pat in ("brick", "tiles"):
        bw, rh, mortar = spec["tile"]
        brick = _n(nt, "ShaderNodeTexBrick", -700, -50, Scale=1.0, **{"Mortar Size": mortar, "Brick Width": bw, "Row Height": rh})
        brick.offset = .5 if pat == "brick" else 0.0
        brick.inputs["Color1"].default_value = c1
        brick.inputs["Color2"].default_value = c2
        brick.inputs["Mortar"].default_value = (*spec.get("mortar", tuple(v * .8 for v in spec["c2"])), 1.0)
        L.new(tc.outputs["UV"], brick.inputs["Vector"])
        mix = _n(nt, "ShaderNodeMix", -450, 150)
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = .35
        L.new(brick.outputs["Color"], mix.inputs[6])
        L.new(ramp.outputs["Color"], mix.inputs[7])
        color = mix.outputs[2]
        inv = _n(nt, "ShaderNodeMath", -450, -150)
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        L.new(brick.outputs["Fac"], inv.inputs[1])
        height = inv.outputs["Value"]
    elif pat == "wave":
        # W2: finer, lower-contrast grain (stretched bands + light distortion) instead of large cartoon rings.
        wave = _n(nt, "ShaderNodeTexWave", -700, -50, Scale=7.0, Distortion=2.2, Detail=6.0)
        wave.wave_type = "BANDS"
        wave.inputs["Detail Roughness"].default_value = .65
        L.new(tc.outputs["UV"], wave.inputs["Vector"])
        soft = _n(nt, "ShaderNodeMapRange", -560, 120)
        soft.inputs["To Min"].default_value = .25
        soft.inputs["To Max"].default_value = .75
        L.new(wave.outputs["Fac"], soft.inputs["Value"])
        mix = _n(nt, "ShaderNodeMix", -450, 150)
        mix.data_type = "RGBA"
        mix.inputs["Factor"].default_value = .5
        L.new(soft.outputs["Result"], mix.inputs["Factor"])
        mix.inputs[6].default_value = c2
        mix.inputs[7].default_value = c1
        color = mix.outputs[2]
        height = wave.outputs["Fac"]
    elif pat == "corrugated":
        wave = _n(nt, "ShaderNodeTexWave", -700, -50, Scale=4.2, Distortion=0.0, Detail=0.0)
        wave.wave_type = "BANDS"
        wave.wave_profile = "SIN"
        wave.bands_direction = "X"
        L.new(tc.outputs["UV"], wave.inputs["Vector"])
        height = wave.outputs["Fac"]
    if spec.get("patches"):
        big = _n(nt, "ShaderNodeTexNoise", -950, 450, Scale=.08, Detail=2.0)
        L.new(tc.outputs["Object"], big.inputs["Vector"])
        thr = _n(nt, "ShaderNodeMapRange", -700, 450, **{"From Min": .55, "From Max": .58})
        L.new(big.outputs["Fac"], thr.inputs["Value"])
        mix = _n(nt, "ShaderNodeMix", -300, 350)
        mix.data_type = "RGBA"
        L.new(thr.outputs["Result"], mix.inputs["Factor"])
        L.new(color, mix.inputs[6])
        mix.inputs[7].default_value = (.05, .05, .055, 1)
        color = mix.outputs[2]
    if spec.get("chips"):
        chip = _n(nt, "ShaderNodeTexNoise", -950, 650, Scale=14.0, Detail=10.0, Roughness=.7)
        L.new(mp.outputs["Vector"], chip.inputs["Vector"])
        thr = _n(nt, "ShaderNodeMapRange", -700, 650, **{"From Min": .66, "From Max": .70})
        L.new(chip.outputs["Fac"], thr.inputs["Value"])
        mix = _n(nt, "ShaderNodeMix", -300, 550)
        mix.data_type = "RGBA"
        L.new(thr.outputs["Result"], mix.inputs["Factor"])
        L.new(color, mix.inputs[6])
        mix.inputs[7].default_value = (.30, .14, .07, 1)
        color = mix.outputs[2]
    # Large-scale variation so repeated surfaces never look uniform.
    big = _n(nt, "ShaderNodeTexNoise", -950, -350, Scale=.35, Detail=3.0)
    L.new(tc.outputs["Object"], big.inputs["Vector"])
    bigmr = _n(nt, "ShaderNodeMapRange", -700, -350, **{"To Min": .82, "To Max": 1.1})
    L.new(big.outputs["Fac"], bigmr.inputs["Value"])
    vary = _n(nt, "ShaderNodeVectorMath", -150, 150)
    vary.operation = "SCALE"
    L.new(color, vary.inputs[0])
    L.new(bigmr.outputs["Result"], vary.inputs["Scale"])
    color = vary.outputs["Vector"]
    if spec.get("tint"):
        hue_var, val_var = spec["tint"]
        info = _n(nt, "ShaderNodeObjectInfo", -450, 600)
        hue = _n(nt, "ShaderNodeMapRange", -250, 650, **{"To Min": .5 - hue_var / 2, "To Max": .5 + hue_var / 2})
        val = _n(nt, "ShaderNodeMapRange", -250, 500, **{"To Min": 1 - val_var, "To Max": 1 + val_var * .5})
        L.new(info.outputs["Random"], hue.inputs["Value"])
        L.new(info.outputs["Random"], val.inputs["Value"])
        hsv = _n(nt, "ShaderNodeHueSaturation", 50, 300)
        L.new(color, hsv.inputs["Color"])
        L.new(hue.outputs["Result"], hsv.inputs["Hue"])
        L.new(val.outputs["Result"], hsv.inputs["Value"])
        hsv.inputs["Saturation"].default_value = spec.get("sat", 1.0)
        color = hsv.outputs["Color"]
    if spec.get("grime", 0) > 0:
        ao = _n(nt, "ShaderNodeAmbientOcclusion", 50, -150, Distance=.6)
        aomr = _n(nt, "ShaderNodeMapRange", 250, -150, **{"To Min": 1 - spec["grime"] * .6, "To Max": 1.0})
        L.new(ao.outputs["AO"], aomr.inputs["Value"])
        g = _n(nt, "ShaderNodeVectorMath", 450, 150)
        g.operation = "SCALE"
        L.new(color, g.inputs[0])
        L.new(aomr.outputs["Result"], g.inputs["Scale"])
        color = g.outputs["Vector"]
    if spec.get("dirt", 0) > 0:
        sep = _n(nt, "ShaderNodeSeparateXYZ", 250, -400)
        L.new(tc.outputs["Object"], sep.inputs["Vector"])
        dmr = _n(nt, "ShaderNodeMapRange", 450, -400, **{"From Min": 0.0, "From Max": 1.4, "To Min": spec["dirt"], "To Max": 0.0})
        L.new(sep.outputs["Z"], dmr.inputs["Value"])
        mix = _n(nt, "ShaderNodeMix", 650, 100)
        mix.data_type = "RGBA"
        L.new(dmr.outputs["Result"], mix.inputs["Factor"])
        L.new(color, mix.inputs[6])
        mix.inputs[7].default_value = (.20, .17, .13, 1)
        color = mix.outputs[2]
    L.new(color, bsdf.inputs["Base Color"])
    rmr = _n(nt, "ShaderNodeMapRange", -450, -600, **{"To Min": spec["rough"][0], "To Max": spec["rough"][1]})
    L.new(noise.outputs["Fac"], rmr.inputs["Value"])
    L.new(rmr.outputs["Result"], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = spec.get("metal", 0.0)
    if "spec" in spec:
        bsdf.inputs["Specular IOR Level"].default_value = spec["spec"]
    if spec["bump"] > 0:
        bump = _n(nt, "ShaderNodeBump", 850, -350, Strength=spec["bump"], Distance=.02)
        L.new(height, bump.inputs["Height"])
        L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # Texture slots for authored PBR maps (W3). Unlinked, no image: no missing data.
    frame = nt.nodes.new("NodeFrame")
    frame.label = f"Slots PBR (W3): ArtSource/Textures/{name}/"
    frame.location = (-1400, -900)
    for k, ch in enumerate(CHANNELS):
        slot = nt.nodes.new("ShaderNodeTexImage")
        slot.name = slot.label = f"SLOT_{ch}"
        slot.location = (-1400 + k * 280, -950)
        slot.parent = frame
        if ch != "BaseColor":
            slot.interpolation = "Linear"
    avg = tuple((a + b) / 2 for a, b in zip(spec["c1"], spec["c2"]))
    mat.diffuse_color = (*avg, 1.0)
    mat.roughness = sum(spec["rough"]) / 2
    mat.metallic = spec.get("metal", 0.0)
    mat["sa_family"] = spec["family"]
    mat["sa_channels"] = ",".join(CHANNELS)
    mat["sa_texel_density_px_m"] = spec["texel"]
    mat["sa_texture_dir"] = f"ArtSource/Textures/{name}/"
    mat["sa_status"] = "procedural_base_W1.5 (texturas PBR autorais pendentes: W3)"
    return mat


def build_library():
    return {name: build_material(name, spec) for name, spec in LIB.items()}


def write_library_json(root):
    out = {
        "schemaVersion": 1,
        "stage": "W1.5 - estrutura da biblioteca PBR (procedural base, não final)",
        "channels": CHANNELS,
        "textureNaming": "ArtSource/Textures/<material>/<material>_<Channel>.png (BaseColor sRGB; Normal OpenGL; Roughness/Metallic/AO lineares)",
        "texelDensityTargets": {"hero_props": 1024, "near_props": "512-1024", "architecture": "256-512", "background": "LOD/proxy"},
        "rules": ["Nenhum material flat como solução final", "Variação por instância e por escala", "Decals obrigatórios em ambientes finais (W3/W4)"],
        "materials": {name: {"family": s["family"], "pattern": s["pattern"], "metallic": s.get("metal", 0.0), "roughnessRange": list(s["rough"]),
                             "texelDensity": s["texel"], "status": "procedural_base_W1.5", "slots": {ch: f"ArtSource/Textures/{name}/{name}_{ch}.png" for ch in CHANNELS}}
                      for name, s in LIB.items()},
    }
    p = Path(root) / "ArtSource" / "Materials" / "material_library_v1.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
