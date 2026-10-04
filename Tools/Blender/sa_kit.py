"""Santa Aurora Old Town modular kit + provisional urban infrastructure props (requires bpy).

All pieces are metric, have real thickness and bevelled edges (LOD0 base for final art, never final low-poly).
Pieces are built with the same parametric code as buildings (sa_arch.Facade) so kit and buildings stay consistent.
"""
import math

import bmesh
import bpy

import sa_arch
from sa_arch import S, Facade
from sa_bl import MeshBuilder, bevelled_object, props

KIT_SLOT_MATS = ["reboco_antigo", "concreto_pintado", "madeira_pintada", "vidro", "ceramica_telha", "concreto",
                 "madeira_pintada", "metal_galvanizado", "plastico", "ferrugem", "vidro_vitrine", "tijolo_aparente"]


def _fac(mb, L):
    return Facade(mb, (0.0, 0.0), (1.0, 0.0), (0.0, -1.0), L)


def _piece(name, mb, lib, coll, family, bevel=.012, mats=None, **meta):
    obj = bevelled_object(name, mb, [lib[m] for m in (mats or KIT_SLOT_MATS)], coll, bevel=bevel)
    props(obj, sa_kit_family=family, sa_stage="W1.5 kit base (LOD0 base, não final)", **meta)
    return obj


def build_kit(lib, coll):
    out = {}

    def add(name, mb, family, **kw):
        out[name] = _piece(name, mb, lib, coll, family, **kw)

    H = 3.0
    for L in (1.0, 2.0, 3.0):
        mb = MeshBuilder()
        _fac(mb, L).wall_band(0, H, [])
        add(f"KIT_Wall_Plain_{int(L)}m", mb, "parede", size=f"{L}x0.25x{H}")
    mb = MeshBuilder(); f = _fac(mb, 2.0)
    o = {"u0": .4, "u1": 1.6, "zb": .95, "zt": 2.25}
    f.wall_band(0, H, [o]); f.window(o, trim=True)
    add("KIT_Wall_Window_2m", mb, "parede")
    mb = MeshBuilder(); f = _fac(mb, 3.0)
    o = {"u0": .75, "u1": 2.25, "zb": .9, "zt": 2.3}
    f.wall_band(0, H, [o]); f.window(o, trim=False, grille=True)
    add("KIT_Wall_Window_3m_Grade", mb, "parede")
    mb = MeshBuilder(); f = _fac(mb, 2.0)
    o = {"u0": .55, "u1": 1.45, "zb": 0.0, "zt": 2.15}
    f.wall_band(0, H, [o]); f.door(o, transom=False)
    add("KIT_Wall_Door_2m", mb, "parede")
    mb = MeshBuilder(); f = _fac(mb, 4.0)
    o = {"u0": .3, "u1": 3.7, "zb": 0.0, "zt": 3.0}
    f.wall_band(0, 4.2, [o]); f.shopfront(o, __import__("random").Random(3))
    add("KIT_Wall_Shopfront_4m", mb, "parede")
    mb = MeshBuilder(); f = _fac(mb, 4.0)
    o = {"u0": .5, "u1": 3.5, "zb": 0.0, "zt": 3.2}
    f.wall_band(0, 4.2, [o]); f.rollup(o)
    add("KIT_Wall_RollUp_4m", mb, "parede")
    mb = MeshBuilder(); f = _fac(mb, 3.0)
    o = {"u0": 1.0, "u1": 2.0, "zb": 0.0, "zt": 2.3}
    f.wall_band(0, H, [o]); f.door(o, mat=S["frame"]); f.balcony(.4, 2.6, 0.0)
    add("KIT_Wall_Balcony_3m", mb, "parede")
    mb = MeshBuilder(); mb.box(0, 0, 0, .32, .32, H, S["facade"])
    add("KIT_Corner_Pilaster", mb, "quina", bevel=.02)
    mb = MeshBuilder(); mb.box(.125, .125, 0, .25, .25, H, S["facade"])
    add("KIT_Corner_Outer", mb, "quina", bevel=.015)
    # Stand-alone doors and windows (frames + leaves/glass).
    for name, w, h, kind in (("KIT_Door_Single", .9, 2.15, "door"), ("KIT_Door_Double", 1.6, 2.3, "door"),
                             ("KIT_Window_120x120", 1.2, 1.2, "win"), ("KIT_Window_150x130", 1.5, 1.3, "win"),
                             ("KIT_Window_80x200", .8, 2.0, "win"), ("KIT_Window_60x50", .6, .5, "win")):
        mb = MeshBuilder(); f = _fac(mb, w + .2)
        o = {"u0": .1, "u1": .1 + w, "zb": 0.0 if kind == "door" else .0, "zt": h}
        if kind == "door":
            f.door(o, step=False)
        else:
            f.window(o, trim=False, sill=True)
        add(name, mb, "porta" if kind == "door" else "janela")
    mb = MeshBuilder(); f = _fac(mb, 1.0)
    f.box(0, 1, 0, .12, -.06, .0, S["trim"]); f.box(0, 1, .12, .22, -.14, .0, S["trim"]); f.box(0, 1, .22, .34, -.24, .0, S["trim"])
    add("KIT_Molding_Cornice_1m", mb, "moldura", bevel=.008)
    mb = MeshBuilder(); f = _fac(mb, 1.0)
    f.box(0, 1, 0, .16, -.06, 0, S["trim"])
    add("KIT_Molding_StringCourse_1m", mb, "moldura", bevel=.008)
    mb = MeshBuilder(); f = _fac(mb, 1.44)
    for (u0, u1, z0, z1) in ((0, .12, 0, 1.32), (1.32, 1.44, 0, 1.32), (0, 1.44, 1.2, 1.32)):
        f.box(u0, u1, z0, z1, -.04, 0, S["trim"])
    add("KIT_Molding_WindowSurround_120", mb, "moldura", bevel=.006)
    # Roof pieces.
    mb = MeshBuilder()
    pitch = .3
    mb.add_face([(0, 0, 0), (2, 0, 0), (2, 4, 4 * pitch), (0, 4, 4 * pitch)], S["roof"])
    mb.add_face([(0, 4, 4 * pitch - .14), (2, 4, 4 * pitch - .14), (2, 0, -.14), (0, 0, -.14)], S["roof"])
    mb.add_face([(0, 0, -.14), (2, 0, -.14), (2, 0, 0), (0, 0, 0)], S["trim"])
    mb.add_face([(2, 0, -.14), (2, 4, 4 * pitch - .14), (2, 4, 4 * pitch), (2, 0, 0)], S["roof"])
    mb.add_face([(0, 4, 4 * pitch - .14), (0, 0, -.14), (0, 0, 0), (0, 4, 4 * pitch)], S["roof"])
    add("KIT_Roof_Tile_Slope_2m", mb, "telhado", bevel=.01)
    mb = MeshBuilder(); mb.box(0, 0, 0, 1.0, .32, .14, S["roof"])
    add("KIT_Roof_Ridge_1m", mb, "telhado", bevel=.03)
    mb = MeshBuilder(); mb.box(0, 0, 0, 1.0, .15, .9, S["facade"]); mb.box(0, 0, .9, 1.0, .24, .07, S["trim"])
    add("KIT_Roof_Parapet_1m", mb, "telhado", bevel=.01)
    mb = MeshBuilder(); mb.box(0, 0, 0, 2.0, 4.0, .06, S["roof"])
    add("KIT_Roof_Corrugated_2m", mb, "telhado", bevel=.004, mats=KIT_SLOT_MATS[:4] + ["telha_fibrocimento"] + KIT_SLOT_MATS[5:])
    mb = MeshBuilder()
    mb.box(0, -.3, 0, 1.0, .6, .03, S["trim"])
    mb.box(0, -.6, -.15, 1.0, .03, .2, S["trim"])
    for k in range(3):
        mb.box(-.4 + k * .4, -.3, .03, .06, .6, .1, S["door"])
    add("KIT_Eave_1m", mb, "beiral", bevel=.006)
    mb = MeshBuilder(); f = _fac(mb, 1.2)
    f.window({"u0": 0, "u1": 1.2, "zb": 0, "zt": 1.2}, grille=True, sill=False)
    add("KIT_Grille_Window_120", mb, "grade", bevel=.003)
    mb = MeshBuilder(); f = _fac(mb, 1.0)
    f.balcony(0, 1.0, 0, depth=.1)
    add("KIT_Railing_1m", mb, "grade", bevel=.003)
    mb = MeshBuilder()
    for x in (0.0, 4.0):
        mb.box(x, 0, 0, .06, .06, 2.0, S["metal"])
    mb.box(2.0, 0, 1.94, 4.06, .06, .06, S["metal"]); mb.box(2.0, 0, .05, 4.06, .06, .06, S["metal"])
    for k in range(1, 40):
        mb.box(k * .1, 0, .08, .018, .018, 1.86, S["metal"])
    for x in (.4, 3.6):
        mb.cylinder(x, 0, -.06, .07, .02, 12, S["rust"])
    add("KIT_Gate_Sliding_4m", mb, "portao", bevel=.004)
    mb = MeshBuilder()
    mb.box(0, 0, 0, .05, .05, 2.0, S["metal"]); mb.box(1.0, 0, 0, .05, .05, 2.0, S["metal"])
    mb.box(.5, 0, 1.95, 1.0, .05, .05, S["metal"]); mb.box(.5, 0, .05, 1.0, .05, .05, S["metal"])
    for k in range(1, 9):
        mb.box(k * .11, 0, .08, .016, .016, 1.86, S["metal"])
    add("KIT_Gate_Pedestrian_1m", mb, "portao", bevel=.004)
    mb = MeshBuilder()
    mb.box(0, 0, 0, 1.0, .14, .012, S["metal"]); mb.box(0, -.065, 0, 1.0, .012, .12, S["metal"]); mb.box(0, .065, 0, 1.0, .012, .09, S["metal"])
    add("KIT_Gutter_1m", mb, "calha", bevel=.003)
    mb = MeshBuilder()
    mb.cylinder(0, 0, .2, .05, 2.8, 12, S["metal"])
    mb.box(.12, 0, .1, .3, .1, .1, S["metal"])
    for z in (.8, 2.2):
        mb.box(0, .06, z, .14, .04, .04, S["metal"])
    add("KIT_Downpipe_3m", mb, "calha", bevel=.004)
    mb = MeshBuilder()
    for k in range(17):
        mb.box(0, k * .28, k * .175, 1.2, .28, .175, S["plinth"])
    mb.box(-.62, 17 * .14, 0, .04, 17 * .28, 17 * .175 + .9, S["metal"], top=True)
    add("KIT_Stair_Flight_120", mb, "escada", bevel=.008, rise=.175, tread=.28)
    mb = MeshBuilder()
    for k in range(3):
        mb.box(0, -k * .3, 0, 1.6 + .2 * (2 - k), .3, .17 * (3 - k), S["plinth"])
    add("KIT_Stair_Entry_3", mb, "escada", bevel=.01)
    mb = MeshBuilder()
    mb.add_face([(-.75, 0, 0), (.75, 0, 0), (.75, 6.0, .5), (-.75, 6.0, .5)], S["plinth"])
    for x in (-.8, .8):
        mb.box(x, 3.0, 0, .1, 6.0, .55, S["plinth"])
    add("KIT_Ramp_1to12", mb, "rampa", bevel=.01, slope="8.3%")
    mb = MeshBuilder()
    mb.box(1.0, 0, 0, 2.0, .15, 2.0, S["facade"]); mb.box(1.0, 0, 2.0, 2.06, .22, .06, S["trim"])
    mb.box(0, 0, 0, .3, .3, 2.15, S["facade"])
    add("KIT_Muro_2m", mb, "muro", bevel=.01)
    mb = MeshBuilder(); mb.box(0, 0, 0, .3, .3, 2.15, S["facade"]); mb.box(0, 0, 2.15, .36, .36, .06, S["trim"])
    add("KIT_Muro_Pilar", mb, "muro", bevel=.01)
    side_mats = ["calcada", "meio_fio", "madeira_pintada", "vidro", "ceramica_telha", "concreto", "madeira_pintada", "metal_galvanizado", "plastico", "ferrugem", "vidro_vitrine", "asfalto"]
    mb = MeshBuilder(); mb.box(0, 0, -.1, 2.0, 2.0, .1, S["facade"])
    add("KIT_Sidewalk_Slab_2m", mb, "calcada", bevel=.004, mats=side_mats)
    mb = MeshBuilder(); mb.box(0, 0, -.15, 2.0, .15, .3, S["trim"])
    add("KIT_Curb_2m", mb, "calcada", bevel=.012, mats=side_mats)
    mb = MeshBuilder()
    r0, r1 = 3.0, 3.15
    for k in range(8):
        a0, a1 = math.pi / 2 * k / 8, math.pi / 2 * (k + 1) / 8
        q = [(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)), (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))]
        mb.prism(q, -.15, .3, S["trim"])
    add("KIT_Curb_Corner_r3", mb, "calcada", bevel=.01, mats=side_mats)
    mb = MeshBuilder(); mb.box(0, 0, -.06, 2.0, .4, .06, S["trim"]); mb.box(0, .21, -.06, 2.0, .02, .03, S["trim"])
    add("KIT_Sarjeta_2m", mb, "calcada", bevel=.004, mats=side_mats)
    return out


def _tapered(mb, r0, r1, h, segs, mat, z0=0.0):
    ring0 = [(r0 * math.cos(2 * math.pi * k / segs), r0 * math.sin(2 * math.pi * k / segs), z0) for k in range(segs)]
    ring1 = [(r1 * math.cos(2 * math.pi * k / segs), r1 * math.sin(2 * math.pi * k / segs), z0 + h) for k in range(segs)]
    for k in range(segs):
        j = (k + 1) % segs
        mb.quad(ring0[k], ring0[j], ring1[j], ring1[k], mat)
    mb.add_face(ring1, mat)


PROP_MATS = ["concreto", "metal_galvanizado", "aco_pintado_cinza", "pintura_industrial", "plastico", "ferrugem", "vidro", "pintura_vermelha", "tronco", "folhagem", "concreto_pintado"]
PM = {n: i for i, n in enumerate(PROP_MATS)}


def build_props(lib, coll):
    if "pintura_vermelha" not in lib:
        import sa_materials
        spec = dict(sa_materials.LIB["pintura_industrial"])
        spec.update({"c1": (.62, .08, .06), "c2": (.48, .05, .04)})
        lib["pintura_vermelha"] = sa_materials.build_material("pintura_vermelha", spec)
    mats = [lib[m] for m in PROP_MATS]
    out = {}

    def add(name, mb, kind, bevel=.01, **kw):
        obj = bevelled_object(name, mb, mats, coll, bevel=bevel)
        props(obj, sa_prop=kind, sa_stage="W1.5 provisório de produção (escala correta, não final)", **kw)
        out[name] = obj

    def pole(mb, transformer=False):
        _tapered(mb, .17, .09, 9.0, 8, PM["concreto"])
        mb.box(0, 0, 8.4, 2.2, .1, .1, PM["concreto"])
        for x in (-.9, 0, .9):
            mb.cylinder(x, 0, 8.5, .04, .16, 8, PM["vidro"])
        # luminaire arm toward the street (+Y local is the street side after rotation)
        mb.box(0, -.8, 7.6, .06, 1.6, .06, PM["metal_galvanizado"])
        mb.box(0, -1.65, 7.5, .26, .6, .12, PM["aco_pintado_cinza"])
        if transformer:
            mb.cylinder(0, .45, 6.0, .32, 1.1, 14, PM["aco_pintado_cinza"])
            mb.box(0, .2, 6.5, .1, .3, .1, PM["metal_galvanizado"])
            mb.box(0, .45, 7.1, .5, .5, .05, PM["aco_pintado_cinza"])

    mb = MeshBuilder(); pole(mb)
    add("PROP_Pole_Concrete", mb, "pole", height_m=9.0)
    mb = MeshBuilder(); pole(mb, True)
    add("PROP_Pole_Transformer", mb, "pole_transformer", height_m=9.0)
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0, .16, .12, 12, PM["pintura_vermelha"])
    mb.cylinder(0, 0, .12, .12, .55, 12, PM["pintura_vermelha"])
    mb.cylinder(0, 0, .67, .14, .06, 12, PM["pintura_vermelha"])
    mb.cylinder(0, 0, .73, .07, .08, 10, PM["pintura_vermelha"])
    for sx in (-1, 1):
        mb.box(sx * .17, 0, .42, .12, .1, .1, PM["pintura_vermelha"])
    add("PROP_Hydrant", mb, "hydrant", bevel=.006)
    mb = MeshBuilder()
    mb.cylinder(0, 0, -.02, .42, .05, 20, PM["ferrugem"])
    mb.cylinder(0, 0, .0, .34, .035, 20, PM["metal_galvanizado"])
    add("PROP_Manhole", mb, "manhole", bevel=.004)
    mb = MeshBuilder()
    mb.box(0, 0, -.02, .9, .4, .04, PM["ferrugem"])
    for k in range(7):
        mb.box(-.36 + k * .12, 0, .015, .03, .34, .01, PM["metal_galvanizado"])
    mb.box(0, .25, .0, 1.0, .1, .12, PM["concreto"])
    add("PROP_StormInlet", mb, "storm_inlet", bevel=.004)
    mb = MeshBuilder()
    mb.box(0, 0, 0, .7, .45, .12, PM["concreto"]); mb.box(0, 0, .12, .6, .35, 1.15, PM["aco_pintado_cinza"])
    mb.box(0, -.18, .3, .5, .02, .8, PM["metal_galvanizado"])
    add("PROP_TelecomBox", mb, "telecom_box", bevel=.008)
    mb = MeshBuilder()
    mb.box(0, 0, 1.2, .45, .22, .6, PM["aco_pintado_cinza"]); mb.box(0, -.12, 1.3, .3, .02, .3, PM["vidro"])
    mb.cylinder(0, 0, .1, .025, 1.1, 8, PM["metal_galvanizado"])
    add("PROP_ElectricBox", mb, "electric_box", bevel=.006)
    mb = MeshBuilder()
    mb.box(0, 0, .2, .4, .22, .45, PM["concreto_pintado"]); mb.box(0, -.115, .28, .3, .02, .3, PM["metal_galvanizado"])
    add("PROP_WaterMeter", mb, "water_meter", bevel=.006)
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0, .03, 2.9, 8, PM["metal_galvanizado"])
    mb.box(.3, 0, 2.7, .62, .02, .18, PM["plastico"]); mb.box(0, .3, 2.48, .02, .62, .18, PM["plastico"])
    add("PROP_StreetSign", mb, "street_sign", bevel=.004)
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0, .03, 2.3, 8, PM["metal_galvanizado"])
    oct_pts = [(.3 * math.cos(math.pi / 8 + k * math.pi / 4), .3 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    for k in range(8):
        a, b = oct_pts[k], oct_pts[(k + 1) % 8]
        mb.quad((a[0], -.03, 2.3 + a[1]), (b[0], -.03, 2.3 + b[1]), (b[0], -.01, 2.3 + b[1]), (a[0], -.01, 2.3 + a[1]), PM["pintura_vermelha"])
    mb.add_face([(p[0], -.03, 2.3 + p[1]) for p in oct_pts][::-1], PM["pintura_vermelha"])
    add("PROP_StopSign", mb, "stop_sign", bevel=.003)
    mb = MeshBuilder()
    mb.cylinder(0, 0, 0, .09, 4.2, 12, PM["aco_pintado_cinza"])
    mb.box(0, -1.6, 4.1, .08, 3.2, .08, PM["aco_pintado_cinza"])
    mb.box(0, -3.1, 3.4, .32, .26, .95, PM["aco_pintado_cinza"])
    for k, z in enumerate((4.1, 3.82, 3.54)):
        mb.cylinder(0, -3.24, z - .1, .1, .03, 12, PM["vidro"])
    mb.box(0, .12, 2.3, .28, .22, .75, PM["aco_pintado_cinza"])
    add("PROP_TrafficLight", mb, "traffic_light", bevel=.006)
    mb = MeshBuilder()
    for x in (-.7, .7):
        mb.box(x, 0, 0, .12, .45, .42, PM["concreto"])
    mb.box(0, 0, .42, 1.7, .48, .08, PM["concreto"])
    add("PROP_Bench", mb, "bench", bevel=.01)
    mb = MeshBuilder(); mb.cylinder(0, 0, 0, .1, .85, 12, PM["aco_pintado_cinza"])
    add("PROP_Bollard", mb, "bollard", bevel=.008)
    # Vegetation proxies (blockout: replaced by authored trees with LOD in W3/W4).
    for name, h, cr in (("PROP_Tree_A", 7.0, 2.6), ("PROP_Tree_B", 9.5, 3.4)):
        mb = MeshBuilder()
        _tapered(mb, .16, .09, h * .55, 8, PM["tronco"])
        me_bm = bmesh.new()
        import random as _r
        rr = _r.Random(len(name))
        for k in range(6):
            bmesh.ops.create_icosphere(me_bm, subdivisions=2, radius=cr * rr.uniform(.55, .8),
                                       matrix=__import__("mathutils").Matrix.Translation((rr.uniform(-cr * .5, cr * .5), rr.uniform(-cr * .5, cr * .5), h * .62 + rr.uniform(0, cr * .7))))
        for v in me_bm.verts:
            pass
        verts = [tuple(v.co) for v in me_bm.verts]
        base = len(mb.verts)
        mb.verts.extend(verts)
        for fce in me_bm.faces:
            mb.faces.append(tuple(base + v.index for v in fce.verts))
            mb.mats.append(PM["folhagem"])
        me_bm.free()
        add(name, mb, "tree_proxy", bevel=0.0, blockout=True)
    return out
