"""W3.1 authored decals as instanced pieces (requires bpy).

Reads ArtSource/Textures/decals_w31/decals_w31.json (baked by bake_decals_w31.py) and builds one plane piece per decal:
ACC_dc_<id>  vertical, facing -Y, bottom edge at local z=0 (facade/wall decals: posters, graffiti, signs, labels, scraps, peeling)
ACC_dcf_<id> horizontal, facing +Z (spray marks / stencils on asphalt and sidewalks)
Material: authored RGBA image + weathering (alpha eroded by noise, grime/fade tint, per-instance variation from Object Info Random).
"""
import json
from pathlib import Path

import bpy

import sa_bl

WEATHER = {"poster": (.35, .25), "graffiti": (.25, .2), "sign": (.15, .3), "mark": (.45, .15), "label": (.1, .15), "scraps": (.4, .3),
           "peeling": (.1, .1)}   # (alpha erosion, fade)


def load(root):
    p = Path(root) / "ArtSource" / "Textures" / "decals_w31" / "decals_w31.json"
    return json.loads(p.read_text(encoding="utf-8"))["decals"] if p.exists() else {}


def material(root, did, meta):
    name = f"decal_w31_{did}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links

    def n(kind, x, y, **kw):
        nd = nt.nodes.new(kind)
        nd.location = (x, y)
        for k, v in kw.items():
            nd.inputs[k].default_value = v
        return nd
    out = n("ShaderNodeOutputMaterial", 900, 0)
    bsdf = n("ShaderNodeBsdfPrincipled", 600, 0, Roughness=.82)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (-300, 150)
    path = Path(root) / "ArtSource" / "Textures" / "decals_w31" / meta["file"]
    img = bpy.data.images.load(str(path), check_existing=True)   # absolute here; save_as_mainfile remaps to '//' relative
    tex.image = img
    tex.extension = "CLIP"
    uv = n("ShaderNodeTexCoord", -900, 0)
    L.new(uv.outputs["UV"], tex.inputs["Vector"])
    oi = n("ShaderNodeObjectInfo", -900, -300)
    ero, fade = WEATHER.get(meta["kind"], (.3, .2))
    # erosion noise (UV space, shifted per instance)
    add = n("ShaderNodeVectorMath", -650, -200)
    add.operation = "ADD"
    L.new(uv.outputs["UV"], add.inputs[0])
    L.new(oi.outputs["Random"], add.inputs[1])
    nz = n("ShaderNodeTexNoise", -450, -200, Scale=9.0, Detail=6.0, Roughness=.65)
    L.new(add.outputs[0], nz.inputs["Vector"])
    mr = n("ShaderNodeMapRange", -250, -200)
    mr.inputs["From Min"].default_value = ero * .9
    mr.inputs["From Max"].default_value = ero * .9 + .08
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mul = n("ShaderNodeMath", 0, -100)
    mul.operation = "MULTIPLY"
    L.new(tex.outputs["Alpha"], mul.inputs[0])
    L.new(mr.outputs["Result"], mul.inputs[1])
    # fade toward a dusty paper/wall tone + dirt
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.location = (200, 150)
    mix.inputs["Factor"].default_value = fade
    L.new(tex.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = (.55, .52, .46, 1)
    dirt = n("ShaderNodeTexNoise", -450, 350, Scale=3.0, Detail=4.0)
    L.new(add.outputs[0], dirt.inputs["Vector"])
    dm = n("ShaderNodeMapRange", -200, 350)
    dm.inputs["To Min"].default_value, dm.inputs["To Max"].default_value = .7, 1.0
    L.new(dirt.outputs["Fac"], dm.inputs["Value"])
    mul2 = nt.nodes.new("ShaderNodeMix")
    mul2.data_type = "RGBA"
    mul2.blend_type = "MULTIPLY"
    mul2.location = (400, 150)
    mul2.inputs["Factor"].default_value = 1.0
    L.new(mix.outputs[2], mul2.inputs[6])
    L.new(dm.outputs["Result"], mul2.inputs[7])
    L.new(mul2.outputs[2], bsdf.inputs["Base Color"])
    L.new(mul.outputs[0], bsdf.inputs["Alpha"])
    if meta["kind"] == "sign":
        bsdf.inputs["Roughness"].default_value = .55
    L.new(bsdf.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "DITHERED"
    except AttributeError:
        pass
    m.diffuse_color = (.6, .55, .5, 1)
    m["sa_family"] = "decal_autoral"
    m["provenance"] = "autoral W3.1 (bake_decals_w31.py)"
    return m


def piece(root, did, meta, coll, flat=False):
    w, h = meta["size_m"]
    mb = sa_bl.MeshBuilder()
    if flat:
        mb.verts += [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    else:
        mb.verts += [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
    mb.faces.append((0, 1, 2, 3))
    mb.mats.append(0)
    o = mb.to_object(("ACC_dcf_" if flat else "ACC_dc_") + did, [material(root, did, meta)], coll)
    uv = o.data.uv_layers.active.data
    for k, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv[k].uv = c
    o.visible_shadow = False
    sa_bl.props(o, sa_stage="W3.1 decal autoral", decal=did, kind=meta["kind"], size_m=list(meta["size_m"]))
    return o
