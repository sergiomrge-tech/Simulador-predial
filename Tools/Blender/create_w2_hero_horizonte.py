"""W2 — Edifício Horizonte: production base of the 12-storey tower used by the prologue.

Run:
blender --background --factory-startup --python Tools/Blender/create_w2_hero_horizonte.py -- --root PROJECT_ROOT

Output: ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend (local frame under W2_horizonte_ROOT).
Modelled inside: ground floor (lobby/portaria, meters, gate room, core, pump room, cistern, trash room, ground garage),
the typical floor index 3 ("quarto andar" of the prologue: corridor, 4 apartment doors, technical panel) and the roof.
The other floors are shell + facade + curtains (apartments closed in W2). Upper-floor windows are a light per-floor mesh.
"""
import argparse
import math
import random
import sys
import zlib
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
from sa_w2 import HeroScene, light_window, partition_plan, text_mesh, wall_x, wall_y  # noqa: E402

H = HeroScene(root, "horizonte", "W2_horizonte")
hero, L, Lrect = H.hero, H.L, H.Lrect
W, D, hw, hd = H.W, H.D, H.hw, H.hd       # 30 x 40
NF, FH, GH = H.bld["floors"], H.bld["fh"], H.bld["ground_h"]
TF = hero["interior"]["typical_floor_index"]
P = "W2_horizonte__"
T = .2
rng = random.Random(zlib.crc32(b"horizonte-w2"))


def z0(f):
    return 0.0 if f == 0 else GH + (f - 1) * FH


def zh(f):
    return GH if f == 0 else FH


ZTOP = z0(NF)
gr = {r["role"]: Lrect(r["rect"]) for r in hero["interior"]["ground"]}
tf = {r["role"]: Lrect(r["rect"]) for r in hero["interior"]["typical_floor"]}
cor = tf["corridor"]
CY0, CY1 = cor[1], cor[3]                 # corridor band (local y)
core = gr["core_stair_elevator"]
CORE = (core[0], CY1, core[2], core[3])   # core starts at the corridor's north edge

# ---------------------------------------------------------------- facade openings per floor (local)
UNIT_X = (-hw, 0.0, hw)


def front_ops(f):
    if f == 0:
        lb = gr["lobby_portaria"]
        return [((lb[0] + lb[2]) / 2, lb[2] - lb[0] - 1.0, 0.0, 3.4, "glass"), (L(next(e["p"] for e in hero["entrances"] if e["role"] == "meters_room_external"))[0], .9, 0, 2.1, "door"),
                (11.5, 1.5, 1.1, 2.3, "win")]
    ops = []
    for s in (-1, 1):
        ops += [(8.0 * s, 2.4, 0.0, 2.2, "balcony"), (2.6 * s, 1.2, 1.1, 1.2, "win"), (13.2 * s, 1.0, 1.1, 1.2, "win")]
    return ops


def back_ops(f):
    if f == 0:
        return [(x, 4.0, .6, 2.6, "grille") for x in (-11.0, -5.5, 0.0)]
    ops = [(x * s, 1.2, 1.1, 1.2, "win") for s in (-1, 1) for x in (2.5, 7.5, 12.5)]
    ops += [(5.0 * s, .6, 1.5, .6, "win") for s in (-1, 1)]
    return ops


def side_ops(f, s):
    if f == 0:
        if s < 0:
            return [(3.5, 4.5, 0.0, 2.6, "garage")]
        return [(10.0, 1.0, 0, 2.1, "door"), (-17.0, 1.2, 1.1, 1.2, "win")]
    return [(y, 1.2, 1.1, 1.2, "win") for y in (-16.0, -11.0, 0.0, 5.0, 10.0, 15.0)]


# Stairwell footprint (local x0, x1, y0, y1), derived from the stair placement below: stair_u at (CORE[2] - .3, STAIR_Y0), width 1.15, run 3.0,
# landing 1.2, two lanes of 1.15 + .1 gap along -X from the stair origin.
STAIR_X1 = CORE[2] - .2
STAIR_X0 = CORE[2] - .3 - (2 * 1.15 + .1)
STAIR_Y0 = CORE[1] + 1.4       # 1.2 m arrival / entry landing between the core wall and the first riser (was .3 m: too narrow for a walker)
STAIR_Y1 = STAIR_Y0 + 3.0 + 1.2 + .05
STAIR_HOLE = (STAIR_X0, STAIR_X1, STAIR_Y0, STAIR_Y1)
STAIR_DOOR_W = 1.2             # 1.0 m left no steering margin for a .28 m capsule (+ .08 skin) between jamb and architrave
STAIR_DOOR_H = 2.4             # 2.1 m left .21 m over the 1.8 m controller: less than the controller's .3 m step lift, so it jammed under the lintel
STAIR_DOOR_OPEN_DEG = 90.0     # stair doors are authored propped open (a closed leaf blocks the only route; the game has no door interaction)

# ---------------------------------------------------------------- shell per floor (walls, slab, bands), light windows, curtains
CURTAINS = ["tecido_lencol", "tecido_colchao", "plastico_branco", "papelao", "parede_pintada"]
for f in range(NF):
    za, h = z0(f), zh(f)
    mb = sa_bl.MeshBuilder()
    mat_out = 3 if f == 0 else 0                                          # granite cladding on the ground floor
    fo = [(p, w, za + zb, za + zb + hh) for p, w, zb, hh, k in front_ops(f)]
    bo = [(p, w, za + zb, za + zb + hh) for p, w, zb, hh, k in back_ops(f)]
    so = {s: [(p, w, za + zb, za + zb + hh) for p, w, zb, hh, k in side_ops(f, s)] for s in (-1, 1)}
    wall_x(mb, -hd + T / 2, -hw, hw, T, za, za + h, fo, mat_out)
    wall_x(mb, hd - T / 2, -hw, hw, T, za, za + h, bo, mat_out)
    wall_y(mb, -hw + T / 2, -hd + T, hd - T, T, za, za + h, so[-1], mat_out)
    wall_y(mb, hw - T / 2, -hd + T, hd - T, T, za, za + h, so[1], mat_out)
    for c, axis, a, b, ops in ((-hd + T + .02, "x", -hw + T, hw - T, fo), (hd - T - .02, "x", -hw + T, hw - T, bo),
                               (-hw + T + .02, "y", -hd + T, hd - T, so[-1]), (hw - T - .02, "y", -hd + T, hd - T, so[1])):
        (wall_x if axis == "x" else wall_y)(mb, c, a, b, .04, za + .15, za + h, ops, 1)
    if f == 0:
        mb.box(0, 0, za, W - .05, D - .05, .15, 2, bottom=True)
    else:
        # Unity validation fix: the floor slab used to be one full-footprint box, so the U stair ran into the slab above it and the
        # building could not be climbed. The slab now has a stairwell opening that covers both flights and the turn landing
        # (the strip between the core wall and the first riser, y in [CORE y + .2, STAIR_Y0], stays as the arrival landing).
        sx0, sx1, sy0, sy1 = STAIR_HOLE
        mb.box((-hw + .025 + sx0) / 2, 0, za, sx0 + hw - .025, D - .05, .15, 2, bottom=True)                              # west of the opening
        mb.box((sx1 + hw - .025) / 2, 0, za, hw - .025 - sx1, D - .05, .15, 2, bottom=True)                              # east of the opening
        mb.box((sx0 + sx1) / 2, (-hd + .025 + sy0) / 2, za, sx1 - sx0, sy0 + hd - .025, .15, 2, bottom=True)              # south (corridor side)
        mb.box((sx0 + sx1) / 2, (sy1 + hd - .025) / 2, za, sx1 - sx0, hd - .025 - sy1, .15, 2, bottom=True)              # north
    if f > 0:
        for (cx, cy, sx, sy) in ((0, -hd - .04, W + .1, .08), (0, hd + .04, W + .1, .08), (-hw - .04, 0, .08, D + .1), (hw + .04, 0, .08, D + .1)):
            mb.box(cx, cy, za - .1, sx, sy, .25, 4)                       # floor band (friso) per storey
    H.mesh(P + f"F{f:02d}_shell", mb, [H.facade, "parede_pintada", "concreto_aparente", "granito", "concreto_pintado"], "Shell",
           floor_index=f, sa_layer="Architecture")
    if f == 0:
        continue
    mb = sa_bl.MeshBuilder()
    cur = sa_bl.MeshBuilder()
    for axis, c, sgn, ops in (("x", -hd, -1, front_ops(f)), ("x", hd, 1, back_ops(f)), ("y", -hw, -1, side_ops(f, -1)), ("y", hw, 1, side_ops(f, 1))):
        for p, w, zb, hh, kind in ops:
            light_window(mb, axis, c, p, w, za + zb, hh, sgn, 0, 1, 2)
            if kind == "balcony":
                continue
            r = rng.random()
            if r < .7:                                                    # curtain / blind behind the glass (closed apartments)
                cover = rng.uniform(.35, 1.0)
                m = 3 + rng.randrange(len(CURTAINS))
                ci = c - sgn * .3
                if axis == "x":
                    mb.box(p - w * (1 - cover) / 2 * rng.choice((-1, 1)), ci, za + zb + .05, w * cover, .02, hh - .05, m)
                else:
                    mb.box(ci, p - w * (1 - cover) / 2 * rng.choice((-1, 1)), za + zb + .05, .02, w * cover, hh - .05, m)
    # unseen apartment interiors: dark back plane 2.5 m behind the openings keeps windows from reading as empty floors
    for axis, c, sgn in (("x", -hd, -1), ("x", hd, 1)):
        cur.box(0, c - sgn * 2.6, za + .15, W - 1, .05, FH - .2, 0)
    for axis, c, sgn in (("y", -hw, -1), ("y", hw, 1)):
        if f != TF:
            cur.box(c - sgn * 2.6, 0, za + .15, .05, D - 6, FH - .2, 0)
    H.mesh(P + f"F{f:02d}_windows", mb, ["aluminio", "vidro", "granito"] + CURTAINS, "Openings", floor_index=f, sa_layer="Architecture",
           lod="LOD0-light (janelas leves mescladas por andar)")
    if True:
        H.mesh(P + f"F{f:02d}_interior_mask", cur, ["parede_pintada"], "Interior", floor_index=f, sa_layer="Architecture",
               note="plano interno provisório: apartamentos fechados no W2")

# ---------------------------------------------------------------- balconies (front), with per-unit variation
for f in range(1, NF):
    za = z0(f)
    mb = sa_bl.MeshBuilder()
    for s in (-1, 1):
        x0, x1 = 8.0 * s - 3.0, 8.0 * s + 3.0
        mb.box(8.0 * s, -hd - .7, za, 6.2, 1.4, .15, 0, bottom=True)                       # cantilever slab
        enclosed = rng.random() < .3
        mb.box(8.0 * s, -hd - 1.37, za + .15, 6.2, .12, .95, 1)                           # tiled parapet (pastilha)
        for x in (x0 - .04, x1 + .04):
            mb.box(x, -hd - .7, za + .15, .12, 1.4, .95, 1)
        mb.box(8.0 * s, -hd - 1.37, za + 1.1, 6.3, .16, .05, 2)                           # aluminium handrail
        if enclosed:                                                                       # glazed retrofit, common in old towers
            mb.box(8.0 * s, -hd - 1.35, za + 1.15, 6.1, .02, 1.6, 3)
            for k in range(6):
                mb.box(x0 + k * 1.2, -hd - 1.35, za + 1.15, .04, .05, 1.6, 2)
        if rng.random() < .6:                                                              # condenser on the balcony
            cx = 8.0 * s + rng.choice((-2.3, 2.3))
            mb.box(cx, -hd - .45, za + .15, .78, .3, .55, 4)
        if rng.random() < .5:                                                              # potted plants
            for k in range(rng.randint(1, 3)):
                px = x0 + .4 + k * .5
                mb.cylinder(px, -hd - 1.15, za + .15, .16, .35, 12, 5)
                mb.cylinder(px, -hd - 1.15, za + .5, .2, .25, 10, 6)
        if rng.random() < .4:                                                              # clothes rack
            mb.box(8.0 * s + 1.0, -hd - .8, za + .15, 1.4, .02, 1.0, 2)
    H.mesh(P + f"F{f:02d}_balconies", mb, ["concreto_pintado", H.facade, "aluminio", "vidro", "plastico_branco", "ceramica_telha", "folhagem"],
           "Shell", bevel=.004, floor_index=f, sa_layer="Architecture")

# ---------------------------------------------------------------- core: walls on every floor, stair, elevator shafts
for f in range(NF):
    za, h = z0(f), zh(f)
    mb = sa_bl.MeshBuilder()
    open_floor = f in (0, TF)
    elev = [(-2.9, 1.0, za + .15, za + 2.25), (-1.0, 1.0, za + .15, za + 2.25)] if open_floor else []
    stair_door = [(2.6, STAIR_DOOR_W, za + .15, za + .15 + STAIR_DOOR_H + .05)] if open_floor else []
    wall_x(mb, CORE[1] + .1, CORE[0], CORE[2], .2, za + .15, za + h, elev + stair_door, 0)
    wall_x(mb, CORE[3] - .1, CORE[0], CORE[2], .2, za + .15, za + h, [], 0)
    wall_y(mb, CORE[0] + .1, CORE[1], CORE[3], .2, za + .15, za + h, [], 0)
    wall_y(mb, CORE[2] - .1, CORE[1], CORE[3], .2, za + .15, za + h, [], 0)
    wall_y(mb, 1.25, CORE[1] + .2, CORE[3] - .2, .15, za + .15, za + h, [], 0)          # stair / lift separation
    wall_y(mb, -1.95, CORE[1] + .2, CORE[1] + 2.6, .1, za + .15, za + h, [], 0)          # between the two shafts
    H.mesh(P + f"F{f:02d}_core", mb, ["concreto_pintado"], "Structure", floor_index=f, sa_layer="Architecture")
K = H.kit("Structure")
for f in range(NF - 1):
    K.stair_u(P + f"stair_F{f:02d}", 1.15, 3.0, zh(f), (CORE[2] - .3, STAIR_Y0, z0(f) + .15), math.pi / 2, steps_per_flight=12 if f == 0 else 9, hollow=True)
for f in (0, TF):
    za = z0(f)
    mb = sa_bl.MeshBuilder()
    for x in (-2.9, -1.0):
        mb.box(x, CORE[1] - .02, za + .15, 1.2, .05, 2.25, 0)                              # stainless door surround
        mb.box(x - .225, CORE[1] - .05, za + .15, .45, .02, 2.1, 1)                         # two leaves
        mb.box(x + .225, CORE[1] - .05, za + .15, .45, .02, 2.1, 1)
        mb.box(x + .75, CORE[1] - .05, za + 1.15, .08, .02, .14, 2)                         # call button panel
        mb.box(x, CORE[1] - .05, za + 2.45, .3, .02, .12, 2)                                # floor indicator
    H.mesh(P + f"F{f:02d}_elevator_doors", mb, ["aco_inox", "aco_inox", "plastico"], "Openings", bevel=.003, floor_index=f, sa_kind="elevator_door")
    H.kit("Openings").door(P + f"F{f:02d}_stair_door", STAIR_DOOR_W - .08, STAIR_DOOR_H, (2.6, CORE[1] + .1, za + .15), 0.0, wall_t=.2, leaf_mat="aco_pintado_cinza",
                           open_deg=-STAIR_DOOR_OPEN_DEG)       # hinged on the west jamb, leaf propped open toward the corridor: the stair landing side stays free (~.9 m remain between leaf tip and corridor wall)

# ---------------------------------------------------------------- ground floor rooms
G_WALLED = ("lobby_portaria", "meters_room", "gate_intercom_room", "shaft_plumbing", "shaft_electrical", "pump_room", "cistern_lower", "trash_room")
lb = gr["lobby_portaria"]
edges, doors = partition_plan(gr, G_WALLED, hw, hd, T, door_override={
    "lobby_portaria": ("x", lb[3], 0.0, 3.0), "shaft_plumbing": ("y", gr["shaft_plumbing"][0], 0.0, .7),
    "shaft_electrical": ("y", gr["shaft_electrical"][2], -.5, .7), "cistern_lower": None})
mb = sa_bl.MeshBuilder()
for axis, c, a, b in edges:
    ops = [(p, w + .07, .15, 2.15 + (.85 if w > 2 else 0)) for ax, cc, p, w, _ in doors if ax == axis and abs(cc - c) < .3 and a < p < b]
    (wall_x if axis == "x" else wall_y)(mb, c, a, b, .14, .15, GH, ops, 0)
for x in (CORE[0] - .07, CORE[2] + .07):                                                    # hall between lobby and core
    wall_y(mb, x, lb[3], CORE[1], .14, .15, GH, [], 0)
H.mesh(P + "F00_partitions", mb, ["parede_pintada"], "Interior", floor_index=0, sa_layer="Architecture")
KO = H.kit("Openings")
for axis, c, p, w, r in doors:
    if w > 1.5:
        continue
    loc = (p, c, .15) if axis == "x" else (c, p, .15)
    KO.door(P + f"F00_door_{r}", w, 2.1, loc, 0.0 if axis == "x" else math.pi / 2, wall_t=.14, leaf_mat="aco_pintado_cinza" if "shaft" in r or "pump" in r else "madeira_pintada")
# lobby: granite floor, glazed front with double door, portaria desk, mailboxes, intercom panel, ceiling lights
mb = sa_bl.MeshBuilder()
mb.box((lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2, .15, lb[2] - lb[0], lb[3] - lb[1], .01, 0)
mb.box(0, (lb[3] + CORE[1]) / 2, .15, CORE[2] - CORE[0], CORE[1] - lb[3], .01, 0)
gx0, gx1 = lb[0] + .5, lb[2] - .5
for k in range(7):
    x = gx0 + k * (gx1 - gx0) / 6
    mb.box(x, -hd + .1, 0, .08, .15, 3.4, 1)                                                 # mullions
mb.box(0, -hd + .1, 3.35, gx1 - gx0, .15, .1, 1)
mb.box(0, -hd + .1, .0, gx1 - gx0, .15, .1, 1)
for k in range(6):
    x = gx0 + (k + .5) * (gx1 - gx0) / 6
    if abs(x) > 1.2:
        mb.box(x, -hd + .1, .1, (gx1 - gx0) / 6 - .1, .012, 3.25, 2)
mb.box(-.45, -hd + .1, .1, .85, .03, 2.3, 2)                                                  # double glass door
mb.box(.45, -hd + .1, .1, .85, .03, 2.3, 2)
mb.box(-.45, -hd + .1, 2.4, 1.8, .03, .95, 2)
mb.box(-.1, -hd + .02, 1.0, .03, .05, .3, 3)
mb.box(.1, -hd + .02, 1.0, .03, .05, .3, 3)
desk = (lb[2] - 2.0, lb[1] + 4.5)
mb.box(desk[0], desk[1], .16, 2.6, .7, 1.05, 4)                                              # portaria desk
mb.box(desk[0], desk[1], 1.21, 2.8, .8, .04, 5)
mb.box(desk[0] + .5, desk[1] + .2, 1.25, .45, .35, .32, 6)                                   # CCTV monitor
H.mesh(P + "F00_lobby", mb, ["granito", "aluminio", "vidro", "aco_inox", "madeira_pintada", "granito", "plastico"], "Interior", bevel=.004,
       floor_index=0, sa_layer="Architecture")
KS = H.kit("Services")
KS.mailboxes(P + "F00_mailboxes_a", (lb[0] + .01, lb[1] + 6.5, .15), math.pi / 2, n=12, z=1.0)
KS.mailboxes(P + "F00_mailboxes_b", (lb[0] + .01, lb[1] + 6.5, .15), math.pi / 2, n=12, z=1.36)
KS.chair_old(P + "F00_portaria_chair", (desk[0], desk[1] + .9, .15), 3.0)
for k, (x, y) in enumerate(((-3, -16), (3, -16), (-3, -11), (3, -11), (0, -6))):
    KS.ceiling_light(P + f"F00_lobby_light_{k}", (x, y, GH - .02))
KS.extinguisher(P + "F00_extinguisher", (CORE[0], CORE[1] - 2.0, .15), math.pi / 2)
# meters room: meter bank (one cabinet per unit, 4 per floor x 11 floors + common), main board
mr = gr["meters_room"]
mb = sa_bl.MeshBuilder()
for row in range(4):
    for col in range(12):
        x = mr[0] + .6 + col * .45
        mb.box(x, mr[3] - .12, .5 + row * .55, .4, .22, .48, 0)
        mb.box(x, mr[3] - .235, .62 + row * .55, .16, .01, .14, 1)
mb.box(mr[2] - .8, mr[3] - .2, .3, .9, .4, 2.0, 2)                                             # general board
for k in range(5):
    mb.cylinder(mr[0] + .8 + k * 1.1, mr[3] - .1, 2.6, .04, 1.4, 10, 3)                        # risers to the electrical shaft
H.mesh(P + "F00_meter_bank", mb, ["aco_pintado_cinza", "vidro", "aco_pintado_cinza", "metal_galvanizado"], "Services", bevel=.003, floor_index=0,
       sa_kind="meter_bank", interactive=True, gameplay="sala de medidores (48 medições + quadro geral)")
KS.ceiling_light(P + "F00_meters_light", ((mr[0] + mr[2]) / 2, (mr[1] + mr[3]) / 2, GH - .02))
# pump room: two pumps on a plinth, manifold, valves, panel (prologue/chapter II pump contract)
pr = gr["pump_room"]
mb = sa_bl.MeshBuilder()
mb.box((pr[0] + pr[2]) / 2, pr[3] - 1.3, .15, 3.6, 1.2, .15, 0)                                # inertia plinth
for k, x in enumerate((pr[0] + 2.2, pr[0] + 4.4)):
    y = pr[3] - 1.3
    mb.cylinder(x, y, .3, .22, .55, 20, 1)                                                     # motor
    mb.box(x, y - .45, .3, .3, .35, .4, 1)                                                     # volute
    mb.cylinder(x, y - .75, .45, .06, 1.9, 14, 2)                                              # discharge riser
    mb.box(x, y - .75, 1.1, .2, .2, .12, 3)                                                    # valve body
    mb.cylinder(x, y - .75, 1.25, .1, .02, 16, 3)                                              # handwheel
mb.box((pr[0] + pr[2]) / 2 + 1.1, pr[3] - 2.05, 2.35, 2.4, .12, .12, 2)                        # manifold
mb.cylinder(pr[0] + 1.0, pr[3] - .3, .15, .08, GH - .3, 14, 2)                                 # suction from the cistern
mb.box(pr[0] + .02, pr[1] + 1.6, 1.0, .25, .6, .8, 4)                                          # pump control panel
mb.box(pr[0] + .16, pr[1] + 1.6, 1.25, .02, .3, .2, 5)
H.mesh(P + "F00_pump_set", mb, ["concreto", "aco_pintado_verde", "metal_galvanizado", "aco_pintado_vermelho", "aco_pintado_cinza", "vidro"], "Services",
       bevel=.004, floor_index=0, sa_kind="pump_set", interactive=True, gameplay="casa de bombas (recalque, contrato preventivo)")
KS.ceiling_light(P + "F00_pump_light", ((pr[0] + pr[2]) / 2, (pr[1] + pr[3]) / 2, GH - .02))
ci = gr["cistern_lower"]
mb = sa_bl.MeshBuilder()
mb.box((ci[0] + ci[2]) / 2, (ci[1] + ci[3]) / 2, .15, ci[2] - ci[0] - .3, ci[3] - ci[1] - .3, 1.6, 0)
mb.box((ci[0] + ci[2]) / 2, (ci[1] + ci[3]) / 2, 1.75, .8, .8, .05, 1)
H.mesh(P + "F00_cistern", mb, ["concreto_aparente", "aco_pintado_cinza"], "Services", floor_index=0, sa_kind="cistern", gameplay="reservatório inferior")
tr = gr["trash_room"]
for k in range(3):
    mb = sa_bl.MeshBuilder()
    mb.box(0, 0, .2, .7, .6, .9, 0)
    mb.box(0, 0, 1.1, .74, .64, .05, 1)
    for x in (-.25, .25):
        mb.cylinder(x, -.3, .05, .1, .05, 12, 2)
    o = H.mesh(P + f"F00_bin_{k}", mb, ["plastico_azul" if k else "aco_pintado_verde", "plastico", "borracha_preta"], "Services", bevel=.01, sa_layer="Props")
    o.location = (tr[0] + .6 + k * .8, tr[3] - .5, .15)
# ground garage: columns, stall lines, ramp opening; driveway outside
mb = sa_bl.MeshBuilder()
gx_end = pr[0]
for x in (-hw + 5.5, -hw + 11.0, -hw + 16.5):
    for y in (12.0, 17.5):
        mb.box(x, y, .15, .4, .4, GH - .15, 0)
for k in range(9):
    x = -hw + .5 + k * 2.6
    if x < gx_end - .3:
        mb.box(x, (hd - 5.2 + hd) / 2, .15, .08, 5.0, .004, 1)
mb.box(-hw + 11.0, 10.0, .15, 22.0, .1, .004, 2)
H.mesh(P + "F00_garage", mb, ["concreto_pintado", "sinalizacao_viaria", "pintura_industrial"], "Interior", floor_index=0, sa_layer="Architecture")

# ---------------------------------------------------------------- typical floor (index TF): corridor of the prologue
za = z0(TF) + .15
mb = sa_bl.MeshBuilder()
door_ops = {}
for role, r in tf.items():
    if role.startswith("apartment_door"):
        y = CY0 if abs(r[1] - CY0) < abs(r[1] - CY1) else CY1
        door_ops.setdefault(y, []).append(((r[0] + r[2]) / 2, .9 + .07, za, za + 2.135))
for y, ops in door_ops.items():
    off = -.07 if y == CY0 else .07
    if y == CY1:
        wall_x(mb, y + off, cor[0], CORE[0], .14, za, za + FH - .15, [o for o in ops if o[0] < CORE[0]], 0)
        wall_x(mb, y + off, CORE[2], cor[2], .14, za, za + FH - .15, [o for o in ops if o[0] > CORE[2]], 0)
    else:
        wall_x(mb, y + off, cor[0], cor[2], .14, za, za + FH - .15, ops, 0)
for x in (cor[0] - .07, cor[2] + .07):
    wall_y(mb, x, CY0 - .14, CY1 + .14, .14, za, za + FH - .15, [], 0)
mb.box((cor[0] + cor[2]) / 2, (CY0 + CY1) / 2, za, cor[2] - cor[0], CY1 - CY0, .01, 1)          # corridor floor tiles
H.mesh(P + f"F{TF:02d}_corridor", mb, ["parede_pintada", "piso_ceramico_bege"], "Interior", floor_index=TF, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
mb.box((cor[0] + cor[2]) / 2, (CY0 + CY1) / 2, za + FH - .45, cor[2] - cor[0], CY1 - CY0, .02, 0, top=False, bottom=True)
H.mesh(P + f"F{TF:02d}_ceiling_corridor", mb, ["parede_pintada"], "Interior", floor_index=TF, sa_layer="Architecture", note="forro rebaixado (oculto no corte)")
KC = H.kit("Interior")
for role, r in tf.items():
    if role.startswith("apartment_door"):
        y = CY0 if abs(r[1] - CY0) < abs(r[1] - CY1) else CY1
        n = role[-1]
        KO.door(P + f"F{TF:02d}_apto_{TF + 1}{n}", .9, 2.1, ((r[0] + r[2]) / 2, y + (-.07 if y == CY0 else .07), za), 0.0, wall_t=.14)
        plate = text_mesh(P + f"F{TF:02d}_apto_{TF + 1}{n}_number", f"{TF + 1}0{n}", .09, H.C["Interior"], H.lib["aco_inox"], extrude=.002)
        plate.parent = H.rootobj
        sgn = 1 if y == CY0 else -1
        plate.location = ((r[0] + r[2]) / 2 + .7, y + sgn * .005, za + 1.5)
        plate.rotation_euler = (math.pi / 2, 0, math.pi if sgn > 0 else 0)
for k, x in enumerate((-10.0, -4.0, 4.0, 10.0)):
    KC.ceiling_light(P + f"F{TF:02d}_corridor_light_{k}", (x, (CY0 + CY1) / 2, za + FH - .47))
q = tf["quadro_tecnico"]
qx = (q[0] + q[2]) / 2
mb = sa_bl.MeshBuilder()                                                                       # technical panel cabinet (fictional, simplified)
mb.box(0, -.09, 1.0, .7, .18, 1.0, 0)
mb.box(0, -.185, 1.03, .66, .012, .94, 1)                                                      # door
mb.box(.27, -.2, 1.45, .03, .02, .1, 2)                                                        # lock
mb.box(0, -.192, 1.75, .25, .005, .07, 3)                                                      # warning label
mb.box(0, -.06, 2.0, .12, .12, FH - 2.15, 4)                                                   # conduit to the shaft above
qd = H.mesh(P + f"F{TF:02d}_quadro_tecnico", mb, ["aco_pintado_cinza", "aco_pintado_cinza", "aco_inox", "pintura_industrial", "metal_galvanizado"],
            "Services", bevel=.003, floor_index=TF, sa_kind="technical_panel", interactive=True,
            gameplay="quadro técnico do quarto andar (prólogo: aquecimento, isolamento, teste, troca, restauração)")
qd.location = (qx, CY1, za)
KC.extinguisher(P + f"F{TF:02d}_extinguisher", (cor[0] + 1.5, CY1, za), 0.0)
mb = sa_bl.MeshBuilder()
mb.box(0, -.12, .9, .75, .24, .95, 0)                                                         # fire hose cabinet
mb.box(0, -.245, .95, .62, .01, .5, 1)
o = H.mesh(P + f"F{TF:02d}_hose_cabinet", mb, ["aco_pintado_vermelho", "vidro"], "Services", bevel=.003, floor_index=TF, sa_kind="fire_hose_cabinet")
o.location, o.rotation_euler = (cor[2] - 2.0, CY0, za), (0, 0, math.pi)
sign = text_mesh(P + f"F{TF:02d}_floor_sign", f"{TF + 1}º ANDAR", .16, H.C["Interior"], H.lib["concreto_pintado"], extrude=.003)
sign.parent = H.rootobj
sign.location, sign.rotation_euler = (-6.5, CY1 - .01, za + 1.8), (math.pi / 2, 0, 0)

# ---------------------------------------------------------------- roof
zr = ZTOP
mb = sa_bl.MeshBuilder()
mb.box(0, 0, zr, W, D, .2, 0, bottom=True)
for (cx, cy, sx, sy) in ((0, -hd + .1, W, .2), (0, hd - .1, W, .2), (-hw + .1, 0, .2, D), (hw - .1, 0, .2, D)):
    mb.box(cx, cy, zr + .2, sx, sy, 1.1, 1)
    mb.box(cx, cy, zr + 1.3, sx + .1 if sx > 1 else .32, sy + .1 if sy > 1 else .32, .06, 2)
rooms_roof = {r["role"]: r for r in hero["roof_items"]}
for role in ("machine_room", "reservatorio_superior"):
    r = Lrect(rooms_roof[role]["rect"])
    h = rooms_roof[role]["h"]
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, zr + .2, r[2] - r[0], r[3] - r[1], h, 3)
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, zr + .2 + h, r[2] - r[0] + .2, r[3] - r[1] + .2, .1, 2)
mr_ = Lrect(rooms_roof["machine_room"]["rect"])
mb.box((mr_[0] + mr_[2]) / 2, mr_[1] - .01, zr + .2, 1.0, .05, 2.1, 4)                         # machine room steel door
for k in range(6):
    mb.box(mr_[0] - .01, mr_[1] + 1.5 + k * .12, zr + 2.2, .04, .08, .5, 4)                    # louvres
rs = Lrect(rooms_roof["reservatorio_superior"]["rect"])
for k in range(12):
    mb.box(rs[2] + .25, rs[1] + 1.0, zr + .4 + k * .3, .5, .04, .04, 4)                        # ladder rungs
for x in (rs[2] + .02, rs[2] + .48):
    mb.box(x, rs[1] + 1.0, zr + .2, .04, .04, 3.9, 4)
hz = Lrect(rooms_roof["roof_hatch"]["rect"])
mb.box((hz[0] + hz[2]) / 2, (hz[1] + hz[3]) / 2, zr + .2, 1.0, 1.0, .5, 3)
mb.box((hz[0] + hz[2]) / 2, (hz[1] + hz[3]) / 2, zr + .7, 1.06, 1.06, .04, 4)
mb.cylinder(-hw + 1.0, hd - 1.0, zr + .2, .03, 6.0, 8, 5)                                       # lightning mast
for (x, y) in ((hw - 3.0, hd - 3.0), (hw - 5.0, hd - 2.0), (-hw + 4.0, -hd + 3.0)):
    mb.cylinder(x, y, zr + .2, .025, 2.5, 8, 5)                                                 # antennas
H.mesh(P + "roof", mb, ["borracha_preta", H.facade, "concreto_pintado", "concreto_aparente", "aco_pintado_cinza", "metal_galvanizado"], "Shell",
       bevel=.004, floor_index=NF, sa_layer="Architecture")

# ---------------------------------------------------------------- site: front wall, gates, canopy, forecourt, driveway, ramp
lot = Lrect(hero["lot"])
ent = {e["role"]: e for e in hero["entrances"]}
pg, vg, ic = L(ent["pedestrian_gate"]["p"]), L(ent["vehicle_gate"]["p"]), L(ent["intercom"]["p"])
mb = sa_bl.MeshBuilder()
fy = lot[1] + .15
gaps = [(pg[0], ent["pedestrian_gate"]["w"]), (vg[0], ent["vehicle_gate"]["w"])]
wall_x(mb, fy, lot[0], lot[2], .2, 0, .9, [(x, w, .9, .9) for x, w in gaps], 0)                 # low wall
for k in range(int((lot[2] - lot[0]) / .15)):
    x = lot[0] + .1 + k * .15
    if all(abs(x - gx) > w / 2 + .05 for gx, w in gaps):
        mb.box(x, fy, .9, .02, .02, 1.4, 1)                                                     # railings
mb.box((lot[0] + lot[2]) / 2, fy, 2.28, lot[2] - lot[0], .05, .04, 1)
for x in (lot[0] + .1, lot[2] - .1):
    wall_y(mb, x, lot[1], lot[3], .2, 0, 2.2, [], 2)                                            # side boundary walls
for gx, w in gaps:                                                                              # gate leaves (closed)
    for k in range(int(w / .12)):
        mb.box(gx - w / 2 + .06 + k * .12, fy - .05, .05, .025, .025, 2.2, 1)
    mb.box(gx, fy - .05, .05, w, .05, .06, 1)
    mb.box(gx, fy - .05, 2.2, w, .05, .06, 1)
cn = Lrect(hero["canopy"]["rect"])
mb.box((cn[0] + cn[2]) / 2, (cn[1] + cn[3]) / 2, hero["canopy"]["h"], cn[2] - cn[0], cn[3] - cn[1], .15, 3, bottom=True)
for x in (cn[0] + .2, cn[2] - .2):
    mb.cylinder(x, cn[1] + .2, 0, .1, hero["canopy"]["h"], 16, 4)
mb.box(0, (fy + -hd) / 2, -.2, cn[2] - cn[0] - 4.0, -hd - fy, .21, 5)                            # entrance path
for s in (-1, 1):
    x0, x1 = (lot[0] + 6.5, -2.0) if s < 0 else (2.0, lot[2] - .5)
    mb.box((x0 + x1) / 2, (fy + .3 + -hd - .3) / 2, -.2, x1 - x0, -hd - fy - .6, .35, 6)         # garden beds
dw = Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "driveway_to_garage"))
rp = Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "garage_ramp_down"))
mb.box((dw[0] + dw[2]) / 2, (dw[1] + rp[1]) / 2, -.2, dw[2] - dw[0], rp[1] - dw[1], .2, 7)
n = 12
for k in range(n):                                                                              # ramp down to the basement (-3 m)
    ya = rp[1] + k * (rp[3] - rp[1]) / n
    mb.box((rp[0] + rp[2]) / 2, ya + (rp[3] - rp[1]) / n / 2, -3.0 * (k + 1) / n - .2, rp[2] - rp[0] - .4, (rp[3] - rp[1]) / n + .02, .2, 7)
for x in (rp[0] + .1, rp[2] - .1):
    mb.box(x, (rp[1] + rp[3]) / 2, -3.2, .2, rp[3] - rp[1], 4.1, 2)
mb.box((lot[0] + lot[2]) / 2, (fy + lot[1]) / 2 - .4, -.2, lot[2] - lot[0], .8, .21, 5)
H.mesh(P + "site", mb, [H.facade, "aco_pintado_cinza", "reboco_antigo", "concreto_pintado", "aco_inox", "granito", "terra", "concreto"], "Site", bevel=.004,
       sa_layer="Roads")
KX = H.kit("Site")
KX.intercom(P + "intercom", (ic[0], fy - .1, 0), 0.0, z=1.35)
KX.entrance_meter(P + "padrao_entrada", (-hw + 1.5, -hd, 0), 0.0, height=3.6)
name = text_mesh(P + "name_letters", "EDIFÍCIO HORIZONTE", .32, H.C["Site"], H.lib["aco_inox"], extrude=.02)
name.parent = H.rootobj
name.location, name.rotation_euler = (0.0, cn[1] - .08, hero["canopy"]["h"] + .02), (math.pi / 2, 0, 0)
for k in range(10):                                                                             # shrubs in the beds (provisional proxies)
    x = rng.uniform(lot[0] + 7, lot[2] - 1)
    if abs(x) < 2.5:
        continue
    mb = sa_bl.MeshBuilder()
    mb.cylinder(0, 0, 0, rng.uniform(.3, .55), rng.uniform(.5, 1.0), 10, 0)
    o = H.mesh(P + f"shrub_{k}", mb, ["folhagem"], "Site", sa_layer="Vegetation", note="arbusto proxy (W3/W4)")
    o.location = (x, rng.uniform(fy + .8, -hd - 1.0), .15)
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -4.4, 120, 120, 4.0, 0)
H.mesh(P + "ground_plate", mb, ["terra"], "CaptureOnly", sa_layer="Terrain", note="só para capturas isoladas")
mb = sa_bl.MeshBuilder()
mb.box(0, lot[1] - 6.0, -.4, 120, 11.0, .35, 0)
H.mesh(P + "street_stub", mb, ["asfalto_gasto"], "CaptureOnly", sa_layer="Roads", note="trecho da Rua da Estação só para as capturas")

from sa_w2 import wear_pass  # noqa: E402
wear_pass(H.lib, H.C["Site"], H.rootobj, [(-hw, -hd, hw, hd, 14.0)], entrances=[(0.0, -hd, "-y")],
          ground_rects=[gr["pump_room"], (-hw + 1, 11.0, 7.0, hd - 1)], drive_lines=[((dw[0] + 3, lot[1] + 1), (dw[0] + 3, rp[1]))],
          seed=11, prefix=P, facility="horizonte")
KG = H.kit("Site")
for k, x in enumerate((-hw + 2.0, -hw + 7.2, -hw + 12.4, -hw + 17.6)):
    if k != 2:
        KG.car(P + f"garage_car_{k}", (x, 15.2, .15), math.pi / 2 + (k % 2) * math.pi, paint=k + 1)
# ---------------------------------------------------------------- state markers, lighting, cameras
H.empty(P + "GP_prologue_spawn_corridor", (cor[0] + 2.0, (CY0 + CY1) / 2, za + .9), (.6, .6, 1.8), sa_kind="spawn", note="entrada do jogador no corredor do prólogo")
H.empty(P + "GP_quadro_tecnico", (qx, CY1 - .3, za + 1.4), (.8, .4, 1.2), sa_kind="interaction", note="ponto de interação do prólogo")
sa_bl.sun_and_sky(H.scene, H.C["Lighting"], elevation_deg=36.0, azimuth_deg=210.0)
H.cam("CAM_W2_horizonte_street", (-14.0, lot[1] - 14.0, 1.7), (-2.0, -hd, 15.0), 16)
H.cam("CAM_W2_horizonte_gate", (pg[0] + 4.0, lot[1] - 4.5, 1.65), (pg[0] - 1.0, -hd, 2.6), 18)
H.cam("CAM_W2_horizonte_lobby", (lb[0] + .8, lb[1] + 1.2, 1.65), (lb[2] - 1.0, lb[3], 1.4), 15)
H.cam("CAM_W2_horizonte_corridor", (cor[0] + 1.0, (CY0 + CY1) / 2, za + 1.65), (cor[2], (CY0 + CY1) / 2, za + 1.3), 16)
H.cam("CAM_W2_horizonte_quadro", (qx - 1.4, CY0 + .35, za + 1.6), (qx, CY1, za + 1.3), 18)
H.cam("CAM_W2_horizonte_pumps", (pr[0] + .7, pr[1] + .6, 1.75), (pr[2] - 1.5, pr[3] - 1.2, .8), 15)
H.cam("CAM_W2_horizonte_meters", (mr[2] - .6, mr[1] + .6, 1.65), (mr[0] + 2.0, mr[3], 1.2), 15)
H.cam("CAM_W2_horizonte_roof", (hw + 10.0, -hd - 12.0, zr + 14.0), (0, 0, zr + 1.0), 22)
H.cam("CAM_W2_horizonte_aerial", (-55.0, -75.0, 55.0), (0, 0, 16.0), 26)
H.cutaway("CAM_W2_horizonte_cut_typical", (0.0, -2.0), z0(TF) + 20.0, 34.0)
H.cutaway("CAM_W2_horizonte_cut_ground", (0.0, 0.0), 30.0, 44.0)
above = lambda f0: [P + f"F{f:02d}_" for f in range(f0, NF)] + [P + "roof", P + f"stair_F{f0 - 1:02d}"] + [P + f"stair_F{f:02d}" for f in range(f0, NF)]
for name_, cam in (("w2_horizonte_01_rua", "CAM_W2_horizonte_street"), ("w2_horizonte_02_portao_interfone", "CAM_W2_horizonte_gate"),
                   ("w2_horizonte_03_portaria", "CAM_W2_horizonte_lobby"), ("w2_horizonte_04_corredor_4andar", "CAM_W2_horizonte_corridor"),
                   ("w2_horizonte_05_quadro_tecnico", "CAM_W2_horizonte_quadro"), ("w2_horizonte_06_casa_bombas", "CAM_W2_horizonte_pumps"),
                   ("w2_horizonte_07_medidores", "CAM_W2_horizonte_meters"), ("w2_horizonte_08_cobertura", "CAM_W2_horizonte_roof"),
                   ("w2_horizonte_09_aerea", "CAM_W2_horizonte_aerial")):
    H.capture(name_, cam)
H.capture("w2_horizonte_10_corte_4andar", "CAM_W2_horizonte_cut_typical", 2000, 2400, above(TF + 1) + [P + f"F{TF:02d}_corridor_light", P + f"F{TF:02d}_ceiling"])
H.capture("w2_horizonte_11_corte_terreo", "CAM_W2_horizonte_cut_ground", 2000, 2400, above(1) + [P + "F00_lobby_light", P + "F00_meters_light", P + "F00_pump_light",
                                                                                                   P + "name_letters", P + "site"])
H.save("W2_horizonte.blend")
