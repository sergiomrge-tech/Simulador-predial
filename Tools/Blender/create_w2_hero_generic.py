"""W2 — generic production base for the remaining Old Town heroes (item E of the W2 queue).

Run:
blender --background --factory-startup --python Tools/Blender/create_w2_hero_generic.py -- --root PROJECT_ROOT --hero <id>

Heroes: apartments, grocery, restaurant, workshop, smalloffice (any hero of oldtown_heroes_v1.json works).
Everything is derived from the JSON: building volumes (multi-wing), entrances (door / rollup / passage / site gate by role),
shopfront side, roof type, awning, secondary volumes, roof items, parking, service yards and ground-floor rooms. Rooms are
fitted out by role (quadro/meters/technical -> panels, salao -> shop shelving or tables, cozinha -> counters, banheiro ->
fixtures, workstations -> desks, boxes -> lifts/bench, reception -> counter). Upper floors are shell + light windows +
curtains (closed, like the Horizonte). Output: ArtSource/Blender/World/OldTown/Heroes/W2_<id>.blend
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
parser.add_argument("--hero", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
from sa_w2 import HeroScene, light_window, partition_plan, text_mesh, wall_x, wall_y  # noqa: E402

H = HeroScene(root, opts.hero, f"W2_{opts.hero}")
hero, L, Lrect = H.hero, H.L, H.Lrect
HID = hero["id"]
P = f"W2_{HID}__"
rng = random.Random(zlib.crc32(HID.encode()))
T = .25
DIRS = {"S": 0, "N": 1, "E": 2, "W": 3}


def local_side(world_dir):
    """World facing (N/S/E/W) -> local side name ('-y' front, '+y', '-x', '+x')."""
    v = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[world_dir]
    a = H.fr.to_local((H.fr.c[0] + v[0], H.fr.c[1] + v[1]))
    if abs(a[0]) > abs(a[1]):
        return "+x" if a[0] > 0 else "-x"
    return "+y" if a[1] > 0 else "-y"


blds = []
for b in hero["buildings"]:
    r = Lrect(b["rect"])
    blds.append(dict(b, r=r, H=b["ground_h"] + b["fh"] * (b["floors"] - 1), mat=H.fixed(b["facade"])))
shop_side = local_side(hero["buildings"][0]["shopfront"]) if hero["buildings"][0].get("shopfront") else None
ents = []
for e in hero["entrances"]:
    p = L(e["p"])
    ents.append(dict(e, lp=p, side=local_side(e["facing"])))


def side_line(r, side):
    x0, y0, x1, y1 = r
    return {"-y": ("x", y0, x0, x1), "+y": ("x", y1, x0, x1), "-x": ("y", x0, y0, y1), "+x": ("y", x1, y0, y1)}[side]


def covered(bi, side):
    """Intervals of a building side shared with another building (no openings there)."""
    axis, c, a, b = side_line(blds[bi]["r"], side)
    out = []
    for j, o in enumerate(blds):
        if j == bi:
            continue
        x0, y0, x1, y1 = o["r"]
        if axis == "x" and x0 - .3 <= c <= x1 + .3 and (abs(c - y0) < .6 or abs(c - y1) < .6 or y0 < c < y1):
            out.append((max(a, x0), min(b, x1)))
        if axis == "y" and y0 - .3 <= c <= y1 + .3 and (abs(c - x0) < .6 or abs(c - x1) < .6 or x0 < c < x1):
            out.append((max(a, y0), min(b, y1)))
    return [iv for iv in out if iv[1] - iv[0] > .5]


def ent_on(bi, side):
    axis, c, a, b = side_line(blds[bi]["r"], side)
    res = []
    for e in ents:
        p = e["lp"]
        u, v = (p[0], p[1]) if axis == "x" else (p[1], p[0])
        if abs(v - c) < .8 and a - .2 <= u <= b + .2:
            res.append((u, e))
    return res


def kind_of(e):
    role = e["role"]
    if "passage" in role:
        return "passage"
    if "gate" in role and "rollup" not in role:
        return "site_gate"
    if e.get("h") or any(k in role for k in ("box_", "loading", "rollup", "vehicle")):
        return "rollup"
    return "door"


# ---------------------------------------------------------------- shells
ROOM = {r["role"]: Lrect(r["rect"]) for r in hero.get("interior", {}).get("rooms", [])}
openings_log = []
for bi, b in enumerate(blds):
    x0, y0, x1, y1 = b["r"]
    nf, fh, gh, Hb = b["floors"], b["fh"], b["ground_h"], b["H"]
    zs_ = [0.0] + [gh + k * fh for k in range(nf - 1)]
    shell, wins = sa_bl.MeshBuilder(), sa_bl.MeshBuilder()
    for side in ("-y", "+y", "-x", "+x"):
        axis, c, a, bb = side_line(b["r"], side)
        out = -1 if side[0] == "-" else 1
        cov = covered(bi, side)
        ein = ent_on(bi, side)
        cline = c - out * T / 2
        L_ = bb - a
        n = max(1, int((L_ - 1.5) / 3.3))
        slots = [a + (k + .5) * L_ / n for k in range(n)]
        for f in range(nf):
            z0 = zs_[f]
            h = gh if f == 0 else fh
            ops = []
            if f == 0:
                for u, e in ein:
                    k = kind_of(e)
                    if k == "site_gate":
                        continue
                    w = e["w"]
                    hh = e.get("h", 2.6 if w > 1.4 else 2.1)
                    if k == "passage":
                        hh = e.get("h", 3.0)
                    ops.append((u, w, 0.0, min(hh, gh - .3), k, e))
                if side == shop_side and b is blds[0]:
                    taken = [(u - e["w"] / 2 - .4, u + e["w"] / 2 + .4) for u, e in ein]
                    s0 = a + .8
                    while s0 < bb - .8:
                        s1 = min(bb - .8, s0 + 3.0)
                        segs = [(s0, s1)]
                        for t0, t1 in taken:
                            segs = [q for s in segs for q in ((s[0], min(s[1], t0)), (max(s[0], t1), s[1])) if q[1] - q[0] > .6]
                        for q0, q1 in segs:
                            ops.append(((q0 + q1) / 2, q1 - q0, .5, gh - .7, "shopwin", None))
                        s0 = s1 + .4
            else:
                for u in slots:
                    if any(c0 - .8 < u < c1 + .8 for c0, c1 in cov):
                        continue
                    ops.append((u, 1.2, 1.0, 1.2, "win", None))
            if f == 0 and side != shop_side:
                for u in slots:
                    if any(c0 - .8 < u < c1 + .8 for c0, c1 in cov) or any(abs(u - o[0]) < o[1] / 2 + 1.0 for o in ops):
                        continue
                    ops.append((u, 1.2, 1.1, 1.2, "win_g", None))
            wops = [(u, w, z0 + zb, z0 + zb + hh) for u, w, zb, hh, _, _ in ops]
            (wall_x if axis == "x" else wall_y)(shell, cline, a, bb, T, z0, z0 + h, wops, 0)
            inner = cline - out * (T / 2 + .02)
            (wall_x if axis == "x" else wall_y)(shell, inner, a + .3, bb - .3, .04, z0 + .15, z0 + h, [(u - 0, w, z1, z2) for u, w, z1, z2 in wops], 1)
            for u, w, zb, hh, k, e in ops:
                openings_log.append((bi, side, f, k))
                if k in ("win", "win_g"):
                    light_window(wins, axis, c, u, w, z0 + zb, hh, out, 0, 1, 2)
                    if k == "win" and rng.random() < .65:
                        cov_ = rng.uniform(.4, 1.0)
                        ci = c - out * .3
                        if axis == "x":
                            wins.box(u, ci, z0 + zb + .05, w * cov_, .02, hh - .05, 3 + rng.randrange(3))
                        else:
                            wins.box(ci, u, z0 + zb + .05, .02, w * cov_, hh - .05, 3 + rng.randrange(3))
                    if k == "win_g":
                        for g in range(int(w / .12)):
                            gu = u - w / 2 + .06 + g * .12
                            if axis == "x":
                                wins.box(gu, c + out * .06, z0 + zb, .015, .015, hh, 6)
                            else:
                                wins.box(c + out * .06, gu, z0 + zb, .015, .015, hh, 6)
                elif k == "shopwin":
                    if axis == "x":
                        wins.box(u, c - out * .05, z0 + zb, w, .03, hh, 1)
                        for xx in (u - w / 2, u + w / 2):
                            wins.box(xx, c, z0 + zb, .06, .12, hh, 0)
                    else:
                        wins.box(c - out * .05, u, z0 + zb, .03, w, hh, 1)
                elif k == "rollup":
                    for s in range(int((hh - .3) / .1)):
                        zz = z0 + .3 + s * .1 + (hh * .55 if e and "box" in e["role"] else 0)
                        if zz > z0 + hh:
                            break
                        if axis == "x":
                            wins.box(u, c - out * .1, zz, w - .04, .025, .07, 6)
                        else:
                            wins.box(c - out * .1, u, zz, .025, w - .04, .07, 6)
                    if axis == "x":
                        wins.box(u, c + out * .25, z0 + hh, w + .3, .5, .5, 6)
                    else:
                        wins.box(c + out * .25, u, z0 + hh, .5, w + .3, .5, 6)
            if f > 0:                                                          # floor band
                if axis == "x":
                    shell.box((a + bb) / 2, c + out * .04, z0 - .1, L_ + .1, .08, .22, 2)
                else:
                    shell.box(c + out * .04, (a + bb) / 2, z0 - .1, .08, L_ + .1, .22, 2)
        if axis == "x":
            shell.box((a + bb) / 2, c + out * .005, 0, L_, .03, .7, 4)           # plinth
        else:
            shell.box(c + out * .005, (a + bb) / 2, 0, .03, L_, .7, 4)
    for f in range(nf):
        shell.box((x0 + x1) / 2, (y0 + y1) / 2, zs_[f], x1 - x0 - .1, y1 - y0 - .1, .15, 3, bottom=True)
    H.mesh(P + f"B{bi}_{b['role']}_shell", shell, [b["mat"], "parede_pintada", "concreto_pintado", "concreto_aparente", "ceramica_piso"], "Shell",
           sa_layer="Architecture", building=b["role"])
    H.mesh(P + f"B{bi}_{b['role']}_openings", wins, ["aluminio", "vidro", "granito", "tecido_lencol", "tecido_colchao", "plastico_branco", "aco_pintado_cinza"],
           "Openings", sa_layer="Architecture", lod="LOD0-light")
    # interior masks for closed upper floors
    if nf > 1:
        mk = sa_bl.MeshBuilder()
        for f in range(1, nf):
            mk.box((x0 + x1) / 2, (y0 + y1) / 2, zs_[f] + .15, max(.5, x1 - x0 - 5.0), max(.5, y1 - y0 - 5.0), fh - .2, 0)
        H.mesh(P + f"B{bi}_interior_mask", mk, ["parede_pintada"], "Interior", sa_layer="Architecture", note="andares superiores fechados no W2")
    # roof
    rf = sa_bl.MeshBuilder()
    roof = b["roof"]
    w_, d_ = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if roof in ("flat_parapet",):
        rf.box(cx, cy, Hb, w_, d_, .15, 0, bottom=True)
        for (px, py, sx, sy) in ((cx, y0 + .1, w_, .2), (cx, y1 - .1, w_, .2), (x0 + .1, cy, .2, d_), (x1 - .1, cy, .2, d_)):
            rf.box(px, py, Hb + .15, sx, sy, .9, 1)
            rf.box(px, py, Hb + 1.05, sx + (.1 if sx > 1 else .14), sy + (.1 if sy > 1 else .14), .05, 2)
        rf.cylinder(cx - w_ * .2, cy + d_ * .2, Hb + .15, .7, .95, 16, 3)
    elif roof in ("gable_side", "hip"):
        rise = min(3.0, w_ * .18) if roof == "gable_side" else min(2.6, min(w_, d_) * .2)
        inset = 0.0 if roof == "gable_side" else min(w_, d_) / 2
        ov = .5
        ridge = [(x0 + inset, cy, Hb + rise), (x1 - inset, cy, Hb + rise)]
        for s in (-1, 1):
            ye = y0 - ov if s < 0 else y1 + ov
            q = [(x0 - ov, ye, Hb - .1), (x1 + ov, ye, Hb - .1), ridge[1], ridge[0]]
            rf.add_face(q if s > 0 else q[::-1], 0)
        if roof == "hip":
            rf.add_face([(x0 - ov, y0 - ov, Hb - .1), ridge[0], (x0 - ov, y1 + ov, Hb - .1)], 0)
            rf.add_face([(x1 + ov, y1 + ov, Hb - .1), ridge[1], (x1 + ov, y0 - ov, Hb - .1)], 0)
        else:
            for xx in (x0, x1):
                for tt, flip in ((-.1, False), (.1, True)):
                    tri = [(xx + tt, y0, Hb), (xx + tt, y1, Hb), (xx + tt, cy, Hb + rise)]
                    rf.add_face(tri[::-1] if flip else tri, 1)
        rf.box(cx, cy, Hb, w_ - .2, d_ - .2, .12, 1, bottom=True)
    elif roof == "sawtooth":
        n = max(2, int(d_ / 6.5))
        step = d_ / n
        for k in range(n):
            ya, yb = y0 + k * step, y0 + (k + 1) * step
            rf.add_face([(x0, ya, Hb), (x1, ya, Hb), (x1, yb - .1, Hb + 2.2), (x0, yb - .1, Hb + 2.2)][::-1], 0)
            rf.add_face([(x0, yb - .1, Hb + 2.2), (x1, yb - .1, Hb + 2.2), (x1, yb, Hb), (x0, yb, Hb)][::-1], 4)   # glazed north lights
            for xx in (x0, x1):
                rf.add_face([(xx, ya, Hb), (xx, yb, Hb), (xx, yb - .1, Hb + 2.2)], 1)
        rf.box(cx, cy, Hb - .2, w_ - .2, d_ - .2, .1, 1, bottom=True)
    H.mesh(P + f"B{bi}_{b['role']}_roof", rf, ["telha_fibrocimento" if roof == "sawtooth" else ("ceramica_telha" if roof != "flat_parapet" else "borracha_preta"),
                                             b["mat"], "concreto_pintado", "plastico_azul", "vidro"], "Structure", sa_layer="Architecture")

# ---------------------------------------------------------------- entrance components (doors, site gates)
KO = H.kit("Openings")
for e in ents:
    k = kind_of(e)
    p = e["lp"]
    rot = {"-y": 0.0, "+y": math.pi, "-x": -math.pi / 2, "+x": math.pi / 2}[e["side"]]
    if k == "door":
        if "shop" in e["role"] or e["role"] == "main" and shop_side:
            mb = sa_bl.MeshBuilder()
            w = e["w"]
            for xx in (-w / 2, 0.0, w / 2):
                mb.box(xx, 0, 0, .06, .12, 2.45, 0)                                            # jambs + meeting stile
            mb.box(0, 0, 2.4, w + .06, .12, .06, 0)
            mb.box(0, 0, 0, w + .06, .12, .04, 0)
            for xx in (-w / 4, w / 4):
                mb.box(xx, -.01, .05, w / 2 - .08, .015, 2.33, 1)
                mb.box(xx + (.12 if xx < 0 else -.12), -.04, 1.0, .03, .04, .4, 0)              # pull handles
            o = H.mesh(P + f"door_{e['role']}", mb, ["aluminio", "vidro"], "Openings", bevel=.003, sa_kind="glass_door", interactive=True)
            o.location, o.rotation_euler = (p[0], p[1], 0), (0, 0, rot)
        else:
            KO.door_entrance_metal(P + f"door_{e['role']}", e["w"], 2.1 if e["w"] < 1.4 else 2.4, (p[0], p[1], 0), rot)
    elif k == "site_gate":
        mb = sa_bl.MeshBuilder()
        for g in range(int(e["w"] / .12)):
            mb.box(-e["w"] / 2 + .06 + g * .12, 0, .05, .025, .025, 2.0, 0)
        mb.box(0, 0, .05, e["w"], .05, .06, 0)
        mb.box(0, 0, 2.0, e["w"], .05, .06, 0)
        o = H.mesh(P + f"gate_{e['role']}", mb, ["aco_pintado_cinza"], "Site", sa_kind="site_gate", interactive=True)
        o.location, o.rotation_euler = (p[0], p[1], 0), (0, 0, rot)

# ---------------------------------------------------------------- awning, secondary volumes, roof items
mb = sa_bl.MeshBuilder()
if hero.get("awning"):
    r = Lrect(hero["awning"]["rect"])
    h = hero["awning"]["h"]
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, h, r[2] - r[0], r[3] - r[1], .08, 0)
    long_x = (r[2] - r[0]) > (r[3] - r[1])
    for k in range(int(max(r[2] - r[0], r[3] - r[1]) / 3.0) + 1):
        t = k * 3.0
        if long_x:
            mb.box(r[0] + t, (r[1] + r[3]) / 2, h - .3, .05, r[3] - r[1], .3, 1)
        else:
            mb.box((r[0] + r[2]) / 2, r[1] + t, h - .3, r[2] - r[0], .05, .3, 1)
for s in hero.get("secondary", []):
    r = Lrect(s["rect"])
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 0, r[2] - r[0], r[3] - r[1], s["h"], 2)
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, s["h"], r[2] - r[0] + .1, r[3] - r[1] + .1, .1, 1)
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, s["h"] + .1, 1.2, .8, .6, 3)             # condensing unit on top
for it in hero.get("roof_items", []):
    r = Lrect(it["rect"])
    bz = max(b["H"] for b in blds)
    for k in range(3):
        mb.box(r[0] + .9 + k * 1.6, (r[1] + r[3]) / 2, bz + .15, 1.2, .5, .9, 3)
H.mesh(P + "awning_secondary", mb, ["lona_toldo" if "lona_toldo" in H.lib else "plastico_azul", "aluminio", "aco_inox", "plastico_branco"], "Shell",
       bevel=.004, sa_layer="Architecture")

# ---------------------------------------------------------------- interiors (ground floor rooms by role)
b0 = blds[0]
hw_, hd_ = (b0["r"][2] - b0["r"][0]) / 2, (b0["r"][3] - b0["r"][1]) / 2
walled = [k for k, r in ROOM.items() if k not in ("salao", "boxes", "workstations", "quadro") and (r[2] - r[0]) * (r[3] - r[1]) > 1.0]
if walled:
    cx0, cy0 = (b0["r"][0] + b0["r"][2]) / 2, (b0["r"][1] + b0["r"][3]) / 2
    shifted = {k: (r[0] - cx0, r[1] - cy0, r[2] - cx0, r[3] - cy0) for k, r in ROOM.items()}
    edges, doors = partition_plan(shifted, walled, hw_, hd_, T)
    mb = sa_bl.MeshBuilder()
    gh0 = b0["ground_h"]
    for axis, c, a, bb in edges:
        ops = [(p, w + .07, .15, 2.25) for ax, cc, p, w, _ in doors if ax == axis and abs(cc - c) < .3 and a < p < bb]
        off = cy0 if axis == "x" else cx0
        offa = cx0 if axis == "x" else cy0
        (wall_x if axis == "x" else wall_y)(mb, c + off, a + offa, bb + offa, .12, .15, gh0, [(p + offa, w, z1, z2) for p, w, z1, z2 in ops], 0)
    H.mesh(P + "partitions", mb, ["parede_pintada"], "Interior", sa_layer="Architecture")
    for axis, c, p, w, r_ in doors:
        loc = (p + cx0, c + cy0, .15) if axis == "x" else (c + cx0, p + cy0, .15)
        KO.door(P + f"door_room_{r_}", .8, 2.1, loc, 0.0 if axis == "x" else math.pi / 2, wall_t=.12)
KI = H.kit("Interior")
KS = H.kit("Services")
mb = sa_bl.MeshBuilder()
for role, r in ROOM.items():
    x0, y0, x1, y1 = r
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w_, d_ = x1 - x0, y1 - y0
    floor_mat = 0 if role not in ("banheiro", "sanitarios", "cozinha", "lavagem", "copa") else 1
    mb.box(cx, cy, .15, w_, d_, .01, floor_mat)
    if w_ * d_ > 2.0:
        KI.ceiling_light(P + f"light_{role}", (cx, cy, b0["ground_h"] - .02))
    if role in ("quadro", "meters", "technical_room", "sala_tecnica", "rack"):
        side_x = abs(x0 - b0["r"][0]) < .6 or abs(x1 - b0["r"][2]) < .6
        if role == "meters":
            for col in range(8):
                for row in range(3):
                    mb.box(x0 + .5 + col * .45, y1 - .12, .6 + row * .55, .4, .22, .48, 3)
        elif role == "rack":
            mb.box(cx, cy, .15, .6, .8, 2.0, 4)
            for k in range(8):
                mb.box(cx, cy - .41, .4 + k * .2, .5, .02, .05, 5)
        else:
            if side_x:
                xw = x0 + .01 if abs(x0 - b0["r"][0]) < .6 else x1 - .01
                KS.panel_qdc(P + f"qdc_{role}", (xw + (.25 if xw < cx else -.25) * 0, cy, .15), math.pi / 2 if xw < cx else -math.pi / 2, z=1.5, ways=18)
            else:
                yw = y1 - .01 if abs(y1 - b0["r"][3]) < abs(y0 - b0["r"][1]) else y0 + .01
                KS.panel_qdc(P + f"qdc_{role}", (cx, yw, .15), 0.0 if yw > cy else math.pi, z=1.5, ways=18)
        H.empty(P + f"GP_{role}", (cx, cy, 1.4), (min(w_, 1.5), min(d_, 1.5), 2.0), sa_kind="interaction", gameplay=f"{role} (diagnóstico)")
    elif role == "salao" and HID == "grocery":
        # W3: stocked gondolas (packages on every level, both faces), refrigerated display, produce stand; visible through the glass
        pm = sa_bl.MeshBuilder()
        prng = random.Random(77)
        gl = min(7.0, w_ - 4.0)
        for k in range(int((d_ - 3.0) / 2.2)):
            yy = y0 + 2.0 + k * 2.2
            KI.shelving(P + f"gondola_{k}", gl, (x0 + 3.2, yy, .15), 0.0, levels=5, h=1.8, depth=.6)
            for lv in range(5):
                z = .15 + .1 + lv * (1.8 - .15) / 4 + .02
                for face in (-1, 1):
                    xx = x0 + 3.25
                    while xx < x0 + 3.2 + gl - .1:
                        bw, bh, bd = prng.uniform(.08, .26), prng.uniform(.1, .3), prng.uniform(.18, .26)
                        if prng.random() > .12:
                            pm.box(xx + bw / 2, yy + face * bd / 2, z, bw - .01, bd, bh, prng.randrange(6))
                        xx += bw
        fr = (x0 + 1.0, y1 - 4.5)
        pm.box(fr[0], fr[1], .15, .8, 4.0, 2.0, 6)                                    # refrigerated display body
        pm.box(fr[0] + .41, fr[1], .3, .02, 3.8, 1.7, 7)                              # glass doors
        for k in range(4):
            for lv in range(4):
                pm.box(fr[0] + .1, fr[1] - 1.6 + k * 1.0, .4 + lv * .42, .3, .7, .25, prng.randrange(6))
        pm.box(x1 - 2.0, y0 + 1.5, .15, 1.6, .9, .75, 8)                              # produce stand
        for k in range(10):
            pm.box(x1 - 2.6 + (k % 5) * .3, y0 + 1.3 + (k // 5) * .4, .9, .28, .36, .15, 9 + k % 3)
        H.mesh(P + "grocery_stock", pm, ["papelao", "plastico_azul", "aco_pintado_vermelho", "plastico_branco", "aco_pintado_verde", "pintura_industrial",
                                         "aco_inox", "vidro", "madeira_crua", "aco_pintado_vermelho", "pintura_industrial", "folhagem"], "Interior",
               sa_layer="Props", note="W3: mercadorias e expositores (mercearia, Capítulo I)")
        lo = KI.ceiling_light(P + "fridge_light", (fr[0] + .2, fr[1], 2.0), drop=.05)
    elif role == "salao" and HID == "restaurant":
        for i in range(int((w_ - 2) / 3.0)):
            for j in range(int((d_ - 2) / 3.0)):
                tx, ty = x0 + 2.0 + i * 3.0, y0 + 2.0 + j * 3.0
                mb.box(tx, ty, .88, .9, .9, .04, 5)
                mb.cylinder(tx, ty, .15, .05, .73, 8, 4)
                for ax, rr in ((-.75, -math.pi / 2), (.75, math.pi / 2)):
                    KI.chair_old(P + f"chair_{i}_{j}_{ax:+.0f}", (tx + ax, ty, .15), rr + rng.uniform(-.2, .2))
    elif role == "caixa":
        mb.box(cx, cy, .15, 1.2, d_ * .8, 1.0, 5)
    elif role in ("cozinha",):
        kl = min(6.0, d_ - 1.0)
        KI.kitchen_counter(P + "kitchen_line", kl, (x1 - .02, y0 + .5 + kl, .15), -math.pi / 2, sink_at=1.0)
        mb.box(cx - .5, cy, .15, 1.2, 2.4, .9, 4)                                                     # stainless island
    elif role in ("banheiro", "sanitarios"):
        KI.toilet(P + f"toilet_{role}", (x0 + .5, y1 - .3, .15), 0.0)
        KI.sink_pedestal(P + f"sink_{role}", (x0 + 1.4, y1 - .15, .15), 0.0)
    elif role in ("copa",):
        KI.kitchen_counter(P + f"counter_{role}", min(2.0, w_ - .4), (x0 + .2, y1 - .02, .15), 0.0, sink_at=.6)
    elif role == "workstations":
        for i in range(int((w_ - 2) / 2.4)):
            for j in range(int((d_ - 2) / 2.6)):
                tx, ty = x0 + 1.6 + i * 2.4, y0 + 1.6 + j * 2.6
                mb.box(tx, ty, .88, 1.4, .7, .04, 5)
                for ox in (-.65, .65):
                    mb.box(tx + ox, ty, .15, .04, .65, .73, 4)
                mb.box(tx, ty + .15, .92, .5, .05, .35, 6)
    elif role == "boxes":
        for k, bx in enumerate((x0 + 4.5, x0 + 14.0)):
            mb.box(bx, cy, .15, 3.0, 5.5, .03, 2)                                                    # lift pads painted
            for sx in (-1, 1):
                mb.box(bx + sx * 1.3, cy, .15, .3, .3, 3.2, 4)                                       # two-post lift
            mb.box(bx, cy, 3.3, 3.0, .3, .2, 4)
        KS.panel_qdc(P + "qdc_boxes", (x0 + .01, cy + 3.0, .15), math.pi / 2, z=1.5, ways=12)
    elif role == "bench":
        KI.workbench(P + "bench", min(3.0, w_ - .6), (x0 + .3, y1 - .4, .15), 0.0, pro=True)
    elif role in ("reception", "depot", "estoque", "despensa", "laundry_service", "meeting", "lavagem"):
        if role in ("depot", "estoque", "despensa"):
            KI.shelving(P + f"shelf_{role}", min(3.0, w_ - .6), (x0 + .3, y1 - .3, .15), 0.0, levels=5)
        elif role == "reception":
            mb.box(cx, cy + d_ * .15, .15, min(2.4, w_ - 1), .6, 1.05, 5)
        elif role == "meeting":
            mb.box(cx, cy, .88, min(3.0, w_ - 1.5), 1.2, .05, 5)
H.mesh(P + "interior_fitout", mb, ["piso_ceramico_bege", "azulejo_branco", "concreto_pintado", "aco_pintado_cinza", "aco_inox", "madeira_pintada",
                                   "plastico"], "Interior", bevel=.004, sa_layer="Props")

# ---------------------------------------------------------------- site: paving, parking, yards, boundary, sign
lot = Lrect(hero["lot"])
mb = sa_bl.MeshBuilder()
mb.box((lot[0] + lot[2]) / 2, (lot[1] + lot[3]) / 2, -.25, lot[2] - lot[0], lot[3] - lot[1], .25, 0)
for p in hero.get("parking", []):
    r = Lrect(p["rect"])
    mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, -.2, r[2] - r[0], r[3] - r[1], .21, 1)
    n = p.get("stalls", 0)
    if n and p["kind"] == "car":
        long_x = (r[2] - r[0]) >= (r[3] - r[1])
        if long_x:
            per = max(1, int((r[2] - r[0]) / 2.5))
            for k in range(per + 1):
                mb.box(r[0] + k * (r[2] - r[0]) / per, (r[1] + r[3]) / 2, .01, .1, min(5.0, r[3] - r[1]), .005, 2)
        else:
            per = max(1, int((r[3] - r[1]) / 2.5))
            for k in range(per + 1):
                mb.box((r[0] + r[2]) / 2, r[1] + k * (r[3] - r[1]) / per, .01, min(5.0, r[2] - r[0]), .1, .005, 2)
for s in hero.get("service", []):
    if "rect" in s:
        r = Lrect(s["rect"])
        mb.box((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, -.2, r[2] - r[0], r[3] - r[1], .205, 3)
fs = "-y"
for side in ("+y", "-x", "+x"):                                                          # boundary walls except the street front
    axis, c, a, bb = side_line(lot, side)
    gaps = [(e["lp"][0] if axis == "x" else e["lp"][1], e["w"]) for e in ents if kind_of(e) == "site_gate"]
    (wall_x if axis == "x" else wall_y)(mb, c, a, bb, .18, 0, 2.0, [(u, w, 0, 2.0) for u, w in gaps], 4)
H.mesh(P + "site", mb, ["calcada", "asfalto_gasto", "sinalizacao_viaria", "concreto", "reboco_antigo"], "Site", sa_layer="Roads")
name = hero["name"].split("(")[0].strip().upper()
if HID == "grocery":
    name = "HORTIFRUTI - FRIOS - BEBIDAS"
if len(name) > 26:
    name = name[:26]
if HID in ("apartments", "smalloffice"):
    name = " "
t = text_mesh(P + "sign_name", name, .45, H.C["Shell"], H.lib["aco_pintado_verde" if HID != "restaurant" else "aco_pintado_vermelho"], extrude=.03)
fr0 = blds[0]["r"]
t.parent, t.location, t.rotation_euler = H.rootobj, ((fr0[0] + fr0[2]) / 2, fr0[1] - .06, blds[0]["ground_h"] - .55), (math.pi / 2, 0, 0)
KX = H.kit("Site")
KX.entrance_meter(P + "padrao_entrada", (fr0[0] + 1.2, fr0[1], 0), 0.0, height=min(4.2, blds[0]["ground_h"]))
for k in range(3):                                                                       # facade AC condensers (retrofit)
    b = blds[rng.randrange(len(blds))]
    if b["floors"] < 2:
        continue
    r = b["r"]
    mb = sa_bl.MeshBuilder()
    mb.box(0, -.15, 0, .78, .3, .55, 0)
    o = H.mesh(P + f"ac_{k}", mb, ["plastico_branco"], "Services", bevel=.004, sa_layer="Props")
    o.location = (rng.uniform(r[0] + 1, r[2] - 1), r[1], b["ground_h"] + rng.randrange(max(1, b["floors"] - 1)) * b["fh"] + .4)
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -1.4, 160, 160, 1.15, 0)
H.mesh(P + "ground_plate", mb, ["terra"], "CaptureOnly", sa_layer="Terrain", note="só para capturas isoladas")

# ---------------------------------------------------------------- W2.5 character pass (per hero) + wear decals
from sa_w2 import wear_pass  # noqa: E402
KC = H.kit("Site")
fr0 = blds[0]["r"]
yF = fr0[1]


def fill_parking(rect, tag, density=.65):
    r = Lrect(rect)
    long_x = (r[2] - r[0]) >= (r[3] - r[1])
    n = max(1, int(((r[2] - r[0]) if long_x else (r[3] - r[1])) / 2.6))
    for k in range(n):
        if rng.random() > density:
            continue
        t = (k + .5) / n
        if long_x:
            c = (r[0] + t * (r[2] - r[0]), (r[1] + r[3]) / 2)
            rot = math.pi / 2 + (math.pi if rng.random() < .5 else 0) + rng.uniform(-.05, .05)
        else:
            c = ((r[0] + r[2]) / 2, r[1] + t * (r[3] - r[1]))
            rot = (math.pi if rng.random() < .5 else 0) + rng.uniform(-.05, .05)
        KC.car(P + f"car_{tag}_{k}", (c[0], c[1], 0.0), rot, paint=rng.randrange(6), van=rng.random() < .12)


def front_slots(b):
    x0, y0, x1, y1 = b["r"]
    L_ = x1 - x0
    n = max(1, int((L_ - 1.5) / 3.3))
    return [x0 + (k + .5) * L_ / n for k in range(n)]


def letters(name, text, size, loc, mat="aco_inox", extrude=.025):
    t = text_mesh(P + name, text, size, H.C["Shell"], H.lib[mat], extrude=extrude)
    t.parent, t.location, t.rotation_euler = H.rootobj, loc, (math.pi / 2, 0, 0)
    return t


mb = sa_bl.MeshBuilder()
if HID == "apartments":
    b = blds[0]
    main = next(e for e in ents if e["role"] == "main")["lp"]
    for f in range(1, b["floors"]):
        z0 = b["ground_h"] + (f - 1) * b["fh"]
        for k, x in enumerate(front_slots(b)):
            if (k + f) % 2:
                continue
            mb.box(x, yF - .55, z0, 2.4, 1.1, .12, 0, bottom=True)                       # balcony slab
            mb.box(x, yF - 1.08, z0 + .12, 2.4, .05, .95, 2)                              # railing panel
            for xx in (x - 1.2, x + 1.2):
                mb.box(xx, yF - .55, z0 + .12, .05, 1.1, 1.0, 1)
            mb.box(x, yF - 1.08, z0 + 1.05, 2.45, .07, .05, 1)
            if rng.random() < .35:
                mb.box(x + .6, yF - .8, z0 + .12, .9, .02, .9, 4 + rng.randrange(2))      # laundry rack
            if rng.random() < .4:
                mb.cylinder(x - .8, yF - .85, z0 + .12, .16, .35, 10, 6)
                mb.cylinder(x - .8, yF - .85, z0 + .47, .22, .3, 8, 7)
    for r_ in range(int((b["H"] - 3.6) / .4)):                                            # cobogó strip over the entrance (stair core)
        for c_ in range(6):
            mb.box(main[0] - 1.0 + c_ * .4, yF - .06, 3.6 + r_ * .4, .34, .14, .34, 3)
    mb.box(main[0], yF - 1.0, 2.9, 3.4, 2.0, .15, 0, bottom=True)                         # entrance canopy
    for xx in (main[0] - 1.6, main[0] + 1.6):
        mb.cylinder(xx, yF - 1.9, 0, .06, 2.9, 10, 1)
    vp = next(e for e in ents if e["role"] == "vehicle_passage")["lp"]
    for k in range(int(4.0 / .14)):
        mb.box(vp[0] - 2.0 + .07 + k * .14, yF + .4, .05, .025, .025, 2.6, 1)            # passage gate bars
    mb.box(vp[0], yF + .4, 2.65, 4.0, .05, .06, 1)
    letters("sign_name", "RESIDENCIAL VILA ANTIGA", .32, (main[0], yF - 2.0, 3.12), "aco_inox")
    cy = Lrect(next(s_["rect"] for s_ in hero["service"] if s_["role"] == "courtyard_service"))
    for k, (tx, ty) in enumerate(((cy[0] + 3, cy[3] - 3), (cy[2] - 4, cy[1] + 4))):
        mb.cylinder(tx, ty, 0, .15, 2.6, 8, 8)
        mb.cylinder(tx, ty, 2.4, 1.6, 2.2, 12, 7)
        mb.box(tx, ty, -.05, 2.2, 2.2, .1, 9)
    KC.clothesline(P + "clothes_a", (cy[0] + 1, cy[3] - 1.5), (cy[0] + 8, cy[3] - 1.5), 2.0, n=7, seed=3)
    KC.clothesline(P + "clothes_b", (cy[0] + 1, cy[3] - 3.0), (cy[0] + 7, cy[3] - 3.0), 2.0, n=5, seed=4)
    fill_parking(next(p_["rect"] for p_ in hero["parking"] if p_["role"] == "courtyard"), "patio", .6)
    for k in range(3):
        KC.drum(P + f"bin_{k}", (cy[2] - 1.0, cy[1] + 1.0 + k * .8, 0.0), 0.0, paint="plastico_azul")
elif HID == "grocery":
    b = blds[0]
    aw = Lrect(hero["awning"]["rect"])
    ah = hero["awning"]["h"]
    for k in range(int((aw[2] - aw[0]) / .9)):                                            # striped awning canvas
        x = aw[0] + .45 + k * .9
        mb.box(x, (aw[1] + aw[3]) / 2, ah + .085, .9, aw[3] - aw[1], .01, 4 + (k % 2))
        mb.box(x, aw[1] - .01, ah - .25, .9, .02, .33, 4 + (k % 2))                       # valance
    mb.box((fr0[0] + fr0[2]) / 2, yF - .08, ah + .25, fr0[2] - fr0[0] - 2.0, .08, .95, 10)   # painted sign board
    letters("sign_board", "MERCEARIA SÃO JORGE", .55, ((fr0[0] + fr0[2]) / 2, yF - .14, ah + .38), "aco_pintado_vermelho")
    letters("sign_since", "DESDE 1978", .2, ((fr0[0] + fr0[2]) / 2 + 9.0, yF - .14, ah + .42), "aco_pintado_vermelho")
    door = next(e for e in ents if e["role"] == "shop_main")["lp"]
    KC.crate_stack(P + "crates_a", (door[0] - 3.2, yF - .6, 0.0), 0.0, n=4)
    KC.crate_stack(P + "crates_b", (door[0] + 2.2, yF - .6, 0.0), 0.0, n=3)
    KC.freezer(P + "freezer", (door[0] + 4.4, yF - .55, 0.0), 0.0)
    KC.a_board(P + "a_board", (door[0] - 1.8, yF - 1.8, 0.0), .3)
    KC.gas_cage(P + "gas_cage", (fr0[0] + 1.6, yF - .5, 0.0), 0.0, n=3)
    for k, x in enumerate(front_slots(b)):                                                # flower boxes, upper residence
        if rng.random() < .55:
            z0 = b["ground_h"] + .95
            mb.box(x, yF - .2, z0 - .25, 1.2, .3, .25, 6)
            mb.box(x, yF - .2, z0, 1.1, .25, .18, 7)
    ly = Lrect(next(s_["rect"] for s_ in hero["service"] if s_["role"] == "loading_yard"))
    KC.pallet_stack(P + "pallets", (ly[0] + 1.5, ly[1] + 4.0, 0.0), .1, n=5)
    KC.car(P + "delivery_van", ((ly[0] + ly[2]) / 2, ly[3] - 4.0, 0.0), math.pi / 2, paint=2, van=True)
    for k in range(2):
        KC.drum(P + f"drum_{k}", (ly[2] - .6, ly[1] + 1.0 + k * .7, 0.0), 0.0, paint="plastico_azul")
    fill_parking(next(p_["rect"] for p_ in hero["parking"] if p_["role"] == "street_bays"), "rua", .7)
elif HID == "restaurant":
    letters("sign_sub", "COMIDA CASEIRA", .25, ((fr0[0] + fr0[2]) / 2, yF - .1, blds[0]["ground_h"] - .95), "aco_pintado_vermelho")
    aw = Lrect(hero["awning"]["rect"])
    for k in range(3):
        tx = aw[0] + 3.0 + k * 7.0
        if abs(tx - (aw[0] + aw[2]) / 2) < 2.0:
            continue
        mb.box(tx, aw[1] - .4, .74, .8, .8, .04, 11)
        mb.cylinder(tx, aw[1] - .4, 0, .05, .74, 8, 1)
        for sgn in (-1, 1):
            KC.chair_old(P + f"terrace_chair_{k}_{sgn}", (tx + sgn * .7, aw[1] - .4, 0.0), sgn * math.pi / 2)
    KC.a_board(P + "menu_board", ((aw[0] + aw[2]) / 2 + 2.0, aw[1] - 1.2, 0.0), -.2)
    for x in (aw[0] + .6, aw[2] - .6):
        mb.box(x, aw[1] - .3, 0, .8, .5, .5, 3)
        mb.box(x, aw[1] - .3, .5, .7, .4, .3, 7)
    cz = ROOM.get("cozinha", fr0)
    duct_x = fr0[2] + .3
    top = blds[0]["H"] + 2.0
    mb.box(duct_x, (cz[1] + cz[3]) / 2, 2.5, .6, .6, top - 2.5, 1)                         # kitchen exhaust duct up the side wall
    mb.box(duct_x - .2, (cz[1] + cz[3]) / 2, top, 1.0, 1.0, .5, 1)
    mb.box(duct_x - .2, (cz[1] + cz[3]) / 2, top + .5, 1.3, 1.3, .08, 1)
    yd = Lrect(next(s_["rect"] for s_ in hero["service"] if s_["role"] == "service_yard"))
    KC.gas_cage(P + "gas_cage", (yd[2] - 2.0, yd[1] + 1.0, 0.0), 0.0, n=4)
    KC.crate_stack(P + "crates_yard", (yd[0] + 1.5, yd[1] + 1.0, 0.0), 0.0, n=4)
    for k in range(3):
        KC.drum(P + f"bin_{k}", (yd[0] + 4.0 + k * .8, yd[3] - 1.0, 0.0), 0.0, paint="plastico_azul" if k else "aco_pintado_verde")
    fill_parking(next(p_["rect"] for p_ in hero["parking"] if p_["role"] == "forecourt_stalls"), "frente", .7)
elif HID == "workshop":
    b = blds[0]
    mb.box((fr0[0] + fr0[2]) / 2, yF - .03, 4.6, fr0[2] - fr0[0], .06, .5, 12)              # painted band
    letters("sign_sub", "BATERIAS - ALTERNADORES - INJEÇÃO", .26, ((fr0[0] + fr0[2]) / 2, yF - .08, 4.68), "aco_pintado_cinza")
    for e in ents:
        if e["role"].startswith("box_"):
            KC.tire_stack(P + f"tires_{e['role']}", (e["lp"][0] + 2.6, yF - .6, 0.0), 0.0, n=5)
    KC.drum(P + "drum_oil_a", (fr0[0] + 1.0, yF - .6, 0.0), 0.0, paint="aco_pintado_vermelho")
    KC.drum(P + "drum_oil_b", (fr0[0] + 1.7, yF - .6, 0.0), 0.0)
    bx = ROOM.get("boxes")
    if bx:
        KC.car(P + "car_on_lift", (bx[0] + 4.5, (bx[1] + bx[3]) / 2, 1.6), math.pi / 2, paint=3)
        KC.car(P + "car_box2", (bx[0] + 14.0, (bx[1] + bx[3]) / 2, .15), math.pi / 2 + .05, paint=0)
        KC.shelving(P + "battery_rack", 2.4, (bx[2] - 3.0, bx[1] + .4, .15), 0.0, levels=4, h=1.6)
    fill_parking(next(p_["rect"] for p_ in hero["parking"] if p_["role"] == "yard_parking"), "patio", .55)
elif HID == "smalloffice":
    b = blds[0]
    for x in [fr0[0] + .6 + k * .8 for k in range(int((fr0[2] - fr0[0] - 1.2) / .8) + 1)]:
        mb.box(x, yF - .25, b["ground_h"] + .1, .06, .45, b["H"] - b["ground_h"] - .2, 1)     # brise-soleil fins
    mb.box((fr0[0] + fr0[2]) / 2, yF - .3, b["H"] - .25, fr0[2] - fr0[0], .5, .12, 1)
    main = next(e for e in ents if e["role"] == "main")["lp"]
    mb.box(main[0], yF - 1.2, 3.0, 4.0, 2.4, .12, 1, bottom=True)                          # entrance canopy
    for xx in (main[0] - 1.9, main[0] + 1.9):
        mb.box(xx, yF - 2.3, 0, .1, .1, 3.0, 1)
    letters("sign_plaque", "PAIVA CONTABILIDADE", .3, (main[0] + 5.5, yF - .06, 2.4), "aco_inox")
    for x in (fr0[0] + 2.0, fr0[2] - 2.0):
        mb.box(x, yF - 1.0, 0, 2.4, .9, .45, 3)
        mb.box(x, yF - 1.0, .45, 2.2, .7, .05, 7)
    fill_parking(next(p_["rect"] for p_ in hero["parking"] if p_["role"] == "rear_parking"), "fundos", .6)
H.mesh(P + "character", mb, ["concreto_pintado", "aluminio", "aco_pintado_cinza", "concreto", "plastico_branco", "plastico_azul", "ceramica_telha",
                             "folhagem", "tronco", "terra", "aco_pintado_verde", "madeira_pintada", "pintura_industrial"], "Shell", bevel=.004,
       sa_layer="Architecture", note="W2.5: identidade do herói (fachada, entrada, volumes de apoio, vida de rua)")
wear_pass(H.lib, H.C["Site"], H.rootobj, [(*b["r"], b["H"]) for b in blds],
          entrances=[(e["lp"][0], e["lp"][1], e["side"]) for e in ents if kind_of(e) != "site_gate"],
          ground_rects=[Lrect(p_["rect"]) for p_ in hero.get("parking", [])],
          drive_lines=[], seed=zlib.crc32(HID.encode()), prefix=P, facility=HID)

# ---------------------------------------------------------------- cameras / captures
sa_bl.sun_and_sky(H.scene, H.C["Lighting"], elevation_deg=34.0, azimuth_deg=210.0)
lw, ld = lot[2] - lot[0], lot[3] - lot[1]
tallest = max(b["H"] for b in blds)
H.cam(f"CAM_W2_{HID}_street", (lw * .1, lot[1] - max(22.0, tallest * 1.6), 1.7), (0.0, fr0[1], tallest * .4), 22)
main = next((e for e in ents if kind_of(e) == "door"), ents[0])
mp = main["lp"]
H.cam(f"CAM_W2_{HID}_entrance", (mp[0] + 3.5, mp[1] - 5.0, 1.65), (mp[0], mp[1], 1.8), 20)
big = max(ROOM.items(), key=lambda kv: (kv[1][2] - kv[1][0]) * (kv[1][3] - kv[1][1])) if ROOM else None
if big:
    r = big[1]
    H.cam(f"CAM_W2_{HID}_interior", ((r[0] + r[2]) / 2, r[1] + .6, 1.65), ((r[0] + r[2]) / 2 + (r[2] - r[0]) * .15, r[3] - .5, 1.2), 15)
tech = next(((k, r) for k, r in ROOM.items() if k in ("quadro", "meters", "technical_room", "sala_tecnica", "rack")), None)
if tech:
    r = tech[1]
    cxr, cyr = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    H.cam(f"CAM_W2_{HID}_tecnico", (cxr + (2.5 if cxr < 0 else -2.5), cyr - 2.2, 1.65), (cxr, cyr, 1.4), 18)
H.cam(f"CAM_W2_{HID}_aerial", (-lw * 1.1, lot[1] - ld * 1.2, max(lw, ld) * .9), (0, 0, tallest * .3), 26)
H.cutaway(f"CAM_W2_{HID}_cutaway", ((lot[0] + lot[2]) / 2, (lot[1] + lot[3]) / 2), 60.0, max(lw, ld) * 1.1)
H.capture(f"w2_{HID}_01_rua", f"CAM_W2_{HID}_street")
H.capture(f"w2_{HID}_02_entrada", f"CAM_W2_{HID}_entrance")
if big:
    H.capture(f"w2_{HID}_03_interior", f"CAM_W2_{HID}_interior")
if tech:
    H.capture(f"w2_{HID}_04_tecnico", f"CAM_W2_{HID}_tecnico")
H.capture(f"w2_{HID}_05_aerea", f"CAM_W2_{HID}_aerial")
H.capture(f"w2_{HID}_06_corte", f"CAM_W2_{HID}_cutaway", 2000, 2000, [P + f"B{i}_" for i in range(len(blds))] + [P + "light_", P + "awning", P + "sign"])
H.save(f"W2_{HID}.blend")
