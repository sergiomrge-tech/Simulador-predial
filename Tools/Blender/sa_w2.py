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
LAYERS = ("Shell", "Structure", "Interior", "Openings", "Services", "Props_G0", "Site", "Lighting", "Gameplay", "Cameras")


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

    def save(self, filename):
        self.scene.render.engine = "BLENDER_EEVEE"
        try:
            self.scene.eevee.use_raytracing = True
        except AttributeError:
            pass
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
