"""Read-only audit of the W3 slice for the W3.2.x corrective patch (never saves the .blend).

Run: blender -b SantaAurora_W3_VerticalSlice.blend --python Tools/Blender/audit_w32x_corridor.py -- --root . --out report.json [--only cars,roofs,...]

cars:   wheel-corner clearance of every parked vehicle against the road/terrain surface under it (buried > 6 cm, floating > 6 cm, roll/pitch).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".")
ap.add_argument("--out", required=True)
ap.add_argument("--only", default="cars")
opt = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
only = set(opt.only.split(","))
report = {"blend": Path(bpy.data.filepath).name}


def world_mesh(objs):
    deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in objs:
        ev = o.evaluated_get(deps)
        me = ev.to_mesh()
        me.transform(o.matrix_world)
        bm.from_mesh(me)
        ev.to_mesh_clear()
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def layer_objects(layer):
    return [o for o in bpy.data.objects if o.get("sa_layer") == layer and o.library is None and o.type == "MESH"]


def surface_z(tree, x, y, ztop):
    """Highest road/terrain hit under (x, y) below ztop."""
    hit = tree.ray_cast(Vector((x, y, ztop)), Vector((0, 0, -1)), 8.0)
    return hit[0].z if hit[0] is not None else None


if "cars" in only:
    ground = world_mesh(layer_objects("Roads") + layer_objects("Terrain"))
    cars = [o for o in bpy.data.objects if o.get("sa_kind") == "vehicle" and o.library is None]
    stats = {"count": len(cars), "buried": 0, "floating": 0, "tilted": 0, "no_surface": 0, "worst": []}
    for o in cars:
        bb = [Vector(c) for c in o.bound_box]
        xs, ys = [c.x for c in bb], [c.y for c in bb]
        zmin = min(c.z for c in bb)
        lx, ly = (max(xs) - min(xs)), (max(ys) - min(ys))
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        pts = [(cx + sx * lx * .36, cy + sy * ly * .42) for sx in (-1, 1) for sy in (-1, 1)]   # wheel contact patches
        worst_gap, ok = 0.0, True
        gaps = []
        for px, py in pts:
            w = o.matrix_world @ Vector((px, py, zmin))
            z = surface_z(ground, w.x, w.y, w.z + 2.0)
            if z is None:
                ok = False
                break
            gaps.append(z - w.z)            # > 0: wheel below the surface (buried); < 0: wheel above it (floating)
        if not ok:
            stats["no_surface"] += 1
            continue
        lo, hi = min(gaps), max(gaps)
        if hi > .06:
            stats["buried"] += 1
        if lo < -.06:
            stats["floating"] += 1
        if hi - lo > .12:
            stats["tilted"] += 1
        stats["worst"].append((round(max(abs(hi), abs(lo)), 3), o.name, round(lo, 3), round(hi, 3)))
    stats["worst"].sort(reverse=True)
    stats["worst"] = stats["worst"][:15]
    report["cars"] = stats

ROOF_PREFIX = ("ACC_w32_", "ACC_w31_platibanda", "ACC_w31_cond_rack", "ACC_tank", "ACC_solar", "ACC_antenna", "ACC_dish", "ACC_roofroom")

if "roofs" in only:
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    seen, floating, sunk, total, rows = {}, 0, 0, 0, []
    import random
    cand = [(inst.object.name, inst.matrix_world.copy(), [Vector(c) for c in inst.object.bound_box]) for inst in deps.object_instances
            if inst.is_instance and inst.object.name.startswith(ROOF_PREFIX)
            and -3000 <= inst.matrix_world.translation.x <= -2250 and -2500 <= inst.matrix_world.translation.y <= -1250]
    random.Random(7).shuffle(cand)
    for name_, mw, bb in cand[:700]:
        zmin = min(c.z for c in bb)
        xs, ys = [c.x for c in bb], [c.y for c in bb]
        cxy = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
        samples = [cxy] + [(min(xs) + (max(xs) - min(xs)) * a_, min(ys) + (max(ys) - min(ys)) * b_) for a_ in (.2, .8) for b_ in (.2, .8)]
        gaps = []
        for sx, sy in samples:
            base = mw @ Vector((sx, sy, zmin))
            ok, loc, nrm, idx, hit_ob, _m = scene.ray_cast(deps, base + Vector((0, 0, .25)), Vector((0, 0, -1)), distance=2.0)
            if ok:
                gaps.append(base.z - loc.z)
            else:                                    # nothing below: a piece buried in a pitched roof has the roof ABOVE its base
                up, uloc, _n, _i, _o, _mm = scene.ray_cast(deps, base, Vector((0, 0, 1)), distance=3.0)
                gaps.append(-0.5 if up else None)
        total += 1
        vals = [g_ for g_ in gaps if g_ is not None]
        if not vals or all(g_ > .08 for g_ in vals):             # every base sample sits more than 8 cm above its support (or has none): floating
            floating += 1
            if len(rows) < 25:
                rows.append((name_, [None if g_ is None else round(g_, 2) for g_ in gaps], tuple(round(v, 1) for v in mw.translation)))
    report["roofs"] = {"pieces": total, "floating": floating, "examples": rows}

Path(opt.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: (v if k != "cars" else {kk: vv for kk, vv in v.items() if kk != "worst"}) for k, v in report.items()}))
