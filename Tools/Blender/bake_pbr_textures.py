"""W3 — authored, tileable PBR texture library for Santa Aurora (procedural source, baked with Cycles).

Run:
blender --background --factory-startup --python Tools/Blender/bake_pbr_textures.py -- --root PROJECT_ROOT [--res 1024] [--only a,b]

Every set is authored here (own procedural graphs, no external images): seamless by construction (4D periodic noise/voronoi on a
torus mapping of the tile UV; brick/tile counts are integers per tile). Output per set:
ArtSource/Textures/<set>/<set>_BaseColor.jpg (sRGB), _Normal.jpg (OpenGL tangent), _Roughness.jpg, _AO.jpg, _Height.jpg, _Metallic.jpg
(metals only) + ArtSource/Textures/texture_library_w3.json (tile size in metres, provenance = own procedural, license = project-owned).
Base colours are authored neutral/light where a set is tinted per material (reboco, aço pintado, madeira).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--res", type=int, default=1024)
parser.add_argument("--only", default="")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
OUT = root / "ArtSource" / "Textures"
TAU = 2 * math.pi


class G:
    """Tiny node-graph helper bound to one material."""

    def __init__(self, mat):
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.L = self.nt.links
        self.x = -2000
        tc = self.node("ShaderNodeTexCoord")
        self.uv = tc.outputs["UV"]
        sep = self.node("ShaderNodeSeparateXYZ")
        self.link(self.uv, sep.inputs[0])
        self.u, self.v = sep.outputs[0], sep.outputs[1]
        self.per = {}

    def node(self, kind, **inputs):
        n = self.nt.nodes.new(kind)
        n.location = (self.x, len(self.nt.nodes) * -40 % 1600)
        self.x += 15
        for k, val in inputs.items():
            n.inputs[k].default_value = val
        return n

    def link(self, a, b):
        self.L.new(a, b)

    def math(self, op, a, b=0.0, c=None):
        n = self.node("ShaderNodeMath")
        n.operation = op
        for i, val in enumerate((a, b) if c is None else (a, b, c)):
            if isinstance(val, (int, float)):
                n.inputs[i].default_value = val
            else:
                self.link(val, n.inputs[i])
        return n.outputs[0]

    def periodic(self, ru=1.0, rv=1.0):
        """(vector, w) on a torus: seamless in u and v. ru/rv stretch features (anisotropy)."""
        key = (ru, rv)
        if key in self.per:
            return self.per[key]
        cu = self.math("COSINE", self.math("MULTIPLY", self.u, TAU))
        su = self.math("SINE", self.math("MULTIPLY", self.u, TAU))
        cv = self.math("COSINE", self.math("MULTIPLY", self.v, TAU))
        sv = self.math("SINE", self.math("MULTIPLY", self.v, TAU))
        comb = self.node("ShaderNodeCombineXYZ")
        self.link(self.math("MULTIPLY", cu, ru), comb.inputs[0])
        self.link(self.math("MULTIPLY", su, ru), comb.inputs[1])
        self.link(self.math("MULTIPLY", cv, rv), comb.inputs[2])
        self.per[key] = (comb.outputs[0], self.math("MULTIPLY", sv, rv))
        return self.per[key]

    def noise(self, freq, detail=4.0, rough=.55, ru=1.0, rv=1.0, distortion=0.0, offset=0.0):
        vec, w = self.periodic(ru, rv)
        n = self.node("ShaderNodeTexNoise", Scale=freq / TAU, Detail=detail, Roughness=rough, Distortion=distortion)
        n.noise_dimensions = "4D"
        self.link(vec, n.inputs["Vector"])
        self.link(self.math("ADD", w, offset * 10.0), n.inputs["W"])
        return n.outputs["Fac"]

    def voronoi(self, freq, feature="F1", out="Distance", ru=1.0, rv=1.0, rand=1.0):
        vec, w = self.periodic(ru, rv)
        n = self.node("ShaderNodeTexVoronoi", Scale=freq / TAU, Randomness=rand)
        n.voronoi_dimensions = "4D"
        n.feature = feature
        self.link(vec, n.inputs["Vector"])
        self.link(w, n.inputs["W"])
        return n.outputs[out]

    def ramp(self, fac, a, b):
        m = self.node("ShaderNodeMix")
        m.data_type = "RGBA"
        self.link(fac, m.inputs["Factor"])
        m.inputs[6].default_value = (*a, 1)
        m.inputs[7].default_value = (*b, 1)
        return m.outputs[2]

    def mixc(self, fac, c1, c2):
        m = self.node("ShaderNodeMix")
        m.data_type = "RGBA"
        self.link(fac, m.inputs["Factor"]) if not isinstance(fac, float) else None
        if isinstance(fac, float):
            m.inputs["Factor"].default_value = fac
        for i, c in ((6, c1), (7, c2)):
            if isinstance(c, tuple):
                m.inputs[i].default_value = (*c, 1)
            else:
                self.link(c, m.inputs[i])
        return m.outputs[2]

    def mr(self, val, a, b, c=0.0, d=1.0):
        n = self.node("ShaderNodeMapRange", **{"From Min": a, "From Max": b, "To Min": c, "To Max": d})
        self.link(val, n.inputs["Value"])
        return n.outputs["Result"]

    def bricks(self, cols, rows, mortar, offset=.5, bevel=.1):
        """Brick/tile grid with integer cols x rows per tile (seamless). Returns (mortar mask 1=joint, per-brick random)."""
        vec = self.node("ShaderNodeCombineXYZ")
        self.link(self.math("MULTIPLY", self.u, float(cols)), vec.inputs[0])
        self.link(self.math("MULTIPLY", self.v, float(rows)), vec.inputs[1])
        b = self.node("ShaderNodeTexBrick", Scale=1.0, **{"Mortar Size": mortar, "Mortar Smooth": bevel, "Brick Width": 1.0, "Row Height": 1.0, "Bias": 0.0})
        b.offset = offset
        b.offset_frequency = 2
        b.squash = 1.0
        b.squash_frequency = 1
        b.inputs["Color1"].default_value = (0, 0, 0, 1)
        b.inputs["Color2"].default_value = (1, 1, 1, 1)
        self.link(vec.outputs[0], b.inputs["Vector"])
        sep = self.node("ShaderNodeSeparateColor")
        self.link(b.outputs["Color"], sep.inputs[0])
        return b.outputs["Fac"], sep.outputs[0]


# ---------------------------------------------------------------- texture set definitions
# Each returns dict(color, rough, height, metal) sockets/values. Heights are 0..1 (0.5 = surface).

def s_reboco(g):
    big = g.noise(3, 3)
    fine = g.noise(40, 6, .6)
    trowel = g.noise(8, 2, .4, ru=1.0, rv=.35, distortion=1.5)
    crack = g.mr(g.voronoi(4, "DISTANCE_TO_EDGE", "Distance"), 0.0, .006, 1.0, 0.0)
    crack = g.math("MULTIPLY", crack, g.mr(g.noise(2, 2), .6, .68))
    patch = g.mr(g.noise(2.2, 2, offset=3), .6, .63)
    mid = g.noise(11, 4, .6, offset=15)
    col = g.ramp(g.mr(g.math("ADD", g.math("ADD", g.math("MULTIPLY", big, .45), g.math("MULTIPLY", mid, .35)), g.math("MULTIPLY", fine, .2)), .32, .68),
                 (.70, .68, .63), (.95, .94, .90))
    col = g.mixc(patch, col, (.86, .85, .80))
    col = g.mixc(g.math("MULTIPLY", crack, .8), col, (.35, .33, .30))
    h = g.math("ADD", g.math("MULTIPLY", fine, .35), g.math("MULTIPLY", trowel, .35))
    h = g.math("SUBTRACT", h, g.math("MULTIPLY", crack, .5))
    rough = g.mr(fine, .3, .7, .78, .95)
    return dict(color=col, rough=rough, height=h, metal=0.0)


def s_concreto(g):
    big = g.noise(2.5, 3)
    fine = g.noise(60, 6, .65)
    pores = g.mr(g.voronoi(55, "F1", "Distance", rand=1.0), 0.0, .1, 1.0, 0.0)
    pores = g.math("MULTIPLY", pores, g.mr(g.noise(9, 2, offset=1), .45, .7))
    stain = g.mr(g.noise(1.5, 3, offset=5), .5, .8)
    mid = g.noise(12, 4, .6, offset=16)
    col = g.ramp(g.mr(g.math("ADD", g.math("ADD", g.math("MULTIPLY", big, .4), g.math("MULTIPLY", mid, .35)), g.math("MULTIPLY", fine, .25)), .32, .68),
                 (.40, .39, .37), (.68, .67, .64))
    col = g.mixc(g.math("MULTIPLY", stain, .45), col, (.33, .32, .30))
    col = g.mixc(g.math("MULTIPLY", pores, .9), col, (.22, .21, .20))
    h = g.math("SUBTRACT", g.math("MULTIPLY", fine, .5), g.math("MULTIPLY", pores, .4))
    return dict(color=col, rough=g.mr(fine, .3, .7, .82, .97), height=h, metal=0.0)


def s_tijolo(g):
    mortar, rnd = g.bricks(5, 16, .028, .5, .25)
    fine = g.noise(70, 5, .6)
    burn = g.mr(g.noise(14, 2, offset=2), .35, .7)
    chip = g.math("MULTIPLY", g.mr(g.noise(30, 6, .7, offset=13), .62, .68), .8)
    soot = g.mr(g.noise(2.5, 3, offset=14), .5, .8)
    col = g.ramp(g.mr(rnd, 0.0, 1.0), (.36, .14, .08), (.60, .30, .17))
    col = g.mixc(g.math("MULTIPLY", burn, .55), col, (.24, .10, .06))
    col = g.mixc(g.math("MULTIPLY", fine, .3), col, (.66, .42, .30))
    col = g.mixc(chip, col, (.72, .52, .40))
    col = g.mixc(mortar, col, (.46, .44, .40))
    col = g.mixc(g.math("MULTIPLY", soot, .35), col, (.16, .12, .10))
    h = g.math("SUBTRACT", g.math("ADD", .65, g.math("MULTIPLY", fine, .15)), g.math("MULTIPLY", mortar, .55))
    return dict(color=col, rough=g.mixc(mortar, (.8, .8, .8), (.95, .95, .95)), height=h, metal=0.0)


def s_asfalto(g):
    agg = g.mr(g.voronoi(140, "F1", "Distance"), 0.0, .35, 1.0, 0.0)
    fine = g.noise(90, 6, .7)
    big = g.noise(2.0, 3)
    crack = g.math("MULTIPLY", g.mr(g.voronoi(1.6, "DISTANCE_TO_EDGE", "Distance"), 0.0, .006, 1.0, 0.0), g.mr(g.noise(3, 2, offset=4), .55, .65))
    col = g.ramp(g.mr(g.math("ADD", g.math("MULTIPLY", fine, .6), g.math("MULTIPLY", big, .4)), .3, .75), (.07, .07, .075), (.16, .16, .165))
    col = g.mixc(g.math("MULTIPLY", agg, .35), col, (.30, .29, .28))
    col = g.mixc(crack, col, (.02, .02, .02))
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", agg, .3), g.math("MULTIPLY", fine, .3)), g.math("MULTIPLY", crack, .5))
    return dict(color=col, rough=g.mr(agg, 0, 1, .92, .78), height=h, metal=0.0)


def s_pedra_portuguesa(g):
    cell = g.voronoi(26, "F1", "Distance", rand=.85)
    edge = g.mr(g.voronoi(26, "DISTANCE_TO_EDGE", "Distance", rand=.85), 0.0, .06, 1.0, 0.0)
    rndc = g.voronoi(26, "F1", "Color", rand=.85)
    sep = g.node("ShaderNodeSeparateColor")
    g.link(rndc, sep.inputs[0])
    band = g.math("SINE", g.math("ADD", g.math("MULTIPLY", g.v, TAU * 2), g.math("MULTIPLY", g.math("SINE", g.math("MULTIPLY", g.u, TAU * 2)), 1.6)))
    wave = g.mr(band, .55, .62)                                        # black wave bands on white limestone (calçadão)
    stone = g.mixc(wave, (.80, .78, .73), (.10, .10, .10))
    stone = g.mixc(g.math("MULTIPLY", g.mr(sep.outputs[0], 0, 1), .22), stone, (.62, .60, .56))
    col = g.mixc(edge, stone, (.30, .28, .25))
    h = g.math("SUBTRACT", g.mr(cell, 0.0, .5, .8, .45), g.math("MULTIPLY", edge, .4))
    return dict(color=col, rough=g.mr(edge, 0, 1, .55, .9), height=h, metal=0.0)


def s_intertravado(g):
    joint, rnd = g.bricks(6, 12, .05, .5, .2)
    fine = g.noise(60, 4, .6)
    col = g.ramp(g.mr(rnd, 0, 1), (.42, .38, .35), (.55, .50, .46))
    col = g.mixc(g.math("MULTIPLY", fine, .3), col, (.30, .28, .26))
    col = g.mixc(joint, col, (.22, .21, .19))
    h = g.math("SUBTRACT", g.math("ADD", .7, g.math("MULTIPLY", fine, .1)), g.math("MULTIPLY", joint, .6))
    return dict(color=col, rough=.9, height=h, metal=0.0)


def s_ladrilho(g):
    joint, rnd = g.bricks(3, 3, .02, 0.0, .1)
    fine = g.noise(50, 4, .6)
    # hydraulic tile relief: 4 diagonal grooves per tile (common Brazilian sidewalk)
    gu = g.math("FRACT", g.math("MULTIPLY", g.math("ADD", g.u, g.v), 12.0))
    groove = g.mr(g.math("ABSOLUTE", g.math("SUBTRACT", gu, .5)), .38, .5)
    col = g.ramp(g.mr(rnd, 0, 1), (.52, .50, .47), (.60, .58, .55))
    col = g.mixc(g.math("MULTIPLY", fine, .25), col, (.40, .38, .35))
    col = g.mixc(joint, col, (.28, .27, .25))
    h = g.math("SUBTRACT", g.math("SUBTRACT", .7, g.math("MULTIPLY", groove, .2)), g.math("MULTIPLY", joint, .5))
    return dict(color=col, rough=.85, height=h, metal=0.0)


def s_meio_fio(g):
    big = g.noise(4, 3)
    fine = g.noise(70, 6, .65)
    joint = g.mr(g.math("ABSOLUTE", g.math("SUBTRACT", g.math("FRACT", g.u), .5)), .49, .5)
    col = g.ramp(g.mr(g.math("ADD", big, fine), .6, 1.4), (.55, .54, .51), (.72, .71, .68))
    col = g.mixc(joint, col, (.25, .24, .22))
    return dict(color=col, rough=g.mr(fine, .3, .7, .8, .95), height=g.math("SUBTRACT", g.math("MULTIPLY", fine, .5), g.math("MULTIPLY", joint, .4)), metal=0.0)


def s_aco_pintado(g):
    fine = g.noise(30, 4, .5)
    chips = g.mr(g.noise(9, 8, .7, offset=6), .61, .64)
    scratches = g.math("MULTIPLY", g.mr(g.noise(3, 2, .3, ru=1.0, rv=.06, distortion=2.0), .62, .64), .8)
    rust = g.math("MULTIPLY", chips, g.mr(g.noise(4, 3, offset=7), .45, .6))
    col = g.ramp(g.mr(fine, .3, .7), (.86, .86, .84), (.93, .93, .91))
    col = g.mixc(chips, col, (.45, .45, .44))                         # primer / bare
    col = g.mixc(rust, col, (.36, .17, .08))
    col = g.mixc(scratches, col, (.62, .62, .62))
    metal = g.math("MULTIPLY", g.math("SUBTRACT", g.math("MAXIMUM", chips, scratches), rust), 1.0)
    h = g.math("SUBTRACT", .6, g.math("MULTIPLY", chips, .25))
    return dict(color=col, rough=g.mr(g.math("MAXIMUM", chips, rust), 0, 1, .38, .75), height=h, metal=metal)


def s_galvanizado(g):
    sp = g.voronoi(14, "F1", "Color", rand=1.0)
    sep = g.node("ShaderNodeSeparateColor")
    g.link(sp, sep.inputs[0])
    fine = g.noise(80, 5, .6)
    white = g.mr(g.noise(2, 3, offset=8), .55, .8)
    col = g.ramp(g.mr(sep.outputs[0], 0, 1), (.55, .56, .57), (.76, .77, .78))
    col = g.mixc(g.math("MULTIPLY", white, .5), col, (.80, .80, .78))                 # white rust bloom
    return dict(color=col, rough=g.mr(sep.outputs[1], 0, 1, .3, .55), height=g.math("MULTIPLY", fine, .4), metal=g.mr(white, 0, 1, 1.0, .6))


def s_ferrugem(g):
    fine = g.noise(40, 8, .7)
    flakes = g.mr(g.voronoi(18, "F1", "Distance"), 0, .4, 1.0, 0.0)
    big = g.noise(3, 3)
    col = g.ramp(g.mr(g.math("ADD", big, fine), .6, 1.4), (.22, .09, .04), (.52, .26, .10))
    col = g.mixc(g.math("MULTIPLY", flakes, .4), col, (.62, .36, .16))
    return dict(color=col, rough=g.mr(fine, .3, .7, .8, .97), height=g.math("ADD", g.math("MULTIPLY", fine, .4), g.math("MULTIPLY", flakes, .3)), metal=.15)


def s_madeira(g):
    grain = g.noise(18, 6, .55, ru=1.0, rv=.08, distortion=2.5)
    rings = g.math("FRACT", g.math("MULTIPLY", grain, 7.0))
    seams = g.mr(g.math("ABSOLUTE", g.math("SUBTRACT", g.math("FRACT", g.math("MULTIPLY", g.u, 5.0)), .5)), .48, .5)
    knots = g.mr(g.voronoi(6, "F1", "Distance", ru=1.0, rv=.3), 0, .04, 1.0, 0.0)
    col = g.ramp(g.mr(rings, 0, 1), (.62, .45, .30), (.78, .60, .42))
    col = g.mixc(knots, col, (.32, .20, .12))
    col = g.mixc(seams, col, (.20, .13, .08))
    return dict(color=col, rough=g.mr(rings, 0, 1, .55, .75), height=g.math("SUBTRACT", g.math("MULTIPLY", rings, .2), g.math("MULTIPLY", seams, .5)), metal=0.0)


def s_ceramica(g):
    joint, rnd = g.bricks(4, 4, .015, 0.0, .1)
    fine = g.noise(40, 3, .5)
    col = g.ramp(g.mr(rnd, 0, 1), (.82, .80, .76), (.90, .88, .84))
    col = g.mixc(g.math("MULTIPLY", fine, .15), col, (.70, .68, .64))
    col = g.mixc(joint, col, (.45, .43, .40))
    return dict(color=col, rough=g.mixc(joint, (.12, .12, .12), (.8, .8, .8)), height=g.math("SUBTRACT", .7, g.math("MULTIPLY", joint, .5)), metal=0.0)


def s_telha(g):
    joint, rnd = g.bricks(4, 6, .03, .5, .4)
    curve = g.math("SINE", g.math("MULTIPLY", g.u, TAU * 4))                       # colonial tile curvature
    moss = g.math("MULTIPLY", g.mr(g.noise(6, 4, offset=9), .55, .75), joint)
    fine = g.noise(50, 5, .6)
    col = g.ramp(g.mr(rnd, 0, 1), (.48, .20, .11), (.66, .32, .18))
    col = g.mixc(g.math("MULTIPLY", fine, .3), col, (.35, .15, .09))
    col = g.mixc(moss, col, (.20, .24, .10))
    col = g.mixc(g.mr(curve, -1, 1, .35, 0.0), col, (.22, .09, .05))
    h = g.math("SUBTRACT", g.math("ADD", .55, g.math("MULTIPLY", curve, .25)), g.math("MULTIPLY", joint, .4))
    return dict(color=col, rough=.85, height=h, metal=0.0)


def s_plastico(g):
    fine = g.noise(80, 3, .4)
    scr = g.mr(g.noise(5, 2, .3, ru=1.0, rv=.05, distortion=2), .62, .64)
    col = g.ramp(g.mr(fine, .3, .7), (.88, .88, .86), (.95, .95, .93))
    col = g.mixc(g.math("MULTIPLY", scr, .4), col, (.75, .75, .73))
    return dict(color=col, rough=g.mr(scr, 0, 1, .35, .55), height=g.math("MULTIPLY", fine, .2), metal=0.0)


def s_borracha(g):
    fine = g.noise(90, 5, .6)
    return dict(color=g.ramp(fine, (.035, .035, .035), (.07, .07, .07)), rough=g.mr(fine, 0, 1, .85, .97), height=g.math("MULTIPLY", fine, .3), metal=0.0)


def s_grama(g):
    blades = g.noise(60, 6, .7, ru=1.0, rv=.4)
    clump = g.noise(4, 3)
    dry = g.mr(g.noise(2.5, 3, offset=10), .55, .75)
    col = g.ramp(g.mr(g.math("ADD", blades, clump), .6, 1.4), (.10, .16, .05), (.24, .34, .10))
    col = g.mixc(g.math("MULTIPLY", dry, .7), col, (.40, .36, .18))
    return dict(color=col, rough=.9, height=g.math("MULTIPLY", blades, .6), metal=0.0)


def s_terra(g):
    fine = g.noise(50, 6, .65)
    pebbles = g.mr(g.voronoi(30, "F1", "Distance"), 0, .15, 1.0, 0.0)
    pebbles = g.math("MULTIPLY", pebbles, g.mr(g.noise(5, 2, offset=11), .5, .65))
    wet = g.mr(g.noise(2, 3, offset=12), .55, .8)
    col = g.ramp(g.mr(fine, .3, .7), (.30, .22, .15), (.45, .35, .24))
    col = g.mixc(g.math("MULTIPLY", wet, .5), col, (.20, .15, .10))
    col = g.mixc(pebbles, col, (.55, .50, .44))
    return dict(color=col, rough=g.mr(wet, 0, 1, .95, .75), height=g.math("ADD", g.math("MULTIPLY", fine, .4), g.math("MULTIPLY", pebbles, .3)), metal=0.0)


def s_cascalho(g):
    edge = g.voronoi(34, "DISTANCE_TO_EDGE", "Distance", rand=1.0)
    c = g.voronoi(34, "F1", "Color", rand=1.0)
    sep = g.node("ShaderNodeSeparateColor")
    g.link(c, sep.inputs[0])
    gap = g.mr(edge, 0.0, .08, 1.0, 0.0)
    col = g.ramp(g.mr(sep.outputs[0], 0, 1), (.34, .32, .29), (.66, .63, .58))
    col = g.mixc(g.math("MULTIPLY", g.mr(sep.outputs[1], 0, 1), .4), col, (.48, .40, .32))
    col = g.mixc(gap, col, (.12, .11, .10))
    return dict(color=col, rough=.9, height=g.mr(edge, 0, .25, .2, .9), metal=0.0)


def s_pastilha(g):
    joint, rnd = g.bricks(12, 12, .08, 0.0, .1)
    col = g.ramp(g.mr(rnd, 0, 1), (.80, .80, .78), (.90, .90, .88))
    col = g.mixc(joint, col, (.55, .54, .50))
    return dict(color=col, rough=g.mixc(joint, (.2, .2, .2), (.85, .85, .85)), height=g.math("SUBTRACT", .7, g.math("MULTIPLY", joint, .5)), metal=0.0)


def s_granito(g):
    a = g.mr(g.voronoi(90, "F1", "Distance"), 0, .2, 1, 0)
    b = g.noise(120, 2, .5)
    col = g.ramp(b, (.18, .17, .16), (.40, .38, .36))
    col = g.mixc(g.math("MULTIPLY", a, .6), col, (.75, .74, .72))
    return dict(color=col, rough=g.mr(b, 0, 1, .2, .4), height=g.math("MULTIPLY", b, .2), metal=0.0)


SETS = {  # name: (builder, tile size m, description)
    "reboco": (s_reboco, 2.0, "reboco de cal/cimento com marcas de desempenadeira, trincas e remendos (base neutra, tingida por material)"),
    "concreto": (s_concreto, 2.0, "concreto com poros de forma, manchas e variação"),
    "tijolo": (s_tijolo, 1.2, "tijolo maciço 24x7,5 cm, juntas de argamassa, queima variável"),
    "asfalto": (s_asfalto, 4.0, "asfalto com agregado, trincas finas"),
    "pedra_portuguesa": (s_pedra_portuguesa, 2.0, "mosaico de pedra portuguesa preto/branco em ondas"),
    "intertravado": (s_intertravado, 1.2, "bloco intertravado 20x10 cm em amarração"),
    "ladrilho": (s_ladrilho, 1.2, "ladrilho hidráulico 40x40 de calçada com sulcos"),
    "meio_fio": (s_meio_fio, 1.0, "meio-fio de concreto pré-moldado com juntas a cada 1 m"),
    "aco_pintado": (s_aco_pintado, 1.0, "aço pintado com lascas, primer exposto, arranhões e ferrugem (base clara, tingida)"),
    "galvanizado": (s_galvanizado, 1.0, "aço galvanizado com cristais (spangle) e oxidação branca"),
    "ferrugem": (s_ferrugem, 1.0, "ferrugem com escamas"),
    "madeira": (s_madeira, 1.0, "tábuas com veios, nós e frestas (base clara, tingida)"),
    "ceramica": (s_ceramica, 1.2, "piso cerâmico esmaltado 30x30 com rejunte"),
    "telha": (s_telha, 1.2, "telha cerâmica colonial com musgo nas juntas"),
    "plastico": (s_plastico, .5, "plástico com riscos"),
    "borracha": (s_borracha, .5, "borracha"),
    "grama": (s_grama, 2.0, "gramado urbano com falhas secas"),
    "terra": (s_terra, 2.0, "solo exposto com seixos e umidade"),
    "cascalho": (s_cascalho, 1.0, "cascalho/brita"),
    "pastilha": (s_pastilha, .6, "pastilha cerâmica 5x5 cm"),
    "granito": (s_granito, 1.0, "granito polido salpicado"),
}


def bake_set(name, builder, res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.bake.margin = 0
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 90
    scene.render.image_settings.color_mode = "RGB"
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    ob = bpy.context.active_object
    ob.data.uv_layers[0].name = "UVMap"
    mat = bpy.data.materials.new(name)
    ob.data.materials.append(mat)
    g = G(mat)
    sock = builder(g)
    out = g.node("ShaderNodeOutputMaterial")
    emit = g.node("ShaderNodeEmission")
    g.link(emit.outputs[0], out.inputs["Surface"])
    bsdf = g.node("ShaderNodeBsdfPrincipled")
    bump = g.node("ShaderNodeBump", Strength=1.0, Distance=.02)

    def as_socket(val):
        if isinstance(val, (int, float)):
            v = g.node("ShaderNodeValue")
            v.outputs[0].default_value = val
            return v.outputs[0]
        return val

    def to_color(val):
        s_ = as_socket(val)
        if s_.type == "RGBA":
            return s_
        c = g.node("ShaderNodeCombineColor")
        for i in range(3):
            g.link(s_, c.inputs[i])
        return c.outputs[0]

    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    files = {}
    height = as_socket(sock["height"])
    ao = g.mr(height, 0.0, .6, .55, 1.0)
    passes = [("BaseColor", sock["color"], "sRGB"), ("Roughness", sock["rough"], "Non-Color"), ("Height", height, "Non-Color"),
              ("AO", ao, "Non-Color")]
    if not isinstance(sock["metal"], float) or sock["metal"] > 0:
        passes.append(("Metallic", sock["metal"], "Non-Color"))
    img_node = g.node("ShaderNodeTexImage")
    g.nt.nodes.active = img_node
    for ch, val, cs in passes:
        img = bpy.data.images.new(f"{name}_{ch}", res, res, alpha=False, float_buffer=False)
        img.colorspace_settings.name = cs
        img_node.image = img
        s_ = to_color(val)
        g.link(s_, emit.inputs["Color"])
        bpy.ops.object.bake(type="EMIT")
        path = d / f"{name}_{ch}.jpg"
        img.filepath_raw = str(path)
        img.file_format = "JPEG"
        scene.render.image_settings.quality = 92
        img.save_render(str(path), scene=scene)
        files[ch] = path.relative_to(root).as_posix()
    # tangent normal from the height through a bump node
    g.link(height, bump.inputs["Height"])
    g.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
    g.link(bsdf.outputs[0], out.inputs["Surface"])
    img = bpy.data.images.new(f"{name}_Normal", res, res, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    img_node.image = img
    scene.cycles.samples = 4
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    path = d / f"{name}_Normal.jpg"
    img.save_render(str(path), scene=scene)
    files["Normal"] = path.relative_to(root).as_posix()
    return files


only = [x for x in opts.only.split(",") if x]
lib_json = OUT / "texture_library_w3.json"
data = json.loads(lib_json.read_text(encoding="utf-8")) if lib_json.exists() else {"sets": {}}
for name, (builder, tile, desc) in SETS.items():
    if only and name not in only:
        continue
    files = bake_set(name, builder, opts.res)
    data["sets"][name] = {"tile_m": tile, "resolution": opts.res, "maps": files, "description": desc,
                          "provenance": "autoral: grafo procedural próprio (Tools/Blender/bake_pbr_textures.py), sem imagens externas",
                          "license": "propriedade do projeto", "normal_convention": "OpenGL (Y+), espaço tangente"}
    print("BAKED", name, list(files))
data["schemaVersion"] = 1
data["stage"] = "W3 vertical slice"
data["seamless"] = "toro 4D (ruído/voronoi periódicos) + grades inteiras por tile"
lib_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("TEXTURE LIBRARY", len(data["sets"]))
