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
    "pedra_portuguesa":     {"family": "pavimento", "c1": (.70, .68, .64), "c2": (.30, .29, .28), "rough": (.7, .9), "scale": 1.0, "bump": .5, "pattern": "tiles", "tile": (.08, .08, .006), "mortar": (.45, .43, .40), "grime": .5, "dirt": .3, "texel": 512},
    "cimentado":            {"family": "concreto", "c1": (.56, .55, .52), "c2": (.44, .43, .41), "rough": (.85, .95), "scale": 1.5, "bump": .25, "pattern": "noise", "patches": True, "grime": .6, "dirt": .4, "texel": 512},
    "piso_intertravado":    {"family": "pavimento", "c1": (.50, .44, .40), "c2": (.40, .35, .32), "rough": (.75, .92), "scale": 1.0, "bump": .45, "pattern": "tiles", "tile": (.2, .1, .004), "mortar": (.30, .29, .27), "grime": .55, "dirt": .3, "texel": 512},
    "meio_fio":             {"family": "concreto", "c1": (.66, .65, .62), "c2": (.52, .51, .49), "rough": (.70, .90), "scale": 2.0, "bump": .3, "pattern": "noise", "grime": .6, "dirt": .5, "texel": 512},
    "metal_galvanizado":    {"family": "metal", "c1": (.62, .63, .64), "c2": (.50, .51, .52), "rough": (.30, .55), "scale": 6.0, "bump": .05, "pattern": "noise", "metal": 1.0, "grime": .45, "dirt": .3, "texel": 1024},
    "aco_pintado_verde":    {"family": "aco_pintado", "c1": (.12, .28, .18), "c2": (.09, .22, .14), "rough": (.40, .65), "scale": 3.0, "bump": .08, "pattern": "noise", "chips": True, "grime": .5, "dirt": .4, "texel": 1024},
    "aco_pintado_cinza":    {"family": "aco_pintado", "c1": (.36, .38, .40), "c2": (.28, .30, .32), "rough": (.40, .65), "scale": 3.0, "bump": .08, "pattern": "noise", "chips": True, "grime": .5, "dirt": .4, "texel": 1024},
    "ferrugem":             {"family": "ferrugem", "c1": (.42, .20, .09), "c2": (.25, .11, .05), "rough": (.75, .95), "scale": 5.0, "bump": .5, "pattern": "noise", "metal": .3, "grime": .4, "dirt": .2, "texel": 1024},
    "aluminio":             {"family": "metal", "c1": (.72, .73, .74), "c2": (.62, .63, .64), "rough": (.28, .45), "scale": 8.0, "bump": .03, "pattern": "noise", "metal": .95, "grime": .4, "dirt": .2, "texel": 1024},
    "madeira_pintada":      {"family": "madeira", "c1": (.36, .20, .12), "c2": (.28, .15, .09), "rough": (.55, .80), "scale": 1.0, "bump": .25, "pattern": "wave", "chips": True, "grime": .55, "dirt": .35, "tint": (.12, .2), "texel": 1024},
    "madeira_crua":         {"family": "madeira", "c1": (.48, .34, .22), "c2": (.34, .23, .14), "rough": (.65, .85), "scale": 1.0, "bump": .35, "pattern": "wave", "grime": .5, "dirt": .3, "texel": 1024},
    "vidro":                {"family": "vidro", "c1": (.08, .10, .11), "c2": (.05, .07, .08), "rough": (.04, .12), "scale": 2.0, "bump": .0, "pattern": "noise", "grime": .3, "dirt": .1, "spec": .9, "texel": 512},
    "vidro_fachada":        {"family": "vidro", "c1": (.03, .03, .035), "c2": (.02, .02, .025), "rough": (.03, .06), "scale": 2.0, "bump": .0, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 256},
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
    # W4 coast
    "areia":                {"family": "terreno", "c1": (.80, .70, .52), "c2": (.70, .60, .44), "rough": (.90, .98), "scale": 1.6, "bump": .10, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 512},
    "pedra_costao":         {"family": "concreto", "c1": (.34, .33, .31), "c2": (.22, .21, .20), "rough": (.80, .97), "scale": 2.4, "bump": .85, "pattern": "noise", "grime": .5, "dirt": .4, "texel": 512},
    "agua_mar":             {"family": "agua", "c1": (.06, .30, .36), "c2": (.02, .14, .24), "rough": (.03, .12), "scale": .05, "bump": .35, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "spec": .9, "texel": 256},
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


# ---------------------------------------------------------------- W3: authored tileable PBR textures (ArtSource/Textures)
ROOT = Path(__file__).resolve().parents[2]
TEX_DIR = ROOT / "ArtSource" / "Textures"
# material -> (texture set, mode): "raw" = authored colour; "tint" = desaturated texture x material colour (paints, plasters, plastics)
TEX_MAP = {
    "reboco_antigo": ("reboco", "tint"), "reboco_pintado": ("reboco", "tint"), "concreto_pintado": ("reboco", "tint"),
    "parede_pintada": ("reboco", "tint"), "pedra_reboco_historico": ("reboco", "tint"), "reboco_pastilha": ("pastilha", "tint"),
    "concreto": ("concreto", "raw"), "concreto_aparente": ("concreto", "raw"), "cimentado": ("concreto", "tint"),
    "calcada": ("ladrilho", "raw"), "meio_fio": ("meio_fio", "raw"), "tijolo_aparente": ("tijolo", "raw"), "tijolo_pintado": ("tijolo", "tint"),
    "asfalto": ("asfalto", "raw"), "asfalto_gasto": ("asfalto", "tint"), "metal_galvanizado": ("galvanizado", "raw"),
    "aluminio": ("galvanizado", "tint"), "aco_inox": ("galvanizado", "tint"), "trilho_aco": ("galvanizado", "tint"),
    "aco_pintado_verde": ("aco_pintado", "tint"), "aco_pintado_cinza": ("aco_pintado", "tint"), "aco_pintado_vermelho": ("aco_pintado", "tint"),
    "pintura_industrial": ("aco_pintado", "tint"), "ferrugem": ("ferrugem", "raw"), "madeira_pintada": ("madeira", "tint"),
    "madeira_crua": ("madeira", "tint"), "ceramica_telha": ("telha", "raw"), "ceramica_piso": ("ceramica", "tint"),
    "piso_ceramico_bege": ("ceramica", "tint"), "azulejo_branco": ("ceramica", "tint"), "plastico": ("plastico", "tint"),
    "plastico_branco": ("plastico", "tint"), "plastico_azul": ("plastico", "tint"), "borracha": ("borracha", "raw"),
    "borracha_preta": ("borracha", "raw"), "grama": ("grama", "raw"), "terra": ("terra", "raw"), "lastro_ferroviario": ("cascalho", "raw"),
    "piso_intertravado": ("intertravado", "raw"), "pedra_portuguesa": ("pedra_portuguesa", "raw"), "granito": ("granito", "raw"),
}
_TEX_LIB = None


def tex_library():
    global _TEX_LIB
    if _TEX_LIB is None:
        p = TEX_DIR / "texture_library_w3.json"
        _TEX_LIB = json.loads(p.read_text(encoding="utf-8"))["sets"] if p.exists() else {}
    return _TEX_LIB


def _img(nt, path, cs, x, y, label):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.location = (x, y)
    n.name = n.label = label
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = cs
    n.image = img
    return n


def build_textured(name, spec, set_name, mode):
    """W3 production material: authored BaseColor/Normal/Roughness/AO(/Metallic) on metric UVs + macro variation, per-object tint and
    the W2.5 wear layers (SA_WEAR) so tiling never reads as a repeated sticker."""
    info = tex_library()[set_name]
    mat = bpy.data.materials.new(name)
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 1700, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 1400, 0)
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = _n(nt, "ShaderNodeTexCoord", -1600, 0)
    mp = _n(nt, "ShaderNodeMapping", -1400, 0)
    t = 1.0 / info["tile_m"]
    mp.inputs["Scale"].default_value = (t, t, t)
    L.new(tc.outputs["UV"], mp.inputs["Vector"])
    maps = {k: ROOT / v for k, v in info["maps"].items()}
    nodes = {}
    for k, (cs, y) in {"BaseColor": ("sRGB", 400), "Roughness": ("Non-Color", 100), "Normal": ("Non-Color", -200), "AO": ("Non-Color", -500),
                       "Metallic": ("Non-Color", -800)}.items():
        if k in maps:
            nodes[k] = _img(nt, maps[k], cs, -1100, y, "SLOT_" + k)
            L.new(mp.outputs["Vector"], nodes[k].inputs["Vector"])
    color = nodes["BaseColor"].outputs["Color"]
    if mode == "tint":
        avg = tuple((a + b) / 2 for a, b in zip(spec["c1"], spec["c2"]))
        hs = _n(nt, "ShaderNodeHueSaturation", -800, 400)
        hs.inputs["Saturation"].default_value = .15
        L.new(color, hs.inputs["Color"])
        mul = _n(nt, "ShaderNodeMix", -600, 400)
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        L.new(hs.outputs["Color"], mul.inputs[6])
        mul.inputs[7].default_value = (*(min(1.0, c * 1.18) for c in avg), 1)
        color = mul.outputs[2]
    elif "raw_mult" in spec:
        pass
    # AO from the authored map (cavities) multiplies the colour
    if "AO" in nodes:
        aom = _n(nt, "ShaderNodeMix", -400, 200)
        aom.data_type = "RGBA"
        aom.blend_type = "MULTIPLY"
        aom.inputs["Factor"].default_value = .85
        L.new(color, aom.inputs[6])
        L.new(nodes["AO"].outputs["Color"], aom.inputs[7])
        color = aom.outputs[2]
    # macro variation (object space, never tiles)
    big = _n(nt, "ShaderNodeTexNoise", -600, -1100, Scale=.22, Detail=3.0)
    L.new(tc.outputs["Object"], big.inputs["Vector"])
    bigmr = _n(nt, "ShaderNodeMapRange", -400, -1100, **{"To Min": .84, "To Max": 1.1})
    L.new(big.outputs["Fac"], bigmr.inputs["Value"])
    vary = _n(nt, "ShaderNodeVectorMath", -200, 300)
    vary.operation = "SCALE"
    L.new(color, vary.inputs[0])
    L.new(bigmr.outputs["Result"], vary.inputs["Scale"])
    color = vary.outputs["Vector"]
    if spec.get("tint"):
        hue_var, val_var = spec["tint"]
        oi = _n(nt, "ShaderNodeObjectInfo", -400, 700)
        hue = _n(nt, "ShaderNodeMapRange", -200, 750, **{"To Min": .5 - hue_var / 2, "To Max": .5 + hue_var / 2})
        val = _n(nt, "ShaderNodeMapRange", -200, 600, **{"To Min": 1 - val_var, "To Max": 1 + val_var * .5})
        L.new(oi.outputs["Random"], hue.inputs["Value"])
        L.new(oi.outputs["Random"], val.inputs["Value"])
        hsv = _n(nt, "ShaderNodeHueSaturation", 0, 400)
        L.new(color, hsv.inputs["Color"])
        L.new(hue.outputs["Result"], hsv.inputs["Hue"])
        L.new(val.outputs["Result"], hsv.inputs["Value"])
        hsv.inputs["Saturation"].default_value = spec.get("sat", 1.0)
        color = hsv.outputs["Color"]
    color = _wear(nt, L, color, spec, tc)
    L.new(color, bsdf.inputs["Base Color"])
    L.new(nodes["Roughness"].outputs["Color"], bsdf.inputs["Roughness"])
    nm = _n(nt, "ShaderNodeNormalMap", 1100, -300, Strength=.9 if spec["family"] not in ("terreno", "asfalto", "pavimento") else .7)
    L.new(nodes["Normal"].outputs["Color"], nm.inputs["Color"])
    L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if "Metallic" in nodes:
        L.new(nodes["Metallic"].outputs["Color"], bsdf.inputs["Metallic"])
    else:
        bsdf.inputs["Metallic"].default_value = spec.get("metal", 0.0)
    avg = tuple((a + b) / 2 for a, b in zip(spec["c1"], spec["c2"]))
    mat.diffuse_color = (*avg, 1.0)
    mat["sa_family"] = spec["family"]
    mat["sa_texture_set"] = set_name
    mat["sa_texture_mode"] = mode
    mat["sa_tile_m"] = info["tile_m"]
    mat["sa_status"] = "W3 produção: texturas PBR autorais (ArtSource/Textures/%s)" % set_name
    return mat


GLASS = {"vidro": dict(color=(.03, .04, .045), alpha=.16, rough=.02), "vidro_vitrine": dict(color=(.04, .05, .055), alpha=.12, rough=.015),
         "vidro_fachada": dict(color=(.025, .03, .035), alpha=.86, rough=.04, fake_interior=True)}


def build_glass(name):
    """W3 glass: thin dielectric with Fresnel-driven opacity (see-through facing the camera, reflective at grazing angles), shadow-transparent.
    vidro / vidro_vitrine = clear (heroes, shopfronts with modelled interiors); vidro_fachada = background buildings without interiors
    (mostly reflective, with a faint fake interior so windows never read as flat plates)."""
    g = GLASS[name]
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 900, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 600, 0)
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*g["color"], 1)
    bsdf.inputs["Roughness"].default_value = g["rough"]
    bsdf.inputs["IOR"].default_value = 1.5
    bsdf.inputs["Specular IOR Level"].default_value = 1.0
    lw = _n(nt, "ShaderNodeLayerWeight", 0, 0, Blend=.35)
    alpha = _n(nt, "ShaderNodeMapRange", 300, 0, **{"From Min": 0.0, "From Max": 1.0, "To Min": g["alpha"], "To Max": 1.0})
    L.new(lw.outputs["Fresnel"], alpha.inputs["Value"])
    L.new(alpha.outputs["Result"], bsdf.inputs["Alpha"])
    if g.get("fake_interior"):
        tc = _n(nt, "ShaderNodeTexCoord", -400, 300)
        nz = _n(nt, "ShaderNodeTexNoise", -200, 300, Scale=.6, Detail=2.0)
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = _n(nt, "ShaderNodeMix", 200, 300)
        ramp.data_type = "RGBA"
        L.new(nz.outputs["Fac"], ramp.inputs["Factor"])
        ramp.inputs[6].default_value = (.02, .022, .025, 1)
        ramp.inputs[7].default_value = (.16, .13, .09, 1)
        L.new(ramp.outputs[2], bsdf.inputs["Base Color"])
    try:
        mat.surface_render_method = "DITHERED"
        mat.use_transparent_shadow = True
    except AttributeError:
        mat.blend_method = "HASHED"
    mat.diffuse_color = (*g["color"], 1)
    mat["sa_family"] = "vidro"
    mat["sa_status"] = "W3 vidro funcional (Fresnel/alpha, sombra transparente)"
    return mat


def build_material(name, spec):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    base = name[:-5] if name.endswith("_hero") else name
    if base in GLASS:
        return build_glass(name) if name == base else build_glass(base)
    tm = TEX_MAP.get(base)
    if tm and tm[0] in tex_library():
        return build_textured(name, spec, *tm)
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
    color = _wear(nt, L, color, spec, tc)
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


MASONRY = {"reboco", "concreto", "tijolo", "pedra", "pintura", "fachada"}
GROUND = {"asfalto", "pavimento", "concreto", "ceramica"}
METALS = {"aco_pintado", "metal"}


def _mixc(nt, L, factor_socket, a, b_color, x, y):
    m = _n(nt, "ShaderNodeMix", x, y)
    m.data_type = "RGBA"
    L.new(factor_socket, m.inputs["Factor"])
    L.new(a, m.inputs[6])
    if isinstance(b_color, tuple):
        m.inputs[7].default_value = b_color
    else:
        L.new(b_color, m.inputs[7])
    return m.outputs[2]


def _math(nt, L, op, a, b, x, y, c=None):
    m = _n(nt, "ShaderNodeMath", x, y)
    m.operation = op
    for i, v in enumerate((a, b) if c is None else (a, b, c)):
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            L.new(v, m.inputs[i])
    return m.outputs["Value"]


def _wear(nt, L, color, spec, tc):
    """W2.5 wear pass (procedural, per family), scaled by the material-wide 'SA_WEAR' value and a per-object random factor:
    rain streaks and rising damp on vertical masonry, plaster patches (remendos), worn/dirty circulation on floors and paving,
    rust bleed on painted steel. Setting every SA_WEAR node to 0 renders the pre-wear look (before/after captures)."""
    fam = spec["family"]
    if fam not in MASONRY | GROUND | METALS:
        return color
    wear = _n(nt, "ShaderNodeValue", 300, -900)
    wear.name = wear.label = "SA_WEAR"
    wear.outputs[0].default_value = 1.0
    info = _n(nt, "ShaderNodeObjectInfo", 300, -1050)
    rnd = _n(nt, "ShaderNodeMapRange", 480, -1050, **{"To Min": .55, "To Max": 1.35})
    L.new(info.outputs["Random"], rnd.inputs["Value"])
    W = _math(nt, L, "MULTIPLY", wear.outputs[0], rnd.outputs["Result"], 650, -950)
    geo = _n(nt, "ShaderNodeNewGeometry", 300, -1250)
    sepn = _n(nt, "ShaderNodeSeparateXYZ", 480, -1250)
    L.new(geo.outputs["Normal"], sepn.inputs["Vector"])
    nz = _math(nt, L, "ABSOLUTE", sepn.outputs["Z"], 0.0, 650, -1250)
    vert = _math(nt, L, "SUBTRACT", 1.0, nz, 820, -1250)
    sepo = _n(nt, "ShaderNodeSeparateXYZ", 480, -1450)
    L.new(tc.outputs["Object"], sepo.inputs["Vector"])
    x0 = 1700
    if fam in MASONRY:
        mp = _n(nt, "ShaderNodeMapping", 650, -1650)
        mp.inputs["Scale"].default_value = (2.2, 2.2, .14)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        nn = _n(nt, "ShaderNodeTexNoise", 820, -1650, Scale=3.0, Detail=4.0, Roughness=.55)
        L.new(mp.outputs["Vector"], nn.inputs["Vector"])
        st = _n(nt, "ShaderNodeMapRange", 1000, -1650, **{"From Min": .52, "From Max": .78})
        L.new(nn.outputs["Fac"], st.inputs["Value"])
        m1 = _math(nt, L, "MULTIPLY", st.outputs["Result"], vert, 1180, -1650)
        m1 = _math(nt, L, "MULTIPLY", m1, W, 1350, -1650)
        m1 = _math(nt, L, "MULTIPLY", m1, .42, 1520, -1650)
        color = _mixc(nt, L, m1, color, (.13, .12, .10, 1), x0, -1650)
        dn = _n(nt, "ShaderNodeTexNoise", 820, -1900, Scale=1.6, Detail=3.0)
        L.new(tc.outputs["Object"], dn.inputs["Vector"])
        edge = _math(nt, L, "MULTIPLY_ADD", dn.outputs["Fac"], .9, 980, -1900, c=.25)
        zr = _math(nt, L, "DIVIDE", sepo.outputs["Z"], edge, 1150, -1900)
        damp = _n(nt, "ShaderNodeMapRange", 1320, -1900, **{"From Min": 0.0, "From Max": 1.0, "To Min": 1.0, "To Max": 0.0})
        L.new(zr, damp.inputs["Value"])
        d2 = _math(nt, L, "MULTIPLY", damp.outputs["Result"], W, 1500, -1900)
        d2 = _math(nt, L, "MULTIPLY", d2, vert, 1650, -1900)
        d2 = _math(nt, L, "MULTIPLY", d2, .5, 1800, -1900)
        color = _mixc(nt, L, d2, color, (.16, .15, .11, 1), x0 + 200, -1900)
        if fam in ("reboco", "pintura", "fachada"):
            pn = _n(nt, "ShaderNodeTexNoise", 820, -2150, Scale=.35, Detail=2.0)
            L.new(tc.outputs["Object"], pn.inputs["Vector"])
            pt = _n(nt, "ShaderNodeMapRange", 1000, -2150, **{"From Min": .61, "From Max": .635})
            L.new(pn.outputs["Fac"], pt.inputs["Value"])
            p2 = _math(nt, L, "MULTIPLY", pt.outputs["Result"], W, 1180, -2150)
            p2 = _math(nt, L, "MINIMUM", p2, .85, 1350, -2150)
            hv = _n(nt, "ShaderNodeHueSaturation", 1500, -2150)
            hv.inputs["Saturation"].default_value = .55
            hv.inputs["Value"].default_value = 1.12
            L.new(color, hv.inputs["Color"])
            color = _mixc(nt, L, p2, color, hv.outputs["Color"], x0 + 400, -2150)
    if fam in GROUND:
        hz = _n(nt, "ShaderNodeMapRange", 1000, -2400, **{"From Min": .7, "From Max": .95})
        L.new(nz, hz.inputs["Value"])
        gn = _n(nt, "ShaderNodeTexNoise", 820, -2550, Scale=.7, Detail=6.0, Roughness=.6)
        L.new(tc.outputs["Object"], gn.inputs["Vector"])
        gt = _n(nt, "ShaderNodeMapRange", 1000, -2550, **{"From Min": .42, "From Max": .78})
        L.new(gn.outputs["Fac"], gt.inputs["Value"])
        g2 = _math(nt, L, "MULTIPLY", gt.outputs["Result"], hz.outputs["Result"], 1180, -2450)
        g2 = _math(nt, L, "MULTIPLY", g2, W, 1350, -2450)
        g2 = _math(nt, L, "MULTIPLY", g2, .38 if fam != "asfalto" else .22, 1520, -2450)
        color = _mixc(nt, L, g2, color, (.09, .085, .075, 1), x0 + 600, -2450)
    if fam in METALS:
        rn = _n(nt, "ShaderNodeTexNoise", 820, -2800, Scale=4.0, Detail=8.0, Roughness=.7)
        L.new(tc.outputs["Object"], rn.inputs["Vector"])
        rt = _n(nt, "ShaderNodeMapRange", 1000, -2800, **{"From Min": .6, "From Max": .72})
        L.new(rn.outputs["Fac"], rt.inputs["Value"])
        bot = _n(nt, "ShaderNodeMapRange", 1000, -2950, **{"From Min": 0.0, "From Max": 1.2, "To Min": 1.0, "To Max": .35})
        L.new(sepo.outputs["Z"], bot.inputs["Value"])
        r2 = _math(nt, L, "MULTIPLY", rt.outputs["Result"], bot.outputs["Result"], 1180, -2850)
        r2 = _math(nt, L, "MULTIPLY", r2, W, 1350, -2850)
        r2 = _math(nt, L, "MULTIPLY", r2, .7, 1520, -2850)
        color = _mixc(nt, L, r2, color, (.33, .15, .07, 1), x0 + 800, -2850)
    return color


def build_decal(name, color, rough=.8, scale=2.0, cover=(.45, .65), alpha=.85):
    """Soft procedural decal (dithered alpha): stains, oil, damp, tire marks, rust runs. Applied to thin planes."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 800, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 500, 0)
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = _n(nt, "ShaderNodeTexCoord", -600, 0)
    nn = _n(nt, "ShaderNodeTexNoise", -400, 0, Scale=scale, Detail=6.0, Roughness=.6)
    L.new(tc.outputs["Object"], nn.inputs["Vector"])
    mr = _n(nt, "ShaderNodeMapRange", -200, 0, **{"From Min": cover[0], "From Max": cover[1], "To Max": alpha})
    L.new(nn.outputs["Fac"], mr.inputs["Value"])
    wear = _n(nt, "ShaderNodeValue", -200, -200)
    wear.name = wear.label = "SA_WEAR"
    wear.outputs[0].default_value = 1.0
    a2 = _math(nt, L, "MULTIPLY", mr.outputs["Result"], wear.outputs[0], 100, -100)
    L.new(a2, bsdf.inputs["Alpha"])
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    try:
        mat.surface_render_method = "DITHERED"
    except AttributeError:
        mat.blend_method = "HASHED"
    mat.diffuse_color = (*color, 1)
    mat["sa_family"] = "decal"
    mat["sa_status"] = "decal procedural W2.5"
    return mat


DECALS = {"decal_umidade": ((.16, .15, .11), .9, 1.4, (.42, .62), .7), "decal_oleo": ((.025, .025, .03), .25, 3.0, (.46, .62), .9),
          "decal_sujeira": ((.18, .15, .11), .95, 2.2, (.45, .7), .75), "decal_pneu": ((.02, .02, .022), .6, 6.0, (.30, .55), .75),
          "decal_ferrugem": ((.30, .13, .05), .8, 5.0, (.5, .65), .8)}


def build_decals(lib):
    for n, (c, r, sc, cv, a) in DECALS.items():
        lib[n] = build_decal(n, c, r, sc, cv, a)
    return lib


def build_library():
    lib = {name: build_material(name, spec) for name, spec in LIB.items()}
    return build_decals(lib)


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


def build_terrain_material(lib):
    """W3 terrain: blend of authored grass / exposed soil / gravel / residual concrete driven by slope (geometry normal) and
    object-space noise, sampled in world metres (terrain UVs are coarse). Steeper ground and worn patches show soil; scattered
    gravel and old concrete remnants near the flat; keeps the relief readable from oblique and aerial views."""
    name = "terreno_w3"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    texl = tex_library()
    if not all(k in texl for k in ("grama", "terra", "cascalho", "concreto")):
        return lib["terra"]
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 1800, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 1500, 0)
    L.new(bsdf.outputs[0], out.inputs["Surface"])
    tc = _n(nt, "ShaderNodeTexCoord", -1800, 0)
    sets = {}
    for k, (setn, y) in enumerate((("grama", 600), ("terra", 200), ("cascalho", -200), ("concreto", -600))):
        info = texl[setn]
        mp = _n(nt, "ShaderNodeMapping", -1500, y)
        t = 1.0 / info["tile_m"]
        mp.inputs["Scale"].default_value = (t, t, t)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        c = _img(nt, ROOT / info["maps"]["BaseColor"], "sRGB", -1200, y, f"SLOT_{setn}_BaseColor")
        n = _img(nt, ROOT / info["maps"]["Normal"], "Non-Color", -1200, y - 150, f"SLOT_{setn}_Normal")
        r = _img(nt, ROOT / info["maps"]["Roughness"], "Non-Color", -1200, y - 300, f"SLOT_{setn}_Roughness")
        for im in (c, n, r):
            L.new(mp.outputs["Vector"], im.inputs["Vector"])
        sets[setn] = (c, n, r)
    geo = _n(nt, "ShaderNodeNewGeometry", -1200, -1000)
    sep = _n(nt, "ShaderNodeSeparateXYZ", -1000, -1000)
    L.new(geo.outputs["Normal"], sep.inputs[0])
    slope = _n(nt, "ShaderNodeMapRange", -800, -1000, **{"From Min": .995, "From Max": .955, "To Min": 0.0, "To Max": 1.0})
    L.new(sep.outputs["Z"], slope.inputs["Value"])
    wear = _n(nt, "ShaderNodeTexNoise", -1000, -1250, Scale=.045, Detail=4.0)
    L.new(tc.outputs["Object"], wear.inputs["Vector"])
    worn = _n(nt, "ShaderNodeMapRange", -800, -1250, **{"From Min": .55, "From Max": .68})
    L.new(wear.outputs["Fac"], worn.inputs["Value"])
    soil = _n(nt, "ShaderNodeMath", -600, -1100)
    soil.operation = "MAXIMUM"
    L.new(slope.outputs["Result"], soil.inputs[0])
    L.new(worn.outputs["Result"], soil.inputs[1])
    gn = _n(nt, "ShaderNodeTexNoise", -1000, -1500, Scale=.09, Detail=3.0)
    L.new(tc.outputs["Object"], gn.inputs["Vector"])
    grav = _n(nt, "ShaderNodeMapRange", -800, -1500, **{"From Min": .64, "From Max": .7})
    L.new(gn.outputs["Fac"], grav.inputs["Value"])
    cn = _n(nt, "ShaderNodeTexNoise", -1000, -1750, Scale=.03, Detail=2.0)
    L.new(tc.outputs["Object"], cn.inputs["Vector"])
    conc = _n(nt, "ShaderNodeMapRange", -800, -1750, **{"From Min": .72, "From Max": .74})
    L.new(cn.outputs["Fac"], conc.inputs["Value"])

    def layer(prev, fac, setn, idx):
        m = _n(nt, "ShaderNodeMix", -200 + idx * 150, 400 - idx * 60)
        m.data_type = "RGBA"
        L.new(fac, m.inputs["Factor"])
        L.new(prev, m.inputs[6])
        L.new(sets[setn][idx_map[idx]].outputs["Color"], m.inputs[7])
        return m.outputs[2]
    idx_map = {0: 0, 1: 1, 2: 2}
    outs = []
    for ch in range(3):          # colour, normal, roughness blended with the same masks
        base = sets["grama"][ch].outputs["Color"]
        for fac, setn in ((soil.outputs[0], "terra"), (grav.outputs["Result"], "cascalho"), (conc.outputs["Result"], "concreto")):
            m = _n(nt, "ShaderNodeMix", -200 + ch * 300, 400 - ch * 300)
            m.data_type = "RGBA"
            L.new(fac, m.inputs["Factor"])
            L.new(base, m.inputs[6])
            L.new(sets[setn][ch].outputs["Color"], m.inputs[7])
            base = m.outputs[2]
        outs.append(base)
    big = _n(nt, "ShaderNodeTexNoise", -600, 900, Scale=.012, Detail=2.0)
    L.new(tc.outputs["Object"], big.inputs["Vector"])
    bmr = _n(nt, "ShaderNodeMapRange", -400, 900, **{"To Min": .8, "To Max": 1.12})
    L.new(big.outputs["Fac"], bmr.inputs["Value"])
    vary = _n(nt, "ShaderNodeVectorMath", 900, 300)
    vary.operation = "SCALE"
    L.new(outs[0], vary.inputs[0])
    L.new(bmr.outputs["Result"], vary.inputs["Scale"])
    L.new(vary.outputs[0], bsdf.inputs["Base Color"])
    nm = _n(nt, "ShaderNodeNormalMap", 1200, -200, Strength=.8)
    L.new(outs[1], nm.inputs["Color"])
    L.new(nm.outputs[0], bsdf.inputs["Normal"])
    rs = _n(nt, "ShaderNodeSeparateColor", 1200, -400)
    L.new(outs[2], rs.inputs[0])
    L.new(rs.outputs[0], bsdf.inputs["Roughness"])
    mat.diffuse_color = (.30, .30, .18, 1)
    mat["sa_family"] = "terreno"
    mat["sa_status"] = "W3 terreno: blend grama/terra/cascalho/concreto por declividade + ruído (texturas autorais)"
    return mat
