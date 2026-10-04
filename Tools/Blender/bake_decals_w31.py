"""W3.1 authored decal textures for Santa Aurora (requires bpy).

Renders, with Blender itself (orthographic camera, emission-only materials, transparent film), a set of fictional decals to RGBA
PNGs: lambe-lambe posters, graffiti pieces/tags, painted shop signs, survey/utility spray marks, stencils, safety labels, glued
poster scraps and peeling-paint patches. Every text, name, phone number and shape is invented here; no brand, logo, real business
or third-party artwork. Uses only Blender's bundled default font.

Output: ArtSource/Textures/decals_w31/<id>.png + decals_w31.json (size in metres, kind, provenance "autoral").

    blender --background --factory-startup --python Tools/Blender/bake_decals_w31.py -- --root .
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
OUT = root / "ArtSource" / "Textures" / "decals_w31"
OUT.mkdir(parents=True, exist_ok=True)

PX_PER_M = 640
BLACK, WHITE = (.02, .02, .02), (.96, .95, .92)


def R(x, y, w, h, c, rot=0.0):
    return ("rect", x, y, w, h, c, rot)


def T(s, x, y, size, c, offset=0.0, rot=0.0, align="CENTER", bold=False):
    return ("text", s, x, y, size, c, offset, rot, align)


def POLY(pts, c):
    return ("poly", pts, c)


def jagged(cx, cy, rx, ry, n, rng, amp=.25):
    """Organic outline: low-frequency harmonics (smooth lobes) plus a little high-frequency jitter (no star spikes)."""
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    pts = []
    n = max(n, 28)
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1 + amp * (math.sin(2 * a + ph[0]) * .5 + math.sin(3 * a + ph[1]) * .35 + math.sin(5 * a + ph[2]) * .2) + rng.uniform(-amp, amp) * .12
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    return pts


def torn_rect(x, y, w, h, rng, teeth=14, amp=.03):
    """Rectangle (centre x, y) with torn edges."""
    pts = []
    for side in range(4):
        for k in range(teeth):
            t = k / teeth
            if side == 0:
                px, py = x - w / 2 + w * t, y - h / 2 + rng.uniform(-amp, amp)
            elif side == 1:
                px, py = x + w / 2 + rng.uniform(-amp, amp), y - h / 2 + h * t
            elif side == 2:
                px, py = x + w / 2 - w * t, y + h / 2 + rng.uniform(-amp, amp)
            else:
                px, py = x - w / 2 + rng.uniform(-amp, amp), y + h / 2 - h * t
            pts.append((px, py))
    return pts


def drips(x0, x1, ytop, c, rng, n=7):
    out = []
    for _ in range(n):
        x = rng.uniform(x0, x1)
        L = rng.uniform(.05, .28)
        w = rng.uniform(.008, .018)
        out.append(R(x, ytop - L / 2, w, L, c))
        out.append(POLY(jagged(x, ytop - L, w * .9, w * .9, 8, rng, .1), c))
    return out


def tabs(x0, y, n, w, h, c, txt, tc):
    els = []
    for k in range(n):
        x = x0 + k * w
        els.append(R(x, y, w - .006, h, c))
        els.append(T(txt, x + .007, y, .019, tc, rot=math.pi / 2))
    return els


rng = random.Random(3101)
DECALS = {}
# ---------------------------------------------------------------- posters (lambe-lambe), 0.60 x 0.85 m
DECALS["cartaz_forro"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, (.96, .80, .16)), R(0, .33, .6, .19, (.72, .10, .06)), T("FORRÓ", 0, .30, .15, WHITE),
    T("NA PRAÇA", 0, .13, .085, (.15, .08, .05)), T("SÁBADO • 20H", 0, .0, .06, (.72, .10, .06)),
    R(0, -.12, .48, .006, (.15, .08, .05)), T("VILA AURORA", 0, -.2, .055, (.15, .08, .05)),
    T("TRIO PÉ DE SERRA", 0, -.28, .035, (.15, .08, .05)), R(0, -.385, .6, .08, (.15, .08, .05)), T("ENTRADA FRANCA", 0, -.4, .04, (.96, .80, .16))])
DECALS["cartaz_violao"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, WHITE), T("AULAS DE", 0, .31, .06, (.1, .2, .5)), T("VIOLÃO", 0, .2, .13, (.1, .2, .5)),
    T("iniciantes • crianças e adultos", 0, .1, .028, BLACK), T("prof. Ademir", 0, .03, .045, BLACK),
    POLY(jagged(0, -.1, .07, .055, 18, random.Random(21), .05), (.55, .32, .12)), POLY(jagged(0, -.03, .05, .04, 18, random.Random(22), .05), (.55, .32, .12)),
    POLY(jagged(0, -.07, .018, .018, 12, random.Random(23), .02), (.15, .08, .04)), R(0, .0, .016, .06, (.3, .18, .08)),
    T("preço popular", 0, -.2, .035, (.6, .1, .08))] + tabs(-.27, -.345, 10, .06, .15, WHITE, "9 4417-2280", BLACK))
DECALS["cartaz_circo"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, (.08, .12, .38))] + [POLY(jagged(rng.uniform(-.25, .25), rng.uniform(-.35, .38), .03, .03, 10, rng, .6), (.98, .82, .2)) for _ in range(9)] + [
    T("CIRCO", 0, .26, .12, (.98, .82, .2)), T("ESTRELA", 0, .13, .085, WHITE), T("DO SUL", 0, .04, .085, WHITE),
    R(0, -.12, .6, .11, (.78, .12, .1), .0), T("ÚLTIMA SEMANA", 0, -.135, .05, WHITE), T("TERRENO DA ESTAÇÃO VELHA", 0, -.27, .03, WHITE),
    T("palhaço Pipoca • trapézio • mágico", 0, -.33, .026, (.98, .82, .2))])
DECALS["cartaz_aluga"] = ("poster", .5, .7, [
    R(0, 0, .5, .7, (.86, .80, .64)), T("ALUGA-SE", 0, .22, .085, (.05, .05, .2)), T("QUARTO", 0, .1, .1, (.05, .05, .2)),
    T("c/ banheiro", 0, 0, .045, BLACK), T("moça ou rapaz", 0, -.07, .04, BLACK), T("TRATAR AQUI", 0, -.22, .05, (.6, .08, .06))])
DECALS["cartaz_mutirao"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, (.18, .48, .26)), T("MUTIRÃO", 0, .3, .1, WHITE), T("DE LIMPEZA DO", 0, .19, .05, WHITE), T("CÓRREGO", 0, .09, .11, (.98, .9, .4)),
    POLY([(-.3, -.06), (-.15, -.03), (0, -.07), (.15, -.02), (.3, -.06), (.3, -.12), (-.3, -.12)], (.4, .7, .9)),
    T("DOMINGO • 8H", 0, -.2, .06, WHITE), T("traga luva e saco", 0, -.28, .035, WHITE), T("associação de moradores", 0, -.36, .028, (.85, .95, .85))])
DECALS["cartaz_feira"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, (.95, .52, .14)), R(0, 0, .52, .77, (.99, .93, .80)), T("FEIRA", 0, .27, .12, (.75, .25, .06)), T("DE TROCAS", 0, .15, .07, (.2, .1, .05)),
    T("roupas • livros • plantas", 0, .05, .032, (.2, .1, .05)), T("LARGO DO MERCADO", 0, -.08, .05, (.75, .25, .06)), T("1º SÁBADO DO MÊS", 0, -.18, .045, (.2, .1, .05))])
DECALS["cartaz_baile"] = ("poster", .6, .85, [
    R(0, 0, .6, .85, (.04, .03, .06))] + [R(-.3 + k * .075, .38, .04, .03, ((.95, .2, .6), (.2, .85, .95), (.98, .85, .2))[k % 3]) for k in range(9)] + [
    T("BAILE", 0, .22, .14, (.95, .2, .6)), T("DA ESTAÇÃO", 0, .08, .075, (.2, .85, .95)), T("SEXTA 22H", 0, -.06, .07, WHITE),
    T("DJ Marquinho • Banda Trem Bão", 0, -.17, .03, (.98, .85, .2)), T("clube recreativo", 0, -.3, .03, (.7, .7, .7))])
DECALS["cartaz_procura"] = ("poster", .42, .6, [
    R(0, 0, .42, .6, WHITE), T("PROCURA-SE", 0, .24, .058, (.7, .05, .05)), R(0, .07, .3, .2, (.78, .62, .38)),
    POLY(jagged(0, .06, .09, .055, 14, rng, .15) , (.55, .38, .2)), POLY(jagged(.08, .1, .04, .035, 10, rng, .1), (.55, .38, .2)),
    T("cachorro caramelo", 0, -.07, .03, BLACK), T("atende por PAÇOCA", 0, -.12, .032, BLACK), T("recompensa", 0, -.18, .03, (.7, .05, .05)),
    T("9 5532-1047", 0, -.24, .036, BLACK)])
# ---------------------------------------------------------------- graffiti, 2.2 x 0.9 m (outline layers via text offset)


def piece(word, fill, size=.42, rot=0.0, drip_c=None, seed=1):
    r_ = random.Random(seed)
    els = [T(word, 0, -.12, size, BLACK, offset=.035, rot=rot), T(word, 0, -.12, size, WHITE, offset=.018, rot=rot), T(word, 0, -.12, size, fill, rot=rot)]
    els += [T(word, -.006, -.112, size, tuple(min(1, c * 1.25 + .08) for c in fill), offset=-.012, rot=rot)]   # inner highlight
    if drip_c:
        els = els[:3] + drips(-.8, .8, -.1, drip_c, r_, 9) + els[3:]
    return els


DECALS["grafite_aurora"] = ("graffiti", 2.2, .9, piece("AURORA", (.95, .42, .08), drip_c=(.95, .42, .08), seed=2))
DECALS["grafite_crua"] = ("graffiti", 2.0, .9, piece("CRUA", (.08, .62, .62), size=.5, rot=.06, drip_c=(.08, .62, .62), seed=3))
DECALS["grafite_vlt"] = ("graffiti", 2.2, .9, piece("VLT85", (.5, .22, .7), size=.44, rot=-.08, seed=4))
DECALS["grafite_tags"] = ("graffiti", 1.6, .7, [
    T("zé+lu", -.35, .12, .16, BLACK, offset=.004, rot=.12), T("dk", .45, .15, .2, (.75, .05, .05), offset=.006, rot=-.2),
    T("SA ZN", .1, -.15, .13, (.1, .2, .6), offset=.004, rot=.05), T("2019", -.5, -.2, .09, BLACK, rot=-.1)] + drips(.3, .6, .05, (.75, .05, .05), random.Random(5), 4))
DECALS["grafite_bomb"] = ("graffiti", 1.4, .8, [
    T("SA", 0, -.16, .55, BLACK, offset=.045), T("SA", 0, -.16, .55, (.98, .45, .7), offset=.02), T("SA", 0, -.16, .55, (.98, .85, .9))])
# ---------------------------------------------------------------- painted shop signs, 2.4 x 0.6 m


def sign(bg, border, title, sub, tc, sc):
    return [R(0, 0, 2.4, .6, border), R(0, 0, 2.3, .5, bg), T(title, 0, .02, .2, tc), T(sub, 0, -.19, .075, sc)]


DECALS["placa_bazar"] = ("sign", 2.4, .6, sign((.97, .93, .78), (.6, .1, .1), "BAZAR DA CIDA", "armarinho • presentes • utilidades", (.6, .1, .1), (.1, .1, .1)))
DECALS["placa_chaveiro"] = ("sign", 2.4, .6, sign((.98, .8, .1), BLACK, "CHAVEIRO 24H", "cópias • fechaduras • carimbos", BLACK, BLACK) + [
    POLY(jagged(-1.0, .02, .07, .07, 16, rng, .02), BLACK), R(-.86, .02, .2, .035, BLACK), R(-.78, -.01, .03, .05, BLACK)])
DECALS["placa_lanches"] = ("sign", 2.4, .6, sign((.75, .12, .08), (.98, .85, .2), "LANCHES DO BETO", "pastel • caldo de cana • salgados", (.98, .9, .4), WHITE))
DECALS["placa_salao"] = ("sign", 2.4, .6, sign((.95, .85, .9), (.55, .15, .4), "SALÃO BELEZA PURA", "corte • escova • manicure", (.55, .15, .4), (.2, .1, .15)))
DECALS["placa_eletro"] = ("sign", 2.4, .6, sign((.1, .25, .55), WHITE, "CONSERTO DE ELETRO", "TV • som • micro-ondas • ventilador", WHITE, (.98, .85, .2)))
# ---------------------------------------------------------------- spray marks, stencils, labels
DECALS["marca_agua"] = ("mark", 1.0, .5, [T("ÁGUA", -.15, .05, .14, (.1, .35, .85), offset=.004), POLY([(.22, .15), (.3, .15), (.3, -.02), (.36, -.02), (.26, -.16), (.16, -.02), (.22, -.02)], (.1, .35, .85)),
                                          T("1,2 m", -.12, -.15, .09, (.1, .35, .85), offset=.003)])
DECALS["marca_rn"] = ("mark", .8, .5, [R(-.2, 0, .3, .03, (.85, .1, .1), .78), R(-.2, 0, .3, .03, (.85, .1, .1), -.78), T("RN-3", .2, -.03, .1, (.85, .1, .1), offset=.003),
                                       T("+0,45", .2, -.15, .06, (.85, .1, .1))])
DECALS["marca_vala"] = ("mark", 1.2, .4, [R(-.3, 0, .7, .03, (.95, .55, .05)), POLY([(.05, .07), (.2, 0), (.05, -.07)], (.95, .55, .05)), T("VALA", .38, -.04, .1, (.95, .55, .05), offset=.003)])
DECALS["estencil_nao_estacione"] = ("mark", 1.4, .35, [T("NÃO ESTACIONE", 0, -.06, .17, WHITE), T("GARAGEM", 0, -.17, .07, WHITE)])
DECALS["etiqueta_perigo"] = ("label", .3, .38, [R(0, 0, .3, .38, (.98, .8, .1)), POLY([(-.12, .02), (.12, .02), (0, .17)], BLACK), POLY([(-.095, .035), (.095, .035), (0, .145)], (.98, .8, .1)),
                                                 POLY([(.005, .13), (-.025, .08), (.0, .08), (-.01, .045), (.025, .095), (.002, .095)], BLACK), T("PERIGO", 0, -.06, .055, BLACK),
                                                 T("ALTA TENSÃO", 0, -.12, .035, BLACK)])
DECALS["etiqueta_numero"] = ("label", .32, .2, [R(0, 0, .32, .2, (.1, .25, .6)), R(0, 0, .29, .17, WHITE), T("214", 0, -.045, .11, (.1, .25, .6))])
# ---------------------------------------------------------------- glued scraps and peeling paint
_sc = []
_r = random.Random(11)
for k in range(9):
    c = _r.choice(((.92, .88, .75), (.95, .75, .2), (.85, .3, .25), (.4, .6, .85), (.9, .9, .9), (.5, .75, .45)))
    x, y = _r.uniform(-.4, .4), _r.uniform(-.28, .28)
    pts = torn_rect(x, y, _r.uniform(.18, .45), _r.uniform(.15, .35), _r, teeth=22, amp=.01)
    _sc.append(POLY(pts, c))
    if _r.random() < .6:
        _sc.append(T(_r.choice(("FES", "ALUG", "ÇA", "SÁB", "20H", "OVIDA", "TRO")), x, y - .03, .06, _r.choice((BLACK, (.6, .1, .08))), rot=_r.uniform(-.1, .1)))
DECALS["restos_cartaz"] = ("scraps", 1.2, .9, [POLY(jagged(0, 0, .5, .36, 30, _r, .1), (.80, .77, .68))] + _sc)
_pe = []
_r = random.Random(13)
for k in range(7):
    cx, cy = _r.uniform(-.35, .35), _r.uniform(-.28, .28)
    rx, ry = _r.uniform(.05, .2), _r.uniform(.04, .14)
    _ro = random.Random(k * 7 + 1)
    _pe.append(POLY(jagged(cx, cy, rx * 1.06, ry * 1.06, 40, random.Random(k), .35), (.90, .88, .83)))     # lifted paint edge
    _pe.append(POLY(jagged(cx, cy, rx, ry, 40, random.Random(k), .35), (.66, .62, .55)))                   # exposed plaster
    if _ro.random() < .5:
        _pe.append(POLY(jagged(cx + rx * .15, cy - ry * .1, rx * .4, ry * .35, 28, _ro, .4), (.56, .36, .28)))   # brick behind
DECALS["tinta_descascando"] = ("peeling", 1.0, .8, _pe)


# ---------------------------------------------------------------- renderer
def emission(c):
    key = "dc_%.3f_%.3f_%.3f" % c
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*(v ** 2.2 for v in c), 1)          # colours above are authored in display (sRGB) space
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def build(elements, coll):
    z = 0.0
    for el in elements:
        z += .001
        if el[0] == "rect":
            _, x, y, w, h, c, rot = el
            me = bpy.data.meshes.new("r")
            cs, sn = math.cos(rot), math.sin(rot)
            pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
            me.from_pydata([(x + px * cs - py * sn, y + px * sn + py * cs, z) for px, py in pts], [], [(0, 1, 2, 3)])
            me.materials.append(emission(c))
            coll.objects.link(bpy.data.objects.new("r", me))
        elif el[0] == "poly":
            _, pts, c = el
            me = bpy.data.meshes.new("p")
            me.from_pydata([(px, py, z) for px, py in pts], [], [tuple(range(len(pts)))])
            bm = bmesh.new()                                   # torn/jagged outlines are concave: triangulate properly
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces[:], ngon_method="BEAUTY")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(emission(c))
            coll.objects.link(bpy.data.objects.new("p", me))
        else:
            _, s, x, y, size, c, offset, rot, align = el
            cu = bpy.data.curves.new("t", "FONT")
            cu.body = s
            cu.size = size
            cu.align_x = align
            cu.align_y = "BOTTOM_BASELINE"
            cu.offset = offset
            cu.materials.append(emission(c))
            o = bpy.data.objects.new("t", cu)
            o.location = (x, y, z)
            o.rotation_euler = (0, 0, rot)
            coll.objects.link(o)


scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
scene.render.engine = "BLENDER_EEVEE"
scene.render.film_transparent = True
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.compression = 90
try:
    scene.eevee.taa_render_samples = 16
except AttributeError:
    pass
world = bpy.data.worlds.new("w")
scene.world = world
camd = bpy.data.cameras.new("c")
camd.type = "ORTHO"
cam = bpy.data.objects.new("c", camd)
scene.collection.objects.link(cam)
cam.location = (0, 0, 5)
scene.camera = cam
meta = {}
for did, (kind, w, h, els) in DECALS.items():
    coll = bpy.data.collections.new(did)
    scene.collection.children.link(coll)
    build(els, coll)
    camd.ortho_scale = max(w, h)
    scene.render.resolution_x = int(min(1024, w * PX_PER_M) * (1 if w >= h else 1))
    scene.render.resolution_y = int(scene.render.resolution_x * h / w)
    scene.render.filepath = str(OUT / f"{did}.png")
    bpy.ops.render.render(write_still=True)
    for o in list(coll.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(coll)
    meta[did] = {"kind": kind, "size_m": [w, h], "file": f"{did}.png", "px": [scene.render.resolution_x, scene.render.resolution_y]}
(OUT / "decals_w31.json").write_text(json.dumps({"provenance": "autoral (gerado por Tools/Blender/bake_decals_w31.py; fonte padrão do Blender)",
                                                 "license": "projeto (autoral)", "decals": meta}, indent=1, ensure_ascii=False), encoding="utf-8")
print("W3.1 DECALS BAKED", len(meta))
