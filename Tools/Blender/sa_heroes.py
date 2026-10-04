"""Old Town hero locations, W1.5 advanced architecture base (requires bpy).

Reads ArtSource/Blender/World/OldTown/oldtown_heroes_v1.json and builds, per hero:
- per-floor shell objects (exterior walls with real openings + floor slab + interior partitions of that floor),
- roof object (+ roof items), canopies, porticos, awnings, front walls/gates, forecourt paving and stall markings,
- gameplay markers (entrances, service, parking, state slots H0-H4 / G0-G4, permanent items) as empties.
Geometry is bevelled (LOD0 base). Interiors are only the spaces needed to validate gameplay space.
"""
import math
import random

import bpy

import sa_arch
from sa_arch import S, WALL_T, Facade, openings_for, roof
from sa_bl import MeshBuilder, bevelled_object, collection, props

FRONT_ROT = {"S": 0.0, "N": math.pi, "E": math.pi / 2, "W": -math.pi / 2}
FACADE_BY_KEY = {"reboco_antigo": "reboco_antigo", "reboco_pintado": "reboco_pintado", "reboco_pastilha": "reboco_pastilha",
                 "tijolo_pintado": "tijolo_pintado", "tijolo_aparente": "tijolo_aparente", "concreto_pintado": "concreto_pintado",
                 "pedra_reboco_historico": "pedra_reboco_historico"}
ROOF_MAT = {"flat_parapet": "concreto", "hip": "ceramica_telha", "gable_side": "ceramica_telha", "gable_metal_parapet": "telha_metalica",
            "sawtooth": "telha_fibrocimento", "barrel": "telha_metalica"}


class Frame:
    """Local building frame (front facade at -Y) placed in the world at centre c, rotation rot, base z."""

    def __init__(self, rect, front, z):
        x0, y0, x1, y1 = rect
        self.c = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.rot = FRONT_ROT[front]
        if front in ("N", "S"):
            self.w, self.d = x1 - x0, y1 - y0
        else:
            self.w, self.d = y1 - y0, x1 - x0
        self.z = z
        self.cs, self.sn = math.cos(self.rot), math.sin(self.rot)

    def to_world(self, p):
        x, y, z = p
        return (self.c[0] + x * self.cs - y * self.sn, self.c[1] + x * self.sn + y * self.cs, self.z + z)

    def to_local(self, p):
        dx, dy = p[0] - self.c[0], p[1] - self.c[1]
        return (dx * self.cs + dy * self.sn, -dx * self.sn + dy * self.cs)


def transformed(mb, frame):
    out = MeshBuilder()
    out.verts = [frame.to_world(v) for v in mb.verts]
    out.faces = list(mb.faces)
    out.mats = list(mb.mats)
    return out


def fixed(lib, name):
    """Hero buildings are split per floor: use an untinted copy so every floor of one building has the same colour."""
    import sa_materials
    spec = sa_materials.LIB.get(name)
    if not spec or not spec.get("tint"):
        return lib[name]
    key = name + "_hero"
    if key not in lib:
        s2 = dict(spec)
        s2.pop("tint")
        lib[key] = sa_materials.build_material(key, s2)
    return lib[key]


def slot_mats(lib, facade="reboco_antigo", roof_mat="concreto", frame_mat="madeira_pintada", door="madeira_pintada"):
    return [fixed(lib, facade), lib["concreto_pintado"], lib[frame_mat], lib["vidro"], lib[roof_mat], lib["concreto"], lib[door],
            lib["metal_galvanizado"], lib["plastico"], lib["ferrugem"], lib["vidro_vitrine"], lib["tijolo_aparente"]]


def entrance_kind(role):
    r = role.lower()
    if "rollup" in r or "vehicle_gate" in r or r.startswith("box_") or "loading" in r or "vehicle_passage" in r:
        return "rollup"
    if "shop_main" in r:
        return "shopfront"
    return "door"


def facade_openings(L, floors, gh, fh, ents, rng, office=False, tall=False):
    """ents: [(u, w, h, kind)] on this facade's ground floor."""
    bands = []
    z = 0.0
    for f in range(floors):
        h = gh if f == 0 else fh
        ops = []
        if f == 0:
            for u, w, hh, kind in ents:
                ops.append({"u0": max(.3, u - w / 2), "u1": min(L - .3, u + w / 2), "zb": 0.0,
                            "zt": min(h - .4, hh if hh else (2.2 if kind == "door" else 3.6)), "kind": kind})
        spacing = 3.0 if not office else 2.6
        if tall:
            spacing = 4.6
        n = max(1, int(L // spacing))
        ww = 1.4 if not office else 1.8
        if tall:
            ww = 1.6
        for k in range(n):
            cu = (k + .5) * L / n
            if any(abs(cu - (o["u0"] + o["u1"]) / 2) < (o["u1"] - o["u0"]) / 2 + ww / 2 + .4 for o in ops):
                continue
            if cu - ww / 2 < .4 or cu + ww / 2 > L - .4:
                continue
            sill = 1.0 if not office else .85
            wh = 1.3 if not office else 1.6
            if tall:
                sill, wh = .7, min(h - 1.2, 2.8)
            ops.append({"u0": cu - ww / 2, "u1": cu + ww / 2, "zb": z + sill, "zt": z + sill + wh, "kind": "window"})
        bands.append((z, z + h, ops))
        z += h
    return bands


def emit_floor_band(fac, band, rng, style):
    z0, z1, ops = band
    fac.wall_band(z0, z1, ops)
    for o in ops:
        k = o["kind"]
        if k == "window":
            fac.window(o, trim=style.get("trim", False), grille=style.get("grille", False) and z0 < .1)
        elif k == "door":
            fac.door(o, transom=style.get("transom", False))
        elif k == "shopfront":
            fac.shopfront(o, rng)
        elif k == "rollup":
            fac.rollup(o)


def partitions(mb, rooms, z0, h, door_side_toward=None, t=.12, skip=("living_sleep", "desk_corner", "kitchenette", "garage_bay",
                                                                         "workshop_bench_area", "stock", "salao", "workstations", "boxes", "plateia", "foyer", "palco")):
    for r in rooms:
        if r["role"] in skip:
            continue
        x0, y0, x1, y1 = r["rect"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # door gap on the side facing door_side_toward (local point) else the longest side
        sides = [("S", (cx, y0)), ("N", (cx, y1)), ("W", (x0, cy)), ("E", (x1, cy))]
        target = door_side_toward or (cx, cy - 100)
        door = min(sides, key=lambda s: (s[1][0] - target[0]) ** 2 + (s[1][1] - target[1]) ** 2)[0]
        for side, _ in sides:
            if side in ("S", "N"):
                y = y0 if side == "S" else y1
                if side == door and x1 - x0 > 1.6:
                    m = cx
                    mb.box((x0 + m - .45) / 2, y, z0, m - .45 - x0, t, h)
                    mb.box((m + .45 + x1) / 2, y, z0, x1 - m - .45, t, h)
                    mb.box(m, y, z0 + 2.1, .9, t, h - 2.1)
                else:
                    mb.box(cx, y, z0, x1 - x0, t, h)
            else:
                x = x0 if side == "W" else x1
                if side == door and y1 - y0 > 1.6:
                    m = cy
                    mb.box(x, (y0 + m - .45) / 2, z0, t, m - .45 - y0, h)
                    mb.box(x, (m + .45 + y1) / 2, z0, t, y1 - m - .45, h)
                    mb.box(x, m, z0 + 2.1, t, .9, h - 2.1)
                else:
                    mb.box(x, cy, z0, t, y1 - y0, h)


class HeroBuilder:
    def __init__(self, lib, terrain, kit, root_coll, marker_coll):
        self.lib = lib
        self.terrain = terrain
        self.kit = kit
        self.root = root_coll
        self.markers = marker_coll
        self.objects = []

    def ground_z(self, rect):
        x0, y0, x1, y1 = rect
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), ((x0 + x1) / 2, (y0 + y1) / 2)]
        return sum(self.terrain.surface(*p) for p in pts) / len(pts) + .12

    def obj(self, name, mb, mats, coll, bevel=.01, **meta):
        o = bevelled_object(name, mb, mats, coll, bevel=bevel)
        props(o, **meta)
        self.objects.append(o)
        return o

    def empty(self, name, loc, size=(1, 1, 1), shape="CUBE", **meta):
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = shape
        e.empty_display_size = .5
        e.location = loc
        e.scale = (max(size[0], .05) / 1.0, max(size[1], .05) / 1.0, max(size[2], .05) / 1.0)
        self.markers.objects.link(e)
        props(e, **meta)
        return e

    def build(self, hero, all_data):
        hid = hero["id"]
        coll = collection("HERO_" + hid, self.root)
        z = self.ground_z(hero["lot"])
        rng = random.Random(len(hid) * 131)
        # Lot platform (levelled) + forecourt paving; downhill side shows as a low retaining plinth.
        x0, y0, x1, y1 = hero["lot"]
        lowest = min(self.terrain.surface(x, y) for x in (x0, x1) for y in (y0, y1))
        mb = MeshBuilder()
        mb.box((x0 + x1) / 2, (y0 + y1) / 2, lowest - .6, x1 - x0, y1 - y0, z - lowest + .6 - .02, S["plinth"])
        plat = self.obj(f"HERO_{hid}__lot_platform", mb, slot_mats(self.lib, facade="calcada"), coll, bevel=.02,
                        facility_id=hid, sa_layer="Architecture", sa_part="lot_platform", ground_z=round(z, 2))
        for b in hero["buildings"]:
            self.building(hero, b, z, coll, rng)
        self.extras(hero, z, coll, rng)
        self.markers_for(hero, z)
        anchor = self.empty(f"HERO_{hid}", ((x0 + x1) / 2, (y0 + y1) / 2, z), (x1 - x0, y1 - y0, 1), "PLAIN_AXES",
                            facility_id=hid, sa_layer="Gameplay", sa_kind="hero_anchor", name_pt=hero["name"], front=hero["front"],
                            street=hero["street"], stage="S1 arquitetura base")
        return z

    def building(self, hero, b, z, coll, rng):
        hid = hero["id"]
        front = hero["front"]
        fr = Frame(b["rect"], front, z)
        w, d = fr.w, fr.d
        floors, fh, gh = b["floors"], b["fh"], b["ground_h"]
        H = gh + fh * (floors - 1)
        facade_mat = FACADE_BY_KEY.get(b.get("facade", "reboco_antigo"), "reboco_antigo")
        roof_kind = b["roof"]
        mats = slot_mats(self.lib, facade=facade_mat, roof_mat=ROOF_MAT.get(roof_kind, "concreto"),
                         frame_mat="aluminio" if hid in ("smalloffice", "horizonte") else "madeira_pintada",
                         door="aco_pintado_verde" if hid in ("garage", "workshop") else "madeira_pintada")
        # Entrances that sit on this building's front facade.
        ents_front = []
        for e in hero["entrances"]:
            lx, ly = fr.to_local(e["p"])
            if abs(ly + d / 2) < .8 and -w / 2 - .1 <= lx <= w / 2 + .1 and e["facing"] == front:
                ents_front.append((lx + w / 2, e.get("w", 1.0), e.get("h"), entrance_kind(e["role"])))
        office = hid in ("smalloffice",)
        style = {"trim": hid in ("horizonte", "apartments", "imperial", "restaurant"), "grille": hid in ("home.starter", "apartments", "grocery"),
                 "transom": hid in ("imperial", "restaurant")}
        if b.get("shopfront") and not any(k == "shopfront" for *_, k in ents_front):
            pass
        sides = {
            "front": (Facade(None, (-w / 2, -d / 2), (1, 0), (0, -1), w), ents_front),
            "back": (Facade(None, (w / 2, d / 2), (-1, 0), (0, 1), w), []),
            "right": (Facade(None, (w / 2, -d / 2), (0, 1), (1, 0), d), []),
            "left": (Facade(None, (-w / 2, d / 2), (0, -1), (-1, 0), d), []),
        }
        # Entrances on other facades (e.g. kitchen service door, rear loading, stage door).
        for e in hero["entrances"]:
            lx, ly = fr.to_local(e["p"])
            if abs(ly - d / 2) < .8 and abs(lx) <= w / 2:
                sides["back"][1].append((w / 2 - lx, e.get("w", 1.0), e.get("h"), entrance_kind(e["role"])))
            elif abs(lx - w / 2) < .8 and abs(ly) <= d / 2:
                sides["right"][1].append((ly + d / 2, e.get("w", 1.0), e.get("h"), entrance_kind(e["role"])))
            elif abs(lx + w / 2) < .8 and abs(ly) <= d / 2:
                sides["left"][1].append((d / 2 - ly, e.get("w", 1.0), e.get("h"), entrance_kind(e["role"])))
        bands = {}
        for key, (fac, ents) in sides.items():
            sparse = key != "front"
            bb = facade_openings(fac.L, floors, gh, fh, ents, rng, office=office, tall=(hid == "imperial"))
            if sparse and hid in ("garage", "workshop", "imperial"):
                bb = [(z0, z1, [o for o in ops if o["kind"] != "window"] + [o for i, o in enumerate(ops) if o["kind"] == "window" and i % 3 == 0])
                      for z0, z1, ops in bb]
            if b.get("shopfront") and key == "front":
                z0_, z1_, ops0 = bb[0]
                taken = [(o["u0"], o["u1"]) for o in ops0 if o["kind"] != "window"]
                ops0 = [o for o in ops0 if o["kind"] != "window"]
                u = .5
                for (a, c) in sorted(taken) + [(fac.L - .5, fac.L)]:
                    if a - u > 2.0:
                        ops0.append({"u0": u, "u1": a - .4, "zb": 0.0, "zt": min(gh - .5, 3.2), "kind": "shopfront"})
                    u = c + .4
                bb[0] = (z0_, z1_, ops0)
            bands[key] = bb
        role = b["role"]
        # Floors as separate objects (cut-away friendly).
        for f in range(floors):
            mb = MeshBuilder()
            for key, (fac0, _) in sides.items():
                fac = Facade(mb, fac0.o, fac0.u, (-fac0.n[0], -fac0.n[1]), fac0.L)
                emit_floor_band(fac, bands[key][f], rng, style)
            fz = 0.0 if f == 0 else gh + fh * (f - 1)
            mb.box(0, 0, fz - .2, w - 2 * WALL_T + .02, d - 2 * WALL_T + .02, .2, S["plinth"])
            if f == 0:
                mb.box(0, 0, -1.5, w + .06, d + .06, 1.5 + .4, S["plinth"], top=False)
            self.interior(hero, b, fr, f, fz, gh if f == 0 else fh, mb)
            self.obj(f"HERO_{hid}__{role}__F{f:02d}", transformed(mb, fr), mats, coll, facility_id=hid, sa_layer="Architecture",
                     sa_part=role, floor_index=f, floor_z=round(z + fz, 2))
        # Roof.
        mb = MeshBuilder()
        mb.box(0, 0, H - .2, w - 2 * WALL_T + .02, d - 2 * WALL_T + .02, .2, S["plinth"])
        parapet = 1.1 if roof_kind in ("gable_metal_parapet", "sawtooth") else 0.0
        rk = "gable_metal" if roof_kind == "gable_metal_parapet" else roof_kind
        attached = hid in ("grocery",)
        top = roof(mb, w, d, H, rk, rng, attached=attached, front_parapet=parapet)
        if style["trim"]:
            Facade(mb, (-w / 2, -d / 2), (1, 0), (0, -1), w).box(-.05, w + .05, H - .35, H, -.22, 0, S["trim"])
            z_ = gh
            for k in range(1, floors):
                Facade(mb, (-w / 2, -d / 2), (1, 0), (0, -1), w).box(-.02, w + .02, z_ - .08, z_ + .08, -.06, 0, S["trim"])
                z_ += fh
        self.obj(f"HERO_{hid}__{role}__ROOF", transformed(mb, fr), mats, coll, facility_id=hid, sa_layer="Architecture", sa_part=role + "_roof",
                 roof_top_z=round(z + top, 2))

    def interior(self, hero, b, fr, f, fz, h, mb):
        """Interior partitions (local frame) only where the hero JSON defines spaces for this floor."""
        it = hero.get("interior")
        if not it:
            return
        hid = hero["id"]

        def loc_rect(r):
            pts = [fr.to_local((r[0], r[1])), fr.to_local((r[2], r[3]))]
            return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]

        def in_building(r):
            x0, y0, x1, y1 = b["rect"]
            cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            return x0 <= cx <= x1 and y0 <= cy <= y1

        hh = h - .2
        if hid == "home.starter":
            if f == it["floor_index"] or f in (0, 2, 3):
                cr = loc_rect(it["corridor_rect"])
                # corridor walls on every floor
                mb.box(cr[0] - .06, (cr[1] + cr[3]) / 2, fz, .12, cr[3] - cr[1], hh, S["facade"])
                mb.box(cr[2] + .06, (cr[1] + cr[3]) / 2, fz, .12, cr[3] - cr[1], hh, S["facade"])
                st = loc_rect(it["stair_rect"])
                for k in range(16):
                    mb.box(st[0] + 1.2, st[1] + .3 + k * .26, fz + k * .1875, 2.2, .26, .1875, S["plinth"])
                mb.box((st[0] + st[2]) / 2, st[3] + .06, fz, st[2] - st[0], .12, hh, S["facade"])
                # unit separation walls (2 units per side)
                ur = loc_rect(it["unit_rect"])
                for xx in (ur[0] - .2,):
                    pass
                mb.box((-fr.w / 2 + cr[0]) / 2, ur[1] - .07, fz, cr[0] + fr.w / 2, .14, hh, S["facade"])
                mb.box((cr[2] + fr.w / 2) / 2, ur[1] - .07, fz, fr.w / 2 - cr[2], .14, hh, S["facade"])
            if f == it["floor_index"]:
                rooms = [{"role": r["role"], "rect": loc_rect(r["rect"])} for r in it["rooms"]]
                door_l = fr.to_local(it["door"]["p"])
                partitions(mb, rooms, fz, hh, door_side_toward=(door_l[0] - 3, door_l[1]))
                kit = loc_rect([r for r in it["rooms"] if r["role"] == "kitchenette"][0]["rect"])
                mb.box((kit[0] + kit[2]) / 2, (kit[1] + kit[3]) / 2, fz, kit[2] - kit[0], kit[3] - kit[1], .9, S["trim"])
            return
        if hid == "garage" and f == 0:
            rooms = [{"role": r["role"], "rect": loc_rect(r["rect"])} for r in it["rooms"]]
            partitions(mb, rooms, fz, 3.0, door_side_toward=(0, 0))
            mz = it["mezzanine_reserve"]
            r = loc_rect(mz["rect"])
            return
        if hid == "horizonte":
            if f == 0:
                rooms = [{"role": r["role"], "rect": loc_rect(r["rect"])} for r in it["ground"]]
                partitions(mb, rooms, fz, hh, door_side_toward=(0, 0), skip=("core_stair_elevator", "shaft_plumbing", "shaft_electrical", "cistern_lower"))
            if f == it["typical_floor_index"]:
                cor = loc_rect([r for r in it["typical_floor"] if r["role"] == "corridor"][0]["rect"])
                mb.box((cor[0] + cor[2]) / 2, cor[1] - .06, fz, cor[2] - cor[0], .12, hh, S["facade"])
                mb.box((cor[0] + cor[2]) / 2, cor[3] + .06, fz, cor[2] - cor[0], .12, hh, S["facade"])
                q = loc_rect([r for r in it["typical_floor"] if r["role"] == "quadro_tecnico"][0]["rect"])
                mb.box((q[0] + q[2]) / 2, (q[1] + q[3]) / 2, fz + 1.2, max(q[2] - q[0], .6), max(q[3] - q[1], .2), .9, S["metal"])
            # shafts and core run through every floor
            for r in it["ground"]:
                if r["role"] in ("core_stair_elevator", "shaft_plumbing", "shaft_electrical"):
                    lr = loc_rect(r["rect"])
                    for side in range(4):
                        x0, y0, x1, y1 = lr
                        if side == 0:
                            mb.box((x0 + x1) / 2, y0, fz, x1 - x0, .15, hh, S["plinth"])
                        elif side == 1:
                            mb.box((x0 + x1) / 2, y1, fz, x1 - x0, .15, hh, S["plinth"])
                        elif side == 2:
                            mb.box(x0, (y0 + y1) / 2, fz, .15, y1 - y0, hh, S["plinth"])
                        else:
                            mb.box(x1, (y0 + y1) / 2, fz, .15, y1 - y0, hh, S["plinth"])
            return
        if f == 0 and "rooms" in it:
            rooms = [{"role": r["role"], "rect": loc_rect(r["rect"])} for r in it["rooms"] if in_building(r["rect"])]
            partitions(mb, rooms, fz, min(hh, 3.2), door_side_toward=(0, 0))

    def extras(self, hero, z, coll, rng):
        hid = hero["id"]
        mats = slot_mats(self.lib, facade="reboco_antigo", roof_mat="concreto", frame_mat="aluminio")
        mb = MeshBuilder()
        top_of = {}
        for b in hero["buildings"]:
            top_of[b["role"]] = b["ground_h"] + b["fh"] * (b["floors"] - 1)
        Hmax = max(top_of.values())
        for it in hero.get("roof_items", []):
            x0, y0, x1, y1 = it["rect"]
            base = top_of.get(it.get("on"), Hmax)
            if it["role"].startswith("reservatorio") or it["role"] == "caixa_dagua":
                for px in (x0 + .3, x1 - .3):
                    for py in (y0 + .3, y1 - .3):
                        mb.box(px, py, z + base, .3, .3, 1.2, S["plinth"])
                mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + base + 1.2, x1 - x0, y1 - y0, it["h"], S["plinth"])
                mb.box(x1 - .4, (y0 + y1) / 2, z + base, .06, .5, 1.2 + it["h"] + .9, S["metal"])
            elif it["role"].startswith("hvac") or it["role"] == "condensers":
                mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + base, x1 - x0, y1 - y0, it["h"], S["sign"])
                for k in range(3):
                    mb.cylinder(x0 + (x1 - x0) * (k + .5) / 3, (y0 + y1) / 2, z + base + it["h"], min(x1 - x0, y1 - y0) * .14, .05, 16, S["metal"])
            else:
                mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + base, x1 - x0, y1 - y0, it["h"], S["facade"])
        if "canopy" in hero:
            x0, y0, x1, y1 = hero["canopy"]["rect"]
            h = hero["canopy"]["h"]
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + h, x1 - x0, y1 - y0, .25, S["trim"])
            for px in (x0 + .2, x1 - .2):
                mb.cylinder(px, y0 + .2, z, .1, h, 12, S["metal"])
        if "awning" in hero:
            x0, y0, x1, y1 = hero["awning"]["rect"]
            h = hero["awning"]["h"]
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + h, x1 - x0, y1 - y0, .08, S["sign"])
        if "portico" in hero:
            p = hero["portico"]
            x0, y0, x1, y1 = p["rect"]
            n = p["columns"]
            for k in range(n):
                cx = x0 + (x1 - x0) * k / (n - 1)
                mb.box(cx, (y0 + y1) / 2, z, 1.4, 1.4, .5, S["trim"])
                mb.cylinder(cx, (y0 + y1) / 2, z + .5, .5, p["h"] - 1.1, 20, S["facade"])
                mb.box(cx, (y0 + y1) / 2, z + p["h"] - .6, 1.3, 1.3, .6, S["trim"])
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, z + p["h"], x1 - x0 + 2, y1 - y0 + 1.2, 1.2, S["trim"])
            # pediment
            cy = y0 - .3
            mb.add_face([(x0 - 1, cy, z + p["h"] + 1.2), (x1 + 1, cy, z + p["h"] + 1.2), ((x0 + x1) / 2, cy, z + p["h"] + 5.0)], S["trim"])
            mb.add_face([(x1 + 1, y1, z + p["h"] + 1.2), (x0 - 1, y1, z + p["h"] + 1.2), ((x0 + x1) / 2, y1, z + p["h"] + 5.0)], S["roof"])
            mb.add_face([(x0 - 1, cy, z + p["h"] + 1.2), ((x0 + x1) / 2, cy, z + p["h"] + 5.0), ((x0 + x1) / 2, y1, z + p["h"] + 5.0), (x0 - 1, y1, z + p["h"] + 1.2)], S["roof"])
            mb.add_face([((x0 + x1) / 2, cy, z + p["h"] + 5.0), (x1 + 1, cy, z + p["h"] + 1.2), (x1 + 1, y1, z + p["h"] + 1.2), ((x0 + x1) / 2, y1, z + p["h"] + 5.0)], S["roof"])
        for sec in hero.get("secondary", []):
            x0, y0, x1, y1 = sec["rect"]
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, z, x1 - x0, y1 - y0, sec["h"], S["metal"])
        # Front boundary with gates for the Horizonte (grade + gates + intercom pillar).
        if hid == "horizonte":
            x0, y0, x1, y1 = hero["lot"]
            yb = y0 + .1
            # low wall segments between the vehicle gate (-2371..-2365.5), pedestrian gate (-2350.7..-2349.3) and the lot edge
            mb.box((-2365.5 + -2353.0) / 2, yb, z, 12.5, .25, .6, S["facade"])
            mb.box((-2347.0 + x1) / 2, yb, z, x1 - (-2347.0), .25, .6, S["facade"])
            for k in range(int((x1 - x0) / .15)):
                xx = x0 + k * .15
                if -2365 < xx < -2353 or -2347 < xx < x1:
                    mb.box(xx, yb, z + .6, .02, .02, 1.6, S["metal"])
            mb.box(-2352.5, yb, z, .45, .45, 1.6, S["facade"])
            mb.box(-2352.5, yb - .24, z + 1.2, .2, .04, .3, S["metal"])
        if hid == "garage":
            mb.box(-2706.15, -2147.0, z + 4.6, .1, 9.0, 1.1, S["sign"])
        if len(mb):
            self.obj(f"HERO_{hid}__details", mb, mats, coll, bevel=.008, facility_id=hid, sa_layer="Architecture", sa_part="details")
        # Gates from the kit (linked duplicates).
        if hid == "horizonte" and "KIT_Gate_Sliding_4m" in self.kit:
            g = self.kit["KIT_Gate_Sliding_4m"].copy()
            g.location = (-2370.5, hero["lot"][1] + .1, z)
            g.scale = (1.25, 1, 1)
            coll.objects.link(g)
            props(g, facility_id=hid, sa_layer="Architecture", sa_part="vehicle_gate")
            p = self.kit["KIT_Gate_Pedestrian_1m"].copy()
            p.location = (-2351.0, hero["lot"][1] + .1, z + .0)
            p.scale = (1.4, 1, 1)
            coll.objects.link(p)
            props(p, facility_id=hid, sa_layer="Architecture", sa_part="pedestrian_gate")
        # Parking stall markings and forecourt paving.
        mb = MeshBuilder()
        for pk in hero.get("parking", []):
            if pk.get("kind") not in ("car", "van", "truck", "dropoff"):
                continue
            x0, y0, x1, y1 = pk["rect"]
            gz = max(self.terrain.surface((x0 + x1) / 2, (y0 + y1) / 2), z - .2) + .03 if pk["kind"] != "van" else z + .02
            mb.box((x0 + x1) / 2, (y0 + y1) / 2, gz - .03, x1 - x0, y1 - y0, .03, S["plinth"])
            for xx in (x0, x1):
                mb.box(xx, (y0 + y1) / 2, gz, .1, y1 - y0, .012, S["sign"])
            for yy in (y0, y1):
                mb.box((x0 + x1) / 2, yy, gz, x1 - x0, .1, .012, S["sign"])
        if len(mb):
            self.obj(f"HERO_{hid}__parking", mb, slot_mats(self.lib, facade="asfalto_gasto"), coll, bevel=0.0, facility_id=hid,
                     sa_layer="Architecture", sa_part="parking")

    def markers_for(self, hero, z):
        hid = hero["id"]
        for e in hero["entrances"]:
            self.empty(f"GP_{hid}__entrance__{e['role']}", (e["p"][0], e["p"][1], z), (e.get("w", 1.0), .3, e.get("h", 2.2) or 2.2), "SINGLE_ARROW",
                       facility_id=hid, sa_layer="Gameplay", sa_kind="entrance", role=e["role"], facing=e["facing"])
        for s_ in hero.get("service", []):
            if "rect" in s_:
                x0, y0, x1, y1 = s_["rect"]
                self.empty(f"GP_{hid}__service__{s_['role']}", ((x0 + x1) / 2, (y0 + y1) / 2, z), (x1 - x0, y1 - y0, 3.0), "CUBE",
                           facility_id=hid, sa_layer="Gameplay", sa_kind="service", role=s_["role"])
        for pk in hero.get("parking", []):
            x0, y0, x1, y1 = pk["rect"]
            self.empty(f"GP_{hid}__parking__{pk['role']}", ((x0 + x1) / 2, (y0 + y1) / 2, z + pk.get("z", 0.0)), (x1 - x0, y1 - y0, 1.5), "CUBE",
                       facility_id=hid, sa_layer="Gameplay", sa_kind="parking", role=pk["role"], vehicle=pk["kind"], stalls=pk.get("stalls", 1))
        it = hero.get("interior") or {}
        floor_z = z
        if hid == "home.starter":
            floor_z = z + 3.0 * it.get("floor_index", 0)
        for state, items in (it.get("states") or {}).items():
            for name, (x, y, w, d, h) in items:
                self.empty(f"SLOT_{hid}__{state}__{name}", (x, y, floor_z + h / 2), (w, d, h), "CUBE",
                           facility_id=hid, sa_layer="Gameplay", sa_kind="state_slot", state=state, item=name)
        for name, (x, y, w, d, h) in it.get("permanent", []):
            self.empty(f"SLOT_{hid}__ALL__{name}", (x, y, floor_z + .9 + h / 2), (w, d, h), "CUBE",
                       facility_id=hid, sa_layer="Gameplay", sa_kind="permanent_item", item=name, note="Elemento permanente: primeira maleta de Guto")
        if hid == "home.starter":
            ur = it["unit_rect"]
            self.empty("GP_home.starter__spawn", ((ur[0] + ur[2]) / 2, (ur[1] + ur[3]) / 2, floor_z + .1), (.5, .5, .5), "ARROWS",
                       facility_id=hid, sa_layer="Gameplay", sa_kind="player_spawn", area_m2=it["area_m2"])
        # Visible blockout proxies of the initial state (H0 / G0) so captures can validate the space.
        first = {"home.starter": "H0", "garage": "G0"}.get(hid)
        if first and it.get("states"):
            mb = MeshBuilder()
            if hid == "home.starter":
                x0, y0, x1, y1 = it["unit_rect"]
                mb.box((x0 + x1) / 2, (y0 + y1) / 2, floor_z + .005, x1 - x0, y1 - y0, .02, 1)
            for name, (x, y, w, d, h) in it["states"][first] + [p_ for p_ in it.get("permanent", [])]:
                zb = floor_z + (.9 if any(name == q[0] for q in it.get("permanent", [])) else 0.0)
                if name in ("bare_bulb",):
                    zb = floor_z + 2.55
                mb.box(x, y, zb, w, d, h, 0 if name not in ("job_board",) else 2)
            o = bevelled_object(f"PROXY_{hid}__{first}", mb, [self.lib["madeira_crua"], self.lib["ceramica_piso"], self.lib["plastico"]],
                                self.markers, bevel=.01)
            props(o, facility_id=hid, sa_layer="Gameplay", sa_kind="state_proxy", state=first, sa_blockout=True,
                  note="Proxies de blockout para validar espaço; mobiliário final é arte W3/W4")
