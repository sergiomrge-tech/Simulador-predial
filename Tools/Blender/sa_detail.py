"""High-detail parametric components for W2 hero locations (requires bpy via sa_bl).

Every component is a separate bevelled object with its own pivot (Unity-prefab friendly), real dimensions in metres,
and materials from the PBR library. These are production-base pieces (LOD0 base), not final art: authored textures,
decals and wear come in W3/W4.
"""
import math

import bmesh
import bpy

import sa_materials
from sa_bl import MeshBuilder, bevelled_object, props

INTERIOR_GAIN = 3.5   # W3: interior lights calibrated for the production look (Khronos, exposure -1.4) against daylight through clear glass
EXTRA_LIB = {
    "papelao": {"family": "papel", "c1": (.62, .48, .30), "c2": (.52, .39, .23), "rough": (.8, .95), "scale": 3.0, "bump": .15, "pattern": "noise", "grime": .4, "dirt": .2, "texel": 512},
    "louca_sanitaria": {"family": "ceramica", "c1": (.92, .92, .90), "c2": (.86, .86, .84), "rough": (.05, .15), "scale": 2.0, "bump": .02, "pattern": "noise", "grime": .35, "dirt": .1, "spec": .7, "texel": 512},
    "granito": {"family": "pedra", "c1": (.24, .22, .21), "c2": (.10, .09, .09), "rough": (.15, .35), "scale": 18.0, "bump": .05, "pattern": "noise", "grime": .2, "dirt": 0.0, "texel": 1024},
    "azulejo_branco": {"family": "ceramica", "c1": (.88, .89, .88), "c2": (.80, .81, .80), "rough": (.10, .25), "scale": 1.0, "bump": .35, "pattern": "tiles", "tile": (.15, .15, .003), "mortar": (.66, .66, .62), "grime": .45, "dirt": .1, "texel": 1024},
    "tecido_colchao": {"family": "tecido", "c1": (.62, .66, .72), "c2": (.50, .54, .60), "rough": (.85, .97), "scale": 25.0, "bump": .2, "pattern": "noise", "grime": .3, "dirt": .1, "texel": 1024},
    "tecido_lencol": {"family": "tecido", "c1": (.82, .80, .74), "c2": (.72, .70, .64), "rough": (.85, .97), "scale": 8.0, "bump": .15, "pattern": "noise", "grime": .25, "dirt": .05, "texel": 1024},
    "plastico_azul": {"family": "plastico", "c1": (.12, .30, .55), "c2": (.09, .24, .45), "rough": (.35, .55), "scale": 4.0, "bump": .05, "pattern": "noise", "grime": .5, "dirt": .2, "texel": 512},
    "aco_inox": {"family": "metal", "c1": (.70, .71, .72), "c2": (.60, .61, .62), "rough": (.18, .32), "scale": 10.0, "bump": .02, "pattern": "noise", "metal": 1.0, "grime": .3, "dirt": .1, "texel": 1024},
    "aco_pintado_vermelho": {"family": "aco_pintado", "c1": (.62, .08, .06), "c2": (.48, .05, .04), "rough": (.35, .55), "scale": 3.0, "bump": .05, "pattern": "noise", "chips": True, "grime": .5, "dirt": .3, "texel": 1024},
    "borracha_preta": {"family": "borracha", "c1": (.05, .05, .05), "c2": (.03, .03, .03), "rough": (.8, .95), "scale": 6.0, "bump": .05, "pattern": "noise", "grime": .2, "dirt": .1, "texel": 512},
    "plastico_branco": {"family": "plastico", "c1": (.90, .89, .86), "c2": (.82, .81, .78), "rough": (.3, .5), "scale": 4.0, "bump": .02, "pattern": "noise", "grime": .45, "dirt": .2, "texel": 512},
    "piso_ceramico_bege": {"family": "ceramica", "c1": (.70, .62, .50), "c2": (.62, .55, .44), "rough": (.25, .45), "scale": 1.0, "bump": .3, "pattern": "tiles", "tile": (.45, .45, .004), "mortar": (.5, .47, .42), "grime": .5, "dirt": .15, "texel": 1024},
    "parede_pintada": {"family": "reboco", "c1": (.84, .82, .76), "c2": (.78, .76, .70), "rough": (.75, .9), "scale": 1.2, "bump": .12, "pattern": "noise", "grime": .55, "dirt": .45, "texel": 512},
    "concreto_aparente": {"family": "concreto", "c1": (.55, .54, .51), "c2": (.43, .42, .40), "rough": (.8, .95), "scale": 1.6, "bump": .3, "pattern": "noise", "grime": .6, "dirt": .4, "texel": 512},
}


def extend_library(lib):
    for name, spec in EXTRA_LIB.items():
        if name not in lib:
            lib[name] = sa_materials.build_material(name, spec)
    if "lampada_emissiva" not in lib:
        m = bpy.data.materials.new("lampada_emissiva")
        nt = m.node_tree
        b = nt.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (1, .92, .78, 1)
        b.inputs["Emission Color"].default_value = (1, .86, .66, 1)
        b.inputs["Emission Strength"].default_value = 12.0
        m.diffuse_color = (1, .9, .7, 1)
        m["sa_status"] = "emissivo de teste (W2)"
        lib["lampada_emissiva"] = m
    return lib


class Kit:
    """Builds detailed components into a collection; each component is a bevelled object with its own pivot."""

    def __init__(self, lib, coll, parent=None):
        self.lib = lib
        self.coll = coll
        self.parent = parent
        self.count = 0

    def obj(self, name, mb, mats, loc=(0, 0, 0), rot=0.0, bevel=.006, segments=2, **meta):
        o = bevelled_object(name, mb, [self.lib[m] for m in mats], self.coll, bevel=bevel, segments=segments)
        o.location = loc
        o.rotation_euler = (0, 0, rot)
        if self.parent:
            o.parent = self.parent
        props(o, sa_stage="W2 base de produção (LOD0 base)", **meta)
        self.count += 1
        return o

    # ------------------------------------------------------------ openings
    def window_sliding(self, name, w, h, loc, rot, grille=False, frame_mat="aluminio"):
        """Two-leaf aluminium sliding window, local origin at the bottom centre of the wall opening (outer face)."""
        mb = MeshBuilder()
        fw, fd = .05, .07
        mb.box(0, .04, 0, w, fd, fw, 0)
        mb.box(0, .04, h - fw, w, fd, fw, 0)
        mb.box(-w / 2 + fw / 2, .04, 0, fw, fd, h, 0)
        mb.box(w / 2 - fw / 2, .04, 0, fw, fd, h, 0)
        sw = (w - 2 * fw) / 2 + .03
        for k, (cx, dy) in enumerate(((-w / 4 + .01, .025), (w / 4 - .01, .055))):
            mb.box(cx, dy, fw, sw, .025, .035, 0)
            mb.box(cx, dy, h - fw - .035, sw, .025, .035, 0)
            mb.box(cx - sw / 2 + .0175, dy, fw, .035, .025, h - 2 * fw, 0)
            mb.box(cx + sw / 2 - .0175, dy, fw, .035, .025, h - 2 * fw, 0)
            mb.box(cx, dy, fw + .035, sw - .07, .006, h - 2 * fw - .07, 1)
            mb.box(cx + (sw / 2 - .06) * (1 if k == 0 else -1), dy - .02, h / 2 - .06, .015, .015, .12, 2)
        mb.box(0, .1, -.04, w + .1, .2, .04, 3)
        if grille:
            n = int(w / .11)
            for k in range(1, n):
                x = -w / 2 + k * w / n
                mb.box(x, -.06, 0, .014, .014, h, 2)
            for z in (.05, h / 2, h - .05):
                mb.box(0, -.06, z, w, .02, .02, 2)
        return self.obj(name, mb, [frame_mat, "vidro", "aco_pintado_cinza", "granito"], loc, rot, bevel=.003, sa_kind="window_sliding", size=f"{w}x{h}")

    def window_basculante(self, name, w, h, loc, rot):
        mb = MeshBuilder()
        for z in (0, h - .04):
            mb.box(0, .04, z, w, .06, .04, 0)
        for x in (-w / 2 + .02, w / 2 - .02):
            mb.box(x, .04, 0, .04, .06, h, 0)
        n = 3
        for k in range(n):
            z0 = .04 + k * (h - .08) / n
            hh = (h - .08) / n
            mb.add_face([(-w / 2 + .04, .02, z0), (w / 2 - .04, .02, z0), (w / 2 - .04, .09, z0 + hh), (-w / 2 + .04, .09, z0 + hh)], 1)
        return self.obj(name, mb, ["aluminio", "vidro"], loc, rot, bevel=.002, sa_kind="window_basculante")

    def door(self, name, w, h, loc, rot, wall_t=.15, leaf_mat="madeira_pintada", open_deg=0.0, glass=False):
        """Interior door: frame (batente) + architrave (alizar) both sides + leaf with handle and hinges. Origin: bottom centre, wall centre."""
        mb = MeshBuilder()
        bt = .035
        for x in (-w / 2 - bt / 2, w / 2 + bt / 2):
            mb.box(x, 0, 0, bt, wall_t + .01, h + bt, 0)
        mb.box(0, 0, h, w + 2 * bt, wall_t + .01, bt, 0)
        for s in (-1, 1):
            y = s * (wall_t / 2 + .006)
            for x in (-w / 2 - bt - .03, w / 2 + bt + .03):
                mb.box(x, y, 0, .06, .012, h + bt + .06, 0)
            mb.box(0, y, h + bt + .03, w + 2 * bt + .12, .012, .06, 0)
        frame = self.obj(name + "__frame", mb, ["madeira_pintada"], loc, rot, bevel=.003, sa_kind="door_frame")
        lb = MeshBuilder()
        lt = .035
        lb.box(w / 2, 0, .005, w - .006, lt, h - .01, 0)
        if glass:
            lb.box(w / 2, 0, h * .55, w * .6, lt + .004, h * .35, 2)
        else:
            for z0, hh in ((.15, h * .38), (h * .55, h * .38)):
                lb.box(w / 2, lt / 2 + .001, z0, w * .7, .006, hh, 0)
                lb.box(w / 2, -lt / 2 - .001, z0, w * .7, .006, hh, 0)
        for s in (-1, 1):
            lb.box(w - .08, s * (lt / 2 + .02), h * .48, .02, .04, .02, 1)
            lb.box(w - .13, s * (lt / 2 + .035), h * .48, .1, .015, .015, 1)
        for z in (.2, h - .25):
            lb.cylinder(0, 0, z, .008, .1, 8, 1)
        cs, sn = math.cos(rot), math.sin(rot)
        hinge = (loc[0] + (-w / 2) * cs, loc[1] + (-w / 2) * sn, loc[2])
        leaf = self.obj(name + "__leaf", lb, [leaf_mat, "aco_inox", "vidro"], hinge, rot + math.radians(open_deg), bevel=.003,
                        sa_kind="door_leaf", interactive=True, hinge="left")
        return frame, leaf

    def door_entrance_metal(self, name, w, h, loc, rot):
        mb = MeshBuilder()
        for x in (-w / 2, w / 2):
            mb.box(x, 0, 0, .06, .2, h, 0)
        mb.box(0, 0, h, w + .06, .2, .06, 0)
        mb.box(0, .02, .01, w - .04, .04, h - .02, 0)
        mb.box(0, -.005, h * .45, w * .7, .01, h * .45, 1)
        n = 8
        for k in range(n + 1):
            x = -w * .35 + k * w * .7 / n
            mb.box(x, -.02, h * .45, .012, .012, h * .45, 2)
        mb.box(w / 2 - .1, -.03, h * .47, .14, .03, .03, 3)
        return self.obj(name, mb, ["aco_pintado_verde", "vidro", "aco_pintado_cinza", "aco_inox"], loc, rot, bevel=.003, sa_kind="door_entrance", interactive=True)

    # ------------------------------------------------------------ electrical / plumbing (fictional, simplified)
    def outlet(self, name, loc, rot, z=.3):
        mb = MeshBuilder()
        mb.box(0, -.005, z - .06, .08, .01, .12, 0)
        for dz in (-.025, .025):
            for dx in (-.007, .007):
                mb.cylinder(dx, -.011, z + dz - .004, .0025, .004, 6, 1)
            mb.cylinder(0, -.011, z + dz + .006, .0025, .004, 6, 1)
        return self.obj(name, mb, ["plastico_branco", "borracha_preta"], loc, rot, bevel=.002, sa_kind="outlet_2P+T", interactive=True)

    def switch(self, name, loc, rot, z=1.1):
        mb = MeshBuilder()
        mb.box(0, -.005, z - .06, .08, .01, .12, 0)
        mb.box(0, -.012, z - .02, .03, .006, .04, 0)
        return self.obj(name, mb, ["plastico_branco"], loc, rot, bevel=.002, sa_kind="light_switch", interactive=True)

    def panel_qdc(self, name, loc, rot, z=1.5, ways=8):
        """Distribution board (fictional): flush box, door with window, rows of breakers visible behind it."""
        mb = MeshBuilder()
        w, h = .34, .42
        mb.box(0, -.004, z - h / 2, w + .04, .008, h + .04, 0)
        mb.box(0, -.014, z - h / 2, w, .012, h, 0)
        mb.box(0, -.022, z + .02, w * .8, .004, .12, 2)
        for k in range(ways):
            x = -w * .38 + k * (w * .76) / (ways - 1)
            mb.box(x, -.017, z + .03, .017, .01, .07, 1)
        mb.box(w / 2 - .03, -.025, z - .02, .015, .01, .05, 3)
        return self.obj(name, mb, ["plastico_branco", "plastico", "vidro", "aco_inox"], loc, rot, bevel=.002, sa_kind="distribution_board",
                        interactive=True, gameplay="quadro de distribuição da unidade (diagnóstico elétrico)")

    def ceiling_light(self, name, loc, bulb_only=False, drop=.35):
        mb = MeshBuilder()
        if bulb_only:
            mb.cylinder(0, 0, -drop, .003, drop, 6, 1)
            mb.cylinder(0, 0, -drop - .05, .018, .05, 12, 1)
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=.032, matrix=__import__("mathutils").Matrix.Translation((0, 0, -drop - .085)))
            base = len(mb.verts)
            mb.verts.extend(tuple(v.co) for v in bm.verts)
            for f in bm.faces:
                mb.faces.append(tuple(base + v.index for v in f.verts))
                mb.mats.append(0)
            bm.free()
        else:
            mb.cylinder(0, 0, -.06, .16, .06, 24, 0)
            mb.cylinder(0, 0, -.004, .04, .004, 12, 1)
        o = self.obj(name, mb, ["lampada_emissiva", "plastico_branco"], loc, 0.0, bevel=.0 if bulb_only else .004, sa_kind="ceiling_light")
        light = bpy.data.lights.new(name + "__light", "POINT")
        light.energy = (160 if bulb_only else 200) * INTERIOR_GAIN
        light.color = (1.0, .84, .64) if bulb_only else (1.0, .9, .78)
        light.shadow_soft_size = .05 if bulb_only else .15
        lo = bpy.data.objects.new(name + "__light", light)
        self.coll.objects.link(lo)
        lo.location = (loc[0], loc[1], loc[2] - (drop + .09 if bulb_only else .09))
        if self.parent:
            lo.parent = self.parent
        props(lo, sa_layer="Lighting", sa_kind="interior_light")
        return o

    def shower_electric(self, name, loc, rot, z=2.1):
        mb = MeshBuilder()
        mb.box(0, -.02, z, .04, .04, .04, 0)
        mb.box(0, -.18, z + .01, .03, .32, .025, 0)
        mb.cylinder(0, -.36, z - .1, .085, .11, 20, 1)
        mb.cylinder(0, -.36, z - .115, .07, .015, 20, 2)
        mb.box(0, -.01, z + .05, .02, .02, .7, 0)
        mb.box(.12, -.01, 1.15, .06, .02, .06, 3)
        return self.obj(name, mb, ["plastico_branco", "plastico_branco", "aco_inox", "aco_inox"], loc, rot, bevel=.003, sa_kind="electric_shower",
                        interactive=True, gameplay="chuveiro elétrico (carga elétrica relevante)")

    def toilet(self, name, loc, rot):
        mb = MeshBuilder()
        mb.prism([(-.17, -.28), (.17, -.28), (.15, .05), (-.15, .05)], 0, .38, 0)
        mb.cylinder(0, -.12, .26, .2, .14, 20, 0)
        mb.box(0, -.12, .40, .38, .46, .025, 0)
        mb.box(0, .16, .38, .4, .18, .38, 0)
        mb.box(0, .16, .76, .42, .2, .03, 0)
        mb.cylinder(.12, .16, .79, .02, .015, 12, 1)
        return self.obj(name, mb, ["louca_sanitaria", "aco_inox"], loc, rot, bevel=.012, segments=3, sa_kind="toilet")

    def sink_pedestal(self, name, loc, rot):
        mb = MeshBuilder()
        mb.prism([(-.09, -.06), (.09, -.06), (.07, .1), (-.07, .1)], 0, .7, 0)
        mb.box(0, -.08, .7, .52, .42, .16, 0)
        mb.box(0, -.1, .84, .38, .26, .02, 2)
        mb.cylinder(0, .07, .86, .018, .14, 12, 1)
        mb.box(0, .0, .98, .025, .14, .025, 1)
        return self.obj(name, mb, ["louca_sanitaria", "aco_inox", "borracha_preta"], loc, rot, bevel=.01, segments=3, sa_kind="sink")

    def kitchen_counter(self, name, length, loc, rot, sink_at=.7):
        """Counter along local +X from the origin, depth along -Y (towards the room), back against the wall at y=0."""
        mb = MeshBuilder()
        d = .6
        mb.box(length / 2, -d / 2 + .02, .1, length - .02, d - .06, .76, 0)
        mb.box(length / 2, -d / 2 + .02, 0, length - .1, d - .14, .1, 4)
        n = max(1, int(length / .5))
        for k in range(n):
            cx = (k + .5) * length / n
            mb.box(cx, -d + .025, .14, length / n - .01, .02, .68, 0)
            mb.box(cx + length / n * .35, -d + .005, .66, .1, .015, .015, 3)
        mb.box(length / 2, -d / 2, .86, length + .02, d + .02, .03, 1)
        mb.box(sink_at, -d / 2 + .02, .73, .5, .38, .16, 2, top=False)
        mb.cylinder(sink_at, -.05, .89, .015, .25, 10, 3)
        mb.box(sink_at, -.15, 1.13, .02, .2, .02, 3)
        return self.obj(name, mb, ["madeira_crua", "granito", "aco_inox", "aco_inox", "concreto"], loc, rot, bevel=.004, sa_kind="kitchen_counter")

    def skirting(self, name, segments, mat="madeira_pintada"):
        mb = MeshBuilder()
        for (x0, y0), (x1, y1) in segments:
            L = math.hypot(x1 - x0, y1 - y0)
            if L < .05:
                continue
            ang = math.atan2(y1 - y0, x1 - x0)
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, 0, L, .015, .07, 0, rot=ang)
        return self.obj(name, mb, [mat], bevel=.002, sa_kind="skirting")

    # ------------------------------------------------------------ building services
    def water_tank(self, name, loc):
        mb = MeshBuilder()
        r, h = .72, .95
        segs = 32
        for k in range(6):
            z = k * h / 6
            rr = r - .02 * (k % 2)
            mb.cylinder(0, 0, z, rr, h / 6, segs, 0, top=False)
        mb.cylinder(0, 0, h, r * .92, .08, segs, 0)
        mb.cylinder(0, 0, h + .08, .3, .06, segs, 0)
        mb.box(r - .05, 0, h * .8, .15, .06, .06, 1)
        return self.obj(name, mb, ["plastico_azul", "plastico_branco"], loc, 0, bevel=.008, sa_kind="water_tank_1000L", gameplay="reservatório superior")

    def entrance_meter(self, name, loc, rot, height=3.0):
        """Service entrance cabinet (fictional 'padrão de entrada'): meter box + conduit rising on the wall."""
        mb = MeshBuilder()
        mb.box(0, -.11, 1.1, .45, .22, .65, 0)
        mb.box(0, -.225, 1.35, .2, .01, .2, 1)
        mb.cylinder(.15, -.06, 1.75, .025, height - 1.75, 10, 2)
        mb.box(.15, -.06, height, .12, .12, .1, 2)
        return self.obj(name, mb, ["aco_pintado_cinza", "vidro", "aco_pintado_cinza"], loc, rot, bevel=.004, sa_kind="service_entrance_meter",
                        interactive=True, gameplay="medição de energia do prédio")

    def intercom(self, name, loc, rot, z=1.3):
        mb = MeshBuilder()
        mb.box(0, -.015, z, .12, .03, .2, 0)
        for k in range(4):
            mb.box(0, -.032, z + .03 + k * .035, .06, .005, .02, 1)
        mb.cylinder(0, -.032, z + .17, .012, .004, 10, 1)
        return self.obj(name, mb, ["aco_inox", "borracha_preta"], loc, rot, bevel=.002, sa_kind="intercom", interactive=True)

    def mailboxes(self, name, loc, rot, n=4, z=1.0):
        mb = MeshBuilder()
        for k in range(n):
            x = (k - (n - 1) / 2) * .27
            mb.box(x, -.12, z, .25, .24, .32, 0)
            mb.box(x, -.245, z + .22, .15, .01, .025, 1)
        return self.obj(name, mb, ["aco_pintado_cinza", "borracha_preta"], loc, rot, bevel=.004, sa_kind="mailboxes")

    def extinguisher(self, name, loc, rot):
        mb = MeshBuilder()
        mb.cylinder(0, -.1, 1.0, .075, .45, 16, 0)
        mb.cylinder(0, -.1, 1.45, .03, .08, 10, 1)
        mb.box(0, -.02, 1.2, .05, .04, .1, 1)
        mb.box(0, -.005, 1.65, .25, .01, .25, 2)
        return self.obj(name, mb, ["aco_pintado_vermelho", "borracha_preta", "pintura_industrial"], loc, rot, bevel=.004, sa_kind="extinguisher")

    def stair_u(self, name, width, run_len, rise_total, loc, rot, steps_per_flight=9, hollow=False):
        """U stair: flight 1 along +X at y in [0,width], landing, flight 2 back along -X at y in [width+.1, 2*width+.1]."""
        mb = MeshBuilder()
        n = steps_per_flight
        r = rise_total / (2 * n)
        t = run_len / n
        for k in range(n):
            if hollow:                                   # stepped soffit: head room above the flight stays one storey minus the tread, not (storey - rise so far)
                mb.box((k + .5) * t, width / 2, k * r, t, width, r, 0)
            else:
                mb.box((k + .5) * t, width / 2, 0, t, width, (k + 1) * r, 0)
        land = 1.2
        mb.box(run_len + land / 2, width + .05, n * r - .18, land, 2 * width + .1, .18, 0)
        for k in range(n):
            x = run_len - (k + .5) * t
            mb.box(x, width * 1.5 + .1, n * r + k * r, t, width, r, 0)
        for (y, z0, z1, x0, x1) in ((.05, .9, n * r + .9, 0, run_len), (2 * width + .05, n * r + .9, 2 * n * r + .9, run_len, 0)):
            steps = 12
            for k in range(steps):
                a, b = k / steps, (k + 1) / steps
                xa, xb = x0 + (x1 - x0) * a, x0 + (x1 - x0) * b
                za, zb = z0 + (z1 - z0) * a, z0 + (z1 - z0) * b
                L = math.hypot(xb - xa, zb - za)
                mb.box((xa + xb) / 2, y, (za + zb) / 2 - .02, abs(xb - xa) + .01, .04, .04, 1)
            for k in range(5):
                a = k / 4
                x = x0 + (x1 - x0) * a
                zt = z0 + (z1 - z0) * a
                mb.box(x, y, zt - .9 - .05, .03, .03, .9, 1)
        return self.obj(name, mb, ["concreto", "aco_pintado_cinza"], loc, rot, bevel=.006, sa_kind="stair_u")

    # ------------------------------------------------------------ H0 / G0 props
    def mattress(self, name, loc, rot):
        mb = MeshBuilder()
        mb.box(0, 0, 0, .9, 1.9, .16, 0)
        o = self.obj(name, mb, ["tecido_colchao"], loc, rot, bevel=.04, segments=3, sa_kind="prop", state="H0")
        mb2 = MeshBuilder()
        mb2.box(.02, .15, .16, .86, 1.45, .02, 0)
        mb2.box(0, -.72, .16, .62, .36, .1, 0)
        self.obj(name + "__sheets_pillow", mb2, ["tecido_lencol"], loc, rot, bevel=.03, segments=3, sa_kind="prop", state="H0")
        return o

    def chair_old(self, name, loc, rot):
        mb = MeshBuilder()
        for x in (-.18, .18):
            for y in (-.18, .18):
                mb.box(x, y, 0, .035, .035, .44, 0)
        mb.box(0, 0, .44, .44, .44, .035, 0)
        for x in (-.18, .18):
            mb.box(x, .2, .47, .035, .035, .45, 0)
        for z in (.66, .82):
            mb.box(0, .2, z, .4, .025, .07, 0)
        return self.obj(name, mb, ["madeira_crua"], loc, rot, bevel=.006, sa_kind="prop", state="H0")

    def cardboard_box(self, name, w, d, h, loc, rot, open_top=False):
        mb = MeshBuilder()
        mb.box(0, 0, 0, w, d, h, 0, top=not open_top)
        if open_top:
            for s in (-1, 1):
                mb.add_face([(-w / 2, s * d / 2, h), (w / 2, s * d / 2, h), (w / 2, s * (d / 2 + d * .35), h + d * .2), (-w / 2, s * (d / 2 + d * .35), h + d * .2)], 0)
        else:
            mb.box(0, 0, h, w + .002, .05, .002, 1)
        return self.obj(name, mb, ["papelao", "plastico"], loc, rot, bevel=.004, sa_kind="prop")

    def toolcase(self, name, loc, rot):
        mb = MeshBuilder()
        mb.box(0, 0, 0, .45, .22, .2, 0)
        mb.box(0, 0, .2, .44, .21, .01, 1)
        for x in (-.08, .08):
            mb.box(x, 0, .21, .02, .02, .05, 1)
        mb.box(0, 0, .26, .2, .025, .02, 2)
        for x in (-.16, .16):
            mb.box(x, -.115, .17, .04, .01, .03, 1)
        return self.obj(name, mb, ["aco_pintado_vermelho", "aco_inox", "borracha_preta"], loc, rot, bevel=.008, sa_kind="prop", permanent=True,
                        story="primeira maleta de ferramentas do Guto")

    def folding_table(self, name, loc, rot, w=1.2, d=.6):
        mb = MeshBuilder()
        mb.box(0, 0, .72, w, d, .03, 0)
        for x in (-w / 2 + .05, w / 2 - .05):
            mb.box(x, 0, 0, .03, d - .1, .72, 1)
        return self.obj(name, mb, ["madeira_crua", "aco_pintado_cinza"], loc, rot, bevel=.004, sa_kind="prop")

    def old_pc(self, name, loc, rot):
        mb = MeshBuilder()
        mb.box(0, 0, 0, .38, .3, .3, 0)
        mb.box(0, -.151, .04, .3, .002, .22, 1)
        mb.box(.35, 0, 0, .18, .42, .38, 0)
        mb.box(0, -.3, 0, .44, .14, .025, 0)
        return self.obj(name, mb, ["plastico_branco", "vidro"], loc, rot, bevel=.008, sa_kind="prop")

    def workbench(self, name, length, loc, rot, pro=False):
        mb = MeshBuilder()
        d = .75 if pro else .65
        mb.box(length / 2, 0, .88, length, d, .05, 0)
        for x in (.05, length - .05):
            for y in (-d / 2 + .05, d / 2 - .05):
                mb.box(x, y, 0, .06, .06, .88, 1)
        mb.box(length / 2, 0, .15, length - .1, d - .1, .03, 0)
        if pro:
            mb.box(length / 2, d / 2 - .02, .93, length, .03, 1.2, 2)
            mb.box(.25, -d / 2 + .1, .93, .2, .14, .12, 1)
        return self.obj(name, mb, ["madeira_crua", "aco_pintado_cinza", "madeira_crua"], loc, rot, bevel=.005, sa_kind="workbench")

    def shelving(self, name, length, loc, rot, levels=5, h=2.0, depth=.45):
        mb = MeshBuilder()
        for x in (0, length):
            for y in (-depth / 2, depth / 2):
                mb.box(x, y, 0, .035, .035, h, 0)
        for k in range(levels):
            z = .1 + k * (h - .15) / (levels - 1)
            mb.box(length / 2, 0, z, length, depth, .02, 1)
        return self.obj(name, mb, ["aco_pintado_cinza", "metal_galvanizado"], loc, rot, bevel=.004, sa_kind="shelving")

    def job_board(self, name, loc, rot):
        mb = MeshBuilder()
        mb.box(0, -.01, 1.2, 1.2, .02, .9, 0)
        mb.box(0, -.022, 1.2, 1.12, .004, .82, 1)
        for k, (x, z) in enumerate(((-.35, 1.85), (-.05, 1.8), (.25, 1.88), (-.3, 1.45), (.1, 1.4))):
            mb.box(x, -.026, z - .11, .18, .002, .22, 2)
        return self.obj(name, mb, ["madeira_crua", "papelao", "plastico_branco"], loc, rot, bevel=.004, sa_kind="job_board", gameplay="quadro de chamados")


    # ------------------------------------------------------------ W2.5 street life (fictional, generic)
    CAR_PAINTS = ("aco_pintado_vermelho", "aco_pintado_verde", "plastico_branco", "aco_pintado_cinza", "plastico_azul", "papelao")

    def car(self, name, loc, rot, paint=0, van=False):
        """Generic parked car / small van proxy (no brand): body, cabin, glass band, wheels, lights. LOD0 base."""
        mb = MeshBuilder()
        L, W = (4.6, 1.85) if van else (4.1, 1.7)
        mb.box(0, 0, .32, L, W, .62, 0)
        if van:
            mb.box(-.45, 0, .94, L - 1.3, W - .06, 1.05, 0)
            mb.box(1.55, 0, .94, .9, W - .1, .55, 1)
        else:
            mb.box(-.2, 0, .94, 2.1, W - .12, .5, 0)
            mb.box(-.2, 0, .98, 2.14, W - .08, .38, 1)
        for x in (-L / 2 + .75, L / 2 - .8):
            for y in (-W / 2 + .05, W / 2 - .05):
                mb.box(x, y, 0, .62, .22, .62, 2)
        for y in (-.6, .6):
            mb.box(L / 2 + .01, y, .6, .02, .3, .12, 3)
            mb.box(-L / 2 - .01, y, .6, .02, .25, .1, 4)
        paint_ = self.CAR_PAINTS[paint % len(self.CAR_PAINTS)]
        return self.obj(name, mb, [paint_, "vidro", "borracha_preta", "plastico_branco", "aco_pintado_vermelho"], loc, rot, bevel=.03,
                        sa_kind="vehicle_proxy", note="veículo genérico (proxy de cena, sem marca)")

    def crate_stack(self, name, loc, rot, n=3):
        mb = MeshBuilder()
        for k in range(n):
            x, z = (k % 2) * .62, (k // 2) * .32
            mb.box(x, 0, z, .58, .4, .3, 0)
            mb.box(x, 0, z + .26, .52, .34, .05, 1)
        return self.obj(name, mb, ["madeira_crua", "folhagem"], loc, rot, bevel=.008, sa_kind="prop")

    def freezer(self, name, loc, rot):
        mb = MeshBuilder()
        mb.box(0, 0, 0, 1.3, .7, .85, 0)
        mb.box(0, 0, .85, 1.32, .72, .05, 1)
        mb.box(0, -.36, .35, 1.0, .01, .3, 2)
        return self.obj(name, mb, ["plastico_branco", "vidro", "plastico_azul"], loc, rot, bevel=.02, sa_kind="prop", note="freezer de sorvete")

    def gas_cage(self, name, loc, rot, n=4):
        mb = MeshBuilder()
        mb.box(0, 0, 0, .55 * n + .2, .7, .1, 2)
        for k in range(n):
            mb.cylinder(-(.55 * n) / 2 + .275 + k * .55, 0, .1, .19, 1.15, 16, 0)
            mb.cylinder(-(.55 * n) / 2 + .275 + k * .55, 0, 1.25, .08, .12, 10, 1)
        for x in (-(.55 * n) / 2 - .05, (.55 * n) / 2 + .05):
            for y in (-.33, .33):
                mb.box(x, y, 0, .04, .04, 1.6, 1)
        mb.box(0, 0, 1.6, .55 * n + .2, .7, .03, 1)
        return self.obj(name, mb, ["aco_pintado_cinza", "metal_galvanizado", "concreto"], loc, rot, bevel=.006, sa_kind="gas_cage",
                        note="abrigo de cilindros de gás (genérico)")

    def pallet_stack(self, name, loc, rot, n=4):
        mb = MeshBuilder()
        for k in range(n):
            z = k * .15
            for y in (-.5, 0, .5):
                mb.box(0, y, z, 1.2, .1, .09, 0)
            for x in (-.5, 0, .5):
                mb.box(x, 0, z + .09, .1, 1.0, .02, 0)
        return self.obj(name, mb, ["madeira_crua"], loc, rot, bevel=.004, sa_kind="prop")

    def tire_stack(self, name, loc, rot, n=4):
        mb = MeshBuilder()
        for k in range(n):
            mb.cylinder(0, 0, k * .22, .33, .21, 16, 0)
        return self.obj(name, mb, ["borracha_preta"], loc, rot, bevel=.02, sa_kind="prop")

    def drum(self, name, loc, rot, paint="aco_pintado_verde"):
        mb = MeshBuilder()
        mb.cylinder(0, 0, 0, .29, .88, 18, 0)
        for z in (.28, .6):
            mb.cylinder(0, 0, z, .3, .03, 18, 0)
        return self.obj(name, mb, [paint], loc, rot, bevel=.004, sa_kind="prop")

    def a_board(self, name, loc, rot):
        mb = MeshBuilder()
        mb.add_face([(-.3, .02, 0), (.3, .02, 0), (.3, .2, .95), (-.3, .2, .95)], 0)
        mb.add_face([(-.3, -.2, .95), (.3, -.2, .95), (.3, -.02, 0), (-.3, -.02, 0)], 0)
        mb.box(0, -.13, .35, .5, .01, .45, 1)
        return self.obj(name, mb, ["madeira_pintada", "borracha_preta"], loc, rot, bevel=0.0, sa_kind="prop", note="cavalete de ofertas")

    def clothesline(self, name, p0, p1, z, n=6, seed=1):
        """Line between two points with hanging clothes (thin planes in varied fabrics)."""
        import random as _r
        rng = _r.Random(seed)
        mb = MeshBuilder()
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        mb.box(L / 2, 0, z, L, .01, .01, 0)
        for k in range(n):
            x = L * (k + .5) / n
            w, h = rng.uniform(.35, .7), rng.uniform(.4, .8)
            mb.box(x, 0, z - h, w, .01, h, 1 + k % 3)
        return self.obj(name, mb, ["aco_pintado_cinza", "tecido_lencol", "plastico_azul", "aco_pintado_vermelho"], (p0[0], p0[1], 0), ang, bevel=0.0,
                        sa_kind="prop")
