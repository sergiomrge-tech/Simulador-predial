"""W2 — Oficina Aurora (G0 state base): high-fidelity production base of the workshop shed.

Run:
blender --background --factory-startup --python Tools/Blender/create_w2_hero_garage.py -- --root PROJECT_ROOT

Output: ArtSource/Blender/World/OldTown/Heroes/W2_garage.blend (local frame under W2_garage_ROOT).
Data: oldtown_heroes_v1.json (rooms, entrances, parking, G0-G4 slots). G0 props are modelled; G1-G4 stay as slots.
"""
import argparse
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
from sa_w2 import HeroScene, text_mesh, wall_x, wall_y  # noqa: E402

H = HeroScene(root, "garage", "W2_garage")
hero, L, Lrect = H.hero, H.L, H.Lrect
W, D, hw, hd = H.W, H.D, H.hw, H.hd
FH = H.bld["fh"]            # 5.5 eave height
RISE = 1.1                  # ridge along local X at y=0 (10% pitch)
T = .25
P = "W2_garage__"

# ---------------------------------------------------------------- openings (local)
ent = {e["role"]: e for e in hero["entrances"]}
rx = L(ent["pedestrian_reception"]["p"])[0]
gx = L(ent["vehicle_gate_rollup"]["p"])[0]
gw, gh = ent["vehicle_gate_rollup"]["w"], ent["vehicle_gate_rollup"]["h"]
rear = L(ent["rear_storage_door"]["p"])
rooms = {r["role"]: Lrect(r["rect"]) for r in hero["interior"]["rooms"]}
front_ops = [(rx, 1.0, 0, 2.1), (gx, gw, 0, gh), (-14.0, 1.5, 1.0, 2.2), (-6.0, 1.6, 1.4, 2.6), (12.5, 1.2, 1.8, 2.6)]
back_ops = [(x, 3.0, 3.8, 4.8) for x in (-8.0, 0.0, 8.0)]
side_neg = [((rooms["office"][1] + rooms["office"][3]) / 2, 1.2, 1.0, 2.2), ((rooms["bathroom"][1] + rooms["bathroom"][3]) / 2, .6, 1.7, 2.2),
            (-7.5, 2.4, 3.8, 4.8), (2.5, 2.4, 3.8, 4.8)]
side_pos = [(rear[1], 1.0, 0, 2.1), (-1.5, 2.4, 3.8, 4.8), (2.5, 2.4, 3.8, 4.8)]

# ---------------------------------------------------------------- shell: outer walls (facade skin + painted inner skin + grey dado band)
mb = sa_bl.MeshBuilder()
wall_x(mb, -hd + .1, -hw, hw, .2, 0, FH + 1.7, front_ops, 0)      # front with parapet hiding the gable roof
wall_x(mb, hd - .1, -hw, hw, .2, 0, FH, back_ops, 0)
wall_y(mb, -hw + .1, -hd + .2, hd - .2, .2, 0, FH, side_neg, 0)
wall_y(mb, hw - .1, -hd + .2, hd - .2, .2, 0, FH, side_pos, 0)
# gable infill on the side walls (triangular prism from eave to ridge)
for x in (-hw + .1, hw - .1):
    a, b = x - .1, x + .1
    mb.add_face([(a, hd - .2, FH), (a, -hd + .2, FH), (a, 0.0, FH + RISE)], 0)
    mb.add_face([(b, -hd + .2, FH), (b, hd - .2, FH), (b, 0.0, FH + RISE)], 0)
    mb.add_face([(a, -hd + .2, FH), (a, 0, FH + RISE), (b, 0, FH + RISE), (b, -hd + .2, FH)], 0)
    mb.add_face([(a, 0, FH + RISE), (a, hd - .2, FH), (b, hd - .2, FH), (b, 0, FH + RISE)], 0)
# parapet cap, plinth and sign band (front)
mb.box(0, -hd + .1, FH + 1.7, W + .1, .3, .06, 2)
mb.box(0, -hd - .005, 0, W + .02, .03, .6, 3)
mb.box(0, hd + .005, 0, W + .02, .03, .6, 3)
mb.box(-hw - .005, 0, 0, .03, D + .02, .6, 3)
mb.box(hw + .005, 0, 0, .03, D + .02, .6, 3)
mb.box(-4.0, -hd - .02, FH + .3, 14.0, .04, 1.1, 4)                 # painted sign band (G0: faded)
for x in [-hw + .45 + k * (W - .9) / 6 for k in range(7)]:
    if all(abs(x - xc) > w / 2 + .3 for xc, w, _, _ in front_ops):
        mb.box(x, -hd - .05, .0, .5, .1, FH + 1.6, 0)                  # pilasters expressing the portal frames
mb.box(rx, -hd - .6, 2.5, 1.8, 1.2, .1, 2)                              # small canopy over the reception door
mb.box(0, -hd - .04, FH - .05, W + .02, .08, .12, 2)                    # drip moulding at eave level
H.mesh(P + "shell_outer", mb, [H.facade, "parede_pintada", "concreto_pintado", "concreto_aparente", "reboco_pintado"], "Shell", bevel=.006,
       sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
inner = [(-hd + .225, "x", -hw + .2, hw - .2, front_ops), (hd - .225, "x", -hw + .2, hw - .2, back_ops),
         (-hw + .225, "y", -hd + .25, hd - .25, side_neg), (hw - .225, "y", -hd + .25, hd - .25, side_pos)]
for c, axis, a, b, ops in inner:
    f = wall_x if axis == "x" else wall_y
    f(mb, c, a, b, .05, .15, FH, ops, 0)
    off = .03 if c < 0 else -.03
    f(mb, c + off, a, b, .012, .15, 1.2, ops, 1)
H.mesh(P + "shell_inner", mb, ["parede_pintada", "concreto_pintado"], "Shell", sa_layer="Architecture")
# floor slab: polished concrete, painted van bay outline, drain grate, forecourt threshold at the gate
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -.25, W - .1, D - .1, .4, 0, bottom=True)
vb = Lrect(next(p["rect"] for p in hero["parking"] if p["role"] == "utility_van_bay_inside"))
for (cx, cy, sx, sy) in (((vb[0] + vb[2]) / 2, vb[1], vb[2] - vb[0], .1), ((vb[0] + vb[2]) / 2, vb[3], vb[2] - vb[0], .1),
                         (vb[0], (vb[1] + vb[3]) / 2, .1, vb[3] - vb[1]), (vb[2], (vb[1] + vb[3]) / 2, .1, vb[3] - vb[1])):
    mb.box(cx, cy, .15, sx, sy, .004, 1)
mb.box((vb[0] + vb[2]) / 2, (vb[1] + vb[3]) / 2, .15, 1.2, .3, .006, 2)
mb.box(gx, -hd + .05, 0, gw + .2, .3, .155, 3)
H.mesh(P + "floor", mb, ["concreto", "pintura_industrial", "metal_galvanizado", "aco_pintado_cinza"], "Shell", sa_layer="Architecture")

# ---------------------------------------------------------------- structure: steel portal frames, purlins, roof sheets, gutter
def zroof(y):
    return FH + RISE * (1 - abs(y) / hd)


mb = sa_bl.MeshBuilder()
frames = [-hw + .45 + k * (W - .9) / 6 for k in range(7)]
for x in frames:
    for y in (-hd + .4, hd - .4):
        mb.box(x, y, .15, .2, .3, FH - .15, 0)
        mb.box(x, y, .15, .4, .4, .02, 0)                               # base plate
    n = 10
    for k in range(n):
        ya = -hd + .4 + k * (D - .8) / n
        yb = ya + (D - .8) / n
        mb.box(x, (ya + yb) / 2, (zroof(ya) + zroof(yb)) / 2 - .45, .16, (D - .8) / n + .02, .3, 0)
    mb.box(x, 0, FH - .7, .08, D - .8, .08, 0)                          # tie rod / lower chord
for y in [-hd + .6 + k * (D - 1.2) / 8 for k in range(9)]:
    mb.box(0, y, zroof(y) - .14, W - .5, .08, .12, 1)                   # galvanised purlins
H.mesh(P + "structure", mb, ["aco_pintado_cinza", "metal_galvanizado"], "Structure", bevel=.004, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
for s in (-1, 1):
    y0, y1 = 0.0, s * (hd + .35)
    for k in range(8):
        xa, xb = -hw - .1 + k * (W + .2) / 8, -hw - .1 + (k + 1) * (W + .2) / 8
        mat = 1 if (k in (2, 5) and s > 0) else 0                        # translucent skylight sheets
        z0, z1 = FH + RISE + .02, FH - .035 * 1
        q = [(xa, y0, z0), (xb, y0, z0), (xb, y1, z1), (xa, y1, z1)]
        mb.add_face(q if s > 0 else q[::-1], mat)
        mb.add_face([(v[0], v[1], v[2] - .02) for v in (q[::-1] if s > 0 else q)], 0)
mb.box(0, hd + .45, FH - .25, W + .2, .18, .16, 2)                       # gutter
mb.box(0, 0, FH + RISE, W + .2, .3, .05, 2)                             # ridge cap
for x in (-hw + .4, hw - .4):
    mb.cylinder(x, hd + .5, 0, .05, FH - .2, 12, 3)                      # downpipes
H.mesh(P + "roof", mb, ["telha_metalica", "plastico_branco", "metal_galvanizado", "aco_pintado_cinza"], "Structure", sa_layer="Architecture")

# ---------------------------------------------------------------- partitions (walled rooms 3 m high with a slab), doors
WALLED = ("reception", "office", "bathroom", "depot", "small_storage")
outer = lambda e: (e[0] == "x" and abs(abs(e[1]) - (hd - T)) < .35) or (e[0] == "y" and abs(abs(e[1]) - (hw - T)) < .35)
edges, doors = [], []
for r in WALLED:
    x0, y0, x1, y1 = rooms[r]
    cand = [("x", y0, x0, x1), ("x", y1, x0, x1), ("y", x0, y0, y1), ("y", x1, y0, y1)]
    cand = [e for e in cand if not outer(e)]
    best = min(cand, key=lambda e: math.hypot(*(((e[2] + e[3]) / 2, e[1]) if e[0] == "x" else (e[1], (e[2] + e[3]) / 2))))
    doors.append((best[0], best[1], (best[2] + best[3]) / 2, r))
    edges.extend(cand)
merged = []
for e in edges:
    axis, c, a, b = e
    segs = [(a, b)]
    for m in merged:
        if m[0] == axis and abs(m[1] - c) < .3:
            nxt = []
            for s0, s1 in segs:
                if m[3] <= s0 or m[2] >= s1:
                    nxt.append((s0, s1))
                    continue
                if m[2] > s0:
                    nxt.append((s0, m[2]))
                if m[3] < s1:
                    nxt.append((m[3], s1))
            segs = nxt
    merged.extend((axis, c, s0, s1) for s0, s1 in segs if s1 - s0 > .2)
mb = sa_bl.MeshBuilder()
ZP = 3.0
for axis, c, a, b in merged:
    ops = [(p, .9 + .07, 0, 2.1 + .035) for ax, cc, p, _ in doors if ax == axis and abs(cc - c) < .3 and a < p < b]
    (wall_x if axis == "x" else wall_y)(mb, c, a, b, .14, .15, ZP, ops, 0)
H.mesh(P + "partitions", mb, ["parede_pintada"], "Interior", sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
for r in WALLED:
    x0, y0, x1, y1 = rooms[r]
    mb.box((x0 + x1) / 2, (y0 + y1) / 2, ZP, x1 - x0 + .14, y1 - y0 + .14, .12, 0, bottom=True)
H.mesh(P + "room_ceilings", mb, ["concreto_aparente"], "Interior", sa_layer="Architecture", note="lajes dos ambientes fechados (oculta no corte)")
KO = H.kit("Openings")
for axis, c, p, r in doors:
    loc = (p, c, .15) if axis == "x" else (c, p, .15)
    KO.door(P + f"door_{r}", .9, 2.1, loc, 0.0 if axis == "x" else math.pi / 2, wall_t=.14, open_deg=(75 if r in ("office", "bathroom") else 0),
            leaf_mat="madeira_pintada")

# ---------------------------------------------------------------- openings: rollup gate, entrance door, windows
mb = sa_bl.MeshBuilder()
open_h = 1.6                                                             # G0: gate partly open
for k in range(int((gh - open_h) / .1)):
    z = open_h + k * .1
    mb.box(gx, -hd + .32, z, gw - .04, .025, .07, 0)
    mb.box(gx, -hd + .335, z + .07, gw - .04, .012, .03, 0)
mb.box(gx, -hd + .32, open_h - .06, gw - .04, .05, .06, 1)              # bottom bar
for x in (gx - gw / 2 - .04, gx + gw / 2 + .04):
    mb.box(x, -hd + .32, 0.15, .08, .1, gh, 1)                           # guides
mb.box(gx, -hd + .55, gh, gw + .4, .55, .6, 2)                           # drum box
mb.box(gx + gw / 2 + .25, -hd + .3, 1.2, .12, .06, .18, 3)               # padlock bracket
H.mesh(P + "rollup_gate", mb, ["metal_galvanizado", "aco_pintado_cinza", "metal_galvanizado", "ferrugem"], "Openings", bevel=.003,
       sa_kind="rollup_gate", interactive=True, state_G0="aberta parcialmente", gameplay="portão de enrolar (acesso de veículo)")
KO.door_entrance_metal(P + "door_reception", 1.0, 2.1, (rx, -hd + .1, 0), 0.0)
KO.door(P + "door_rear_storage", 1.0, 2.1, (hw - .125, rear[1], .15), math.pi / 2, wall_t=.25, leaf_mat="aco_pintado_cinza")
for xc, w, zb, zt in front_ops[2:]:
    KO.window_sliding(P + f"win_front_{xc:+.1f}", w, zt - zb, (xc, -hd, zb), 0.0, grille=True)
for xc, w, zb, zt in back_ops:  # clerestory strips
    KO.window_basculante(P + f"clerestory_back_{xc:+.1f}", w, zt - zb, (xc, hd, zb), math.pi)
for yc, w, zb, zt in side_neg:
    if zt - zb < .8:
        KO.window_basculante(P + f"basc_side_{yc:+.1f}", w, zt - zb, (-hw, yc, zb), -math.pi / 2)
    else:
        KO.window_sliding(P + f"win_side_{yc:+.1f}", w, zt - zb, (-hw, yc, zb), -math.pi / 2, grille=True)
for yc, w, zb, zt in side_pos[1:]:
    KO.window_basculante(P + f"clerestory_side_{yc:+.1f}", w, zt - zb, (hw, yc, zb), math.pi / 2)

# ---------------------------------------------------------------- services: lighting, power, water, plumbing
KS = H.kit("Services")
for x in (-4.0, 3.0, 10.0):
    for y in (-4.0, 4.0):
        lamp = KS.ceiling_light(P + f"lamp_{x:+.0f}_{y:+.0f}", (x, y, zroof(y) - .45), drop=.7)
        bpy.data.lights[lamp.name + "__light"].energy = 650
re = rooms["reception"]
KS.panel_qdc(P + "qdc_main", (re[0] + .01, re[1] + 2.6, .15), math.pi / 2, ways=12)
KS.entrance_meter(P + "padrao_entrada", (rx - 1.4, -hd, 0), 0.0, height=4.6)
KS.switch(P + "switch_reception", (rx + .75, -hd + .26, .15), math.pi)
bt = rooms["bathroom"]
KS.water_tank(P + "caixa_dagua", ((bt[0] + bt[2]) / 2 + .2, (bt[1] + bt[3]) / 2, ZP + .12))
KS.toilet(P + "toilet", (bt[0] + .5, bt[3] - .27, .15), 0.0)
KS.sink_pedestal(P + "sink", (bt[0] + 1.4, bt[3] - .15, .15), 0.0)
KS.ceiling_light(P + "bath_light", ((bt[0] + bt[2]) / 2, (bt[1] + bt[3]) / 2, ZP - .01))
ba = rooms["workshop_bench_area"]
mb = sa_bl.MeshBuilder()
mb.box((ba[0] + ba[2]) / 2, hd - .265, 3.2, ba[2] - ba[0], .03, .03, 0)  # surface conduit feeding the bench outlets
for k, x in enumerate((ba[0] + 1.0, ba[0] + 3.0, ba[0] + 5.0, ba[2] - 1.0)):
    mb.box(x, hd - .265, 1.1, .025, .03, 2.1, 0)
    KS.outlet(P + f"outlet_bench_{k}", (x, hd - .25, .15), 0.0, z=1.1)
H.mesh(P + "conduits", mb, ["metal_galvanizado"], "Services", sa_layer="Infrastructure")

# ---------------------------------------------------------------- G0 props (from the JSON slots)
KP = H.kit("Props_G0")
g0 = {n: L((x, y)) for n, (x, y, w, d, h) in hero["interior"]["states"]["G0"]}
b = g0["old_bench"]
KP.workbench(P + "G0_old_bench", 2.0, (b[0] - 1.0, hd - T - .33, .15), 0.0)
s = g0["single_shelf"]
KP.shelving(P + "G0_single_shelf", 1.8, (s[0] - .9, s[1], .15), 0.0, levels=4, h=1.9)
bx = g0["boxes"]
KP.cardboard_box(P + "G0_box_a", .6, .45, .4, (bx[0], bx[1], .15), .3)
KP.cardboard_box(P + "G0_box_b", .5, .4, .3, (bx[0] + .05, bx[1] + .05, .55), -.2, open_top=True)
KP.cardboard_box(P + "G0_box_c", .55, .4, .35, (bx[0] - .55, bx[1] + .2, .15), 1.1)
pc = g0["old_pc_folding_table"]
of = rooms["office"]
KP.folding_table(P + "G0_folding_table", (of[0] + .4, pc[1], .15), math.pi / 2)
KP.old_pc(P + "G0_old_pc", (of[0] + .35, pc[1] - .1, .9), math.pi / 2)
KP.chair_old(P + "G0_office_chair", (of[0] + 1.1, pc[1] + .2, .15), -1.3)
jb = g0["job_board"]
KP.job_board(P + "G0_job_board", (jb[0], of[1] - .075, .15), 0.0)
KP.chair_old(P + "G0_reception_chair", (re[0] + 1.2, re[1] + 1.4, .15), .6)
mg = L(hero["interior"]["permanent"][0][1][:2])
KP.toolcase(P + "ALL_maleta_guto", (mg[0] + .2, mg[1], .15), .2)
mb = sa_bl.MeshBuilder()
mb.box((re[0] + re[2]) / 2 + .6, re[1] + 3.2, .15, 2.2, .55, 1.05, 0)    # reception counter
mb.box((re[0] + re[2]) / 2 + .6, re[1] + 3.2, 1.2, 2.3, .65, .04, 1)
H.mesh(P + "G0_reception_counter", mb, ["madeira_pintada", "granito"], "Props_G0", bevel=.006, sa_kind="prop")
for k, (x, y) in enumerate(((hw + 2.5, -6.0), (hw + 3.2, -5.3), (hw + 2.4, 4.0))):
    mb = sa_bl.MeshBuilder()
    mb.cylinder(0, 0, 0, .29, .88, 20, 0)
    for z in (.28, .6):
        mb.cylinder(0, 0, z, .3, .03, 20, 0)
    o = H.mesh(P + f"yard_drum_{k}", mb, ["aco_pintado_verde" if k else "ferrugem"], "Site", bevel=.004, sa_layer="Props")
    o.location = (x, y, 0)
H.state_slots(z_of=lambda st, n: 3.0 if n == "mezzanine_reserve" else .15)

# ---------------------------------------------------------------- sign (G0 faded hand-painted), site
t = text_mesh(P + "sign_text", "OFICINA AURORA", .62, H.C["Shell"], H.lib["aco_pintado_verde"])
t.parent = H.rootobj
t.location = (-4.0, -hd - .045, FH + .55)
t.rotation_euler = (math.pi / 2, 0, 0)
sa_bl.props(t, facility_id="garage", sa_stage="W2", state="G0", note="letreiro pintado desbotado; o letreiro novo é o slot G4 facade_sign")
lot = Lrect(hero["lot"])
mb = sa_bl.MeshBuilder()
mb.box((lot[0] + lot[2]) / 2, (lot[1] - hd) / 2, -.2, lot[2] - lot[0], -hd - lot[1], .2, 0)       # concrete forecourt
for p in hero["parking"]:
    if p["kind"] != "car":
        continue
    r = Lrect(p["rect"])
    for x in (r[0], r[2]):
        mb.box(x, (r[1] + r[3]) / 2, 0, .1, r[3] - r[1], .005, 1)
    mb.box((r[0] + r[2]) / 2, r[1] + .3, 0, r[2] - r[0] - .4, .15, .12, 2)                       # wheel stop
ua = Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "utility_vehicle_access"))
for k in range(6):
    x = ua[0] + .3 + k * (ua[2] - ua[0] - .6) / 5
    mb.box(x, (ua[1] + ua[3]) / 2, 0, .2, ua[3] - ua[1] - .4, .005, 3)                           # keep-clear hatching
mb.box((lot[0] + lot[2]) / 2, lot[1] + .15, -.2, lot[2] - lot[0], .3, .35, 2)                      # curb line at the street
yard = Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "side_yard"))
mb.box((yard[0] + yard[2]) / 2, (yard[1] + yard[3]) / 2, -.2, yard[2] - yard[0], yard[3] - yard[1], .18, 4)
H.mesh(P + "forecourt", mb, ["concreto", "sinalizacao_viaria", "meio_fio", "pintura_industrial", "terra"], "Site", bevel=.004, sa_layer="Roads")
mb = sa_bl.MeshBuilder()
fx = yard[2] - .05
for k in range(int((yard[3] - yard[1]) / 2.5) + 1):
    mb.cylinder(fx, yard[1] + k * 2.5, 0, .03, 2.0, 8, 0)
mb.box(fx, (yard[1] + yard[3]) / 2, 1.95, .04, yard[3] - yard[1], .04, 0)
mb.box(fx, (yard[1] + yard[3]) / 2, .05, .01, yard[3] - yard[1], 1.85, 1)
mb.box((yard[0] + yard[2]) / 2, yard[1] + .05, .05, yard[2] - yard[0], .01, 1.85, 1)           # gate leaf to the forecourt
H.mesh(P + "yard_fence", mb, ["metal_galvanizado", "metal_galvanizado"], "Site", sa_layer="Props", note="tela de alambrado (malha final via alpha no W3)")
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -1.25, 90, 90, 1.0, 0)
H.mesh(P + "ground_plate", mb, ["terra"], "CaptureOnly", sa_layer="Terrain", note="só para capturas isoladas")

from sa_w2 import wear_pass  # noqa: E402
wear_pass(H.lib, H.C["Site"], H.rootobj, [(-hw, -hd, hw, hd, FH + 1.6)], entrances=[(rx, -hd, "-y"), (gx, -hd, "-y")],
          ground_rects=[vb, Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "side_yard"))],
          drive_lines=[((gx, -hd - 9.0), (gx, -hd + 6.0))], seed=7, prefix=P, facility="garage")
# ---------------------------------------------------------------- lighting, cameras, captures
sa_bl.sun_and_sky(H.scene, H.C["Lighting"], elevation_deg=34.0, azimuth_deg=250.0)
H.cam("CAM_W2_garage_street", (-3.0, -32.0, 1.7), (-1.0, -hd, 3.6), 20)
H.cam("CAM_W2_garage_gate", (7.5, -18.5, 1.65), (1.5, -hd, 2.2), 20)
H.cam("CAM_W2_garage_bay", (-7.0, -9.6, 1.65), (5.0, 8.0, 1.6), 15)
H.cam("CAM_W2_garage_reception", (re[2] - .4, re[1] + .5, 1.6), (re[0] + 2.0, re[3], 1.4), 15)
H.cam("CAM_W2_garage_office", (of[2] - .3, of[3] - .4, 1.6), (of[0], pc[1], .9), 16)
H.cam("CAM_W2_garage_bench", (b[0] - 2.5, b[1] - 5.5, 1.65), (b[0] + .5, hd, 1.1), 18)
H.cam("CAM_W2_garage_aerial", (-26.0, -36.0, 19.0), (0, 0, 3.0), 24)
H.cutaway("CAM_W2_garage_cutaway", (3.0, -4.0), 30.0, 44.0)
hide_roof = [P + "roof", P + "structure", P + "lamp_", P + "caixa", P + "room_ceilings", P + "bath_light"]
for name, cam, *rest in (("w2_garage_01_rua", "CAM_W2_garage_street"), ("w2_garage_02_portao", "CAM_W2_garage_gate"),
                         ("w2_garage_03_galpao", "CAM_W2_garage_bay"), ("w2_garage_04_recepcao_quadro", "CAM_W2_garage_reception"),
                         ("w2_garage_05_escritorio_pc", "CAM_W2_garage_office"), ("w2_garage_06_bancada", "CAM_W2_garage_bench"),
                         ("w2_garage_07_aerea", "CAM_W2_garage_aerial")):
    H.capture(name, cam)
H.capture("w2_garage_08_corte_G0", "CAM_W2_garage_cutaway", 2400, 1800, hide_roof)
H.save("W2_garage.blend")
