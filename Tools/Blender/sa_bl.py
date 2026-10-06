"""Blender helpers shared by the Santa Aurora W1.5 generators (requires bpy).

- MeshBuilder: accumulates geometry with per-face material slots and writes metric box-projected UVs
  (1 UV unit = 1 m) so every mesh is ready for portable PBR textures later.
- Primitive builders (boxes, bevelled boxes, cylinders, prisms, ribbons draped on terrain).
- Collections, custom properties and Geometry Nodes point instancing (one object per streaming cell).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


# ---------------------------------------------------------------- collections

def collection(name, parent=None, hide_render=False):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    c.hide_render = hide_render
    return c


def link(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.node_groups, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def props(obj, **kw):
    for k, v in kw.items():
        obj[k] = v
    return obj


# ---------------------------------------------------------------- mesh builder

class MeshBuilder:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.mats = []

    def __len__(self):
        return len(self.faces)

    def add_face(self, vs, mat=0):
        base = len(self.verts)
        self.verts.extend(vs)
        self.faces.append(tuple(range(base, base + len(vs))))
        self.mats.append(mat)

    def quad(self, a, b, c, d, mat=0):
        self.add_face([a, b, c, d], mat)

    def box(self, cx, cy, z0, sx, sy, sz, mat=0, rot=0.0, top=True, bottom=False, sides=True):
        """Axis box (optionally rotated about Z around its centre). Faces are separate (flat shading, clean UVs)."""
        hx, hy = sx / 2, sy / 2
        cs, sn = math.cos(rot), math.sin(rot)

        def P(x, y, z):
            return (cx + x * cs - y * sn, cy + x * sn + y * cs, z)

        z1 = z0 + sz
        c = [P(-hx, -hy, z0), P(hx, -hy, z0), P(hx, hy, z0), P(-hx, hy, z0), P(-hx, -hy, z1), P(hx, -hy, z1), P(hx, hy, z1), P(-hx, hy, z1)]
        if sides:
            self.quad(c[0], c[1], c[5], c[4], mat)
            self.quad(c[1], c[2], c[6], c[5], mat)
            self.quad(c[2], c[3], c[7], c[6], mat)
            self.quad(c[3], c[0], c[4], c[7], mat)
        if top:
            self.quad(c[4], c[5], c[6], c[7], mat)
        if bottom:
            self.quad(c[3], c[2], c[1], c[0], mat)

    def obb_box(self, corners, z0, h, mat=0, top=True):
        """Prism over 4 ground corners (counter-clockwise), from z0 to z0+h."""
        c = [(p[0], p[1], z0) for p in corners] + [(p[0], p[1], z0 + h) for p in corners]
        for i in range(4):
            j = (i + 1) % 4
            self.quad(c[i], c[j], c[4 + j], c[4 + i], mat)
        if top:
            self.quad(c[4], c[5], c[6], c[7], mat)

    def prism(self, poly, z0, h, mat=0, top=True, side_mat=None):
        n = len(poly)
        lo = [(p[0], p[1], z0) for p in poly]
        hi = [(p[0], p[1], z0 + h) for p in poly]
        for i in range(n):
            j = (i + 1) % n
            self.quad(lo[i], lo[j], hi[j], hi[i], side_mat if side_mat is not None else mat)
        if top:
            self.add_face(hi, mat)

    def cylinder(self, cx, cy, z0, r, h, segs=16, mat=0, top=True, top_mat=None):
        ring0 = [(cx + r * math.cos(2 * math.pi * k / segs), cy + r * math.sin(2 * math.pi * k / segs), z0) for k in range(segs)]
        ring1 = [(x, y, z0 + h) for x, y, _ in ring0]
        for k in range(segs):
            j = (k + 1) % segs
            self.quad(ring0[k], ring0[j], ring1[j], ring1[k], mat)
        if top:
            self.add_face(ring1, top_mat if top_mat is not None else mat)

    def ribbon(self, pts, width, zfun, lift=0.05, mat=0, step=4.0, offset=0.0):
        """Flat ribbon following a 2D polyline; z sampled per vertex from zfun(x, y) + lift."""
        dense = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(1, int(math.ceil(L / step)))
            for k in range(1, n + 1):
                t = k / n
                dense.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        left, right = [], []
        m = len(dense)
        for i in range(m):
            a = dense[max(0, i - 1)]
            b = dense[min(m - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            p = dense[i]
            l = (p[0] + nx * (offset + width / 2), p[1] + ny * (offset + width / 2))
            r = (p[0] + nx * (offset - width / 2), p[1] + ny * (offset - width / 2))
            left.append((l[0], l[1], zfun(*l) + lift))
            right.append((r[0], r[1], zfun(*r) + lift))
        for i in range(m - 1):
            self.quad(right[i], right[i + 1], left[i + 1], left[i], mat)
        return left, right

    def to_object(self, name, materials, coll, smooth=False, uv_scale=1.0):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        for m in materials:
            me.materials.append(m)
        if self.mats:
            me.polygons.foreach_set("material_index", self.mats)
        write_box_uvs(me, uv_scale, getattr(self, "tangent_uv", False))
        if smooth:
            me.shade_smooth()
        obj = bpy.data.objects.new(name, me)
        coll.objects.link(obj)
        return obj


def write_box_uvs(me, scale=1.0, tangent=False):
    """Metric box projection per face (1 UV = 1 m / scale). tangent=True lays vertical faces along their own horizontal tangent, so round
    columns, domes and angled walls get an unsheared texture (resort kit); the default keeps the axis-dominant projection of the Old Town."""
    uv = me.uv_layers.new(name="UVMap")
    data = uv.data
    co = [v.co for v in me.vertices]
    for poly in me.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            v = co[me.loops[li].vertex_index]
            if tangent and az < 0.75:
                hl = math.hypot(n.x, n.y) or 1.0
                tx, ty = -n.y / hl, n.x / hl
                data[li].uv = ((v.x * tx + v.y * ty) / scale, v.z / scale)
            elif az >= ax and az >= ay:
                data[li].uv = (v.x / scale, v.y / scale)
            elif ax >= ay:
                data[li].uv = (v.y / scale, v.z / scale)
            else:
                data[li].uv = (v.x / scale, v.z / scale)


# ---------------------------------------------------------------- bevelled pieces (kit / props / heroes)

def bevelled_object(name, mb, materials, coll, bevel=0.012, segments=2, angle_deg=30.0, smooth=True):
    """Builds an object from a MeshBuilder, welds coincident vertices and bevels sharp edges (no low-poly hard edges)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.verts, [], mb.faces)
    me.update()
    for m in materials:
        me.materials.append(m)
    if mb.mats:
        me.polygons.foreach_set("material_index", mb.mats)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bm.normal_update()
    if bevel > 0:
        lim = math.radians(angle_deg)
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim]
        if edges:
            bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=segments, profile=0.5, affect="EDGES", clamp_overlap=True)
    bm.to_mesh(me)
    bm.free()
    write_box_uvs(me, 1.0, getattr(mb, "tangent_uv", False))
    if smooth:
        me.shade_smooth()
        try:
            me.set_sharp_from_angle(angle=math.radians(35))
        except AttributeError:
            pass
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    return obj


# ---------------------------------------------------------------- geometry nodes instancing

def instancer_group(library):
    """Node group per library collection: points carry int 'variant', float 'rot', float 'scl'.
    (Blender 5.x: the collection is set inside the group instead of through a modifier input.)"""
    name = "SA_Instance_" + library.name
    ng = bpy.data.node_groups.get(name)
    if ng:
        return ng
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nodes, links = ng.nodes, ng.links
    gin = nodes.new("NodeGroupInput")
    gout = nodes.new("NodeGroupOutput")
    coll = nodes.new("GeometryNodeCollectionInfo")
    coll.transform_space = "ORIGINAL"
    coll.inputs["Separate Children"].default_value = True
    coll.inputs["Reset Children"].default_value = True
    inst = nodes.new("GeometryNodeInstanceOnPoints")
    inst.inputs["Pick Instance"].default_value = True
    var = nodes.new("GeometryNodeInputNamedAttribute")
    var.data_type = "INT"
    var.inputs["Name"].default_value = "variant"
    rot = nodes.new("GeometryNodeInputNamedAttribute")
    rot.data_type = "FLOAT"
    rot.inputs["Name"].default_value = "rot"
    scl = nodes.new("GeometryNodeInputNamedAttribute")
    scl.data_type = "FLOAT"
    scl.inputs["Name"].default_value = "scl"
    comb = nodes.new("ShaderNodeCombineXYZ")
    coll.inputs["Collection"].default_value = library
    links.new(gin.outputs["Geometry"], inst.inputs["Points"])
    links.new(coll.outputs["Instances"], inst.inputs["Instance"])
    links.new(var.outputs["Attribute"], inst.inputs["Instance Index"])
    links.new(rot.outputs["Attribute"], comb.inputs["Z"])
    links.new(comb.outputs["Vector"], inst.inputs["Rotation"])
    links.new(scl.outputs["Attribute"], inst.inputs["Scale"])
    links.new(inst.outputs["Instances"], gout.inputs["Geometry"])
    return ng


def point_cloud_object(name, points, library, coll, extra_props=None):
    """points: list of (x, y, z, variant_index, rot, scale). Creates a vertex-only mesh with GN instancing."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(p[0], p[1], p[2]) for p in points], [], [])
    me.update()
    a_var = me.attributes.new("variant", "INT", "POINT")
    a_rot = me.attributes.new("rot", "FLOAT", "POINT")
    a_scl = me.attributes.new("scl", "FLOAT", "POINT")
    a_var.data.foreach_set("value", [int(p[3]) for p in points])
    a_rot.data.foreach_set("value", [float(p[4]) for p in points])
    a_scl.data.foreach_set("value", [float(p[5]) for p in points])
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    mod = obj.modifiers.new("SA_Instances", "NODES")
    mod.node_group = instancer_group(library)
    if extra_props:
        props(obj, **extra_props)
    return obj


def library_collection(name, objects, parent):
    """Collection whose children order defines the GN instance index (sorted by name)."""
    c = collection(name, parent, hide_render=True)
    c.hide_viewport = False
    for o in sorted(objects, key=lambda o: o.name):
        link(o, c)
        o.location = (0, 0, 0)
    return c, {o.name: i for i, o in enumerate(sorted(objects, key=lambda o: o.name))}


# ---------------------------------------------------------------- cameras / lights

def camera(name, coll, loc, target=None, rot=None, ortho=None, lens=35, clip=(1.0, 30000.0)):
    data = bpy.data.cameras.new(name)
    data.clip_start, data.clip_end = clip
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    else:
        data.lens = lens
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    obj.location = loc
    if target is not None:
        obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    elif rot is not None:
        obj.rotation_euler = rot
    return obj


def sun_and_sky(scene, coll, elevation_deg=36.0, azimuth_deg=300.0, strength=4.0, sky_strength=0.35, exposure=-1.4, look="w3"):
    if look == "w3":
        return production_look(scene, coll, elevation_deg=elevation_deg, azimuth_deg=azimuth_deg)
    sun_data = bpy.data.lights.new("SA_Sun", "SUN")
    sun_data.energy = strength
    sun_data.angle = math.radians(1.2)
    sun = bpy.data.objects.new("SA_Sun", sun_data)
    coll.objects.link(sun)
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    sun.rotation_euler = (math.pi / 2 - el, 0, az)
    world = bpy.data.worlds.get("SA_World") or bpy.data.worlds.new("SA_World")
    scene.world = world
    nt = world.node_tree
    bg = nt.nodes.get("Background")
    sky = nt.nodes.get("SA_Sky") or nt.nodes.new("ShaderNodeTexSky")
    sky.name = "SA_Sky"
    try:
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = el
        sky.sun_rotation = az
        sky.altitude = 120.0
        sky.air_density = 1.2
        sky.aerosol_density = 1.6
    except (AttributeError, TypeError):
        pass
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = sky_strength
    scene.view_settings.view_transform = "Standard"
    looks = [i.identifier for i in scene.view_settings.bl_rna.properties["look"].enum_items]
    for want in ("AgX - Punchy", "AgX - Medium High Contrast", "AgX - High Contrast"):
        if want in looks:
            scene.view_settings.look = want
            break
    scene.view_settings.exposure = exposure
    world.color = (0.55, 0.62, 0.70)
    return sun



def production_look(scene, coll, elevation_deg=30.0, azimuth_deg=300.0, sun_energy=5.0, sky_strength=.3, exposure=-1.4, haze=0.0):
    """W3 lighting look: physical sky with sun disc, AgX tone mapping (no blown sky), soft sun shadows, ray-traced/horizon-scan AO and GI,
    light aerial haze (depth cue that also helps the relief read in oblique views). Day/night ready: sun + sky are the only drivers."""
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    sun_data = bpy.data.lights.new("SA_Sun", "SUN")
    sun_data.energy = sun_energy
    sun_data.angle = math.radians(.9)
    sun_data.color = (1.0, .93, .84)
    sun = bpy.data.objects.new("SA_Sun", sun_data)
    coll.objects.link(sun)
    sun.rotation_euler = (math.pi / 2 - el, 0, az)
    world = bpy.data.worlds.get("SA_World") or bpy.data.worlds.new("SA_World")
    scene.world = world
    nt = world.node_tree
    bg = nt.nodes.get("Background")
    sky = nt.nodes.get("SA_Sky") or nt.nodes.new("ShaderNodeTexSky")
    sky.name = "SA_Sky"
    try:
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = el
        sky.sun_rotation = az
        sky.altitude = 300.0
        sky.air_density = 1.0
        sky.aerosol_density = 1.2
    except (AttributeError, TypeError):
        pass
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = sky_strength
    if haze > 0:
        vol = nt.nodes.get("SA_Haze") or nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.name = "SA_Haze"
        vol.inputs["Density"].default_value = haze
        vol.inputs["Color"].default_value = (.78, .84, .92, 1)
        out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
    vs = scene.view_settings
    try:
        try:
            vs.view_transform = "Khronos PBR Neutral"      # keeps material saturation; sky stays below clipping
        except TypeError:
            vs.view_transform = "AgX"
        looks = [i.identifier for i in vs.bl_rna.properties["look"].enum_items]
        for want in ("AgX - Medium High Contrast", "AgX - Base Contrast", "None"):
            if want in looks:
                vs.look = want
                break
    except TypeError:
        vs.view_transform = "Standard"
    vs.exposure = exposure
    ee = scene.eevee
    for attr, val in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8),
                      ("use_fast_gi", True), ("fast_gi_distance", 6.0), ("volumetric_end", 1800.0), ("volumetric_tile_size", "8"),
                      ("use_volumetric_shadows", False), ("shadow_pool_size", "1024")):
        try:
            setattr(ee, attr, val)
        except (AttributeError, TypeError):
            pass
    try:
        ee.ray_tracing_method = "SCREEN"
        ee.ray_tracing_options.resolution_scale = "2"
        ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    except (AttributeError, TypeError):
        pass
    world.color = (0.55, 0.62, 0.70)
    scene["sa_look"] = "W3 production (AgX, sky+sun, haze, ray-traced AO/GI)"
    return sun
