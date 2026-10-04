"""W3.2 vehicles: authored, generic (no real make, model or logo) parked cars for Santa Aurora (requires bpy).

Six families with their own silhouettes: hatch compacto, sedan, utilitário leve (picape), SUV compacto, van de serviço and an
older boxy hatch. W3.2 rebuilds LOD0 for 3-5 m viewing:
- body = lofted surface (PCHIP side profile for hood / deck / roof, tumblehome, rounded plan corners, real wheel-arch tunnels);
- greenhouse = second loft (curved roof, raked windshield and rear glass, pillars) over a cabin opening;
- transparent tinted glass over a minimal interior (dash, steering wheel, console, front seats, rear bench);
- wheels with shouldered tyre profile, dish, spokes, hub and brake disc; arch flares and side sills;
- headlamp / tail-lamp housings with emissive cores and clear lenses; mirrors with stalk; door shut lines, handles, fictional plate.
LOD0 ~12-22k tris, LOD1 (no interior, simple wheels, coarse stations) ~1.5-3k tris, proxy = two boxes.
"""
import math
import random
import zlib

import bmesh
import bpy

import sa_bl

FAMILIES = {
    # top: body top (hood / belt / deck) as (x, z) front at +x. gh: greenhouse (x rear base, x rear roof, x front roof, x front base, roof z).
    "hatch": dict(L=3.85, W=1.66, wb=2.45, r=.29, zs=.27, rs=.12, crown=.025, m=.62, rf=.55, rr=.40, tw=.20,
                  top=[(-1.925, .66), (-1.84, .82), (-1.55, .88), (.70, .88), (1.05, .88), (1.45, .84), (1.78, .76), (1.925, .64)],
                  gh=(-1.60, -1.12, .22, .95, 1.43), spokes=5, seat="cinza"),
    "sedan": dict(L=4.40, W=1.72, wb=2.60, r=.30, zs=.27, rs=.13, crown=.025, m=.62, rf=.60, rr=.45, tw=.21,
                  top=[(-2.20, .72), (-2.12, .90), (-1.85, .95), (-1.45, .94), (.75, .88), (1.0, .88), (1.5, .86), (1.95, .78), (2.20, .64)],
                  gh=(-1.35, -.78, .38, 1.05, 1.44), spokes=5, seat="bege"),
    "picape": dict(L=4.50, W=1.74, wb=2.75, r=.32, zs=.30, rs=.12, crown=.02, m=.64, rf=.55, rr=.30, tw=.23,
                   top=[(-2.25, .78), (-2.20, .86), (-.40, .86), (-.30, .95), (.95, .95), (1.5, .94), (2.0, .86), (2.25, .70)],
                   gh=(-.32, -.22, .40, 1.08, 1.62), spokes=6, seat="cinza", bed=(-2.23, -.40, .86, 1.22)),
    "suv": dict(L=4.20, W=1.80, wb=2.55, r=.34, zs=.30, rs=.14, crown=.025, m=.62, rf=.55, rr=.30, tw=.24,
                top=[(-2.10, .78), (-2.04, 1.0), (-1.7, 1.02), (.8, 1.0), (1.2, 1.0), (1.65, .97), (2.0, .86), (2.10, .70)],
                gh=(-1.98, -1.90, .52, 1.12, 1.68), spokes=5, seat="cinza", rails=True),
    "van": dict(L=4.95, W=1.90, wb=3.00, r=.32, zs=.30, rs=.16, crown=.03, m=.66, rf=.45, rr=.20, tw=.23,
                top=[(-2.475, 1.90), (-2.40, 2.05), (-2.0, 2.08), (1.45, 2.08), (1.75, 1.82), (2.05, 1.30), (2.30, 1.05), (2.475, .78)],
                gh=None, spokes=5, seat="cinza", van=True, win=(1.15, 1.95, 1.0, 1.78), shield=(1.55, 2.05)),
    "hatch_antigo": dict(L=3.70, W=1.60, wb=2.40, r=.28, zs=.27, rs=.07, crown=.015, m=.76, rf=.30, rr=.25, tw=.18,
                         top=[(-1.85, .70), (-1.80, .80), (-1.60, .80), (.9, .80), (1.35, .78), (1.75, .68), (1.85, .56)],
                         gh=(-1.62, -1.45, .35, .92, 1.36), spokes=0, seat="bege"),
}
PAINTS = {"branco": (.86, .86, .84), "prata": (.62, .63, .64), "vermelho": (.50, .06, .05), "azul_escuro": (.05, .09, .22),
          "preto": (.03, .03, .035), "bege": (.68, .60, .45), "verde_velho": (.20, .30, .20), "amarelo_servico": (.82, .62, .06)}
SEATS = {"cinza": (.09, .09, .10), "bege": (.30, .25, .17)}
M = {"paint": 0, "glass": 1, "tyre": 2, "rim": 3, "trim": 4, "head": 5, "tail": 6, "plate": 7, "liner": 8, "dash": 9, "seat": 10,
     "lens": 11, "lens_red": 12, "chrome": 13}


# ---------------------------------------------------------------- materials
def paint_material(lib, key, worn=False):
    name = f"pintura_carro_{key}" + ("_gasta" if worn else "")
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    c = PAINTS[key]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.5 if not worn else 9.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = (.45, .8) if not worn else (.56, .72)
    mr.inputs["To Max"].default_value = .15 if not worn else .35
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    mix.inputs[6].default_value = (*c, 1)
    mix.inputs[7].default_value = ((.30, .28, .25, 1) if worn else (*(v * .7 for v in c), 1))      # dust / oxidised paint
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = .22 if not worn else .6
    b.inputs["Coat Weight"].default_value = .6 if not worn else 0.0
    b.inputs["Metallic"].default_value = .35 if key in ("prata", "azul_escuro") and not worn else 0.0
    m.diffuse_color = (*c, 1)
    m["sa_family"] = "pintura_veiculo"
    return m


def glass_material():
    """Opaque tinted glass for LOD1 / distance (reads as a reflective window, no refraction noise)."""
    if "vidro_veiculo" in bpy.data.materials:
        return bpy.data.materials["vidro_veiculo"]
    m = bpy.data.materials.new("vidro_veiculo")
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (.015, .02, .025, 1)
    b.inputs["Roughness"].default_value = .04
    b.inputs["Specular IOR Level"].default_value = .8
    m.diffuse_color = (.02, .025, .03, 1)
    return m


def clear_glass_material(name="vidro_veiculo_claro", color=(.012, .016, .02), alpha=.30, rough=.03):
    """LOD0 automotive glass: tinted but Fresnel-transparent, so the modelled interior reads from 3-5 m."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 1.0
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = .4
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = alpha
    nt.links.new(lw.outputs["Fresnel"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], b.inputs["Alpha"])
    try:
        m.surface_render_method = "DITHERED"
        m.use_transparent_shadow = True
    except AttributeError:
        m.blend_method = "HASHED"
    m.diffuse_color = (*color, 1)
    m["sa_family"] = "vidro_veiculo"
    return m


def lens_material(name, color, alpha):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = clear_glass_material(name, color, alpha, .05)
    m["sa_family"] = "lente_veiculo"
    return m


def light_material(name, color, strength):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Emission Color"].default_value = (*color, 1)
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = .1
    m.diffuse_color = (*color, 1)
    return m


def plain_material(name, color, rough, metallic=0.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    m.diffuse_color = (*color, 1)
    return m


# ---------------------------------------------------------------- math helpers
def _curve(pts):
    """Monotone cubic (PCHIP) through (x, y) points; clamps outside the range."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    mm = [0.0] * n
    mm[0], mm[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            mm[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            mm[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        i = 0
        while xs[i + 1] < x:
            i += 1
        t = (x - xs[i]) / h[i]
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * mm[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * mm[i + 1])
    return f


def _rbox(mb, c, size, mat, ry=0.0, rz=0.0, top=True, bottom=True):
    """Box centred at c with size (sx, sy, sz), rotated about Y (pitch, radians) then Z (yaw)."""
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    cy_, sy_ = math.cos(ry), math.sin(ry)
    cz_, sz_ = math.cos(rz), math.sin(rz)

    def P(x, y, z):
        x1, z1 = x * cy_ + z * sy_, -x * sy_ + z * cy_
        return (c[0] + x1 * cz_ - y * sz_, c[1] + x1 * sz_ + y * cz_, c[2] + z1)

    k = [P(-sx, -sy, -sz), P(sx, -sy, -sz), P(sx, sy, -sz), P(-sx, sy, -sz), P(-sx, -sy, sz), P(sx, -sy, sz), P(sx, sy, sz), P(-sx, sy, sz)]
    mb.quad(k[0], k[1], k[5], k[4], mat)
    mb.quad(k[1], k[2], k[6], k[5], mat)
    mb.quad(k[2], k[3], k[7], k[6], mat)
    mb.quad(k[3], k[0], k[4], k[7], mat)
    if top:
        mb.quad(k[4], k[5], k[6], k[7], mat)
    if bottom:
        mb.quad(k[3], k[2], k[1], k[0], mat)


def _extrude_xz(mb, pts, y0, y1, mat):
    """Prism from an (x, z) polygon (counter-clockwise seen from +y) extruded between y0 < y1."""
    n = len(pts)
    mb.add_face([(x, y1, z) for x, z in pts], mat)
    mb.add_face([(x, y0, z) for x, z in pts[::-1]], mat)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        mb.quad((a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1]), (a[0], y1, a[1]), mat)


# ---------------------------------------------------------------- wheels
def _wheel(mb, cx, cy, r, side, width, segs, spokes, hi, phase):
    """Wheel along Y (side = +1 outer face toward +Y): shouldered tyre profile, rim lip, dish, spokes, hub, brake disc."""
    R = r
    rr = R * .64
    hw_ = width / 2
    prof = ([(rr * .98, -hw_ * .85), (R * .80, -hw_ * 1.0), (R * .93, -hw_ * .95), (R * .99, -hw_ * .62), (R, -hw_ * .30),
             (R, hw_ * .30), (R * .99, hw_ * .62), (R * .93, hw_ * .95), (R * .80, hw_ * 1.0), (rr * .98, hw_ * .85)] if hi else
            [(rr * .98, -hw_ * .9), (R * .92, -hw_ * 1.0), (R, -hw_ * .4), (R, hw_ * .4), (R * .92, hw_ * 1.0), (rr * .98, hw_ * .9)])

    def at(rho, ay, t):
        return (cx + math.cos(t) * rho, cy + side * ay, r + math.sin(t) * rho)

    for k in range(segs):
        t0, t1 = 2 * math.pi * k / segs, 2 * math.pi * (k + 1) / segs
        for j in range(len(prof) - 1):
            (ra, aa), (rb, ab) = prof[j], prof[j + 1]
            q = [at(ra, aa, t0), at(rb, ab, t0), at(rb, ab, t1), at(ra, aa, t1)]
            mb.add_face(q if side > 0 else q[::-1], M["tyre"])
    ay_dish, ay_lip = hw_ * .62, hw_ * .86
    for k in range(segs):                                                  # dish (dark, brake disc behind the spokes)
        t0, t1 = 2 * math.pi * k / segs, 2 * math.pi * (k + 1) / segs
        tri = [at(0.0, ay_dish, t0), at(rr * .98, ay_dish, t0), at(rr * .98, ay_dish, t1), at(0.0, ay_dish, t1)]
        mb.add_face(tri if side > 0 else tri[::-1], M["liner"])
        lip = [at(rr * .80, ay_lip, t0), at(rr * .98, ay_lip, t0), at(rr * .98, ay_lip, t1), at(rr * .80, ay_lip, t1)]   # rim lip
        mb.add_face(lip if side > 0 else lip[::-1], M["rim"])
        wall = [at(rr * .98, ay_lip, t0), at(rr * .98, hw_ * .85, t0), at(rr * .98, hw_ * .85, t1), at(rr * .98, ay_lip, t1)]
        mb.add_face(wall if side > 0 else wall[::-1], M["rim"])
    if hi:
        hub_r = R * .10
        for k in range(10):                                                # hub cap
            t0, t1 = 2 * math.pi * k / 10, 2 * math.pi * (k + 1) / 10
            tri = [at(hub_r, ay_dish + .012, t0), at(hub_r, ay_dish + .012, t1), at(0.0, ay_dish + .028, t1), at(0.0, ay_dish + .028, t0)]
            mb.add_face(tri if side > 0 else tri[::-1], M["chrome"])
        n_sp = spokes or 8
        for s in range(n_sp):                                              # spokes (radial boxes in the wheel plane)
            th = phase + 2 * math.pi * s / n_sp
            mid = (rr * .86 + R * .09) / 2
            _rbox(mb, (cx + math.cos(th) * mid, cy + side * (ay_dish + .02), r + math.sin(th) * mid),
                  (rr * .86 - R * .09, .016 if spokes else .02, .042 if spokes else .02), M["rim"], ry=-th, bottom=False)
        mb.add_face([at(rr * .74, ay_dish - .004, 2 * math.pi * k / 24) for k in range(24)][::1 if side > 0 else -1], M["liner"])   # brake disc plate
        cal = phase + 1.9
        _rbox(mb, (cx + math.cos(cal) * rr * .55, cy + side * (ay_dish - .03), r + math.sin(cal) * rr * .55), (.10, .05, .13), M["trim"])  # caliper


# ---------------------------------------------------------------- body
def _ring(x, zb, zt, hwx, f):
    """One closed cross-section ring (bottom centre -> +Y side -> top centre -> -Y side). Returns (points, edge index, top index)."""
    H = max(zt - zb, .04)
    rs = max(.03, min(f["rs"], H - min(.15, H * .28) - .03))
    ye = hwx - rs
    zl = zb + min(.15, H * .28)
    zu = zt - rs
    P = [(0.0, zb), (hwx * .80, zb), (hwx * .955, zb + min(.045, H * .12)), (hwx, zl)]
    if f.get("van"):
        w0, w1 = f["win"][0], f["win"][1]
        P += [(hwx, min(max(w0, zl + .02), zu - .04)), (hwx * .995, min(max(w1, zl + .04), zu - .02))]
    else:
        for t in (.40, .75):
            P.append((hwx * (1 - .05 * t * t), zl + (zu - zl) * t))
    P.append((hwx * .985, zu))
    for a in (35, 65):
        P.append((ye + rs * math.cos(math.radians(a)), zu + rs * math.sin(math.radians(a))))
    ie = len(P)
    P.append((ye, zt))
    cr = f["crown"]
    P += [(ye * .62, zt + cr * .45), (ye * .25, zt + cr * .9), (0.0, zt + cr)]
    n = len(P)
    full = P + [(-y, z) for y, z in P[-2:0:-1]]
    return full, ie, n - 1


def _arch_trim(mb, xw, side, r, ar, hwx):
    """Thin dark flare following the wheel arch on the outside of the body."""
    t0 = math.asin(max(-1.0, min(.95, (.30 - r) / ar)))
    pts_i = [(xw + ar * math.cos(t0 + (math.pi - 2 * t0) * k / 12), r + ar * math.sin(t0 + (math.pi - 2 * t0) * k / 12)) for k in range(13)]
    pts_o = [(xw + (ar + .035) * math.cos(t0 + (math.pi - 2 * t0) * k / 12), r + (ar + .035) * math.sin(t0 + (math.pi - 2 * t0) * k / 12)) for k in range(13)]
    y = side * (hwx + .004)
    for k in range(12):
        q = [(pts_i[k][0], y, pts_i[k][1]), (pts_i[k + 1][0], y, pts_i[k + 1][1]), (pts_o[k + 1][0], y, pts_o[k + 1][1]), (pts_o[k][0], y, pts_o[k][1])]
        mb.add_face(q if side > 0 else q[::-1], M["liner"])


def build(family, lib, coll, paint="branco", worn=False, lod=0, name=None, plate_seed=0):
    f = FAMILIES[family]
    hi = lod == 0
    L, W, wb, r, zs = f["L"], f["W"], f["wb"], f["r"], f["zs"]
    hw = W / 2
    xf, xr = L / 2, -L / 2
    mb = sa_bl.MeshBuilder()
    zt_f = _curve(f["top"])
    ar = r + .06
    arch_x = (wb / 2, -wb / 2)

    def zb_f(x):
        z = zs + .12 * max(0.0, (abs(x) - (xf - .30)) / .30) ** 2
        for xw in arch_x:
            d = abs(x - xw)
            if d < ar:
                z = max(z, r + math.sqrt(ar * ar - d * d))
        return min(z, zt_f(x) - .14)

    def s_f(x):
        rl = f["rf"] if x > 0 else f["rr"]
        xc = xf - rl if x > 0 else xr + rl
        u = (abs(x) - abs(xc)) / rl if abs(x) > abs(xc) else 0.0
        u = min(u, 1.0)
        return f["m"] + (1 - f["m"]) * math.sqrt(max(0.0, 1 - u * u))

    # stations: uniform + dense around the arches + greenhouse bounds
    step = .08 if hi else .42
    xs = {round(xr + k * L / max(1, round(L / step)), 4) for k in range(round(L / step) + 1)}
    for xw in arch_x:
        k = xw - ar
        while k <= xw + ar + 1e-6:
            xs.add(round(k, 4))
            k += (.03 if hi else .15)
    gh = f.get("gh")
    if gh:
        xs.update({gh[0], gh[3]})
    stations = sorted(xs)
    merged = [stations[0]]
    for x in stations[1:]:
        if x - merged[-1] > .006:
            merged.append(x)
    stations = merged

    rings, edge_i, top_i = [], 0, 0
    for x in stations:
        pts, edge_i, top_i = _ring(x, zb_f(x), zt_f(x), hw * s_f(x), f)
        rings.append([(x, y, z) for (y, z) in pts])
    N = len(rings[0])
    cab = (gh[0] + .10, gh[3] - .10) if gh else None
    sh = f.get("shield")
    wn = f.get("win")
    for i in range(len(stations) - 1):
        xc_ = (stations[i] + stations[i + 1]) / 2
        for k in range(N):
            if cab and cab[0] < xc_ < cab[1] and edge_i <= k < N - edge_i:
                continue                                                  # cabin opening (seats / dash visible through the glass)
            mat = M["liner"] if k in (0, N - 1) else M["paint"]
            if sh and sh[0] < xc_ < sh[1] and top_i - 3 <= k < top_i + 3:
                mat = M["glass"]
            if wn and wn[2] < xc_ < wn[3] and k in (4, N - 5):
                mat = M["glass"]
            mb.quad(rings[i][k], rings[i][(k + 1) % N], rings[i + 1][(k + 1) % N], rings[i + 1][k], mat)
    mb.add_face(rings[-1], M["paint"])
    mb.add_face(rings[0][::-1], M["paint"])

    # greenhouse loft
    x_b = 0.0
    zroof = None
    if gh:
        x_rb, x_rr, x_rf, x_fb, roof = gh
        zr0, zr1 = zt_f(x_rb), zt_f(x_fb)
        x_b = (x_rr + x_rf) / 2 - .12
        mid = (x_rr + x_rf) / 2
        zroof = _curve([(x_rb, zr0), (x_rb + .45 * (x_rr - x_rb), zr0 + .52 * (roof - zr0)), (x_rr, roof - .03), (mid, roof + .015),
                        (x_rf, roof - .03), (x_rf + .55 * (x_fb - x_rf), zr1 + .44 * (roof - zr1)), (x_fb, zr1)])
        gst = [x for x in stations if x_rb - 1e-6 <= x <= x_fb + 1e-6]
        grings = []
        for x in gst:
            pts, ie, _ = _ring(x, zb_f(x), zt_f(x), hw * s_f(x), f)
            ye, zt = pts[ie]
            h = max(0.0, zroof(x) - zt)
            tum = .05 + .03 * min(1.0, h)
            g = [(ye, zt), (ye - ye * tum * .5, zt + .5 * h), (ye - ye * tum * 1.4 - .02 * min(1.0, h), zt + .93 * h), (ye * .56, zt + .995 * h),
                 (ye * .22, zt + h), (0.0, zt + h)]
            grings.append([(x, y, z) for (y, z) in g + [(-y, z) for (y, z) in g[-2::-1]]])
        GN = len(grings[0])
        for i in range(len(gst) - 1):
            xc_ = (gst[i] + gst[i + 1]) / 2
            rake_f = xc_ > x_rf + .06
            rake_r = xc_ < x_rr - .05
            pillar = (not van_like(f)) and (abs(xc_ - x_b) < .05 or (xc_ < x_rr + .10 and family in ("sedan", "suv", "hatch")))
            for k in range(GN - 1):
                top_seg = k in (3, 4, 5, 6)
                if rake_f or rake_r:
                    mat = M["glass"] if top_seg else M["paint"]
                elif k in (0, 1, GN - 2, GN - 3):
                    mat = M["paint"] if pillar else M["glass"]
                else:
                    mat = M["paint"]
                mb.quad(grings[i][k], grings[i][k + 1], grings[i + 1][k + 1], grings[i + 1][k], mat)
        if f.get("rails"):
            gm = grings[len(gst) // 2]
            for ii in (2, GN - 3):
                _rbox(mb, ((x_rr + x_rf) / 2, gm[ii][1] * .9, gm[ii][2] + .03), (x_rf - x_rr - .2, .035, .035), M["chrome"])

    # wheels, arch flares, sills, underbody
    segs = 24 if hi else 8
    wph = 0.0
    rng = random.Random(zlib.crc32(family.encode()))
    for xw in arch_x:
        for s in (1, -1):
            _wheel(mb, xw, s * (hw - .17), r, s, f["tw"], segs, f["spokes"], hi, rng.uniform(0, 2 * math.pi) + wph)
            if hi:
                _arch_trim(mb, xw, s, r, ar, hw)
    if hi:
        for s in (-1, 1):
            _rbox(mb, (0.0, s * (hw + .003), zs + .045), (wb - 2 * ar - .05, .012, .09), M["trim"])         # side sill
            _rbox(mb, (0.0, s * (hw + .003), zs + .33), (wb - 2 * ar - .12, .008, .012), M["trim"])         # body-side character line
        _rbox(mb, (0.0, 0.0, zs - .02), (wb - 2 * ar, W - .5, .03), M["liner"])                          # floor pan

    # nose / tail: bumpers' lower valance, grille, plates, lights, exhaust
    zfe = (zb_f(xf) + zt_f(xf)) / 2
    zre = (zb_f(xr) + zt_f(xr)) / 2
    _rbox(mb, (xf + .004, 0.0, zb_f(xf) + .05), (.05, W * f["m"] - .12, .10), M["trim"])
    _rbox(mb, (xr - .004, 0.0, zb_f(xr) + .05), (.05, W * f["m"] - .12, .10), M["trim"])
    if hi:
        xg = xf - .03
        zg = zt_f(xf - .08) - .13
        _rbox(mb, (xg, 0.0, zg), (.05, W * f["m"] * .8, .12), M["trim"], ry=0.0)
        for k in range(3):
            _rbox(mb, (xg + .03, 0.0, zg - .035 + k * .035), (.012, W * f["m"] * .76, .008), M["chrome"])
        for xp, sg, zp in ((xf + .006, 1, zfe - .03), (xr - .006, -1, zre - .03)):
            _rbox(mb, (xp, 0.0, zp), (.014, .40, .13), M["plate"])
        _rbox(mb, (xr - .06, -.46, zb_f(xr) + .01), (.18, .06, .06), M["chrome"])                         # exhaust tip
    for s in (-1, 1):                                                                                  # lamps on the end faces
        yl = s * (hw * f["m"] * .62)
        zl_h = zfe + .02
        zl_t = (zre + .02) if not f.get("van") else .98
        _rbox(mb, (xf - .012, yl, zl_h), (.07, .32, .10), M["trim"])                                      # headlamp housing
        _rbox(mb, (xr + .012, yl, zl_t), (.07, .30, .13 if not f.get("van") else .30), M["trim"])        # tail-lamp housing
        if hi:
            for yy in (-.07, .07):
                _rbox(mb, (xf + .004, yl + yy, zl_h), (.03, .09, .07), M["head"], bottom=False)
            _rbox(mb, (xf + .022, yl, zl_h), (.012, .32, .10), M["lens"])
            _rbox(mb, (xr - .004, yl, zl_t), (.03, .24, .09 if not f.get("van") else .24), M["tail"], bottom=False)
            _rbox(mb, (xr - .022, yl, zl_t), (.012, .30, .13 if not f.get("van") else .30), M["lens_red"])
        else:
            _rbox(mb, (xf + .01, yl, zl_h), (.03, .30, .09), M["head"])
            _rbox(mb, (xr - .01, yl, zl_t), (.03, .26, .10), M["tail"])

    # cabin details
    if gh:
        x_rb, x_rr, x_rf, x_fb, roof = gh
        zt0 = zt_f(x_fb)
        for s in (-1, 1):
            xm = x_fb - .20
            ym = s * (hw * s_f(xm) + .075)
            zm = zt_f(xm) + .09
            _rbox(mb, (xm, ym, zm), (.11, .075, .08), M["paint"])                                          # mirror housing
            _rbox(mb, (xm + .02, s * (hw * s_f(xm) + .025), zm - .02), (.07, .06, .022), M["trim"])         # mirror stalk
            if hi:
                for xh in (x_b + .22, x_b - .30):
                    if xh > x_rb + .15 and xh < x_fb - .25:
                        _rbox(mb, (xh, s * (hw + .01), zt_f(xh) - .17), (.14, .018, .028), M["trim"])      # door handles
                for xseam in (x_fb - .50, x_b - .04, x_rb + .40):
                    zlo = zs + .09
                    for xw_ in arch_x:
                        if abs(xseam - xw_) < ar:
                            zlo = max(zlo, r + math.sqrt(ar * ar - (xseam - xw_) ** 2) + .03)
                    _rbox(mb, (xseam, s * (hw + .003), (zlo + zt_f(xseam) - .01) / 2), (.010, .007, zt_f(xseam) - .01 - zlo), M["trim"])
    if hi and gh:
        _interior(mb, f, gh, zt_f, zb_f, hw, s_f)
    if hi and f.get("van"):
        _van_extras(mb, f, hw, zt_f, zb_f)
    if f.get("bed"):
        bx0, bx1, bz0, bz1 = f["bed"]
        for yy in (-hw + .06, hw - .06):
            _rbox(mb, ((bx0 + bx1) / 2, yy, (bz0 + bz1) / 2), (bx1 - bx0, .07, bz1 - bz0), M["paint"], top=True)
        _rbox(mb, (bx0 + .04, 0.0, (bz0 + bz1) / 2), (.07, W - .14, bz1 - bz0), M["paint"])
        _rbox(mb, (bx1 - .03, 0.0, (bz0 + bz1) / 2 - .04), (.06, W - .14, bz1 - bz0 - .08), M["paint"])
        _rbox(mb, ((bx0 + bx1) / 2, 0.0, bz0 + .012), (bx1 - bx0 - .1, W - .22, .025), M["liner"])      # bed liner

    mats = [paint_material(lib, paint, worn), clear_glass_material() if hi else glass_material(), lib["borracha_preta"],
            plain_material("aro_liga_carro", (.46, .47, .49), .35, .9) if hi else lib["aluminio"], lib["borracha_preta"], light_material("farol_veiculo", (.9, .9, .85), .5),
            light_material("lanterna_veiculo", (.6, .04, .03), .8), lib["plastico_branco"], plain_material("liner_veiculo", (.015, .015, .016), .8),
            plain_material("interior_carro", (.07, .07, .075), .9), plain_material("banco_carro_" + f["seat"], SEATS[f["seat"]], .9),
            lens_material("lente_farol", (.5, .55, .55), .22), lens_material("lente_lanterna", (.35, .02, .02), .45),
            plain_material("cromado_carro", (.55, .56, .58), .25, 1.0)]
    nm = name or f"VEH_{family}_{paint}" + ("_gasto" if worn else "") + ("" if lod == 0 else f"_LOD{lod}")
    o = _object(nm, mb, mats, coll, bevel=.008 if hi else 0.0)
    if hi:
        rng = random.Random(plate_seed or zlib.crc32(nm.encode()))
        txt = "SA" + rng.choice("ABCDEFGH") + " " + str(rng.randint(0, 9)) + rng.choice("ABCDEFGHJK") + f"{rng.randint(10, 99)}"
        try:
            from sa_w2 import text_mesh
            for sgn, xx, zz in ((1, xf + .015, zfe - .03), (-1, xr - .015, zre - .03)):
                t = text_mesh(nm + f"_placa{sgn}", txt, .055, coll, lib["borracha_preta"], extrude=.002)
                t.location = (xx, 0, zz - .02)
                t.rotation_euler = (math.pi / 2, 0, math.pi / 2 if sgn > 0 else -math.pi / 2)
                bpy.context.view_layer.update()
                t.data.transform(t.matrix_basis)
                t.matrix_basis.identity()
                _join(o, t)
        except Exception:
            pass
    sa_bl.props(o, sa_stage="W3.2 veículo autoral (genérico, sem marca)", vehicle_family=family, paint=paint, worn=worn, lod=lod)
    return o


def van_like(f):
    return bool(f.get("van"))


def _interior(mb, f, gh, zt_f, zb_f, hw, s_f):
    """Minimal readable interior: dash, steering wheel, console, front seats, rear bench (driver on the left, +Y)."""
    x_rb, x_rr, x_rf, x_fb, roof = gh
    zf = .40
    xd = x_fb - .06
    zt = zt_f(xd)
    iw = hw * .88
    _extrude_xz(mb, [(xd - .60, zf - .08), (xd, zf - .08), (xd, zt + .03), (xd - .18, zt + .11), (xd - .42, zt + .09), (xd - .60, zt - .02)], -iw, iw, M["dash"])
    _rbox(mb, (xd - .50, .36, zt + .14), (.26, .36, .10), M["dash"])                                         # instrument hood
    ca = math.radians(24)
    cx_, cy_, cz_ = xd - .66, .36, zt - .04
    u = (0.0, 1.0, 0.0)
    v = (math.sin(ca), 0.0, math.cos(ca))
    nseg, nt = 16, 5
    tube = []
    for k in range(nseg):
        th = 2 * math.pi * k / nseg
        c = (cx_ + .19 * (math.cos(th) * u[0] + math.sin(th) * v[0]), cy_ + .19 * (math.cos(th) * u[1] + math.sin(th) * v[1]),
             cz_ + .19 * (math.cos(th) * u[2] + math.sin(th) * v[2]))
        rad = (math.cos(th) * u[0] + math.sin(th) * v[0], math.cos(th) * u[1] + math.sin(th) * v[1], math.cos(th) * u[2] + math.sin(th) * v[2])
        nrm = (-math.cos(ca), 0.0, math.sin(ca))
        ring = []
        for j in range(nt):
            ph = 2 * math.pi * j / nt
            ring.append(tuple(c[i] + .017 * (math.cos(ph) * rad[i] + math.sin(ph) * nrm[i]) for i in range(3)))
        tube.append(ring)
    for k in range(nseg):
        k2 = (k + 1) % nseg
        for j in range(nt):
            j2 = (j + 1) % nt
            mb.quad(tube[k][j], tube[k2][j], tube[k2][j2], tube[k][j2], M["dash"])
    _rbox(mb, (cx_, cy_, cz_), (.05, .10, .05), M["dash"], ry=-ca)
    for yy in (-1, 1):                                                                                       # spokes
        _rbox(mb, (cx_, cy_ + yy * .09, cz_ - .01), (.02, .17, .02), M["dash"], ry=-ca)
    _rbox(mb, (xd - .52, .36, zt - .02), (.22, .06, .06), M["dash"], ry=.5)                                  # column
    xs_f = x_fb - .98
    for yy in (.36, -.36):
        _seat(mb, xs_f, yy, zf)
    _rbox(mb, (xs_f + .25, 0.0, zf + .10), (.62, .20, .20), M["dash"])                                       # centre console
    xr_ = max(x_rb + .40, xs_f - .80)
    _rbox(mb, (xr_, 0.0, zf + .07), (.50, .96, .14), M["seat"])
    _rbox(mb, (xr_ - .22, 0.0, zf + .35), (.11, .96, .56), M["seat"], ry=-.2)
    for yy in (-.28, 0.0, .28):
        _rbox(mb, (xr_ - .26, yy, zf + .70), (.07, .16, .12), M["seat"])


def _seat(mb, x, y, zf):
    _rbox(mb, (x, y, zf + .07), (.50, .46, .14), M["seat"])
    _rbox(mb, (x - .22, y, zf + .35), (.11, .46, .56), M["seat"], ry=-.2)
    _rbox(mb, (x - .27, y, zf + .70), (.07, .20, .14), M["seat"])
    _rbox(mb, (x + .02, y, zf - .08), (.30, .30, .16), M["liner"])                                           # seat rail


def _van_extras(mb, f, hw, zt_f, zb_f):
    """Cab interior visible through the cab-door glass, rear door seams, slide door line, roof-light bar."""
    w0, w1, xa, xb = f["win"]
    zf = .42
    xd = xb - .05
    _extrude_xz(mb, [(xd - .55, zf - .1), (xd, zf - .1), (xd, 1.30), (xd - .20, 1.38), (xd - .45, 1.34), (xd - .55, 1.20)], -hw * .86, hw * .86, M["dash"])
    ca = math.radians(30)
    _rbox(mb, (xd - .66, .40, 1.22), (.04, .38, .04), M["dash"], ry=-ca)
    _rbox(mb, (xd - .66, .40, 1.22), (.05, .05, .35), M["dash"], ry=-ca)
    for yy in (.40, -.40):
        _rbox(mb, (xd - 1.05, yy, zf + .09), (.50, .50, .18), M["seat"])
        _rbox(mb, (xd - 1.28, yy, zf + .52), (.12, .50, .70), M["seat"], ry=-.15)
    for s in (-1, 1):
        for xs_, top_ in ((.35, 1.95), (-.95, 1.95), (xb - .30, 1.95)):                                       # slide / cab door seams
            zlo = f["zs"] + .12
            for xw_ in (f["wb"] / 2, -f["wb"] / 2):
                if abs(xs_ - xw_) < f["r"] + .08:
                    zlo = max(zlo, f["r"] + math.sqrt(max(0.0, (f["r"] + .06) ** 2 - (xs_ - xw_) ** 2)) + .05)
            _rbox(mb, (xs_, s * (hw + .004), (zlo + top_) / 2), (.012, .008, top_ - zlo), M["trim"])


# ---------------------------------------------------------------- mesh finishing
def _object(name, mb, materials, coll, bevel=.03):
    """Welds, triangulates concave n-gons and bevels hard edges."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.verts, [], mb.faces)
    me.update()
    for m in materials:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mb.mats)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.triangulate(bm, faces=[fc for fc in bm.faces if len(fc.verts) > 4], ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if bevel > 0:
        lim = math.radians(45)
        body = {0, 1}                                              # only paint / glass creases are bevelled (trim boxes stay crisp)
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim
                 and all(fc.material_index in body for fc in e.link_faces)]
        try:
            bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=1, profile=.5, affect="EDGES", clamp_overlap=True)
        except Exception:
            pass
    bm.to_mesh(me)
    bm.free()
    sa_bl.write_box_uvs(me)
    me.shade_smooth()
    try:
        me.set_sharp_from_angle(angle=math.radians(40))
    except AttributeError:
        pass
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o


def _join(target, other):
    me, ome = target.data, other.data
    nv = len(me.vertices)
    verts = [tuple(v.co) for v in me.vertices] + [tuple(v.co) for v in ome.vertices]
    faces = [tuple(p.vertices) for p in me.polygons] + [tuple(i + nv for i in p.vertices) for p in ome.polygons]
    mi = [p.material_index for p in me.polygons]
    mats = list(me.materials)
    om = ome.materials[0] if ome.materials else mats[0]
    if om not in mats:
        mats.append(om)
    mi += [mats.index(om)] * len(ome.polygons)
    smooth = [p.use_smooth for p in me.polygons] + [False] * len(ome.polygons)
    new = bpy.data.meshes.new(me.name)
    new.from_pydata(verts, [], faces)
    for m in mats:
        new.materials.append(m)
    new.polygons.foreach_set("material_index", mi)
    new.polygons.foreach_set("use_smooth", smooth)
    sa_bl.write_box_uvs(new)
    target.data = new
    bpy.data.objects.remove(other)


LIBRARY = [  # (family, paint, worn) variants instanced in the slice
    ("hatch", "branco", False), ("hatch", "vermelho", False), ("hatch", "prata", False), ("hatch", "preto", False),
    ("sedan", "prata", False), ("sedan", "azul_escuro", False), ("sedan", "branco", False), ("sedan", "bege", True),
    ("picape", "branco", False), ("picape", "verde_velho", True), ("suv", "preto", False), ("suv", "prata", False), ("suv", "vermelho", False),
    ("van", "branco", False), ("van", "amarelo_servico", False), ("hatch_antigo", "bege", True), ("hatch_antigo", "verde_velho", True),
    ("hatch_antigo", "azul_escuro", True), ("sedan", "verde_velho", True),
]

PAINT_ORDER = ("vermelho", "verde_velho", "branco", "prata", "azul_escuro", "bege", "preto")


def instance(family, lib, coll, paint, worn, name, lod=0):
    """Object sharing one mesh per (family, paint, worn, lod) variant."""
    key = f"VEHMESH_{family}_{paint}_{int(bool(worn))}_L{lod}"
    me = bpy.data.meshes.get(key)
    if me is None:
        o = build(family, lib, coll, paint, worn, lod, name=name)
        o.data.name = key
        return o
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    sa_bl.props(o, sa_stage="W3.2 veículo autoral (genérico, sem marca)", vehicle_family=family, paint=paint, worn=bool(worn), lod=lod)
    return o


def proxy(family, lib, coll):
    """Distance proxy: two boxes (body + cabin) with the family's footprint and height."""
    f = FAMILIES[family]
    L, W = f["L"], f["W"]
    hz = max(z for _, z in f["top"])
    mb = sa_bl.MeshBuilder()
    gh = f.get("gh")
    if f.get("van"):
        mb.box(0, 0, .25, L, W, hz - .25, 0)
    else:
        zt = _curve(f["top"])(0.0)
        mb.box(0, 0, .25, L, W, zt - .25, 0)
        mb.box((gh[1] + gh[2]) / 2 - .1, 0, zt, gh[3] - gh[0] - .6, W - .2, gh[4] - zt, 1)
    o = mb.to_object(f"VEH_{family}_PROXY", [paint_material(lib, "prata"), glass_material()], coll)
    sa_bl.props(o, sa_stage="W3.2 veículo proxy (distância)", vehicle_family=family, lod="proxy")
    return o
