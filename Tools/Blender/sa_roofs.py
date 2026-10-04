"""W3.2 roof and rooftop volume kit for the Old Town slice (requires bpy).

Small authored pieces (origin at the lot-local placement point, z = 0 on the roof / ground) that break the aerial repetition of the
W2 building families: partial colonial tile roofs, fibre-cement and metal sheds, parapets of different heights and profiles,
water tanks, stair heads, skylights, clotheslines, chimneys, exhausts, technical volumes, solar rows and side extensions.
Placement (per lot / block, deterministic, by neighbourhood character) lives in create_oldtown_base.py.
"""
import math
import re

import sa_bl

CW = (4, 6, 8, 10)          # width classes (m) for pitched / parapet pieces

PIECES = {}                  # kind -> materials


def _reg(kind, mats):
    PIECES[kind] = mats


for _w in CW:
    _reg(f"w32_colonial{_w}", ["ceramica_telha", "concreto_pintado", "madeira_crua"])
    _reg(f"w32_fibro{_w}", ["telha_fibrocimento", "concreto"])
    _reg(f"w32_metal{_w}", ["telha_metalica", "aco_pintado_cinza"])
    _reg(f"w32_platibanda_alta{_w}", ["concreto_pintado", "concreto"])
    _reg(f"w32_platibanda_curva{_w}", ["concreto_pintado", "concreto"])
    _reg(f"w32_platibanda_degrau{_w}", ["concreto_pintado", "concreto"])
    _reg(f"w32_puxadinho{_w}", ["reboco_pintado", "telha_fibrocimento", "aluminio"])
for _k, _m in {
    "w32_caixa_pequena": ["plastico_azul", "tijolo_aparente", "plastico_branco"],
    "w32_caixa_torre": ["plastico_azul", "tijolo_aparente", "concreto", "metal_galvanizado"],
    "w32_casa_escada": ["reboco_pintado", "concreto", "aco_pintado_cinza"],
    "w32_claraboia": ["aluminio", "vidro", "concreto"],
    "w32_claraboia_grande": ["aluminio", "vidro", "concreto"],
    "w32_varal": ["metal_galvanizado", "plastico_branco", "plastico_azul", "aco_pintado_verde"],
    "w32_chamine": ["tijolo_aparente", "concreto", "metal_galvanizado"],
    "w32_exaustor": ["aluminio", "metal_galvanizado"],
    "w32_vol_tecnico": ["concreto_pintado", "aco_pintado_cinza", "plastico_branco", "borracha"],
    "w32_solar_fileira": ["vidro", "aluminio"],
    "w32_condensadoras": ["plastico_branco", "aco_pintado_cinza", "borracha"],
}.items():
    _reg(_k, _m)


def _gable(mb, w, d, z0, z1, mat_roof, mat_wall, ridge_x=True, ov=.25):
    """Two-slope roof over a w x d footprint, ridge along X; gable triangles in mat_wall."""
    hw, hd = w / 2 + ov, d / 2 + ov
    for s in (-1, 1):
        mb.add_face([(-hw, s * hd, z0 - .08), (hw, s * hd, z0 - .08), (hw, 0, z1), (-hw, 0, z1)][::s], mat_roof)
    for xs in (-1, 1):
        mb.add_face([(xs * w / 2, -d / 2, z0 - .08), (xs * w / 2, d / 2, z0 - .08), (xs * w / 2, 0, z1 - .06)][::xs], mat_wall)
    mb.box(0, 0, z1 - .04, w + ov * 2, .14, .08, mat_roof)


def build(kind, lib, coll):
    mb = sa_bl.MeshBuilder()
    mats = PIECES[kind]
    m_ = re.search(r"(\d+)$", kind)
    cw = int(m_.group(1)) if m_ else 0
    w = float(cw) if cw else 0.0
    if kind.startswith("w32_colonial"):
        d = 4.6
        mb.box(0, 0, 0, w, d, .45, 1)                                          # low masonry drum
        _gable(mb, w, d, .45, 1.75, 0, 1, ov=.28)
        for k in range(6):
            mb.box(-w / 2 + .3 + k * (w - .6) / 5, 0, .4, .08, d + .5, .03, 2)  # battens / rafter ends
    elif kind.startswith("w32_fibro"):
        d = 4.2
        for x_ in (-w / 2 + .15, w / 2 - .15):
            mb.box(x_, -d / 2 + .1, 0, .16, .16, .55, 1)
            mb.box(x_, d / 2 - .1, 0, .16, .16, 1.15, 1)
        mb.add_face([(-w / 2 - .2, -d / 2 - .25, .55), (w / 2 + .2, -d / 2 - .25, .55), (w / 2 + .2, d / 2 + .15, 1.2), (-w / 2 - .2, d / 2 + .15, 1.2)], 0)
        for k in range(int(w / .33)):
            xk = -w / 2 + .3 + k * .33
            mb.add_face([(xk, -d / 2 - .25, .56), (xk + .1, -d / 2 - .25, .56), (xk + .1, d / 2 + .15, 1.21), (xk, d / 2 + .15, 1.21)], 0)
    elif kind.startswith("w32_metal"):
        d = 4.6
        for x_ in (-w / 2 + .1, w / 2 - .1):
            for y_ in (-d / 2 + .1, d / 2 - .1):
                mb.box(x_, y_, 0, .1, .1, 1.3, 1)
        _gable(mb, w, d, 1.3, 1.62, 0, 1, ov=.15)
        for k in range(int(w / .3)):
            xk = -w / 2 + .2 + k * .3
            mb.box(xk, 0, 1.46, .035, d + .3, .03, 0)
    elif kind.startswith("w32_platibanda_alta"):
        mb.box(0, 0, 0, w, .22, 1.5, 0)
        mb.box(0, -.03, 1.5, w + .12, .30, .10, 1)
        mb.box(0, -.06, 1.12, w + .04, .06, .08, 1)
    elif kind.startswith("w32_platibanda_curva"):
        n = 14
        pts = [(-w / 2, 1.1)] + [(-w / 2 + w * k / n, 1.1 + .75 * math.sin(math.pi * k / n) ** .8) for k in range(n + 1)] + [(w / 2, 1.1)]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            mb.quad((a[0], -.11, 0), (b[0], -.11, 0), (b[0], -.11, b[1]), (a[0], -.11, a[1]), 0)
            mb.quad((b[0], .11, 0), (a[0], .11, 0), (a[0], .11, a[1]), (b[0], .11, b[1]), 0)
            mb.quad((a[0], -.11, a[1]), (b[0], -.11, b[1]), (b[0], .11, b[1]), (a[0], .11, a[1]), 1)
        mb.box(-w / 2, 0, 0, .22, .22, 1.1, 0)
        mb.box(w / 2, 0, 0, .22, .22, 1.1, 0)
    elif kind.startswith("w32_platibanda_degrau"):
        seg = w / 5
        for k, hz in enumerate((.9, 1.25, 1.6, 1.25, .9)):
            mb.box(-w / 2 + seg * (k + .5), 0, 0, seg, .22, hz, 0)
        mb.box(0, -.03, 1.6, seg + .1, .30, .08, 1)
    elif kind.startswith("w32_puxadinho"):
        d = 3.2
        h0, h1 = 2.5, 2.9
        mb.box(0, d / 2, 0, w, d, h0, 0, top=False)
        mb.add_face([(-w / 2 - .2, -.2, h0), (w / 2 + .2, -.2, h0), (w / 2 + .2, d + .15, h1), (-w / 2 - .2, d + .15, h1)], 1)
        mb.box(-w / 4, -.005, 0, .9, .01, 2.0, 2)
        mb.box(w / 4, -.005, 1.0, 1.2, .01, .9, 2)
    elif kind == "w32_caixa_pequena":
        mb.box(0, 0, 0, 1.0, 1.0, .5, 1)
        mb.cylinder(0, 0, .5, .46, .85, 16, 0)
        mb.cylinder(0, 0, 1.35, .30, .06, 16, 2)
    elif kind == "w32_caixa_torre":
        for x_ in (-.6, .6):
            for y_ in (-.6, .6):
                mb.box(x_, y_, 0, .35, .35, 1.7, 1)
        mb.box(0, 0, 1.7, 1.9, 1.9, .16, 2)
        mb.cylinder(0, 0, 1.86, .8, 1.25, 20, 0)
        mb.cylinder(0, 0, 3.11, .5, .06, 16, 0)
        for z_ in range(1, 9):
            mb.box(1.1, .0, 0.2 * z_, .02, .35, .03, 3)
        mb.box(1.1, -.17, 0, .02, .02, 2.0, 3)
        mb.box(1.1, .17, 0, .02, .02, 2.0, 3)
    elif kind == "w32_casa_escada":
        mb.box(0, 0, 0, 2.7, 2.7, 2.4, 0)
        mb.box(0, 0, 2.4, 3.1, 3.1, .12, 1)
        mb.box(0, -1.351, 0, .9, .02, 2.0, 2)
    elif kind in ("w32_claraboia", "w32_claraboia_grande"):
        sx, sy = (1.0, 1.0) if kind == "w32_claraboia" else (2.6, 1.3)
        mb.box(0, 0, 0, sx + .3, sy + .3, .25, 2)
        for s in (-1, 1):
            mb.add_face([(-sx / 2, s * sy / 2, .25), (sx / 2, s * sy / 2, .25), (sx / 2, 0, .25 + sy * .38), (-sx / 2, 0, .25 + sy * .38)][::s], 1)
        for k in range(int(sx / .45) + 1):
            xk = -sx / 2 + k * sx / max(1, int(sx / .45))
            mb.box(xk, 0, .25, .04, sy, .04, 0)
    elif kind == "w32_varal":
        for x_ in (-1.4, 1.4):
            mb.box(x_, 0, 0, .06, .06, 2.0, 0)
        for dz in (0, .18):
            mb.box(0, 0, 1.9 - dz, 2.8, .012, .012, 0)
        cols = (1, 2, 3, 1, 2)
        for k, c_ in enumerate(cols):
            mb.box(-1.0 + k * .5, 0, 1.25 + (k % 2) * .05, .38, .015, .6, c_)
    elif kind == "w32_chamine":
        mb.box(0, 0, 0, .6, .6, 1.8, 0)
        mb.box(0, 0, 1.8, .8, .8, .1, 1)
        mb.box(0, 0, 1.9, .5, .5, .15, 2)
    elif kind == "w32_exaustor":
        for x_ in (-.55, .55):
            mb.cylinder(x_, 0, 0, .22, .35, 12, 1)
            for k in range(8):
                a = 2 * math.pi * k / 8
                mb.box(x_ + math.cos(a) * .18, math.sin(a) * .18, .35, .02, .02, .22, 0)
            mb.cylinder(x_, 0, .55, .3, .06, 12, 0)
    elif kind == "w32_vol_tecnico":
        mb.box(0, 0, 0, 3.2, 2.2, 2.3, 0)
        mb.box(0, 0, 2.3, 3.4, 2.4, .12, 1)
        for k in range(8):
            mb.box(-1.0 + k * .28, -1.105, 1.0, .18, .02, .05, 1)
        for x_ in (-.8, .8):
            mb.cylinder(x_, 1.15, 1.2, .35, .06, 14, 2, top=True)
        mb.box(0, 1.1, 0, 1.6, .4, .9, 2)
    elif kind == "w32_solar_fileira":
        for k in range(3):
            x_ = -1.1 + k * 1.1
            mb.add_face([(x_ - .5, -.9, .55), (x_ + .5, -.9, .55), (x_ + .5, .9, 1.2), (x_ - .5, .9, 1.2)], 0)
            mb.box(x_, -.85, 0, .06, .06, .55, 1)
            mb.box(x_, .85, 0, .06, .06, 1.15, 1)
    elif kind == "w32_condensadoras":
        for k in range(3):
            x_ = -1.0 + k * 1.0
            mb.box(x_, 0, .15, .8, .35, .6, 0)
            mb.cylinder(x_, -.18, .22, .24, .02, 14, 1)
            mb.box(x_, 0, 0, .75, .08, .15, 1)
        mb.box(0, 0, .02, 3.0, .06, .06, 2)
    o = sa_bl.bevelled_object("ACC_" + kind, mb, [lib[m] for m in mats], coll, bevel=.004)
    sa_bl.props(o, sa_stage="W3.2 cobertura / volume de telhado (LOD0)")
    return o
