"""W2 — Lar inicial (Edifício Santa Clara, Apto 12): high-fidelity production base.

Run:
blender --background --factory-startup --python Tools/Blender/create_w2_hero_home.py -- --root PROJECT_ROOT

Output: ArtSource/Blender/World/OldTown/Heroes/W2_home_starter.blend
The building is modelled in a local frame (front facade at -Y, origin at the building centre on the ground) under a root
empty placed at the world position used by the Old Town base, so the hero can be loaded as its own scene in Unity.
Data source: ArtSource/Blender/World/OldTown/oldtown_heroes_v1.json (rooms, door, windows, H0-H4 slots).
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

import sa_bl  # noqa: E402
import sa_detail  # noqa: E402
import sa_materials  # noqa: E402
from masterplan_layout import load_spec  # noqa: E402
from sa_heroes import Frame  # noqa: E402
from sa_terrain import Terrain  # noqa: E402

data = json.loads((root / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json").read_text(encoding="utf-8"))
hero = next(h for h in data["heroes"] if h["id"] == "home.starter")
spec = load_spec(root)
terrain = Terrain(spec)
bld = hero["buildings"][0]
x0, y0, x1, y1 = hero["lot"]
ground = sum(terrain.surface(*p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), ((x0 + x1) / 2, (y0 + y1) / 2))) / 5 + .12
fr = Frame(bld["rect"], hero["front"], ground)
W, D = fr.w, fr.d          # 14 x 19
FH = bld["fh"]             # 3.0
NF = bld["floors"]         # 4
T_OUT, T_IN = .25, .14

sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "W2_home_starter"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
lib = sa_materials.build_library()
sa_detail.extend_library(lib)
from sa_heroes import fixed  # noqa: E402
FACADE = fixed(lib, bld["facade"]).name
lib[FACADE] = bpy.data.materials[FACADE]
try:
    scene.eevee.shadow_pool_size = "1024"
except (AttributeError, TypeError):
    pass

top = sa_bl.collection("W2_home.starter")
C = {k: sa_bl.collection(f"W2_home__{k}", top) for k in ("Shell", "Interior", "Openings", "Services", "Props_H0", "Site", "Gameplay")}
scene_only = sa_bl.collection("W2_home.starter__SceneOnly")  # outside the hero collection: never travels with a linked instance
C.update({k: sa_bl.collection(f"W2_home__{k}", scene_only) for k in ("Lighting", "Cameras", "CaptureOnly")})
rootobj = bpy.data.objects.new("W2_home.starter_ROOT", None)
rootobj.empty_display_type = "ARROWS"
rootobj.location = (fr.c[0], fr.c[1], ground)
rootobj.rotation_euler = (0, 0, fr.rot)
top.objects.link(rootobj)
sa_bl.props(rootobj, facility_id="home.starter", sa_stage="W2 base de produção", world_ground_z=round(ground, 3),
            note="Raiz do herói: filhos em coordenadas locais (frente em -Y). Transform = posição no mundo (Cidade Antiga).")


def L(p):
    """World (x, y) -> local (x, y)."""
    return fr.to_local(p)


def Lrect(r):
    a, b = L((r[0], r[1])), L((r[2], r[3]))
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def parented(o):
    o.parent = rootobj
    return o


def mesh(name, mb, mats, coll, bevel=0.0, **meta):
    if bevel:
        o = sa_bl.bevelled_object(name, mb, [lib[m] for m in mats], coll, bevel=bevel)
    else:
        o = mb.to_object(name, [lib[m] for m in mats], coll)
    sa_bl.props(o, facility_id="home.starter", sa_stage="W2 base de produção", **meta)
    return parented(o)


def wall_segment(mb, p0, p1, t, z0, z1, ops, mat, mat_in=None):
    """Axis/oblique wall from p0 to p1 (centre line), thickness t, with openings [(s0, s1, zb, zt)] along the segment."""
    L_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    ux, uy = math.cos(ang), math.sin(ang)

    def piece(s0, s1, za, zb):
        if s1 - s0 < .01 or zb - za < .01:
            return
        c = (p0[0] + ux * (s0 + s1) / 2, p0[1] + uy * (s0 + s1) / 2)
        mb.box(c[0], c[1], za, s1 - s0, t, zb - za, mat, rot=ang)

    cur = 0.0
    for s0, s1, zb, zt in sorted(ops):
        piece(cur, s0, z0, z1)
        piece(s0, s1, z0, zb)
        piece(s0, s1, zt, z1)
        cur = s1
    piece(cur, L_, z0, z1)


# ---------------------------------------------------------------- plan (local)
unit = Lrect(hero["interior"]["unit_rect"])
cor = Lrect(hero["interior"]["corridor_rect"])
stair = Lrect(hero["interior"]["stair_rect"])
hw, hd = W / 2, D / 2
front_y = -hd
unit_back = unit[3] if abs(unit[1] - (front_y + T_OUT)) < .5 else unit[1]
front_units_y = (front_y + T_OUT, unit[3]) if unit[1] < 0 else (unit[1], unit[3])
fy0, fy1 = sorted((unit[1], unit[3]))
sy0, sy1 = stair[1], stair[3]
if sy0 < 0:
    raise RuntimeError("stair zone expected at the back (local +Y)")
cx0, cx1 = cor[0], cor[2]
by0, by1 = fy1 + T_IN, sy0 - T_IN / 2
units = {
    "12_front_A": (unit[0], fy0, unit[2], fy1),
    "front_B": (-unit[2], fy0, -unit[0], fy1),
    "back_A": (unit[0], by0, unit[2], by1),
    "back_B": (-unit[2], by0, -unit[0], by1),
}
door_w = hero["interior"]["door"]["w"]
door_local = L(hero["interior"]["door"]["p"])
door_s = door_local[1]  # position along the corridor wall (local y)

# ---------------------------------------------------------------- shell per floor
win_front = [w for w in hero["interior"]["windows"] if w["wall"] == "N"][0]
win_side = [w for w in hero["interior"]["windows"] if w["wall"] == "W"]
wx_front = L(win_front["p"])[0]
entrance_x = L(hero["entrances"][0]["p"])[0]
openings_by_floor = {}
for f in range(NF):
    z0 = f * FH
    ops = {"front": [], "back": [], "side_A": [], "side_B": []}
    sill, wh = win_front["sill"], win_front["h"]
    for sx in (1, -1):
        cxw = wx_front * sx
        ops["front"].append((cxw + hw - win_front["w"] / 2, cxw + hw + win_front["w"] / 2, z0 + sill, z0 + sill + wh, "window", cxw))
        cxb = cxw
        ops["back"].append((hw - cxb - .8, hw - cxb + .8, z0 + 1.0, z0 + 2.2, "window", cxb))
    if f == 0:
        ops["front"].append((entrance_x + hw - .6, entrance_x + hw + .6, z0, z0 + 2.3, "door", entrance_x))
    else:
        ops["back"].append((hw - .7, hw + .7, z0 + 1.2, z0 + 2.0, "window", 0.0))  # stair window
    for k, w in enumerate(win_side):
        s = L(w["p"])[1] + hd
        kind = "basculante" if w["h"] < .8 else "window"
        ops["side_A"].append((s - w["w"] / 2, s + w["w"] / 2, z0 + w["sill"], z0 + w["sill"] + w["h"], kind, s))
        ops["side_B"].append((D - s - w["w"] / 2, D - s + w["w"] / 2, z0 + w["sill"], z0 + w["sill"] + w["h"], kind, D - s))
        sb = (L(w["p"])[1] - fy0) + by0 + hd
        ops["side_A"].append((sb - w["w"] / 2, sb + w["w"] / 2, z0 + w["sill"], z0 + w["sill"] + w["h"], kind, sb))
        ops["side_B"].append((D - sb - w["w"] / 2, D - sb + w["w"] / 2, z0 + w["sill"], z0 + w["sill"] + w["h"], kind, D - sb))
    openings_by_floor[f] = ops

# U stair at the back: flights along -X from x=-1.0, landing at the west; slab opening above it.
STAIR_ORIGIN = (-1.0, sy1 - .15)
STAIR_W, STAIR_RUN = 1.1, 2.52
STAIR_HOLE = (STAIR_ORIGIN[0] - STAIR_RUN - 1.25, STAIR_ORIGIN[1] - 2 * STAIR_W - .15, STAIR_ORIGIN[0] + .05, STAIR_ORIGIN[1] + .05)
assert unit[0] > 0, "Apto 12 expected at local +X (east of the corridor)"
side_x = unit[0] - T_OUT / 2 if unit[0] < 0 else unit[2] + T_OUT / 2
sideA_x = -hw + T_OUT / 2 if side_x < 0 else hw - T_OUT / 2
for f in range(NF):
    z0, z1 = f * FH, (f + 1) * FH
    mb = sa_bl.MeshBuilder()
    o = openings_by_floor[f]
    # outer skin (plaster) + inner skin (paint)
    segs = {
        "front": ((-hw, front_y + .1), (hw, front_y + .1)),
        "back": ((hw, hd - .1), (-hw, hd - .1)),
        "side_A": ((-hw + .1, front_y), (-hw + .1, hd)),
        "side_B": ((hw - .1, hd), (hw - .1, front_y)),
    }
    for key, (p0, p1) in segs.items():
        ops = [(a, b, zb, zt) for a, b, zb, zt, _, _ in o[key]]
        wall_segment(mb, p0, p1, .2, z0, z1, ops, 0)
    segs_in = {
        "front": ((-hw + .2, front_y + .225), (hw - .2, front_y + .225)),
        "back": ((hw - .2, hd - .225), (-hw + .2, hd - .225)),
        "side_A": ((-hw + .225, front_y + .2), (-hw + .225, hd - .2)),
        "side_B": ((hw - .225, hd - .2), (hw - .225, front_y + .2)),
    }
    for key, (p0, p1) in segs_in.items():
        ops = [(a - .2 if key in ("front", "back") else a - .2, b - .2 if key in ("front", "back") else b - .2, zb, zt) for a, b, zb, zt, _, _ in o[key]]
        wall_segment(mb, p0, p1, .05, z0 + .15, z1, ops, 1)
    # painted ceiling skin under the next slab (the slab underside stays raw concrete only where unseen)
    mb.box(0, 0, z1 - .012, W - .5, D - .5, .01, 1, top=False, bottom=True)
    # plinth band (ceramic) on the ground floor exterior
    if f == 0:
        mb.box(0, front_y - .005, -.6, W + .02, .03, 1.2, 2)
        mb.box(0, hd + .005, -.6, W + .02, .03, 1.2, 2)
        mb.box(-hw - .005, 0, -.6, .03, D + .02, 1.2, 2)
        mb.box(hw + .005, 0, -.6, .03, D + .02, 1.2, 2)
    # floor slab with edge band (friso) on the facade
    if f == 0:
        mb.box(0, 0, z0, W - .02, D - .02, .15, 3, bottom=True)
    else:
        hx0, hy0, hx1, hy1 = STAIR_HOLE
        for (ax0, ay0, ax1, ay1) in ((-hw + .01, -hd + .01, hw - .01, hy0), (-hw + .01, hy1, hw - .01, hd - .01),
                                     (-hw + .01, hy0, hx0, hy1), (hx1, hy0, hw - .01, hy1)):
            mb.box((ax0 + ax1) / 2, (ay0 + ay1) / 2, z0, ax1 - ax0, ay1 - ay0, .15, 3, bottom=True)
    if f > 0:
        for (cx, cy, sx, sy) in ((0, front_y - .03, W + .06, .06), (0, hd + .03, W + .06, .06), (-hw - .03, 0, .06, D + .06), (hw + .03, 0, .06, D + .06)):
            mb.box(cx, cy, z0 - .05, sx, sy, .2, 4)
    mesh(f"W2_home__shell_F{f:02d}", mb, [FACADE, "parede_pintada", "ceramica_piso",
                                         "concreto_aparente", "concreto_pintado"], C["Shell"], floor_index=f, sa_layer="Architecture")

# Roof: slab, parapet with cap, water tanks on concrete base, hatch, vents, rear downpipes.
zr = NF * FH
mb = sa_bl.MeshBuilder()
mb.box(0, 0, zr, W, D, .15, 0, bottom=True)
for (cx, cy, sx, sy) in ((0, front_y + .075, W, .15), (0, hd - .075, W, .15), (-hw + .075, 0, .15, D), (hw - .075, 0, .15, D)):
    mb.box(cx, cy, zr + .15, sx, sy, .9, 1)
for (cx, cy, sx, sy) in ((0, front_y + .075, W + .08, .27), (0, hd - .075, W + .08, .27), (-hw + .075, 0, .27, D + .08), (hw - .075, 0, .27, D + .08)):
    mb.box(cx, cy, zr + 1.05, sx, sy, .06, 2)
mb.box(-1.6, 4.0, zr + .15, 4.4, 2.2, .5, 0)          # tank base
mb.box(-2.0, 7.4, zr + .15, .9, .9, .25, 0)           # hatch frame (above the stair)
mb.box(-2.0, 7.4, zr + .4, .8, .8, .04, 3)            # hatch lid
for (vx, vy) in ((-4.5, -3.0), (4.5, -3.0), (-4.5, 3.0)):
    mb.cylinder(vx, vy, zr + .15, .05, .6, 10, 4)
for (dx, dy) in ((-hw + .3, hd + .06), (hw - .3, hd + .06)):
    mb.cylinder(dx, dy, .1, .05, zr + .05, 12, 4)
mesh("W2_home__roof", mb, ["concreto_aparente", "reboco_antigo", "concreto_pintado", "aco_pintado_cinza", "plastico_branco"], C["Shell"], bevel=.006, sa_layer="Architecture")
K = sa_detail.Kit(lib, C["Services"], parent=rootobj)
K.water_tank("W2_home__caixa_dagua_A", (-2.6, 4.0, zr + .65))
K.water_tank("W2_home__caixa_dagua_B", (-.6, 4.0, zr + .65))

# ---------------------------------------------------------------- windows and doors (detailed objects)
KO = sa_detail.Kit(lib, C["Openings"], parent=rootobj)
for f in range(NF):
    o = openings_by_floor[f]
    for a, b, zb, zt, kind, c in o["front"]:
        if kind == "window":
            KO.window_sliding(f"W2_home__win_front_F{f}_{c:+.1f}", b - a, zt - zb, (c, front_y, zb), 0.0, grille=(f == 0))
        else:
            KO.door_entrance_metal(f"W2_home__door_entrance", b - a, zt - zb, (c, front_y + .1, zb), 0.0)
    for a, b, zb, zt, kind, c in o["back"]:
        KO.window_sliding(f"W2_home__win_back_F{f}_{c:+.1f}", b - a, zt - zb, (c, hd, zb), math.pi, grille=(f == 0))
    for key, xs, rot in (("side_A", -hw, -math.pi / 2), ("side_B", hw, math.pi / 2)):
        for a, b, zb, zt, kind, s in o[key]:
            y = front_y + s if key == "side_A" else hd - s
            if kind == "basculante":
                KO.window_basculante(f"W2_home__basc_{key}_F{f}_{s:.1f}", b - a, zt - zb, (xs, y, zb), rot)
            else:
                KO.window_sliding(f"W2_home__win_{key}_F{f}_{s:.1f}", b - a, zt - zb, (xs, y, zb), rot, grille=(f == 0))

# ---------------------------------------------------------------- interior walls per floor (corridor, units, stair zone)
for f in range(NF):
    z0 = f * FH + .15
    z1 = (f + 1) * FH
    mb = sa_bl.MeshBuilder()
    # corridor walls with unit doors
    for xs in (cx0 - T_IN / 2, cx1 + T_IN / 2):
        ops = []
        for uy in (door_s, door_s - fy0 + by0):
            s = uy - (front_y + T_OUT)
            ops.append((s - door_w / 2 - .035, s + door_w / 2 + .035, z0, z0 + 2.135))
        wall_segment(mb, (xs, front_y + T_OUT), (xs, sy0), T_IN, z0, z1, ops, 0)
    # front/back unit separation and stair zone wall (with corridor opening)
    for xs0, xs1 in ((-hw + T_OUT, cx0 - T_IN), (cx1 + T_IN, hw - T_OUT)):
        wall_segment(mb, (xs0, fy1 + T_IN / 2), (xs1, fy1 + T_IN / 2), T_IN, z0, z1, [], 0)
        wall_segment(mb, (xs0, sy0), (xs1, sy0), T_IN, z0, z1, [], 0)
    mesh(f"W2_home__partitions_F{f:02d}", mb, ["parede_pintada"], C["Interior"], floor_index=f, sa_layer="Architecture")
    # corridor finishes: floor tile, ceiling lights, switch, extinguisher
    mb = sa_bl.MeshBuilder()
    mb.box((cx0 + cx1) / 2, (front_y + T_OUT + sy0) / 2, z0, cx1 - cx0, sy0 - front_y - T_OUT, .012, 0)
    mesh(f"W2_home__corridor_floor_F{f:02d}", mb, ["piso_ceramico_bege"], C["Interior"], floor_index=f)
    KI = sa_detail.Kit(lib, C["Interior"], parent=rootobj)
    for yy in (front_y + 3.0, (front_y + sy0) / 2 + 2.0):
        KI.ceiling_light(f"W2_home__corridor_light_F{f}_{yy:.1f}", (0, yy, z1 - .02))
    KI.switch(f"W2_home__corridor_switch_F{f}", (cx0 + .005, front_y + 1.0, f * FH + .15), math.pi / 2)
    KI.extinguisher(f"W2_home__extinguisher_F{f}", (cx1 - .005, sy0 - 1.2, f * FH + .15), -math.pi / 2)
    # unit doors (other units closed; Apto 12 door ajar)
    for ux_wall, sgn in ((cx0 - T_IN / 2, 1), (cx1 + T_IN / 2, -1)):
        for uy in (door_s, door_s - fy0 + by0):
            is12 = (f == hero["interior"]["floor_index"] and sgn == (1 if unit[0] < 0 else -1) and uy == door_s)
            KO.door(f"W2_home__unitdoor_F{f}_{ux_wall:+.1f}_{uy:+.1f}", door_w, 2.1, (ux_wall, uy, z0), math.pi / 2,
                    wall_t=T_IN, open_deg=(-70 if is12 else 0))

# Stair (one U-flight per storey) in the stair zone.
for f in range(NF - 1):  # the top floor reaches the roof through the hatch
    K.stair_u(f"W2_home__stair_F{f}", STAIR_W, STAIR_RUN, FH, (STAIR_ORIGIN[0], STAIR_ORIGIN[1], f * FH + .15), math.pi)

# ---------------------------------------------------------------- Apto 12 (floor_index) full interior
fi = hero["interior"]["floor_index"]
zf = fi * FH + .15
zc = (fi + 1) * FH
rooms = {r["role"]: Lrect(r["rect"]) for r in hero["interior"]["rooms"]}
mb = sa_bl.MeshBuilder()
ux0, uy0, ux1, uy1 = units["12_front_A"]
mb.box((ux0 + ux1) / 2, (uy0 + uy1) / 2, zf, ux1 - ux0, uy1 - uy0, .012, 0)
bx0, by0_, bx1, by1_ = rooms["bathroom"]
mb.box((bx0 + bx1) / 2, (by0_ + by1_) / 2, zf + .012, bx1 - bx0, by1_ - by0_, .006, 1)
mesh("W2_home__apto12_floor", mb, ["piso_ceramico_bege", "azulejo_branco"], C["Interior"], floor_index=fi, sa_layer="Architecture")
# bathroom and storage partitions (with door openings) + wall tiles
mb = sa_bl.MeshBuilder()
door_side = 1 if (bx0 + bx1) / 2 < (ux0 + ux1) / 2 else -1
inner_x = bx1 if door_side > 0 else bx0
wall_segment(mb, (inner_x, by0_), (inner_x, by1_), .1, zf, zc, [(abs(by1_ - by0_) / 2 - .35, abs(by1_ - by0_) / 2 + .35, zf, zf + 2.1)], 0)
inner_y = by1_ if (by0_ + by1_) / 2 < (uy0 + uy1) / 2 else by0_
wall_segment(mb, (bx0, inner_y), (bx1, inner_y), .1, zf, zc, [], 0)
sx0, sy0_, sx1, sy1_ = rooms["storage"]
st_inner_y = sy1_ if (sy0_ + sy1_) / 2 < (uy0 + uy1) / 2 else sy0_
wall_segment(mb, (sx0, st_inner_y), (sx1, st_inner_y), .08, zf, zf + 2.4, [(.1, (sx1 - sx0) - .1, zf, zf + 2.1)], 0)
st_inner_x = sx0 if (sx0 + sx1) / 2 > (ux0 + ux1) / 2 else sx1
wall_segment(mb, (st_inner_x, sy0_), (st_inner_x, sy1_), .08, zf, zf + 2.4, [], 0)
for (p0, p1) in (((bx1 - .006, by0_ + .05), (bx1 - .006, by1_)), ((bx0 + .05, by1_ - .006), (bx1, by1_ - .006)), ((bx0 + .05, by0_ + .056), (bx1, by0_ + .056))):
    wall_segment(mb, p0, p1, .012, zf, zf + 1.8, [], 1)
mesh("W2_home__apto12_partitions", mb, ["parede_pintada", "azulejo_branco"], C["Interior"], floor_index=fi, sa_layer="Architecture")
KA = sa_detail.Kit(lib, C["Interior"], parent=rootobj)
kx0, ky0, kx1, ky1 = rooms["kitchenette"]
along_x = (kx1 - kx0) >= (ky1 - ky0)
wall_side_y = ky0 if abs(ky0 - uy0) < abs(ky1 - uy1) else ky1
KA.kitchen_counter("W2_home__apto12_kitchenette", kx1 - kx0, (kx0, wall_side_y, zf), 0.0 if wall_side_y == ky1 else math.pi, sink_at=(kx1 - kx0) * .45)
# Wet core: toilet and sink on the back/inner walls, electric shower on the exterior wall under the basculante window.
KA.toilet("W2_home__apto12_toilet", (bx0 + .8, by1_ - .27, zf), 0.0)
KA.sink_pedestal("W2_home__apto12_sink", (bx0 + .75, by0_ + .18, zf), math.pi)
KA.shower_electric("W2_home__apto12_shower", (bx1, (by0_ + by1_) / 2, zf), -math.pi / 2)
# Entry wall is the corridor wall at ux0 (room towards +X): QDC and switch next to the door.
KA.panel_qdc("W2_home__apto12_qdc", (ux0 + .01, door_s - 1.0, zf), math.pi / 2)
for k, (px, py, rot, zz) in enumerate(((ux0 + .01, uy0 + 1.5, math.pi / 2, .3), (ux1 - .01, uy0 + 2.0, -math.pi / 2, .3),
                                       ((ux0 + ux1) / 2, uy0 + .01, math.pi, .3), (kx0 + .3, ky1 - .01, 0.0, 1.1), (ux0 + .6, uy0 + .01, math.pi, .3))):
    KA.outlet(f"W2_home__apto12_outlet_{k}", (px, py, zf), rot, z=zz)
KA.switch("W2_home__apto12_switch_entry", (ux0 + .01, door_s - .55, zf), math.pi / 2)
bulb = L(next(it for it in hero["interior"]["states"]["H0"] if it[0] == "bare_bulb")[1][:2])
KA.ceiling_light("W2_home__apto12_bulb", (bulb[0], bulb[1], zc - .02), bulb_only=True)
KA.ceiling_light("W2_home__apto12_bath_light", ((bx0 + bx1) / 2, (by0_ + by1_) / 2, zc - .02))
from sa_w2 import area_fill  # noqa: E402
# W3.1: soft daylight-bounce fill for the empty H0 flat (the bare bulb stays the only fixture in the hero)
area_fill(C["Lighting"], rootobj, "W2_home__apto12_fill", ((ux0 + ux1) / 2, (uy0 + uy1) / 2, zc - .1), (ux1 - ux0) * .7, (uy1 - uy0) * .7,
          (ux1 - ux0) * (uy1 - uy0) * 16.0, color=(1.0, .9, .78))
# W3.3: occupancy glow in the neighbouring units (Apto 12 stays the empty H0 flat): a warm/cool fill behind the front windows of the
# other flats so the building reads as inhabited; deterministic pattern, ~60% of the units lit, never the Apto 12 window
_OCC_TINTS = ((1.0, .84, .62), (1.0, .93, .80), (.86, .92, 1.0), (1.0, .78, .55))
for f_ in range(NF):
    for k_, sx_ in enumerate((1, -1)):
        if f_ == fi and sx_ > 0:
            continue
        if (f_ * 5 + k_ * 3 + 1) % 5 in (0, 3):
            continue
        cx_ = wx_front * sx_
        area_fill(C["Lighting"], rootobj, f"W2_home__occ_fill_F{f_}_{k_}", (cx_, front_y + 1.6, (f_ + 1) * FH - .12), 1.8, 2.4, 600.0,
                  color=_OCC_TINTS[(f_ + k_) % len(_OCC_TINTS)])
KA.skirting("W2_home__apto12_skirting", [((ux0, uy0 + .01), (ux1, uy0 + .01)), ((ux0 + .01, uy0), (ux0 + .01, uy1)), ((ux0, uy1 - .01), (ux1, uy1 - .01))])
KA.coll = C["Interior"]
# H0 props from the JSON slots (local positions), state H0 + permanent item
KP = sa_detail.Kit(lib, C["Props_H0"], parent=rootobj)
for name, (x, y, w, d, h) in hero["interior"]["states"]["H0"]:
    p = L((x, y))
    if name == "mattress_floor":
        KP.mattress("W2_home__H0_mattress", (p[0], p[1], zf + .012), math.pi / 2 if w > d else 0.0)
    elif name == "old_chair":
        KP.chair_old("W2_home__H0_chair", (p[0], p[1], zf + .012), .4)
    elif name == "boxes":
        KP.cardboard_box("W2_home__H0_box_a", .6, .45, .4, (p[0], p[1], zf + .012), .2)
        KP.cardboard_box("W2_home__H0_box_b", .45, .35, .3, (p[0] + .05, p[1] + .08, zf + .412), -.3, open_top=True)
        KP.cardboard_box("W2_home__H0_box_c", .5, .4, .35, (p[0] + .55, p[1] - .2, zf + .012), .9)
for name, (x, y, w, d, h) in hero["interior"]["permanent"]:
    p = L((x, y))
    KP.toolcase("W2_home__ALL_maleta_guto", (p[0], p[1], zf + .012), .3)
# State slot markers (H0-H4) as empties in local coordinates
for state, items in hero["interior"]["states"].items():
    for name, (x, y, w, d, h) in items:
        p = L((x, y))
        e = bpy.data.objects.new(f"W2_SLOT_home__{state}__{name}", None)
        e.empty_display_type = "CUBE"
        e.location = (p[0], p[1], zf + h / 2)
        e.scale = (max(w, .05) / 2, max(d, .05) / 2, max(h, .05) / 2)
        C["Gameplay"].objects.link(e)
        parented(e)
        sa_bl.props(e, facility_id="home.starter", sa_kind="state_slot", state=state, item=name, sa_layer="Gameplay")

# ---------------------------------------------------------------- facade life and wear (rule-based, deterministic)
mb = sa_bl.MeshBuilder()
for f, sx in ((1, -1), (2, 1), (3, -1), (3, 1)):
    x = wx_front * sx + 1.25 * sx
    z = f * FH + .55
    mb.box(x, front_y - .16, z, .78, .28, .55, 0)                    # condenser body
    mb.cylinder(x + .1, front_y - .305, z + .12, .2, .01, 20, 1)      # fan grille
    for k in (-.3, .3):
        mb.box(x + k, front_y - .12, z - .06, .04, .26, .06, 2)       # brackets
    mb.cylinder(x - .3, front_y - .03, .4, .012, z - .4, 8, 3)        # condensate hose down the facade
mesh("W2_home__facade_life", mb, ["plastico_branco", "aco_pintado_cinza", "metal_galvanizado", "borracha_preta", "ferrugem"], C["Shell"], bevel=.004,
     sa_layer="Props", note="Condensadoras e mangueiras (regras simples); manchas de escorrimento ficam para decals no W3")
# Exposed conduit feeding the H0 bare bulb (typical retrofit in old buildings)
mb = sa_bl.MeshBuilder()
mb.box((ux0 + bulb[0]) / 2, bulb[1], zc - .03, bulb[0] - ux0, .025, .02, 0)
mb.box(ux0 + .02, (bulb[1] + door_s - .55) / 2, zc - .03, .025, abs(bulb[1] - (door_s - .55)), .02, 0)
mb.box(ux0 + .02, door_s - .55, zf + 1.2, .025, .025, zc - zf - 1.2, 0)
mesh("W2_home__apto12_conduit", mb, ["plastico_branco"], C["Interior"], floor_index=fi, sa_layer="Infrastructure")

# ---------------------------------------------------------------- site: entrance, canopy, services, boundary, forecourt
mb = sa_bl.MeshBuilder()
mb.box(entrance_x, front_y - .75, 2.45, 2.4, 1.5, .12, 0)            # canopy slab
mb.box(entrance_x, front_y - 1.48, 2.37, 2.4, .04, .2, 1)            # drip edge
for k in range(2):
    mb.box(entrance_x, front_y - .3 - k * .3, -.2, 2.0 - k * .3, .3 + k * .3, .2 + (1 - k) * .17, 0)
mb.box(entrance_x + 1.0, front_y - .006, 2.0, .3, .012, .2, 2)       # house number plate
mesh("W2_home__entrance", mb, ["concreto_pintado", "concreto_aparente", "aco_inox"], C["Site"], bevel=.008, sa_layer="Architecture")
KS = sa_detail.Kit(lib, C["Site"], parent=rootobj)
KS.intercom("W2_home__intercom", (entrance_x - .95, front_y, 0), 0.0)
KS.mailboxes("W2_home__mailboxes", (entrance_x - 2.2, front_y, 0), 0.0, n=4)
KS.entrance_meter("W2_home__padrao_entrada", (entrance_x + 2.4, front_y, 0), 0.0, height=4.0)
KS.panel_qdc("W2_home__qdc_comum", (cx0 + .01, front_y + 2.2, .15), math.pi / 2)
lot_l = Lrect(hero["lot"])
fz = front_y - 6.0  # street-side edge of the forecourt (lot front + forecourt)
mb = sa_bl.MeshBuilder()
mb.box(0, (front_y + fz) / 2, -.25, W + 6, front_y - fz, .25, 0)
for pk in hero["parking"]:
    r = Lrect(pk["rect"])
    for xx in (r[0], r[2]):
        mb.box(xx, (r[1] + r[3]) / 2, 0, .1, r[3] - r[1], .006, 1)
    mb.box((r[0] + r[2]) / 2, max(r[1], r[3]) - .15, 0, r[2] - r[0] - .3, .15, .12, 2)
for xx in (-hw - 3, hw + 3):
    mb.box(xx, (front_y + fz) / 2, 0, .2, front_y - fz, .5, 3)
mesh("W2_home__forecourt", mb, ["calcada", "sinalizacao_viaria", "concreto", "reboco_antigo"], C["Site"], bevel=.004, sa_layer="Roads")
for (sx, sgn) in ((-hw - .2, -1), (hw + .2, 1)):
    mb = sa_bl.MeshBuilder()
    mb.box(sx + sgn * 1.4, (front_y + hd) / 2, -.2, 2.8, D, .2, 0)
    mesh(f"W2_home__side_passage_{'A' if sgn < 0 else 'B'}", mb, ["concreto_aparente"], C["Site"], sa_layer="Roads")

from sa_w2 import wear_pass  # noqa: E402
wear_pass(lib, C["Site"], rootobj, [(-hw, -hd, hw, hd, NF * FH)], entrances=[(entrance_x, front_y, "-y")],
          ground_rects=[Lrect(pk["rect"]) for pk in hero["parking"]], seed=5, prefix="W2_home__", facility="home.starter")
KL = sa_detail.Kit(lib, C["Site"], parent=rootobj)
KL.clothesline("W2_home__clothes_back", (-hw + 1.0, hd + 1.4), (hw - 1.0, hd + 1.4), 1.9, n=8, seed=9)
# ---------------------------------------------------------------- terrain patch under the lot, lights, cameras
sa_bl.sun_and_sky(scene, C["Lighting"], elevation_deg=34.0, azimuth_deg=330.0)
for o in C["Lighting"].objects:
    if o.type == "LIGHT" and o.data.type == "SUN":
        pass
cams = C["Cameras"]


def lcam(name, loc, target, lens):
    w = lambda p: fr.to_world(p)
    return sa_bl.camera(name, cams, w(loc), target=w(target), lens=lens, clip=(.05, 2000))


ux_c = (ux0 + ux1) / 2
lcam("CAM_W2_home_street", (2.5, front_y - 16, 1.7), (0, front_y, 5.5), 22)
lcam("CAM_W2_home_entrance", (entrance_x + 2.2, front_y - 3.6, 1.65), (entrance_x - .6, front_y, 1.6), 20)
lcam("CAM_W2_home_apto12_view", (ux0 + .35, door_s - .25, zf + 1.6), (ux1 - .6, uy0 + .6, zf + .9), 14)
lcam("CAM_W2_home_apto12_kitchen", (ux_c, uy0 + 1.4, zf + 1.6), (kx0 + (kx1 - kx0) / 2, wall_side_y, zf + .9), 18)
lcam("CAM_W2_home_corridor", (0, front_y + 1.0, fi * FH + 1.75), (0, sy0, fi * FH + 1.3), 18)
lcam("CAM_W2_home_roof", (hw + 6, hd + 8, zr + 7), (0, 2, zr + .8), 24)
cut = sa_bl.camera("CAM_W2_home_cutaway", cams, fr.to_world((ux_c, (uy0 + uy1) / 2, zf + 14)), rot=(0, 0, fr.rot), ortho=9.0, clip=(.05, 200))
scene.render.engine = "BLENDER_EEVEE"
try:
    scene.eevee.use_raytracing = True
    scene.eevee.ray_tracing_options.resolution_scale = "2"
except AttributeError:
    pass
captures = [
    ["w2_home_01_rua", "CAM_W2_home_street", 2400, 1350, []],
    ["w2_home_02_entrada", "CAM_W2_home_entrance", 2400, 1350, []],
    ["w2_home_03_apto12_interior", "CAM_W2_home_apto12_view", 2400, 1350, []],
    ["w2_home_04_apto12_cozinha_banheiro", "CAM_W2_home_apto12_kitchen", 2400, 1350, []],
    ["w2_home_05_corredor", "CAM_W2_home_corridor", 2400, 1350, []],
    ["w2_home_06_cobertura", "CAM_W2_home_roof", 2400, 1350, []],
    ["w2_home_07_corte_apto12", "CAM_W2_home_cutaway", 1800, 1800, ["W2_home__shell_F02", "W2_home__shell_F03", "W2_home__roof", "W2_home__caixa",
                                                                   "W2_home__partitions_F02", "W2_home__partitions_F03", "W2_home__stair_F02", "W2_home__stair_F03",
                                                                   "W2_home__corridor_light_F2", "W2_home__corridor_light_F3", "W2_home__unitdoor_F2", "W2_home__unitdoor_F3",
                                                                   "W2_home__win_front_F2", "W2_home__win_front_F3", "W2_home__win_back_F2", "W2_home__win_back_F3",
                                                                   "W2_home__win_side_A_F2", "W2_home__win_side_A_F3", "W2_home__win_side_B_F2", "W2_home__win_side_B_F3",
                                                                   "W2_home__basc_side_A_F2", "W2_home__basc_side_A_F3", "W2_home__basc_side_B_F2", "W2_home__basc_side_B_F3",
                                                                   "W2_home__extinguisher_F2", "W2_home__extinguisher_F3", "W2_home__corridor_floor_F02", "W2_home__corridor_floor_F03",
                                                                   "W2_home__corridor_switch_F2", "W2_home__corridor_switch_F3"]],
]
scene["sa_captures"] = json.dumps(captures)
scene["sa_hero"] = "home.starter"
scene["facility_stage"] = "W2 base de produção (não é arte final)"
# A small terrain plate so exterior shots have ground.
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -1.2, 70, 70, .95, 0)
mesh("W2_home__ground_plate", mb, ["terra"], C["CaptureOnly"], sa_layer="Terrain", note="só para capturas isoladas")
from sa_w2 import bake_interior_probe  # noqa: E402
bake_interior_probe(top, C["Lighting"], "home.starter", rootobj)
out = root / "ArtSource" / "Blender" / "World" / "OldTown" / "Heroes"
out.mkdir(parents=True, exist_ok=True)
blend = out / "W2_home_starter.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
print("W2 HOME GENERATED", blend.name, len(bpy.data.objects))
