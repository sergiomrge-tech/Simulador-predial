"""W3 production vegetation for the vertical slice (requires bpy): urban trees with real branch structure and alpha leaf cards,
three LODs per species, grass tufts and spontaneous weeds. Everything is generated here (own procedural leaf/grass masks, no external
assets or images), deterministic per species.

LOD0  trunk + primary/secondary branches + 70-170 leaf cards (~0.6-1.6k tris)   -> instanced in the slice
LOD1  trunk + primary branches + ~35% of the cards (~0.3-0.6k tris)               -> library (Unity LOD group)
LOD2  the W2.5 species proxy (~0.1-0.4k tris)                                       -> far field / rest of the district
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

import sa_bl


# ---------------------------------------------------------------- materials (procedural alpha masks)
def _n(nt, kind, x, y, **inp):
    n = nt.nodes.new(kind)
    n.location = (x, y)
    for k, v in inp.items():
        n.inputs[k].default_value = v
    return n


def leaf_material(name, c1, c2, kind="leaf"):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = _n(nt, "ShaderNodeOutputMaterial", 900, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 400, 100)
    tr = _n(nt, "ShaderNodeBsdfTranslucent", 400, -200)
    mix = _n(nt, "ShaderNodeMixShader", 700, 0)
    mix.inputs[0].default_value = .22
    L.new(bsdf.outputs[0], mix.inputs[1])
    L.new(tr.outputs[0], mix.inputs[2])
    cut = _n(nt, "ShaderNodeMixShader", 800, 100)          # alpha cut applied to the whole leaf shader (principled + translucent)
    clear = _n(nt, "ShaderNodeBsdfTransparent", 600, 300)
    L.new(clear.outputs[0], cut.inputs[1])
    L.new(mix.outputs[0], cut.inputs[2])
    L.new(cut.outputs[0], out.inputs["Surface"])
    tc = _n(nt, "ShaderNodeTexCoord", -900, 0)
    if kind == "leaf":
        # clusters of rounded leaves: voronoi cells shrunk by a noise field, holes between clusters
        vor = _n(nt, "ShaderNodeTexVoronoi", -650, 100, Scale=5.0, Randomness=1.0)
        L.new(tc.outputs["UV"], vor.inputs["Vector"])
        nz = _n(nt, "ShaderNodeTexNoise", -650, -150, Scale=3.0, Detail=3.0)
        L.new(tc.outputs["UV"], nz.inputs["Vector"])
        thr = _n(nt, "ShaderNodeMath", -400, 50)
        thr.operation = "MULTIPLY_ADD"
        L.new(nz.outputs["Fac"], thr.inputs[0])
        thr.inputs[1].default_value = .3
        thr.inputs[2].default_value = .36
        lt = _n(nt, "ShaderNodeMath", -250, 50)
        lt.operation = "LESS_THAN"
        L.new(vor.outputs["Distance"], lt.inputs[0])
        L.new(thr.outputs[0], lt.inputs[1])
        # fade towards the card border so the quad outline never shows
        grad = _n(nt, "ShaderNodeTexGradient", -650, -400)
        grad.gradient_type = "QUADRATIC_SPHERE"
        mpg = _n(nt, "ShaderNodeMapping", -800, -400)
        mpg.inputs["Location"].default_value = (-.5, -.5, 0)
        mpg.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
        L.new(tc.outputs["UV"], mpg.inputs["Vector"])
        L.new(mpg.outputs["Vector"], grad.inputs["Vector"])
        inside = _n(nt, "ShaderNodeMath", -250, -400)
        inside.operation = "GREATER_THAN"
        L.new(grad.outputs["Fac"], inside.inputs[0])
        inside.inputs[1].default_value = .3
        alpha = _n(nt, "ShaderNodeMath", -100, -100)
        alpha.operation = "MULTIPLY"                      # binary alpha (cut-out leaves, no see-through haze)
        L.new(lt.outputs[0], alpha.inputs[0])
        L.new(inside.outputs[0], alpha.inputs[1])
        cv = vor.outputs["Color"]
    else:
        # grass blades: thin stripes, tapering to random heights
        wv = _n(nt, "ShaderNodeTexWave", -650, 100, Scale=6.0, Distortion=1.2, Detail=2.0)
        wv.wave_type = "BANDS"
        wv.bands_direction = "X"
        L.new(tc.outputs["UV"], wv.inputs["Vector"])
        sep = _n(nt, "ShaderNodeSeparateXYZ", -650, -200)
        L.new(tc.outputs["UV"], sep.inputs[0])
        nz = _n(nt, "ShaderNodeTexNoise", -650, -400, Scale=14.0, Detail=1.0)
        L.new(tc.outputs["UV"], nz.inputs["Vector"])
        tip = _n(nt, "ShaderNodeMath", -400, -300)
        tip.operation = "MULTIPLY_ADD"
        L.new(nz.outputs["Fac"], tip.inputs[0])
        tip.inputs[1].default_value = .9
        tip.inputs[2].default_value = .25
        below = _n(nt, "ShaderNodeMath", -250, -250)
        below.operation = "LESS_THAN"
        L.new(sep.outputs["Y"], below.inputs[0])
        L.new(tip.outputs[0], below.inputs[1])
        blade = _n(nt, "ShaderNodeMath", -400, 100)
        blade.operation = "GREATER_THAN"
        L.new(wv.outputs["Fac"], blade.inputs[0])
        blade.inputs[1].default_value = .62
        alpha = _n(nt, "ShaderNodeMath", -100, -100)
        alpha.operation = "MULTIPLY"
        L.new(blade.outputs[0], alpha.inputs[0])
        L.new(below.outputs[0], alpha.inputs[1])
        cv = nz.outputs["Color"]
    hue = _n(nt, "ShaderNodeMix", 0, 250)
    hue.data_type = "RGBA"
    sepc = _n(nt, "ShaderNodeSeparateColor", -200, 250)
    L.new(cv, sepc.inputs[0])
    L.new(sepc.outputs[0], hue.inputs["Factor"])
    hue.inputs[6].default_value = (*c1, 1)
    hue.inputs[7].default_value = (*c2, 1)
    oi = _n(nt, "ShaderNodeObjectInfo", -200, 450)
    vr = _n(nt, "ShaderNodeMapRange", 0, 450, **{"To Min": .82, "To Max": 1.12})
    L.new(oi.outputs["Random"], vr.inputs["Value"])
    sc = _n(nt, "ShaderNodeVectorMath", 200, 300)
    sc.operation = "SCALE"
    L.new(hue.outputs[2], sc.inputs[0])
    L.new(vr.outputs["Result"], sc.inputs["Scale"])
    L.new(sc.outputs[0], bsdf.inputs["Base Color"])
    L.new(sc.outputs[0], tr.inputs["Color"])
    bsdf.inputs["Roughness"].default_value = .55
    L.new(alpha.outputs[0], cut.inputs[0])
    try:
        mat.surface_render_method = "DITHERED"
        mat.use_backface_culling = False
        mat.use_transparent_shadow = True
    except AttributeError:
        mat.blend_method = "CLIP"
    mat.diffuse_color = (*c1, 1)
    mat["sa_family"] = "vegetacao"
    mat["sa_status"] = "W3 vegetação de produção: máscara alpha procedural própria"
    return mat


LEAF_COLORS = {"oiti": ((.06, .16, .05), (.12, .25, .07)), "sibipiruna": ((.16, .26, .07), (.30, .40, .12)),
               "mangueira": ((.04, .11, .04), (.09, .19, .06)), "ipe": ((.18, .28, .08), (.30, .38, .12)),
               "ipe_flor": ((.80, .62, .08), (.95, .78, .18)), "ipe_rosa_flor": ((.70, .30, .50), (.86, .48, .66)),
               "jovem": ((.12, .24, .06), (.22, .34, .09)), "palmeira": ((.14, .25, .07), (.24, .34, .10)),
               "arbusto": ((.07, .17, .05), (.14, .27, .07)), "grama": ((.16, .25, .06), (.40, .40, .16)), "erva": ((.12, .22, .05), (.30, .36, .10))}


# ---------------------------------------------------------------- geometry helpers
def tube(mb, a, b, ra, rb, segs, mat):
    a, b = Vector(a), Vector(b)
    axis = (b - a)
    if axis.length < 1e-4:
        return
    z = axis.normalized()
    x = z.orthogonal().normalized()
    y = z.cross(x)
    base = len(mb.verts)
    for (p, r) in ((a, ra), (b, rb)):
        for k in range(segs):
            t = 2 * math.pi * k / segs
            mb.verts.append(tuple(p + (x * math.cos(t) + y * math.sin(t)) * r))
    for k in range(segs):
        k2 = (k + 1) % segs
        mb.faces.append((base + k, base + k2, base + segs + k2, base + segs + k))
        mb.mats.append(mat)


def card(mb, centre, normal, size, spin, mat, uv_store):
    n = Vector(normal).normalized()
    x = n.orthogonal().normalized()
    y = n.cross(x)
    rot = Matrix.Rotation(spin, 3, n)
    x, y = rot @ x, rot @ y
    c = Vector(centre)
    h = size / 2
    base = len(mb.verts)
    for (sx, sy) in ((-h, -h), (h, -h), (h, h), (-h, h)):
        mb.verts.append(tuple(c + x * sx + y * sy))
    mb.faces.append((base, base + 1, base + 2, base + 3))
    mb.mats.append(mat)
    uv_store.append(((0, 0), (1, 0), (1, 1), (0, 1)))


SPECIES = {
    #            trunk_h, r0,  crown centre z, radii (x, z), primaries, cards, card size, leaf key, flower key
    "oiti":       (2.6, .17, 4.4, (2.6, 1.9), 5, 150, .95, "oiti", None),
    "sibipiruna": (3.4, .20, 5.5, (3.8, 1.5), 6, 160, 1.05, "sibipiruna", None),
    "mangueira":  (2.2, .27, 4.6, (3.6, 2.6), 6, 175, 1.1, "mangueira", None),
    "ipe":        (3.0, .13, 4.6, (2.1, 1.5), 4, 70, .85, "ipe", "ipe_flor"),
    "ipe_rosa":   (3.0, .13, 4.6, (2.1, 1.5), 4, 70, .85, "ipe", "ipe_rosa_flor"),
    "jovem":      (1.6, .06, 2.5, (1.0, .9), 3, 30, .6, "jovem", None),
    "arbusto":    (0.0, .0, .6, (.9, .55), 0, 40, .6, "arbusto", None),
}


def tree(name, lib, coll, lod=0, seed=None):
    """Build species `name` at LOD `lod` (0 or 1) as one object at the origin (pivot at the trunk base)."""
    rng = random.Random(seed if seed is not None else hash(name) & 0xffff)
    mb = sa_bl.MeshBuilder()
    uvs = []
    mats = [lib["tronco"]]
    if name == "palmeira":
        return palm(name, lib, coll, lod, rng)
    th, r0, cz, (rx, rz), prim, ncards, csize, leaf, flower = SPECIES[name]
    lm = leaf_material("folha_" + leaf, *LEAF_COLORS[leaf])
    mats.append(lm)
    if flower:
        mats.append(leaf_material("folha_" + flower, *LEAF_COLORS[flower]))
    if th > 0:
        lean = Vector((rng.uniform(-.08, .08), rng.uniform(-.08, .08), 1)).normalized()
        top = lean * th
        tube(mb, (0, 0, 0), top, r0, r0 * .72, 8 if lod == 0 else 6, 0)
        tips = []
        for k in range(prim):
            a = 2 * math.pi * k / prim + rng.uniform(-.3, .3)
            out = Vector((math.cos(a) * rx * rng.uniform(.45, .75), math.sin(a) * rx * rng.uniform(.45, .75), cz - th + rng.uniform(-.2, rz * .6)))
            p1 = top + out
            tube(mb, top, p1, r0 * .5, r0 * .18, 6 if lod == 0 else 5, 0)
            tips.append(p1)
            if lod == 0:
                for j in range(2):
                    d2 = (p1 - top).normalized() + Vector((rng.uniform(-.6, .6), rng.uniform(-.6, .6), rng.uniform(.0, .6)))
                    p2 = p1 + d2.normalized() * rng.uniform(.6, 1.2)
                    mid = top.lerp(p1, rng.uniform(.5, .8))
                    tube(mb, mid, p2, r0 * .16, r0 * .06, 4, 0)
                    tips.append(p2)
    else:
        tips = [Vector((0, 0, cz))]
    n = int(ncards * 3.6) if lod == 0 else max(12, int(ncards * 1.1))
    centre = Vector((0, 0, cz))
    for k in range(n):
        # cards cluster around branch tips and fill the crown ellipsoid shell
        if tips and rng.random() < .55:
            base = rng.choice(tips) + Vector((rng.uniform(-.7, .7), rng.uniform(-.7, .7), rng.uniform(-.4, .6)))
        else:
            u, v = rng.uniform(0, 2 * math.pi), math.acos(rng.uniform(-.6, 1))
            sh = rng.uniform(.55, 1.0)
            base = centre + Vector((math.sin(v) * math.cos(u) * rx * sh, math.sin(v) * math.sin(u) * rx * sh, math.cos(v) * rz * sh))
        normal = (base - centre).normalized() + Vector((rng.uniform(-.5, .5), rng.uniform(-.5, .5), rng.uniform(-.2, .8)))
        size = csize * rng.uniform(.9, 1.4) * (1.0 if lod == 0 else 1.6)
        mat = 2 if (flower and rng.random() < .45) else 1
        card(mb, base, normal, size, rng.uniform(0, 6.28), mat, uvs)
    if name == "jovem":
        for dx in (-.25, .25):
            tube(mb, (dx, 0, 0), (dx, 0, 1.6), .025, .025, 4, len(mats))
        mats.append(lib["madeira_crua"])
    o = _finish(mb, uvs, mats, coll, f"VEG_{name}" + ("" if lod == 0 else f"_LOD{lod}"))
    sa_bl.props(o, sa_stage="W3 vegetação de produção", species=name, lod=lod)
    return o


def palm(name, lib, coll, lod, rng):
    mb = sa_bl.MeshBuilder()
    uvs = []
    lm = leaf_material("folha_palmeira", *LEAF_COLORS["palmeira"])
    tube(mb, (0, 0, 0), (0, 0, 11.0), .24, .2, 10 if lod == 0 else 6, 0)
    for k in range(4):
        tube(mb, (0, 0, k * 2.6), (0, 0, k * 2.6 + .08), .26, .26, 10, 0)        # trunk rings
    lm = leaf_material("folha_palmeira_frond", *LEAF_COLORS["palmeira"], kind="grass")
    nf = 16 if lod == 0 else 9
    for k in range(nf):
        a = k * 2 * math.pi / nf + rng.uniform(-.15, .15)
        d = Vector((math.cos(a), math.sin(a), 0))
        w = d.cross(Vector((0, 0, 1)))
        lift = rng.uniform(-.2, .4)
        pts = [Vector((0, 0, 11.1)), Vector((0, 0, 11.1)) + d * 1.6 + Vector((0, 0, .45 + lift)), Vector((0, 0, 11.1)) + d * 3.3 + Vector((0, 0, -1.1 + lift))]
        wid = (.15, .75, .1)
        for j in range(2):                                                         # frond as two leaflet strips (blade mask across)
            a0, a1 = pts[j], pts[j + 1]
            base = len(mb.verts)
            for p in (a0 - w * wid[j], a0 + w * wid[j], a1 + w * wid[j + 1], a1 - w * wid[j + 1]):
                mb.verts.append(tuple(p))
            mb.faces.append((base, base + 1, base + 2, base + 3))
            mb.mats.append(1)
            uvs.append(((0, j / 2), (1, j / 2), (1, (j + 1) / 2), (0, (j + 1) / 2)))
    o = _finish(mb, uvs, [lib["tronco"], lm], coll, "VEG_palmeira" + ("" if lod == 0 else f"_LOD{lod}"))
    sa_bl.props(o, sa_stage="W3 vegetação de produção", species=name, lod=lod)
    return o


def tuft(kind, lib, coll):
    """Grass tuft (3 crossed blade cards) or weed clump (small leaf cards) for slopes, greens and cracks."""
    rng = random.Random(7 if kind == "grama" else 9)
    mb = sa_bl.MeshBuilder()
    uvs = []
    mat = leaf_material("folha_" + kind, *LEAF_COLORS[kind], kind="grass" if kind == "grama" else "leaf")
    if kind == "grama":
        for k in range(3):
            a = k * math.pi / 3
            d = Vector((math.cos(a), math.sin(a), 0)) * .28
            base = len(mb.verts)
            for p in ((-d.x, -d.y, 0), (d.x, d.y, 0), (d.x, d.y, .42), (-d.x, -d.y, .42)):
                mb.verts.append(p)
            mb.faces.append((base, base + 1, base + 2, base + 3))
            mb.mats.append(0)
            uvs.append(((0, 0), (1, 0), (1, 1), (0, 1)))
    else:
        for k in range(7):
            card(mb, (rng.uniform(-.15, .15), rng.uniform(-.15, .15), rng.uniform(.05, .25)), (rng.uniform(-.5, .5), rng.uniform(-.5, .5), 1),
                 rng.uniform(.18, .3), rng.uniform(0, 6.28), 0, uvs)
    o = _finish(mb, uvs, [mat], coll, f"VEG_tufo_{kind}")
    sa_bl.props(o, sa_stage="W3 vegetação de produção", species=kind, lod=0)
    return o


def _finish(mb, uvs, mats, coll, name):
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.verts, [], mb.faces)
    me.update()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mb.mats)
    uv = me.uv_layers.new(name="UVMap")
    # card faces carry 0..1 UVs (leaf masks); tube faces get a simple cylindrical-ish mapping
    li = 0
    card_iter = iter(uvs)
    for poly in me.polygons:
        if mats[poly.material_index].get("sa_family") == "vegetacao" and len(poly.loop_indices) == 4:
            q = next(card_iter, ((0, 0), (1, 0), (1, 1), (0, 1)))
            for k, l in enumerate(poly.loop_indices):
                uv.data[l].uv = q[k]
        else:
            for l in poly.loop_indices:
                co = me.vertices[me.loops[l].vertex_index].co
                uv.data[l].uv = (math.atan2(co.y, co.x) * .3, co.z * .5)
    for poly in me.polygons:
        poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o
