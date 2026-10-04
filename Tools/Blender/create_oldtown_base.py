"""Generate the Cidade Antiga production base (W1.5) from the shared Old Town layout.

Run:
blender --background --factory-startup --python Tools/Blender/create_oldtown_base.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend
ArtSource/Blender/World/OldTown/oldtown_generation_report.json
ArtSource/Blender/World/OldTown/oldtown_streaming_manifest_v1.json
ArtSource/Materials/material_library_v1.json

Content is production STRUCTURE (S1/S2 base): real street network, sidewalks/curbs, building family instances,
hero architecture, provisional infrastructure props at correct scale and streaming organisation.
It is NOT final art: final surfaces, decals, clutter and LODs follow the Art Bible (never low-poly as final).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_arch  # noqa: E402
import sa_bl  # noqa: E402
import sa_heroes  # noqa: E402
import sa_kit  # noqa: E402
import sa_materials  # noqa: E402
from masterplan_layout import load_spec  # noqa: E402
from oldtown_layout import OldTown, rail_x  # noqa: E402
from sa_geom import dist, lerp, norm, perp, resample
from sa_geom import sub as vsub  # noqa: E402
from sa_terrain import Terrain  # noqa: E402
from urban_fabric import OLDTOWN_VARIANTS, STREET, carriageway  # noqa: E402

LAYERS = ["Terrain", "Roads", "Architecture", "Infrastructure", "Props", "Vegetation", "Lighting", "Gameplay"]
BOUNDS = (-3950.0, -3950.0, -1100.0, -350.0)
SIDEWALK_H = 0.15
ROAD_LIFT = 0.05


def subcell(x, y):
    ix, iz = int((x + 4000) // 1000), int((y + 4000) // 1000)
    sx, sz = int(((x + 4000) % 1000) // 250), int(((y + 4000) % 1000) // 250)
    return f"SA_M{ix:02d}_{iz:02d}", f"SA_M{ix:02d}_{iz:02d}_S{sx:02d}_{sz:02d}"


spec = load_spec(root)
terrain = Terrain(spec)
ot = OldTown(root, spec)
sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "SantaAurora_CidadeAntiga_W1_5"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0

lib = sa_materials.build_library()
import sa_detail  # noqa: E402
sa_detail.extend_library(lib)
sa_materials.write_library_json(root)

top = sa_bl.collection("OT_CidadeAntiga")
library = sa_bl.collection("OT_Library", top, hide_render=True)
layer_coll = {L: sa_bl.collection(f"OT_{L}", top) for L in LAYERS}
cams = sa_bl.collection("OT_Cameras", top)
cell_colls = {}


def cell_collection(layer, macro):
    key = (layer, macro)
    if key not in cell_colls:
        cell_colls[key] = sa_bl.collection(f"OT_{layer}_{macro}", layer_coll[layer])
    return cell_colls[key]


manifest = {"subcells": {}, "heroes": {}, "lots": []}


def register(layer, name, sub, obj, **extra):
    d = manifest["subcells"].setdefault(sub, {})
    d.setdefault(layer, []).append(name)
    sa_bl.props(obj, sa_layer=layer, sa_cell=sub[:9], sa_subcell=sub, **extra)


# ---------------------------------------------------------------- libraries
kit_coll = sa_bl.collection("OT_Lib_Kit", library, hide_render=True)
kit = sa_kit.build_kit(lib, kit_coll)
props_coll_tmp = sa_bl.collection("OT_Lib_Props_tmp", library, hide_render=True)
props_objs = sa_kit.build_props(lib, props_coll_tmp)
props_lib, props_index = sa_bl.library_collection("OT_Lib_Props", list(props_objs.values()), library)
bpy.data.collections.remove(props_coll_tmp)

fam_tmp = sa_bl.collection("OT_Lib_Families_tmp", library, hide_render=True)
fam_objs = []
variant_stats = {}
for k, v in enumerate(OLDTOWN_VARIANTS):
    mb = sa_bl.MeshBuilder()
    top_z = sa_arch.building_mesh(mb, v, k)
    o = mb.to_object("FAM_" + v["id"], [lib[n] for n in sa_arch.variant_materials(v, k)], fam_tmp)
    sa_bl.props(o, sa_family=v["family"], sa_variant=v["id"], footprint_m=[v["w"], v["d"]], floors=v["floors"], height_m=v["height"],
                roof=v["roof"], sa_stage="W1.5 famÃ­lia de massing (LOD1 base; LOD0 final pendente)")
    variant_stats[v["id"]] = {"faces": len(mb.faces), "top_z": round(top_z, 2)}
    fam_objs.append(o)
fam_lib, fam_index = sa_bl.library_collection("OT_Lib_Families", fam_objs, library)
bpy.data.collections.remove(fam_tmp)

PROP_FOR = {"pole": "PROP_Pole_Concrete", "pole_transformer": "PROP_Pole_Transformer", "hydrant": "PROP_Hydrant", "manhole": "PROP_Manhole",
            "storm_inlet": "PROP_StormInlet", "telecom_box": "PROP_TelecomBox", "electric_box": "PROP_ElectricBox", "water_meter": "PROP_WaterMeter",
            "street_sign": "PROP_StreetSign", "stop_sign": "PROP_StopSign", "traffic_light": "PROP_TrafficLight", "bench": "PROP_Bench",
            "bollard": "PROP_Bollard"}
INFRA_KINDS = {"pole", "pole_transformer", "hydrant", "manhole", "storm_inlet", "telecom_box", "electric_box", "water_meter", "traffic_light"}
PROP_KINDS = {"street_sign", "stop_sign", "bench", "bollard"}

# ---------------------------------------------------------------- terrain (per subcell)
STEP = 8.0
x0, y0, x1, y1 = BOUNDS
nx, ny = int((x1 - x0) // STEP), int((y1 - y0) // STEP)
H = [[terrain.ground(x0 + i * STEP, y0 + j * STEP) for j in range(ny + 1)] for i in range(nx + 1)]
buckets = {}
for i in range(nx):
    for j in range(ny):
        cx, cy = x0 + (i + .5) * STEP, y0 + (j + .5) * STEP
        macro, sub = subcell(cx, cy)
        buckets.setdefault((macro, sub), []).append((i, j))
for (macro, sub), quads in buckets.items():
    mb = sa_bl.MeshBuilder()
    for i, j in quads:
        a = (x0 + i * STEP, y0 + j * STEP, H[i][j])
        b = (x0 + (i + 1) * STEP, y0 + j * STEP, H[i + 1][j])
        c = (x0 + (i + 1) * STEP, y0 + (j + 1) * STEP, H[i + 1][j + 1])
        d = (x0 + i * STEP, y0 + (j + 1) * STEP, H[i][j + 1])
        mb.quad(a, b, c, d, 0)
    name = f"OT_Terrain_{sub}"
    o = mb.to_object(name, [lib["terra"]], cell_collection("Terrain", macro), uv_scale=4.0)
    register("Terrain", name, sub, o)

# ---------------------------------------------------------------- roads, sidewalks, curbs, markings
g = ot.graph
deg = g.degree()
inc = g.incident()
ROAD_MATS = ["asfalto", "asfalto_gasto", "calcada", "meio_fio", "sinalizacao_viaria", "grama", "concreto", "terra", "piso_intertravado"]
STATS = {"corners_filleted": 0, "curb_ramps": 0, "accessories": {}, "forecourt_planters": 0, "forecourt_bollards": 0}
RM = {n: i for i, n in enumerate(ROAD_MATS)}
road_mb = {}


def rmb(p):
    macro, sub = subcell(*p)
    key = (macro, sub)
    if key not in road_mb:
        road_mb[key] = sa_bl.MeshBuilder()
    return road_mb[key]


def zs(x, y):
    return terrain.surface(x, y)


def trim(nid):
    if deg.get(nid, 0) >= 3:
        return max(carriageway(g.edges[e]["cls"]) for e in inc[nid]) / 2 + .6
    return 0.0


def strip(mb, a, b, off, width, lift, mat, curb=False, curb_side=1):
    """Strip parallel to segment ab at lateral offset; optional curb face on its inner edge."""
    u = norm(vsub(b, a))
    n = perp(u)
    pts = resample([a, b], 4.0)
    left, right = [], []
    for p in pts:
        l = (p[0] + n[0] * (off + width / 2), p[1] + n[1] * (off + width / 2))
        r = (p[0] + n[0] * (off - width / 2), p[1] + n[1] * (off - width / 2))
        left.append((l[0], l[1], zs(*l) + lift))
        right.append((r[0], r[1], zs(*r) + lift))
    for i in range(len(pts) - 1):
        mb.quad(right[i], right[i + 1], left[i + 1], left[i], mat)
    if curb:
        edge = right if curb_side > 0 else left
        for i in range(len(pts) - 1):
            p, q = edge[i], edge[i + 1]
            lo_p, lo_q = (p[0], p[1], p[2] - SIDEWALK_H), (q[0], q[1], q[2] - SIDEWALK_H)
            if curb_side > 0:
                mb.quad(lo_p, lo_q, q, p, RM["meio_fio"])
            else:
                mb.quad(lo_q, lo_p, p, q, RM["meio_fio"])


for eid, e in g.edges.items():
    a, b = g.seg(eid)
    cls = e["cls"]
    L = dist(a, b)
    if L < .5:
        continue
    mid = lerp(a, b, .5)
    mb = rmb(mid)
    u = norm(vsub(b, a))
    cw = carriageway(cls)
    sw = STREET[cls]["sidewalk"]
    if cls == "passage":
        strip(mb, a, b, 0, STREET[cls]["total"], SIDEWALK_H + ROAD_LIFT, RM["calcada"])
        continue
    surf = RM["asfalto_gasto"] if cls in ("alley", "service", "local") else RM["asfalto"]
    strip(mb, a, b, 0, cw, ROAD_LIFT, surf)
    ta, tb = trim(e["a"]), trim(e["b"])
    if L - ta - tb > .5 and sw > 0:
        sa = (a[0] + u[0] * ta, a[1] + u[1] * ta)
        sb = (b[0] - u[0] * tb, b[1] - u[1] * tb)
        strip(mb, sa, sb, cw / 2 + sw / 2, sw, ROAD_LIFT + SIDEWALK_H, RM["calcada"], curb=True, curb_side=1)
        strip(mb, sa, sb, -(cw / 2 + sw / 2), sw, ROAD_LIFT + SIDEWALK_H, RM["calcada"], curb=True, curb_side=-1)
    if cls == "arterial":
        strip(mb, a, b, 0, 3.0, ROAD_LIFT + SIDEWALK_H, RM["grama"], curb=False)
        for s_ in (1, -1):
            strip(mb, a, b, s_ * 1.6, .2, ROAD_LIFT + SIDEWALK_H, RM["meio_fio"])
            strip(mb, a, b, s_ * 5.2, .12, ROAD_LIFT + .006, RM["sinalizacao_viaria"])
    if cls in ("main", "local", "arterial"):
        # dashed lane marking
        t = 2.0 + ta
        while t < L - 3 - tb:
            p = (a[0] + u[0] * t, a[1] + u[1] * t)
            q = (a[0] + u[0] * (t + 3), a[1] + u[1] * (t + 3))
            if cls == "arterial":
                for s_ in (1, -1):
                    strip(mb, p, q, s_ * 3.4, .12, ROAD_LIFT + .006, RM["sinalizacao_viaria"])
            elif cls == "main":
                strip(mb, p, q, 0, .12, ROAD_LIFT + .006, RM["sinalizacao_viaria"])
            t += 8.0 if cls != "local" else 1e9

for nid, eids in inc.items():
    if deg.get(nid, 0) < 3:
        continue
    p = g.nodes[nid]
    mb = rmb(p)
    r = trim(nid)
    poly = [(p[0] + r * math.cos(2 * math.pi * k / 16), p[1] + r * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    mb.add_face([(q[0], q[1], zs(*q) + ROAD_LIFT + .004) for q in poly], RM["asfalto"])
    # Corner sidewalk pieces between consecutive approaches.
    dirs = []
    for e in eids:
        ed = g.edges[e]
        other = ed["b"] if ed["a"] == nid else ed["a"]
        d = norm(vsub(g.nodes[other], p))
        dirs.append((math.atan2(d[1], d[0]), d, carriageway(ed["cls"]), STREET[ed["cls"]]["sidewalk"]))
    dirs.sort()
    for k in range(len(dirs)):
        a1, d1, cw1, sw1 = dirs[k]
        a2, d2, cw2, sw2 = dirs[(k + 1) % len(dirs)]
        if sw1 <= 0 or sw2 <= 0:
            continue
        gap = (a2 - a1) % (2 * math.pi)
        if gap > math.radians(170) or gap < math.radians(20):
            continue
        n1, n2 = perp(d1), perp(d2)
        A = (p[0] + d1[0] * r + n1[0] * cw1 / 2, p[1] + d1[1] * r + n1[1] * cw1 / 2)
        B = (p[0] + d1[0] * r + n1[0] * (cw1 / 2 + sw1), p[1] + d1[1] * r + n1[1] * (cw1 / 2 + sw1))
        C = (p[0] + d2[0] * r - n2[0] * (cw2 / 2 + sw2), p[1] + d2[1] * r - n2[1] * (cw2 / 2 + sw2))
        D = (p[0] + d2[0] * r - n2[0] * cw2 / 2, p[1] + d2[1] * r - n2[1] * cw2 / 2)
        # W2 (N3): filleted corner. Inner (curb) and outer edges follow quadratic curves whose control points are the
        # intersections of the two curb lines, so the corner bends with the streets instead of a straight chamfer.
        def meet(P0, dA, P1, dB):
            den = dA[0] * dB[1] - dA[1] * dB[0]
            if abs(den) < 1e-3:
                return ((P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2)
            t = ((P1[0] - P0[0]) * dB[1] - (P1[1] - P0[1]) * dB[0]) / den
            X = (P0[0] + dA[0] * t, P0[1] + dA[1] * t)
            if dist(X, p) > 3 * r + 12:
                return ((P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2)
            return X

        ci, co = meet(A, d1, D, d2), meet(B, d1, C, d2)
        nseg = 8
        bez = lambda P0, Q, P1, t: ((1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * Q[0] + t * t * P1[0], (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * Q[1] + t * t * P1[1])
        inner = [bez(A, ci, D, k / nseg) for k in range(nseg + 1)]
        outer_ = [bez(B, co, C, k / nseg) for k in range(nseg + 1)]
        ramp = ot.in_core(p) and gap < math.radians(135)
        zt = lambda q: zs(*q) + ROAD_LIFT + SIDEWALK_H
        zi = []
        for k, q in enumerate(inner):
            low = ramp and 3 <= k <= 5                                     # curb cut (rebaixo) at the corner apex
            zi.append(zs(*q) + ROAD_LIFT + (.02 if low else SIDEWALK_H))
        for k in range(nseg):
            a3 = (inner[k][0], inner[k][1], zi[k])
            b3 = (inner[k + 1][0], inner[k + 1][1], zi[k + 1])
            c3 = (outer_[k + 1][0], outer_[k + 1][1], zt(outer_[k + 1]))
            d3 = (outer_[k][0], outer_[k][1], zt(outer_[k]))
            mb.quad(a3, b3, c3, d3, RM["calcada"])
            lo_a, lo_b = (a3[0], a3[1], zs(*inner[k]) + ROAD_LIFT - .01), (b3[0], b3[1], zs(*inner[k + 1]) + ROAD_LIFT - .01)
            mb.quad(lo_a, lo_b, b3, a3, RM["meio_fio"])
        STATS["corners_filleted"] += 1
        if ramp:
            STATS["curb_ramps"] += 1
            for k in (3, 5):
                q = inner[k]
                mb.box(q[0], q[1], zs(*q) + ROAD_LIFT + .015, .25, .25, .006, RM["sinalizacao_viaria"])  # tactile marker
    # Zebra crossings where traffic lights stand (major x major).
    majors = {g.edges[e].get("name") for e in eids if g.edges[e]["cls"] in ("main", "arterial")}
    if len(majors) >= 2 and ot.in_core(p):
        for ang, d, cw, sw in dirs:
            if cw < 7:
                continue
            n = perp(d)
            base = (p[0] + d[0] * (r + 2.5), p[1] + d[1] * (r + 2.5))
            k = -cw / 2 + .6
            while k < cw / 2 - .4:
                c0 = (base[0] + n[0] * k, base[1] + n[1] * k)
                strip(mb, c0, (c0[0] + d[0] * 3.0, c0[1] + d[1] * 3.0), 0, .5, ROAD_LIFT + .007, RM["sinalizacao_viaria"])
                k += 1.0

# Plazas, parking lots, vacant lots ("terrenos"), driveway aprons for big doors.
for pl in ot.data["plazas"]:
    px0, py0, px1, py1 = pl["rect"]
    c = ((px0 + px1) / 2, (py0 + py1) / 2)
    mb = rmb(c)
    zc = zs(*c)
    mb.box(c[0], c[1], zc - .8, px1 - px0, py1 - py0, .8 + ROAD_LIFT + SIDEWALK_H, RM["calcada"])
    for gx in (px0 + (px1 - px0) * .25, px0 + (px1 - px0) * .75):
        mb.box(gx, c[1], zc + ROAD_LIFT + SIDEWALK_H, (px1 - px0) * .18, (py1 - py0) * .4, .25, RM["grama"])
# Hero forecourts: paved, at sidewalk level (they stay open between facade and street).
for hid, fc in ot.forecourts().items():
    mb = rmb(fc.c)
    zc = min(zs(*q) for q in fc.corners())
    mb.obb_box(fc.corners(), zc - .6, .6 + ROAD_LIFT + SIDEWALK_H - .01, RM["piso_intertravado"])
    # W2 (N4): planters at the two street-side corners and a bollard line, leaving the entrance axis free.
    h = next(hh for hh in ot.data["heroes"] if hh["id"] == hid)
    hc = ((h["lot"][0] + h["lot"][2]) / 2, (h["lot"][1] + h["lot"][3]) / 2)
    cs_ = sorted(fc.corners(), key=lambda q: -dist(q, hc))[:2]
    ztop = zc + ROAD_LIFT + SIDEWALK_H - .01
    edge = norm(vsub(cs_[1], cs_[0]))
    elen = dist(cs_[0], cs_[1])
    inward = norm(vsub(fc.c, lerp(cs_[0], cs_[1], .5)))
    ang = math.atan2(edge[1], edge[0])
    for k, q in enumerate(cs_):
        s_ = 1 if k == 0 else -1
        c = (q[0] + edge[0] * s_ * 1.6 + inward[0] * 1.0, q[1] + edge[1] * s_ * 1.6 + inward[1] * 1.0)
        mb.box(c[0], c[1], ztop, 2.6, 1.2, .45, RM["concreto"], rot=ang)
        mb.box(c[0], c[1], ztop + .45, 2.4, 1.0, .03, RM["grama"], rot=ang)
        STATS["forecourt_planters"] += 1
    n_b = int(elen // 1.8)
    for k in range(1, n_b):
        t = k * elen / n_b
        if abs(t - elen / 2) < 2.2 or t < 3.4 or t > elen - 3.4:
            continue
        c = (cs_[0][0] + edge[0] * t + inward[0] * .4, cs_[0][1] + edge[1] * t + inward[1] * .4)
        mb.cylinder(c[0], c[1], ztop, .1, .85, 10, RM["concreto"])
        STATS["forecourt_bollards"] += 1
for lot in ot.lots:
    if lot["family"] not in ("vacant", "parking"):
        continue
    o = lot["obb"]
    mb = rmb(o.c)
    zc = min(zs(*q) for q in o.corners())
    if lot["family"] == "parking":
        mb.obb_box(o.corners(), zc - .3, .3 + ROAD_LIFT, RM["asfalto_gasto"])
        nst = int(o.hw * 2 // 2.6)
        for k in range(nst + 1):
            uu = -o.hw + k * 2.6
            pa = (o.c[0] + o.u[0] * uu + o.v[0] * -o.hd * .1, o.c[1] + o.u[1] * uu + o.v[1] * -o.hd * .1)
            pb = (o.c[0] + o.u[0] * uu + o.v[0] * o.hd * .9, o.c[1] + o.u[1] * uu + o.v[1] * o.hd * .9)
            strip(mb, pa, pb, 0, .1, ROAD_LIFT + .007, RM["sinalizacao_viaria"])
    else:
        mb.obb_box(o.corners(), zc - .3, .3 + .02, RM["terra"])
for lot in ot.lots:
    v = None
    if lot["family"] in ("vacant", "parking"):
        continue
    if lot["variant"] in ("ofi_a", "ofi_b", "ofi_c", "ofi_d", "arm_a", "arm_b", "arm_c", "arm_d", "dep_a", "dep_b", "dep_c", "dep_d", "ab_d"):
        f = lot["front"]
        back = norm(vsub(lot["obb"].c, f))
        a = (f[0] - back[0] * 2.0, f[1] - back[1] * 2.0)
        b = (f[0] + back[0] * (lot.get("setback", 0) + .4), f[1] + back[1] * (lot.get("setback", 0) + .4))
        strip(rmb(f), a, b, 0, 4.5, ROAD_LIFT + SIDEWALK_H + .01, RM["concreto"])

# Railway: ballast, sleepers and rails (sleepers only near the Old Town).
for rail in spec["railways"]:
    pts = [tuple(p) for p in rail["points"]]
    pts = [p for p in resample(pts, 20.0) if BOUNDS[1] - 50 <= p[1] <= BOUNDS[3] + 50 and BOUNDS[0] - 50 <= p[0] <= BOUNDS[2]]
    if len(pts) < 2:
        continue
    tracks = (-2.2, 2.2) if rail["kind"] == "main" else (0.0,)
    for a, b in zip(pts, pts[1:]):
        mb = rmb(lerp(a, b, .5))
        strip(mb, a, b, 0, rail["width"] - 2, .35, RM["terra"])
        u = norm(vsub(b, a))
        n = perp(u)
        L = dist(a, b)
        for tr in tracks:
            t = 0.3
            while t < L:
                c = (a[0] + u[0] * t + n[0] * tr, a[1] + u[1] * t + n[1] * tr)
                mb.box(c[0], c[1], zs(*c) + .35, .24, 2.6, .16, RM["concreto"], rot=math.atan2(u[1], u[0]))
                t += .65
            for s_ in (-.72, .72):
                strip(mb, a, b, tr + s_, .08, .52, RM["meio_fio"])
for (macro, sub), mb in road_mb.items():
    name = f"OT_Roads_{sub}"
    o = mb.to_object(name, [lib[m] for m in ROAD_MATS], cell_collection("Roads", macro))
    register("Roads", name, sub, o)

# ---------------------------------------------------------------- architecture: family instances per subcell
arch_pts = {}
for lot in ot.lots:
    if lot["family"] in ("vacant", "parking"):
        continue
    o = lot["obb"]
    zc = min(zs(*q) for q in o.corners())
    macro, sub = subcell(*o.c)
    arch_pts.setdefault((macro, sub), []).append((o.c[0], o.c[1], zc, fam_index["FAM_" + lot["variant"]], lot["rot"], 1.0))
    manifest["lots"].append({"id": lot["id"], "variant": lot["variant"], "family": lot["family"], "x": round(o.c[0], 2), "y": round(o.c[1], 2),
                             "z": round(zc, 2), "rot": round(lot["rot"], 4), "subcell": sub, "neighbourhood": lot["hood"]})
for (macro, sub), pts in arch_pts.items():
    name = f"OT_Architecture_{sub}"
    o = sa_bl.point_cloud_object(name, pts, fam_lib, cell_collection("Architecture", macro))
    register("Architecture", name, sub, o, instances=len(pts))

# ---------------------------------------------------------------- W2 (N1): rule-based accessories breaking the repetition
# Small instanced pieces placed per lot from its variant (roof type, floors, tags) with a stable crc32 seed: roof water
# tanks, solar heaters, antennas, dishes, facade/back AC condensers, service-entrance boxes and downpipes.
import zlib  # noqa: E402

ACC_MATS = {"tank": ["plastico_azul", "plastico_branco"], "tank_fc": ["telha_fibrocimento", "concreto"], "solar": ["vidro", "aluminio"],
            "antenna": ["metal_galvanizado"], "dish": ["plastico_branco", "metal_galvanizado"], "ac": ["plastico_branco", "aco_pintado_cinza"],
            "meterbox": ["aco_pintado_cinza", "vidro"], "downpipe": ["plastico"]}


def acc_piece(kind):
    mb = sa_bl.MeshBuilder()
    if kind == "tank":
        mb.cylinder(0, 0, 0, .7, .9, 12, 0)
        mb.cylinder(0, 0, .9, .64, .1, 12, 1)
    elif kind == "tank_fc":
        mb.box(0, 0, 0, 1.4, 1.4, .25, 1)
        mb.box(0, 0, .25, 1.2, 1.2, .9, 0)
    elif kind == "solar":
        mb.box(0, 0, .5, 2.0, 1.0, .06, 0)
        mb.box(0, .55, .55, 1.6, .5, .5, 1)
        for x in (-.9, .9):
            mb.box(x, -.3, 0, .05, .05, .55, 1)
    elif kind == "antenna":
        mb.cylinder(0, 0, 0, .025, 2.6, 5, 0)
        for k in range(4):
            mb.box(0, 0, 1.8 + k * .22, .9 - k * .15, .02, .02, 0)
    elif kind == "dish":
        mb.cylinder(0, 0, 0, .03, .5, 5, 1)
        mb.cylinder(0, -.1, .45, .3, .06, 10, 0)
    elif kind == "ac":
        mb.box(0, -.15, 0, .78, .3, .55, 0)
        for x in (-.28, .28):
            mb.box(x, -.12, -.06, .04, .26, .06, 1)
    elif kind == "meterbox":
        mb.box(0, -.12, 0, .5, .24, .7, 0)
        mb.box(0, -.245, .3, .2, .01, .2, 1)
        mb.cylinder(.18, -.06, .7, .025, 2.4, 5, 0)
    elif kind == "downpipe":
        mb.cylinder(0, -.06, 0, .05, 1.0, 6, 0)
    # Street-distance pieces: no bevel and few segments (heroes carry the LOD0 detail; these only break repetition).
    o = mb.to_object("ACC_" + kind, [lib[m] for m in ACC_MATS[kind]], library)
    sa_bl.props(o, sa_stage="W2 acessório (LOD0 base)")
    return o


acc_objs = [acc_piece(k) for k in ACC_MATS]
acc_lib, acc_index = sa_bl.library_collection("OT_Lib_Accessories", acc_objs, library)
VAR = {v["id"]: v for v in OLDTOWN_VARIANTS}
acc_pts = {}


def place(lot, kind, lx, ly, lz, rot_extra=0.0, scl=1.0):
    o = lot["obb"]
    r = lot["rot"]
    cs, sn = math.cos(r), math.sin(r)
    x, y = o.c[0] + lx * cs - ly * sn, o.c[1] + lx * sn + ly * cs
    macro, sub = subcell(x, y)
    acc_pts.setdefault((macro, sub), []).append((x, y, lot_z[lot["id"]] + lz, acc_index["ACC_" + kind], r + rot_extra, scl))
    STATS["accessories"][kind] = STATS["accessories"].get(kind, 0) + 1


lot_z = {}
for lot in ot.lots:
    if lot["family"] in ("vacant", "parking") or lot["variant"] not in VAR:
        continue
    o = lot["obb"]
    lot_z[lot["id"]] = min(zs(*q) for q in o.corners())
    v = VAR[lot["variant"]]
    w, d, H = v["w"], v["d"], v["height"]
    lid = str(lot["id"])
    roll = lambda k, lid=lid: zlib.crc32(f"{lid}:{k}".encode()) / 4294967295.0
    flat = v["roof"] in ("flat_parapet", "roofless")
    resid = v["family"] in ("sobrado_estreito", "casa_terrea", "comercio_residencia", "predio_3pav", "predio_4a6", "abandonada_reformada")
    if v["roof"] == "roofless":
        continue
    if flat and roll(0) < .65:
        place(lot, "tank" if roll(1) < .6 else "tank_fc", (roll(2) - .5) * (w - 2.4), (roll(3) - .2) * (d - 2.4) * .5, H + .05)
    if resid and roll(4) < .25 and w >= 5:
        place(lot, "solar", (roll(5) - .5) * (w - 2.2), d * .15, H + (.05 if flat else .9))
    if roll(6) < .35:
        place(lot, "antenna", (roll(7) - .5) * (w - 1), (roll(8) - .5) * (d - 1), H + (.05 if flat else 1.2))
    if resid and roll(9) < .18:
        place(lot, "dish", w / 2 - .6, -d / 2 + 1.0, H + (.05 if flat else .6), rot_extra=.4)
    if resid and v["floors"] >= 2 and roll(10) < .4:
        f = 1 + int(roll(11) * (v["floors"] - 1))
        place(lot, "ac", (roll(12) - .5) * (w - 1.2), -d / 2, v["ground_h"] + (f - 1) * v["fh"] + .3)
    if resid and roll(13) < .5:
        place(lot, "ac", (roll(14) - .5) * (w - 1.2), d / 2, v["ground_h"] * .45, rot_extra=math.pi)
    if resid and roll(15) < .55:
        place(lot, "meterbox", (w / 2 - .45) * (1 if roll(16) < .5 else -1), -d / 2, .7)
    if roll(17) < .45 and H > 3.5:
        place(lot, "downpipe", (w / 2 - .12) * (1 if roll(18) < .5 else -1), -d / 2, 0.0, scl=1.0)
for (macro, sub), pts in acc_pts.items():
    name = f"OT_Accessories_{sub}"
    o = sa_bl.point_cloud_object(name, pts, acc_lib, cell_collection("Architecture", macro))
    register("Architecture", name, sub, o, instances=len(pts), note="W2 N1: acessórios por regra")

# Special lots (suppliers, used cars, fuel, cafÃ©, house with workshop) and the EstaÃ§Ã£o Velha landmark.
spec_coll = sa_bl.collection("OT_Architecture_SpecialLots", layer_coll["Architecture"])
SPECIAL_VARIANT = {"shop": "cr_d", "cafe": "cr_b", "house_workshop": "cas_d"}
for s_ in ot.data["specialLots"]:
    rx0, ry0, rx1, ry1 = s_["rect"]
    c = ((rx0 + rx1) / 2, (ry0 + ry1) / 2)
    zc = min(zs(rx0, ry0), zs(rx1, ry0), zs(rx1, ry1), zs(rx0, ry1))
    rot = sa_heroes.FRONT_ROT[s_["front"]]
    mb = sa_bl.MeshBuilder()
    if s_["kind"] in SPECIAL_VARIANT:
        v = dict(next(q for q in OLDTOWN_VARIANTS if q["id"] == SPECIAL_VARIANT[s_["kind"]]))
        v["w"], v["d"] = 14.0, 15.0
        sa_arch.building_mesh(mb, v, len(s_["id"]))
        mats = [lib[n] for n in sa_arch.variant_materials(v, len(s_["id"]))]
    elif s_["kind"] == "car_lot":
        mb.box(0, 0, -.3, 20, 20, .35, sa_arch.S["plinth"])
        mb.box(-6, 6, .05, 6, 5, 3.2, sa_arch.S["facade"])
        for k in range(6):
            mb.box(-7 + (k % 3) * 5, -5 + (k // 3) * 6, .05, 1.8, 4.3, 1.45, sa_arch.S["sign"])
        mb.box(0, -9.6, 0, 20, .12, 1.0, sa_arch.S["metal"])
        mats = sa_heroes.slot_mats(lib, facade="reboco_pintado")
    else:  # fuel station
        mb.box(0, 0, -.3, 20, 20, .35, sa_arch.S["plinth"])
        for px in (-6, 6):
            for py in (-4, 4):
                mb.box(px, py, .05, .4, .4, 5.0, sa_arch.S["metal"])
        mb.box(0, 0, 5.05, 16, 12, .6, sa_arch.S["sign"])
        for px in (-3, 3):
            mb.box(px, 0, .05, .8, 1.8, 1.6, sa_arch.S["sign"])
        mb.box(5, 8, .05, 6, 3.5, 3.0, sa_arch.S["facade"])
        mats = sa_heroes.slot_mats(lib, facade="concreto_pintado")
    verts = []
    cs, sn = math.cos(rot), math.sin(rot)
    mb.verts = [(c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, zc + z) for (x, y, z) in mb.verts]
    o = sa_bl.bevelled_object("OT_Special_" + s_["id"], mb, mats, spec_coll, bevel=.01)
    macro, sub = subcell(*c)
    register("Architecture", o.name, sub, o, facility_id=s_["id"], name_pt=s_["name"], sa_kind=s_["kind"])
for lm in ot.data["landmarks"]:
    rx0, ry0, rx1, ry1 = lm["rect"]
    c = ((rx0 + rx1) / 2, (ry0 + ry1) / 2)
    zc = zs(*c) + .2
    w, d = ry1 - ry0, rx1 - rx0  # station is long along the track (north-south); local front faces east
    v = {"id": "estacao", "family": "landmark", "w": w, "d": d, "floors": lm["floors"], "fh": lm["fh"], "ground_h": lm["fh"],
         "roof": lm["roof"], "attached": False, "tags": ["shop"], "height": lm["fh"] * lm["floors"]}
    mb = sa_bl.MeshBuilder()
    sa_arch.building_mesh(mb, v, 77)
    tx0, ty0, tx1, ty1 = lm["tower"]["rect"]
    mb.box(0, 0, 0, ty1 - ty0, tx1 - tx0, lm["tower"]["h"], sa_arch.S["facade"])
    mb.box(0, 0, lm["tower"]["h"], (ty1 - ty0) + .6, (tx1 - tx0) + .6, .5, sa_arch.S["trim"])
    for yy in (-(tx1 - tx0) / 2 - .02,):
        mb.cylinder(0, yy, lm["tower"]["h"] - 2.2, .9, .05, 24, sa_arch.S["sign"])
    rot = sa_heroes.FRONT_ROT["E"]
    cs, sn = math.cos(rot), math.sin(rot)
    mb.verts = [(c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, zc + z) for (x, y, z) in mb.verts]
    px0, py0, px1, py1 = lm["platform"]
    mb.box((px0 + px1) / 2, (py0 + py1) / 2, zs((px0 + px1) / 2, (py0 + py1) / 2) - .2, px1 - px0, py1 - py0, 1.1, sa_arch.S["plinth"])
    for k in range(9):
        yy = py0 + 10 + k * ((py1 - py0) - 20) / 8
        mb.box(px1 - 1.2, yy, zs(px1, yy) + .9, .2, .2, 3.4, sa_arch.S["metal"])
    mb.box((px0 + px1) / 2, (py0 + py1) / 2, zs((px0 + px1) / 2, (py0 + py1) / 2) + 4.3, px1 - px0 + 1.5, py1 - py0 - 10, .15, sa_arch.S["roof"])
    o = sa_bl.bevelled_object("OT_Landmark_EstacaoVelha", mb, sa_heroes.slot_mats(lib, facade="pedra_reboco_historico", roof_mat="ceramica_telha"),
                              spec_coll, bevel=.012)
    macro, sub = subcell(*c)
    register("Architecture", o.name, sub, o, facility_id=lm["id"], name_pt=lm["name"])

# ---------------------------------------------------------------- heroes
hero_root = sa_bl.collection("OT_Heroes", layer_coll["Architecture"])
hero_markers = sa_bl.collection("OT_Gameplay_Heroes", layer_coll["Gameplay"])
hb = sa_heroes.HeroBuilder(lib, terrain, kit, hero_root, hero_markers)
hero_z = {}
for hero in ot.data["heroes"]:
    hero_z[hero["id"]] = hb.build(hero, ot.data)
    x0h, y0h, x1h, y1h = hero["lot"]
    macro, sub = subcell((x0h + x1h) / 2, (y0h + y1h) / 2)
    manifest["heroes"][hero["id"]] = {"name": hero["name"], "subcell": sub, "ground_z": round(hero_z[hero["id"]], 2),
                                      "objects": [o.name for o in hb.objects if o.get("facility_id") == hero["id"]]}
for o in hb.objects:
    x, y = o.get("ground_z", 0), 0
for o in list(hb.objects) + [e for e in hero_markers.objects]:
    fid = o.get("facility_id")
    if fid:
        h = next(hh for hh in ot.data["heroes"] if hh["id"] == fid)
        macro, sub = subcell((h["lot"][0] + h["lot"][2]) / 2, (h["lot"][1] + h["lot"][3]) / 2)
        sa_bl.props(o, sa_cell=sub[:9], sa_subcell=sub)

# ---------------------------------------------------------------- W2 heroes: linked collection instances (LOD0), W1.5 massing kept as LOD1
# Each W2 hero .blend keeps its world transform on its root, so an instance at the origin lands in place. The W1.5 hero
# objects stay in the file (hidden in render, tagged LOD1) and keep their gameplay markers and IDs untouched.
W2_HEROES = {"home.starter": "W2_home_starter.blend", "garage": "W2_garage.blend", "horizonte": "W2_horizonte.blend", "imperial": "W2_imperial.blend"}
w2_coll = sa_bl.collection("OT_Heroes_W2_LOD0", layer_coll["Architecture"])
STATS["w2_heroes_linked"] = []
for hid, fn in W2_HEROES.items():
    path = root / "ArtSource" / "Blender" / "World" / "OldTown" / "Heroes" / fn
    if not path.exists():
        continue
    with bpy.data.libraries.load(str(path), link=True, relative=True) as (src, dst):
        dst.collections = [c for c in src.collections if c == f"W2_{hid}"]
    if not dst.collections:
        continue
    inst = bpy.data.objects.new(f"W2I_{hid}", None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = dst.collections[0]
    w2_coll.objects.link(inst)
    h = next(hh for hh in ot.data["heroes"] if hh["id"] == hid)
    macro, sub = subcell((h["lot"][0] + h["lot"][2]) / 2, (h["lot"][1] + h["lot"][3]) / 2)
    register("Architecture", inst.name, sub, inst, facility_id=hid, sa_lod="LOD0 (W2, link)", source=f"Heroes/{fn}")
    lod1 = bpy.data.collections.get("HERO_" + hid)
    proxies = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(f"PROXY_{hid}__")]
    for o in (list(lod1.all_objects) if lod1 else []) + [o for o in hb.objects if o.get("facility_id") == hid] + proxies:
        if o.type == "EMPTY" and not o.name.startswith("HERO_"):
            continue                                     # gameplay markers stay as they are
        o.hide_render = True
        o["sa_lod"] = "LOD1 (massing W1.5; LOD0 = W2I_" + hid + ")"
    STATS["w2_heroes_linked"].append(hid)

# ---------------------------------------------------------------- infrastructure, props, vegetation, lighting
infra_pts, prop_pts, tree_pts, light_pts = {}, {}, {}, {}
tree_lib, tree_index = None, None
for kind, pts in ot.points.items():
    for (x, y, rot) in pts:
        macro, sub = subcell(x, y)
        if kind == "tree":
            tree_pts.setdefault((macro, sub), []).append((x, y, zs(x, y) + ROAD_LIFT + SIDEWALK_H, 0 if (int(x * 7 + y * 3) % 3) else 1, rot, .5 + (int(x * 13 + y * 7) % 7) * .05))
            continue
        if kind == "streetlight_head":
            light_pts.setdefault((macro, sub), []).append((x, y, zs(x, y) + 7.5, 0, rot, 1.0))
            continue
        z = zs(x, y) + (ROAD_LIFT + .005 if kind in ("manhole",) else ROAD_LIFT if kind == "storm_inlet" else ROAD_LIFT + SIDEWALK_H)
        target = infra_pts if kind in INFRA_KINDS else prop_pts
        target.setdefault((macro, sub), []).append((x, y, z, props_index[PROP_FOR[kind]], rot, 1.0))
for (macro, sub), pts in infra_pts.items():
    name = f"OT_Infrastructure_{sub}"
    o = sa_bl.point_cloud_object(name, pts, props_lib, cell_collection("Infrastructure", macro))
    register("Infrastructure", name, sub, o, instances=len(pts))
for (macro, sub), pts in prop_pts.items():
    name = f"OT_Props_{sub}"
    o = sa_bl.point_cloud_object(name, pts, props_lib, cell_collection("Props", macro))
    register("Props", name, sub, o, instances=len(pts))
tree_objs = [props_objs["PROP_Tree_A"].copy(), props_objs["PROP_Tree_B"].copy()]
tree_objs[0].name, tree_objs[1].name = "VEG_Tree_A", "VEG_Tree_B"
for t_ in tree_objs:
    bpy.context.scene.collection.objects.link(t_)
tree_lib, tree_index = sa_bl.library_collection("OT_Lib_Vegetation", tree_objs, library)
for (macro, sub), pts in tree_pts.items():
    name = f"OT_Vegetation_{sub}"
    o = sa_bl.point_cloud_object(name, pts, tree_lib, cell_collection("Vegetation", macro))
    register("Vegetation", name, sub, o, instances=len(pts), blockout_vegetation=True)
for (macro, sub), pts in light_pts.items():
    me = bpy.data.meshes.new(f"OT_Lighting_{sub}")
    me.from_pydata([(p[0], p[1], p[2]) for p in pts], [], [])
    o = bpy.data.objects.new(f"OT_Lighting_{sub}", me)
    cell_collection("Lighting", macro).objects.link(o)
    register("Lighting", o.name, sub, o, light_kind="streetlight_led", lumens=12000, colour_k=4000, count=len(pts))
# Gameplay: lot anchors per subcell (future property/economy hooks).
lot_pts = {}
for lot in ot.lots:
    macro, sub = subcell(*lot["obb"].c)
    lot_pts.setdefault((macro, sub), []).append(lot)
for (macro, sub), lots in lot_pts.items():
    me = bpy.data.meshes.new(f"OT_Gameplay_Lots_{sub}")
    me.from_pydata([(l["obb"].c[0], l["obb"].c[1], zs(*l["obb"].c)) for l in lots], [], [])
    a = me.attributes.new("lot_index", "INT", "POINT")
    a.data.foreach_set("value", [int(l["id"][7:]) for l in lots])
    o = bpy.data.objects.new(f"OT_Gameplay_Lots_{sub}", me)
    cell_collection("Gameplay", macro).objects.link(o)
    register("Gameplay", o.name, sub, o, lots=len(lots))

# ---------------------------------------------------------------- lighting, render settings, cameras
sa_bl.sun_and_sky(scene, cams)
scene.render.engine = "BLENDER_EEVEE"
try:
    scene.eevee.use_shadows = True
    scene.eevee.shadow_ray_count = 2
    scene.eevee.use_raytracing = False
except AttributeError:
    pass
scene.render.film_transparent = False


def cam(name, loc, target=None, ortho=None, lens=35, rot=None):
    return sa_bl.camera(name, cams, loc, target=target, ortho=ortho, lens=lens, rot=rot, clip=(.5, 12000.0))


home = next(h for h in ot.data["heroes"] if h["id"] == "home.starter")
garage = next(h for h in ot.data["heroes"] if h["id"] == "garage")
hz = hero_z
cam("CAM_OT_Top", (-2525, -2050, 3000), rot=(0, 0, 0), ortho=1900)
cam("CAM_OT_Oblique", (-1650, -3350, 650), target=(-2500, -2000, 20), lens=32)
cam("CAM_OT_Home_Exterior", (-2855, -2257, hz["home.starter"] + 1.7), target=(-2860, -2279, hz["home.starter"] + 6.0), lens=20)
cam("CAM_OT_Home_Cutaway", (-2863.9, -2274.3, hz["home.starter"] + 3.0 + 16), rot=(0, 0, 0), ortho=11.0)
cam("CAM_OT_Garage_Exterior", (-2738, -2175, hz["garage"] + 5), target=(-2700, -2148, hz["garage"] + 3), lens=26)
cam("CAM_OT_Garage_Cutaway", (-2695, -2147, hz["garage"] + 40), rot=(0, 0, 0), ortho=40.0)
cam("CAM_OT_Horizonte", (-2326, -1861, hz["horizonte"] + 2.5), target=(-2352, -1802, hz["horizonte"] + 17), lens=18)
cam("CAM_OT_Horizonte_Frente", (-2338, -1849, hz["horizonte"] + 1.7), target=(-2352, -1812, hz["horizonte"] + 11), lens=16)
cam("CAM_OT_Imperial", (-2000, -2512, hz["imperial"] + 7), target=(-2052, -2615, hz["imperial"] + 11), lens=24)
cam("CAM_OT_Cells", (-2525, -2050, 3000), rot=(0, 0, 0), ortho=3100)
scene.camera = bpy.data.objects["CAM_OT_Oblique"]

scene["facility_world"] = "Santa Aurora"
scene["facility_area"] = "Cidade Antiga"
scene["facility_stage"] = "W1.5 base de produÃ§Ã£o (estrutura; nÃ£o Ã© arte final)"
out_dir = root / "ArtSource" / "Blender" / "World" / "OldTown"
blend = out_dir / "SantaAurora_CidadeAntiga_Base_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)

manifest_out = {
    "schemaVersion": 1,
    "stage": "W1.5",
    "convention": "SA_Mxx_yy (1 km) / SA_Mxx_yy_Sxx_yy (250 m); layers = " + ", ".join(LAYERS),
    "families": {v["id"]: {"family": v["family"], "w": v["w"], "d": v["d"], "floors": v["floors"], "height": v["height"], "roof": v["roof"],
                           "libraryIndex": fam_index["FAM_" + v["id"]]} for v in OLDTOWN_VARIANTS},
    "props": props_index,
    "subcells": manifest["subcells"],
    "heroes": manifest["heroes"],
    "lots": manifest["lots"],
}
(out_dir / "oldtown_streaming_manifest_v1.json").write_text(json.dumps(manifest_out, ensure_ascii=False) + "\n", encoding="utf-8")
counts = {c.name: len(c.all_objects) for c in top.children}
inst = sum(len(v) for v in arch_pts.values())
report = {
    "blend": blend.relative_to(root).as_posix(),
    "blenderVersion": bpy.app.version_string,
    "objectCount": len(bpy.data.objects),
    "collectionObjectCounts": counts,
    "subcells": len(manifest["subcells"]),
    "familyVariants": len(OLDTOWN_VARIANTS),
    "variantFaces": variant_stats,
    "buildingInstances": inst,
    "infrastructureInstances": sum(len(v) for v in infra_pts.values()),
    "propInstances": sum(len(v) for v in prop_pts.values()),
    "trees": sum(len(v) for v in tree_pts.values()),
    "streetLights": sum(len(v) for v in light_pts.values()),
    "kitPieces": sorted(kit),
    "props": sorted(props_objs),
    "materials": sorted(lib),
    "heroes": {k: {"ground_z": round(v, 2)} for k, v in hero_z.items()},
    "layout": ot.metrics,
    "w2": dict(STATS, accessoryInstances=sum(len(v) for v in acc_pts.values())),
    "status": "W2 production base (W1.5 structure + N1/N3/N4 refinements) - not final art",
}
(out_dir / "oldtown_generation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("OLD TOWN BASE GENERATED", json.dumps({k: report[k] for k in ("blend", "objectCount", "buildingInstances", "subcells")}))
