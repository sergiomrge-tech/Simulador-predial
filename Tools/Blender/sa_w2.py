"""Shared scaffolding for W2 hero generators (one .blend per hero, local frame under a root empty).

Local frame (sa_heroes.Frame): front facade at -Y, origin at the building centre on the ground. The root empty carries the
world transform used by the Old Town base, so each hero can be opened as its own scene and still sit in the world.
"""
import json
import math
from pathlib import Path

import bpy

import sa_bl
import sa_detail
import sa_materials
from masterplan_layout import load_spec
from sa_heroes import Frame, fixed
from sa_terrain import Terrain

STAGE = "W2 base de produção"
LAYERS = ("Shell", "Structure", "Interior", "Openings", "Services", "Props_G0", "Site", "Gameplay")
SCENE_ONLY = ("Lighting", "Cameras", "CaptureOnly")   # outside the hero collection: never travels with a linked instance


class HeroScene:
    def __init__(self, root, hero_id, prefix, building_index=0):
        self.root = Path(root)
        data = json.loads((self.root / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json").read_text(encoding="utf-8"))
        self.hero = next(h for h in data["heroes"] if h["id"] == hero_id)
        self.id, self.prefix = hero_id, prefix
        terrain = Terrain(load_spec(self.root))
        x0, y0, x1, y1 = self.hero["lot"]
        pts = ((x0, y0), (x1, y0), (x1, y1), (x0, y1), ((x0 + x1) / 2, (y0 + y1) / 2))
        self.ground = sum(terrain.surface(*p) for p in pts) / len(pts) + .12
        self.bld = self.hero["buildings"][building_index]
        self.fr = Frame(self.bld["rect"], self.hero["front"], self.ground)
        self.W, self.D = self.fr.w, self.fr.d
        self.hw, self.hd = self.W / 2, self.D / 2
        sa_bl.clear_scene()
        self.scene = bpy.context.scene
        self.scene.name = f"W2_{hero_id}"
        self.scene.unit_settings.system = "METRIC"
        self.scene.unit_settings.scale_length = 1.0
        try:
            self.scene.eevee.shadow_pool_size = "1024"
        except (AttributeError, TypeError):
            pass
        self.lib = sa_materials.build_library()
        sa_detail.extend_library(self.lib)
        self.facade = self.fixed(self.bld["facade"])
        self.top = sa_bl.collection(f"W2_{hero_id}")
        self.C = {k: sa_bl.collection(f"{prefix}_{k}", self.top) for k in LAYERS}
        self.scene_only = sa_bl.collection(f"W2_{hero_id}__SceneOnly")
        self.C.update({k: sa_bl.collection(f"{prefix}_{k}", self.scene_only) for k in SCENE_ONLY})
        self.rootobj = bpy.data.objects.new(f"W2_{hero_id}_ROOT", None)
        self.rootobj.empty_display_type = "ARROWS"
        self.rootobj.location = (self.fr.c[0], self.fr.c[1], self.ground)
        self.rootobj.rotation_euler = (0, 0, self.fr.rot)
        self.top.objects.link(self.rootobj)
        sa_bl.props(self.rootobj, facility_id=hero_id, sa_stage=STAGE, world_ground_z=round(self.ground, 3),
                    note="Raiz do herói: filhos em coordenadas locais (frente em -Y). Transform = posição no mundo (Cidade Antiga).")
        self.captures = []

    # ------------------------------------------------------------ helpers
    def fixed(self, name):
        m = fixed(self.lib, name)
        self.lib[m.name] = m
        return m.name

    def kit(self, layer):
        return sa_detail.Kit(self.lib, self.C[layer], parent=self.rootobj)

    def L(self, p):
        return self.fr.to_local(p)

    def Lrect(self, r):
        a, b = self.L((r[0], r[1])), self.L((r[2], r[3]))
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))

    def mesh(self, name, mb, mats, layer, bevel=0.0, **meta):
        mats = [self.lib[m] for m in mats]
        if bevel:
            o = sa_bl.bevelled_object(name, mb, mats, self.C[layer], bevel=bevel)
        else:
            o = mb.to_object(name, mats, self.C[layer])
        o.parent = self.rootobj
        sa_bl.props(o, facility_id=self.id, sa_stage=STAGE, **meta)
        return o

    def empty(self, name, loc, size, layer="Gameplay", shape="CUBE", **meta):
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = shape
        e.location = loc
        e.scale = tuple(max(s, .05) / 2 for s in size)
        self.C[layer].objects.link(e)
        e.parent = self.rootobj
        sa_bl.props(e, facility_id=self.id, **meta)
        return e

    def state_slots(self, z_of=lambda state, name: 0.0, tag="SLOT"):
        interior = self.hero["interior"]
        for state, items in interior["states"].items():
            for name, (x, y, w, d, h) in items:
                p = self.L((x, y))
                sw, sd = (d, w) if self.hero["front"] in ("E", "W") else (w, d)
                z = z_of(state, name)
                self.empty(f"W2_{tag}_{self.id}__{state}__{name}", (p[0], p[1], z + h / 2), (sw, sd, h), sa_kind="state_slot", state=state, item=name,
                           sa_layer="Gameplay")
        for name, (x, y, w, d, h) in interior.get("permanent", []):
            p = self.L((x, y))
            self.empty(f"W2_{tag}_{self.id}__ALL__{name}", (p[0], p[1], h / 2), (w, d, h), sa_kind="state_slot", state="ALL", item=name, sa_layer="Gameplay")

    def cam(self, name, loc, target, lens):
        w = self.fr.to_world
        return sa_bl.camera(name, self.C["Cameras"], w(loc), target=w(target), lens=lens, clip=(.05, 2000))

    def cutaway(self, name, center, z, ortho):
        return sa_bl.camera(name, self.C["Cameras"], self.fr.to_world((center[0], center[1], z)), rot=(0, 0, self.fr.rot), ortho=ortho, clip=(.05, 300))

    def capture(self, name, cam, w=2400, h=1350, hide=()):
        self.captures.append([name, cam, w, h, list(hide)])

    def bake_interior_probe(self):
        return bake_interior_probe(self.top, self.C["Lighting"], self.id, self.rootobj)

    def save(self, filename):
        self.scene.render.engine = "BLENDER_EEVEE"
        try:
            self.scene.eevee.use_raytracing = True
        except AttributeError:
            pass
        self.bake_interior_probe()
        self.scene["sa_captures"] = json.dumps(self.captures)
        self.scene["sa_hero"] = self.id
        self.scene["facility_stage"] = STAGE + " (não é arte final)"
        out = self.root / "ArtSource" / "Blender" / "World" / "OldTown" / "Heroes"
        out.mkdir(parents=True, exist_ok=True)
        path = out / filename
        bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
        bak = path.with_suffix(".blend1")
        if bak.exists():
            bak.unlink()
        print("W2 HERO GENERATED", path.name, len(bpy.data.objects))
        return path


def area_fill(coll, parent, name, loc, sx, sy, energy, color=(1.0, .86, .70)):
    """W3.1: warm rectangular fill under the ceiling (tubular-fixture equivalent) for interior captures; scene-only."""
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = max(.5, sx), max(.5, sy)
    ld.energy = energy
    ld.color = color
    try:
        ld.use_shadow = True
    except AttributeError:
        pass
    o = bpy.data.objects.new(name, ld)
    coll.objects.link(o)
    o.parent = parent
    o.location = loc
    o["sa_stage"] = "W3.1 luz de preenchimento interior (captura; equivalente a luminárias tubulares)"
    return o


def bake_interior_probe(hero_coll, light_coll, hid, rootobj=None):
    """W3.1: baked irradiance volume over the hero (scene-only collection) so interiors receive occluded, bounced light instead of
    the unshadowed blue world ambient. Unity equivalent: Adaptive Probe Volume over the hero (documented, not exported)."""
    from mathutils import Matrix, Vector
    bpy.context.view_layer.update()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in hero_coll.all_objects:
        if o.type != "MESH" or o.hide_render:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    if lo.x > hi.x:
        return None
    lo -= Vector((.5, .5, .2))
    hi += Vector((.5, .5, .5))
    pd = bpy.data.lightprobes.new(f"IV_{hid}", "VOLUME")
    size = hi - lo
    pd.resolution_x, pd.resolution_y, pd.resolution_z = (max(4, min(40, int(v / 1.2))) for v in size)
    po = bpy.data.objects.new(f"IV_{hid}", pd)
    light_coll.objects.link(po)
    mw = Matrix.LocRotScale((lo + hi) / 2, None, size / 2)
    if rootobj is not None:
        po.parent = rootobj
    po.matrix_world = mw
    po["sa_stage"] = "W3.1 volume de irradiância (somente cena/captura; Unity: Adaptive Probe Volume)"
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = po
    po.select_set(True)
    try:
        with bpy.context.temp_override(object=po, active_object=po, selected_objects=[po]):
            bpy.ops.object.lightprobe_cache_bake(subset="ACTIVE")
        print("W3.1 IRRADIANCE VOLUME BAKED", hid, tuple(round(v, 1) for v in size))
    except Exception as ex:                                         # bake is an enhancement; never block generation
        print("W3.1 IRRADIANCE VOLUME BAKE FAILED", hid, ex)
    return po


def wall_x(mb, y, x0, x1, t, z0, z1, ops, mat):
    """Wall along X at y (centre line) from x0 to x1; ops = [(xc, w, zb, zt)] openings."""
    cur = x0
    for xc, w, zb, zt in sorted(ops):
        a, b = max(x0, xc - w / 2), min(x1, xc + w / 2)
        if a > cur:
            mb.box((cur + a) / 2, y, z0, a - cur, t, z1 - z0, mat)
        if zb > z0:
            mb.box((a + b) / 2, y, z0, b - a, t, zb - z0, mat)
        if zt < z1:
            mb.box((a + b) / 2, y, zt, b - a, t, z1 - zt, mat)
        cur = b
    if x1 > cur:
        mb.box((cur + x1) / 2, y, z0, x1 - cur, t, z1 - z0, mat)


def wall_y(mb, x, y0, y1, t, z0, z1, ops, mat):
    """Wall along Y at x; ops = [(yc, w, zb, zt)]."""
    cur = y0
    for yc, w, zb, zt in sorted(ops):
        a, b = max(y0, yc - w / 2), min(y1, yc + w / 2)
        if a > cur:
            mb.box(x, (cur + a) / 2, z0, t, a - cur, z1 - z0, mat)
        if zb > z0:
            mb.box(x, (a + b) / 2, z0, t, b - a, zb - z0, mat)
        if zt < z1:
            mb.box(x, (a + b) / 2, zt, t, b - a, z1 - zt, mat)
        cur = b
    if y1 > cur:
        mb.box(x, (cur + y1) / 2, z0, t, y1 - cur, z1 - z0, mat)


def wall_rot(side):
    """Rotation for components whose back faces local +Y, mounted on an interior face looking into the room.
    side = direction from the object towards the wall: '+y', '-y', '+x', '-x'."""
    return {"+y": 0.0, "-y": math.pi, "+x": -math.pi / 2, "-x": math.pi / 2}[side]


def text_mesh(name, text, size, coll, mat, extrude=.006):
    """Builtin-font text converted to a mesh (no external font file)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = text
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    coll.objects.link(ob)
    me = bpy.data.meshes.new_from_object(ob)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    me.materials.append(mat)
    return o


def partition_plan(rooms, walled, hw, hd, T, door_w=.9, door_override=None):
    """Interior walls from room rects: drop edges on the outer walls, merge shared/colinear edges, one door per room on the
    edge nearest the building centre (or door_override[room] = (axis, c, p, w)). Returns (edges, doors)."""
    door_override = door_override or {}

    def outer(e):
        return (e[0] == "x" and abs(abs(e[1]) - (hd - T)) < .35) or (e[0] == "y" and abs(abs(e[1]) - (hw - T)) < .35)

    edges, doors = [], []
    for r in walled:
        x0, y0, x1, y1 = rooms[r]
        cand = [e for e in (("x", y0, x0, x1), ("x", y1, x0, x1), ("y", x0, y0, y1), ("y", x1, y0, y1)) if not outer(e)]
        if r in door_override:
            if door_override[r]:
                doors.append(door_override[r] + (r,))
        elif cand:
            best = min(cand, key=lambda e: math.hypot(*(((e[2] + e[3]) / 2, e[1]) if e[0] == "x" else (e[1], (e[2] + e[3]) / 2))))
            doors.append((best[0], best[1], (best[2] + best[3]) / 2, door_w, r))
        edges.extend(cand)
    merged = []
    for axis, c, a, b in edges:
        segs = [(a, b)]
        for m in merged:
            if m[0] == axis and abs(m[1] - c) < .3:
                nxt = []
                for s0, s1 in segs:
                    if m[3] <= s0 or m[2] >= s1:
                        nxt.append((s0, s1))
                        continue
                    if m[2] > s0:
                        nxt.append((s0, m[2]))
                    if m[3] < s1:
                        nxt.append((m[3], s1))
                segs = nxt
        merged.extend((axis, c, s0, s1) for s0, s1 in segs if s1 - s0 > .2)
    return merged, doors


def light_window(mb, axis, c, pos, w, zb, h, out_sign, m_frame, m_glass, m_sill):
    """Lightweight window (LOD0-light) merged into a per-floor mesh: frame, mullion, glass, sill.
    axis 'x': wall along X at y=c; 'y': wall along Y at x=c. out_sign = +1/-1 direction of the exterior."""
    d = .07
    if axis == "x":
        y = c + out_sign * .02
        mb.box(pos, y, zb, w, d, .05, m_frame)
        mb.box(pos, y, zb + h - .05, w, d, .05, m_frame)
        for x in (pos - w / 2 + .025, pos, pos + w / 2 - .025):
            mb.box(x, y, zb, .05, d, h, m_frame)
        mb.box(pos, y - out_sign * .01, zb + .05, w - .05, .006, h - .1, m_glass)
        mb.box(pos, c + out_sign * .12, zb - .04, w + .1, .2, .04, m_sill)
    else:
        x = c + out_sign * .02
        mb.box(x, pos, zb, d, w, .05, m_frame)
        mb.box(x, pos, zb + h - .05, d, w, .05, m_frame)
        for y in (pos - w / 2 + .025, pos, pos + w / 2 - .025):
            mb.box(x, y, zb, d, .05, h, m_frame)
        mb.box(x - out_sign * .01, pos, zb + .05, .006, w - .05, h - .1, m_glass)
        mb.box(c + out_sign * .12, pos, zb - .04, .2, w + .1, .04, m_sill)



def wear_pass(lib, coll, parent, rects, entrances=(), ground_rects=(), drive_lines=(), seed=1, prefix="W2_", facility=""):
    """W2.5 decal pass for a hero: damp at wall bases, run-off streaks, dirt at doors, oil in parking, tire marks on drives.
    rects: [(x0, y0, x1, y1, height)] footprints (local). entrances: [(x, y, side)], side in '-y','+y','-x','+x'.
    ground_rects: [(x0, y0, x1, y1)] parking/yards for oil stains. drive_lines: [((x0, y0), (x1, y1))] for tire marks."""
    import random as _r
    rng = _r.Random(seed)
    mb = sa_bl.MeshBuilder()
    mats = ["decal_umidade", "decal_sujeira", "decal_oleo", "decal_pneu", "decal_ferrugem"]
    n_v = n_h = 0
    for (x0, y0, x1, y1, hgt) in rects:
        for side in ("-y", "+y", "-x", "+x"):
            if side[1] == "y":
                c, a, b = (y0 - .03 if side == "-y" else y1 + .03), x0, x1
            else:
                c, a, b = (x0 - .03 if side == "-x" else x1 + .03), y0, y1
            L = b - a
            t = rng.uniform(0, 3)
            while t < L - 1:
                w = rng.uniform(1.5, 4.5)
                h = rng.uniform(.5, 1.3)
                u0, u1 = a + t, min(b, a + t + w)
                quad = [(u0, 0.0), (u1, 0.0), (u1, h), (u0, h)]
                pts = [((u, c, z) if side[1] == "y" else (c, u, z)) for u, z in quad]
                mb.add_face(pts if side in ("-y", "+x") else pts[::-1], 0)
                n_v += 1
                if rng.random() < .45 and hgt > 3:
                    sw, z1 = rng.uniform(.4, 1.0), rng.uniform(2.0, hgt - .3)
                    um = u0 + rng.uniform(0, max(.1, w - sw))
                    zb_ = z1 - rng.uniform(1.2, 2.8)
                    q2 = [(um, zb_), (um + sw, zb_), (um + sw, z1), (um, z1)]
                    pts = [((u, c, z) if side[1] == "y" else (c, u, z)) for u, z in q2]
                    mb.add_face(pts if side in ("-y", "+x") else pts[::-1], 1)
                    n_v += 1
                t += w + rng.uniform(1.5, 6.0)
    for (x, y, side) in entrances:
        dx, dy = {"-y": (0, -1.2), "+y": (0, 1.2), "-x": (-1.2, 0), "+x": (1.2, 0)}[side]
        mb.box(x + dx, y + dy, .012, 2.4, 2.0, .004, 1)
        n_h += 1
    for (x0, y0, x1, y1) in ground_rects:
        for k in range(max(1, int((x1 - x0) * (y1 - y0) / 25))):
            if rng.random() < .6:
                mb.box(rng.uniform(x0 + .8, x1 - .8), rng.uniform(y0 + .8, y1 - .8), .008, rng.uniform(.8, 1.6), rng.uniform(.6, 1.2), .004, 2)
                n_h += 1
    for (p0, p1) in drive_lines:
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if L < 1:
            continue
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        for w in (-.8, .8):
            c = ((p0[0] + p1[0]) / 2 + nx * w, (p0[1] + p1[1]) / 2 + ny * w)
            mb.box(c[0], c[1], .01, L, .32, .004, 3, rot=ang)
            n_h += 1
    o = mb.to_object(prefix + "wear_decals", [lib[m] for m in mats], coll)
    o.parent = parent
    sa_bl.props(o, facility_id=facility, sa_stage="W2.5 wear pass", sa_kind="decals", vertical=n_v, ground=n_h)
    return o
