"""W4 - Orla das Palmeiras: the southern coast of Santa Aurora (beaches, sea, promenade, avenue, piers, lighthouse, seafront).

Run:
blender --background --factory-startup --python Tools/Blender/create_coast.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/World/Coast/SantaAurora_Orla_v1.blend
ArtSource/Blender/World/Coast/orla_generation_report.json

The terrain comes from Tools/Map/sa_terrain.py (shore_z + coast profile), so the strip joins the masterplan terrain without a seam.
Original content only (no assets of other games). Seafront buildings are massing with floor bands; production art follows the Old Town pipeline.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
import sa_materials  # noqa: E402
from masterplan_layout import load_spec  # noqa: E402
from sa_geom import Noise2, smoothstep  # noqa: E402
from sa_terrain import COAST_PROMENADE_DZ, Terrain, shore_z  # noqa: E402

spec = load_spec(root)
coast = spec["coast"]
T = Terrain(spec)
rng = random.Random(4004)
dune_a = Noise2(random.Random(41), 90.0, octaves=2)
dune_b = Noise2(random.Random(42), 22.0, octaves=1)
patch_n = Noise2(random.Random(43), 140.0, octaves=2)
col_n = Noise2(random.Random(44), 55.0, octaves=2)

out_dir = root / "ArtSource" / "Blender" / "World" / "Coast"
out_dir.mkdir(parents=True, exist_ok=True)

sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "SantaAurora_W4_Orla"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
lib = sa_materials.build_library()
C = {n: sa_bl.collection(n) for n in ("00_Terrain", "01_Sea", "02_Promenade_Avenue", "03_Piers_Landmarks", "04_Seafront", "05_Beach_Props",
                                      "06_Vegetation", "07_Library", "08_Cameras")}
C["07_Library"].hide_render = True
PROM_DZ = COAST_PROMENADE_DZ
AVE_DZ = coast["avenue"]["offsetFromShore"]
X0, X1 = -4000.0, 4000.0


def dzf(x, z):
    return z - shore_z(x)


def ground(x, z):
    h = T.surface(x, z)
    d = dzf(x, z)
    if 25.0 < d < 150.0:
        k = smoothstep(25.0, 48.0, d) * smoothstep(150.0, 122.0, d)
        h += k * (1.15 * dune_a(x, z) + .30 * dune_b(x, z))
    return max(h, -9.0)


def tangent_angle(x):
    return math.atan2(shore_z(x + 5.0) - shore_z(x - 5.0), 10.0)


def alpha_material(name, color, alpha, rough=.5, emission=None):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Roughness"].default_value = rough
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = 3.0
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        pass
    m.diffuse_color = (*color, alpha)
    return m


def colour(name, base, **over):
    return sa_materials.build_material(name, dict(sa_materials.LIB[base], **over))


# ---------------------------------------------------------------- materials (sand, sea, foam, accents)
def sand_material():
    m = bpy.data.materials.new("MP_Orla_Areia")
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    L.new(b.outputs["BSDF"], out.inputs["Surface"])
    col = nt.nodes.new("ShaderNodeAttribute")
    col.attribute_name = "col"
    wet = nt.nodes.new("ShaderNodeAttribute")
    wet.attribute_name = "wet"
    sandy = nt.nodes.new("ShaderNodeAttribute")
    sandy.attribute_name = "sandy"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.inputs["Scale"].default_value = 140.0
    grain.inputs["Detail"].default_value = 6.0
    L.new(geo.outputs["Position"], grain.inputs["Vector"])
    blot = nt.nodes.new("ShaderNodeTexNoise")
    blot.inputs["Scale"].default_value = .35
    blot.inputs["Detail"].default_value = 3.0
    L.new(geo.outputs["Position"], blot.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    sfac = nt.nodes.new("ShaderNodeMath")
    sfac.operation = "MULTIPLY_ADD"
    sfac.inputs[1].default_value = .45
    sfac.inputs[2].default_value = .10
    L.new(sandy.outputs["Fac"], sfac.inputs[0])
    L.new(sfac.outputs[0], mix.inputs[0])
    L.new(col.outputs["Color"], mix.inputs[6])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = .72
    mr.inputs["To Max"].default_value = 1.18
    L.new(blot.outputs["Fac"], mr.inputs["Value"])
    L.new(mr.outputs["Result"], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs["Base Color"])
    rough = nt.nodes.new("ShaderNodeMath")
    rough.operation = "MULTIPLY_ADD"
    rough.inputs[1].default_value = -.78
    rough.inputs[2].default_value = .96
    L.new(wet.outputs["Fac"], rough.inputs[0])
    L.new(rough.outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = .06     # dry sand is diffuse; grazing-angle Fresnel was washing it grey-blue
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = .05
    sb = nt.nodes.new("ShaderNodeMath")
    sb.operation = "MULTIPLY"
    sb.inputs[1].default_value = .14
    L.new(sandy.outputs["Fac"], sb.inputs[0])
    L.new(sb.outputs[0], bump.inputs["Strength"])
    rip = nt.nodes.new("ShaderNodeTexWave")
    rip.inputs["Scale"].default_value = 2.2
    rip.inputs["Distortion"].default_value = 6.0
    rip.inputs["Detail"].default_value = 2.0
    L.new(geo.outputs["Position"], rip.inputs["Vector"])
    hsum = nt.nodes.new("ShaderNodeMath")
    hsum.operation = "ADD"
    L.new(grain.outputs["Fac"], hsum.inputs[0])
    rmul = nt.nodes.new("ShaderNodeMath")
    rmul.operation = "MULTIPLY"
    rmul.inputs[1].default_value = .35
    L.new(rip.outputs["Fac"], rmul.inputs[0])
    L.new(rmul.outputs[0], hsum.inputs[1])
    L.new(hsum.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = (.8, .7, .52, 1)
    return m


def sea_material():
    m = bpy.data.materials.new("MP_Orla_Mar")
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    L.new(b.outputs["BSDF"], out.inputs["Surface"])
    col = nt.nodes.new("ShaderNodeAttribute")
    col.attribute_name = "col"
    L.new(col.outputs["Color"], b.inputs["Base Color"])
    L.new(col.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = .05
    b.inputs["Specular IOR Level"].default_value = .9
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sw = nt.nodes.new("ShaderNodeTexNoise")
    sw.inputs["Scale"].default_value = .07
    sw.inputs["Detail"].default_value = 4.0
    L.new(geo.outputs["Position"], sw.inputs["Vector"])
    rip = nt.nodes.new("ShaderNodeTexNoise")
    rip.inputs["Scale"].default_value = .35
    rip.inputs["Detail"].default_value = 2.0
    L.new(geo.outputs["Position"], rip.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    L.new(sw.outputs["Fac"], add.inputs[0])
    L.new(rip.outputs["Fac"], add.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .22
    bump.inputs["Distance"].default_value = .6
    L.new(add.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], b.inputs["Normal"])
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        pass
    m.diffuse_color = (.05, .3, .36, .8)
    return m


M_SAND, M_SEA = sand_material(), sea_material()
M_FOAM = alpha_material("MP_Orla_Espuma", (.96, .98, .98), .62, .55)
M_CICLO = colour("MP_Orla_Ciclovia", "asfalto", c1=(.46, .16, .12), c2=(.36, .12, .09))
M_UMB = [colour("MP_Orla_Guardasol_A", "plastico", c1=(.80, .18, .12), c2=(.70, .14, .10)),
         colour("MP_Orla_Guardasol_B", "plastico", c1=(.92, .90, .84), c2=(.84, .82, .76)),
         colour("MP_Orla_Guardasol_C", "plastico", c1=(.10, .42, .62), c2=(.08, .34, .52)),
         colour("MP_Orla_Guardasol_D", "plastico", c1=(.95, .72, .12), c2=(.86, .62, .10))]
M_RED = colour("MP_Orla_FarolVermelho", "pintura_industrial", c1=(.70, .10, .08), c2=(.58, .08, .06))
M_WHITE = colour("MP_Orla_Branco", "concreto_pintado", c1=(.90, .89, .85), c2=(.80, .79, .75))
M_LAMP = alpha_material("MP_Orla_Lampada", (1.0, .86, .6), 1.0, .3, emission=(1.0, .8, .5))


# ---------------------------------------------------------------- terrain strip (5 m lattice, 1 km chunks)
def sand_colour(x, z, d):
    j = .93 + .12 * col_n(x, z)
    patch = patch_n(x, z)
    if d < -60:
        c, w = (.40, .38, .28), 1.0
    elif d < 0:
        t = smoothstep(-60, 0, d)
        c, w = (.40 + .08 * t, .38 + .02 * t, .28 + .02 * t), 1.0
    elif d < 7:
        c, w = (.47, .39, .29), 1.0
    elif d < 34:
        t = smoothstep(7, 34, d)
        c, w = (.47 + .53 * t, .36 + .36 * t, .24 + .12 * t), 1.0 - .8 * t
    elif d < PROM_DZ - 12:
        c, w = (1.0, .72, .36), 0.0
        if d > 112 and patch > .12:                         # beach-grass dunes next to the promenade
            g = smoothstep(.12, .45, patch) * smoothstep(112, 135, d)
            c = (c[0] + (.33 - c[0]) * g, c[1] + (.39 - c[1]) * g, c[2] + (.17 - c[2]) * g)
    elif d < AVE_DZ + 60:
        c, w = (.44, .41, .35), 0.0
    else:
        c, w = (.40, .37, .31), 0.0
    sandy_k = .86 if -60 <= d < PROM_DZ - 12 else 1.0
    return (min(1, c[0] * j * sandy_k), min(1, c[1] * j * sandy_k), min(1, c[2] * j * sandy_k), 1.0), w


STEP = 5.0
ZS0, ZS1 = -4350.0, -3150.0
nz = int(round((ZS1 - ZS0) / STEP))
tcount = 0
for chunk in range(8):
    cx0 = X0 + chunk * 1000.0
    nxc = int(1000 / STEP)
    verts, cols, wets, sandys, faces = [], [], [], [], []
    for i in range(nxc + 1):
        x = cx0 + i * STEP
        for j in range(nz + 1):
            z = ZS0 + j * STEP
            verts.append((x, z, ground(x, z)))
            c, w = sand_colour(x, z, dzf(x, z))
            cols.append(c)
            wets.append(w)
            sandys.append(1.0 if -2 < dzf(x, z) < PROM_DZ - 12 else 0.0)
    for i in range(nxc):
        for j in range(nz):
            a = i * (nz + 1) + j
            faces.append((a, a + nz + 1, a + nz + 2, a + 1))
    me = bpy.data.meshes.new(f"Terrain_Orla_{chunk:02d}")
    me.from_pydata(verts, [], faces)
    me.update()
    ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", [v for c in cols for v in c])
    wa = me.attributes.new("wet", "FLOAT", "POINT")
    wa.data.foreach_set("value", wets)
    sa = me.attributes.new("sandy", "FLOAT", "POINT")
    sa.data.foreach_set("value", sandys)
    me.materials.append(M_SAND)
    me.shade_smooth()
    o = bpy.data.objects.new(f"Terrain_Orla_{chunk:02d}", me)
    C["00_Terrain"].objects.link(o)
    sa_bl.props(o, sa_layer="Terrain", coast_chunk=chunk)
    tcount += len(verts)

# ---------------------------------------------------------------- sea (graded colour + alpha, rows follow the waterline)
OFFS = [8, -2, -8, -16, -30, -50, -80, -120, -180, -260, -380, -550, -800, -1200, -2000, -3500, -7000]
XS = [-16000.0, -9000.0, -5000.0] + [X0 - 600 + k * 20.0 for k in range(int((X1 - X0 + 1200) / 20) + 1)] + [5000.0, 9000.0, 16000.0]


def sea_col(off):
    d = -off
    t = smoothstep(0, 260, d)
    t2 = smoothstep(200, 1400, d)
    r = .20 + (.04 - .20) * t + (.015 - .04) * t2
    g = .62 + (.36 - .62) * t + (.17 - .36) * t2
    b = .60 + (.46 - .60) * t + (.28 - .46) * t2
    a = .30 + .62 * smoothstep(0, 140, d) + .08 * smoothstep(140, 600, d)
    return (r, g, b, min(1.0, a))


sv, sc, sf = [], [], []
for xi, x in enumerate(XS):
    for k, off in enumerate(OFFS):
        sv.append((x, shore_z(x) + off, 0.0))
        sc.append(sea_col(off))
for xi in range(len(XS) - 1):
    for k in range(len(OFFS) - 1):
        a = xi * len(OFFS) + k
        sf.append((a, a + len(OFFS), a + len(OFFS) + 1, a + 1))
me = bpy.data.meshes.new("Sea_Orla")
me.from_pydata(sv, [], sf)
me.update()
ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
ca.data.foreach_set("color", [v for c in sc for v in c])
me.materials.append(M_SEA)
sea = bpy.data.objects.new("Sea_Orla", me)
C["01_Sea"].objects.link(sea)
sa_bl.props(sea, sa_layer="Terrain", sea_level_m=0.0)

mb = sa_bl.MeshBuilder()
xs_line = [X0 - 200 + k * 10.0 for k in range(int((X1 - X0 + 400) / 10) + 1)]
mb.ribbon([(x, shore_z(x) - 3.0) for x in xs_line], 2.4, lambda a, b: 0.0, lift=.04, mat=0, step=10.0)   # swash
x = X0
while x < X1:
    for dz_, wd in ((-7.0, 1.6), (-22.0, 2.4), (-52.0, 3.2)):
        ln = rng.uniform(14, 70)
        if rng.random() < .72:
            pts = [(x + s, shore_z(x + s) + dz_ + 1.5 * math.sin((x + s) / 9.0)) for s in range(0, int(ln) + 1, 6)]
            if len(pts) > 1:
                mb.ribbon(pts, wd * rng.uniform(.6, 1.2), lambda a, b: 0.0, lift=.05, mat=0, step=6.0)
    x += rng.uniform(12, 55)
foam = mb.to_object("Foam_Orla", [M_FOAM], C["01_Sea"])
sa_bl.props(foam, sa_layer="Terrain")

# ---------------------------------------------------------------- promenade, bike lane, avenue, plaza, cross streets
mb = sa_bl.MeshBuilder()
RM = ["pedra_portuguesa", "meio_fio", "asfalto", "calcada", "sinalizacao_viaria", "concreto", "grama"]
R = {k: i for i, k in enumerate(RM)}
nmat = len(RM)
xs_line = [X0 + k * 10.0 for k in range(int((X1 - X0) / 10) + 1)]
prom = [(x, shore_z(x) + PROM_DZ) for x in xs_line]
ave = [(x, shore_z(x) + AVE_DZ) for x in xs_line]
zs = T.surface
mb.ribbon(prom, 12.0, zs, lift=.14, mat=R["pedra_portuguesa"], step=10.0)
for s_ in (-1, 1):
    mb.ribbon(prom, .45, zs, lift=.26, mat=R["meio_fio"], step=10.0, offset=s_ * 6.2)
mb.ribbon(prom, 2.6, zs, lift=.14, mat=nmat, step=10.0, offset=9.0)                       # red bike lane (material index nmat)
mb.ribbon(prom, 24.0, zs, lift=.06, mat=R["grama"], step=10.0, offset=22.0)               # planted verge
mb.ribbon(ave, 15.0, zs, lift=.14, mat=R["asfalto"], step=10.0)
for s_ in (-1, 1):
    mb.ribbon(ave, 4.2, zs, lift=.2, mat=R["calcada"], step=10.0, offset=s_ * 9.6)
    mb.ribbon(ave, .45, zs, lift=.24, mat=R["meio_fio"], step=10.0, offset=s_ * 7.6)
x = X0
while x < X1 - 30:                                                                          # centre dashes
    seg = [(x + s, shore_z(x + s) + AVE_DZ) for s in range(0, 31, 10)]
    mb.ribbon(seg, .16, zs, lift=.16, mat=R["sinalizacao_viaria"], step=10.0)
    x += 44.0
# plaza where R03 (Av. das Palmeiras) meets the avenue
r03x = 100.0
pc = (r03x, shore_z(r03x) + (PROM_DZ + AVE_DZ) / 2 - 2)
mb.box(pc[0], pc[1], zs(*pc) - .1, 64.0, 34.0, .45, R["pedra_portuguesa"])
# cross streets (access to the interior blocks)
streets = [x for x in range(-3600, 3601, 450) if abs(x - r03x) > 120]
for sx_ in streets:
    p0 = (float(sx_), shore_z(sx_) + AVE_DZ + 8)
    p1 = (float(sx_), shore_z(sx_) + AVE_DZ + 420)
    mb.ribbon([p0, p1], 9.0, zs, lift=.12, mat=R["asfalto"], step=12.0)
    for s_ in (-1, 1):
        mb.ribbon([p0, p1], 2.6, zs, lift=.18, mat=R["calcada"], step=12.0, offset=s_ * 5.8)
rm = [lib[k] for k in RM] + [M_CICLO]
pa = mb.to_object("Promenade_Avenue_Orla", rm, C["02_Promenade_Avenue"])
sa_bl.props(pa, sa_layer="Roads", road_name=coast["avenue"]["name"], ties_to=coast["avenue"]["tiesTo"])

# ---------------------------------------------------------------- library: palms, grass, umbrellas, loungers, lamps, benches, boulders, boats
lib_objs = []


def lib_obj(name, mb_, mats, smooth=False):
    o = mb_.to_object(name, mats, C["07_Library"], smooth=smooth)
    lib_objs.append(o)
    return o


def palm(name, h, lean, seed):
    r = random.Random(seed)
    mb_ = sa_bl.MeshBuilder()
    rings, nseg = 12, 10
    lean_dir = r.uniform(0, 6.28)
    ld = (math.cos(lean_dir), math.sin(lean_dir))

    def ctr(tt):
        return (lean * tt ** 1.7 * ld[0], lean * tt ** 1.7 * ld[1], h * tt)

    prev = None
    for k in range(rings + 1):
        tt = k / rings
        rad = (.40 - .17 * tt) * (1.0 + (.55 * (1 - tt) ** 6)) * (1.0 + .05 * math.cos(k * math.pi))
        cx_, cy_, cz_ = ctr(tt)
        ring = [(cx_ + rad * math.cos(2 * math.pi * s / nseg), cy_ + rad * math.sin(2 * math.pi * s / nseg), cz_) for s in range(nseg)]
        if prev:
            for s in range(nseg):
                s2 = (s + 1) % nseg
                mb_.quad(prev[s], prev[s2], ring[s2], ring[s], 0)
        prev = ring
    top = ctr(1.0)
    n_fr = 14
    for f in range(n_fr):
        a = 2 * math.pi * f / n_fr + r.uniform(-.12, .12)
        ln = r.uniform(4.6, 5.8)
        rise = r.uniform(.5, 1.5) if f % 2 else r.uniform(1.4, 2.2)
        droop = r.uniform(1.8, 3.2)
        ca_, sa_ = math.cos(a), math.sin(a)
        stations = 7
        pts = []
        for s in range(stations + 1):
            u = s / stations
            rad = ln * u
            zz = rise * math.sin(math.pi * u * .8) - droop * u * u
            wd = .62 * math.sin(math.pi * min(1.0, u * 1.08)) ** .7 + .04
            pts.append((rad, zz, wd))
        for (r0, z0, w0), (r1, z1, w1) in zip(pts, pts[1:]):
            def P(rad, zz, side, w_):
                return (top[0] + ca_ * rad - sa_ * side, top[1] + sa_ * rad + ca_ * side, top[2] - .15 + zz - abs(side) * .45 - .0 * w_)
            mb_.add_face([P(r0, z0, -w0, w0), P(r1, z1, -w1, w1), P(r1, z1, 0, 0), P(r0, z0, 0, 0)], 1)
            mb_.add_face([P(r0, z0, 0, 0), P(r1, z1, 0, 0), P(r1, z1, w1, w1), P(r0, z0, w0, w0)], 1)
        for sgn in (-1, 1):                                    # leaflet fringe hanging from the midrib
            for s in range(1, stations):
                u = s / stations
                rad = ln * u
                zz = rise * math.sin(math.pi * u * .8) - droop * u * u
                wd = pts[s][2]
                x0_ = top[0] + ca_ * rad - sa_ * sgn * wd
                y0_ = top[1] + sa_ * rad + ca_ * sgn * wd
                z0_ = top[2] - .15 + zz - wd * .45
                mb_.add_face([(x0_, y0_, z0_), (x0_ + ca_ * .55 - sa_ * sgn * .12, y0_ + sa_ * .55 + ca_ * sgn * .12, z0_ - .75),
                              (x0_ + ca_ * .28, y0_ + sa_ * .28, z0_ - .08)], 1)
    for k in range(6):
        mb_.cylinder(top[0] + .32 * math.cos(k * 1.1), top[1] + .32 * math.sin(k * 1.1), top[2] - .55, .14, .28, 6, 0)
    return lib_obj(name, mb_, [lib["tronco"], lib["folhagem"]], smooth=False)


palms = [palm("LIB_Palma_A", 9.0, 1.1, 1), palm("LIB_Palma_B", 11.5, 1.8, 2), palm("LIB_Palma_C", 13.5, 2.4, 3), palm("LIB_Palma_D", 7.0, .6, 4)]

mb = sa_bl.MeshBuilder()
for k in range(7):
    a = k * math.pi / 3.5 + .3
    ca_, sa_ = math.cos(a), math.sin(a)
    mb.add_face([(0, 0, 0), (ca_ * .45 - sa_ * .03, sa_ * .45 + ca_ * .03, .55), (ca_ * .75, sa_ * .75, .35)], 0)
    mb.add_face([(0, 0, 0), (ca_ * .45 + sa_ * .03, sa_ * .45 - ca_ * .03, .55), (ca_ * .75, sa_ * .75, .35)], 0)
grass = lib_obj("LIB_Capim_Duna", mb, [lib["folhagem"]])

umbs = []
for ui in range(4):
    mb = sa_bl.MeshBuilder()
    mb.cylinder(0, 0, 0, .025, 2.35, 6, 1)
    ring = [(1.15 * math.cos(2 * math.pi * k / 10), 1.15 * math.sin(2 * math.pi * k / 10), 2.0) for k in range(10)]
    for k in range(10):
        mb.add_face([(0, 0, 2.5), ring[k], ring[(k + 1) % 10]], 0 if k % 2 == 0 else 1)
    umbs.append(lib_obj(f"LIB_Guardasol_{ui}", mb, [M_UMB[ui], M_WHITE, lib["aluminio"]]))

mb = sa_bl.MeshBuilder()
for sx_ in (-.4, .4):
    mb.box(sx_, 0, .0, .08, 1.9, .30, 0)
mb.box(0, 0, .30, .8, 1.9, .06, 0)
mb.box(0, .75, .36, .8, .6, .30, 0, rot=0.0)
lounger = lib_obj("LIB_Espreguicadeira", mb, [lib["plastico"]])

mb = sa_bl.MeshBuilder()
mb.cylinder(0, 0, 0, .09, 7.4, 8, 0)
mb.box(0, .7, 7.0, .14, 1.5, .14, 0)
mb.box(0, 1.35, 6.82, .5, .3, .22, 0)
mb.box(0, 1.35, 6.8, .4, .24, .05, 1)
lamp = lib_obj("LIB_Poste_Orla", mb, [lib["aco_pintado_cinza"], M_LAMP])

mb = sa_bl.MeshBuilder()
mb.box(0, 0, .45, 1.9, .5, .07, 0)
mb.box(0, -.25, .55, 1.9, .06, .5, 0)
for sx_ in (-.8, .8):
    mb.box(sx_, 0, 0, .1, .45, .45, 1)
bench = lib_obj("LIB_Banco_Orla", mb, [lib["madeira_crua"], lib["aco_pintado_cinza"]])

boulders = []
for bi in range(3):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    r = random.Random(100 + bi)
    ph = [r.uniform(0, 6.28) for _ in range(6)]
    for v in bm.verts:
        k = 1.0 + .22 * math.sin(v.co.x * 2.3 + ph[0]) * math.cos(v.co.y * 1.9 + ph[1]) + .14 * math.sin(v.co.z * 3.1 + v.co.x * 1.7 + ph[2]) + r.uniform(-.04, .04)
        v.co.x *= k * 1.25
        v.co.y *= k * 1.0
        v.co.z *= k * .62
    me = bpy.data.meshes.new(f"LIB_Rocha_{bi}")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(lib["pedra_costao"])
    me.shade_smooth()
    o = bpy.data.objects.new(f"LIB_Rocha_{bi}", me)
    C["07_Library"].objects.link(o)
    lib_objs.append(o)
    boulders.append(o)

boats = []
for bi, (ln, wd) in enumerate(((11.0, 3.4), (8.5, 2.9), (15.0, 4.2))):
    mb = sa_bl.MeshBuilder()
    hull = [(-ln / 2, -wd / 2), (ln / 4, -wd / 2), (ln / 2, 0), (ln / 4, wd / 2), (-ln / 2, wd / 2)]
    mb.prism(hull, .0, 1.1, 0, side_mat=0)
    mb.box(-ln * .08, 0, 1.1, ln * .42, wd * .66, 1.1, 1)
    mb.box(-ln * .08, 0, 2.2, ln * .46, wd * .72, .1, 0)
    boats.append(lib_obj(f"LIB_Barco_{bi}", mb, [M_WHITE, lib["vidro_fachada"]]))


def library_of(objs, name):
    c, idx = sa_bl.library_collection(name, objs, C["07_Library"])
    return c, idx


pl_c, pl_i = library_of(palms, "LIB_Palmas")
gr_c, gr_i = library_of([grass], "LIB_Capim")
um_c, um_i = library_of(umbs, "LIB_Guardasois")
lo_c, lo_i = library_of([lounger], "LIB_Espreguicadeiras")
la_c, la_i = library_of([lamp], "LIB_Postes")
be_c, be_i = library_of([bench], "LIB_Bancos")
ro_c, ro_i = library_of(boulders, "LIB_Rochas")
bo_c, bo_i = library_of(boats, "LIB_Barcos")

# ---------------------------------------------------------------- vegetation: palms (promenade verge, avenue, dunes), dune grass
palm_pts = []
for x in range(-3990, 3990, 15):
    for dz_, jit in ((PROM_DZ + 14.5, 1.0), (PROM_DZ + 26.0, 1.5), (AVE_DZ - 11.5, 1.0), (AVE_DZ + 11.5, 1.0)):
        if abs(x - r03x) < 36 and dz_ < AVE_DZ - 5:
            continue
        xx = x + rng.uniform(-2.5, 2.5) + (7.5 if dz_ in (PROM_DZ + 26.0, AVE_DZ + 11.5) else 0.0)
        zz = shore_z(xx) + dz_ + rng.uniform(-jit, jit)
        palm_pts.append((xx, zz, zs(xx, zz) - .1, rng.randrange(len(palms)), rng.uniform(0, 6.28), rng.uniform(.82, 1.18)))
for _ in range(900):                     # scattered dune palms
    xx = rng.uniform(X0 + 40, X1 - 40)
    zz = shore_z(xx) + rng.uniform(112, 160)
    if patch_n(xx, zz) > .2 and rng.random() < .35:
        palm_pts.append((xx, zz, ground(xx, zz) - .1, rng.randrange(len(palms)), rng.uniform(0, 6.28), rng.uniform(.7, 1.1)))
for chunk in range(8):
    pts = [p for p in palm_pts if X0 + chunk * 1000 <= p[0] < X0 + (chunk + 1) * 1000]
    if pts:
        o = sa_bl.point_cloud_object(f"Palms_Orla_{chunk:02d}", pts, pl_c, C["06_Vegetation"])
        sa_bl.props(o, sa_layer="Vegetation", blockout_vegetation=True)

grass_pts = []
for _ in range(22000):
    xx = rng.uniform(X0, X1)
    zz = shore_z(xx) + rng.uniform(100, 166)
    pv = patch_n(xx, zz)
    if dzf(xx, zz) > 112 and pv > .16 and rng.random() < smoothstep(.12, .5, pv):
        grass_pts.append((xx, zz, ground(xx, zz), 0, rng.uniform(0, 6.28), rng.uniform(.8, 1.9)))
for chunk in range(8):
    pts = [p for p in grass_pts if X0 + chunk * 1000 <= p[0] < X0 + (chunk + 1) * 1000]
    if pts:
        o = sa_bl.point_cloud_object(f"Grass_Orla_{chunk:02d}", pts, gr_c, C["06_Vegetation"])
        sa_bl.props(o, sa_layer="Vegetation", blockout_vegetation=True)

# ---------------------------------------------------------------- street furniture along promenade and avenue
lamp_pts, bench_pts = [], []
for x in range(-3990, 3990, 30):
    zz = shore_z(x) + PROM_DZ + 7.0
    lamp_pts.append((x, zz, zs(x, zz), 0, math.pi * 1.5 - tangent_angle(x) * 0, 1.0))
for x in range(-3980, 3980, 36):
    for s_ in (-1, 1):
        zz = shore_z(x) + AVE_DZ + s_ * 8.4
        lamp_pts.append((x, zz, zs(x, zz), 0, math.pi * (1.5 if s_ < 0 else .5), 1.0))
for x in range(-3960, 3960, 44):
    zz = shore_z(x) + PROM_DZ - 6.8
    bench_pts.append((x, zz, zs(x, zz), 0, math.pi * .5 + tangent_angle(x), 1.0))
for chunk in range(8):
    for nm, src, cc in (("Lamps", lamp_pts, la_c), ("Benches", bench_pts, be_c)):
        pts = [p for p in src if X0 + chunk * 1000 <= p[0] < X0 + (chunk + 1) * 1000]
        if pts:
            o = sa_bl.point_cloud_object(f"{nm}_Orla_{chunk:02d}", pts, cc, C["05_Beach_Props"])
            sa_bl.props(o, sa_layer="Props")

# ---------------------------------------------------------------- beach life: umbrellas and loungers in clusters, volleyball courts
um_pts, lo_pts = [], []
centres = [(-3400, 1), (-2600, 1), (-1900, 1), (-1200, 1), (-500, 1.2), (100, 1.6), (700, 1.2), (1900, 1), (2150, 1.4), (2800, 1), (3500, 1)]
for cx, dens in centres:
    n_cl = int(190 * dens)
    for _ in range(n_cl):
        xx = cx + rng.gauss(0, 150 * dens)
        dz_ = rng.uniform(46, 112)
        zz = shore_z(xx) + dz_
        if abs(xx - 100) < 14 and dz_ > 0:
            continue
        h = ground(xx, zz)
        rot = rng.uniform(0, 6.28)
        um_pts.append((xx, zz, h, rng.randrange(4), rot, rng.uniform(.9, 1.1)))
        for k in range(2):
            la = rot + (math.pi * .5 if k else -math.pi * .5) + rng.uniform(-.3, .3)
            lx, lz = xx + math.cos(la) * 1.6, zz + math.sin(la) * 1.6
            lo_pts.append((lx, lz, ground(lx, lz) + .02, 0, tangent_angle(xx) + math.pi * .5 + rng.uniform(-.25, .25), 1.0))
for chunk in range(8):
    for nm, src, cc in (("Umbrellas", um_pts, um_c), ("Loungers", lo_pts, lo_c)):
        pts = [p for p in src if X0 + chunk * 1000 <= p[0] < X0 + (chunk + 1) * 1000]
        if pts:
            o = sa_bl.point_cloud_object(f"{nm}_Orla_{chunk:02d}", pts, cc, C["05_Beach_Props"])
            sa_bl.props(o, sa_layer="Props")

mb = sa_bl.MeshBuilder()
courts = [(-2900, 100), (-1500, 105), (-300, 98), (600, 100), (1950, 104), (3000, 100)]
for cxx, dz_ in courts:
    zc = shore_z(cxx) + dz_
    a = tangent_angle(cxx)
    hz = ground(cxx, zc)
    pts_c = [(-8, -4), (8, -4), (8, 4), (-8, 4), (-8, -4)]
    wpt = [(cxx + px * math.cos(a) - py * math.sin(a), zc + px * math.sin(a) + py * math.cos(a)) for px, py in pts_c]
    for p0, p1 in zip(wpt, wpt[1:]):
        mb.ribbon([p0, p1], .1, lambda x_, y_, hz=hz: hz, lift=.03, mat=1, step=4.0)
    for sx_ in (-1, 1):
        mb.cylinder(cxx + sx_ * 0 + (-sx_ * 0), zc + sx_ * 4.1, hz, .06, 2.5, 6, 0)
    mb.box(cxx, zc, hz + 1.9, .03, 8.2, .75, 2, rot=a)
vb = mb.to_object("Volleyball_Courts", [lib["aluminio"], lib["sinalizacao_viaria"], lib["plastico"]], C["05_Beach_Props"])
sa_bl.props(vb, sa_layer="Props")

# ---------------------------------------------------------------- piers
mb = sa_bl.MeshBuilder()
for pier in coast["piers"]:
    px = float(pier["x"])
    zA = shore_z(px) + 150.0
    ln, wd = pier["length"], pier["width"]
    deck_z = 2.95
    zB = zA - ln
    mb.box(px, (zA + zB) / 2, deck_z - .3, wd, ln, .3, 1)
    head_w, head_l = wd * 2.6, wd * 1.8
    mb.box(px, zB - head_l / 2 + 2, deck_z - .3, head_w, head_l, .3, 1)
    for k in range(int(ln // 9) + 1):
        zz = zA - k * 9.0
        for sx_ in (-wd / 2 + .5, wd / 2 - .5):
            mb.box(px + sx_, zz, -7.0, .5, .5, deck_z - .3 + 7.0, 0)
        mb.box(px, zz, deck_z - .65, wd, .45, .35, 0)
    for sx_ in (-wd / 2 + .06, wd / 2 - .06):                        # railings
        mb.box(px + sx_, (zA + zB) / 2, deck_z, .08, ln, 1.05, 2, top=True)
    for sx_ in (-head_w / 2 + .06, head_w / 2 - .06):
        mb.box(px + sx_, zB - head_l / 2 + 2, deck_z, .08, head_l, 1.05, 2)
    mb.box(px, zB - head_l + 2, deck_z, head_w, .08, 1.05, 2)
    mb.box(px, zB - head_l / 2 + 2, deck_z + 3.2, 6.0, 4.0, .18, 3)    # shade canopy
    for cxp, czp in ((px - 2.6, zB - head_l / 2 + 3.5), (px + 2.6, zB - head_l / 2 + 3.5), (px - 2.6, zB - head_l / 2 + .5), (px + 2.6, zB - head_l / 2 + .5)):
        mb.cylinder(cxp, czp, deck_z, .07, 3.2, 6, 2)
pier_obj = mb.to_object("Piers_Orla", [lib["madeira_crua"], lib["madeira_pintada"], lib["aluminio"], lib["telha_metalica"]], C["03_Piers_Landmarks"])
sa_bl.props(pier_obj, sa_layer="Architecture", piers=",".join(p["id"] for p in coast["piers"]))
pier_lamps = []
for pier in coast["piers"]:
    for k in range(int(pier["length"] // 24) + 1):
        for s_ in (-1, 1):
            pier_lamps.append((pier["x"] + s_ * (pier["width"] / 2 - .35), shore_z(pier["x"]) + 150.0 - 6 - k * 24.0, 2.95, 0, math.pi * (1.5 if s_ < 0 else .5), .55))
o_ = sa_bl.point_cloud_object("Pier_Lamps_Orla", pier_lamps, la_c, C["03_Piers_Landmarks"])
sa_bl.props(o_, sa_layer="Props")

# ---------------------------------------------------------------- lighthouse + keeper house on the east headland
lx = float(coast["landmarks"][0]["x"])
lz = shore_z(lx) + 118.0
lg = ground(lx, lz)
mb = sa_bl.MeshBuilder()
mb.box(lx, lz, lg - 1, 15.0, 15.0, 2.4, 0)
y0 = lg + 1.4
for r_, h_, m_ in ((5.0, 12.0, 1), (4.55, 9.0, 2), (4.15, 9.0, 1), (3.8, 8.0, 2), (3.5, 7.0, 1)):
    mb.cylinder(lx, lz, y0, r_, h_, 20, m_, top=False)
    y0 += h_
mb.cylinder(lx, lz, y0, 5.4, .7, 20, 3)
mb.cylinder(lx, lz, y0 + .7, 5.2, 1.05, 20, 3, top=False)
mb.cylinder(lx, lz, y0 + .7, 2.7, 4.0, 14, 4)
ring = [(lx + 3.1 * math.cos(2 * math.pi * k / 14), lz + 3.1 * math.sin(2 * math.pi * k / 14), y0 + 4.7) for k in range(14)]
for k in range(14):
    mb.add_face([ring[k], ring[(k + 1) % 14], (lx, lz, y0 + 7.2)], 2)
mb.box(lx + 14, lz - 4, lg - .5, 12.0, 8.0, 4.8, 0)
mb.add_face([(lx + 7.6, lz - 8.6, lg + 4.3), (lx + 20.4, lz - 8.6, lg + 4.3), (lx + 20.4, lz - 4, lg + 6.6), (lx + 7.6, lz - 4, lg + 6.6)], 5)
mb.add_face([(lx + 7.6, lz + .6, lg + 4.3), (lx + 20.4, lz + .6, lg + 4.3), (lx + 20.4, lz - 4, lg + 6.6), (lx + 7.6, lz - 4, lg + 6.6)], 5)
lh = mb.to_object("Farol_Santa_Aurora", [lib["concreto_pintado"], M_WHITE, M_RED, lib["aco_pintado_cinza"], lib["vidro_vitrine"], lib["ceramica_telha"]],
                  C["03_Piers_Landmarks"])
sa_bl.props(lh, facility_id=coast["landmarks"][0]["id"], sa_layer="Architecture")
beam = bpy.data.lights.new("Farol_Luz", "SPOT")
beam.energy = 4.0e6
beam.spot_size = math.radians(24)
beam.color = (1.0, .92, .72)
bo_ = bpy.data.objects.new("Farol_Luz", beam)
C["03_Piers_Landmarks"].objects.link(bo_)
bo_.location = (lx, lz, y0 + 3.0)
bo_.rotation_euler = (math.radians(92), 0, math.radians(200))

# ---------------------------------------------------------------- lifeguard towers and kiosks
mb = sa_bl.MeshBuilder()
x = -3700.0
n_tower = 0
while x < 3700:
    zz = shore_z(x) + 92.0
    g_ = ground(x, zz)
    for sx_ in (-1.1, 1.1):
        for sz_ in (-1.1, 1.1):
            mb.box(x + sx_, zz + sz_, g_ - .3, .2, .2, 3.1, 0)
    mb.box(x, zz, g_ + 2.6, 3.0, 3.0, .18, 0)
    mb.box(x, zz, g_ + 2.78, 2.2, 2.2, 2.1, 1)
    mb.box(x, zz, g_ + 4.88, 3.0, 3.0, .16, 2)
    mb.box(x, zz - 1.12, g_ + 3.4, 1.4, .05, .9, 3)
    mb.ribbon([(x + 1.6, zz + 1.2), (x + 3.4, zz + 3.4)], .9, lambda a_, b_, g_=g_: g_ + .5, lift=.0, mat=0, step=1.0)
    x += coast["lifeguardEvery"] + rng.uniform(-30, 30)
    n_tower += 1
x = -3600.0
n_kiosk = 0
while x < 3600:
    if abs(x - r03x) > 50:
        zz = shore_z(x) + PROM_DZ + 19.0
        g_ = zs(x, zz)
        a = tangent_angle(x)
        mb.box(x, zz, g_, 7.0, 4.6, 3.1, 4, rot=a)
        mb.box(x, zz, g_ + 3.1, 8.6, 6.0, .22, 5, rot=a)
        mb.box(x - math.sin(a) * -2.3, zz - 2.3 * math.cos(a), g_ + 1.0, 5.4, .1, 1.1, 6, rot=a)
        for k in range(4):
            tx = x + (k - 1.5) * 1.9
            mb.cylinder(tx - math.sin(a) * -4.6, zz - 4.6 * math.cos(a), g_, .55, .05, 10, 0)
            mb.cylinder(tx - math.sin(a) * -4.6, zz - 4.6 * math.cos(a), g_ + .05, .05, .7, 6, 0)
            mb.cylinder(tx - math.sin(a) * -4.6, zz - 4.6 * math.cos(a), g_ + .75, .5, .04, 10, 0)
        n_kiosk += 1
    x += coast["kioskEvery"] + rng.uniform(-40, 40)
beach_struct = mb.to_object("Beach_Structures_Orla", [lib["madeira_pintada"], lib["plastico"], lib["aco_pintado_cinza"], lib["aluminio"], lib["reboco_pastilha"],
                                                       lib["telha_metalica"], lib["vidro_vitrine"]], C["05_Beach_Props"])
sa_bl.props(beach_struct, sa_layer="Props", lifeguard_towers=n_tower, kiosks=n_kiosk)

# ---------------------------------------------------------------- rocks (headland costao + breakwater of the east marina) and boats
rock_pts = []
for _ in range(520):
    xx = lx + rng.gauss(0, 140)
    dz_ = rng.uniform(-70, 60)
    zz = shore_z(xx) + dz_
    sc_ = rng.uniform(.9, 4.2) * (1.4 if abs(xx - lx) < 90 else 1.0)
    rock_pts.append((xx, zz, ground(xx, zz) + (0 if dz_ > 0 else max(-.5, ground(xx, zz) * 0)) - .25 * sc_, rng.randrange(3), rng.uniform(0, 6.28), sc_))
bx0 = 2330.0
for k in range(110):
    t = k / 109
    xx = bx0 + 60.0 * math.sin(t * 2.2) + t * 40
    zz = shore_z(xx) + 40 - 300 * t
    for dd in (-1.2, 1.2):
        sc_ = rng.uniform(1.6, 3.0)
        rock_pts.append((xx + dd + rng.uniform(-.6, .6), zz + rng.uniform(-.8, .8), max(0.4, 1.0 - t * .6) - 1.2 + sc_ * .3, rng.randrange(3), rng.uniform(0, 6.28), sc_))
o = sa_bl.point_cloud_object("Rocks_Orla", rock_pts, ro_c, C["03_Piers_Landmarks"])
sa_bl.props(o, sa_layer="Terrain")
boat_pts = []
for _ in range(34):
    xx = 2150 + rng.uniform(-220, 330)
    zz = shore_z(xx) - rng.uniform(50, 230)
    boat_pts.append((xx, zz, .1, rng.randrange(3), rng.uniform(0, 6.28), rng.uniform(.9, 1.2)))
o = sa_bl.point_cloud_object("Boats_Orla", boat_pts, bo_c, C["03_Piers_Landmarks"])
sa_bl.props(o, sa_layer="Props")

# ---------------------------------------------------------------- seafront: two rows of buildings along the avenue (massing with floor bands)
FACADE = ["reboco_pintado", "reboco_pintado", "concreto_pintado", "reboco_pastilha", "concreto_pintado", "reboco_pastilha"]
if "fachada_cortina" not in lib:
    lib["fachada_cortina"] = sa_materials.build_material("fachada_cortina", {
        "family": "vidro", "c1": (.26, .34, .40), "c2": (.18, .24, .30), "rough": (.08, .2), "scale": 1.0, "bump": .2, "pattern": "tiles",
        "tile": (1.5, 3.8, .06), "mortar": (.55, .57, .58), "metal": .4, "grime": .2, "dirt": 0.0, "spec": .8, "texel": 256})
SEASIDE = {"orla_areia": (.74, .62, .44), "orla_branco": (.80, .79, .74), "orla_amarelo": (.80, .64, .26), "orla_azul": (.40, .56, .62),
           "orla_coral": (.72, .38, .28), "orla_verde": (.46, .58, .46)}
for nm_, c_ in SEASIDE.items():
    lib[nm_] = sa_materials.build_material("MP_" + nm_, dict(sa_materials.LIB["reboco_pintado"], c1=c_, c2=tuple(v * .86 for v in c_), tint=(0.0, 0.0)))
FACADE = ["orla_areia", "orla_branco", "orla_amarelo", "orla_azul", "orla_coral", "orla_verde", "orla_branco", "orla_areia", "reboco_pastilha"]
FM = ["reboco_pintado", "concreto_pintado", "reboco_pastilha", "fachada_cortina", "concreto", "aco_pintado_cinza", "vidro_vitrine", "telha_metalica"] + list(SEASIDE)
FI = {k: i for i, k in enumerate(FM)}
sf_cells = {}
n_build = 0
for row, (d0, d1, hlo, hhi) in enumerate(((AVE_DZ + 22, AVE_DZ + 62, 14.0, 52.0), (AVE_DZ + 92, AVE_DZ + 150, 24.0, 96.0))):
    x = X0 + 20.0
    while x < X1 - 60:
        w = rng.uniform(26, 52) if row == 0 else rng.uniform(34, 60)
        xc = x + w / 2
        near_cross = any(abs(xc - s_) < w / 2 + 11 for s_ in streets)
        near_r03 = abs(xc - r03x) < w / 2 + 18
        if near_cross or near_r03 or (row == 1 and rng.random() < .35):
            x += w * .5 + 6
            continue
        dep = rng.uniform(26, 38) if row == 0 else rng.uniform(32, 46)
        zc = shore_z(xc) + d0 + dep / 2
        a = tangent_angle(xc)
        g_ = min(zs(xc - w / 2, zc), zs(xc + w / 2, zc), zs(xc, zc + dep / 2)) - 1.2
        # tall towers are rarer; heights follow a skewed draw (GTA-like waterfront skyline, original massing)
        h = hlo + (hhi - hlo) * (rng.random() ** 2.2)
        fm = FI[rng.choice(FACADE)] if h < 60 else FI[rng.choice(["fachada_cortina", "orla_branco", "orla_azul", "fachada_cortina", "orla_areia"])]
        key = (int((xc - X0) // 1000))
        mbb = sf_cells.setdefault(key, sa_bl.MeshBuilder())
        floors = max(3, int(h // 3.2))
        mbb.box(xc, zc, g_, w, dep, 4.6, FI["vidro_vitrine"], rot=a)                                       # glazed ground floor
        mbb.box(xc, zc, g_ + 4.6, w, dep, h - 4.6, fm, rot=a)
        mbb.box(xc, zc, g_ + h, w + .4, dep + .4, .35, FI["concreto"], rot=a)                              # parapet slab
        if fm != FI["fachada_cortina"]:
            for f in range(1, floors):
                zb = g_ + 4.6 + (f - 1) * 3.2
                if zb > g_ + h - 1:
                    break
                ox = math.sin(a) * (dep / 2 + .6)
                oz = -math.cos(a) * (dep / 2 + .6)
                mbb.box(xc + ox * -1 * -1, zc + oz, zb + 2.6, w * .92, 1.25, .16, FI["concreto"], rot=a)         # balcony slab toward the sea
                mbb.box(xc + ox * -1 * -1, zc + oz - math.cos(a) * .55, zb + 2.7, w * .92, .05, .95, FI["aco_pintado_cinza"], rot=a)
        mbb.box(xc + rng.uniform(-w / 5, w / 5), zc + rng.uniform(-dep / 5, dep / 5), g_ + h + .35, rng.uniform(4, 9), rng.uniform(4, 8),
                rng.uniform(2.2, 4.2), FI["concreto"], rot=a)
        if rng.random() < .55:
            mbb.cylinder(xc + w * .25, zc, g_ + h + .35, 1.7, 3.0, 12, FI["metal_galvanizado"] if "metal_galvanizado" in FI else FI["concreto"])
        n_build += 1
        x += w + rng.uniform(5, 16)
for key, mbb in sf_cells.items():
    o = mbb.to_object(f"Seafront_Orla_{key:02d}", [lib[k] for k in FM], C["04_Seafront"])
    sa_bl.props(o, sa_layer="Architecture", seafront_blockout=True)

# ---------------------------------------------------------------- traffic and people (original generic cars + authored figures)
import sa_vehicles  # noqa: E402
lib.setdefault("borracha_preta", lib["borracha"])
lib.setdefault("plastico_branco", lib["plastico"])

veh_tmp = sa_bl.collection("tmp_orla_vehicles", C["07_Library"], hide_render=True)
VEH_KEYS = [k for k in sa_vehicles.LIBRARY if k[0] in ("hatch", "sedan", "suv", "picape", "van", "hatch_antigo")]
veh_objs = []
for (fam_, pk_, worn_) in VEH_KEYS:
    veh_objs.append(sa_vehicles.build(fam_, lib, veh_tmp, pk_, worn_, lod=1))
vh_c, vh_i = library_of(veh_objs, "LIB_Veiculos_LOD1")
veh_index = {k: vh_i[o.name] for k, o in zip(VEH_KEYS, veh_objs)}
new_keys = [k for k in VEH_KEYS if not k[2] and k[0] not in ("van", "picape")]
old_keys = [k for k in VEH_KEYS if k[2]]
svc_keys = [k for k in VEH_KEYS if k[0] in ("van", "picape")]

veh_pts = []
parked = moving = 0
cw_half = 7.5
x = X0 + 30.0
while x < X1 - 30:
    a = tangent_angle(x)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    zc = shore_z(x) + AVE_DZ
    blocked = abs(x - r03x) < 28 or any(abs(x - s_) < 11 for s_ in streets)
    for side in (1, -1):
        if blocked and rng.random() < .8:
            continue
        for lane_off, kind in ((side * (cw_half - 1.05), "park"), (side * 2.7, "move")):
            if kind == "park" and rng.random() > .46:
                continue
            if kind == "move" and rng.random() > .13:
                continue
            xx = x + nx * lane_off
            zz = zc + ny * lane_off
            heading = a + (math.pi if side == 1 else 0.0) + rng.uniform(-.03, .03) + (rng.uniform(-.05, .05) if kind == "move" else 0.0)
            pool = new_keys if rng.random() < .62 else (old_keys if rng.random() < .55 else svc_keys + new_keys)
            key = rng.choice(pool)
            veh_pts.append((xx, zz, zs(xx, zz) + .14, veh_index[key], heading, 1.0))
            parked += kind == "park"
            moving += kind == "move"
    x += 6.4
for chunk in range(8):
    pts = [p_ for p_ in veh_pts if X0 + chunk * 1000 <= p_[0] < X0 + (chunk + 1) * 1000]
    if pts:
        o = sa_bl.point_cloud_object(f"Vehicles_Orla_{chunk:02d}", pts, vh_c, C["05_Beach_Props"])
        sa_bl.props(o, sa_layer="Props", vehicles_lod="LOD1")

CLOTH = {}


def cloth(rgb):
    k = tuple(round(v, 2) for v in rgb)
    if k not in CLOTH:
        CLOTH[k] = colour("MP_Orla_Roupa_%02d%02d%02d" % tuple(int(v * 99) for v in k), "plastico", c1=rgb, c2=tuple(v * .82 for v in rgb), tint=(0.0, 0.0))
    return CLOTH[k]


def limb(mb_, p0, p1, r0, r1, mat, sy=1.0, segs=8):
    ax = Vector((p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]))
    ax.normalize()
    ref = Vector((0, 1, 0)) if abs(ax.y) < .9 else Vector((1, 0, 0))
    u = ax.cross(ref).normalized()
    w = ax.cross(u).normalized()
    r_a = [(Vector(p0) + u * r0 * math.cos(2 * math.pi * k / segs) + w * r0 * sy * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    r_b = [(Vector(p1) + u * r1 * math.cos(2 * math.pi * k / segs) + w * r1 * sy * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    for k in range(segs):
        k2 = (k + 1) % segs
        mb_.quad(tuple(r_a[k]), tuple(r_a[k2]), tuple(r_b[k2]), tuple(r_b[k]), mat)
    mb_.add_face([tuple(v) for v in reversed(r_a)], mat)
    mb_.add_face([tuple(v) for v in r_b], mat)


def head_mesh(mb_, c, rr, mat, sx=1.0, sy=1.0, sz=1.0, rings=6, segs=10):
    prev = None
    for i in range(rings + 1):
        th = math.pi * i / rings
        ring = [(c[0] + rr * sx * math.sin(th) * math.cos(2 * math.pi * s / segs), c[1] + rr * sy * math.sin(th) * math.sin(2 * math.pi * s / segs),
                 c[2] + rr * sz * math.cos(th)) for s in range(segs)]
        if prev:
            for s in range(segs):
                s2 = (s + 1) % segs
                mb_.quad(prev[s], prev[s2], ring[s2], ring[s], mat)
        prev = ring


def person(name, skin, shirt, pants, hair, stride, mode="walk", dress=False, tall=1.0):
    mb_ = sa_bl.MeshBuilder()
    sw = stride
    for s_ in (-1, 1):
        fx = s_ * sw
        if dress:
            limb(mb_, (fx * .6, s_ * .075, .05), (0, s_ * .075, .55), .045, .06, 0)
        else:
            limb(mb_, (fx, s_ * .085, .09), (0, s_ * .085, .93), .052, .085, 2)
        mb_.box(fx + .05, s_ * .085, .0, .26, .10, .09, 4)                    # shoes
    if dress:
        limb(mb_, (0, 0, .50), (0, 0, 1.0), .24, .17, 1)
    limb(mb_, (0, 0, .90), (0, 0, 1.48), .165, .19, 1, sy=1.28)
    limb(mb_, (0, 0, 1.46), (0, 0, 1.60), .052, .048, 0)
    head_mesh(mb_, (.01, 0, 1.69), .105, 0, sx=1.0, sy=.92, sz=1.12)
    head_mesh(mb_, (-.015, 0, 1.725), .112, 3, sx=1.02, sy=.98, sz=.98, rings=5)
    for s_ in (-1, 1):                                                         # arms swing against the legs
        sx_ = -s_ * sw * .8
        limb(mb_, (0, s_ * .215, 1.43), (sx_ * .6, s_ * .245, 1.16), .045, .04, 1)
        limb(mb_, (sx_ * .6, s_ * .245, 1.16), (sx_, s_ * .25, .90), .036, .03, 0)
    if tall != 1.0:
        mb_.verts = [(v[0], v[1], v[2] * tall) for v in mb_.verts]
    if mode == "lie":
        mb_.verts = [(v[2] - .85, v[1], .08 + v[0] * .9) for v in mb_.verts]
    return lib_obj(name, mb_, [cloth(skin), cloth(shirt), cloth(pants), cloth(hair), cloth((.12, .12, .13))])


SKIN = [(.52, .34, .24), (.40, .26, .18), (.62, .45, .33), (.25, .16, .11), (.70, .52, .40)]
SHIRT = [(.78, .78, .74), (.14, .30, .55), (.70, .18, .14), (.18, .45, .30), (.92, .72, .15), (.08, .08, .10), (.62, .22, .46), (.88, .45, .15)]
PANTS = [(.12, .16, .26), (.18, .18, .20), (.60, .52, .38), (.10, .30, .32)]
HAIR = [(.04, .03, .03), (.18, .11, .06), (.45, .30, .14), (.62, .60, .58)]
walkers, lyers, swimmers = [], [], []
for i in range(10):
    walkers.append(person(f"LIB_Pedestre_{i:02d}", SKIN[i % 5], SHIRT[(i * 3) % 8], PANTS[i % 4], HAIR[(i * 2) % 4], .11 if i % 2 else .07,
                          dress=(i % 5 == 3), tall=.94 + (i % 4) * .035))
for i in range(5):
    lyers.append(person(f"LIB_Banhista_{i:02d}", SKIN[(i + 1) % 5], SHIRT[(i * 3 + 1) % 8], (.12, .22, .45) if i % 2 else (.8, .25, .2), HAIR[i % 4], .04, mode="lie",
                        tall=.95 + (i % 3) * .04))
for i in range(4):
    swimmers.append(person(f"LIB_Nadador_{i:02d}", SKIN[(i + 2) % 5], (.10, .25, .50) if i % 2 else (.80, .30, .25), (.10, .25, .50), HAIR[i % 4], .05))
wk_c, wk_i = library_of(walkers, "LIB_Pedestres")
ly_c, ly_i = library_of(lyers, "LIB_Banhistas")
sw_c, sw_i = library_of(swimmers, "LIB_Nadadores")

ped_pts, lie_pts, swim_pts = [], [], []
x = X0 + 10.0
while x < X1 - 10:
    for dz_ in (PROM_DZ + rng.uniform(-5.0, 5.0), AVE_DZ + (rng.choice((-1, 1)) * 9.6)):
        if rng.random() < (.55 if dz_ < AVE_DZ - 20 else .22):
            xx = x + rng.uniform(-3, 3)
            zz = shore_z(xx) + dz_
            heading = tangent_angle(xx) + (0 if rng.random() < .5 else math.pi) + rng.uniform(-.12, .12)
            ped_pts.append((xx, zz, zs(xx, zz) + .15, rng.randrange(len(walkers)), heading, rng.uniform(.96, 1.04)))
    x += 9.0
for (px_u, pz_u, ph_u, pv_u, pr_u, ps_u) in um_pts:                      # sunbathers by the umbrellas, some people standing
    for k in range(rng.choice((0, 1, 1, 2))):
        a_ = rng.uniform(0, 6.28)
        xx, zz = px_u + math.cos(a_) * 1.9, pz_u + math.sin(a_) * 1.9
        lie_pts.append((xx, zz, ground(xx, zz), rng.randrange(len(lyers)), a_ + math.pi / 2, 1.0))
    if rng.random() < .30:
        a_ = rng.uniform(0, 6.28)
        xx, zz = px_u + math.cos(a_) * 2.6, pz_u + math.sin(a_) * 2.6
        ped_pts.append((xx, zz, ground(xx, zz), rng.randrange(len(walkers)), rng.uniform(0, 6.28), 1.0))
for cx_, dens in centres:
    for _ in range(int(55 * dens)):
        xx = cx_ + rng.gauss(0, 140 * dens)
        zz = shore_z(xx) - rng.uniform(8, 42)
        swim_pts.append((xx, zz, -1.28, rng.randrange(len(swimmers)), rng.uniform(0, 6.28), 1.0))
    for _ in range(int(40 * dens)):                                         # wading and strolling in the swash zone
        xx = cx_ + rng.gauss(0, 130 * dens)
        zz = shore_z(xx) + rng.uniform(-1.5, 12.0)
        ped_pts.append((xx, zz, ground(xx, zz), rng.randrange(len(walkers)), tangent_angle(xx) + rng.choice((0, math.pi)), 1.0))
for chunk in range(8):
    for nm, src, cc in (("Pedestrians", ped_pts, wk_c), ("Sunbathers", lie_pts, ly_c), ("Swimmers", swim_pts, sw_c)):
        pts = [p_ for p_ in src if X0 + chunk * 1000 <= p_[0] < X0 + (chunk + 1) * 1000]
        if pts:
            o = sa_bl.point_cloud_object(f"{nm}_Orla_{chunk:02d}", pts, cc, C["05_Beach_Props"])
            sa_bl.props(o, sa_layer="Props", life=nm.lower())

# ---------------------------------------------------------------- night lighting (off for daytime renders: collection hidden in render)
night = sa_bl.collection("09_Night_Lights", hide_render=True)
night.hide_viewport = True
n_night = 0
for k, (lx_, lz_, lzz_, _, _, _) in enumerate(lamp_pts):
    ld = bpy.data.lights.new(f"Night_Poste_{k:04d}", "SPOT")
    ld.energy = 1800.0
    ld.spot_size = math.radians(115)
    ld.spot_blend = .6
    ld.color = (1.0, .78, .5)
    ld.shadow_soft_size = .15
    ld.use_shadow = False
    lo_ = bpy.data.objects.new(ld.name, ld)
    night.objects.link(lo_)
    lo_.location = (lx_, lz_, lzz_ + 7.0)
    n_night += 1
for k, (lx_, lz_, lzz_, _, _, _) in enumerate(pier_lamps):
    ld = bpy.data.lights.new(f"Night_Pier_{k:03d}", "SPOT")
    ld.energy = 900.0
    ld.spot_size = math.radians(110)
    ld.spot_blend = .6
    ld.color = (1.0, .8, .55)
    ld.use_shadow = False
    lo_ = bpy.data.objects.new(ld.name, ld)
    night.objects.link(lo_)
    lo_.location = (lx_, lz_, lzz_ + 4.2)
    n_night += 1
moon = bpy.data.lights.new("Night_Moon", "SUN")
moon.energy = 0.12
moon.color = (.62, .72, 1.0)
mo_ = bpy.data.objects.new("Night_Moon", moon)
night.objects.link(mo_)
mo_.rotation_euler = (math.radians(55), 0, math.radians(200))

# ---------------------------------------------------------------- cameras, sun, save
cams = C["08_Cameras"]
px_ = float(coast["piers"][0]["x"])
sa_bl.camera("CAM_Orla_Aerea", cams, (-900, -4420, 230), target=(100, -3720, 8), lens=30, clip=(1, 30000))
sa_bl.camera("CAM_Orla_Praia", cams, (-380, shore_z(-380) + 38, ground(-380, shore_z(-380) + 38) + 1.65), target=(60, shore_z(60) + 70, 7), lens=22, clip=(.3, 30000))
sa_bl.camera("CAM_Orla_Pier", cams, (px_, shore_z(px_) - 40, 6.5), target=(px_, shore_z(px_) + 420, 22), lens=26, clip=(.3, 30000))
sa_bl.camera("CAM_Orla_Farol", cams, (1050, -4140, 22), target=(lx, lz, 28), lens=34, clip=(1, 30000))
sa_bl.camera("CAM_Orla_Calcadao", cams, (-1210, shore_z(-1210) + PROM_DZ - 1, zs(-1210, shore_z(-1210) + PROM_DZ - 1) + 1.7),
             target=(-880, shore_z(-880) + PROM_DZ + 2, 5), lens=24, clip=(.3, 30000))
sa_bl.camera("CAM_Orla_Avenida", cams, (-880, shore_z(-880) + AVE_DZ - 2.7, zs(-880, shore_z(-880) + AVE_DZ - 2.7) + 2.0),
             target=(-560, shore_z(-560) + AVE_DZ - 3.0, 4.5), lens=26, clip=(.3, 30000))
sa_bl.camera("CAM_Orla_Mar_Alto", cams, (700, -4900, 520), target=(-200, -3500, 0), lens=26, clip=(1, 40000))
sa_bl.production_look(scene, cams, elevation_deg=27.0, azimuth_deg=300.0)
scene.camera = bpy.data.objects["CAM_Orla_Aerea"]
scene.render.engine = "BLENDER_EEVEE"
scene["facility_revision"] = "W4"
scene["facility_coast"] = coast["id"]
output = out_dir / "SantaAurora_Orla_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
rep = {"blend": output.relative_to(root).as_posix(), "blenderVersion": bpy.app.version_string, "terrainVertices": tcount,
       "objectCount": len(bpy.data.objects), "palms": len(palm_pts), "dune_grass": len(grass_pts), "umbrellas": len(um_pts), "loungers": len(lo_pts),
       "lifeguardTowers": n_tower, "kiosks": n_kiosk, "seafrontBuildings": n_build, "piers": [p["id"] for p in coast["piers"]],
       "lamps": len(lamp_pts), "benches": len(bench_pts), "rocks": len(rock_pts), "boats": len(boat_pts), "nightLights": n_night, "vehicles": len(veh_pts), "parkedCars": parked, "movingCars": moving, "pedestrians": len(ped_pts), "sunbathers": len(lie_pts), "swimmers": len(swim_pts), "status": "W4 coast - first production pass"}
(out_dir / "orla_generation_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("ORLA GENERATED", json.dumps(rep))
