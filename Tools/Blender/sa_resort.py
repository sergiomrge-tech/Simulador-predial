"""Grand Aurora resort kit (requires bpy through sa_bl / sa_materials): luxury coastal-tropical architecture helpers.

Language: warm travertine and white lime plaster, teak slats and decks, bronze/brass details, floor-to-ceiling glass with glass
balustrades, deep eaves, roof gardens, stepped terraces with water. Everything builds into sa_bl.MeshBuilder with the shared slot list
below, in world coordinates (X east, Y north, Z up). A Frame maps building-local (u along the facade, d depth inward, z up) to world.
"""
import math

import sa_bl

SLOT_NAMES = ["travertino", "estuque", "teca", "brise", "vidro", "latao", "basalto", "terracota", "azulejo", "palha",
              "aco_preto", "marmore", "concreto", "tecido", "luz", "madeira_escura", "verde"]
S = {n: i for i, n in enumerate(SLOT_NAMES)}

# New (clean, expensive) materials; same spec schema as sa_materials.LIB
LIB_RESORT = {
    "travertino":      {"family": "pedra", "c1": (.80, .74, .62), "c2": (.70, .63, .52), "rough": (.45, .70), "scale": 1.0, "bump": .35, "pattern": "tiles", "tile": (.9, .6, .006), "mortar": (.62, .56, .46), "grime": .12, "dirt": .08, "texel": 1024},
    "estuque":         {"family": "reboco", "c1": (.93, .91, .86), "c2": (.86, .84, .78), "rough": (.65, .85), "scale": 1.2, "bump": .12, "pattern": "noise", "grime": .12, "dirt": .12, "texel": 512},
    "teca":            {"family": "madeira", "c1": (.52, .34, .19), "c2": (.40, .25, .14), "rough": (.45, .70), "scale": 1.0, "bump": .25, "pattern": "wave", "grime": .1, "dirt": .05, "texel": 1024},
    "brise":           {"family": "madeira", "c1": (.44, .28, .15), "c2": (.33, .20, .11), "rough": (.40, .62), "scale": 1.0, "bump": .2, "pattern": "wave", "grime": .1, "dirt": .05, "texel": 512},
    "vidro":           {"family": "metal", "c1": (.38, .56, .66), "c2": (.26, .42, .52), "rough": (.03, .08), "scale": 2.0, "bump": .0, "pattern": "noise", "metal": .8, "grime": .02, "dirt": .02, "texel": 256},
    "latao":           {"family": "metal", "c1": (.72, .55, .26), "c2": (.58, .42, .18), "rough": (.22, .40), "scale": 6.0, "bump": .03, "pattern": "noise", "metal": 1.0, "grime": .08, "dirt": .05, "texel": 512},
    "basalto":         {"family": "pedra", "c1": (.13, .13, .14), "c2": (.08, .08, .09), "rough": (.35, .65), "scale": 2.0, "bump": .5, "pattern": "noise", "grime": .1, "dirt": .1, "texel": 512},
    "terracota":       {"family": "ceramica", "c1": (.62, .31, .18), "c2": (.50, .24, .14), "rough": (.55, .80), "scale": 1.0, "bump": .6, "pattern": "tiles", "tile": (.22, .38, .02), "grime": .12, "dirt": .05, "texel": 512},
    "azulejo":         {"family": "ceramica", "c1": (.10, .56, .62), "c2": (.07, .44, .52), "rough": (.10, .25), "scale": 1.0, "bump": .1, "pattern": "tiles", "tile": (.12, .12, .004), "mortar": (.75, .78, .76), "grime": .05, "dirt": .03, "texel": 512},
    "palha":           {"family": "cobertura", "c1": (.62, .50, .28), "c2": (.45, .34, .18), "rough": (.85, .98), "scale": 1.0, "bump": .8, "pattern": "corrugated", "grime": .2, "dirt": .1, "texel": 512},
    "aco_preto":       {"family": "metal", "c1": (.04, .04, .045), "c2": (.025, .025, .03), "rough": (.35, .6), "scale": 3.0, "bump": .04, "pattern": "noise", "metal": .85, "grime": .05, "dirt": .03, "texel": 512},
    "marmore":         {"family": "pedra", "c1": (.92, .91, .89), "c2": (.80, .79, .78), "rough": (.12, .30), "scale": 1.0, "bump": .05, "pattern": "tiles", "tile": (.8, .8, .004), "mortar": (.7, .7, .7), "grime": .03, "dirt": .02, "texel": 1024},
    "concreto":        {"family": "concreto", "c1": (.72, .71, .68), "c2": (.62, .61, .58), "rough": (.6, .8), "scale": 1.4, "bump": .1, "pattern": "noise", "grime": .1, "dirt": .1, "texel": 512},
    "tecido":          {"family": "tecido", "c1": (.94, .92, .86), "c2": (.86, .84, .78), "rough": (.85, .98), "scale": 6.0, "bump": .15, "pattern": "noise", "grime": .05, "dirt": .05, "texel": 512},
    "madeira_escura":  {"family": "madeira", "c1": (.20, .12, .07), "c2": (.13, .08, .05), "rough": (.35, .6), "scale": 1.0, "bump": .2, "pattern": "wave", "grime": .05, "dirt": .03, "texel": 512},
    "verde":           {"family": "terreno", "c1": (.20, .36, .13), "c2": (.12, .24, .08), "rough": (.8, .95), "scale": .5, "bump": .3, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 256},
    "buganvile":       {"family": "vegetacao", "c1": (.78, .10, .36), "c2": (.55, .06, .26), "rough": (.7, .9), "scale": .5, "bump": .3, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "texel": 256},
    "agua_piscina":    {"family": "agua", "c1": (.14, .80, .84), "c2": (.05, .50, .64), "rough": (.02, .06), "scale": .06, "bump": .08, "pattern": "noise", "grime": 0.0, "dirt": 0.0, "spec": 1.0, "texel": 256},
}


def extend_library(lib):
    import sa_materials
    for name, spec in LIB_RESORT.items():
        if name not in lib:
            lib[name] = sa_materials.build_material(name, spec)
    wm = lib.get("agua_piscina")
    if wm is not None and wm.node_tree is not None:
        for n in wm.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Color"].default_value = (.10, .70, .78, 1)
                n.inputs["Emission Strength"].default_value = 0.35
    if "luz_quente" not in lib:
        import bpy
        m = bpy.data.materials.new("luz_quente")
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (1.0, .85, .6, 1)
        b.inputs["Emission Color"].default_value = (1.0, .78, .5, 1)
        b.inputs["Emission Strength"].default_value = 0.0      # turned on by the night look
        lib["luz_quente"] = m
    return lib


def materials_for(lib):
    """Material list in slot order (index = S[name]); 'luz' maps to the warm emissive."""
    return [lib["luz_quente"] if n == "luz" else lib[n] for n in SLOT_NAMES]


class Frame:
    """Building-local frame: u along the facade (0..L), d depth measured inward from the facade line, z up (absolute)."""

    def __init__(self, mb, origin, angle=0.0):
        self.mb = mb
        self.o = origin
        self.c, self.s = math.cos(angle), math.sin(angle)

    def shift(self, du=0.0, dd=0.0):
        """New frame whose origin is moved by (du, dd) in this frame's own axes."""
        x, y, _ = self.P(du, dd, 0.0)
        f = Frame(self.mb, (x, y), 0.0)
        f.c, f.s = self.c, self.s
        return f

    def P(self, u, d, z):
        # u runs along (c, s); depth d runs along (-s, c): d > 0 is "behind" the facade, so the outside is d < 0.
        return (self.o[0] + u * self.c - d * self.s, self.o[1] + u * self.s + d * self.c, z)

    def box(self, u0, u1, d0, d1, z0, z1, mat, top=True, bottom=False, front=True, back=True, sides=True):
        if u1 - u0 < 1e-4 or d1 - d0 < 1e-4 or z1 - z0 < 1e-4:
            return
        P, mb = self.P, self.mb
        c = [P(u0, d0, z0), P(u1, d0, z0), P(u1, d1, z0), P(u0, d1, z0), P(u0, d0, z1), P(u1, d0, z1), P(u1, d1, z1), P(u0, d1, z1)]
        if front:
            mb.quad(c[0], c[1], c[5], c[4], mat)
        if sides:
            mb.quad(c[1], c[2], c[6], c[5], mat)
            mb.quad(c[3], c[0], c[4], c[7], mat)
        if back:
            mb.quad(c[2], c[3], c[7], c[6], mat)
        if top:
            mb.quad(c[4], c[5], c[6], c[7], mat)
        if bottom:
            mb.quad(c[3], c[2], c[1], c[0], mat)

    def quad(self, p0, p1, p2, p3, mat):
        self.mb.quad(self.P(*p0), self.P(*p1), self.P(*p2), self.P(*p3), mat)

    def cyl(self, u, d, z0, r, h, segs=14, mat=0, top=True):
        x, y, _ = self.P(u, d, z0)
        self.mb.cylinder(x, y, z0, r, h, segs, mat, top)


# ------------------------------------------------------------------------------------------------ guest wing

def wing(fr, L, D, z0, floors, fh=3.4, bd=2.2, seed=0, brise=0.33, roof_garden=True, ground_open=False, loggia=True, end_pavilions=True, pitched=False):
    """Stepped-balcony guest wing. Facade (balconies) looks to d < 0. L along u, D deep, floors of height fh."""
    import random
    rng = random.Random(seed)
    T = 0.28
    if loggia:                                                                                      # ground floor: open travertine arcade with a lounge behind
        lh = 4.6
        a = fr.shift(0.0, -bd)
        cnt = max(2, int(round(L / 4.5)))
        arcade(a, L, cnt, z0, z0 + lh, depth=0.9, pier=0.8)
        fr.box(0.2, L - 0.2, -bd + 0.9, 0.2, z0, z0 + lh, S["marmore"], top=False, front=False, back=False, sides=False)
        fr.box(0.1, L - 0.1, 0.0, 0.18, z0 + 0.1, z0 + lh - 0.2, S["vidro"], top=False, back=False, sides=False)
        fr.box(0, L, 0, D, z0 + 0.0, z0 + lh, S["estuque"], front=False, top=False)
        z0 = z0 + lh
        floors -= 1
    bay = 4.5
    nb = max(1, int(L // bay))
    bw = L / nb
    for f in range(floors):
        z = z0 + f * fh
        # structural slab: main + balcony cantilever, with a thin travertine edge band
        fr.box(0, L, 0, D, z, z + T, S["concreto"], top=False, bottom=True)
        fr.box(-0.2, L + 0.2, -bd, 0.0, z, z + T, S["estuque"])
        fr.box(-0.2, L + 0.2, -bd - 0.04, -bd, z, z + T + 0.04, S["travertino"], top=False)
        for b in range(nb):
            u0, u1 = b * bw, (b + 1) * bw
            zc = z + T
            # glazed room front: recessed 0.35 behind the slab edge, mullions at the bay edges, solid privacy walls between bays
            fr.box(u0 + 0.12, u1 - 0.12, 0.05, 0.12, zc, zc + fh - T - 0.1, S["vidro"], top=False, back=False, sides=False)
            fr.box(u0 + 0.10, u0 + 0.20, 0.0, 0.18, zc, zc + fh - T, S["aco_preto"], top=False)
            fr.box(u0, u0 + 0.12, -bd, 0.12, zc, zc + fh - T, S["estuque"])             # privacy wall between balconies
            # balcony: glass balustrade + brass handrail
            rail_z = zc + 1.05
            fr.box(u0 + 0.12, u1 - 0.12, -bd + 0.10, -bd + 0.16, zc + 0.1, rail_z, S["vidro"], top=False, back=False, sides=False)
            fr.box(u0 + 0.12, u1 - 0.12, -bd + 0.08, -bd + 0.18, rail_z, rail_z + 0.05, S["latao"])
            # timber brise-soleil: a sliding screen covering part of the balcony front, fins every 0.14 m
            if rng.random() < brise:
                su0 = u0 + bw * rng.choice((0.1, 0.4))
                su1 = su0 + bw * 0.5
                n = int((su1 - su0) / 0.14)
                for k in range(n):
                    fu = su0 + k * 0.14
                    fr.box(fu, fu + 0.06, -bd + 0.22, -bd + 0.34, zc, zc + fh - T - 0.1, S["brise"], top=False, bottom=False)
            # lounge chair and planter on some balconies (life, scale)
            if rng.random() < 0.55:
                fr.box(u0 + 0.7, u0 + 1.6, -bd + 0.6, -bd + 1.6, zc, zc + 0.35, S["tecido"])
                fr.box(u0 + 0.7, u0 + 1.6, -bd + 1.4, -bd + 1.6, zc + 0.35, zc + 0.75, S["tecido"])
            if rng.random() < 0.45:
                fr.box(u1 - 1.0, u1 - 0.3, -bd + 0.2, -bd + 0.8, zc, zc + 0.5, S["basalto"])
        # end walls
        fr.box(-0.12, 0.12, -bd, D, z + T, z + fh, S["estuque"])
        fr.box(L - 0.12, L + 0.12, -bd, D, z + T, z + fh, S["estuque"])
    # roof: thin slab, deep eave, planted roof garden behind a travertine parapet
    zr = z0 + floors * fh
    if pitched:                                                                                     # whole-wing terracotta hip roof (varies the skyline)
        fr.box(-0.6, L + 0.6, -bd - 1.0, D + 0.6, zr, zr + 0.35, S["concreto"], bottom=True)
        hip_roof(fr, -1.2, L + 1.2, -bd - 1.8, D + 1.2, zr + 0.35, 5.0, S["terracota"], ridge=0.12)
        return zr + 5.4
    if end_pavilions:                                                                               # taller gabled corner pavilions (rhythm in the skyline)
        for (ua, ub) in ((-0.6, 7.5), (L - 7.5, L + 0.6)):
            fr.box(ua + 0.6, ub - 0.6, -bd, D, zr, zr + 3.4, S["estuque"])
            hip_roof(fr, ua - 0.9, ub + 0.9, -bd - 1.5, D + 1.0, zr + 3.4, 2.6, S["terracota"])
        fr.box(7.5, L - 7.5, -bd - 1.0, -bd - 0.9, zr + 0.35, zr + 0.75, S["travertino"])
    fr.box(-0.6, L + 0.6, -bd - 1.0, D + 0.6, zr, zr + 0.35, S["concreto"], bottom=True)
    if not end_pavilions:
        fr.box(-0.6, L + 0.6, -bd - 1.0, -bd - 0.9, zr + 0.35, zr + 0.75, S["travertino"])
    if roof_garden:
        fr.box(7.8, L - 7.8, -bd + 0.2, D - 0.5, zr + 0.35, zr + 0.7, S["verde"]) if end_pavilions else fr.box(0.5, L - 0.5, -bd + 0.2, D - 0.5, zr + 0.35, zr + 0.7, S["verde"])
        for k in range(int(L // 6)):
            fr.box(1.0 + k * 6, 4.8 + k * 6, 0.5, 2.5, zr + 0.55, zr + 1.1, S["vidro"])      # solar skylight bands
    return zr


def hip_roof(fr, u0, u1, d0, d1, zr, rise, mat, ridge=0.28):
    """Hipped roof: four sloped planes to a short ridge, with a thin fascia."""
    L, D = u1 - u0, d1 - d0
    cu0, cu1 = u0 + L * ridge, u1 - L * ridge
    cd0, cd1 = d0 + D * ridge, d1 - D * ridge
    top = zr + rise
    fr.quad((u0, d0, zr), (u1, d0, zr), (cu1, cd0, top), (cu0, cd0, top), mat)
    fr.quad((u1, d1, zr), (u0, d1, zr), (cu0, cd1, top), (cu1, cd1, top), mat)
    fr.quad((u0, d1, zr), (u0, d0, zr), (cu0, cd0, top), (cu0, cd1, top), mat)
    fr.quad((u1, d0, zr), (u1, d1, zr), (cu1, cd1, top), (cu1, cd0, top), mat)
    fr.quad((cu0, cd0, top), (cu1, cd0, top), (cu1, cd1, top), (cu0, cd1, top), mat)
    fr.box(u0 - 0.05, u1 + 0.05, d0 - 0.05, d1 + 0.05, zr - 0.22, zr + 0.06, S["estuque"], top=False)


# ------------------------------------------------------------------------------------------------ lobby pavilion

def lobby(fr, L, D, z0, H=11.0):
    """Grand hall: stone plinth, double-height glass front, round columns, huge hipped roof with deep eaves and a glazed lantern."""
    plinth = 0.7
    fr.box(-3, L + 3, -9, D + 2, z0, z0 + plinth, S["travertino"], bottom=True)                   # raised plaza under the front eave
    fr.box(0, L, 0, D, z0 + plinth, z0 + plinth + 0.2, S["marmore"])                              # polished floor
    zf = z0 + plinth + 0.2
    # walls: solid travertine back and side wings, glass front wall with bronze mullions
    fr.box(0, L, D - 0.6, D, zf, zf + H, S["travertino"], front=False)
    for side in (0, L - 0.6):
        fr.box(side, side + 0.6, 0, D, zf, zf + H, S["travertino"])
    n = int(L // 2.2)
    for k in range(1, n):
        u = k * L / n
        fr.box(u - 0.06, u + 0.06, 0.0, 0.22, zf, zf + H - 0.2, S["latao"], top=False)
    fr.box(0.6, L - 0.6, 0.05, 0.12, zf, zf + H - 0.2, S["vidro"], top=False, back=False, sides=False)
    fr.box(0.6, L - 0.6, -0.1, 0.3, zf + 4.4, zf + 4.65, S["latao"])                               # transom
    # interior: coffered timber ceiling, reception desk, lounge groups, planters and a great chandelier
    fr.box(0.6, L - 0.6, 0.6, D - 0.6, zf + H - 0.25, zf + H - 0.05, S["teca"], top=False, bottom=True)
    for k in range(7):
        u = 6.0 + k * (L - 12.0) / 6
        fr.box(u - 0.15, u + 0.15, 0.6, D - 0.6, zf + H - 0.55, zf + H - 0.25, S["madeira_escura"], top=False)
    fr.box(L / 2 - 6, L / 2 + 6, D - 5.5, D - 3.5, zf, zf + 1.15, S["marmore"])                         # reception desk
    fr.box(L / 2 - 6.1, L / 2 + 6.1, D - 5.6, D - 3.4, zf + 1.15, zf + 1.25, S["latao"])
    for gu in (L * 0.2, L * 0.8):
        fr.box(gu - 3.2, gu + 3.2, 4.0, 8.4, zf, zf + 0.02, S["tecido"])
        for dx, dd in ((-2.6, 0.0), (2.6, 0.0), (0.0, -1.9), (0.0, 1.9)):
            fr.box(gu + dx - 1.0, gu + dx + 1.0, 6.2 + dd - 0.9, 6.2 + dd + 0.9, zf, zf + 0.45, S["tecido"])
            fr.box(gu + dx - 1.0, gu + dx + 1.0, 6.2 + dd - 0.9, 6.2 + dd + 0.9, zf + 0.45, zf + 0.9, S["madeira_escura"], top=False)
        fr.cyl(gu, 6.2, zf, 0.9, 0.45, 14, S["marmore"])
    for pu in (L * 0.38, L * 0.62):
        fr.cyl(pu, 3.2, zf, 0.7, 1.0, 14, S["basalto"])
    for k in range(3):
        fr.cyl(L / 2, D / 2 - 1.0 + (k - 1) * 0.0, zf + H - 1.0 - k * 0.6, 3.4 - k * 0.9, 0.12, 24, S["latao"])
    fr.cyl(L / 2, D / 2 - 1.0, zf + H - 4.6, 0.55, 3.6, 14, S["luz"])
    # colonnade on the front (round columns on stone bases)
    nc = int(L // 4.5)
    for k in range(nc + 1):
        u = k * L / nc
        fr.box(u - 0.45, u + 0.45, -3.9, -3.0, zf - plinth + 0.7, zf - plinth + 1.3, S["travertino"])
        fr.cyl(u, -3.45, zf - plinth + 1.3, 0.34, H - 0.8, 18, S["estuque"])
        fr.box(u - 0.5, u + 0.5, -3.95, -2.95, zf + H - 0.9, zf + H - 0.5, S["travertino"])
    # roof: four sloped planes (hip) with a thick fascia, terracotta tiles, central glazed lantern
    zr = zf + H
    ov = 4.2
    u0, u1, d0, d1 = -ov, L + ov, -4.0 - ov, D + ov
    rise = 4.2
    cu0, cu1, cd0, cd1 = L * 0.30, L * 0.70, D * 0.22 - 1.0, D * 0.78
    top = zr + rise
    rt, fa = S["terracota"], S["estuque"]
    fr.box(u0, u1, d0, d1, zr - 0.35, zr, S["teca"], top=False, bottom=True)                        # warm timber soffit under the eaves
    fr.quad((u0, d0, zr), (u1, d0, zr), (cu1, cd0, top), (cu0, cd0, top), rt)
    fr.quad((u1, d1, zr), (u0, d1, zr), (cu0, cd1, top), (cu1, cd1, top), rt)
    fr.quad((u0, d1, zr), (u0, d0, zr), (cu0, cd0, top), (cu0, cd1, top), rt)
    fr.quad((u1, d0, zr), (u1, d1, zr), (cu1, cd1, top), (cu1, cd0, top), rt)
    for (a, b) in (((u0, d0), (u1, d0)), ((u1, d0), (u1, d1)), ((u1, d1), (u0, d1)), ((u0, d1), (u0, d0))):       # fascia ring
        fr.quad((a[0], a[1], zr - 0.35), (b[0], b[1], zr - 0.35), (b[0], b[1], zr + 0.12), (a[0], a[1], zr + 0.12), fa)
    fr.box(cu0, cu1, cd0, cd1, top, top + 0.9, S["vidro"], top=False)                                # lantern glass
    fr.box(cu0 - 0.4, cu1 + 0.4, cd0 - 0.4, cd1 + 0.4, top + 0.9, top + 1.2, S["aco_preto"])
    return zr


# ------------------------------------------------------------------------------------------------ tower with lantern crown

def tower(fr, L, D, z0, floors=14, fh=3.3):
    """Torre Aurora: slim block whose floor plates step back every 4 floors; corner balconies in teak; a glazed lantern crown (the lighthouse echo)."""
    T = 0.3
    cur_l, cur_d, ou, od = L, D, 0.0, 0.0
    for f in range(floors):
        if f and f % 4 == 0:
            ou += 1.4; od += 1.0
            cur_l, cur_d = L - 2 * ou, D - 2 * od
        z = z0 + f * fh
        u0, u1, d0, d1 = ou, ou + cur_l, od, od + cur_d
        fr.box(u0 - 0.3, u1 + 0.3, d0 - 0.3, d1 + 0.3, z, z + T, S["travertino"], bottom=True)       # projecting slab edge
        fr.box(u0, u1, d0, d1, z + T, z + fh, S["vidro"], top=False)                                  # glass skin
        npier = max(2, int(cur_l // 6.0))
        for k in range(npier + 1):                                                                     # travertine piers carry the facade rhythm
            u = u0 + k * cur_l / npier
            fr.box(u - 0.35, u + 0.35, d0 - 0.18, d0 + 0.5, z, z + fh, S["travertino"])
            fr.box(u - 0.35, u + 0.35, d1 - 0.5, d1 + 0.18, z, z + fh, S["travertino"])
        for dd in (d0, d1 - 0.5):
            fr.box(u0 - 0.18, u0 + 0.5, dd, dd + 0.5, z, z + fh, S["travertino"])
            fr.box(u1 - 0.5, u1 + 0.18, dd, dd + 0.5, z, z + fh, S["travertino"])
        for k in range(int(cur_l // 1.6) + 1):                                                         # mullions
            u = u0 + k * cur_l / max(1, int(cur_l // 1.6))
            fr.box(u - 0.04, u + 0.04, d0 - 0.06, d0 + 0.02, z + T, z + fh, S["aco_preto"], top=False)
            fr.box(u - 0.04, u + 0.04, d1 - 0.02, d1 + 0.06, z + T, z + fh, S["aco_preto"], top=False)
        fr.box(u0 - 0.05, u0 + 0.12, d0, d1, z + T, z + fh, S["estuque"])                              # solid end walls
        fr.box(u1 - 0.12, u1 + 0.05, d0, d1, z + T, z + fh, S["estuque"])
        if f % 2 == 1:                                                                                  # teak balcony ribbon on the sea side
            fr.box(u0, u1, d0 - 1.6, d0 - 0.3, z, z + 0.22, S["teca"])
            fr.box(u0, u1, d0 - 1.65, d0 - 1.59, z + 0.22, z + 1.2, S["vidro"], top=False, back=False, sides=False)
            fr.box(u0, u1, d0 - 1.70, d0 - 1.56, z + 1.2, z + 1.26, S["latao"])
    zt = z0 + floors * fh
    u0, u1, d0, d1 = ou, ou + cur_l, od, od + cur_d
    fr.box(u0 - 0.8, u1 + 0.8, d0 - 0.8, d1 + 0.8, zt, zt + 0.5, S["travertino"], bottom=True)       # crown plate
    # lantern: glazed lighthouse-like crown with warm light, brass ribs and a slender mast
    cu, cd = (u0 + u1) / 2, (d0 + d1) / 2
    fr.box(cu - 3.2, cu + 3.2, cd - 2.6, cd + 2.6, zt + 0.5, zt + 6.0, S["luz"], top=False)
    for k in range(-3, 4):
        fr.box(cu + k * 0.9 - 0.05, cu + k * 0.9 + 0.05, cd - 2.7, cd - 2.55, zt + 0.5, zt + 6.0, S["latao"], top=False)
        fr.box(cu + k * 0.9 - 0.05, cu + k * 0.9 + 0.05, cd + 2.55, cd + 2.7, zt + 0.5, zt + 6.0, S["latao"], top=False)
    fr.box(cu - 3.6, cu + 3.6, cd - 3.0, cd + 3.0, zt + 6.0, zt + 6.5, S["latao"])
    fr.cyl(cu, cd, zt + 6.5, 0.12, 9.0, 8, S["latao"])
    return zt + 15.5


# ------------------------------------------------------------------------------------------------ water, stone, shade

def retaining_wall(fr, L, z_lo, z_hi, thick=0.7, planter=True):
    """Travertine retaining wall along u at d = 0 (outside d < 0), with coping and a planter strip on top."""
    fr.box(0, L, 0, thick, z_lo, z_hi, S["travertino"])
    fr.box(-0.05, L + 0.05, -0.08, thick + 0.1, z_hi, z_hi + 0.14, S["marmore"])
    if planter:
        fr.box(0.2, L - 0.2, 0.0, thick, z_hi + 0.14, z_hi + 0.55, S["verde"])


def stairs(fr, L, run, z_lo, z_hi, tread=0.34):
    """Monumental stair climbing toward +d (u along facade). Returns nothing; treads in travertine with brass nosing."""
    n = max(2, int(round((z_hi - z_lo) / 0.16)))
    rise = (z_hi - z_lo) / n
    step_d = run / n
    for k in range(n):
        d0 = k * step_d
        z = z_lo + (k + 1) * rise
        fr.box(0, L, d0, d0 + step_d + 0.02, z_lo, z, S["travertino"], top=True)
        fr.box(0, L, d0 - 0.01, d0 + 0.03, z - 0.03, z, S["latao"], top=False)
    fr.box(-0.3, 0.0, 0, run, z_lo, z_hi + 0.9, S["travertino"])                                    # cheek walls
    fr.box(L, L + 0.3, 0, run, z_lo, z_hi + 0.9, S["travertino"])


def pool(mb_arch, mb_water, x0, y0, x1, y1, z_top, depth=1.4, infinity_side=None, coping=0.45, tile=S["azulejo"]):
    """Pool with travertine coping, tiled basin and a water surface 0.06 below the rim. infinity_side: 's','n','e','w' or None."""
    zw = z_top - 0.06
    inner = (x0 + coping, y0 + coping, x1 - coping, y1 - coping)
    if infinity_side:
        ix0, iy0, ix1, iy1 = inner
        if infinity_side == "s":
            iy0 = y0 - 0.2
        elif infinity_side == "n":
            iy1 = y1 + 0.2
        elif infinity_side == "e":
            ix1 = x1 + 0.2
        else:
            ix0 = x0 - 0.2
        inner = (ix0, iy0, ix1, iy1)
    ix0, iy0, ix1, iy1 = inner
    zb = z_top - depth
    # coping ring (skipped on the infinity edge)
    def b(a0, b0, a1, b1, z0, z1, m):
        mb_arch.box((a0 + a1) / 2, (b0 + b1) / 2, z0, a1 - a0, b1 - b0, z1 - z0, m)
    if infinity_side != "w":
        b(x0, y0, ix0, y1, z_top - 0.25, z_top, S["travertino"])
    if infinity_side != "e":
        b(ix1, y0, x1, y1, z_top - 0.25, z_top, S["travertino"])
    if infinity_side != "s":
        b(ix0, y0, ix1, iy0, z_top - 0.25, z_top, S["travertino"])
    if infinity_side != "n":
        b(ix0, iy1, ix1, y1, z_top - 0.25, z_top, S["travertino"])
    # basin: floor + walls (tiled) seen through the water
    b(ix0, iy0, ix1, iy1, zb - 0.2, zb, tile)
    for (a0, b0, a1, b1) in ((ix0 - 0.2, iy0, ix0, iy1), (ix1, iy0, ix1 + 0.2, iy1), (ix0, iy0 - 0.2, ix1, iy0), (ix0, iy1, ix1, iy1 + 0.2)):
        b(a0, b0, a1, b1, zb, z_top - 0.25, tile)
    if infinity_side:                                                                              # catch trough below the edge
        if infinity_side == "s":
            b(x0, y0 - 1.6, x1, y0 - 0.2, z_top - 1.4, z_top - 1.1, tile)
            b(x0, y0 - 1.8, x1, y0 - 1.6, z_top - 1.4, z_top - 0.9, S["travertino"])
    mb_water.quad((ix0, iy0, zw), (ix1, iy0, zw), (ix1, iy1, zw), (ix0, iy1, zw), 0)
    return zw


def pergola(fr, L, D, z0, h=3.0, slat=0.12, canopy=False):
    """Teak pergola: 4+ posts, primary beams, closely spaced slats; optional white fabric canopy."""
    nu = max(2, int(L // 3.5) + 1)
    for k in range(nu):
        u = k * L / (nu - 1)
        for d in (0.0, D):
            fr.box(u - 0.1, u + 0.1, d - 0.1, d + 0.1, z0, z0 + h, S["teca"])
        fr.box(u - 0.09, u + 0.09, -0.15, D + 0.15, z0 + h, z0 + h + 0.26, S["teca"])
    n = int(L / (slat * 3))
    for k in range(n + 1):
        u = k * L / n
        fr.box(u - slat / 2, u + slat / 2, -0.4, D + 0.4, z0 + h + 0.26, z0 + h + 0.38, S["brise"])
    if canopy:
        fr.box(0, L, 0, D, z0 + h + 0.4, z0 + h + 0.43, S["tecido"])


def thatch_roof(fr, cu, cd, z, r, h, segs=12):
    """Round palapa: conical thatch roof over a central mast (beach cabana)."""
    x, y, _ = fr.P(cu, cd, z)
    mb = fr.mb
    ring = [(x + r * math.cos(2 * math.pi * k / segs), y + r * math.sin(2 * math.pi * k / segs), z) for k in range(segs)]
    apex = (x, y, z + h)
    for k in range(segs):
        mb.add_face([ring[k], ring[(k + 1) % segs], apex], S["palha"])
    mb.cylinder(x, y, z - 2.4, 0.07, 2.4 + h * 0.9, 8, S["madeira_escura"])


def villa(fr, L, D, z0, seed=0):
    """Bangalô: stone plinth, glass living room facing the sea, flat roof slab with deep eave and teak pergola, private plunge pool and deck."""
    fr.box(-1, L + 1, -7.5, D + 0.6, z0, z0 + 0.5, S["travertino"], bottom=True)                    # terrace platform
    fr.box(0, L, 0, D, z0 + 0.5, z0 + 3.4, S["estuque"])                                           # solid core
    fr.box(0.4, L - 0.4, -0.1, 0.1, z0 + 0.7, z0 + 3.2, S["vidro"], top=False, back=False, sides=False)
    for k in range(5):
        u = 0.4 + k * (L - 0.8) / 4
        fr.box(u - 0.05, u + 0.05, -0.15, 0.1, z0 + 0.5, z0 + 3.3, S["aco_preto"], top=False)
    fr.box(-1.0, L + 1.0, -3.5, D + 0.6, z0 + 3.4, z0 + 3.7, S["concreto"], bottom=True)           # roof slab with a 3.5 m eave
    fr.box(-1.0, L + 1.0, -3.5, -3.4, z0 + 3.7, z0 + 3.95, S["travertino"])
    fr.box(0.4, L - 0.4, -3.0, 0, z0 + 0.5, z0 + 0.58, S["teca"])                                   # teak deck under the eave
    fr.box(0.6, L - 0.6, -7.2, -3.6, z0 + 0.5, z0 + 0.62, S["teca"])
    return z0 + 3.95


# ------------------------------------------------------------------------------------------------ landscape

def arch_prism(fr, u0, u1, z_spring, rise, d0, d1, mat, n=10):
    """Semicircular-ish arch opening cut: returns the spandrel fill above an arch (a prism whose lower edge follows the arch curve)."""
    w = u1 - u0
    pts = []
    for k in range(n + 1):
        t = k / n
        u = u0 + t * w
        z = z_spring + rise * math.sin(math.pi * t)
        pts.append((u, z))
    return pts


def arcade(fr, L, n, z0, z1, depth=0.9, pier=0.9, mat_pier=None, mat_fill=None):
    """Travertine arcade wall along u at d = 0..depth: n arches between piers, a lintel band and cornice above. Arch openings are left
    open (or glazed by the caller). Reads as a grand Mediterranean/colonial base under each terrace."""
    mp = S["travertino"] if mat_pier is None else mat_pier
    bay = L / n
    spring = z0 + (z1 - z0) * 0.62
    top = z1
    rise = (z1 - z0) * 0.26
    for k in range(n + 1):
        u = k * bay
        fr.box(u - pier / 2, u + pier / 2, 0, depth, z0, spring, mp)
    for k in range(n):
        ua, ub = k * bay + pier / 2, (k + 1) * bay - pier / 2
        pts = arch_prism(fr, ua, ub, spring, rise, 0, depth, mp, n=10)
        # spandrel: vertical strips from the arch curve up to the lintel
        for (p0, p1) in zip(pts, pts[1:]):
            fr.quad((p0[0], 0, p0[1]), (p1[0], 0, p1[1]), (p1[0], 0, top), (p0[0], 0, top), mp)
            fr.quad((p1[0], depth, p1[1]), (p0[0], depth, p0[1]), (p0[0], depth, top), (p1[0], depth, top), mp)
            fr.quad((p0[0], depth, p0[1]), (p1[0], depth, p1[1]), (p1[0], 0, p1[1]), (p0[0], 0, p0[1]), mp)      # soffit of the arch
    fr.box(-0.2, L + 0.2, -0.12, depth + 0.12, top, top + 0.22, S["marmore"])                                   # cornice
    fr.box(-0.1, L + 0.1, -0.06, depth + 0.06, top + 0.22, top + 0.6, S["travertino"])                          # parapet base
    for k in range(int(L // 0.55)):                                                                              # balusters
        fr.box(k * 0.55 + 0.12, k * 0.55 + 0.30, -0.04, 0.14, top + 0.6, top + 1.15, S["marmore"], top=False)
    fr.box(-0.1, L + 0.1, -0.08, 0.18, top + 1.15, top + 1.27, S["marmore"])


def palm_royal(mb_trunk, mb_leaf, base, h=12.0, lean=(0.0, 0.0), seed=0, crown=5.2):
    """Royal palm: tapered, gently bent, ringed trunk with a crown of arching fronds. mb_trunk uses mat 0, mb_leaf mat 0 (separate objects)."""
    import random
    rng = random.Random(seed)
    bx, by, bz = base
    lx, ly = lean
    segs, ring = 12, 8
    prev = None
    for k in range(segs + 1):
        t = k / segs
        cx = bx + lx * t * t * h
        cy = by + ly * t * t * h
        r = 0.34 - 0.13 * t if t > 0.03 else 0.42
        z = bz + h * t
        cur = []
        for j in range(ring):
            a = 2 * math.pi * j / ring
            cur.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        if prev is not None:
            for j in range(ring):
                i2 = (j + 1) % ring
                mb_trunk.quad(prev[j], prev[i2], cur[i2], cur[j], 0)
        prev = cur
    tx, ty, tz = bx + lx * h, by + ly * h, bz + h
    nf = 16
    for k in range(nf):
        a = 2 * math.pi * k / nf + rng.uniform(-.12, .12)
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        length = crown * rng.uniform(.85, 1.15)
        droop = rng.uniform(1.1, 2.3)
        up = rng.uniform(.8, 1.8) if k % 2 else rng.uniform(1.8, 2.8)
        pts = []
        for s in range(7):
            t = s / 6
            pts.append((tx + dx * length * t, ty + dy * length * t, tz + up * math.sin(t * 2.2) - droop * t * t))
        for s in range(6):
            w0 = 0.55 * math.sin(math.pi * min(1.0, (s + .4) / 6)) + .06
            w1 = 0.55 * math.sin(math.pi * min(1.0, (s + 1.4) / 6)) + .06
            a0, a1 = pts[s], pts[s + 1]
            mb_leaf.quad((a0[0] - px * w0, a0[1] - py * w0, a0[2]), (a0[0] + px * w0, a0[1] + py * w0, a0[2]),
                         (a1[0] + px * w1, a1[1] + py * w1, a1[2]), (a1[0] - px * w1, a1[1] - py * w1, a1[2]), 0)
            mb_leaf.quad((a1[0] - px * w1, a1[1] - py * w1, a1[2]), (a1[0] + px * w1, a1[1] + py * w1, a1[2]),
                         (a0[0] + px * w0, a0[1] + py * w0, a0[2]), (a0[0] - px * w0, a0[1] - py * w0, a0[2]), 0)


def lounger(fr, u, d, z, rot_u=1.0):
    """Sun lounger with a towel and a small side table (pool-deck life)."""
    fr.box(u, u + 0.75, d, d + 2.0, z + 0.22, z + 0.34, S["teca"])
    fr.box(u + 0.05, u + 0.7, d + 0.02, d + 0.1, z, z + 0.22, S["aco_preto"], top=False)
    fr.box(u + 0.05, u + 0.7, d + 1.9, d + 1.98, z, z + 0.22, S["aco_preto"], top=False)
    fr.box(u + 0.04, u + 0.71, d + 0.15, d + 1.55, z + 0.34, z + 0.40, S["tecido"])
    fr.box(u + 0.04, u + 0.71, d + 1.55, d + 2.0, z + 0.34, z + 0.7, S["tecido"])


def umbrella(fr, u, d, z, r=1.7, h=2.6, segs=10):
    """Parasol: slim pole and a white fabric cone."""
    x, y, _ = fr.P(u, d, z)
    fr.mb.cylinder(x, y, z, 0.03, h, 6, S["latao"])
    ring = [(x + r * math.cos(2 * math.pi * k / segs), y + r * math.sin(2 * math.pi * k / segs), z + h - 0.45) for k in range(segs)]
    apex = (x, y, z + h + 0.1)
    for k in range(segs):
        fr.mb.add_face([ring[k], ring[(k + 1) % segs], apex], S["tecido"])


def fountain(fr, u, d, z, r=4.2):
    """Tiered stone fountain basin (water quads are added by the caller)."""
    x, y, _ = fr.P(u, d, z)
    mb = fr.mb
    mb.cylinder(x, y, z, r + 0.5, 0.55, 28, S["travertino"], top=False)
    mb.cylinder(x, y, z + 0.55, r + 0.62, 0.14, 28, S["marmore"])
    mb.cylinder(x, y, z, 0.5, 2.2, 14, S["travertino"])
    mb.cylinder(x, y, z + 2.2, 1.6, 0.25, 20, S["travertino"])
    mb.cylinder(x, y, z + 2.45, 0.2, 1.2, 10, S["travertino"])
    mb.cylinder(x, y, z + 3.6, 0.8, 0.15, 16, S["travertino"])
    return (x, y, z + 0.5, r)


def lamp(fr, u, d, z, h=4.2):
    """Bronze garden lamp post with a warm glowing lantern (emissive at night)."""
    x, y, _ = fr.P(u, d, z)
    fr.mb.cylinder(x, y, z, 0.08, h, 8, S["aco_preto"])
    fr.mb.cylinder(x, y, z + h, 0.22, 0.45, 8, S["luz"])
    fr.mb.cylinder(x, y, z + h + 0.45, 0.28, 0.08, 8, S["aco_preto"])


def dome(fr, u, d, z, r=4.5, drum_h=3.2, segs=20, rings=7, mat=None):
    """Drum with arched openings (read as blind arches) and a terracotta/copper dome with a brass finial."""
    mat = S["terracota"] if mat is None else mat
    x, y, _ = fr.P(u, d, z)
    mb = fr.mb
    mb.cylinder(x, y, z, r + 0.25, drum_h, segs, S["estuque"], top=False)
    mb.cylinder(x, y, z + drum_h, r + 0.4, 0.3, segs, S["travertino"])
    zc = z + drum_h + 0.3
    prev = [(x + r * math.cos(2 * math.pi * k / segs), y + r * math.sin(2 * math.pi * k / segs), zc) for k in range(segs)]
    for i in range(1, rings + 1):
        phi = (math.pi / 2) * i / rings
        rr, hh = r * math.cos(phi), r * 0.85 * math.sin(phi)
        cur = [(x + rr * math.cos(2 * math.pi * k / segs), y + rr * math.sin(2 * math.pi * k / segs), zc + hh) for k in range(segs)]
        for k in range(segs):
            j = (k + 1) % segs
            mb.quad(prev[k], prev[j], cur[j], cur[k], mat)
        prev = cur
    mb.cylinder(x, y, zc + r * 0.85, 0.08, 1.6, 6, S["latao"])


def campanile(fr, u, d, z, w=7.0, h=26.0):
    """Square bell tower: travertine shaft with string courses, a belvedere with arches, a pyramidal terracotta roof and a brass finial."""
    fr.box(u - w / 2, u + w / 2, d - w / 2, d + w / 2, z, z + h, S["travertino"])
    for k in range(1, 5):
        zz = z + k * h / 5.5
        fr.box(u - w / 2 - 0.25, u + w / 2 + 0.25, d - w / 2 - 0.25, d + w / 2 + 0.25, zz, zz + 0.35, S["marmore"])
    for side in (-1, 1):                                                                           # slit windows on all four faces
        fr.box(u - 0.4, u + 0.4, d + side * (w / 2 + 0.02) - 0.03, d + side * (w / 2 + 0.02) + 0.03, z + h * 0.25, z + h * 0.25 + 3.0, S["vidro"], top=False, bottom=False, front=True, back=True, sides=False)
        fr.box(u + side * (w / 2 + 0.02) - 0.03, u + side * (w / 2 + 0.02) + 0.03, d - 0.4, d + 0.4, z + h * 0.25, z + h * 0.25 + 3.0, S["vidro"], top=False, bottom=False, front=True, back=True, sides=False)
    zb = z + h
    fr.box(u - w / 2 - 0.6, u + w / 2 + 0.6, d - w / 2 - 0.6, d + w / 2 + 0.6, zb, zb + 0.5, S["travertino"], bottom=True)
    for ix in (-1, 1):                                                                             # belvedere piers with open arches
        for iz in (-1, 1):
            fr.box(u + ix * (w / 2 - 0.4) - 0.4, u + ix * (w / 2 - 0.4) + 0.4, d + iz * (w / 2 - 0.4) - 0.4, d + iz * (w / 2 - 0.4) + 0.4, zb + 0.5, zb + 4.6, S["travertino"])
    fr.box(u - w / 2 - 0.4, u + w / 2 + 0.4, d - w / 2 - 0.4, d + w / 2 + 0.4, zb + 4.6, zb + 5.0, S["travertino"], bottom=True)
    rx = w / 2 + 1.6
    apex = fr.P(u, d, zb + 5.0 + 6.0)
    corners = [fr.P(u - rx, d - rx, zb + 5.0), fr.P(u + rx, d - rx, zb + 5.0), fr.P(u + rx, d + rx, zb + 5.0), fr.P(u - rx, d + rx, zb + 5.0)]
    for k in range(4):
        fr.mb.add_face([corners[k], corners[(k + 1) % 4], apex], S["terracota"])
    x, y, _ = fr.P(u, d, zb + 11.0)
    fr.mb.cylinder(x, y, zb + 11.0, 0.1, 2.6, 6, S["latao"])
    fr.box(u - 1.0, u + 1.0, d - 1.0, d + 1.0, zb + 0.5, zb + 3.6, S["luz"], top=False, bottom=False)       # glowing lantern inside the belvedere


def shade_tree(trunk_mb, crown_mb, base, h=7.0, r=4.2, seed=0):
    """Flame-tree style umbrella crown: a short bent trunk and a broad crown made of overlapping soft masses."""
    import random
    rng = random.Random(seed)
    bx, by, bz = base
    bend = (rng.uniform(-.8, .8), rng.uniform(-.8, .8))
    prev = None
    for k in range(5):
        t = k / 4
        cx, cy, z = bx + bend[0] * t * t, by + bend[1] * t * t, bz + h * t
        rad = 0.38 - 0.16 * t
        cur = [(cx + rad * math.cos(2 * math.pi * j / 7), cy + rad * math.sin(2 * math.pi * j / 7), z) for j in range(7)]
        if prev:
            for j in range(7):
                trunk_mb.quad(prev[j], prev[(j + 1) % 7], cur[(j + 1) % 7], cur[j], 0)
        prev = cur
    tx, ty, tz = bx + bend[0], by + bend[1], bz + h
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-.3, .3)
        rr = r * rng.uniform(.35, .75) if k else 0.0
        blob(crown_mb, (tx + rr * math.cos(a), ty + rr * math.sin(a), tz + rng.uniform(-.2, 1.0)), r * rng.uniform(.5, .75), 0, seed=rng.randrange(10000), rings=9, segs=16)


def parterre(fr, L, D, z, flowers_mb, seed=0, cell=6.0):
    """Formal garden: clipped verde hedges in a grid of beds, marble gravel paths, bougainvillea blobs in the beds."""
    import random
    rng = random.Random(seed)
    nu, nd = max(1, int(L // cell)), max(1, int(D // cell))
    cu, cd = L / nu, D / nd
    fr.box(0, L, 0, D, z, z + 0.04, S["marmore"])
    for i in range(nu + 1):
        fr.box(i * cu - 0.3, i * cu + 0.3, 0, D, z + 0.04, z + 0.75, S["verde"])
    for j in range(nd + 1):
        fr.box(0, L, j * cd - 0.3, j * cd + 0.3, z + 0.04, z + 0.75, S["verde"])
    for i in range(nu):
        for j in range(nd):
            x, y, _ = fr.P((i + .5) * cu, (j + .5) * cd, z)
            fr.box(i * cu + 0.35, (i + 1) * cu - 0.35, j * cd + 0.35, (j + 1) * cd - 0.35, z + 0.04, z + 0.25, S["madeira_escura"])
            for k in range(3):
                blob(flowers_mb, (x + rng.uniform(-1.2, 1.2), y + rng.uniform(-1.2, 1.2), z + 0.4), rng.uniform(.35, .6), 0, seed=rng.randrange(1000), rings=4, segs=7)


def blob(mb, c, r, mat, seed=0, rings=5, segs=9):
    """Soft rounded shrub/hedge mass: a noisy UV sphere."""
    import random
    rng = random.Random(seed)
    cx, cy, cz = c
    pts = []
    for i in range(rings + 1):
        phi = math.pi * i / rings
        row = []
        for k in range(segs):
            th = 2 * math.pi * k / segs
            rr = r * (0.82 + 0.3 * rng.random())
            row.append((cx + rr * math.sin(phi) * math.cos(th), cy + rr * math.sin(phi) * math.sin(th), cz + rr * 0.72 * math.cos(phi)))
        pts.append(row)
    for i in range(rings):
        for k in range(segs):
            j = (k + 1) % segs
            mb.add_face([pts[i][k], pts[i][j], pts[i + 1][j], pts[i + 1][k]], mat)
