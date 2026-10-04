"""Parametric architecture for the Old Town (requires only math; emits into sa_bl.MeshBuilder).

Building local frame: X along the street frontage [-w/2, w/2], Y depth [-d/2 front, +d/2 back], Z up (0 = ground at front).
Facades are built as wall pieces around real openings (recessed windows with frames, sills and glass; doors with steps;
shopfronts with roller-shutter boxes; roll-up doors), plus mouldings, plinths, cornices, roofs with real thickness and
eaves, gutters/downpipes, AC units, balconies, awnings, signage and scaffolding. Used by background families
(LOD1 base, no bevel), hero buildings and the modular kit (both bevelled as LOD0 base for final art).
"""
import math
import random

# Material slot indices shared by every architecture mesh.
SLOT_NAMES = ["facade", "trim", "frame", "glass", "roof", "plinth", "door", "metal", "sign", "rust", "shopglass", "brick"]
S = {n: i for i, n in enumerate(SLOT_NAMES)}
WALL_T = 0.25


class Facade:
    """Maps facade coordinates (u along facade, z up, depth inward) to building coordinates."""

    def __init__(self, mb, origin, u_dir, out_dir, length):
        self.mb = mb
        self.o = origin
        self.u = u_dir
        self.n = (-out_dir[0], -out_dir[1])  # inward
        self.L = length

    def P(self, u, z, dep):
        return (self.o[0] + self.u[0] * u + self.n[0] * dep, self.o[1] + self.u[1] * u + self.n[1] * dep, z)

    def box(self, u0, u1, z0, z1, d0, d1, mat, top=True, bottom=False, front=True, back=False):
        if u1 - u0 <= 1e-4 or z1 - z0 <= 1e-4 or d1 - d0 <= 1e-4:
            return
        P = self.P
        c = [P(u0, z0, d0), P(u1, z0, d0), P(u1, z0, d1), P(u0, z0, d1), P(u0, z1, d0), P(u1, z1, d0), P(u1, z1, d1), P(u0, z1, d1)]
        mb = self.mb
        if front:
            mb.quad(c[0], c[1], c[5], c[4], mat)
        mb.quad(c[1], c[2], c[6], c[5], mat)
        if back:
            mb.quad(c[2], c[3], c[7], c[6], mat)
        mb.quad(c[3], c[0], c[4], c[7], mat)
        if top:
            mb.quad(c[4], c[5], c[6], c[7], mat)
        if bottom:
            mb.quad(c[3], c[2], c[1], c[0], mat)

    def plane(self, u0, u1, z0, z1, dep, mat):
        P = self.P
        self.mb.quad(P(u0, z0, dep), P(u1, z0, dep), P(u1, z1, dep), P(u0, z1, dep), mat)

    # ------------------------------------------------------------ wall band with openings
    def wall_band(self, z0, z1, openings, t=WALL_T, mat=S["facade"]):
        """openings: list of dicts with u0, u1, zb, zt (absolute z). Wall pieces fill everything else."""
        ops = sorted([o for o in openings if o["zt"] > z0 and o["zb"] < z1], key=lambda o: o["u0"])
        cur = 0.0
        for o in ops:
            self.box(cur, o["u0"], z0, z1, 0, t, mat)
            self.box(o["u0"], o["u1"], z0, max(z0, o["zb"]), 0, t, mat)
            self.box(o["u0"], o["u1"], min(z1, o["zt"]), z1, 0, t, mat)
            # Reveals (jambs/head/sill faces) inside the opening.
            cur = o["u1"]
        self.box(cur, self.L, z0, z1, 0, t, mat)

    # ------------------------------------------------------------ openings
    def window(self, o, frame_mat=S["frame"], trim=False, grille=False, sill=True, mullion=True):
        u0, u1, zb, zt = o["u0"], o["u1"], o["zb"], o["zt"]
        fw, fd0, fd1 = .06, .07, .14
        self.box(u0, u1, zb, zb + fw, fd0, fd1, frame_mat)
        self.box(u0, u1, zt - fw, zt, fd0, fd1, frame_mat)
        self.box(u0, u0 + fw, zb, zt, fd0, fd1, frame_mat)
        self.box(u1 - fw, u1, zb, zt, fd0, fd1, frame_mat)
        if mullion and u1 - u0 > 1.0:
            m = (u0 + u1) / 2
            self.box(m - .03, m + .03, zb, zt, fd0, fd1, frame_mat)
        self.plane(u0 + fw, u1 - fw, zb + fw, zt - fw, .11, S["glass"])
        # Back of the recess (dark room interior impression).
        self.plane(u0, u1, zb, zt, WALL_T, S["plinth"])
        if sill:
            self.box(u0 - .05, u1 + .05, zb - .05, zb, -.06, .12, S["trim"])
        if trim:
            self.box(u0 - .12, u0, zb, zt + .12, -.03, 0, S["trim"], front=True)
            self.box(u1, u1 + .12, zb, zt + .12, -.03, 0, S["trim"])
            self.box(u0, u1, zt, zt + .12, -.03, 0, S["trim"])
        if grille:
            n = max(3, int((u1 - u0) / .12))
            for k in range(1, n):
                uu = u0 + (u1 - u0) * k / n
                self.box(uu - .008, uu + .008, zb, zt, -.04, -.025, S["metal"])
            self.box(u0, u1, (zb + zt) / 2 - .01, (zb + zt) / 2 + .01, -.045, -.02, S["metal"])

    def door(self, o, mat=S["door"], step=True, transom=False):
        u0, u1, zb, zt = o["u0"], o["u1"], o["zb"], o["zt"]
        self.box(u0, u0 + .07, zb, zt, .03, .14, S["frame"])
        self.box(u1 - .07, u1, zb, zt, .03, .14, S["frame"])
        self.box(u0, u1, zt - .07, zt, .03, .14, S["frame"])
        top = zt - .07
        if transom:
            self.plane(u0 + .07, u1 - .07, top - .45, top, .1, S["glass"])
            self.box(u0 + .07, u1 - .07, top - .5, top - .45, .05, .12, S["frame"])
            top -= .5
        self.box(u0 + .07, u1 - .07, zb, top, .08, .12, mat)
        self.plane(u0, u1, zb, zt, WALL_T, S["plinth"])
        if step:
            self.box(u0 - .25, u1 + .25, zb - .17, zb, -.45, .05, S["plinth"])

    def shopfront(self, o, rng):
        u0, u1, zb, zt = o["u0"], o["u1"], o["zb"], o["zt"]
        # Roller-shutter box above, slatted shutter partially down, glass behind with aluminium mullions.
        self.box(u0 - .05, u1 + .05, zt, zt + .38, -.32, .02, S["metal"])
        down = rng.choice([0.0, 0.0, .35, 1.0])
        if down > 0:
            hz = zt - (zt - zb) * down
            self.box(u0 + .02, u1 - .02, hz, zt, -.08, -.04, S["metal"])
            for k in range(int((zt - hz) / .12)):
                z = zt - .12 * (k + 1)
                self.box(u0 + .02, u1 - .02, z, z + .015, -.09, -.04, S["metal"])
        n = max(2, int((u1 - u0) / 1.4))
        for k in range(n + 1):
            uu = u0 + (u1 - u0) * k / n
            self.box(uu - .03, uu + .03, zb, zt, .05, .12, S["frame"])
        self.box(u0, u1, zb, zb + .35, .03, .14, S["frame"])
        self.box(u0, u1, zt - .06, zt, .05, .12, S["frame"])
        self.plane(u0, u1, zb + .35, zt - .06, .1, S["shopglass"])
        self.plane(u0, u1, zb, zt, WALL_T, S["plinth"])
        self.box(u0 - .2, u1 + .2, zb - .12, zb, -.6, .05, S["plinth"])

    def rollup(self, o):
        u0, u1, zb, zt = o["u0"], o["u1"], o["zb"], o["zt"]
        self.box(u0 - .1, u1 + .1, zt, zt + .45, -.35, .05, S["metal"])
        self.box(u0, u0 + .08, zb, zt, -.05, .1, S["metal"])
        self.box(u1 - .08, u1, zb, zt, -.05, .1, S["metal"])
        self.plane(u0 + .08, u1 - .08, zb, zt, .02, S["metal"])
        for k in range(int((zt - zb) / .1)):
            z = zb + .1 * k
            self.box(u0 + .08, u1 - .08, z, z + .02, -.015, .02, S["metal"])
        self.plane(u0, u1, zb, zt, WALL_T, S["plinth"])

    def ac_unit(self, u, z):
        self.box(u - .4, u + .4, z, z + .55, -.32, 0, S["sign"])
        for k in range(5):
            self.box(u - .35, u + .35, z + .08 + k * .09, z + .1 + k * .09, -.33, -.32, S["metal"])
        self.box(u - .38, u - .3, z - .25, z, -.3, 0, S["metal"])

    def sign(self, u0, u1, z0, z1):
        self.box(u0, u1, z0, z1, -.12, -.02, S["sign"])

    def awning(self, u0, u1, z, depth=1.2, drop=.35):
        P = self.P
        self.mb.quad(P(u0, z, 0), P(u1, z, 0), P(u1, z - drop, -depth), P(u0, z - drop, -depth), S["sign"])
        self.mb.quad(P(u0, z - drop, -depth), P(u1, z - drop, -depth), P(u1, z - drop - .25, -depth), P(u0, z - drop - .25, -depth), S["sign"])
        for uu in (u0 + .05, u1 - .05):
            self.box(uu - .02, uu + .02, z - drop - .05, z, -depth, -depth + .04, S["metal"])

    def balcony(self, u0, u1, z, depth=1.0):
        self.box(u0, u1, z - .15, z, -depth, 0, S["plinth"], bottom=True)
        n = max(4, int((u1 - u0) / .13))
        for k in range(n + 1):
            uu = u0 + (u1 - u0) * k / n
            self.box(uu - .01, uu + .01, z, z + 1.0, -depth + .02, -depth + .04, S["metal"])
        self.box(u0, u1, z + .98, z + 1.04, -depth, -depth + .06, S["metal"])
        for uu in (u0, u1 - .04):
            self.box(uu, uu + .04, z, z + 1.04, -depth, 0, S["metal"])

    def scaffold(self, z_top):
        L = self.L
        for uu in [k * 2.0 for k in range(int(L / 2.0) + 1)]:
            uu = min(uu, L - .05)
            for dep in (-.4, -1.4):
                self.box(uu, uu + .05, 0, z_top + 1.0, dep - .05, dep, S["metal"])
        z = 2.0
        while z < z_top + .5:
            self.box(0, L, z, z + .05, -1.45, -.35, S["metal"])
            self.box(0, L, z - .05, z, -1.4, -.4, S["door"])
            z += 2.0


# ---------------------------------------------------------------- façade layout

def openings_for(L, floors, ground_h, fh, rng, kind="residential", door_u=None, shop=False, big_door=False, sparse=False):
    """Returns per-floor opening lists: [(floor_z0, floor_z1, [openings])]."""
    out = []
    z = 0.0
    for f in range(floors):
        h = ground_h if f == 0 else fh
        ops = []
        if f == 0 and big_door:
            bw = min(L * .6, rng.choice([3.5, 4.0, 4.5, 5.0]))
            c = L / 2 + rng.uniform(-L * .1, L * .1)
            ops.append({"u0": c - bw / 2, "u1": c + bw / 2, "zb": 0.0, "zt": min(h - .6, 4.4), "kind": "rollup"})
            if L - bw > 3.0:
                du = c + bw / 2 + .8 if c < L / 2 else c - bw / 2 - 1.7
                ops.append({"u0": du, "u1": du + .9, "zb": 0.0, "zt": 2.1, "kind": "door"})
        elif f == 0 and shop:
            margin = .6
            dw = .9
            ops.append({"u0": margin, "u1": margin + dw, "zb": 0.0, "zt": 2.3, "kind": "door"})
            s0 = margin + dw + .4
            if L - s0 - .5 > 1.4:
                ops.append({"u0": s0, "u1": L - .5, "zb": 0.0, "zt": min(h - .5, 3.2), "kind": "shopfront"})
        else:
            spacing = rng.uniform(2.4, 3.2) if not sparse else rng.uniform(3.5, 5.0)
            n = max(1, int(L // spacing))
            ww = min(1.5, spacing * .5) if kind != "office" else min(2.0, spacing * .7)
            wh = rng.choice([1.2, 1.3, 1.4]) if kind != "office" else 1.6
            sill = 1.0 if kind != "office" else .8
            if f == 0:
                du = door_u if door_u is not None else (L / 2 if n % 2 == 0 else L * .25)
                ops.append({"u0": du - .45, "u1": du + .45, "zb": 0.0, "zt": 2.15, "kind": "door"})
            for k in range(n):
                cu = (k + .5) * L / n
                if f == 0 and abs(cu - (ops[0]["u0"] + .45)) < ww / 2 + .7:
                    continue
                if cu - ww / 2 < .35 or cu + ww / 2 > L - .35:
                    continue
                ops.append({"u0": cu - ww / 2, "u1": cu + ww / 2, "zb": z + sill, "zt": z + sill + wh, "kind": "window"})
        for o in ops:
            if o["kind"] != "window":
                o["zb"] += z
                o["zt"] += z
        out.append((z, z + h, ops))
        z += h
    return out


def build_facade(fac, bands, rng, style):
    """Emit walls + openings for one facade."""
    for z0, z1, ops in bands:
        fac.wall_band(z0, z1, ops)
        for o in ops:
            k = o["kind"]
            if k == "window":
                fac.window(o, trim=style.get("trim", False), grille=style.get("grille", False) and z0 < .1)
            elif k == "door":
                fac.door(o, transom=style.get("transom", False))
            elif k == "shopfront":
                fac.shopfront(o, rng)
            elif k == "rollup":
                fac.rollup(o)


# ---------------------------------------------------------------- roofs

def roof(mb, w, d, H, kind, rng, attached=True, front_parapet=0.0):
    """Roof on top of a w x d body whose walls end at height H."""
    oh = .55
    goh = .0 if attached else .35
    t = .14
    if kind in ("flat_parapet", "roofless_flat"):
        mb.quad((-w / 2 + WALL_T, -d / 2 + WALL_T, H - .1), (w / 2 - WALL_T, -d / 2 + WALL_T, H - .1),
                (w / 2 - WALL_T, d / 2 - WALL_T, H - .1), (-w / 2 + WALL_T, d / 2 - WALL_T, H - .1), S["roof"])
        ph = .9
        for (x0, y0, x1, y1) in ((-w / 2, -d / 2, w / 2, -d / 2 + .15), (-w / 2, d / 2 - .15, w / 2, d / 2),
                                 (-w / 2, -d / 2, -w / 2 + .15, d / 2), (w / 2 - .15, -d / 2, w / 2, d / 2)):
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, H, x1 - x0, y1 - y0, ph, S["facade"])
        mb.box(0, -d / 2 + .02, H + ph, w + .06, .24, .07, S["trim"])
        if rng.random() < .6:
            tx, ty = rng.uniform(-w / 2 + 1.5, w / 2 - 1.5), rng.uniform(0, d / 2 - 1.5)
            mb.box(tx, ty, H - .1, 1.6, 1.6, .5, S["plinth"])
            mb.cylinder(tx, ty, H + .4, .65, 1.1, 14, S["sign"])
        return H + ph
    if kind in ("gable_side", "gable_front", "gable_metal", "gable_brick", "gable_metal_broken"):
        along_x = kind != "gable_front"
        pitch = .30 if kind in ("gable_side", "gable_front", "gable_brick") else .12
        mat = S["roof"]
        span = d if along_x else w
        length = w if along_x else d
        rise = span / 2 * pitch
        # Two slabs with thickness, overhanging eaves; local axes a (along ridge), b (across).
        def P(a, b, z):
            return (a, b, z) if along_x else (b, a, z)
        a0, a1 = -length / 2 - goh, length / 2 + goh
        for side in (-1, 1):
            if kind == "gable_metal_broken" and side == 1:
                a1_eff = a0 + (a1 - a0) * .45
            else:
                a1_eff = a1
            be = side * (span / 2 + oh)
            ze = H - oh * pitch
            br = 0.0
            zr = H + rise
            top = [P(a0, be, ze + t), P(a1_eff, be, ze + t), P(a1_eff, br, zr + t), P(a0, br, zr + t)]
            bot = [P(a0, be, ze), P(a1_eff, be, ze), P(a1_eff, br, zr), P(a0, br, zr)]
            if (side == 1) == along_x:
                top = [top[1], top[0], top[3], top[2]]
                bot = [bot[1], bot[0], bot[3], bot[2]]
            if side == -1:
                mb.add_face(top[::-1] if along_x else top, mat)
            else:
                mb.add_face(top if along_x else top[::-1], mat)
            mb.add_face(bot if side == -1 else bot[::-1], mat)
            # fascia board along the eave
            mb.add_face([P(a0, be, ze - .12), P(a1_eff, be, ze - .12), P(a1_eff, be, ze + t), P(a0, be, ze + t)], S["trim"])
            # gutter + downpipes
            if kind in ("gable_side", "gable_front"):
                gb = side * (span / 2 + oh + .08)
                mb.box(*(P(0, gb, 0)[:2]), ze - .2, *((a1 - a0, .14) if along_x else (.14, a1 - a0)), .14, S["metal"], top=False)
                for aa in (a0 + .2, a1 - .2):
                    x, y, _ = P(aa, side * (span / 2 + .12), 0)
                    mb.cylinder(x, y, 0, .05, ze - .2, 8, S["metal"], top=False)
        # Gable end triangles (walls) and ridge cap.
        for aa in (-length / 2, length / 2):
            if kind == "gable_brick" and aa == (-length / 2 if not along_x else -length / 2):
                pass
            tri = [P(aa, -span / 2, H), P(aa, span / 2, H), P(aa, 0, H + rise)]
            mb.add_face(tri if (aa > 0) == along_x else tri[::-1], S["brick"] if kind == "gable_brick" else S["facade"])
        mb.box(*(P(0, 0, 0)[:2]), H + rise + t - .02, *((a1 - a0, .3) if along_x else (.3, a1 - a0)), .12, mat)
        if front_parapet > 0:
            # platibanda on the street façade hiding the roof (common on shops/workshops)
            mb.box(0, -d / 2 + .1, H, w, .2, front_parapet, S["facade"])
            mb.box(0, -d / 2 + .1, H + front_parapet, w + .08, .3, .08, S["trim"])
            if kind == "gable_brick":
                for k, frac in enumerate((.25, .5, .75)):
                    mb.box(0, -d / 2 + .1, H + front_parapet + .08, w * (1 - frac * .8), .2, .45 + k * .0, S["brick"])
        return H + rise + t
    if kind == "hip":
        oh2 = oh
        x0, x1, y0, y1 = -w / 2 - oh2, w / 2 + oh2, -d / 2 - oh2, d / 2 + oh2
        pitch = .32
        ze = H - oh2 * pitch
        if w >= d:
            rise = (y1 - y0) / 2 * pitch
            r0, r1 = (x0 + (y1 - y0) / 2, 0), (x1 - (y1 - y0) / 2, 0)
        else:
            rise = (x1 - x0) / 2 * pitch
            r0, r1 = (0, y0 + (x1 - x0) / 2), (0, y1 - (x1 - x0) / 2)
        zr = ze + rise
        A, B, C, D = (x0, y0, ze), (x1, y0, ze), (x1, y1, ze), (x0, y1, ze)
        R0, R1 = (r0[0], r0[1], zr), (r1[0], r1[1], zr)
        if w >= d:
            mb.add_face([A, B, R1, R0], S["roof"])
            mb.add_face([C, D, R0, R1], S["roof"])
            mb.add_face([B, C, R1], S["roof"])
            mb.add_face([D, A, R0], S["roof"])
        else:
            mb.add_face([B, C, R1, R0], S["roof"])
            mb.add_face([D, A, R0, R1], S["roof"])
            mb.add_face([A, B, R0], S["roof"])
            mb.add_face([C, D, R1], S["roof"])
        # soffit + fascia ring
        mb.add_face([D, C, B, A], S["trim"])
        for (p, q) in ((A, B), (B, C), (C, D), (D, A)):
            mb.add_face([p, q, (q[0], q[1], q[2] + .16), (p[0], p[1], p[2] + .16)], S["trim"])
        return zr
    if kind == "shed_metal":
        pitch = .1
        z_front = H + d * pitch + .3
        mb.add_face([(-w / 2 - .2, -d / 2 - .4, z_front), (-w / 2 - .2, d / 2 + .5, H), (w / 2 + .2, d / 2 + .5, H), (w / 2 + .2, -d / 2 - .4, z_front)][::-1], S["roof"])
        mb.add_face([(-w / 2 - .2, -d / 2 - .4, z_front - .1), (w / 2 + .2, -d / 2 - .4, z_front - .1), (w / 2 + .2, d / 2 + .5, H - .1), (-w / 2 - .2, d / 2 + .5, H - .1)][::-1], S["roof"])
        for sx in (-1, 1):
            tri = [(sx * w / 2, -d / 2, H), (sx * w / 2, d / 2, H), (sx * w / 2, -d / 2, z_front)]
            mb.add_face(tri if sx > 0 else tri[::-1], S["facade"])
        if front_parapet > 0:
            mb.box(0, -d / 2 + .1, H, w, .2, front_parapet + d * pitch + .4, S["facade"])
        return z_front
    if kind == "sawtooth":
        n = max(2, int(d // 7))
        step = d / n
        for k in range(n):
            y0 = -d / 2 + k * step
            y1 = y0 + step
            zt = H + 2.2
            mb.add_face([(-w / 2, y0, H), (w / 2, y0, H), (w / 2, y1, zt), (-w / 2, y1, zt)], S["roof"])
            mb.add_face([(w / 2, y1, H), (-w / 2, y1, H), (-w / 2, y1, zt), (w / 2, y1, zt)], S["glass"])
            for sx in (-1, 1):
                tri = [(sx * w / 2, y0, H), (sx * w / 2, y1, H), (sx * w / 2, y1, zt)]
                mb.add_face(tri if sx > 0 else tri[::-1], S["facade"])
        if front_parapet > 0:
            mb.box(0, -d / 2 + .1, H, w, .2, front_parapet + 2.4, S["facade"])
        return H + 2.2
    if kind == "barrel":
        segs = 12
        rise = w * .18
        pts = []
        for k in range(segs + 1):
            a = math.pi * k / segs
            pts.append((-math.cos(a) * (w / 2 + .3), H + math.sin(a) * rise))
        for k in range(segs):
            (x0, z0), (x1, z1) = pts[k], pts[k + 1]
            mb.add_face([(x1, -d / 2 - .3, z1), (x0, -d / 2 - .3, z0), (x0, d / 2 + .3, z0), (x1, d / 2 + .3, z1)], S["roof"])
        for yy, flip in ((-d / 2, False), (d / 2, True)):
            poly = [(x, yy, z) for x, z in pts[1:-1]] + [(w / 2, yy, H), (-w / 2, yy, H)]
            mb.add_face(poly[::-1] if not flip else poly, S["facade"])
        return H + rise
    if kind == "roofless":
        # Walls end raggedly; a few exposed beams remain.
        for k in range(int(w // 1.2)):
            x = -w / 2 + .6 + k * 1.2
            mb.box(x, -d / 2 + .12, H, 1.2, .25, rng.uniform(-.8, .4) + .8, S["facade"])
        for k in range(int(d // 3)):
            y = -d / 2 + 1.5 + k * 3
            if rng.random() < .6:
                mb.box(0, y, H - .4, w - .5, .18, .25, S["door"])
        return H + .8
    return H


# ---------------------------------------------------------------- building

def building_mesh(mb, v, seed, detail="lod1"):
    """Emit a whole Old Town building variant v (dict from urban_fabric.OLDTOWN_VARIANTS) into mb."""
    rng = random.Random(seed)
    w, d = v["w"], v["d"]
    floors, fh, gh = v["floors"], v["fh"], v["ground_h"]
    H = gh + fh * (floors - 1)
    fam = v["family"]
    tags = set(v["tags"])
    attached = v["attached"]
    style = {"trim": fam in ("sobrado_estreito", "comercio_residencia", "predio_3pav") and rng.random() < .7,
             "grille": fam in ("casa_terrea", "sobrado_estreito", "comercio_residencia") and rng.random() < .6,
             "transom": fam in ("sobrado_estreito", "predio_3pav", "predio_4a6") and rng.random() < .5}
    # Foundation/plinth goes below ground to absorb slopes.
    mb.box(0, 0, -1.5, w - 2 * WALL_T, d - 2 * WALL_T, H + 1.5 - .12, S["plinth"], top=False)
    mb.box(0, 0, -1.5, w + .06, d + .06, 1.5 + .45, S["plinth"], top=False)
    kind = "office" if fam in ("pequeno_comercial",) else "residential"
    big = "big_door" in tags
    shop = "shop" in tags
    sparse = fam in ("armazem", "deposito", "oficina")
    front = Facade(mb, (-w / 2, -d / 2), (1, 0), (0, -1), w)
    bands = openings_for(w, floors, gh, fh, rng, kind, shop=shop, big_door=big, sparse=sparse)
    build_facade(front, bands, rng, style)
    back = Facade(mb, (w / 2, d / 2), (-1, 0), (0, 1), w)
    bands_b = openings_for(w, floors, gh, fh, rng, kind, door_u=w * .7, sparse=True)
    build_facade(back, bands_b, rng, {})
    for sx in (1, -1):
        side = Facade(mb, (sx * w / 2, -sx * d / 2), (0, sx), (sx, 0), d)
        if attached:
            for z0, z1, _ in bands:
                side.wall_band(z0, z1, [])
        else:
            bands_s = openings_for(d, floors, gh, fh, rng, kind, door_u=d * .75, sparse=True)
            build_facade(side, bands_s, rng, {})
    # Mouldings: string courses between floors and a cornice on the street front.
    if style["trim"] or fam in ("predio_3pav", "predio_4a6"):
        z = gh
        for f in range(1, floors):
            front.box(-.02, w + .02, z - .08, z + .08, -.06, 0, S["trim"])
            z += fh
        front.box(-.05, w + .05, H - .35, H, -.22, 0, S["trim"])
    if shop and rng.random() < .75:
        front.sign(.5, w - .5, gh - .05, gh + .55)
    if shop and rng.random() < .35:
        front.awning(.4, w - .4, gh - .1)
    if fam == "predio_4a6" and rng.random() < .6:
        z = gh + fh
        for f in range(1, floors):
            cu = w / 2
            front.balcony(cu - 1.4, cu + 1.4, z - .02)
            z += fh
    if floors >= 2 and rng.random() < .55:
        for _ in range(rng.randint(1, 3)):
            front.ac_unit(rng.uniform(.8, w - .8), gh + fh * rng.randint(0, floors - 2) + 2.0)
    if "scaffold" in tags:
        front.scaffold(H)
    roof_kind = v["roof"]
    parapet = 0.0
    if roof_kind in ("gable_metal", "shed_metal", "sawtooth", "gable_metal_broken") and fam in ("oficina", "deposito", "abandonada_reformada"):
        parapet = 1.2
    if roof_kind == "gable_brick":
        parapet = 1.0
    if fam == "comercio_residencia" and roof_kind.startswith("gable"):
        parapet = .9
    top = roof(mb, w, d, H, roof_kind, rng, attached=attached, front_parapet=parapet)
    return top


def variant_materials(v, seed):
    """Material names for SLOT_NAMES of a background variant (deterministic per variant)."""
    rng = random.Random(seed * 7 + 3)
    fam = v["family"]
    facade = rng.choice(["reboco_antigo", "reboco_pintado", "reboco_pintado", "tijolo_pintado"])
    if fam == "armazem":
        facade = "tijolo_aparente"
    if fam in ("oficina", "deposito"):
        facade = rng.choice(["concreto_pintado", "reboco_antigo", "tijolo_aparente"])
    if fam == "pequeno_comercial":
        facade = rng.choice(["reboco_pintado", "reboco_pastilha"])
    roof = {"gable_side": "ceramica_telha", "gable_front": "ceramica_telha", "hip": "ceramica_telha", "gable_brick": "telha_fibrocimento",
            "gable_metal": "telha_metalica", "shed_metal": "telha_fibrocimento", "sawtooth": "telha_fibrocimento", "barrel": "telha_metalica",
            "gable_metal_broken": "telha_metalica", "flat_parapet": "concreto", "roofless": "concreto"}[v["roof"]]
    frame = rng.choice(["madeira_pintada", "aluminio", "aco_pintado_verde"]) if fam not in ("pequeno_comercial",) else "aluminio"
    door = rng.choice(["madeira_pintada", "aco_pintado_cinza", "aco_pintado_verde"])
    return [facade, "concreto_pintado", frame, "vidro", roof, "concreto", door, "metal_galvanizado", "plastico", "ferrugem", "vidro_vitrine", "tijolo_aparente"]
