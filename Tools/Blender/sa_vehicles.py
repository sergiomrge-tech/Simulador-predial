"""W3.1 vehicles: authored, generic (no real make, model or logo) parked cars for Santa Aurora (requires bpy).

Five families with their own silhouettes: hatch compacto, sedan, utilitário leve (picape), SUV compacto, van de serviço,
plus an older boxy hatch for the outer neighbourhoods. Each car: body (rounded side profile + narrower greenhouse), glass,
4 wheels (tyre, rim, hub), wheel-arch liners, bumpers, headlights, tail lights, mirrors, door seams, handles and a fictional
plate. LOD0 (bevelled, ~1.5-2.5k tris) / LOD1 (no bevel, low segment wheels, ~0.4k tris) / proxy (W2.5 box car).
"""
import math
import random
import zlib

import bmesh
import bpy
from mathutils import Vector

import sa_bl

FAMILIES = {
    # length, width, wheelbase, wheel r, profile: list of (x, z) along the side (front at +x), greenhouse (x0, x1, top, bel, rake f, rake r)
    "hatch":    dict(L=3.85, W=1.66, wb=2.45, r=.29, prof=[(-1.92, .32), (-1.95, .62), (-1.85, .86), (1.62, .86), (1.90, .74), (1.94, .42), (1.85, .30)],
                     gh=(-1.78, .95, 1.42, .86, .55, .18)),
    "sedan":    dict(L=4.40, W=1.72, wb=2.60, r=.30, prof=[(-2.18, .34), (-2.20, .70), (-2.05, .88), (1.85, .86), (2.15, .74), (2.20, .44), (2.10, .32)],
                     gh=(-1.45, .80, 1.44, .87, .65, .55)),
    "picape":   dict(L=4.50, W=1.74, wb=2.75, r=.32, prof=[(-2.22, .40), (-2.25, .95), (2.0, .95), (2.22, .82), (2.25, .48), (2.15, .36)],
                     gh=(-.25, 1.05, 1.62, .95, .55, .05), bed=(-2.15, -.3, .95, 1.25)),
    "suv":      dict(L=4.20, W=1.80, wb=2.55, r=.34, prof=[(-2.08, .44), (-2.10, .92), (-1.98, 1.00), (1.75, .98), (2.06, .86), (2.10, .52), (2.0, .40)],
                     gh=(-1.92, .85, 1.66, 1.0, .5, .12)),
    "van":      dict(L=4.95, W=1.90, wb=3.00, r=.32, prof=[(-2.45, .40), (-2.48, 2.05), (1.60, 2.05), (2.30, 1.10), (2.45, .62), (2.35, .38)],
                     gh=(1.55, 2.08, 1.95, 1.1, .7, 0.0), van=True),
    "hatch_antigo": dict(L=3.70, W=1.60, wb=2.40, r=.28, prof=[(-1.84, .32), (-1.86, .80), (1.70, .80), (1.85, .70), (1.86, .40), (1.80, .30)],
                         gh=(-1.70, .85, 1.36, .80, .25, .08)),
}
PAINTS = {"branco": (.86, .86, .84), "prata": (.62, .63, .64), "vermelho": (.50, .06, .05), "azul_escuro": (.05, .09, .22),
          "preto": (.03, .03, .035), "bege": (.68, .60, .45), "verde_velho": (.20, .30, .20), "amarelo_servico": (.82, .62, .06)}


def paint_material(lib, key, worn=False):
    name = f"pintura_carro_{key}" + ("_gasta" if worn else "")
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    c = PAINTS[key]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.5 if not worn else 9.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = (.45, .8) if not worn else (.56, .72)
    mr.inputs["To Max"].default_value = .15 if not worn else .35
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    mix.inputs[6].default_value = (*c, 1)
    mix.inputs[7].default_value = ((.30, .28, .25, 1) if worn else (*(v * .7 for v in c), 1))      # dust / oxidised paint
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = .22 if not worn else .6
    b.inputs["Coat Weight"].default_value = .6 if not worn else 0.0
    b.inputs["Metallic"].default_value = .35 if key in ("prata", "azul_escuro") and not worn else 0.0
    m.diffuse_color = (*c, 1)
    m["sa_family"] = "pintura_veiculo"
    return m


def glass_material():
    """Tinted automotive glass: dark, glossy and opaque (reads as a reflective window, no refraction noise)."""
    if "vidro_veiculo" in bpy.data.materials:
        return bpy.data.materials["vidro_veiculo"]
    m = bpy.data.materials.new("vidro_veiculo")
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (.015, .02, .025, 1)
    b.inputs["Roughness"].default_value = .04
    b.inputs["Specular IOR Level"].default_value = .8
    m.diffuse_color = (.02, .025, .03, 1)
    return m


def light_material(name, color, strength):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Emission Color"].default_value = (*color, 1)
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = .1
    m.diffuse_color = (*color, 1)
    return m


def _wheel(mb, cx, cy, r, w, segs, m_tyre, m_rim):
    """Horizontal wheel along Y: tyre (with sidewall bulge), rim face and hub."""
    for (ra, rb, y0, y1, mat) in ((r * .93, r, -w / 2, w / 2, m_tyre), (r * .62, r * .62, -w / 2 - .005, -w / 2 + .02, m_rim)):
        base = len(mb.verts)
        for yy in (y0, y1):
            for k in range(segs):
                t = 2 * math.pi * k / segs
                rr = rb
                mb.verts.append((cx + math.cos(t) * rr, cy + yy, r + math.sin(t) * rr))
        for k in range(segs):
            k2 = (k + 1) % segs
            mb.faces.append((base + k, base + k2, base + segs + k2, base + segs + k))
            mb.mats.append(mat)
        for side, off in ((0, 0), (1, segs)):                       # caps
            idx = [base + off + k for k in range(segs)]
            mb.faces.append(tuple(idx if side else idx[::-1]))
            mb.mats.append(m_rim if side == 0 else mat)


def build(family, lib, coll, paint="branco", worn=False, lod=0, name=None, plate_seed=0):
    f = FAMILIES[family]
    L, W, wb, r = f["L"], f["W"], f["wb"], f["r"]
    mb = sa_bl.MeshBuilder()
    M = {"paint": 0, "glass": 1, "tyre": 2, "rim": 3, "trim": 4, "head": 5, "tail": 6, "plate": 7, "liner": 8}
    # lower body: side profile with real wheel-arch cut-outs, extruded across the width
    prof = _profile_with_arches(f["prof"], wb, r)
    hw = W / 2
    n = len(prof)
    narch = len(f["prof"])
    base = len(mb.verts)
    for (x, z) in prof:
        mb.verts.append((x, -hw, z))
    for (x, z) in prof:
        mb.verts.append((x, hw, z))
    mb.faces.append(tuple(base + k for k in range(n))[::-1])
    mb.mats.append(M["paint"])
    mb.faces.append(tuple(base + n + k for k in range(n)))
    mb.mats.append(M["paint"])
    for k in range(n):
        k2 = (k + 1) % n
        mb.faces.append((base + k, base + k2, base + n + k2, base + n + k))
        mb.mats.append(M["liner"] if k >= narch and k2 >= narch else M["paint"])
    # greenhouse (cabin): trapezoid in side view, narrower than the body, glass sides and paint roof
    x0, x1, top, bel, rf, rr = f["gh"]
    gw = hw - .1
    if not f.get("van"):
        pts = [(x0, bel), (x1, bel), (x1 - rf, top), (x0 + rr, top)]
        base = len(mb.verts)
        for (x, z) in pts:
            mb.verts.append((x, -gw, z))
        for (x, z) in pts:
            mb.verts.append((x, gw, z))
        mb.faces.append((base + 3, base + 2, base + 1, base + 0))
        mb.mats.append(M["glass"])
        mb.faces.append((base + 4, base + 5, base + 6, base + 7))
        mb.mats.append(M["glass"])
        for k, mat in ((0, M["paint"]), (1, M["glass"]), (2, M["paint"]), (3, M["glass"])):
            k2 = (k + 1) % 4
            mb.faces.append((base + k, base + k2, base + 4 + k2, base + 4 + k))
            mb.mats.append(mat)
    if f.get("van"):                                                     # van: big side glass band behind the cab, sliding door seam
        mb.box(-.6, -hw - .002, 1.25, 3.4, .01, .55, M["glass"])
        mb.box(-.6, hw + .002, 1.25, 3.4, .01, .55, M["glass"])
        mb.box(.2, -hw - .004, .45, .02, .01, 1.5, M["trim"])
        (ax, az), (bx, bz) = (1.60, 2.05), (2.30, 1.10)                  # windshield on the sloped nose
        nx, nz = (az - bz), (bx - ax)
        ln = math.hypot(nx, nz)
        ox, oz = nx / ln * .012, nz / ln * .012
        t0, t1 = .08, .78
        pa = (ax + (bx - ax) * t0 + ox, az + (bz - az) * t0 + oz)
        pb = (ax + (bx - ax) * t1 + ox, az + (bz - az) * t1 + oz)
        mb.add_face([(pb[0], -hw + .1, pb[1]), (pb[0], hw - .1, pb[1]), (pa[0], hw - .1, pa[1]), (pa[0], -hw + .1, pa[1])], M["glass"])
        for s in (-1, 1):
            mb.box(1.3, s * (hw + .002), 1.22, .62, .01, .6, M["glass"])    # cab door windows
    if f.get("bed"):                                                     # pick-up bed walls
        bx0, bx1, bz0, bz1 = f["bed"]
        for yy in (-hw + .04, hw - .04):
            mb.box((bx0 + bx1) / 2, yy, bz0, bx1 - bx0, .06, bz1 - bz0, M["paint"])
        mb.box(bx0 + .03, 0, bz0, .06, W - .08, bz1 - bz0, M["paint"])
        mb.box((bx0 + bx1) / 2, 0, bz0 - .02, bx1 - bx0, W - .1, .03, M["trim"])
    # wheels, arch liners
    segs = 14 if lod == 0 else 8
    for xw in (wb / 2, -wb / 2):
        for s in (-1, 1):
            _wheel(mb, xw, s * (hw - .12), r, .2, segs, M["tyre"], M["rim"])
    # bumpers, lights, plates, mirrors, handles, seams
    fx, bxm = max(p[0] for p in prof), min(p[0] for p in prof)
    mb.box(fx + .01, 0, .3, .12, W - .06, .2, M["trim"])
    mb.box(bxm - .01, 0, .32, .12, W - .06, .2, M["trim"])
    zl = .62 if not f.get("van") else .85
    for s in (-1, 1):
        mb.box(fx - .015, s * (hw - .28), zl, .04, .34, .12, M["head"])
        mb.box(bxm + .015, s * (hw - .2), zl + .04, .04, .28, .15, M["tail"])
        mb.box((x1 - .05) if not f.get("van") else 1.68, s * (hw + .07), bel + .08, .14, .1, .1, M["paint"])        # mirrors
        for xh in (.35, -.55):
            mb.box(xh, s * (hw + .006), bel - .14, .14, .015, .03, M["trim"])       # handles
        mb.box(-.1, s * (hw + .003), .45, .01, .006, bel - .5, M["trim"])          # door seam
    mb.box(fx - .005, 0, zl - .01, .02, W - .9, .1, M["trim"])                          # grille
    for xp in ((x0 + rr + .07, (x0 + x1) / 2 + .1) if not f.get("van") else ()):          # B/C pillars over the side glass
        for s in (-1, 1):
            mb.box(xp, s * (gw + .004), bel, .09, .01, top - bel, M["paint"])
    mb.box(fx + .07, 0, .4, .02, .4, .13, M["plate"])
    mb.box(bxm - .07, 0, .44, .02, .4, .13, M["plate"])
    mats = [paint_material(lib, paint, worn), glass_material(), lib["borracha_preta"], lib["aco_inox" if lod == 0 else "aluminio"],
            lib["borracha_preta"], light_material("farol_veiculo", (.9, .9, .85), .5), light_material("lanterna_veiculo", (.6, .04, .03), .8),
            lib["plastico_branco"], lib["borracha_preta"]]
    nm = name or f"VEH_{family}_{paint}" + ("_gasto" if worn else "") + ("" if lod == 0 else f"_LOD{lod}")
    o = _object(nm, mb, mats, coll, bevel=.03 if lod == 0 else 0.0)
    # fictional plate text (Mercosul-like layout, invented letters) on LOD0 only
    if lod == 0:
        rng = random.Random(plate_seed or zlib.crc32(nm.encode()))
        txt = "SA" + rng.choice("ABCDEFGH") + " " + str(rng.randint(0, 9)) + rng.choice("ABCDEFGHJK") + f"{rng.randint(10, 99)}"
        try:
            from sa_w2 import text_mesh
            for sgn, xx in ((1, fx + .085), (-1, bxm - .085)):
                t = text_mesh(nm + f"_placa{sgn}", txt, .055, coll, lib["borracha_preta"], extrude=.002)
                t.location = (xx, 0, .435 if sgn > 0 else .475)
                t.rotation_euler = (math.pi / 2, 0, math.pi / 2 if sgn > 0 else -math.pi / 2)
                bpy.context.view_layer.update()
                t.data.transform(t.matrix_basis)
                t.matrix_basis.identity()
                _join(o, t)
        except Exception:
            pass
    sa_bl.props(o, sa_stage="W3.1 veículo autoral (genérico, sem marca)", vehicle_family=family, paint=paint, worn=worn, lod=lod)
    return o


def _profile_with_arches(prof, wb, r):
    """Closes the side profile along the sill (front -> rear) with semicircular wheel arches."""
    pts = list(prof)
    zf, zr = prof[-1][1], prof[0][1]
    ar = r + .045
    for xw, zb in ((wb / 2, zf), (-wb / 2, zr)):
        t0 = math.asin(max(-1.0, min(.95, (zb - r) / ar)))
        for k in range(13):
            t = t0 + (math.pi - 2 * t0) * k / 12
            pts.append((xw + ar * math.cos(t), r + ar * math.sin(t)))
    return pts


def _object(name, mb, materials, coll, bevel=.03):
    """Welds, triangulates concave n-gons (the arched side panels) and bevels the body edges."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.verts, [], mb.faces)
    me.update()
    for m in materials:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mb.mats)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.triangulate(bm, faces=[fc for fc in bm.faces if len(fc.verts) > 4], ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if bevel > 0:
        lim = math.radians(25)
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim]
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=1, profile=.5, affect="EDGES", clamp_overlap=True)
    bm.to_mesh(me)
    bm.free()
    sa_bl.write_box_uvs(me)
    me.shade_smooth()
    try:
        me.set_sharp_from_angle(angle=math.radians(35))
    except AttributeError:
        pass
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o


def _join(target, other):
    me, ome = target.data, other.data
    nv = len(me.vertices)
    verts = [tuple(v.co) for v in me.vertices] + [tuple(v.co) for v in ome.vertices]
    faces = [tuple(p.vertices) for p in me.polygons] + [tuple(i + nv for i in p.vertices) for p in ome.polygons]
    mi = [p.material_index for p in me.polygons]
    mats = list(me.materials)
    om = ome.materials[0] if ome.materials else mats[0]
    if om not in mats:
        mats.append(om)
    mi += [mats.index(om)] * len(ome.polygons)
    smooth = [p.use_smooth for p in me.polygons] + [False] * len(ome.polygons)
    new = bpy.data.meshes.new(me.name)
    new.from_pydata(verts, [], faces)
    for m in mats:
        new.materials.append(m)
    new.polygons.foreach_set("material_index", mi)
    new.polygons.foreach_set("use_smooth", smooth)
    sa_bl.write_box_uvs(new)
    target.data = new
    bpy.data.objects.remove(other)


LIBRARY = [  # (family, paint, worn) variants instanced in the slice
    ("hatch", "branco", False), ("hatch", "vermelho", False), ("hatch", "prata", False), ("hatch", "preto", False),
    ("sedan", "prata", False), ("sedan", "azul_escuro", False), ("sedan", "branco", False), ("sedan", "bege", True),
    ("picape", "branco", False), ("picape", "verde_velho", True), ("suv", "preto", False), ("suv", "prata", False), ("suv", "vermelho", False),
    ("van", "branco", False), ("van", "amarelo_servico", False), ("hatch_antigo", "bege", True), ("hatch_antigo", "verde_velho", True),
    ("hatch_antigo", "azul_escuro", True), ("sedan", "verde_velho", True),
]

PAINT_ORDER = ("vermelho", "verde_velho", "branco", "prata", "azul_escuro", "bege", "preto")


def instance(family, lib, coll, paint, worn, name, lod=0):
    """Object sharing one mesh per (family, paint, worn, lod) variant."""
    key = f"VEHMESH_{family}_{paint}_{int(bool(worn))}_L{lod}"
    me = bpy.data.meshes.get(key)
    if me is None:
        o = build(family, lib, coll, paint, worn, lod, name=name)
        o.data.name = key
        return o
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    sa_bl.props(o, sa_stage="W3.1 veículo autoral (genérico, sem marca)", vehicle_family=family, paint=paint, worn=bool(worn), lod=lod)
    return o


def proxy(family, lib, coll):
    """Distance proxy: two boxes (body + cabin) with the family's footprint and height."""
    f = FAMILIES[family]
    L, W = f["L"], f["W"]
    hz = max(z for _, z in f["prof"])
    x0, x1, top, bel, rf, rr = f["gh"]
    mb = sa_bl.MeshBuilder()
    mb.box(0, 0, .25, L, W, hz - .25, 0)
    if not f.get("van"):
        mb.box((x0 + x1) / 2, 0, hz, x1 - x0 - rf * .5, W - .2, top - hz, 1)
    o = mb.to_object(f"VEH_{family}_PROXY", [paint_material(lib, "prata"), glass_material()], coll)
    sa_bl.props(o, sa_stage="W3.1 veículo proxy (distância)", vehicle_family=family, lod="proxy")
    return o
