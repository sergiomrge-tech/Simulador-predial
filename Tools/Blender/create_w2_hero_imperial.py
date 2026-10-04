"""W2 — Teatro Imperial: production base of the heritage theatre (Chapter II client, obsolete electrical system).

Run:
blender --background --factory-startup --python Tools/Blender/create_w2_hero_imperial.py -- --root PROJECT_ROOT

Output: ArtSource/Blender/World/OldTown/Heroes/W2_imperial.blend (local frame under W2_imperial_ROOT, front at -Y).
Volumes from oldtown_heroes_v1.json (foyer, auditorium, fly tower, backstage dock, portico). Dressing-room wings (camarins,
listed in the structure registry) fill the lot between the fly tower and the side paths so the stage door has a wall.
Modelled inside: foyer + box office, plateia with balcony and booth, stage with proscenium/curtain/fly gallery/gridiron,
backstage with the old electrical board next to a half-done retrofit. Visual brief: aged heritage, partial reforms,
old installations living with retrofit (REGISTRO_ESTRUTURAS, IMPERIAL).
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
import sa_materials  # noqa: E402
from sa_w2 import HeroScene, text_mesh, wall_x, wall_y  # noqa: E402

H = HeroScene(root, "imperial", "W2_imperial", building_index=1)
hero, L, Lrect = H.hero, H.L, H.Lrect
P = "W2_imperial__"
rng = random.Random(zlib.crc32(b"imperial-w2"))
for name, spec in {"veludo_vermelho": {"family": "tecido", "c1": (.42, .05, .06), "c2": (.30, .03, .04), "rough": (.8, .95), "scale": 30.0, "bump": .15,
                                       "pattern": "noise", "grime": .35, "dirt": .1, "texel": 1024},
                   "madeira_palco": {"family": "madeira", "c1": (.20, .14, .09), "c2": (.13, .09, .06), "rough": (.55, .8), "scale": 1.0, "bump": .3,
                                     "pattern": "wave", "grime": .6, "dirt": .3, "texel": 1024},
                   "dourado_velho": {"family": "metal", "c1": (.52, .40, .18), "c2": (.36, .27, .12), "rough": (.35, .6), "scale": 5.0, "bump": .1,
                                     "pattern": "noise", "metal": .8, "grime": .6, "dirt": .2, "texel": 512},
                   "ardosia": {"family": "pedra", "c1": (.16, .17, .17), "c2": (.10, .11, .11), "rough": (.5, .7), "scale": 6.0, "bump": .1,
                               "pattern": "noise", "grime": .4, "dirt": .1, "texel": 512},
                   "lona_obra": {"family": "tecido", "c1": (.30, .36, .33), "c2": (.22, .27, .25), "rough": (.7, .9), "scale": 4.0, "bump": .2,
                                 "pattern": "noise", "grime": .5, "dirt": .3, "texel": 512}}.items():
    H.lib[name] = sa_materials.build_material(name, spec)
B = {b["role"]: Lrect(b["rect"]) for b in hero["buildings"]}
bh = {b["role"]: b for b in hero["buildings"]}
FO, AU, FT, BK = B["foyer"], B["auditorium"], B["fly_tower"], B["backstage_dock"]
STONE, BRICK = H.fixed("pedra_reboco_historico"), H.fixed("tijolo_aparente")
PLINTH = 1.05                       # raised heritage ground floor (portico platform level)
STAGE = .95                         # stage / backstage / dock level (1.1 m above the front stalls row)
FH_F = bh["foyer"]["fh"]
ZF = FH_F * bh["foyer"]["floors"]   # foyer cornice 12.9
ZA = bh["auditorium"]["fh"]         # auditorium eave 19
RA = 8.0                            # auditorium gable rise
ZT = bh["fly_tower"]["fh"]          # 33
ZB = bh["backstage_dock"]["fh"] * bh["backstage_dock"]["floors"]
WING = ((FT[2], FT[1], AU[2] - .25, FT[3]), (AU[0] + .25, FT[1], FT[0], FT[3]))  # camarins (local +x wing, -x wing)


# ---------------------------------------------------------------- helpers
def arch(mb, cx, y, zb, w, h, depth, m_frame, m_glass, out=-1, spandrel=None):
    """Round-headed window in a wall along X (outer face at y, exterior towards out*Y): moulded ring + jambs + glass."""
    r = w / 2
    zs = zb + h                                    # springing line
    n = 12
    ring_o, ring_i = r + .14, r
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        pi0 = (cx + math.cos(a0) * ring_i, zs + math.sin(a0) * ring_i)
        pi1 = (cx + math.cos(a1) * ring_i, zs + math.sin(a1) * ring_i)
        po0 = (cx + math.cos(a0) * ring_o, zs + math.sin(a0) * ring_o)
        po1 = (cx + math.cos(a1) * ring_o, zs + math.sin(a1) * ring_o)
        yf = y + out * .06
        mb.quad((po0[0], yf, po0[1]), (po1[0], yf, po1[1]), (pi1[0], yf, pi1[1]), (pi0[0], yf, pi0[1]), m_frame)
        mb.quad((pi0[0], yf, pi0[1]), (pi1[0], yf, pi1[1]), (pi1[0], y - out * depth, pi1[1]), (pi0[0], y - out * depth, pi0[1]), m_frame)
        yg = y - out * depth * .6
        mb.add_face([(cx, yg, zs), (pi0[0], yg, pi0[1]), (pi1[0], yg, pi1[1])], m_glass)
        if spandrel is not None:                    # close the rectangular wall opening above the arch
            corner = (cx + r, zs + r) if a0 < math.pi / 2 else (cx - r, zs + r)
            for yy in (y, y - out * depth):
                mb.add_face([(corner[0], yy, corner[1]), (pi1[0], yy, pi1[1]), (pi0[0], yy, pi0[1])], spandrel)
    for x in (cx - r - .07, cx + r + .07):
        mb.box(x, y + out * .03, zb, .14, .06, h, m_frame)
    mb.box(cx, y - out * depth * .6, zb, w, .02, h, m_glass)
    mb.box(cx, y + out * .05, zb - .12, w + .4, .22, .12, m_frame)          # sill
    for k in range(1, 4):                                                   # glazing bars
        mb.box(cx, y - out * depth * .6 + out * .01, zb + k * h / 4, w, .02, .03, m_frame)
    mb.box(cx, y - out * depth * .6 + out * .01, zb, .03, .02, h + r, m_frame)


def gable(mb, y, x0, x1, z0, rise, t, mat):
    """Triangular gable wall in the plane y (thickness t along Y)."""
    xm = (x0 + x1) / 2
    for yy, flip in ((y - t / 2, False), (y + t / 2, True)):
        tri = [(x0, yy, z0), (x1, yy, z0), (xm, yy, z0 + rise)]
        mb.add_face(tri[::-1] if flip else tri, mat)
    for (a, b) in (((x0, z0), (xm, z0 + rise)), ((xm, z0 + rise), (x1, z0))):
        mb.quad((a[0], y - t / 2, a[1]), (b[0], y - t / 2, b[1]), (b[0], y + t / 2, b[1]), (a[0], y + t / 2, a[1]), mat)


def balusters(mb, x0, x1, y, z, h, m):
    n = int((x1 - x0) / .32)
    mb.box((x0 + x1) / 2, y, z, x1 - x0, .4, .15, m)
    mb.box((x0 + x1) / 2, y, z + h - .14, x1 - x0 + .1, .46, .14, m)
    for k in range(n):
        x = x0 + .16 + k * (x1 - x0 - .32) / max(1, n - 1)
        mb.cylinder(x, y, z + .15, .07, h - .29, 6, m)


# ---------------------------------------------------------------- foyer (3 floors, classical front)
hw_f = (FO[2] - FO[0]) / 2
yF = FO[1]                                       # front face (local -Y)
win_x = [-30 + 6 * k for k in range(11)]
door_x = [-12.0, -6.0, 0.0, 6.0, 12.0]
bo = L(next(e["p"] for e in hero["entrances"] if e["role"] == "box_office"))
mb = sa_bl.MeshBuilder()
gf_ops = [(x, 2.4, PLINTH, PLINTH + 3.0) for x in door_x] + [(bo[0], 1.2, PLINTH + .9, PLINTH + 2.3)] + \
         [(s * x, 1.4, PLINTH + .9, PLINTH + 2.9) for s in (-1, 1) for x in (18.0, 27.0, 32.0) if abs(s * x - bo[0]) > 2]
f1_ops = [(x, 1.8, FH_F + .6, FH_F + .6 + 2.6 + .9) for x in win_x]
f2_ops = [(x, 1.4, 2 * FH_F + .7, 2 * FH_F + .7 + 1.7) for x in win_x]
wall_x(mb, yF + .3, FO[0], FO[2], .6, 0, FH_F, gf_ops, 0)
wall_x(mb, yF + .3, FO[0], FO[2], .6, FH_F, 2 * FH_F, f1_ops, 0)
wall_x(mb, yF + .3, FO[0], FO[2], .6, 2 * FH_F, ZF, f2_ops, 0)
for x in (FO[0] + .3, FO[2] - .3):
    wall_y(mb, x, FO[1] + .6, FO[3], .6, 0, ZF, [(FO[1] + 5.5, 1.4, FH_F + .9, FH_F + 3.1), (FO[1] + 5.5, 1.4, 2 * FH_F + .7, 2 * FH_F + 2.4)], 0)
for k in range(9):                                                                          # rusticated base grooves
    mb.box(0, yF - .02, .45 + k * .45, FO[2] - FO[0] + .04, .04, .05, 1)
for z, d, hh in ((FH_F - .1, .25, .3), (2 * FH_F - .1, .2, .25), (ZF - .2, .6, .45), (ZF + .25, .75, .25)):
    mb.box(0, yF - d / 2 + .02, z, FO[2] - FO[0] + 2 * d, d, hh, 2)                          # bands and main cornice
for x in [x0 + 3 for x0 in win_x[:-1]] + [FO[0] + .35, FO[2] - .35]:
    mb.box(x, yF - .1, FH_F + .2, .7, .2, ZF - FH_F - .4, 2)                                 # giant-order pilasters
    mb.box(x, yF - .16, ZF - .65, .9, .32, .45, 2)                                           # capitals
mb.box(0, (FO[1] + FO[3]) / 2, ZF, FO[2] - FO[0], FO[3] - FO[1], .25, 3)                     # foyer roof slab
balusters(mb, FO[0] + .5, -6.5, yF + .2, ZF + .5, 1.1, 2)
balusters(mb, 6.5, FO[2] - .5, yF + .2, ZF + .5, 1.1, 2)
mb.box(0, yF + .4, ZF + .5, 13.0, .8, 2.6, 0)                                                 # central attic
mb.box(0, yF + .2, ZF + 3.1, 13.6, 1.0, .3, 2)
for x in win_x[3:8]:
    balusters(mb, x - 1.2, x + 1.2, yF - .5, FH_F + .1, .9, 2)                                # balconettes, piano nobile
    mb.box(x, yF - .4, FH_F, 2.6, .8, .12, 2)
for x in win_x:                                                                              # 2nd floor window surrounds
    mb.box(x, yF - .04, 2 * FH_F + .55, 1.8, .08, .15, 2)
    mb.box(x, yF - .04, 2 * FH_F + 2.45, 1.9, .1, .22, 2)
H.mesh(P + "foyer_shell", mb, [STONE, "concreto_pintado", "pedra_reboco_historico", "concreto_aparente"], "Shell", bevel=.01, sa_layer="Architecture",
       note="fachada clássica: base rusticada, ordem gigante, janelas em arco, cornija e balaustrada")
mb = sa_bl.MeshBuilder()
for x in win_x:
    arch(mb, x, yF, FH_F + .6, 1.8, 2.6, .5, 0, 1, out=-1, spandrel=2)
for x in door_x:
    arch(mb, x, yF, PLINTH, 2.4, 3.0 - 1.2, .5, 0, 1, out=-1, spandrel=2)
for x in win_x:
    mb.box(x, yF + .3, 2 * FH_F + .7, 1.4, .03, 1.7, 1)
    mb.box(x, yF + .28, 2 * FH_F + .7, .05, .05, 1.7, 0)
for x, w, zb, zt in gf_ops[5:]:
    mb.box(x, yF + .3, zb, w, .03, zt - zb, 1)
    for k in range(9):
        mb.box(x - w / 2 + .08 + k * (w - .16) / 8, yF - .03, zb, .025, .025, zt - zb, 3)
H.mesh(P + "foyer_openings", mb, ["madeira_pintada", "vidro", STONE, "aco_pintado_cinza"], "Openings", sa_layer="Architecture")

# ---------------------------------------------------------------- portico (8 columns, entablature, pediment, steps)
pr = Lrect(hero["portico"]["rect"])
ph = hero["portico"]["h"]
mb = sa_bl.MeshBuilder()
mb.box(0, (pr[1] + yF) / 2, 0, pr[2] - pr[0] + 2, yF - pr[1] + 1.0, PLINTH, 0, bottom=True)   # platform
for k in range(5):                                                                           # steps down to the largo
    mb.box(0, pr[1] - .3 - k * .35, 0, pr[2] - pr[0] + 2 + k * .6, .35, PLINTH - k * .21, 0)
cols = [pr[0] + 3 + k * (pr[2] - pr[0] - 6) / (hero["portico"]["columns"] - 1) for k in range(hero["portico"]["columns"])]
cy = (pr[1] + pr[3]) / 2
for x in cols:
    mb.box(x, cy, PLINTH, 1.5, 1.5, .5, 1)                                                     # plinth
    mb.cylinder(x, cy, PLINTH + .5, .62, .3, 24, 1)                                           # torus
    mb.cylinder(x, cy, PLINTH + .8, .55, ph - PLINTH - 1.6, 24, 1)                            # shaft
    mb.cylinder(x, cy, ph - .8, .66, .35, 24, 1)                                              # echinus
    mb.box(x, cy, ph - .45, 1.5, 1.5, .45, 1)                                                 # abacus
xe0, xe1 = cols[0] - 1.2, cols[-1] + 1.2
mb.box(0, (pr[1] + yF) / 2 + .2, ph, xe1 - xe0, yF - pr[1] + .8, 1.4, 2)                      # entablature
mb.box(0, pr[1] - .05, ph + 1.4, xe1 - xe0 + .6, .5, .3, 2)
gable(mb, pr[1] + .1, xe0, xe1, ph + 1.7, 4.2, .6, 2)                                       # pediment
for side in (-1, 1):                                                                         # raking cornices
    a, b = (xe0 - .3, ph + 1.7), (0, ph + 1.7 + 4.4)
    if side > 0:
        a, b = (xe1 + .3, ph + 1.7), (0, ph + 1.7 + 4.4)
    n = 10
    for k in range(n):
        p0 = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
        p1 = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
        mb.box((p0[0] + p1[0]) / 2, pr[1] - .1, (p0[1] + p1[1]) / 2 - .15, abs(p1[0] - p0[0]) + .05, .6, .3, 2)
mb.box(0, (pr[1] + yF) / 2 + .2, ph + 1.7, xe1 - xe0, yF - pr[1] - .2, .2, 3, bottom=True)
H.mesh(P + "portico", mb, ["granito", "pedra_reboco_historico", STONE, "ceramica_telha"], "Shell", bevel=.012, sa_layer="Architecture")
t = text_mesh(P + "letters_attic", "TEATRO IMPERIAL", .85, H.C["Shell"], H.lib["aco_inox"], extrude=.04)
t.parent, t.location, t.rotation_euler = H.rootobj, (0, yF - .25, ZF + 1.3), (math.pi / 2, 0, 0)
t = text_mesh(P + "letters_date", "MCMXII", .5, H.C["Shell"], H.lib["pedra_reboco_historico"], extrude=.03)
t.parent, t.location, t.rotation_euler = H.rootobj, (0, pr[1] - .25, ph + 2.6), (math.pi / 2, 0, 0)

# ---------------------------------------------------------------- auditorium (walls, gables, tiled roof, side exits)
mb = sa_bl.MeshBuilder()
exits = [(-15.0, 1.8, PLINTH, PLINTH + 2.5), (0.0, 1.8, PLINTH, PLINTH + 2.5), (12.0, 1.8, PLINTH, PLINTH + 2.5)]
highs = [(y, 1.4, 12.5, 15.0) for y in (-18.0, -12.0, -6.0, 0.0, 6.0, 12.0, 18.0)]
for x in (AU[0] + .35, AU[2] - .35):
    wall_y(mb, x, AU[1], AU[3], .7, 0, ZA, exits + highs, 0)
    s = -1 if x < 0 else 1
    for y in [AU[1] + 1 + k * (AU[3] - AU[1] - 2) / 9 for k in range(10)]:
        mb.box(x + s * .4, y, .0, .2, .8, ZA - .5, 1)                                         # pilaster strips
    mb.box(x + s * .4, 0, ZA - .55, .55, AU[3] - AU[1] + .6, .55, 1)                          # eave cornice
    mb.box(x + s * .38, 0, 0, .1, AU[3] - AU[1], 1.0, 2)                                      # stone plinth band
    for y, w, zb, zt in exits:
        mb.box(x + s * 1.0, y, zt + .25, 1.6, 2.6, .12, 1)                                    # exit canopy
wall_x(mb, AU[1] + .35, AU[0] + .7, AU[2] - .7, .7, FH_F, ZA, [], 0)                           # front end wall above the foyer
gable(mb, AU[1] + .35, AU[0], AU[2], ZA, RA, .7, 0)
gable(mb, AU[3] - .35, AU[0], AU[2], ZA, RA, .7, 0)
mb.box(0, AU[1] - .05, ZA - .1, AU[2] - AU[0] + .6, .5, .4, 1)
H.mesh(P + "auditorium_shell", mb, [STONE, "pedra_reboco_historico", "granito"], "Shell", bevel=.01, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
for s in (-1, 1):
    x_e, x_r = (AU[0] - .6, 0.0) if s < 0 else (AU[2] + .6, 0.0)
    for (ya, yb) in ((AU[1] - .5, AU[3] + .5),):
        z_e, z_r = ZA - .2, ZA + RA + .15
        q = [(x_e, ya, z_e), (x_e, yb, z_e), (x_r, yb, z_r), (x_r, ya, z_r)]
        mb.add_face(q if s > 0 else q[::-1], 0)
        mb.add_face([(v[0], v[1], v[2] - .15) for v in (q[::-1] if s > 0 else q)], 0)
mb.box(0, 0, ZA + RA + .05, .6, AU[3] - AU[1] + 1.0, .25, 1)                                  # ridge
for x in (AU[0] - .45, AU[2] + .45):
    mb.box(x, 0, ZA - .45, .3, AU[3] - AU[1] + 1.0, .25, 2)                                  # gutters
    for y in (AU[1] + 2, AU[3] - 2):
        mb.cylinder(x, y, 0, .07, ZA - .4, 10, 2)
for it in hero["roof_items"]:                                                                # HVAC on steel platforms
    r = Lrect(it["rect"])
    xc, yc = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    zr = ZA + RA * (1 - abs(xc) / ((AU[2] - AU[0]) / 2))
    mb.box(xc, yc, zr - .2, r[2] - r[0] + 1.2, r[3] - r[1] + 1.2, .2, 3)
    for dx in (-1, 1):
        for dy in (-1, 1):
            mb.box(xc + dx * (r[2] - r[0]) / 2, yc + dy * (r[3] - r[1]) / 2, zr - 1.6, .15, .15, 1.6, 3)
    mb.box(xc, yc, zr, r[2] - r[0], r[3] - r[1], it["h"], 4)
    for k in range(3):
        mb.cylinder(xc - 2.2 + k * 2.2, yc, zr + it["h"], .7, .15, 16, 3)
    mb.box(xc, yc + (r[3] - r[1]) / 2 + .5, zr + .5, 1.0, 1.0, .8, 5)                         # duct into the roof
H.mesh(P + "auditorium_roof", mb, ["ceramica_telha", "ceramica_telha", "metal_galvanizado", "aco_pintado_cinza", "plastico_branco", "metal_galvanizado"],
       "Structure", sa_layer="Architecture", note="telhado cerâmico; HVAC é retrofit visível")

# ---------------------------------------------------------------- fly tower, camarins wings, backstage dock (brick)
mb = sa_bl.MeshBuilder()
for x in (FT[0] + .3, FT[2] - .3):                                                           # wide openings stage <-> wings
    wall_y(mb, x, FT[1], FT[3], .6, 0, ZT, [((FT[1] + FT[3]) / 2, 9.0, STAGE, STAGE + 7.0)], 0)
for y in (FT[1] + .3, FT[3] - .3):
    wall_x(mb, y, FT[0], FT[2], .6, ZA if y < FT[1] + 1 else ZB, ZT, [], 0)
for x in [FT[0] + 2 + k * (FT[2] - FT[0] - 4) / 6 for k in range(7)]:
    mb.box(x, FT[3] + .05, ZB, .9, .2, ZT - ZB - .6, 0)                                       # brick pilasters (rear)
for y in [FT[1] + 2 + k * (FT[3] - FT[1] - 4) / 4 for k in range(5)]:
    for x in (FT[0] - .05, FT[2] + .05):
        mb.box(x, y, 8.0, .2, .9, ZT - 8.6, 0)
for z in (ZT - .6, ZT - .2):
    mb.box((FT[0] + FT[2]) / 2, (FT[1] + FT[3]) / 2, z, FT[2] - FT[0] + .5, FT[3] - FT[1] + .5, .3 if z > ZT - .5 else .4, 1)
for x in (-6.0, 6.0):                                                                        # smoke hatches
    mb.box(x, (FT[1] + FT[3]) / 2, ZT, 3.0, 3.0, .7, 2)
for k in range(4):
    for x in (FT[0] - .02, FT[2] + .02):
        mb.box(x, FT[1] + 4 + k * 4.5, ZT - 3.5, .06, 1.6, 1.2, 3)                            # louvres
for k in range(int((ZT - ZB) / .3)):
    mb.box(FT[2] + .35, FT[3] - 3.0, ZB + .3 + k * .3, .04, .5, .04, 3)                        # cat ladder
mb.box((FT[0] + FT[2]) / 2, (FT[1] + FT[3]) / 2, ZT - .3, FT[2] - FT[0] - .2, FT[3] - FT[1] - .2, .3, 2, bottom=True)
H.mesh(P + "fly_tower", mb, [BRICK, "concreto_pintado", "metal_galvanizado", "aco_pintado_cinza"], "Shell", bevel=.008, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
sd = L(next(e["p"] for e in hero["entrances"] if e["role"] == "stage_door"))
for (x0, y0, x1, y1) in WING:
    outer = x1 if x1 > 0 else x0
    ops = [(y, 1.2, STAGE + .9 + f * 4.0, STAGE + 2.2 + f * 4.0) for f in range(2) for y in (y0 + 3, y0 + 8, y0 + 13, y0 + 18)]
    if outer < 0:
        ops = [o for o in ops if abs(o[0] - sd[1]) > 1.5 or o[2] > 4] + [(sd[1], 1.0, STAGE, STAGE + 2.1)]
    wall_y(mb, outer - (.3 if outer > 0 else -.3), y0, y1, .6, 0, 8.6, ops, 0)
    mb.box((x0 + x1) / 2, (y0 + y1) / 2, 8.6, x1 - x0, y1 - y0, .3, 1, bottom=True)
    mb.box((x0 + x1) / 2, (y0 + y1) / 2, 4.6, x1 - x0, y1 - y0, .2, 1, bottom=True)
    mb.box((x0 + x1) / 2, (y0 + y1) / 2, -.3, x1 - x0, y1 - y0, STAGE + .3, 1)                # wing floor at stage level
    if outer < 0:
        for k in range(4):                                                                   # steps up to the stage door
            mb.box(outer - .6 - k * .3, sd[1], -.2, .3, 1.6, STAGE + .2 - k * STAGE / 4, 1)
    for z in (4.5, 8.4):
        mb.box(outer, (y0 + y1) / 2, z, .12, y1 - y0, .2, 2)
    for k in range(3):                                                                       # retrofit AC units on the wing
        mb.box(outer + (.3 if outer > 0 else -.3), y0 + 4 + k * 6.5, 6.4, .3, .8, .55, 3)
H.mesh(P + "camarins_wings", mb, [BRICK, "concreto_aparente", "concreto_pintado", "plastico_branco"], "Shell", bevel=.006, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
dk = L(next(e["p"] for e in hero["entrances"] if e["role"] == "loading_dock"))
wall_x(mb, BK[3] - .3, BK[0], BK[2], .6, 0, ZB, [(dk[0], 5.0, STAGE, STAGE + 4.5)] + [(x, 1.2, STAGE + 1.0, STAGE + 2.2) for x in (-25, -15, 15, 25)]
       + [(x, 1.2, 4.5 + 1.2, 4.5 + 2.4) for x in (-25, -15, -5, 5, 15, 25)], 0)
for x in (BK[0] + .3, BK[2] - .3):
    wall_y(mb, x, BK[1], BK[3], .6, 0, ZB, [], 0)
mb.box((BK[0] + BK[2]) / 2, (BK[1] + BK[3]) / 2, ZB, BK[2] - BK[0], BK[3] - BK[1], .3, 1, bottom=True)
mb.box((BK[0] + BK[2]) / 2, (BK[1] + BK[3]) / 2, 4.5, BK[2] - BK[0], BK[3] - BK[1], .2, 1, bottom=True)
mb.box(dk[0], BK[3] + 1.5, 0, 9.0, 3.0, STAGE, 1)                                            # dock platform
for x in (dk[0] - 3.5, dk[0] + 3.5):
    mb.box(x, BK[3] + 3.05, .4, .35, .15, .6, 2)                                             # rubber bumpers
mb.box(dk[0], BK[3] + 1.6, STAGE + 4.7, 7.0, 3.2, .15, 3)                                    # dock canopy
mb.box(dk[0], BK[3] + .3, STAGE + 4.5, 5.6, .5, .6, 3)                                       # rollup drum
for k in range(int(4.2 / .1)):
    mb.box(dk[0], BK[3] - .25, STAGE + .2 + k * .1, 4.96, .03, .07, 4)
H.mesh(P + "backstage_dock", mb, [BRICK, "concreto_aparente", "borracha_preta", "aco_pintado_cinza", "metal_galvanizado"], "Shell", bevel=.006,
       sa_layer="Architecture")

# ---------------------------------------------------------------- interiors
R = {r["role"]: Lrect(r["rect"]) for r in hero["interior"]["rooms"]}
# Foyer: stone floor, two rows of columns, box office, side stairs, chandeliers.
mb = sa_bl.MeshBuilder()
mb.box(0, (FO[1] + FO[3]) / 2, 0, FO[2] - FO[0] - 1.2, FO[3] - FO[1] - .6, PLINTH + .02, 0)
for k, z in enumerate((FH_F, 2 * FH_F)):
    mb.box(0, (FO[1] + FO[3]) / 2, z, FO[2] - FO[0] - 1.2, FO[3] - FO[1] - .6, .3, 1, bottom=True)
    if k == 0:
        mb.box(0, (FO[1] + FO[3]) / 2 + 1.0, z - .01, 16.0, 4.5, .32, 2, top=False)           # void over the stair hall
for x in (-21.0, -15.0, -9.0, 9.0, 15.0, 21.0):
    mb.cylinder(x, FO[1] + 5.5, PLINTH, .35, FH_F - PLINTH, 16, 3)
b_ = R["bilheteria"]
wall_x(mb, b_[3], b_[0], b_[2], .15, PLINTH, FH_F, [((b_[0] + b_[2]) / 2, 1.6, PLINTH + 1.0, PLINTH + 1.7)], 4)
for x in (b_[0], b_[2]):
    wall_y(mb, x, b_[1], b_[3], .15, PLINTH, FH_F, [], 4)
mb.box((b_[0] + b_[2]) / 2, b_[3] - .25, PLINTH + .95, 1.8, .5, .05, 1)                       # ticket counter
for s in (-1, 1):                                                                            # imperial stair, two flights
    for k in range(16):
        mb.box(s * 3.0, FO[3] - 1.0 - k * .3, PLINTH + k * (FH_F - PLINTH) / 16, 3.0, .32, (FH_F - PLINTH) / 16 + .02, 0)
wall_x(mb, FO[3] - .3, FO[0] + .6, FO[2] - .6, .6, 0, FH_F, [(x, 2.0, PLINTH, PLINTH + 3.0) for x in (-20.0, -10.0, 10.0, 20.0)], 1)  # foyer / stalls wall with doors
H.mesh(P + "foyer_interior", mb, ["granito", "concreto_pintado", "parede_pintada", "pedra_reboco_historico", "madeira_pintada"], "Interior",
       sa_layer="Architecture")
KI = H.kit("Interior")
for x in (-15.0, 0.0, 15.0):
    lo = KI.ceiling_light(P + f"foyer_chandelier_{x:+.0f}", (x, (FO[1] + FO[3]) / 2, FH_F - .02), drop=.9)
    bpy.data.lights[lo.name + "__light"].energy = 450
# Stalls: raked floor stepped per row, seat rows (merged per block), balcony U, booth, ceiling with rosette.
pl = R["plateia"]
y_back, y_front = AU[1] + .7, pl[3] - 3.5          # seats region (orchestra pit in front)
rows = 26
zb_, zf_ = PLINTH, -.15                # back rows level with the foyer, raked down to the stage


def rake(y):
    return zf_ + (zb_ - zf_) * (y - y_front) / (y_back - y_front)


mb = sa_bl.MeshBuilder()
for k in range(rows):
    ya = y_back + k * (y_front - y_back) / rows
    yb = ya + (y_front - y_back) / rows
    mb.box(0, (ya + yb) / 2, -1.0, pl[2] - pl[0] - 1.4, abs(yb - ya) + .01, rake(ya) + 1.0, 0)
mb.box(0, (y_front + pl[3] - 3.0) / 2, -1.0, pl[2] - pl[0] - 1.4, pl[3] - 3.0 - y_front, zf_ + 1.0, 0)
for x in (-14.0, 14.0):
    mb.box(x, pl[3] - 1.5, -1.6, 2.0, 3.0, 1.6 + zf_, 0)                                     # stalls floor beside the pit
mb.box(0, pl[3] - 1.5, -1.8, 26.0, 3.0, .2, 1)                                                # orchestra pit floor (-1.6)
mb.box(0, pl[3] - 3.0, -1.6, 26.0, .2, 1.6 + zf_ + .9, 1)                                    # pit rail
H.mesh(P + "stalls_floor", mb, ["madeira_palco", "concreto_pintado"], "Interior", sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
blocks = [(-12.0, 12.0), (-31.0, -14.5), (14.5, 31.0)]
seats = 0
for k in range(rows - 1):
    ya = y_back + (k + .5) * (y_front - y_back) / rows
    z = rake(y_back + k * (y_front - y_back) / rows)
    for x0, x1 in blocks:
        mb.box((x0 + x1) / 2, ya + .05, z + .42, x1 - x0, .45, .1, 0)                         # seat pans
        mb.box((x0 + x1) / 2, ya - .22, z + .45, x1 - x0, .08, .55, 0)                        # backrests
        n = int((x1 - x0) / .55)
        seats += n
        for i in range(n + 1):
            mb.box(x0 + i * (x1 - x0) / n, ya, z, .05, .5, .66, 1)                           # armrests / standards
H.mesh(P + "stalls_seats", mb, ["veludo_vermelho", "aco_pintado_cinza"], "Interior", sa_layer="Props", seats=seats,
       note="poltronas mescladas por bloco (LOD0 base); instancing por poltrona na Unity")
mb = sa_bl.MeshBuilder()
zbal = 7.4
for (x0, y0, x1, y1) in ((pl[0], AU[1] + .7, pl[2], AU[1] + 7.5), (pl[0], AU[1] + 7.5, pl[0] + 5.0, 8.0), (pl[2] - 5.0, AU[1] + 7.5, pl[2], 8.0)):
    mb.box((x0 + x1) / 2, (y0 + y1) / 2, zbal, x1 - x0, y1 - y0, .35, 0, bottom=True)
mb.box(0, AU[1] + 7.6, zbal + .35, pl[2] - pl[0] - 10, .25, 1.0, 1)                           # balcony fronts (painted, gilt band)
mb.box(0, AU[1] + 7.75, zbal + .55, pl[2] - pl[0] - 10, .06, .18, 2)
for x in (pl[0] + 5.1, pl[2] - 5.1):
    mb.box(x, (AU[1] + 7.5 + 8.0) / 2, zbal + .35, .25, 8.0 - AU[1] - 7.5, 1.0, 1)
for x in (-20.0, -10.0, 0.0, 10.0, 20.0):
    mb.cylinder(x, AU[1] + 7.3, rake(AU[1] + 7.3), .2, zbal - rake(AU[1] + 7.3), 12, 1)
for k in range(5):                                                                           # balcony seat risers + rows
    y = AU[1] + 1.4 + k * 1.15
    z = zbal + .35 + (4 - k) * .38
    mb.box(0, y, zbal + .35, pl[2] - pl[0] - 1.4, 1.15, (4 - k) * .38 + .01, 3)
    mb.box(0, y + .15, z + .42, pl[2] - pl[0] - 12, .45, .1, 4)
    mb.box(0, y - .12, z + .45, pl[2] - pl[0] - 12, .08, .55, 4)
cb = R["cabine"]
mb.box((cb[0] + cb[2]) / 2, AU[1] + 1.2, zbal + 2.4, cb[2] - cb[0], 2.2, 2.6, 5)               # control booth on the balcony
mb.box((cb[0] + cb[2]) / 2, AU[1] + 2.31, zbal + 3.4, cb[2] - cb[0] - 1.0, .02, .8, 6)
mb.box(0, 0, ZA - 2.0, pl[2] - pl[0], AU[3] - AU[1] - 1.0, .3, 5, top=False, bottom=True)     # flat ceiling
mb.cylinder(0, -2.0, ZA - 2.1, 4.0, .1, 32, 2)                                               # rosette
H.mesh(P + "balcony_booth_ceiling", mb, ["concreto_pintado", "veludo_vermelho", "dourado_velho", "madeira_pintada", "veludo_vermelho",
                                         "parede_pintada", "vidro"], "Interior", bevel=.006, sa_layer="Architecture")
lo = KI.ceiling_light(P + "chandelier_main", (0, -2.0, ZA - 2.2), drop=2.0)
bpy.data.lights[lo.name + "__light"].energy = 3000
for k, y in enumerate((-15.0, 5.0)):
    for x in (-25.0, 25.0):
        lo = KI.ceiling_light(P + f"stalls_light_{k}_{x:+.0f}", (x, y, ZA - 2.1), drop=.4)
        bpy.data.lights[lo.name + "__light"].energy = 600
# Stage: floor, proscenium arch, curtain halves, fly galleries, gridiron, battens with borders.
pa = R["palco"]
mb = sa_bl.MeshBuilder()
mb.box(0, (pl[3] + FT[3]) / 2, 0, FT[2] - FT[0] - 1.2, FT[3] - pl[3] - .6, STAGE, 0, bottom=True)
wall_x(mb, AU[3] - .4, AU[0] + .7, AU[2] - .7, .8, STAGE, ZA, [(0.0, 24.0, STAGE, STAGE + 10.0)], 1)  # proscenium wall
for x in (-12.6, 12.6):
    mb.box(x, AU[3] - .9, STAGE, 1.2, .3, 10.4, 2)                                            # proscenium frame
mb.box(0, AU[3] - .9, STAGE + 10.0, 26.4, .3, 1.4, 2)
for s in (-1, 1):
    mb.box(s * 7.4, AU[3] + .3, STAGE, 10.4, .12, 10.0, 3)                                     # main curtain (half open)
mb.box(0, AU[3] + .3, STAGE + 9.0, 24.0, .14, 1.0, 3)                                         # pelmet
for s in (-1, 1):
    mb.box(s * (FT[2] - 1.6), (FT[1] + FT[3]) / 2, 9.0, 2.2, FT[3] - FT[1] - 1.2, .2, 4, bottom=True)   # fly galleries
    for k in range(10):
        mb.cylinder(s * (FT[2] - 2.6), FT[1] + 1.5 + k * 1.9, 9.2, .03, 1.0, 6, 4)            # pin rail
H.mesh(P + "stage", mb, ["madeira_palco", STONE, "dourado_velho", "veludo_vermelho", "aco_pintado_cinza", "borracha_preta"], "Interior",
       bevel=.004, sa_layer="Architecture")
mb = sa_bl.MeshBuilder()
mb.box(0, (FT[1] + FT[3]) / 2, 30.0, FT[2] - FT[0] - 1.2, FT[3] - FT[1] - 1.2, .1, 4)       # gridiron
for k in range(9):
    y = FT[1] + 2.0 + k * 2.1
    mb.box(0, y, 18.0 + (k % 3) * 2.5, 22.0, .06, .06, 4)                                     # battens
    if k % 2 == 0:
        mb.box(0, y + .1, 15.0 + (k % 3) * 2.5, 22.0, .05, 3.0, 5)                            # black borders
H.mesh(P + "stage_rigging", mb, ["madeira_palco", STONE, "dourado_velho", "veludo_vermelho", "aco_pintado_cinza", "borracha_preta"], "Interior",
       sa_layer="Architecture", note="urdimento, varas e bambolinas")
for x in (-8.0, 0.0, 8.0):
    lo = KI.ceiling_light(P + f"stage_work_light_{x:+.0f}", (x, (FT[1] + FT[3]) / 2, 17.0), drop=.5)
    bpy.data.lights[lo.name + "__light"].energy = 900
# Backstage: floor, racks, road cases, costume rail, old electrical board + half-done retrofit (gameplay).
mb = sa_bl.MeshBuilder()
mb.box(0, (BK[1] + BK[3]) / 2, 0, BK[2] - BK[0] - 1.2, BK[3] - BK[1] - .6, STAGE, 0, bottom=True)
for k in range(5):
    x = -20.0 + k * 3.2
    mb.box(x, BK[3] - 1.5, STAGE, 1.2, .8, .9 + (k % 2) * .3, 1)                              # road cases
    mb.box(x, BK[3] - 1.5, STAGE + .9 + (k % 2) * .3, 1.24, .84, .04, 2)
mb.box(14.0, BK[1] + 1.5, STAGE + 1.7, 4.0, .05, .05, 2)                                      # costume rail
for k in range(14):
    mb.box(12.2 + k * .27, BK[1] + 1.5, STAGE + .7, .2, .5, 1.0, 3 + (k % 2))
H.mesh(P + "backstage_interior", mb, ["madeira_palco", "borracha_preta", "aco_pintado_cinza", "veludo_vermelho", "tecido_lencol"], "Interior",
       bevel=.004, sa_layer="Props")
qa = R["quadro_antigo"]
qy = (qa[1] + qa[3]) / 2
mb = sa_bl.MeshBuilder()                                                                     # old board: slate on a wooden frame (fictional)
mb.box(0, -.06, 1.0, 1.8, .12, 2.1, 0)
mb.box(0, -.13, 1.1, 1.6, .02, 1.9, 1)
for r_ in range(4):
    for c_ in range(5):
        x, z = -.6 + c_ * .3, 1.4 + r_ * .42
        mb.cylinder(x, -.16, z, .045, .06, 10, 2)                                            # porcelain fuse carriers
        mb.box(x, -.16, z + .1, .02, .05, .1, 3)
for c_ in range(3):
    mb.box(-.5 + c_ * .5, -.2, 2.9, .14, .1, .32, 3)                                          # knife switches
    mb.box(-.5 + c_ * .5, -.25, 3.15, .03, .12, .03, 4)
for x in (-.55, .55):
    mb.cylinder(x, -.17, 1.18, .09, .08, 16, 2)                                               # old meters
mb.box(0, -.05, 3.25, 1.2, .1, 1.6, 0)                                                        # cloth-wired cables going up
H.mesh(P + "quadro_antigo", mb, ["madeira_crua", "ardosia", "louca_sanitaria", "aco_pintado_cinza", "borracha_preta"], "Services", bevel=.003,
       sa_kind="old_electrical_board", interactive=True, gameplay="quadro antigo do teatro (Capítulo II: sistema elétrico ultrapassado)")
qd = bpy.data.objects[P + "quadro_antigo"]
qd.location, qd.rotation_euler = (BK[0] + .6, qy, STAGE), (0, 0, math.pi / 2)
KS = H.kit("Services")
KS.panel_qdc(P + "retrofit_qdc", (BK[0] + .6, qy + 2.0, STAGE), math.pi / 2, z=1.6, ways=24)
mb = sa_bl.MeshBuilder()
for k in range(4):                                                                           # new conduits, stopped mid-run (reform in progress)
    mb.box(BK[0] + .66, qy + 1.85 + k * .1, STAGE + 1.85, .03, .03, 3.0 - k * .5, 0)
mb.box(BK[0] + .66, qy + 1.9, STAGE + 4.9, .03, 6.0, .03, 0)
mb.box(BK[0] + 1.6, qy + 3.0, STAGE, .9, .5, .4, 1)                                          # cable reel on the floor
H.mesh(P + "retrofit_conduits", mb, ["metal_galvanizado", "madeira_crua"], "Services", sa_layer="Infrastructure", note="retrofit inacabado")
KS.extinguisher(P + "backstage_extinguisher", (BK[0] + .6, qy - 2.5, STAGE), math.pi / 2)
KS.ceiling_light(P + "backstage_light", (0, (BK[1] + BK[3]) / 2, 4.48))
KS.ceiling_light(P + "quadro_light", (BK[0] + 2.0, qy, 4.48))

# ---------------------------------------------------------------- site: largo drop-off, dock apron, service path, heritage reform
mb = sa_bl.MeshBuilder()
lot = Lrect(hero["lot"])
dz = Lrect(next(p["rect"] for p in hero["parking"] if p["role"] == "plaza_dropoff"))
mb.box(0, (lot[1] + pr[1]) / 2 - 1.5, -.2, lot[2] - lot[0], pr[1] - lot[1] - 3.0 + 6, .2, 0)   # stone paving in front of the steps
mb.box((dz[0] + dz[2]) / 2, (dz[1] + dz[3]) / 2, -.2, dz[2] - dz[0], dz[3] - dz[1], .21, 1)
ap = Lrect(next(p["rect"] for p in hero["parking"] if p["role"] == "dock_apron"))
mb.box((ap[0] + ap[2]) / 2, (ap[1] + ap[3]) / 2 + 1, -.2, ap[2] - ap[0], ap[3] - ap[1] + 2, .2, 1)
for x in (-4.0, 4.0):
    mb.box(x, (ap[1] + ap[3]) / 2, 0, .12, ap[3] - ap[1], .005, 2)
sp = Lrect(next(s["rect"] for s in hero["service"] if s["role"] == "east_service_path"))
mb.box((sp[0] + sp[2]) / 2, (sp[1] + sp[3]) / 2, -.2, sp[2] - sp[0], sp[3] - sp[1], .2, 3)
mb.box(-(lot[2] - .1), (sp[1] + sp[3]) / 2, 0, .2, sp[3] - sp[1], 2.4, 4)
mb.box(lot[2] - .1, (lot[1] + lot[3]) / 2 + 10, 0, .2, lot[3] - lot[1] - 20, 2.4, 4)
for x in (-24.0, -16.0, 16.0, 24.0):                                                       # cast-iron lamp posts on the forecourt
    mb.cylinder(x, pr[1] - 4.0, 0, .12, 4.2, 12, 5)
    mb.cylinder(x, pr[1] - 4.0, 4.2, .22, .5, 12, 6)
for x in (-27.0, 27.0):                                                                    # poster frames on the portico wall
    mb.box(x, yF - .08, PLINTH + 1.0, 1.4, .08, 2.0, 7)
    mb.box(x, yF - .13, PLINTH + 1.1, 1.2, .02, 1.8, 8)
mb.box(-31.5, yF - .05, PLINTH + 1.2, .9, .04, .6, 9)                                       # heritage plaque
H.mesh(P + "site", mb, ["granito", "asfalto_gasto", "sinalizacao_viaria", "concreto", BRICK, "aco_pintado_verde", "lampada_emissiva",
                        "madeira_pintada", "papelao", "aco_inox"], "Site", bevel=.005, sa_layer="Roads")
mb = sa_bl.MeshBuilder()                                                                     # partial reform: scaffold + tarp on the west foyer bay
x0s, x1s = FO[2] - 14.0, FO[2] + .2
for k in range(int((x1s - x0s) / 2.0) + 1):
    x = x0s + k * 2.0
    for y in (yF - 1.4, yF - .5):
        mb.cylinder(x, y, 0, .03, ZF + 1.5, 6, 0)
for z in [1.0 + 2.0 * k for k in range(7)]:
    for y in (yF - 1.4, yF - .5):
        mb.box((x0s + x1s) / 2, y, z, x1s - x0s, .05, .05, 0)
    mb.box((x0s + x1s) / 2, yF - .95, z - .05, x1s - x0s, .9, .05, 1)
mb.box((x0s + x1s) / 2, yF - 1.5, 3.0, x1s - x0s, .02, ZF - 2.0, 2)
H.mesh(P + "reform_scaffold", mb, ["metal_galvanizado", "madeira_crua", "lona_obra"], "Site", sa_layer="Props", note="reforma parcial da fachada")
mb = sa_bl.MeshBuilder()
for k in range(5):                                                                           # exposed retrofit conduits climbing the east side
    mb.box(AU[0] - .75, -10.0 + k * .12, .5, .05, .05, ZA - 1.0, 0)
mb.box(AU[0] - .75, -9.76, .5, .3, .4, .6, 1)
H.mesh(P + "facade_conduits", mb, ["metal_galvanizado", "aco_pintado_cinza"], "Services", sa_layer="Infrastructure")
mb = sa_bl.MeshBuilder()
mb.box(0, 0, -2.2, 160, 170, 2.0, 0)
H.mesh(P + "ground_plate", mb, ["terra"], "CaptureOnly", sa_layer="Terrain", note="só para capturas isoladas")
H.empty(P + "GP_quadro_antigo", (BK[0] + 1.0, qy, STAGE + 1.4), (.6, 2.0, 2.2), sa_kind="interaction", note="quadro antigo + retrofit")
H.empty(P + "GP_basement_hatch", (lot[2] - 1.0, L(next(e["p"] for e in hero["entrances"] if e["role"] == "technical_basement_hatch"))[1], .3), (1.2, 1.2, .6),
        sa_kind="access", note="alçapão do porão técnico (porão não modelado no W2)")

# ---------------------------------------------------------------- lighting, cameras, captures
sa_bl.sun_and_sky(H.scene, H.C["Lighting"], elevation_deg=34.0, azimuth_deg=200.0)
H.cam("CAM_W2_imperial_largo", (-26.0, pr[1] - 42.0, 1.7), (0.0, yF, 11.0), 18)
H.cam("CAM_W2_imperial_portico", (9.5, pr[1] + 1.2, PLINTH + 1.65), (-4.0, yF, PLINTH + 3.0), 16)
H.cam("CAM_W2_imperial_foyer", (-26.0, FO[1] + 1.5, PLINTH + 1.65), (6.0, FO[3] - 1.0, PLINTH + 2.5), 16)
H.cam("CAM_W2_imperial_stalls", (6.0, pl[3] + 2.0, STAGE + 1.7), (0.0, AU[1], 6.0), 14)
H.cam("CAM_W2_imperial_stage", (-4.0, AU[1] + 12.0, rake(AU[1] + 12.0) + 1.6), (0.0, FT[1] + 4.0, 6.0), 18)
H.cam("CAM_W2_imperial_quadro", (BK[0] + 4.2, qy - 1.8, STAGE + 1.65), (BK[0] + .4, qy + .8, STAGE + 1.6), 18)
H.cam("CAM_W2_imperial_dock", (14.0, ap[3] + 10.0, 2.2), (0.0, BK[3], 5.0), 18)
H.cam("CAM_W2_imperial_aerial", (-95.0, -110.0, 75.0), (0, 0, 10.0), 26)
H.cutaway("CAM_W2_imperial_cutaway", (0.0, 8.0), 70.0, 105.0)
hide_cut = [P + "stage_rigging", P + "auditorium_roof", P + "balcony_booth_ceiling", P + "chandelier", P + "stalls_light", P + "stage_work", P + "fly_tower",
            P + "backstage_light", P + "quadro_light", P + "foyer_chandelier"]
for name, cam in (("w2_imperial_01_largo", "CAM_W2_imperial_largo"), ("w2_imperial_02_portico", "CAM_W2_imperial_portico"),
                  ("w2_imperial_03_foyer", "CAM_W2_imperial_foyer"), ("w2_imperial_04_plateia", "CAM_W2_imperial_stalls"),
                  ("w2_imperial_05_palco", "CAM_W2_imperial_stage"), ("w2_imperial_06_quadro_antigo", "CAM_W2_imperial_quadro"),
                  ("w2_imperial_07_doca", "CAM_W2_imperial_dock"), ("w2_imperial_08_aerea", "CAM_W2_imperial_aerial")):
    H.capture(name, cam)
H.capture("w2_imperial_09_corte", "CAM_W2_imperial_cutaway", 2000, 2400, hide_cut)
H.save("W2_imperial.blend")
