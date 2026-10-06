"""Generate the metric Santa Aurora masterplan, revision W1.5, from the shared layout.

Run:
blender --background --factory-startup --python Tools/Blender/create_santa_aurora_masterplan.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/World/SantaAurora_Masterplan_v1_5.blend   (the W1 file SantaAurora_Masterplan_v1.blend is kept untouched)
ArtSource/Blender/World/masterplan_generation_report.json

The masterplan is planning geometry for the whole 8x8 km city (massing level). Production art of each district
follows the Old Town pipeline (Tools/Blender/create_oldtown_base.py) and the Art Bible: never low-poly as final.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
import sa_materials  # noqa: E402
from masterplan_layout import Layout, load_registry, load_spec  # noqa: E402
from sa_geom import dist, lerp, norm, perp, resample  # noqa: E402
from sa_geom import sub as vsub  # noqa: E402
from sa_terrain import BANK_OUTER, COAST_PROMENADE_DZ, WATER_LEVEL, shore_z  # noqa: E402
from urban_fabric import STREET, carriageway  # noqa: E402

world_dir = root / "ArtSource" / "Blender" / "World"
spec = load_spec(root)
layout = Layout(spec, load_registry(root), root=root)
report_layout = layout.checks()
if layout.errors:
    raise RuntimeError("layout invalid; run Tools/Map/validate_masterplan.py:\n" + "\n".join(layout.errors[:30]))
T = layout.terrain

sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "SantaAurora_W1_5"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0
lib = sa_materials.build_library()
if "fachada_cortina" not in lib:
    lib["fachada_cortina"] = sa_materials.build_material("fachada_cortina", {
        "family": "vidro", "c1": (.26, .34, .40), "c2": (.18, .24, .30), "rough": (.08, .2), "scale": 1.0, "bump": .2, "pattern": "tiles",
        "tile": (1.5, 3.8, .06), "mortar": (.55, .57, .58), "metal": .4, "grime": .2, "dirt": 0.0, "spec": .8, "texel": 256})

C = {name: sa_bl.collection(name) for name in ("00_Terrain", "01_Water", "02_Roads", "03_Rail", "04_Fabric", "05_Campaign_Locations",
                                              "06_Life_Economy_Locations", "07_Vegetation", "08_Labels", "09_Streaming_Guides", "10_Cameras",
                                              "11_Streaming_Subgrid", "12_Library")}
C["11_Streaming_Subgrid"].hide_render = True
C["12_Library"].hide_render = True
wx0, wz0, wx1, wz1 = layout.world


def cell_of(x, y):
    return int((x - wx0) // 1000), int((y - wz0) // 1000)


def cell_name(ix, iz):
    return f"SA_M{ix:02d}_{iz:02d}"


# ---------------------------------------------------------------- terrain with zone tint + contours
ZONE_COL = {"old": (.50, .42, .32), "expansion": (.52, .50, .40), "civic": (.55, .53, .46), "corporate": (.46, .48, .50),
            "industrial": (.44, .41, .37), "technology": (.44, .50, .48), "reserve": (.30, .38, .22), "T_canal": (.34, .42, .26),
            "T_corp_tech": (.40, .47, .36)}
for z in layout.zones:
    ZONE_COL.setdefault(z["id"], (.48, .45, .38))


def ground_material():
    mat = bpy.data.materials.new("MP_Ground_Relief")
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "zone_col"
    attr.attribute_type = "GEOMETRY"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Position"], sep.inputs["Vector"])
    lines = []
    for interval, width, strength in ((5.0, .06, .18), (25.0, .14, .35)):
        div = nt.nodes.new("ShaderNodeMath")
        div.operation = "DIVIDE"
        div.inputs[1].default_value = interval
        L.new(sep.outputs["Z"], div.inputs[0])
        fr = nt.nodes.new("ShaderNodeMath")
        fr.operation = "FRACT"
        L.new(div.outputs[0], fr.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath")
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = width / interval * 2.5
        L.new(fr.outputs[0], lt.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = strength
        L.new(lt.outputs[0], mul.inputs[0])
        lines.append(mul)
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    L.new(lines[0].outputs[0], add.inputs[0])
    L.new(lines[1].outputs[0], add.inputs[1])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(add.outputs[0], inv.inputs[1])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = .02
    L.new(geo.outputs["Position"], noise.inputs["Vector"])
    nmr = nt.nodes.new("ShaderNodeMapRange")
    nmr.inputs["To Min"].default_value = .85
    nmr.inputs["To Max"].default_value = 1.08
    L.new(noise.outputs["Fac"], nmr.inputs["Value"])
    m1 = nt.nodes.new("ShaderNodeVectorMath")
    m1.operation = "SCALE"
    L.new(attr.outputs["Color"], m1.inputs[0])
    L.new(inv.outputs[0], m1.inputs["Scale"])
    m2 = nt.nodes.new("ShaderNodeVectorMath")
    m2.operation = "SCALE"
    L.new(m1.outputs["Vector"], m2.inputs[0])
    L.new(nmr.outputs["Result"], m2.inputs["Scale"])
    L.new(m2.outputs["Vector"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = .95
    mat.diffuse_color = (.45, .43, .36, 1)
    mat["sa_status"] = "visualização de relevo/zonas do masterplan (não é material final)"
    return mat


ground_mat = ground_material()
STEP = 20.0
n = int((wx1 - wx0) // STEP)
H = [[T.ground(wx0 + i * STEP, wz0 + j * STEP) for j in range(n + 1)] for i in range(n + 1)]
ZC = {}
for i in range(n + 1):
    for j in range(n + 1):
        x, y = wx0 + i * STEP, wz0 + j * STEP
        dz_c = y - shore_z(x)
        if dz_c < COAST_PROMENADE_DZ - 8:                       # W4 coast: seabed, wet sand and dry sand (linear albedo)
            ZC[(i, j)] = (.20, .19, .15) if dz_c < -4 else (.24, .20, .15) if dz_c < 8 else (.46, .37, .23)
        elif dz_c < COAST_PROMENADE_DZ + 40:
            ZC[(i, j)] = (.40, .38, .34)
        elif T.canal_distance(x, y) < BANK_OUTER + 4:
            ZC[(i, j)] = (.46, .46, .44)
        else:
            ZC[(i, j)] = ZONE_COL.get(layout.zone_of((x, y)), (.45, .42, .35))
per = int(1000 // STEP)
for ix in range(8):
    for iz in range(8):
        verts, faces, cols = [], [], []
        idx = {}
        for i in range(ix * per, ix * per + per + 1):
            for j in range(iz * per, iz * per + per + 1):
                idx[(i, j)] = len(verts)
                verts.append((wx0 + i * STEP, wz0 + j * STEP, H[i][j]))
                cols.append(ZC[(i, j)])
        for i in range(ix * per, ix * per + per):
            for j in range(iz * per, iz * per + per):
                faces.append((idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]))
        me = bpy.data.meshes.new(f"Terrain_{cell_name(ix, iz)}")
        me.from_pydata(verts, [], faces)
        a = me.color_attributes.new("zone_col", "FLOAT_COLOR", "POINT")
        a.data.foreach_set("color", [c for col in cols for c in (*col, 1.0)])
        me.materials.append(ground_mat)
        o = bpy.data.objects.new(f"Terrain_{cell_name(ix, iz)}", me)
        C["00_Terrain"].objects.link(o)
        sa_bl.props(o, sa_layer="Terrain", sa_cell=cell_name(ix, iz))
ground_check = bpy.data.objects.new("World_Bounds_8km", None)
ground_check.empty_display_type = "CUBE"
ground_check.scale = (4000, 4000, 1)
C["00_Terrain"].objects.link(ground_check)
sa_bl.props(ground_check, facility_world_size_m=8000)

# ---------------------------------------------------------------- water: canal + retention basin (with retaining walls)
mb = sa_bl.MeshBuilder()
mb.ribbon([tuple(p) for p in spec["canal"]["points"]], 34.0, lambda x, y: WATER_LEVEL, lift=0.0, mat=0, step=10.0)
for osp in layout.open_spaces:
    if osp.get("kind") == "water":
        z0 = T.surface(osp["x"], osp["z"])
        mb.box(osp["x"], osp["z"], z0 - 3.0, osp["width"] - 2, osp["depth"] - 2, 2.2, 0)
        for (cx, cy, sx, sy) in ((osp["x"], osp["z"] - osp["depth"] / 2, osp["width"], .5), (osp["x"], osp["z"] + osp["depth"] / 2, osp["width"], .5),
                                 (osp["x"] - osp["width"] / 2, osp["z"], .5, osp["depth"]), (osp["x"] + osp["width"] / 2, osp["z"], .5, osp["depth"])):
            mb.box(cx, cy, z0 - 3.2, sx, sy, 4.0, 1)
mb_sea = sa_bl.MeshBuilder()
mb_sea.box(0, -6350.0, -2.0, 20000.0, 5300.0, 2.0, 0)                  # W4 sea at 0 m; the terrain profile hides its inland edge
sea_o = mb_sea.to_object("Sea_South", [lib["agua_mar"]], C["01_Water"])
sa_bl.props(sea_o, sa_layer="Terrain", sea_level_m=0.0, coast_id=spec["coast"]["id"])
water = mb.to_object("Water_Canal_and_Basin", [lib["agua_canal"], lib["concreto"]], C["01_Water"])
sa_bl.props(water, facility_id=spec["canal"]["id"], sa_layer="Terrain", water_level_m=WATER_LEVEL)

# ---------------------------------------------------------------- roads
ROAD_MATS = ["asfalto", "calcada", "grama", "sinalizacao_viaria", "meio_fio", "concreto", "asfalto_gasto"]
RM = {k: i for i, k in enumerate(ROAD_MATS)}
road_mbs = {}


def rmb(p):
    k = cell_of(*p)
    if k not in road_mbs:
        road_mbs[k] = sa_bl.MeshBuilder()
    return road_mbs[k]


zs = T.surface
for road in layout.roads:
    pts = road["points"]
    cls = road["class"]
    total = road["width"]
    roundabout = road.get("roundabout")
    sw = 0.0 if roundabout else STREET[cls]["sidewalk"]
    cw = total - 2 * sw
    for a, b in zip(pts, pts[1:]):
        mb = rmb(lerp(a, b, .5))
        mb.ribbon([a, b], cw, zs, lift=.12, mat=RM["asfalto"], step=12.0)
        if sw:
            for s_ in (1, -1):
                mb.ribbon([a, b], sw, zs, lift=.3, mat=RM["calcada"], step=12.0, offset=s_ * (cw / 2 + sw / 2))
        if cls == "arterial" and not roundabout:
            mb.ribbon([a, b], 3.0, zs, lift=.3, mat=RM["grama"], step=12.0)
        # lane dashes
        L = dist(a, b)
        u = norm(vsub(b, a))
        t = 1.0
        while t < L - 3:
            p = (a[0] + u[0] * t, a[1] + u[1] * t)
            q = (a[0] + u[0] * (t + 3), a[1] + u[1] * (t + 3))
            if cls == "arterial" and not roundabout:
                for s_ in (1, -1):
                    mb.ribbon([p, q], .15, zs, lift=.14, mat=RM["sinalizacao_viaria"], step=10, offset=s_ * 5.0)
            elif cls == "collector":
                mb.ribbon([p, q], .15, zs, lift=.14, mat=RM["sinalizacao_viaria"], step=10)
            t += 9.0
    # Bridge decks where the road spans the canal channel.
    for p in resample(pts, 6.0):
        if T.canal_distance(*p) < BANK_OUTER:
            mb = rmb(p)
            mb.box(p[0], p[1], zs(*p) - 1.3, total * .95, total * .95, 1.4, RM["concreto"])
for rb in layout.roundabouts:
    c = tuple(rb["centre"])
    mb = rmb(c)
    island = [(c[0] + (rb["radius"] - 6) * math.cos(2 * math.pi * k / 32), c[1] + (rb["radius"] - 6) * math.sin(2 * math.pi * k / 32)) for k in range(32)]
    mb.prism(island, zs(*c) - .5, .9, RM["grama"], side_mat=RM["meio_fio"])
for zid, edges in layout.local_edges.items():
    for a, b, cls in edges:
        mb = rmb(lerp(a, b, .5))
        cw = carriageway(cls)
        sw = STREET[cls]["sidewalk"]
        mat = RM["asfalto_gasto"] if cls in ("local", "alley", "service", "industrial") else RM["asfalto"]
        if cls == "passage":
            mb.ribbon([a, b], 3.0, zs, lift=.2, mat=RM["calcada"], step=15.0)
            continue
        mb.ribbon([a, b], cw, zs, lift=.1, mat=mat, step=15.0)
        if sw:
            for s_ in (1, -1):
                mb.ribbon([a, b], sw, zs, lift=.22, mat=RM["calcada"], step=15.0, offset=s_ * (cw / 2 + sw / 2))
for dw in layout.driveways:
    mb = rmb(dw["a"])
    mb.ribbon([tuple(dw["b"]), tuple(dw["a"])], 8.0, zs, lift=.08, mat=RM["concreto"], step=10.0)
for (ix, iz), mb in road_mbs.items():
    o = mb.to_object(f"Roads_{cell_name(ix, iz)}", [lib[m] for m in ROAD_MATS], C["02_Roads"])
    sa_bl.props(o, sa_layer="Roads", sa_cell=cell_name(ix, iz))
for road in layout.roads:
    sa_bl.props(bpy.data.objects.new(f"{road['id']}_{road['name']}", None), road_id=road["base"], road_class=road["class"])
    e = bpy.data.objects[f"{road['id']}_{road['name']}"]
    e.location = (road["points"][len(road["points"]) // 2][0], road["points"][len(road["points"]) // 2][1], 10)
    e["centerline"] = json.dumps([[round(p[0], 1), round(p[1], 1)] for p in road["control"]])
    e["width_m"] = road["width"]
    C["02_Roads"].objects.link(e)

# ---------------------------------------------------------------- rail
mb = sa_bl.MeshBuilder()
for rail in layout.rails:
    g = rail["geom"]
    mb.ribbon(g, rail["width"] - 2, zs, lift=.35, mat=0, step=10.0)
    tracks = (-2.2, 2.2) if rail["kind"] == "main" else (0.0,)
    for tr in tracks:
        for s_ in (-.72, .72):
            mb.ribbon(g, .1, zs, lift=.55, mat=1, step=10.0, offset=tr + s_)
rail_obj = mb.to_object("Rail_Network", [lib["lastro_ferroviario"], lib["trilho_aco"]], C["03_Rail"])
sa_bl.props(rail_obj, sa_layer="Roads", railways=",".join(r["id"] for r in layout.rails))

# ---------------------------------------------------------------- fabric (all buildings) merged per macro cell and material
FAB_MATS = ["reboco_pintado", "concreto_pintado", "concreto", "fachada_cortina", "telha_metalica", "metal_galvanizado", "reboco_antigo",
            "ceramica_telha", "grama", "asfalto_gasto", "terra", "calcada"]
FM = {k: i for i, k in enumerate(FAB_MATS)}
FAMILY_MAT = {"house_low": "reboco_pintado", "row_mixed": "reboco_pintado", "shop_row": "reboco_pintado", "mid_res": "concreto_pintado",
              "condo_slab": "concreto_pintado", "tower_res": "concreto_pintado", "office_mid": "concreto", "office_tower": "fachada_cortina",
              "institutional": "concreto", "campus_lab": "concreto_pintado", "campus_tower": "fachada_cortina", "depot": "concreto_pintado",
              "service_shed": "concreto_pintado", "industrial_lot": "concreto_pintado", "small_factory": "concreto_pintado"}
fab_mbs = {}


def fmb(p):
    k = cell_of(*p)
    if k not in fab_mbs:
        fab_mbs[k] = sa_bl.MeshBuilder()
    return fab_mbs[k]


def base_z(obb):
    return min(zs(*q) for q in obb.corners())


counted = 0
for b in layout.buildings:
    if b["kind"] == "pad":
        continue
    o = b["obb"]
    mb = fmb(o.c)
    z0 = base_z(o) - 1.0
    mat = FM[FAMILY_MAT.get(b["family"], "concreto_pintado")]
    if b["kind"] in ("shed",):
        mat = FM["concreto_pintado"]
    if b["kind"] == "dock":
        mat = FM["concreto"]
    if b["kind"] == "podium":
        mat = FM["concreto"]
    mb.obb_box(o.corners(), z0, b["h"] + 1.0, mat)
    if b["kind"] == "shed":
        cs = o.corners()
        mb.add_face([(q[0], q[1], z0 + b["h"] + 1.0 + .02) for q in cs], FM["telha_metalica"])
    counted += 1
for c in layout.cylinders:
    mb = fmb(c["centre"])
    z0 = zs(*c["centre"]) - .5
    mb.cylinder(c["centre"][0], c["centre"][1], z0, c["r"], c["h"] + .5, 16 if c["kind"] != "chimney" else 12,
                FM["metal_galvanizado"] if c["kind"] != "chimney" else FM["concreto"])
    counted += 1
for lot in layout.oldtown.lots:
    if lot["family"] in ("vacant", "parking"):
        continue
    o = lot["obb"]
    mb = fmb(o.c)
    z0 = base_z(o) - 1.0
    roofed = lot["family"] in ("casa_terrea", "sobrado_estreito")
    mb.obb_box(o.corners(), z0, lot["height"] + 1.0, FM["reboco_antigo"], top=not roofed)
    if roofed:
        cs = o.corners()
        zt = z0 + lot["height"] + 1.0
        mid_a = lerp(cs[0], cs[1], .5)
        mid_b = lerp(cs[3], cs[2], .5)
        ridge = (zt + o.hd * .3 * 2)
        # gable with ridge along the street (cs[0]-cs[1] is the front edge)
        ra, rb_ = lerp(cs[0], cs[3], .5), lerp(cs[1], cs[2], .5)
        mb.add_face([(cs[0][0], cs[0][1], zt), (cs[1][0], cs[1][1], zt), (rb_[0], rb_[1], zt + o.hd * .3), (ra[0], ra[1], zt + o.hd * .3)], FM["ceramica_telha"])
        mb.add_face([(cs[2][0], cs[2][1], zt), (cs[3][0], cs[3][1], zt), (ra[0], ra[1], zt + o.hd * .3), (rb_[0], rb_[1], zt + o.hd * .3)], FM["ceramica_telha"])
    counted += 1
for pad in layout.open_pads:
    o = pad["obb"]
    mb = fmb(o.c)
    mat = {"green": "grama", "sports": "grama", "parking_lot": "asfalto_gasto", "vacant": "terra", "yard": "calcada", "truck_parking": "asfalto_gasto"}.get(pad["kind"], "calcada")
    mb.obb_box(o.corners(), base_z(o) - .3, .45, FM[mat])
for (ix, iz), mb in fab_mbs.items():
    o = mb.to_object(f"Fabric_{cell_name(ix, iz)}", [lib[m] for m in FAB_MATS], C["04_Fabric"])
    sa_bl.props(o, sa_layer="Architecture", sa_cell=cell_name(ix, iz))

# ---------------------------------------------------------------- campaign + life locations (individual objects with IDs)
registry = {l["id"]: l for l in layout.registry.get("locations", [])}
HERO_MATS = [lib["reboco_pintado"], lib["concreto"]]
pri_mat = {"hero": sa_materials.build_material("MP_Hero_Highlight", dict(sa_materials.LIB["pintura_industrial"], c1=(.85, .48, .12), c2=(.75, .40, .10))),
           "super": sa_materials.build_material("MP_SuperHero_Highlight", dict(sa_materials.LIB["pintura_industrial"], c1=(.78, .18, .10), c2=(.66, .14, .08))),
           "a": sa_materials.build_material("MP_Campaign_Highlight", dict(sa_materials.LIB["pintura_industrial"], c1=(.20, .46, .58), c2=(.16, .38, .48)))}
life_mat = sa_materials.build_material("MP_Life_Highlight", dict(sa_materials.LIB["pintura_industrial"], c1=(.25, .72, .32), c2=(.2, .6, .26)))
for loc in layout.campaign:
    p = loc["priority"].lower()
    key = "super" if p.startswith("super") else "hero" if p == "hero" else "a"
    r = layout.campaign_rects[loc["id"]]
    zc = max(zs(r[0], r[1]), zs(r[2], r[1]), zs(r[2], r[3]), zs(r[0], r[3]))
    mb = sa_bl.MeshBuilder()
    mb.box(loc["x"], loc["z"], zc - 2.0, loc["width"], loc["depth"], 2.2, 1)
    pad = mb.to_object("LOC_" + loc["id"], HERO_MATS, C["05_Campaign_Locations"])
    sa_bl.props(pad, facility_id=loc["id"], district=loc["district"], priority=loc["priority"], footprint_m=[loc["width"], loc["depth"]],
                access_road=layout.access[loc["id"]]["road"], sa_layer="Architecture")
    if loc["id"] in registry:
        pad["visible_floors"] = registry[loc["id"]].get("visibleFloors", 0)
        pad["chapters"] = ",".join(registry[loc["id"]].get("chapters", []))
    mb = sa_bl.MeshBuilder()
    for v in layout.campaign_volumes(loc):
        if v["role"].startswith("service_tunnel"):
            continue
        mb.box(v["x"], v["z"], zc, v["w"], v["d"], v["h"], 0)
    vo = mb.to_object(f"LOC_{loc['id']}__massing", [pri_mat[key]], C["05_Campaign_Locations"])
    sa_bl.props(vo, facility_id=loc["id"], sa_layer="Architecture")
for loc in layout.life:
    zc = zs(loc["x"], loc["z"])
    mb = sa_bl.MeshBuilder()
    h = 13.0 if loc["id"] == "home.starter" else 9.0
    mb.box(loc["x"], loc["z"], zc - 1, 20, 20, h + 1, 0)
    mb.cylinder(loc["x"], loc["z"], zc + h, 1.2, 40, 8, 0)
    o = mb.to_object("LIFE_" + loc["id"], [life_mat], C["06_Life_Economy_Locations"])
    sa_bl.props(o, facility_id=loc["id"], district=loc["district"], access_road=layout.access[loc["id"]]["road"], sa_layer="Gameplay")

# ---------------------------------------------------------------- vegetation (GN instances per macro cell)
tmp = sa_bl.collection("tmp_trees", C["12_Library"], hide_render=True)
trees = []
for name, h, r in (("MP_Tree_A", 7.0, 2.8), ("MP_Tree_B", 10.0, 3.6)):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=__import__("mathutils").Matrix.Translation((0, 0, h * .7)))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    mb = sa_bl.MeshBuilder()
    mb.cylinder(0, 0, 0, .2, h * .6, 6, 0)
    trunk = mb.to_object(name + "_trunk", [lib["tronco"]], tmp)
    crown = bpy.data.objects.new(name, me)
    me.materials.append(lib["folhagem"])
    tmp.objects.link(crown)
    trunk.parent = crown
    with bpy.context.temp_override(active_object=crown, selected_editable_objects=[crown, trunk], selected_objects=[crown, trunk]):
        bpy.ops.object.join()
    trees.append(crown)
tree_lib, tree_idx = sa_bl.library_collection("MP_Lib_Trees", trees, C["12_Library"])
bpy.data.collections.remove(tmp)
tree_cells = {}
for (x, y, s, kind) in layout.trees:
    k = cell_of(x, y)
    tree_cells.setdefault(k, []).append((x, y, zs(x, y), 1 if s > 1.1 else 0, (x * 1.7 + y) % 6.28, s * (.75 if kind == "old" else 1.0)))
for (ix, iz), pts in tree_cells.items():
    o = sa_bl.point_cloud_object(f"Vegetation_{cell_name(ix, iz)}", pts, tree_lib, C["07_Vegetation"])
    sa_bl.props(o, sa_layer="Vegetation", sa_cell=cell_name(ix, iz), blockout_vegetation=True)

# ---------------------------------------------------------------- labels, streaming guides, cameras


def label(text, x, y, z, size, coll):
    cu = bpy.data.curves.new("L_" + text, "FONT")
    cu.body = text
    cu.align_x = cu.align_y = "CENTER"
    cu.size = size
    cu.extrude = size * .02
    o = bpy.data.objects.new("Label_" + text, cu)
    o.location = (x, y, z)
    cu.materials.append(lib["sinalizacao_viaria"])
    coll.objects.link(o)
    return o


for d in spec["districts"]:
    cx, cy = d["center"]
    label(d["name"], cx, cy, zs(cx, cy) + 250, 110, C["08_Labels"])
for z in layout.zones:
    x0, y0, x1, y1 = z["bounds"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    label(z["name"].split(" (")[0], cx, cy, zs(cx, cy) + 180, 40, C["08_Labels"])
for loc in layout.campaign:
    label(loc["id"], loc["x"], loc["z"] - loc["depth"] / 2 - 30, zs(loc["x"], loc["z"]) + 90, 30, C["08_Labels"])
mb = sa_bl.MeshBuilder()
for x in range(wx0, wx1 + 1, 1000):
    mb.ribbon([(x, wz0), (x, wz1)], 8, lambda a, b: 0.0, lift=95.0, step=1000)
for y in range(wz0, wz1 + 1, 1000):
    mb.ribbon([(wx0, y), (wx1, y)], 8, lambda a, b: 0.0, lift=95.0, step=1000)
grid_mat = sa_materials.build_material("MP_Grid", dict(sa_materials.LIB["pintura_industrial"], c1=(.95, .85, .15), c2=(.9, .8, .1)))
mb.to_object("GRID_Macro_1km", [grid_mat], C["11_Streaming_Subgrid"])
mb = sa_bl.MeshBuilder()
for x in range(wx0, wx1 + 1, 250):
    if (x - wx0) % 1000:
        mb.ribbon([(x, wz0), (x, wz1)], 3, lambda a, b: 0.0, lift=94.0, step=1000)
for y in range(wz0, wz1 + 1, 250):
    if (y - wz0) % 1000:
        mb.ribbon([(wx0, y), (wx1, y)], 3, lambda a, b: 0.0, lift=94.0, step=1000)
mb.to_object("GRID_Sub_250m", [grid_mat], C["11_Streaming_Subgrid"])
for ix in range(8):
    for iz in range(8):
        name = cell_name(ix, iz)
        cx, cy = wx0 + ix * 1000 + 500, wz0 + iz * 1000 + 500
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "CUBE"
        e.empty_display_size = 500
        e.location = (cx, cy, 0)
        e["streaming_cell"] = name
        e["zone_owner"] = layout.zone_of((cx, cy))
        C["09_Streaming_Guides"].objects.link(e)
        label(name, cx - 380, cy + 450, 100, 34, C["11_Streaming_Subgrid"])

cams = C["10_Cameras"]
sa_bl.camera("CAM_World_Top", cams, (0, 0, 9000), rot=(0, 0, 0), ortho=8400, clip=(10, 20000))
sa_bl.camera("CAM_World_Oblique", cams, (-3800, -7600, 3600), target=(0, -300, 0), lens=30, clip=(10, 30000))
TILT = math.radians(35)
views = {"old": (-2500, -1950, 3200), "expansion": (150, -2200, 3200), "industrial": (-2350, 2000, 3400), "corporate": (2500, -150, 3000),
         "technology": (2400, 2400, 3200), "civic": (0, 400, 2600)}
for did, (cx, cy, span) in views.items():
    dist_ = 6000
    sa_bl.camera("CAM_District_" + did, cams, (cx, cy - dist_ * math.sin(TILT), zs(cx, cy) + dist_ * math.cos(TILT)), rot=(TILT, 0, 0), ortho=span,
                 clip=(10, 20000))
sa_bl.camera("CAM_Skyline", cams, (-1300, -3700, 260), target=(2300, 300, 60), lens=38, clip=(5, 20000))
sa_bl.camera("CAM_Transition_OldExp", cams, (-1050, -3150, 260), target=(-1050, -1950, 15), lens=30, clip=(5, 20000))
sa_bl.camera("CAM_Industrial_Low", cams, (-1500, 900, 160), target=(-2400, 2000, 15), lens=32, clip=(5, 20000))
# W2.5: relief view from the south edge of the Old Town over the córrego valley (R02) down to the drainage canal in the north.
sa_bl.camera("CAM_World_OldTown_Canal", cams, (-2950, -3500, 260), target=(-2550, 2600, 0), lens=34, clip=(5, 20000))
sa_bl.sun_and_sky(scene, cams)
scene.camera = bpy.data.objects["CAM_World_Oblique"]
scene.render.engine = "BLENDER_EEVEE"

scene["facility_world"] = "Santa Aurora"
scene["facility_masterplan_schema"] = spec["schemaVersion"]
scene["facility_world_size_m"] = 8000
scene["facility_revision"] = "W1.5"
scene["facility_blockout_only"] = True
output = world_dir / "SantaAurora_Masterplan_v1_5.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
rep = {
    "blend": output.relative_to(root).as_posix(),
    "previousRevisionKept": "ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend",
    "blenderVersion": bpy.app.version_string,
    "revision": "W1.5",
    "units": "meters",
    "worldSizeMeters": [wx1 - wx0, wz1 - wz0],
    "objectCount": len(bpy.data.objects),
    "collectionObjectCounts": {c.name: len(c.all_objects) for c in scene.collection.children},
    "fabricVolumes": counted,
    "trees": len(layout.trees),
    "layout": {k: v for k, v in report_layout.items() if k not in ("access", "oldTown")},
    "status": "W1.5 masterplan - planning geometry, not final art",
}
(world_dir / "masterplan_generation_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("SANTA AURORA MASTERPLAN W1.5 GENERATED", json.dumps({k: rep[k] for k in ("blend", "objectCount", "fabricVolumes")}))
