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
parser.add_argument("--slice", default="", help="W3 vertical slice: x0,y0,x1,y1 aligned to the 250 m grid (rebuilt in high fidelity)")
parser.add_argument("--context", type=float, default=900.0, help="W3: link base subcells up to this distance around the slice")
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
from sa_terrain import Terrain, hero_pads  # noqa: E402
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
SLICE = tuple(float(v) for v in opts.slice.split(",")) if opts.slice else None


def sub_bounds(sub):
    m, s_ = sub.split("_S")
    ix, iz = int(m[4:6]), int(m[7:9])
    sx, sz = int(s_[:2]), int(s_[3:5])
    x0 = -4000 + ix * 1000 + sx * 250
    y0 = -4000 + iz * 1000 + sz * 250
    return x0, y0, x0 + 250, y0 + 250


def in_slice_sub(sub):
    if not SLICE:
        return True
    x0, y0, x1, y1 = sub_bounds(sub)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return SLICE[0] <= cx <= SLICE[2] and SLICE[1] <= cy <= SLICE[3]


def in_slice_pt(p, pad=0.0):
    return not SLICE or (SLICE[0] - pad <= p[0] <= SLICE[2] + pad and SLICE[1] - pad <= p[1] <= SLICE[3] + pad)

terrain = Terrain(spec, pads=hero_pads(root, spec))   # W2.5: urban relief + flat hero pads
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
    top_z = sa_arch.building_mesh(mb, v, k, detail="lod0" if SLICE else "lod1")
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
STEP = 4.0 if SLICE else 8.0
x0, y0, x1, y1 = (SLICE[0] - 4, SLICE[1] - 4, SLICE[2] + 4, SLICE[3] + 4) if SLICE else BOUNDS
nx, ny = int((x1 - x0) // STEP), int((y1 - y0) // STEP)
H = [[terrain.ground(x0 + i * STEP, y0 + j * STEP) for j in range(ny + 1)] for i in range(nx + 1)]
buckets = {}
CHANNEL_CUT = 0
for i in range(nx):
    for j in range(ny):
        cx, cy = x0 + (i + .5) * STEP, y0 + (j + .5) * STEP
        if cy < -300 and terrain.valley_distance(cx, cy) < STEP * .75:
            CHANNEL_CUT += 1                                   # W2.5: open the ground under the córrego (roads cover the rest)
            continue
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
    o = mb.to_object(name, [sa_materials.build_terrain_material(lib)], cell_collection("Terrain", macro), uv_scale=4.0)
    register("Terrain", name, sub, o)

# ---------------------------------------------------------------- roads, sidewalks, curbs, markings
g = ot.graph
deg = g.degree()
inc = g.incident()
ROAD_MATS = ["asfalto", "asfalto_gasto", "calcada", "meio_fio", "sinalizacao_viaria", "grama", "concreto", "terra", "piso_intertravado",
             "pedra_portuguesa", "cimentado", "decal_pneu", "decal_oleo", "decal_sujeira", "pedra_reboco_historico", "agua_canal", "aco_pintado_cinza",
             "concreto_aparente"]
STATS = {"stairways": 0, "stair_steps": 0, "retaining_walls": 0, "podiums": 0, "tire_mark_segments": 0, "asphalt_patches": 0,
         "oil_stains": 0, "wire_spans": 0, "channel_m": 0.0, "sidewalk_materials": {}, "corners_filleted": 0, "curb_ramps": 0, "accessories": {}, "forecourt_planters": 0, "forecourt_bollards": 0}
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




import zlib as _zlib  # noqa: E402


def _h(*k):
    return _zlib.crc32(":".join(str(x) for x in k).encode()) / 4294967295.0


def sidewalk_mat(eid, side, mid, cls):
    """W2.5 (Part 5): sidewalks vary per frontage, like owners paving their own stretch."""
    r = _h("sw", eid, side)
    if ot.in_core(mid) and cls in ("main",) and r < .55:
        return RM["pedra_portuguesa"]
    if r < .45:
        return RM["calcada"]
    if r < .7:
        return RM["cimentado"]
    if r < .88:
        return RM["piso_intertravado"]
    return RM["pedra_portuguesa"]


def stairway(mb, a, b, width):
    """Urban stairway (escadaria) for steep passages/alleys: flights of real steps following the terrain, landings, handrails."""
    L = dist(a, b)
    u = norm(vsub(b, a))
    n = perp(u)
    za, zb = zs(*a) + ROAD_LIFT + SIDEWALK_H, zs(*b) + ROAD_LIFT + SIDEWALK_H
    if zb < za:
        a, b, za, zb, u = b, a, zb, za, (-u[0], -u[1])
        n = perp(u)
    rise = zb - za
    nsteps = max(2, int(rise / .17))
    run = L / nsteps
    ang = math.atan2(u[1], u[0])
    for k in range(nsteps):
        c = (a[0] + u[0] * (k + .5) * run, a[1] + u[1] * (k + .5) * run)
        z0 = min(zs(*c), za) - .4
        mb.box(c[0], c[1], z0, run + .02, width, za + (k + 1) * rise / nsteps - z0, RM["cimentado"] if k % 12 else RM["concreto"], rot=ang)
    for s_ in (1, -1):
        for k in range(0, nsteps, 4):
            t0, t1 = k * run, min(L, (k + 4) * run)
            p0 = (a[0] + u[0] * t0 + n[0] * s_ * (width / 2 - .1), a[1] + u[1] * t0 + n[1] * s_ * (width / 2 - .1))
            p1 = (a[0] + u[0] * t1 + n[0] * s_ * (width / 2 - .1), a[1] + u[1] * t1 + n[1] * s_ * (width / 2 - .1))
            z0 = za + k * rise / nsteps + .9
            z1 = za + min(nsteps, k + 4) * rise / nsteps + .9
            mb.box(p0[0], p0[1], za + (k + 1) * rise / nsteps, .05, .05, .9, RM["aco_pintado_cinza"])
            mid_ = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            mb.box(mid_[0], mid_[1], (z0 + z1) / 2 - .02, seg, .05, .05 + abs(z1 - z0), RM["aco_pintado_cinza"], rot=ang)
    STATS["stairways"] += 1
    STATS["stair_steps"] += nsteps


def corrego(mb, a, b, ta, tb):
    """Canalized stream (córrego) in the R02 median: concrete channel 2 m deep with parapets, water, railings; culverts under junctions."""
    L = dist(a, b)
    u = norm(vsub(b, a))
    if L - ta - tb < 2:
        return
    sa_ = (a[0] + u[0] * ta, a[1] + u[1] * ta)
    sb_ = (b[0] - u[0] * tb, b[1] - u[1] * tb)
    strip(mb, sa_, sb_, 0, 3.0, -2.0, RM["concreto_aparente"])                         # bed
    strip(mb, sa_, sb_, 0, 2.2, -1.55, RM["agua_canal"])                               # water
    n = perp(u)
    pts = resample([sa_, sb_], 4.0)
    for s_ in (1, -1):
        inner = [(p[0] + n[0] * s_ * 1.5, p[1] + n[1] * s_ * 1.5) for p in pts]
        outer = [(p[0] + n[0] * s_ * 1.8, p[1] + n[1] * s_ * 1.8) for p in pts]
        for i in range(len(pts) - 1):
            zi0, zi1 = zs(*inner[i]), zs(*inner[i + 1])
            q = [(inner[i][0], inner[i][1], zi0 - 2.0), (inner[i + 1][0], inner[i + 1][1], zi1 - 2.0),
                 (inner[i + 1][0], inner[i + 1][1], zi1 + .45), (inner[i][0], inner[i][1], zi0 + .45)]
            mb.add_face(q if s_ > 0 else q[::-1], RM["concreto_aparente"])
            zo0, zo1 = zs(*outer[i]), zs(*outer[i + 1])
            mb.quad((inner[i][0], inner[i][1], zi0 + .45), (inner[i + 1][0], inner[i + 1][1], zi1 + .45),
                    (outer[i + 1][0], outer[i + 1][1], zo1 + .45), (outer[i][0], outer[i][1], zo0 + .45), RM["concreto"])
            q2 = [(outer[i][0], outer[i][1], zo0 + ROAD_LIFT), (outer[i + 1][0], outer[i + 1][1], zo1 + ROAD_LIFT),
                  (outer[i + 1][0], outer[i + 1][1], zo1 + .45), (outer[i][0], outer[i][1], zo0 + .45)]
            mb.add_face(q2[::-1] if s_ > 0 else q2, RM["concreto"])
        strip(mb, sa_, sb_, s_ * 1.65, .05, 1.35, RM["aco_pintado_cinza"])               # handrail
        t = 0.0
        while t < L - ta - tb:
            c = (sa_[0] + u[0] * t + n[0] * s_ * 1.65, sa_[1] + u[1] * t + n[1] * s_ * 1.65)
            mb.box(c[0], c[1], zs(*c) + .45, .05, .05, .9, RM["aco_pintado_cinza"])
            t += 2.5
    STATS["channel_m"] += L - ta - tb


def road_decals(mb, eid, a, b, cls, cw, L):
    """W2.5 wear decals on asphalt: tire marks along the lanes, asphalt patches (remendos) and oil stains at stops."""
    if cls not in ("local", "main", "collector", "arterial", "industrial"):
        return
    u = norm(vsub(b, a))
    ang = math.atan2(u[1], u[0])
    if _h("tm", eid) < .55 and L > 30:
        for lane in ((-cw / 4, cw / 4) if cw >= 6 else (0.0,)):
            t0 = 4 + _h("tm0", eid, lane) * max(1, L - 30)
            seg = min(L - t0 - 2, 12 + _h("tm1", eid, lane) * 30)
            if seg < 5:
                continue
            for wheel in (-.85, .85):
                p0 = (a[0] + u[0] * t0, a[1] + u[1] * t0)
                p1 = (a[0] + u[0] * (t0 + seg), a[1] + u[1] * (t0 + seg))
                strip(mb, p0, p1, lane + wheel, .32, ROAD_LIFT + .008, RM["decal_pneu"])
            STATS["tire_mark_segments"] += 1
    for k in range(int(L / 45) + (1 if _h("pt", eid) < .4 else 0)):
        if _h("pp", eid, k) > .45:
            continue
        t = 3 + _h("pq", eid, k) * max(1, L - 6)
        c = (a[0] + u[0] * t + perp(u)[0] * (_h("pw", eid, k) - .5) * cw * .6, a[1] + u[1] * t + perp(u)[1] * (_h("pw", eid, k) - .5) * cw * .6)
        w, d = 1.2 + _h("px", eid, k) * 3.5, .8 + _h("py", eid, k) * 2.0
        mb.box(c[0], c[1], zs(*c) + ROAD_LIFT - .02, w, d, .035, RM["asfalto"] if _h("pc", eid, k) < .5 else RM["asfalto_gasto"],
               rot=ang + (_h("pr", eid, k) - .5) * .3)
        STATS["asphalt_patches"] += 1
    if _h("oil", eid) < .3:
        t = 2 + _h("ot", eid) * max(1, L - 4)
        off = (cw / 2 - 1.2) * (1 if _h("os", eid) < .5 else -1)
        c = (a[0] + u[0] * t + perp(u)[0] * off, a[1] + u[1] * t + perp(u)[1] * off)
        mb.box(c[0], c[1], zs(*c) + ROAD_LIFT + .006, 1.8, 1.2, .004, RM["decal_oleo"], rot=ang)
        STATS["oil_stains"] += 1

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
    grade = abs(zs(*b) - zs(*a)) / L
    if cls == "passage" or (cls == "alley" and grade > .055 and L < 120):
        if grade > .04:
            stairway(mb, a, b, STREET[cls]["total"] if cls == "passage" else 3.2)
        else:
            strip(mb, a, b, 0, STREET[cls]["total"], SIDEWALK_H + ROAD_LIFT, RM["calcada"])
        continue
    surf = RM["asfalto_gasto"] if cls in ("alley", "service", "local") else RM["asfalto"]
    channel = cls == "arterial" and e.get("road") == "R02" and mid[1] < -300
    if channel:
        half = (cw - 3.6) / 2
        for s_ in (1, -1):
            strip(mb, a, b, s_ * (1.8 + half / 2), half, ROAD_LIFT, surf)
    else:
        strip(mb, a, b, 0, cw, ROAD_LIFT, surf)
    road_decals(mb, eid, a, b, cls, cw, L)
    ta, tb = trim(e["a"]), trim(e["b"])
    if L - ta - tb > .5 and sw > 0:
        sa = (a[0] + u[0] * ta, a[1] + u[1] * ta)
        sb = (b[0] - u[0] * tb, b[1] - u[1] * tb)
        for s_ in (1, -1):
            sm = sidewalk_mat(eid, s_, mid, cls)
            STATS["sidewalk_materials"][ROAD_MATS[sm]] = STATS["sidewalk_materials"].get(ROAD_MATS[sm], 0) + 1
            strip(mb, sa, sb, s_ * (cw / 2 + sw / 2), sw, ROAD_LIFT + SIDEWALK_H, sm, curb=True, curb_side=s_)
    if cls == "arterial" and channel:
        corrego(mb, a, b, ta, tb)
        for s_ in (1, -1):
            strip(mb, a, b, s_ * 5.2, .12, ROAD_LIFT + .006, RM["sinalizacao_viaria"])
    elif cls == "arterial":
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
        if lot.get("green"):
            # W2.5 pracinha: grass, a crossing path of cimentado and a low curb around it
            zt = max(zs(*q) for q in o.corners()) + .04
            mb.obb_box(o.corners(), zc - .3, zt - zc + .3, RM["grama"])
            mb.obb_box(o.grown(.15).corners(), zc - .3, zt - zc + .38, RM["meio_fio"], top=False)
            ang = math.atan2(o.u[1], o.u[0])
            mb.box(o.c[0], o.c[1], zt + .005, o.hw * 2, 1.4, .02, RM["cimentado"], rot=ang)
            STATS["pocket_greens"] = STATS.get("pocket_greens", 0) + 1
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
# W2.5 street trees: square pits (terra + concrete rim) or short grass strips between trees on residential streets.
for (x, y, ang, linear) in ot.tree_pits:
    mb = rmb((x, y))
    z = zs(x, y) + ROAD_LIFT + SIDEWALK_H
    if linear:
        mb.box(x, y, z - .02, 3.2 + (abs(x * 7 + y * 3) % 2.5), .9, .035, RM["grama"], rot=ang)
    else:
        mb.box(x, y, z - .02, 1.2, 1.2, .03, RM["terra"], rot=ang)
        for dx, dy, sx, sy in ((0, .62, 1.36, .12), (0, -.62, 1.36, .12), (.62, 0, .12, 1.24), (-.62, 0, .12, 1.24)):
            cs_, sn_ = math.cos(ang), math.sin(ang)
            mb.box(x + dx * cs_ - dy * sn_, y + dx * sn_ + dy * cs_, z - .02, sx, sy, .07, RM["concreto"], rot=ang)
        if SLICE and in_slice_pt((x, y), 20):
            # W3.1: surface roots and soil spill, some pits with a broken curb ring (older trees lifting the paving)
            k_seed = int(abs(x) * 13 + abs(y) * 7)
            for k_ in range(3 + k_seed % 3):
                a_ = ang + k_ * 2.1 + (k_seed % 7) * .3
                L_ = .5 + ((k_seed >> k_) % 5) * .14
                cx_, cy_ = x + math.cos(a_) * (.25 + L_ / 2), y + math.sin(a_) * (.25 + L_ / 2)
                mb.box(cx_, cy_, z - .03, L_, .07 + (k_ % 2) * .03, .06, RM["terra"], rot=a_)
            mb.box(x + math.cos(ang + 1) * .2, y + math.sin(ang + 1) * .2, z + .003, 1.5, .5, .004, RM["terra"], rot=ang + .5)
STATS["tree_pits"] = len(ot.tree_pits)
for (macro, sub), mb in road_mb.items():
    name = f"OT_Roads_{sub}"
    o = mb.to_object(name, [lib[m] for m in ROAD_MATS], cell_collection("Roads", macro))
    register("Roads", name, sub, o)

# ---------------------------------------------------------------- architecture: family instances per subcell
LOT_Z = {}
slope_mb = {}
WALL_TOP_GREEN = []
SLOPE_SITES = []


def slope_works(lot, o, cz, zc):
    """Podium (exposed basement) where the ground falls more than the plinth covers; retaining wall where it rises behind."""
    lo, hi = min(cz), max(cz)
    key = subcell(*o.c)
    mb = slope_mb.setdefault(key, sa_bl.MeshBuilder())
    if zc - lo > 1.3:
        g_ = o.grown(.12)
        mb.obb_box(g_.corners(), lo - .4, zc - lo + .4 - .05, 0)
        STATS["podiums"] += 1
    if hi - zc > 1.2:
        # wall along the back edge of the lot (the edge farthest from the front point), from zc to the uphill ground
        cs_ = o.corners()
        f = lot.get("front", o.c)
        far = sorted(range(4), key=lambda i: -dist(cs_[i], f))[:2]
        p0, p1 = cs_[far[0]], cs_[far[1]]
        L_ = dist(p0, p1)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c = lerp(p0, p1, .5)
        top = max(zs(*p0), zs(*p1))
        mb.box(c[0], c[1], zc - .3, L_ + .3, .35, top - zc + .55, 1, rot=ang)
        mb.box(c[0], c[1], top + .25, L_ + .4, .45, .08, 2, rot=ang)
        STATS["retaining_walls"] += 1
        SLOPE_SITES.append((top - zc, c, ang, f))
        if (int(abs(c[0]) * 5 + abs(c[1]) * 3) % 10) < 4:
            back = norm(vsub(c, f))
            for k in range(1 + int(L_ // 6)):
                t_ = (k + .5) / (1 + int(L_ // 6)) - .5
                q = (c[0] + math.cos(ang) * t_ * L_ + back[0] * .9, c[1] + math.sin(ang) * t_ * L_ + back[1] * .9)
                WALL_TOP_GREEN.append((q[0], q[1], top + .2))


arch_pts = {}
for lot in ot.lots:
    if lot["family"] in ("vacant", "parking"):
        continue
    o = lot["obb"]
    cz = [zs(*q) for q in o.corners()]
    # W2.5: entrance at street level (front point), basement exposed downhill, retaining wall uphill.
    zc = zs(*lot["front"]) + ROAD_LIFT + .02 if lot.get("front") else min(cz)
    LOT_Z[lot["id"]] = zc
    slope_works(lot, o, cz, zc)
    macro, sub = subcell(*o.c)
    arch_pts.setdefault((macro, sub), []).append((o.c[0], o.c[1], zc, fam_index["FAM_" + lot["variant"]], lot["rot"], 1.0))
    manifest["lots"].append({"id": lot["id"], "variant": lot["variant"], "family": lot["family"], "x": round(o.c[0], 2), "y": round(o.c[1], 2),
                             "z": round(zc, 2), "rot": round(lot["rot"], 4), "subcell": sub, "neighbourhood": lot["hood"]})
for (macro, sub), pts in arch_pts.items():
    name = f"OT_Architecture_{sub}"
    o = sa_bl.point_cloud_object(name, pts, fam_lib, cell_collection("Architecture", macro))
    register("Architecture", name, sub, o, instances=len(pts))
for (macro, sub), mb in slope_mb.items():
    if not mb.faces:
        continue
    name = f"OT_SlopeWorks_{sub}"
    o = mb.to_object(name, [lib["pedra_reboco_historico"], lib["concreto_aparente"], lib["concreto_pintado"]], cell_collection("Architecture", macro))
    register("Architecture", name, sub, o, note="W2.5: embasamentos e muros de arrimo dos lotes em desnível")

# ---------------------------------------------------------------- W2 (N1): rule-based accessories breaking the repetition
# Small instanced pieces placed per lot from its variant (roof type, floors, tags) with a stable crc32 seed: roof water
# tanks, solar heaters, antennas, dishes, facade/back AC condensers, service-entrance boxes and downpipes.
import zlib  # noqa: E402

ACC_MATS = {"tank": ["plastico_azul", "plastico_branco"], "tank_fc": ["telha_fibrocimento", "concreto"], "solar": ["vidro", "aluminio"],
            "antenna": ["metal_galvanizado"], "dish": ["plastico_branco", "metal_galvanizado"], "ac": ["plastico_branco", "aco_pintado_cinza"],
            "meterbox": ["aco_pintado_cinza", "vidro"], "downpipe": ["plastico"],
            "wall6": ["reboco_pintado", "aco_pintado_cinza", "concreto_pintado"], "wall8": ["reboco_pintado", "aco_pintado_cinza", "concreto_pintado"],
            "wall10": ["reboco_pintado", "aco_pintado_cinza", "concreto_pintado"], "bin": ["plastico_azul", "borracha_preta"],
            "dumpster": ["aco_pintado_vermelho", "ferrugem"], "roofroom": ["reboco_antigo", "telha_fibrocimento", "aluminio"],
            "shrub": ["folhagem", "terra"], "rubble": ["concreto", "tijolo_aparente"], "tarp": ["plastico_azul", "madeira_crua"]}


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
    elif kind.startswith("wall"):
        w = float(kind[4:])
        gate = 3.0 if w >= 8 else 1.0
        x_g = w / 2 - gate / 2 - .3
        for xa, xb in ((-w / 2, x_g - gate / 2), (x_g + gate / 2, w / 2)):
            if xb - xa > .1:
                mb.box((xa + xb) / 2, 0, -.3, xb - xa, .18, 1.9, 0)
                mb.box((xa + xb) / 2, 0, 1.6, xb - xa + .04, .24, .06, 2)
        for k in range(int(gate / .12)):
            mb.box(x_g - gate / 2 + .06 + k * .12, 0, .05, .02, .02, 1.75, 1)
        mb.box(x_g, 0, 1.75, gate, .04, .05, 1)
    elif kind == "bin":
        mb.box(0, 0, 0, .58, .7, .95, 0)
        mb.box(0, 0, .95, .6, .74, .05, 0)
        mb.cylinder(0, .3, 0, .1, .05, 6, 1)
    elif kind == "dumpster":
        mb.prism([(-1.6, -.9), (1.6, -.9), (1.9, .9), (-1.9, .9)], .15, 1.2, 0)
        for x in (-1.2, 1.2):
            mb.box(x, 0, 0, .2, 1.6, .15, 1)
    elif kind == "roofroom":
        mb.box(0, 0, 0, 3.6, 3.0, 2.5, 0)
        mb.box(0, 0, 2.5, 4.0, 3.4, .06, 1)
        mb.box(1.0, -1.51, .9, .9, .02, 1.0, 2)
    elif kind == "shrub":
        mb.cylinder(0, 0, 0, .55, .9, 8, 0)
        mb.cylinder(0, 0, .9, .4, .4, 8, 0)
    elif kind == "rubble":
        for k, (x, y, s_) in enumerate(((-.6, -.2, .9), (.5, .3, .7), (0, .8, .5), (.9, -.6, .4))):
            mb.box(x, y, 0, s_ * 1.4, s_, s_ * .55, k % 2)
    elif kind == "tarp":
        for x in (-1.3, 1.3):
            for y in (-1.0, 1.0):
                mb.box(x, y, 0, .08, .08, 2.2 if y < 0 else 2.6, 1)
        mb.add_face([(-1.5, -1.1, 2.2), (1.5, -1.1, 2.2), (1.5, 1.1, 2.6), (-1.5, 1.1, 2.6)], 0)
    # Street-distance pieces: no bevel and few segments (heroes carry the LOD0 detail; these only break repetition).
    o = mb.to_object("ACC_" + kind, [lib[m] for m in ACC_MATS[kind]], library)
    sa_bl.props(o, sa_stage="W2 acessório (LOD0 base)")
    return o


if SLICE:
    ACC_MATS.update({"trashbag": ["borracha_preta"], "pallet": ["madeira_crua"], "cone": ["aco_pintado_vermelho", "plastico_branco"],
                     "plate": ["plastico_branco", "aco_pintado_vermelho", "metal_galvanizado"]})
    # W3.1 background variants (per lot, themed per ~60 m block): marquises, balconies, external stairs, rear annexes,
    # reformed ground-floor cladding, raised front parapets, steel car gates and rooftop condenser racks.
    W31 = {}
    for _w in (3, 5, 7, 9):
        for _c, _m in (("pastilha", "plastico_azul"), ("ceramica", "piso_ceramico_bege"), ("azulejo", "azulejo_branco"), ("granito", "granito"),
                       ("verde", "aco_pintado_verde"), ("tijolo", "tijolo_aparente")):
            W31[f"w31_reforma{_w}_{_c}"] = [_m, "concreto_pintado"]
    for _w in (5, 7, 9):
        W31[f"w31_platibanda{_w}"] = ["concreto_pintado", "concreto"]
    W31.update({"w31_marquise": ["concreto_pintado", "aco_pintado_cinza"], "w31_marquise_metal": ["telha_metalica", "aco_pintado_cinza"],
                "w31_sacada": ["concreto_pintado", "aco_pintado_cinza"], "w31_escada_ext": ["concreto", "aco_pintado_cinza"],
                "w31_anexo": ["concreto_pintado", "telha_fibrocimento", "aluminio", "vidro"], "w31_portao": ["aco_pintado_cinza", "aco_pintado_verde"],
                "w31_cond_rack": ["aco_pintado_cinza", "plastico_branco", "borracha_preta"], "w31_grade_janela": ["aco_pintado_cinza"]})
    ACC_MATS.update(W31)
    _base_acc_piece = acc_piece

    def _w31_piece(kind):
        mb = sa_bl.MeshBuilder()
        if kind.startswith("w31_reforma"):
            w_ = float(kind[11:].split("_")[0])
            mb.box(0, -.012, .02, w_, .024, 2.6, 0)                         # cladding over the ground floor
            mb.box(0, -.03, 2.62, w_ + .04, .06, .08, 1)                    # capping band
        elif kind.startswith("w31_platibanda"):
            w_ = float(kind[14:])
            mb.box(0, .1, 0, w_, .2, .95, 0)
            mb.box(0, .1, .95, w_ + .06, .28, .07, 1)
        elif kind == "w31_marquise":
            mb.box(0, -.55, 0, 2.6, 1.1, .12, 0)
            mb.box(0, -1.08, -.08, 2.6, .06, .2, 0)
            for x_ in (-1.1, 1.1):
                mb.add_face([(x_, -1.05, .12), (x_ + .02, -1.05, .12), (x_ + .02, -.02, .9), (x_, -.02, .9)], 1)
        elif kind == "w31_marquise_metal":
            mb.add_face([(-1.6, -1.2, 0), (1.6, -1.2, 0), (1.6, 0, .35), (-1.6, 0, .35)], 0)
            mb.add_face([(-1.6, 0, .35), (1.6, 0, .35), (1.6, -1.2, 0), (-1.6, -1.2, 0)], 0)
            for x_ in (-1.5, 0, 1.5):
                mb.box(x_, -.6, .0, .04, 1.2, .05, 1)
        elif kind == "w31_sacada":
            mb.box(0, -.45, 0, 2.4, .9, .12, 0)
            for k_ in range(13):
                x_ = -1.15 + k_ * 2.3 / 12
                mb.box(x_, -.88, .12, .025, .025, .95, 1)
            for x_ in (-1.18, 1.18):
                for k_ in range(5):
                    mb.box(x_, -.85 + k_ * .2, .12, .025, .025, .95, 1)
            mb.box(0, -.88, 1.06, 2.4, .05, .04, 1)
            for x_ in (-1.18, 1.18):
                mb.box(x_, -.45, 1.06, .05, .9, .04, 1)
        elif kind == "w31_escada_ext":
            n_ = 16
            for k_ in range(n_):                                             # straight flight along +x, rising to 2.9 m
                mb.box(-2.1 + k_ * .27, -.5, k_ * .18, .28, .9, .18 if k_ == 0 else .06, 0)
                mb.box(-2.1 + k_ * .27, -.5, max(0, k_ * .18 - .25), .28, .9, .25 if k_ else .0, 0)
            mb.box(2.35, -.6, 2.82, 1.1, 1.1, .12, 0)                        # landing at the upper door
            mb.box(2.35, -1.1, 0, .12, .12, 2.82, 1)
            for k_ in range(0, n_, 3):
                mb.box(-2.1 + k_ * .27, -.94, k_ * .18 + .06, .03, .03, .95, 1)
            mb.add_face([(-2.1, -.95, 1.0), (2.2, -.95, 1.0 + 2.88), (2.2, -.93, 1.0 + 2.88), (-2.1, -.93, 1.0)], 1)
            mb.add_face([(-2.1, -.93, 1.0), (2.2, -.93, 3.88), (2.2, -.95, 3.88), (-2.1, -.95, 1.0)], 1)
        elif kind == "w31_anexo":
            mb.box(0, 1.3, 0, 3.2, 2.6, 2.6, 0)
            mb.add_face([(-1.75, -.05, 2.95), (1.75, -.05, 2.95), (1.75, 2.75, 2.6), (-1.75, 2.75, 2.6)], 1)
            mb.add_face([(-1.75, 2.75, 2.6), (1.75, 2.75, 2.6), (1.75, -.05, 2.95), (-1.75, -.05, 2.95)], 1)
            mb.box(.6, 2.61, 1.2, 1.0, .03, .8, 2)
            mb.box(.6, 2.625, 1.25, .9, .02, .7, 3)
            mb.box(-.8, 2.61, .0, .8, .03, 2.1, 2)
        elif kind == "w31_portao":
            mb.box(0, 0, 0, 3.2, .06, .06, 0)
            mb.box(0, 0, 1.9, 3.2, .06, .06, 0)
            for x_ in (-1.6, 1.6):
                mb.box(x_, 0, 0, .06, .06, 1.96, 0)
            for k_ in range(24):
                mb.box(-1.5 + k_ * 3.0 / 23, 0, .06, .02, .02, 1.84, 0)
            mb.box(0, -.01, .1, 3.1, .02, .5, 1)                             # lower sheet panel
        elif kind == "w31_cond_rack":
            mb.box(0, 0, 0, 2.6, .7, .08, 0)
            for x_ in (-.85, 0, .85):
                mb.box(x_, 0, .08, .78, .32, .55, 1)
                mb.cylinder(x_ + .12, -.17, .32, .17, .01, 16, 2)
            for x_ in (-1.25, 1.25):
                mb.box(x_, 0, -.45, .05, .6, .45, 0)
        elif kind == "w31_grade_janela":
            mb.box(0, 0, 0, 1.3, .03, .03, 0)
            mb.box(0, 0, 1.15, 1.3, .03, .03, 0)
            for k_ in range(9):
                mb.box(-.6 + k_ * 1.2 / 8, 0, 0, .018, .018, 1.18, 0)
            for x_ in (-.66, .66):
                mb.box(x_, 0, 0, .03, .03, 1.18, 0)
        o_ = sa_bl.bevelled_object("ACC_" + kind, mb, [lib[m] for m in ACC_MATS[kind]], library, bevel=.004)
        sa_bl.props(o_, sa_stage="W3.1 variante de fundo (LOD0)")
        return o_

    def acc_piece(kind):  # noqa: F811
        if kind.startswith("w31_"):
            return _w31_piece(kind)
        if kind not in ("trashbag", "pallet", "cone", "plate"):
            return _base_acc_piece(kind)
        mb = sa_bl.MeshBuilder()
        if kind == "trashbag":
            import bmesh as _bm2
            from mathutils import Matrix as _M2
            for k_, (x_, y_, r_) in enumerate(((0, 0, .28), (.38, .1, .24), (.15, .36, .22))):
                bm_ = _bm2.new()
                _bm2.ops.create_icosphere(bm_, subdivisions=2, radius=r_, matrix=_M2.Translation((x_, y_, r_ * .8)) @ _M2.Diagonal((1, 1, .8, 1)))
                base_ = len(mb.verts)
                mb.verts.extend(tuple(v.co) for v in bm_.verts)
                for f_ in bm_.faces:
                    mb.faces.append(tuple(base_ + v.index for v in f_.verts))
                    mb.mats.append(0)
                bm_.free()
        elif kind == "pallet":
            for k_ in range(3):
                for y_ in (-.5, 0, .5):
                    mb.box(0, y_, k_ * .15, 1.2, .1, .09, 0)
                for x_ in (-.5, 0, .5):
                    mb.box(x_, 0, k_ * .15 + .09, .1, 1.0, .02, 0)
        elif kind == "cone":
            mb.box(0, 0, 0, .4, .4, .03, 0)
            mb.cylinder(0, 0, .03, .14, .6, 12, 0)
            mb.cylinder(0, 0, .3, .12, .1, 12, 1)
        else:  # no-parking plate on a post at a garage door (generic, no text)
            mb.cylinder(0, 0, 0, .03, 2.2, 8, 2)
            mb.cylinder(0, -.03, 1.9, .25, .02, 20, 1)
            mb.cylinder(0, -.05, 1.9, .2, .02, 20, 0)
        o_ = sa_bl.bevelled_object("ACC_" + kind, mb, [lib[m] for m in ACC_MATS[kind]], library, bevel=.004)
        sa_bl.props(o_, sa_stage="W3 clutter (LOD0)")
        return o_
    # posters: board + fictitious text, four variants
    from sa_w2 import text_mesh as _tm  # noqa: E402
    for k_, txt in enumerate(("ALUGA-SE", "VENDE-SE", "FESTA NA PRACA", "CONSERTOS")):
        mb = sa_bl.MeshBuilder()
        mb.box(0, -.01, 1.5, 1.0, .02, .7, 0)
        brd = sa_bl.bevelled_object(f"ACC_poster{k_}", mb, [lib["papelao"] if k_ % 2 else lib["plastico_branco"]], library, bevel=.003)
        t_ = _tm(f"ACC_poster{k_}_txt", txt, .13, library, lib["aco_pintado_vermelho"] if k_ % 2 == 0 else lib["borracha_preta"], extrude=.002)
        t_.location = (0, -.022, 1.8)
        t_.rotation_euler = (math.pi / 2, 0, 0)
        bpy.context.view_layer.update()
        t_.data.transform(t_.matrix_basis)
        t_.matrix_basis.identity()
        # join text into the board mesh
        _me = brd.data
        _tme = t_.data
        _nv = len(_me.vertices)
        _verts = [tuple(v.co) for v in _me.vertices] + [tuple(v.co) for v in _tme.vertices]
        _faces = [tuple(p_.vertices) for p_ in _me.polygons] + [tuple(i + _nv for i in p_.vertices) for p_ in _tme.polygons]
        _mi = [p_.material_index for p_ in _me.polygons] + [1] * len(_tme.polygons)
        _new = bpy.data.meshes.new(brd.name)
        _new.from_pydata(_verts, [], _faces)
        for m_ in list(_me.materials) + list(_tme.materials):
            _new.materials.append(m_)
        _new.polygons.foreach_set("material_index", _mi)
        sa_bl.write_box_uvs(_new)
        brd.data = _new
        bpy.data.objects.remove(t_)
        ACC_MATS[f"poster{k_}"] = None
        globals().setdefault("_POSTERS", []).append(brd)
if SLICE:
    import sa_decals  # noqa: E402
    DECAL_META = sa_decals.load(root)
    for _did, _m in DECAL_META.items():
        globals().setdefault("_POSTERS", []).append(sa_decals.piece(root, _did, _m, library, flat=False))
        if _m["kind"] == "mark":
            globals().setdefault("_POSTERS", []).append(sa_decals.piece(root, _did, _m, library, flat=True))
    from oldtown_layout import NEIGHBOURHOODS as _NB  # noqa: E402
    HOOD_CHAR = {h_["id"]: h_["character"] for h_ in _NB}
    DC = {k: [d for d, m in DECAL_META.items() if m["kind"] == k] for k in ("poster", "graffiti", "sign", "mark", "label", "scraps", "peeling")}
acc_objs = [acc_piece(k) for k in ACC_MATS if ACC_MATS[k] is not None] + list(globals().get("_POSTERS", []))
acc_lib, acc_index = sa_bl.library_collection("OT_Lib_Accessories", acc_objs, library)
VAR = {v["id"]: v for v in OLDTOWN_VARIANTS}
acc_pts = {}
LOT_ACC = {}


def place(lot, kind, lx, ly, lz, rot_extra=0.0, scl=1.0):
    o = lot["obb"]
    r = lot["rot"]
    cs, sn = math.cos(r), math.sin(r)
    x, y = o.c[0] + lx * cs - ly * sn, o.c[1] + lx * sn + ly * cs
    macro, sub = subcell(x, y)
    acc_pts.setdefault((macro, sub), []).append((x, y, lot_z[lot["id"]] + lz, acc_index["ACC_" + kind], r + rot_extra, scl))
    STATS["accessories"][kind] = STATS["accessories"].get(kind, 0) + 1
    LOT_ACC.setdefault(lot["id"], []).append(kind)


lot_z = {}
for lot in ot.lots:
    if lot["family"] in ("vacant", "parking") or lot["variant"] not in VAR:
        continue
    o = lot["obb"]
    lot_z[lot["id"]] = LOT_Z.get(lot["id"], min(zs(*q) for q in o.corners()))
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
    # W2.5 (Part 5): neighbourhood life
    sb = v.get("setback", 0.0)
    lotw = lot["obb"].hw * 2
    if v["family"] in ("casa_terrea", "sobrado_estreito", "abandonada_reformada") and sb >= 1.5 and roll(19) < .8:
        wk = "wall10" if lotw >= 10.2 else "wall8" if lotw >= 8.2 else "wall6"
        place(lot, wk, 0.0, -d / 2 - sb + .1, 0.0)
        if roll(20) < .55:
            place(lot, "shrub", (roll(21) - .5) * (w - 2), -d / 2 - sb / 2, 0.0, scl=.7 + roll(22) * .5)
    if resid and roll(23) < .35:
        place(lot, "bin", w / 2 - .5 - roll(24) * 1.5, -d / 2 - sb - .25, 0.0, rot_extra=(roll(25) - .5) * .5)
    if v["family"] in ("oficina", "armazem", "deposito") and roll(26) < .3:
        place(lot, "dumpster", -w / 2 + 2.2, -d / 2 - sb - .9, 0.0, rot_extra=(roll(27) - .5) * .3)
    if flat and resid and roll(28) < .12 and w >= 6:
        place(lot, "roofroom", (roll(29) - .5) * (w - 4), d / 2 - 2.2, H + .05)
    if flat and roll(30) < .06 and w >= 5:
        place(lot, "tarp", (roll(31) - .5) * (w - 3.4), (roll(32) - .5) * (d - 3), H + .05)
if SLICE:
    for lot in ot.lots:
        if lot["family"] in ("vacant", "parking") or lot["variant"] not in VAR or not in_slice_pt(lot["obb"].c):
            continue
        v = VAR[lot["variant"]]
        w, d = v["w"], v["d"]
        sb = v.get("setback", 0.0)
        lid = str(lot["id"])
        roll = lambda k, lid=lid: zlib.crc32(f"c{lid}:{k}".encode()) / 4294967295.0
        commerce = v["family"] in ("comercio_residencia", "pequeno_comercial") or "shop" in v["tags"]
        resid_ = v["family"] in ("sobrado_estreito", "casa_terrea", "comercio_residencia", "predio_3pav", "predio_4a6")
        H = v["height"]
        lotw_ = lot["obb"].hw * 2
        if (commerce or v["family"] == "abandonada_reformada") and roll(0) < .2:
            place(lot, f"poster{int(roll(1) * 4) % 4}", (roll(2) - .5) * (w - 1.2), -d / 2 - .01, 0.0)
        if (commerce or roll(3) < .15) and roll(4) < .5:
            for k in range(1 + int(roll(5) * 2)):
                place(lot, "trashbag", w / 2 - .6 - k * .7, -d / 2 - sb - .45, 0.0, rot_extra=roll(6 + k) * 6)
        if v["family"] in ("armazem", "deposito", "oficina") and roll(9) < .45:
            place(lot, "pallet", -w / 2 + 1.0 + roll(10) * 2, -d / 2 - sb - .7, 0.0, rot_extra=(roll(11) - .5) * .4)
        if "big_door" in v["tags"] and roll(12) < .5:
            place(lot, "plate", w / 2 - .3, -d / 2 - sb - .3, 0.0)
        # W3.1 background variants, themed per ~60 m block so neighbouring lots share a period of reforms
        bx_, by_ = int(lot["obb"].c[0] // 60), int(lot["obb"].c[1] // 60)
        theme = zlib.crc32(f"blk{bx_}:{by_}".encode()) % 6
        clad = ("pastilha", "ceramica", "azulejo", "granito", "verde", "tijolo")[theme]
        wcls = max([c_ for c_ in (3, 5, 7, 9) if c_ <= w - .4] or [0])
        gh_ = v["ground_h"]
        if wcls and v["family"] not in ("armazem", "deposito", "oficina") and roll(80) < (.45 if theme in (0, 1, 2) else .22):
            ck = clad if roll(81) < .75 else ("pastilha", "ceramica", "azulejo", "granito", "verde", "tijolo")[int(roll(82) * 6) % 6]
            place(lot, f"w31_reforma{wcls}_{ck}", 0.0, -d / 2 - .002, 0.0, scl=min(1.0, (gh_ - .25) / 2.7) if gh_ < 2.95 else 1.0)
        if (commerce or resid_) and gh_ >= 2.9 and roll(83) < .35:
            place(lot, "w31_marquise" if roll(84) < .6 else "w31_marquise_metal", (roll(85) - .5) * max(0, w - 3.4), -d / 2, gh_ - .35)
        if resid_ and v["floors"] >= 2 and w >= 4.5 and roll(86) < .4:
            for f_ in range(1, min(v["floors"], 4)):
                if roll(87 + f_) < .7:
                    place(lot, "w31_sacada", (roll(91) - .5) * max(0, w - 2.8), -d / 2, gh_ + (f_ - 1) * v["fh"] - .02)
        if v["family"] in ("sobrado_estreito", "casa_terrea", "comercio_residencia") and v["floors"] >= 2 and sb >= 1.3 and w >= 6 and roll(95) < .5:
            place(lot, "w31_escada_ext", 0.0, -d / 2 - .02, 0.0)
        if resid_ and lot["obb"].hd * 2 - d > 3.2 and roll(96) < .45 and w >= 4:
            place(lot, "w31_anexo", (roll(97) - .5) * max(0, w - 3.6), d / 2, 0.0)
        if v["roof"] == "flat_parapet" and wcls >= 5 and roll(98) < .35:
            place(lot, f"w31_platibanda{min(wcls, 9)}", 0.0, -d / 2, H)
        if v["family"] in ("casa_terrea", "sobrado_estreito", "abandonada_reformada") and sb >= 1.5 and lotw_ >= 6.2 and roll(99) < .4:
            place(lot, "w31_portao", (lotw_ / 2 - 1.9) * (1 if roll(100) < .5 else -1), -d / 2 - sb + .02, 0.0)
        if (commerce or v["family"] in ("predio_3pav", "predio_4a6", "pequeno_comercial")) and v["roof"] == "flat_parapet" and roll(101) < .4:
            place(lot, "w31_cond_rack", (roll(102) - .5) * max(0, w - 3.2), (roll(103) - .2) * (d - 2) * .4, H + .5)
        if resid_ and roll(104) < .35:
            for k in range(1 + int(roll(105) * 2)):
                place(lot, "w31_grade_janela", (roll(106 + k) - .5) * max(0, w - 1.6), -d / 2 - .04, .95)
        # W3.1 authored decals: shop signs, lambe-lambe clusters, glue scraps, graffiti, labels, house numbers, peeling paint
        fz = -d / 2
        old_fabric = v["family"] in ("abandonada_reformada", "armazem", "deposito", "oficina") or HOOD_CHAR.get(lot.get("hood"), "").startswith("core")
        if commerce and v["ground_h"] >= 3.0 and roll(40) < .7:
            place(lot, "dc_" + DC["sign"][int(roll(41) * 997) % len(DC["sign"])], (roll(42) - .5) * max(0, w - 3.0), fz - .025, v["ground_h"] - .72)
        if (commerce or v["family"] in ("abandonada_reformada", "armazem", "deposito")) and roll(43) < .55:
            n_ = 1 + int(roll(44) * 3)
            x_ = (w / 2 - .8) * (1 if roll(45) < .5 else -1)
            for k in range(n_):
                place(lot, "dc_" + DC["poster"][int(roll(46 + k) * 997) % len(DC["poster"])], x_ - (k * .62) * (1 if x_ > 0 else -1),
                      fz - .018 - k * .002, 1.25 + (roll(50 + k) - .5) * .25)
            if roll(54) < .6:
                place(lot, "dc_restos_cartaz", x_ - n_ * .62 * (1 if x_ > 0 else -1), fz - .016, 1.0 + roll(55) * .4)
        if v["family"] in ("abandonada_reformada", "armazem", "deposito", "oficina") and roll(56) < .6:
            place(lot, "dc_" + DC["graffiti"][int(roll(57) * 997) % len(DC["graffiti"])], (roll(58) - .5) * max(0, w - 2.4), fz - .022, .25 + roll(59) * .3)
        elif roll(60) < .14:
            place(lot, "dc_grafite_tags", (roll(61) - .5) * max(0, w - 1.8), fz - .022, .4 + roll(62) * .5)
        if (old_fabric or roll(63) < .25) and roll(64) < .6:
            for k in range(1 + int(roll(65) * 2)):
                place(lot, "dc_tinta_descascando", (roll(66 + k) - .5) * max(0, w - 1.2), fz - .012, .3 + roll(68 + k) * (min(H, 6) - 1.4))
        if resid_ and roll(70) < .45:
            place(lot, "dc_etiqueta_numero", (w / 2 - .45) * (1 if roll(71) < .5 else -1), fz - .014, 2.05)
        if roll(72) < .12:
            place(lot, "dc_etiqueta_perigo", (w / 2 - .5) * (1 if roll(73) < .5 else -1), fz - .014, 1.3)
        if "big_door" in v["tags"] and roll(74) < .45:
            place(lot, "dc_estencil_nao_estacione", 0.0, fz - .02, 2.45 if v["ground_h"] >= 3.2 else .9)
    cone_sites = 0
    for (x, y, rot) in ot.points.get("manhole", []):
        if in_slice_pt((x, y)) and (int(abs(x) * 7 + abs(y) * 3) % 9) == 0:
            cone_sites += 1
            for k in range(3):
                q = (x + math.cos(k * 2.1) * 1.1, y + math.sin(k * 2.1) * 1.1)
                macro, sub = subcell(*q)
                acc_pts.setdefault((macro, sub), []).append((q[0], q[1], zs(*q) + ROAD_LIFT, acc_index["ACC_cone"], rot + k, 1.0))
    STATS["w3_cone_sites"] = cone_sites
    marks = 0
    for (x, y, rot) in ot.points.get("manhole", []):
        if in_slice_pt((x, y)) and (int(abs(x) * 5 + abs(y) * 11) % 4) == 0:
            mk = ("marca_agua", "marca_rn", "marca_vala")[int(abs(x) * 3 + abs(y)) % 3]
            q = (x + math.cos(rot) * 1.0, y + math.sin(rot) * 1.0)
            macro, sub = subcell(*q)
            acc_pts.setdefault((macro, sub), []).append((q[0], q[1], zs(*q) + ROAD_LIFT + .012, acc_index["ACC_dcf_" + mk], rot, 1.0))
            marks += 1
    STATS["w31_spray_marks"] = marks
for lot in ot.lots:                                                                     # small urban voids
    if lot["family"] != "vacant" or lot.get("green"):
        continue
    o = lot["obb"]
    lot_z[lot["id"]] = min(zs(*q) for q in o.corners()) + .02
    lid = str(lot["id"])
    roll = lambda k, lid=lid: zlib.crc32(f"v{lid}:{k}".encode()) / 4294967295.0
    for k in range(1 + int(roll(0) * 3)):
        place(lot, "shrub", (roll(1 + k) - .5) * o.hw * 1.6, (roll(5 + k) - .5) * o.hd * 1.6, 0.0, scl=.6 + roll(9 + k) * .8)
    if roll(14) < .5:
        place(lot, "rubble", (roll(15) - .5) * o.hw, (roll(16) - .5) * o.hd, 0.0, rot_extra=roll(17) * 3)
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
W2_HEROES = {"home.starter": "W2_home_starter.blend", "garage": "W2_garage.blend", "horizonte": "W2_horizonte.blend", "imperial": "W2_imperial.blend",
             "apartments": "W2_apartments.blend", "grocery": "W2_grocery.blend", "restaurant": "W2_restaurant.blend", "workshop": "W2_workshop.blend",
             "smalloffice": "W2_smalloffice.blend"}
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
TREE_QUEUE = []
W31_TREES = {"gate_clear": 0, "pruned": 0}
if SLICE:
    _gates = [l_["front"] for l_ in ot.lots if l_.get("front") and l_["variant"] in VAR and
              ("big_door" in VAR[l_["variant"]]["tags"] or VAR[l_["variant"]]["family"] in ("oficina", "armazem", "deposito"))]
    for h_ in ot.data["heroes"]:                             # hero frontage centre (front = N/S/E/W side of the lot)
        x0_, y0_, x1_, y1_ = h_["lot"]
        _gates.append({"N": ((x0_ + x1_) / 2, y1_), "S": ((x0_ + x1_) / 2, y0_), "E": (x1_, (y0_ + y1_) / 2),
                       "W": (x0_, (y0_ + y1_) / 2)}.get(str(h_.get("front", "S"))[:1], ((x0_ + x1_) / 2, y0_)))
    _pl = [(x_, y_, r_) for k_ in ("pole", "pole_transformer") for (x_, y_, r_) in ot.points.get(k_, [])]
    _pg = {}
    for (x_, y_, r_) in _pl:
        _pg.setdefault((int(x_ // 40), int(y_ // 40)), []).append((x_, y_, r_))
for (x, y, rot, sp, scl) in ot.street_trees:
    if SLICE and in_slice_pt((x, y), 40):
        if any(dist((x, y), g_) < 3.2 for g_ in _gates):
            W31_TREES["gate_clear"] += 1                   # W3.1: keep garage/vehicle gates clear
            continue
        near_ = [q for gx in (-1, 0, 1) for gy in (-1, 0, 1) for q in _pg.get((int(x // 40) + gx, int(y // 40) + gy), [])]
        for (px_, py_, pr_) in near_:
            ux_, uy_ = math.cos(pr_), math.sin(pr_)
            along_ = (x - px_) * ux_ + (y - py_) * uy_
            lat_ = abs(-(x - px_) * uy_ + (y - py_) * ux_)
            if abs(along_) < 40 and lat_ < 1.8 and sp != "jovem":
                scl = min(scl, .74)                        # crown pruned under the overhead wires (W3.1)
                W31_TREES["pruned"] += 1
                break
    TREE_QUEUE.append((x, y, zs(x, y) + ROAD_LIFT + SIDEWALK_H - .02, sp, rot, scl))
for (x, y, z) in WALL_TOP_GREEN:
    TREE_QUEUE.append((x, y, z, "arbusto", (x * 13.1) % 6.28, .7 + (abs(x * 7 + y) % 5) * .1))
tree_lib, tree_index = None, None
for kind, pts in ot.points.items():
    for (x, y, rot) in pts:
        macro, sub = subcell(x, y)
        if kind == "tree":
            # plaza and back-yard trees (W1.5 points): species chosen by context, scale varied
            r_ = (int(abs(x) * 7 + abs(y) * 3) % 100) / 100.0
            sp = ("palmeira" if r_ < .12 else "sibipiruna" if r_ < .45 else "oiti") if ot.in_core((x, y)) else ("mangueira" if r_ < .4 else "oiti" if r_ < .75 else "ipe")
            TREE_QUEUE.append((x, y, zs(x, y) + ROAD_LIFT + SIDEWALK_H, sp, rot, .8 + (int(abs(x) * 13 + abs(y) * 7) % 7) * .06))
            continue
        if kind == "streetlight_head":
            light_pts.setdefault((macro, sub), []).append((x, y, zs(x, y) + 7.5, 0, rot, 1.0))
            continue
        if y < -300 and kind in ("manhole", "storm_inlet") and terrain.valley_distance(x, y) < 2.2:
            continue                                           # W2.5: no manholes floating over the open channel
        z = zs(x, y) + (ROAD_LIFT + .005 if kind in ("manhole",) else ROAD_LIFT if kind == "storm_inlet" else ROAD_LIFT + SIDEWALK_H)
        target = infra_pts if kind in INFRA_KINDS else prop_pts
        target.setdefault((macro, sub), []).append((x, y, z, props_index[PROP_FOR[kind]], rot, 1.0))
# W2.5 (Part 5): overhead power + telecom wiring between neighbouring poles (sagging spans, triangular section, light).
_poles = [(x, y, r) for k_ in ("pole", "pole_transformer") for (x, y, r) in ot.points.get(k_, [])]
_grid = {}
for i_, (x, y, r) in enumerate(_poles):
    _grid.setdefault((int(x // 50), int(y // 50)), []).append(i_)
wire_mb = {}
_done = set()
for i_, (x, y, r) in enumerate(_poles):
    ux, uy = math.cos(r), math.sin(r)
    cand = []
    for gx in range(int(x // 50) - 1, int(x // 50) + 2):
        for gy in range(int(y // 50) - 1, int(y // 50) + 2):
            for j_ in _grid.get((gx, gy), []):
                if j_ == i_:
                    continue
                X, Y, _ = _poles[j_]
                d_ = math.hypot(X - x, Y - y)
                if 12 < d_ < 46 and abs(((X - x) * ux + (Y - y) * uy) / d_) > .92:
                    cand.append((d_, j_, 1 if (X - x) * ux + (Y - y) * uy > 0 else -1))
    for sgn in (1, -1):
        best = min((c for c in cand if c[2] == sgn), default=None)
        if not best or (min(i_, best[1]), max(i_, best[1])) in _done:
            continue
        _done.add((min(i_, best[1]), max(i_, best[1])))
        X, Y, _ = _poles[best[1]]
        za_, zb_ = zs(x, y) + ROAD_LIFT + SIDEWALK_H, zs(X, Y) + ROAD_LIFT + SIDEWALK_H
        mb = wire_mb.setdefault(subcell((x + X) / 2, (y + Y) / 2), sa_bl.MeshBuilder())
        dx, dy = (X - x) / best[0], (Y - y) / best[0]
        nx_, ny_ = -dy, dx
        for off, hz_, sag, rad in ((-.55, 8.6, .9, .018), (.55, 8.6, .9, .018), (0.0, 6.3, .6, .03)):
            prev = None
            for k in range(7):
                t = k / 6
                px, py = x + (X - x) * t + nx_ * off, y + (Y - y) * t + ny_ * off
                pz = za_ + (zb_ - za_) * t + hz_ - sag * 4 * t * (1 - t)
                if prev:
                    ax_, ay_, az_ = prev
                    for (o1, o2) in (((0, rad), (rad, -rad)), ((rad, -rad), (-rad, -rad)), ((-rad, -rad), (0, rad))):
                        mb.quad((ax_ + nx_ * o1[0], ay_ + ny_ * o1[0], az_ + o1[1]), (px + nx_ * o1[0], py + ny_ * o1[0], pz + o1[1]),
                                (px + nx_ * o2[0], py + ny_ * o2[0], pz + o2[1]), (ax_ + nx_ * o2[0], ay_ + ny_ * o2[0], az_ + o2[1]), 0)
                prev = (px, py, pz)
        STATS["wire_spans"] += 1
for (macro, sub), mb in wire_mb.items():
    name = f"OT_Infrastructure_Wires_{sub}"
    o = mb.to_object(name, [lib["borracha_preta"]], cell_collection("Infrastructure", macro))
    register("Infrastructure", name, sub, o, note="W2.5: fiação aérea (energia + telecom)")
for (macro, sub), pts in infra_pts.items():
    name = f"OT_Infrastructure_{sub}"
    o = sa_bl.point_cloud_object(name, pts, props_lib, cell_collection("Infrastructure", macro))
    register("Infrastructure", name, sub, o, instances=len(pts))
for (macro, sub), pts in prop_pts.items():
    name = f"OT_Props_{sub}"
    o = sa_bl.point_cloud_object(name, pts, props_lib, cell_collection("Props", macro))
    register("Props", name, sub, o, instances=len(pts))
# W2.5 species-like proxies (better silhouettes than the W1.5 sphere clusters; still provisional, final vegetation with LOD later).
import bmesh as _bm  # noqa: E402
from mathutils import Matrix as _Mx, Vector as _Vx  # noqa: E402

for nm_, c1_, c2_ in (("folhagem_oiti", (.10, .22, .07), (.06, .15, .05)), ("folhagem_clara", (.30, .40, .13), (.20, .30, .09)),
                      ("folhagem_manga", (.07, .16, .06), (.04, .10, .04)), ("flores_ipe_amarelo", (.78, .62, .10), (.60, .45, .06)),
                      ("flores_ipe_rosa", (.70, .34, .52), (.52, .22, .38)), ("folhagem_palmeira", (.18, .30, .10), (.12, .22, .07))):
    lib[nm_] = sa_materials.build_material(nm_, dict(sa_materials.LIB["folhagem"], c1=c1_, c2=c2_))


def _crown(mb, centre, radius, blobs, flat, mat, seed, subdiv=1):
    import random as _rr
    rr = _rr.Random(seed)
    for k in range(int(blobs * 1.8)):
        bm = _bm.new()
        rad = radius * rr.uniform(.36, .58)
        off = (rr.uniform(-radius * .62, radius * .62), rr.uniform(-radius * .62, radius * .62), rr.uniform(-radius * .3, radius * .35) * flat)
        _bm.ops.create_icosphere(bm, subdivisions=subdiv, radius=rad, matrix=_Mx.Translation(_Vx(centre) + _Vx(off)) @ _Mx.Diagonal((1, 1, flat, 1)))
        for v in bm.verts:
            v.co += _Vx((rr.uniform(-.18, .18), rr.uniform(-.18, .18), rr.uniform(-.14, .14))) * rad
        base = len(mb.verts)
        mb.verts.extend(tuple(v.co) for v in bm.verts)
        for f in bm.faces:
            mb.faces.append(tuple(base + v.index for v in f.verts))
            mb.mats.append(mat)
        bm.free()


def _trunk(mb, h, r0, r1, lean=(0, 0), mat=0, segs=6):
    for k in range(4):
        z0, z1 = h * k / 4, h * (k + 1) / 4
        r = r0 + (r1 - r0) * (k + .5) / 4
        mb.cylinder(lean[0] * z0, lean[1] * z0, z0, r, z1 - z0, segs, mat)


def species(name):
    mb = sa_bl.MeshBuilder()
    if name == "oiti":            # dense rounded evergreen, medium (typical sidewalk tree)
        _trunk(mb, 2.6, .16, .11)
        _crown(mb, (0, 0, 4.4), 2.6, 7, .8, 1, 11)
        mats = ["tronco", "folhagem_oiti"]
    elif name == "sibipiruna":    # wide, flat, airy crown, medium-large
        _trunk(mb, 3.4, .2, .12, lean=(.04, 0))
        for bx, by in ((1.2, .4), (-1.0, .8), (.2, -1.1)):
            mb.box(bx * .5, by * .5, 3.2, .1, .1, 1.4, 0, rot=math.atan2(by, bx))
        _crown(mb, (0, 0, 5.6), 3.8, 9, .45, 1, 12)
        mats = ["tronco", "folhagem_clara"]
    elif name == "mangueira":     # big dark dome, back yards and greens
        _trunk(mb, 2.2, .26, .18)
        _crown(mb, (0, 0, 4.6), 3.6, 8, .85, 1, 13)
        mats = ["tronco", "folhagem_manga"]
    elif name == "ipe":           # small/medium, open irregular crown, flowering (yellow)
        _trunk(mb, 3.0, .12, .07, lean=(.06, .03))
        _crown(mb, (.2, .1, 4.4), 1.9, 6, .7, 1, 14)
        _crown(mb, (.2, .1, 4.9), 1.5, 3, .6, 2, 15)
        mats = ["tronco", "folhagem_clara", "flores_ipe_amarelo"]
    elif name == "ipe_rosa":
        _trunk(mb, 3.0, .12, .07, lean=(-.05, .04))
        _crown(mb, (-.2, .1, 4.4), 1.9, 6, .7, 1, 16)
        _crown(mb, (-.2, .1, 4.9), 1.6, 4, .6, 2, 17)
        mats = ["tronco", "folhagem_oiti", "flores_ipe_rosa"]
    elif name == "jovem":         # recently planted young tree with stakes and protection
        _trunk(mb, 1.6, .06, .04)
        _crown(mb, (0, 0, 2.5), 1.0, 4, .9, 1, 18)
        for dx in (-.25, .25):
            mb.box(dx, 0, 0, .04, .04, 1.6, 2)
        mb.box(0, 0, 1.2, .55, .04, .04, 2)
        mats = ["tronco", "folhagem", "madeira_crua"]
    elif name == "palmeira":      # imperial-palm-like, plazas and stately streets
        _trunk(mb, 11.0, .24, .2, segs=8)
        import random as _rr
        rr = _rr.Random(19)
        for k in range(9):
            a_ = k * 2 * math.pi / 9 + rr.uniform(-.2, .2)
            L_ = rr.uniform(2.6, 3.4)
            tip = (math.cos(a_) * L_, math.sin(a_) * L_, 11.0 - rr.uniform(.8, 1.6))
            w_ = .5
            px, py = -math.sin(a_) * w_, math.cos(a_) * w_
            mb.add_face([(0, 0, 11.2), (tip[0] * .5 + px, tip[1] * .5 + py, 11.4), tip, (tip[0] * .5 - px, tip[1] * .5 - py, 11.4)], 1)
        mats = ["tronco", "folhagem_palmeira"]
    else:                         # arbusto: low shrub mass (tops of retaining walls, greens)
        _crown(mb, (0, 0, .6), .9, 4, .7, 0, 20)
        mats = ["folhagem_oiti"]
    o = mb.to_object("VEG_" + name, [lib[m] for m in mats], library)
    for poly in o.data.polygons:                       # smooth crowns (no faceted low-poly read)
        poly.use_smooth = True
    sa_bl.props(o, sa_stage="W2.5 proxy de espécie (provisório)", species=name)
    return o


# ---------------------------------------------------------------- W3.1 street-front taludes (slice only)
# Vacant/green lots on the uphill side of a street: stepped retaining wall at the back of the sidewalk (terrain heights are NOT
# changed: the wall follows the existing ground ~3 m inside the lot), coping, weep holes, foot drainage channel, damp/contact band,
# steps cut into the wall with a pipe handrail, and brush/grass on the slope above.
TALUDE_SITES = []
if SLICE:
    TM = {"pedra": 0, "concreto": 1, "capa": 2, "tijolo": 3, "furo": 4, "umidade": 5, "corrimao": 6}
    tal_mb = {}
    for lot in ot.lots:
        if lot["family"] != "vacant" or not lot.get("front") or not in_slice_pt(lot["obb"].c, -5):
            continue
        o_ = lot["obb"]
        f_ = lot["front"]
        if any(r_[0] - 2 <= o_.c[0] <= r_[2] + 2 and r_[1] - 2 <= o_.c[1] <= r_[3] + 2 for r_ in (pd["rect"] for pd in terrain.pads)):
            continue
        inward = norm(vsub(o_.c, f_))
        cs_ = o_.corners()
        near = sorted(range(4), key=lambda i: dist(cs_[i], f_))[:2]
        p0, p1 = cs_[near[0]], cs_[near[1]]
        p0 = (p0[0] + inward[0] * .25, p0[1] + inward[1] * .25)
        p1 = (p1[0] + inward[0] * .25, p1[1] + inward[1] * .25)
        Lw = dist(p0, p1)
        if Lw < 8:
            continue
        rise = max(zs(q[0] + inward[0] * 3, q[1] + inward[1] * 3) for q in (p0, p1, lerp(p0, p1, .5))) - zs(*lerp(p0, p1, .5))
        if rise < .7:
            continue
        seed_ = zlib.crc32(lot["id"].encode())
        wmat = (TM["pedra"], TM["concreto"], TM["tijolo"])[seed_ % 3]
        macro, sub = subcell(*o_.c)
        mb = tal_mb.setdefault((macro, sub), sa_bl.MeshBuilder())
        ua = norm(vsub(p1, p0))
        ang = math.atan2(ua[1], ua[0])
        nseg = max(2, int(Lw // 3.2))
        stair_k = 0 if (seed_ >> 3) % 2 else nseg - 1
        h_max = 0.0
        for k in range(nseg):
            t0, t1 = k / nseg, (k + 1) / nseg
            a_ = lerp(p0, p1, t0)
            b_ = lerp(p0, p1, t1)
            c_ = lerp(a_, b_, .5)
            zb = min(zs(*a_), zs(*b_)) - .25
            zt = max(zs(a_[0] + inward[0] * 3, a_[1] + inward[1] * 3), zs(b_[0] + inward[0] * 3, b_[1] + inward[1] * 3)) + .3
            h_ = zt - zb
            h_max = max(h_max, h_)
            seg_L = dist(a_, b_)
            cc = (c_[0] + inward[0] * .18, c_[1] + inward[1] * .18)
            if k == stair_k and Lw > 10:
                # steps cut into the wall: 1.3 m wide flight climbing into the lot, side cheeks, pipe handrail
                nst = max(3, int(h_ / .18))
                run = .29
                side_w = (seg_L - 1.3) / 2
                for sgn in (-1, 1):
                    q_ = (cc[0] + ua[0] * sgn * (seg_L / 2 - side_w / 2), cc[1] + ua[1] * sgn * (seg_L / 2 - side_w / 2))
                    mb.box(q_[0], q_[1], zb, side_w, .36, h_, wmat, rot=ang)
                for j in range(nst):
                    q_ = (cc[0] + inward[0] * (j * run), cc[1] + inward[1] * (j * run))
                    mb.box(q_[0], q_[1], zb, 1.3, run + .02, .25 + (j + 1) * (h_ - .25) / nst, TM["concreto"], rot=ang)
                for sgn in (-1, 1):
                    for j in (0, nst - 1):
                        q_ = (cc[0] + ua[0] * sgn * .7 + inward[0] * j * run, cc[1] + ua[1] * sgn * .7 + inward[1] * j * run)
                        mb.box(q_[0], q_[1], zb + .25 + (j + 1) * (h_ - .25) / nst, .04, .04, .95, TM["corrimao"], rot=ang)
                    qa = (cc[0] + ua[0] * sgn * .7, cc[1] + ua[1] * sgn * .7)
                    qb = (qa[0] + inward[0] * (nst - 1) * run, qa[1] + inward[1] * (nst - 1) * run)
                    za_, zb_ = zb + .25 + (h_ - .25) / nst + .95, zb + h_ + .95
                    mb.add_face([(qa[0] - ua[0] * .02, qa[1] - ua[1] * .02, za_), (qa[0] + ua[0] * .02, qa[1] + ua[1] * .02, za_),
                                 (qb[0] + ua[0] * .02, qb[1] + ua[1] * .02, zb_), (qb[0] - ua[0] * .02, qb[1] - ua[1] * .02, zb_)], TM["corrimao"])
                    mb.add_face([(qa[0], qa[1], za_ + .02), (qb[0], qb[1], zb_ + .02), (qb[0], qb[1], zb_ - .02), (qa[0], qa[1], za_ - .02)], TM["corrimao"])
                continue
            mb.box(cc[0], cc[1], zb, seg_L + .02, .36, h_, wmat, rot=ang)                         # wall panel (stepped tops)
            mb.box(cc[0], cc[1], zt, seg_L + .06, .44, .07, TM["capa"], rot=ang)                  # coping
            # weep holes (PVC drains) and the damp/contact band at the foot
            for j in range(max(1, int(seg_L // 1.6))):
                tq = (j + .5) / max(1, int(seg_L // 1.6)) - .5
                q_ = (cc[0] + ua[0] * tq * seg_L - inward[0] * .2, cc[1] + ua[1] * tq * seg_L - inward[1] * .2)
                mb.box(q_[0], q_[1], zb + .55, .07, .1, .07, TM["furo"], rot=ang)
                if h_ > 2.2:
                    mb.box(q_[0], q_[1], zb + 1.55, .07, .1, .07, TM["furo"], rot=ang)
            fq = (cc[0] - inward[0] * .186, cc[1] - inward[1] * .186)
            mb.box(fq[0], fq[1], zb + .2, seg_L, .004, min(h_ - .3, .55 + (seed_ % 5) * .12), TM["umidade"], rot=ang)
            # rain streaks under every other coping joint
            if k % 2 == 0:
                sq = (cc[0] + ua[0] * seg_L * .45 - inward[0] * .188, cc[1] + ua[1] * seg_L * .45 - inward[1] * .188)
                mb.box(sq[0], sq[1], zt - 1.2, .35, .004, 1.15, TM["umidade"], rot=ang)
        # foot drainage channel (canaleta) along the wall
        fc_ = lerp(p0, p1, .5)
        fq = (fc_[0] - inward[0] * .05, fc_[1] - inward[1] * .05)
        mb.box(fq[0], fq[1], zs(*fc_) + ROAD_LIFT + SIDEWALK_H - .03, Lw, .22, .04, TM["capa"], rot=ang)
        mid_ = lerp(p0, p1, .5)
        TALUDE_SITES.append((h_max, mid_, inward, lot["id"], Lw))
        _dr = (seed_ >> 5) % 4
        if _dr < 3:
            _did = ("grafite_aurora", "grafite_crua", "grafite_tags")[_dr]
            _src = bpy.data.objects.get("ACC_dc_" + _did)
            if _src:
                tq = .3 if stair_k != 0 else .7
                wq = (p0[0] + ua[0] * Lw * tq - inward[0] * .025, p0[1] + ua[1] * Lw * tq - inward[1] * .025)
                do = bpy.data.objects.new(f"OT_Decal_Talude_{len(TALUDE_SITES):02d}", _src.data)
                cell_collection("Architecture", macro).objects.link(do)
                do.location = (wq[0], wq[1], zs(*wq) + .2)
                do.rotation_euler = (0, 0, math.atan2(-inward[0], inward[1]))
                register("Architecture", do.name, sub, do, sa_kind="decal", decal=_did)
        # slope vegetation above the wall: brush and tall grass on the retained ground
        trng = __import__("random").Random(seed_)
        for j in range(int(Lw * 1.6)):
            tq = trng.uniform(.05, .95)
            dq = trng.uniform(.6, 6.0)
            q_ = (p0[0] + ua[0] * Lw * tq + inward[0] * dq, p0[1] + ua[1] * Lw * tq + inward[1] * dq)
            TREE_QUEUE.append((q_[0], q_[1], zs(*q_) - .02, trng.choice(("tufo_mato", "tufo_grama_alta", "tufo_grama", "tufo_mato")),
                               trng.uniform(0, 6.28), trng.uniform(.7, 1.4)))
        if trng.random() < .5:
            q_ = (mid_[0] + inward[0] * 2.5, mid_[1] + inward[1] * 2.5)
            TREE_QUEUE.append((q_[0], q_[1], zs(*q_), "arbusto", trng.uniform(0, 6.28), trng.uniform(.8, 1.2)))
    for (macro, sub), mb in tal_mb.items():
        name = f"OT_SlopeWorks_W31_{sub}"
        o = mb.to_object(name, [lib[m] for m in ("pedra_reboco_historico", "concreto_aparente", "concreto_pintado", "tijolo_aparente",
                                                 "borracha_preta", "decal_umidade", "aco_pintado_cinza")], cell_collection("Architecture", macro))
        register("Architecture", name, sub, o, note="W3.1: arrimos de frente de rua (taludes em terrenos vagos), escada, drenagem")
    STATS["w31_street_taludes"] = len(TALUDE_SITES)
    STATS["w31_talude_max_h_m"] = round(max((t[0] for t in TALUDE_SITES), default=0), 2)


SPECIES = ("oiti", "sibipiruna", "mangueira", "ipe", "ipe_rosa", "jovem", "palmeira", "arbusto")
if SLICE:
    import sa_vegetation  # noqa: E402
    tree_objs = [sa_vegetation.tree(n, lib, library) for n in SPECIES]
    TREE_VARIANTS = ("oiti", "sibipiruna", "mangueira", "ipe", "jovem")
    for n in TREE_VARIANTS:                              # W3.1: two more individuals per common species (no nearby clones)
        tree_objs += [sa_vegetation.tree(n, lib, library, variant=v_) for v_ in ("_b", "_c")]
    tree_objs += [sa_vegetation.tuft(k, lib, library) for k in ("grama", "grama_alta", "erva", "mato")]
    lod_coll = sa_bl.collection("OT_Lib_Vegetation_LODs", library, hide_render=True)
    for n in SPECIES:                                    # LOD1 kept in the file for the Unity LOD groups (not instanced here)
        if n != "arbusto":
            sa_vegetation.tree(n, lib, lod_coll, lod=1)
    # grass and weeds: slopes/taludes, open ground, greens, cracks along curbs and wall bases
    _occ = {}
    for lot in ot.lots:
        if lot["family"] in ("vacant",) and not lot.get("green"):
            continue
        o_ = lot["obb"]
        for gx in range(int((o_.c[0] - 25) // 25), int((o_.c[0] + 25) // 25) + 1):
            for gy in range(int((o_.c[1] - 25) // 25), int((o_.c[1] + 25) // 25) + 1):
                _occ.setdefault((gx, gy), []).append(("lot", o_))
    for eid, e in g.edges.items():
        a_, b_ = g.seg(eid)
        if not (in_slice_pt(a_, 40) or in_slice_pt(b_, 40)):
            continue
        hw_ = STREET[e["cls"]]["total"] / 2 + .3
        for p_ in resample([a_, b_], 20.0):
            _occ.setdefault((int(p_[0] // 25), int(p_[1] // 25)), []).append(("road", (a_, b_, hw_)))

    def _free(p_):
        cells_ = [(int(p_[0] // 25) + i, int(p_[1] // 25) + j) for i in (-1, 0, 1) for j in (-1, 0, 1)]
        for kind_, it in (x for c_ in cells_ for x in _occ.get(c_, [])):
            if kind_ == "lot" and it.contains(p_):
                return False
            if kind_ == "road":
                a_, b_, hw_ = it
                from sa_geom import point_seg as _ps
                if _ps(p_, a_, b_)[0] < hw_:
                    return False
        for pd in terrain.pads:
            r_ = pd["rect"]
            if r_[0] - 2 <= p_[0] <= r_[2] + 2 and r_[1] - 2 <= p_[1] <= r_[3] + 2:
                return False
        return True
    _rng = __import__("random").Random(3031)
    tufts = 0
    yy = SLICE[1] + 1.2
    while yy < SLICE[3]:
        xx = SLICE[0] + 1.2
        while xx < SLICE[2]:
            q_ = (xx + _rng.uniform(-1, 1), yy + _rng.uniform(-1, 1))
            dzx = zs(q_[0] + 2, q_[1]) - zs(q_[0] - 2, q_[1])
            dzy = zs(q_[0], q_[1] + 2) - zs(q_[0], q_[1] - 2)
            slope_ = math.hypot(dzx, dzy) / 4.0
            pr_ = min(.75, .1 + slope_ * 2.5)
            if _rng.random() < pr_ and _free(q_):
                _r = _rng.random()
                _k = "tufo_grama" if _r < .5 else "tufo_grama_alta" if _r < .7 else "tufo_mato" if _r < .85 else "tufo_erva"
                TREE_QUEUE.append((q_[0], q_[1], zs(*q_) - .02, _k, _rng.uniform(0, 6.28), _rng.uniform(.6, 1.5)))
                tufts += 1
            xx += 2.4
        yy += 2.4
    # W3.1: dense spontaneous cover on vacant lots (mixed short grass, tall grass, brush, broadleaf weeds; worn path = sparser band)
    vac_tufts = 0
    for lot in ot.lots:
        if lot["family"] != "vacant" or not in_slice_pt(lot["obb"].c, -2):
            continue
        o_ = lot["obb"]
        if any(r_[0] - 2 <= o_.c[0] <= r_[2] + 2 and r_[1] - 2 <= o_.c[1] <= r_[3] + 2 for r_ in (pd["rect"] for pd in terrain.pads)):
            continue
        lr = __import__("random").Random(zlib.crc32(("veg" + str(lot["id"])).encode()))
        path_off = lr.uniform(-o_.hw * .5, o_.hw * .5)
        lx = -o_.hw + .6
        while lx < o_.hw - .6:
            ly = -o_.hd + .6
            while ly < o_.hd - .6:
                jx, jy = lx + lr.uniform(-.45, .45), ly + lr.uniform(-.45, .45)
                pr_ = .15 if abs(jx - path_off) < .5 else .72
                if lr.random() < pr_:
                    q_ = (o_.c[0] + o_.u[0] * jx + o_.v[0] * jy, o_.c[1] + o_.u[1] * jx + o_.v[1] * jy)
                    _r = lr.random()
                    _k = "tufo_grama" if _r < .45 else "tufo_grama_alta" if _r < .68 else "tufo_mato" if _r < .86 else "tufo_erva"
                    TREE_QUEUE.append((q_[0], q_[1], zs(*q_) - .02, _k, lr.uniform(0, 6.28), lr.uniform(.55, 1.5)))
                    vac_tufts += 1
                ly += .75
            lx += .75
    STATS["w31_vacant_lot_tufts"] = vac_tufts
    cracks = 0
    for eid, e in g.edges.items():
        if e["cls"] in ("passage",):
            continue
        a_, b_ = g.seg(eid)
        if not in_slice_pt(lerp(a_, b_, .5)):
            continue
        u_ = norm(vsub(b_, a_))
        n_ = perp(u_)
        L_ = dist(a_, b_)
        cw_, sw_ = carriageway(e["cls"]), STREET[e["cls"]]["sidewalk"]
        for side_ in (1, -1):
            for off_ in ((cw_ / 2 + .08), (cw_ / 2 + sw_ - .1)) if sw_ > 0 else ((cw_ / 2 - .1),):
                t_ = _rng.uniform(1, 6)
                while t_ < L_ - 1:
                    q_ = (a_[0] + u_[0] * t_ + n_[0] * side_ * off_, a_[1] + u_[1] * t_ + n_[1] * side_ * off_)
                    zq = zs(*q_) + (ROAD_LIFT if off_ < cw_ / 2 + .2 else ROAD_LIFT + SIDEWALK_H)
                    TREE_QUEUE.append((q_[0], q_[1], zq, "tufo_erva" if _rng.random() < .55 else "tufo_grama", _rng.uniform(0, 6.28), _rng.uniform(.35, .8)))
                    cracks += 1
                    t_ += _rng.uniform(4, 14)
    STATS["w3_tufts"] = tufts
    STATS["w3_crack_weeds"] = cracks
else:
    tree_objs = [species(n) for n in SPECIES]
tree_lib, tree_index = sa_bl.library_collection("OT_Lib_Vegetation", tree_objs, library)
_veg_tris = {}
for (x, y, z, sp, rot, scl) in TREE_QUEUE:
    if sp == "ipe" and (int(abs(x) * 3 + abs(y)) % 3 == 0):
        sp = "ipe_rosa"
    if SLICE and sp in TREE_VARIANTS:
        sp += ("", "_b", "_c")[zlib.crc32(f"{x:.1f},{y:.1f}".encode()) % 3]
    macro, sub = subcell(x, y)
    tree_pts.setdefault((macro, sub), []).append((x, y, z, tree_index["VEG_" + sp], rot, scl))
    STATS.setdefault("vegetation_by_species", {})
    STATS["vegetation_by_species"][sp] = STATS["vegetation_by_species"].get(sp, 0) + 1
STATS["vegetation_species_tris"] = {o.name: sum(len(p_.vertices) - 2 for p_ in o.data.polygons) for o in tree_objs}
STATS["street_tree_layout"] = ot.tree_stats
STATS["w31_trees"] = W31_TREES
for (macro, sub), pts in tree_pts.items():
    name = f"OT_Vegetation_{sub}"
    o = sa_bl.point_cloud_object(name, pts, tree_lib, cell_collection("Vegetation", macro))
    register("Vegetation", name, sub, o, instances=len(pts), blockout_vegetation=True, note="W2.5 proxies de espécies (provisório)")
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

# ---------------------------------------------------------------- W3.1 parked vehicles (slice only)
# Authored generic cars (sa_vehicles) parked along the slice streets: shared-mesh instances pitched to the street grade.
# Older/worn cars on local residential streets, newer ones on main/collector streets, service vehicles near Oficina/Horizonte.
if SLICE:
    import random as _rnd  # noqa: E402
    import sa_vehicles  # noqa: E402
    veh_lib = sa_bl.collection("OT_Lib_Vehicles", library, hide_render=True)
    veh_lods = sa_bl.collection("OT_Lib_Vehicles_LODs", library, hide_render=True)
    VEH = {}
    for (fam_, pk_, worn_) in sa_vehicles.LIBRARY:
        VEH[(fam_, pk_, worn_)] = sa_vehicles.build(fam_, lib, veh_lib, pk_, worn_)
        sa_vehicles.build(fam_, lib, veh_lods, pk_, worn_, lod=1)
    for fam_ in sa_vehicles.FAMILIES:
        sa_vehicles.proxy(fam_, lib, veh_lods)
    _new = [k for k in VEH if not k[2] and k[0] not in ("van", "picape")]
    _old = [k for k in VEH if k[2]]
    _svc = [k for k in VEH if k[0] in ("van", "picape") and not k[2]]
    _vr = _rnd.Random(3101)
    _heroes = {h["id"]: h["lot"] for h in ot.data["heroes"]}
    _service_at = [_heroes[k] for k in ("garage", "horizonte") if k in _heroes]

    def _near_rect(q, r, m):
        return r[0] - m <= q[0] <= r[2] + m and r[1] - m <= q[1] <= r[3] + m
    parked, veh_count = 0, {}
    EDGE_CARS = {}
    for eid, e in sorted(g.edges.items()):
        if e["cls"] in ("passage", "alley", "service"):
            continue
        a_, b_ = g.seg(eid)
        if not in_slice_pt(lerp(a_, b_, .5)):
            continue
        L_ = dist(a_, b_)
        if L_ < 18:
            continue
        u_ = norm(vsub(b_, a_))
        n_ = perp(u_)
        cw_ = carriageway(e["cls"])
        if abs(zs(*b_) - zs(*a_)) / L_ > .14:
            continue
        for side_ in (1, -1):
            if e["cls"] == "local" and side_ == -1 and _vr.random() < .45:
                continue                                  # many residential streets park on one side only
            off_ = cw_ / 2 - 1.05
            t_ = _vr.uniform(8, 13)
            while t_ < L_ - 8:
                q_ = (a_[0] + u_[0] * t_ + n_[0] * side_ * off_, a_[1] + u_[1] * t_ + n_[1] * side_ * off_)
                step_ = _vr.uniform(5.4, 8.5)
                if _vr.random() < (.2 if e["cls"] == "arterial" else .32) and not any(_near_rect(q_, r, 5.5) for r in _heroes.values()) and                         not any(dist(q_, ts_[1]) < ts_[4] / 2 + 4 for ts_ in TALUDE_SITES):
                    if any(_near_rect(q_, r, 30) for r in _service_at) and _vr.random() < .6:
                        key_ = _vr.choice(_svc)
                    elif _vr.random() < (.45 if e["cls"] == "local" else .12):
                        key_ = _vr.choice(_old)
                    else:
                        key_ = _vr.choice(_new)
                    head_ = math.atan2(u_[1], u_[0]) + (math.pi if side_ == 1 else 0.0) + _vr.uniform(-.04, .04)
                    hx, hy = math.cos(head_), math.sin(head_)
                    pitch_ = math.atan2(zs(q_[0] + hx * 2, q_[1] + hy * 2) - zs(q_[0] - hx * 2, q_[1] - hy * 2), 4.0)
                    macro, sub = subcell(*q_)
                    src_ = VEH[key_]
                    vo = bpy.data.objects.new(f"OT_Vehicle_{sub}_{parked:03d}", src_.data)
                    cell_collection("Props", macro).objects.link(vo)
                    vo.location = (q_[0], q_[1], zs(*q_) + ROAD_LIFT - .01)
                    vo.rotation_euler = (0.0, -pitch_, head_)
                    register("Props", vo.name, sub, vo, sa_kind="vehicle", vehicle=src_.name, sa_lod="LOD0 (LOD1/proxy em OT_Lib_Vehicles_LODs)")
                    veh_count[key_[0]] = veh_count.get(key_[0], 0) + 1
                    EDGE_CARS.setdefault(eid, []).append((q_, key_, side_))
                    parked += 1
                    step_ += 1.5
                t_ += step_
    STATS["w31_parked_vehicles"] = parked
    STATS["w31_vehicles_by_family"] = veh_count
    STATS["w31_vehicle_lod0_tris"] = {o.name: sum(len(p_.vertices) - 2 for p_ in o.data.polygons) for o in VEH.values()}

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
# W2.5 views: steepest core street (from its low end looking uphill), Alto da Aurora overlook, córrego valley, wear street.
best = None
for eid, e in g.edges.items():
    if e["cls"] not in ("local", "main"):
        continue
    a, b = g.seg(eid)
    L = dist(a, b)
    if L < 70 or not (-3300 < a[1] < -1100 and -3400 < a[0] < -1500):
        continue
    gr_ = abs(zs(*b) - zs(*a)) / L
    if best is None or gr_ > best[0]:
        best = (gr_, a, b)
gr_, a, b = best
lo_, hi_ = (a, b) if zs(*a) < zs(*b) else (b, a)
u = norm(vsub(hi_, lo_))
cpos = (lo_[0] - u[0] * 6, lo_[1] - u[1] * 6)
cam("CAM_OT_Rua_Relevo", (cpos[0], cpos[1], zs(*cpos) + 1.7), target=(hi_[0], hi_[1], zs(*hi_) + 2.0), lens=24)
STATS["relief_street_grade_pct"] = round(gr_ * 100, 1)
ap = (-2250.0, -850.0)
cam("CAM_OT_Alto_Aurora", (ap[0] - 60, ap[1] - 140, zs(ap[0] - 60, ap[1] - 140) + 28), target=(-2700, -1900, zs(-2700, -1900)), lens=26)
vz, vx = -2050.0, -2745.0
cam("CAM_OT_Vale_Corrego", (vx + .3, vz - 40, zs(vx, vz - 40) + 2.2), target=(vx - 10, vz + 140, zs(vx, vz + 140) + 1.0), lens=22)
# Street descending into the córrego valley: steepest core edge whose low end is near R02, seen from its high end.
vbest = None
for eid, e in g.edges.items():
    if e["cls"] not in ("local", "main"):
        continue
    a, b = g.seg(eid)
    L = dist(a, b)
    if L < 60 or not (-3000 < a[1] < -1200):
        continue
    lo_, hi_ = (a, b) if zs(*a) < zs(*b) else (b, a)
    if terrain.valley_distance(*lo_) > 160 or terrain.valley_distance(*hi_) < terrain.valley_distance(*lo_) + 30:
        continue
    gr_ = (zs(*hi_) - zs(*lo_)) / L
    if vbest is None or gr_ > vbest[0]:
        vbest = (gr_, lo_, hi_)
gr_, lo_, hi_ = vbest
u = norm(vsub(lo_, hi_))
cpos = (hi_[0] - u[0] * 4, hi_[1] - u[1] * 4)
far = (lo_[0] + u[0] * 220, lo_[1] + u[1] * 220)
cam("CAM_OT_Vale_Panorama", (cpos[0], cpos[1], zs(*cpos) + 1.8), target=(far[0], far[1], zs(*far) + 4.0), lens=24)
STATS["valley_street_grade_pct"] = round(gr_ * 100, 1)
cam("CAM_OT_Wear_Rua", (-3290, -1622, zs(-3290, -1622) + 1.7), target=(-3420, -1606, zs(-3420, -1606) + 3.0), lens=22)   # Av. Velha, no hero in view
# W2.5 vegetation views: most planted residential street (from one end), a pocket green, and an oblique of the residential north.
import collections as _col  # noqa: E402
_tgrid = _col.Counter((int(t[0] // 20), int(t[1] // 20)) for t in ot.street_trees)
rbest = None
for eid, e in g.edges.items():
    if e["cls"] not in ("local", "main"):
        continue
    a, b = g.seg(eid)
    L = dist(a, b)
    if L < 45:
        continue
    cnt = sum(_tgrid[(int(p[0] // 20), int(p[1] // 20))] for p in resample([a, b], 20.0))
    if rbest is None or cnt / L > rbest[0]:
        rbest = (cnt / L, a, b)
_, a, b = rbest
u = norm(vsub(b, a))
cpos = (a[0] + u[0] * 3 + perp(u)[0] * 1.5, a[1] + u[1] * 3 + perp(u)[1] * 1.5)
cam("CAM_OT_Rua_Arborizada", (cpos[0], cpos[1], zs(*cpos) + 1.7), target=(b[0], b[1], zs(*b) + 3.0), lens=22)
pg = next((l for l in ot.lots if l.get("green") and l["obb"].hw > 7), None)
if pg:
    o = pg["obb"]
    cp = (o.c[0] - o.v[0] * (o.hd + 10) + o.u[0] * 6, o.c[1] - o.v[1] * (o.hd + 10) + o.u[1] * 6)
    cam("CAM_OT_Pracinha", (cp[0], cp[1], zs(*cp) + 2.0), target=(o.c[0], o.c[1], zs(*o.c) + 1.5), lens=22)
cam("CAM_OT_Residencial_Obliqua", (-2050, -1300, zs(-2050, -1300) + 140), target=(-2300, -880, zs(-2300, -880)), lens=28)
if SLICE:
    cx_, cy_ = (SLICE[0] + SLICE[2]) / 2, (SLICE[1] + SLICE[3]) / 2
    cam("CAM_W3_Corredor", (SLICE[2] + 120, SLICE[1] - 160, zs(cx_, cy_) + 210), target=(cx_ - 60, cy_ + 60, zs(cx_, cy_)), lens=30)
    cam("CAM_W3_Aereo", (SLICE[0] - 90, SLICE[1] - 200, zs(cx_, cy_) + 95), target=(-2745, cy_ + 150, zs(-2745, cy_ + 150) - 5), lens=28)
    best = None
    for eid, e in g.edges.items():
        if e["cls"] not in ("local", "main"):
            continue
        a, b = g.seg(eid)
        L = dist(a, b)
        if L < 60 or not (in_slice_pt(a, -30) and in_slice_pt(b, -30)):
            continue
        gr_ = abs(zs(*b) - zs(*a)) / L
        if best is None or gr_ > best[0]:
            best = (gr_, a, b)
    if best:
        gr_, a, b = best
        lo_, hi_ = (a, b) if zs(*a) < zs(*b) else (b, a)
        u = norm(vsub(hi_, lo_))
        cpos = (lo_[0] - u[0] * 6 + perp(u)[0] * 1.2, lo_[1] - u[1] * 6 + perp(u)[1] * 1.2)
        cam("CAM_W3_Rua", (cpos[0], cpos[1], zs(*cpos) + 1.7), target=(hi_[0], hi_[1], zs(*hi_) + 2.2), lens=22)
        STATS["w3_street_grade_pct"] = round(gr_ * 100, 1)
    tsites = sorted(TALUDE_SITES, key=lambda st: -(min(st[0], 3.5) + st[4] * .05))
    if tsites:
        # W3.1: dedicated talude view from the opposite sidewalk at eye height (no roofs in the way), oblique along the wall
        h_, c, inward, lid, Lw = tsites[0]
        ua = perp(inward)
        cp = (c[0] - inward[0] * 7 + ua[0] * 5, c[1] - inward[1] * 7 + ua[1] * 5)
        cam("CAM_W31_Talude", (cp[0], cp[1], zs(*cp) + 1.65), target=(c[0] + inward[0] * 1.0 - ua[0] * 1.5, c[1] + inward[1] * 1.0 - ua[1] * 1.5,
                                                                     zs(*c) + min(h_, 3) * .55), lens=22)
        h2 = tsites[1] if len(tsites) > 1 else tsites[0]
        c2, in2 = h2[1], h2[2]
        cp = (c2[0] - in2[0] * 6.5 - perp(in2)[0] * 4.5, c2[1] - in2[1] * 6.5 - perp(in2)[1] * 4.5)
        cam("CAM_W31_Talude_B", (cp[0], cp[1], zs(*cp) + 1.65), target=(c2[0] + in2[0] * 2, c2[1] + in2[1] * 2, zs(*c2) + min(h2[0], 3) * .6), lens=22)
        STATS["w31_talude_capture_site"] = {"lot": lid, "wall_h_m": round(h_, 2), "wall_len_m": round(Lw, 1)}
    sites = sorted([st for st in SLOPE_SITES if in_slice_pt(st[1], -20)], key=lambda st: -st[0])
    if sites:
        h_, c, ang, f = sites[0]
        away = norm(vsub(f, c))
        cp = (c[0] - away[0] * 16 + math.cos(ang) * 12, c[1] - away[1] * 16 + math.sin(ang) * 12)
        cam("CAM_W3_Talude", (cp[0], cp[1], max(zs(*cp), zs(*c)) + h_ + 14), target=(c[0] + away[0] * 6, c[1] + away[1] * 6, zs(*c)), lens=24)
        STATS["w3_talude_height_m"] = round(h_, 2)
    # ---------------- W3.1 cameras (chosen from what was generated: parked cars, variant-rich lots, decals, grass)
    def _lot_cam(name, lot_, back=9.0, side=3.5, h=1.65, th=2.2, lens=24):
        o_ = lot_["obb"]
        f_ = lot_["front"]
        outw = norm(vsub(f_, o_.c))
        al = perp(outw)
        cp_ = (f_[0] + outw[0] * back + al[0] * side, f_[1] + outw[1] * back + al[1] * side)
        tq = (f_[0] - outw[0] * .5, f_[1] - outw[1] * .5)
        cam(name, (cp_[0], cp_[1], max(zs(*cp_), zs(*f_)) + h), target=(tq[0], tq[1], zs(*f_) + th), lens=lens)
    if "EDGE_CARS" in globals() and EDGE_CARS:
        ranked = sorted(EDGE_CARS.items(), key=lambda kv: -(len(kv[1]) + len({k_[1][0] for k_ in kv[1]}) * 1.5))
        used_ = []
        for nm_, (eid_, cars_) in zip(("CAM_W31_Carros_A", "CAM_W31_Carros_B"), [r_ for r_ in ranked if True][:8:3]):
            a_, b_ = g.seg(eid_)
            u_ = norm(vsub(b_, a_))
            n_ = perp(u_)
            sd = cars_[0][2]
            cw_ = carriageway(g.edges[eid_]["cls"])
            first = min(cars_, key=lambda c_: dist(c_[0], a_))[0]
            cp_ = (first[0] - u_[0] * 7 + n_[0] * sd * (cw_ / 2 + 1.3), first[1] - u_[1] * 7 + n_[1] * sd * (cw_ / 2 + 1.3))
            tq = (first[0] + u_[0] * 14, first[1] + u_[1] * 14)
            cam(nm_, (cp_[0], cp_[1], zs(*cp_) + 1.6), target=(tq[0], tq[1], zs(*tq) + .9), lens=24)
        STATS["w31_car_cameras"] = [len(ranked[0][1])]
    _sun = (-.866, -.5)                                       # horizontal direction toward the sun (production_look azimuth 300°)

    def _lit(l_):
        o_ = norm(vsub(l_["front"], l_["obb"].c))
        return o_[0] * _sun[0] + o_[1] * _sun[1] > .25
    _var = lambda l_: sum(1 for k_ in LOT_ACC.get(l_["id"], []) if k_.startswith("w31_"))
    _dec = lambda l_: sum(1 for k_ in LOT_ACC.get(l_["id"], []) if k_.startswith("dc_"))
    cand = [l_ for l_ in ot.lots if l_.get("front") and in_slice_pt(l_["obb"].c, -15) and l_["id"] in LOT_ACC and _lit(l_)]
    if cand:
        # block view: lot whose ~45 m neighbourhood holds the most variant pieces
        def _blk(l_):
            return sum(_var(m_) for m_ in cand if dist(m_["obb"].c, l_["obb"].c) < 45)
        bl_ = max(cand, key=_blk)
        _lot_cam("CAM_W31_Quadra", bl_, back=6.5, side=26.0, h=7.5, th=3.5, lens=26)
        fl_ = max(cand, key=lambda l_: _var(l_) * 2 + _dec(l_) + (3 if any(k_.startswith("dc_placa") for k_ in LOT_ACC[l_["id"]]) else 0))
        _lot_cam("CAM_W31_Fachada", fl_, back=9.5, side=3.0, h=1.7, th=2.4, lens=24)
        dl_ = max((l_ for l_ in cand if l_ is not fl_), key=lambda l_: _dec(l_) * 2 + (4 if any(k_.startswith("dc_grafite") for k_ in LOT_ACC[l_["id"]]) else 0))
        _lot_cam("CAM_W31_Decals", dl_, back=5.0, side=-1.5, h=1.55, th=1.4, lens=28)
        STATS["w31_capture_lots"] = {"quadra": bl_["id"], "fachada": fl_["id"], "decals": dl_["id"]}
    vac = [l_ for l_ in ot.lots if l_["family"] == "vacant" and l_.get("front") and in_slice_pt(l_["obb"].c, -10)]
    if vac:
        gl_ = max(vac, key=lambda l_: zs(*l_["obb"].c) - zs(*l_["front"]) + l_["obb"].hw * .05)
        o_ = gl_["obb"]
        inw = norm(vsub(o_.c, gl_["front"]))
        cp_ = (gl_["front"][0] + inw[0] * 2.5 + perp(inw)[0] * 1.5, gl_["front"][1] + inw[1] * 2.5 + perp(inw)[1] * 1.5)
        tq = (o_.c[0] + inw[0] * 2, o_.c[1] + inw[1] * 2)
        cam("CAM_W31_Grama", (cp_[0], cp_[1], zs(*cp_) + .75), target=(tq[0], tq[1], zs(*tq) + .2), lens=28)
    gz = zs(-2594, -1480)
    cam("CAM_W3_Mercearia", (-2616, -1468, gz + 1.7), target=(-2590, -1481, gz + 3.0), lens=20)
    cam("CAM_W3_Vidro", (-2599.5, -1478.5, gz + 1.6), target=(-2588, -1482, gz + 1.3), lens=22)
    hz_ = zs(-2860, -2270)
    cam("CAM_W3_Material", (-2851.5, -2265.5, hz_ + 1.55), target=(-2857.5, -2270.4, hz_ + 1.1), lens=32)
    import collections as _c2
    tg = _c2.Counter((int(t[0] // 20), int(t[1] // 20)) for t in ot.street_trees if in_slice_pt((t[0], t[1])))
    vbest = None
    for eid, e in g.edges.items():
        if e["cls"] not in ("local", "main"):
            continue
        a, b = g.seg(eid)
        L = dist(a, b)
        if L < 45 or not (in_slice_pt(a, -10) and in_slice_pt(b, -10)):
            continue
        cnt = sum(tg[(int(p[0] // 20), int(p[1] // 20))] for p in resample([a, b], 20.0))
        if vbest is None or cnt / L > vbest[0]:
            vbest = (cnt / L, a, b)
    if vbest:
        _, a, b = vbest
        u = norm(vsub(b, a))
        cpos = (a[0] + u[0] * 3 + perp(u)[0] * 2.0, a[1] + u[1] * 3 + perp(u)[1] * 2.0)
        cam("CAM_W3_Vegetacao", (cpos[0], cpos[1], zs(*cpos) + 1.7), target=(b[0], b[1], zs(*b) + 3.0), lens=24)
    mz = zs(-2620, -1650)
    cam("CAM_W3_Clutter", (-2617, -1665, mz + 1.7), target=(-2626, -1560, zs(-2626, -1560) + 2.4), lens=24)
scene.camera = bpy.data.objects["CAM_OT_Oblique"]

scene["facility_world"] = "Santa Aurora"
scene["facility_area"] = "Cidade Antiga"
scene["facility_stage"] = "W2.5 base de produção (relevo + desgaste; não é arte final)"
out_dir = root / "ArtSource" / "Blender" / "World" / "OldTown"
blend = out_dir / "SantaAurora_CidadeAntiga_Base_v1.blend"
if SLICE:
    removed = 0
    for o_ in list(bpy.data.objects):
        sc_ = o_.get("sa_subcell")
        if sc_ and not in_slice_sub(sc_):
            bpy.data.objects.remove(o_)
            removed += 1
    # context: link the W2.5/W3 district subcells around the slice from the base file (same streaming names, no duplicates)
    base_manifest = json.loads((out_dir / "oldtown_streaming_manifest_v1.json").read_text(encoding="utf-8"))
    want = []
    for sub, layers in base_manifest["subcells"].items():
        if in_slice_sub(sub):
            continue
        bx0, by0, bx1, by1 = sub_bounds(sub)
        dx_ = max(SLICE[0] - bx1, 0, bx0 - SLICE[2])
        dy_ = max(SLICE[1] - by1, 0, by0 - SLICE[3])
        if math.hypot(dx_, dy_) > opts.context:
            continue
        for layer, names in layers.items():
            if layer in ("Gameplay",):
                continue
            want += names
    ctx = sa_bl.collection("W3_Context_Base_Linked", top)
    with bpy.data.libraries.load(str(blend), link=True, relative=True) as (src, dst):
        dst.objects = [n for n in want if n in src.objects]
    for o_ in dst.objects:
        if o_ is not None:
            ctx.objects.link(o_)
    STATS["w3_slice"] = {"rect": SLICE, "removed_outside": removed, "context_linked": len([o_ for o_ in dst.objects if o_ is not None])}
    out_dir = out_dir / "W3"
    out_dir.mkdir(parents=True, exist_ok=True)
    blend = out_dir / "SantaAurora_W3_VerticalSlice.blend"
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
if not SLICE:  # the slice reuses the district manifest (same streaming names) and writes only its own report
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
(out_dir / ("w3_slice_generation_report.json" if SLICE else "oldtown_generation_report.json")).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("OLD TOWN BASE GENERATED", json.dumps({k: report[k] for k in ("blend", "objectCount", "buildingInstances", "subcells")}))
