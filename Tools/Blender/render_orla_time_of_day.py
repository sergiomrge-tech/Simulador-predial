import bpy, sys, math
a = sys.argv[sys.argv.index("--")+1:]
outdir, mode, cams = a[0], a[1], a[2:]
sc = bpy.context.scene
sun = bpy.data.objects["SA_Sun"]
world = bpy.data.worlds["SA_World"]
sky = world.node_tree.nodes["SA_Sky"]
bg = world.node_tree.nodes["Background"]
if mode == "dusk":
    el, az, en, col, bgs, exp = 3.0, 250.0, 3.2, (1.0, .52, .26), .45, -.6
elif mode == "night":
    el, az, en, col, bgs, exp = -9.0, 250.0, 0.0, (.5, .6, 1.0), .9, 1.2
else:
    el, az, en, col, bgs, exp = 27.0, 300.0, 5.0, (1.0, .93, .84), .3, -1.4
sun.rotation_euler = (math.pi/2 - math.radians(max(el, 1.0)), 0, math.radians(az))
sun.data.energy = en
sun.data.color = col
sky.sun_elevation = math.radians(el)
sky.sun_rotation = math.radians(az)
bg.inputs["Strength"].default_value = bgs
sc.view_settings.exposure = exp
lamp_k = 40.0 if mode == "night" else 14.0 if mode == "dusk" else 3.0
for m in bpy.data.materials:
    n = m.name.lower()
    if m.use_nodes and any(k in n for k in ("lampada", "luz_", "head", "tail", "lens", "farol_luz", "lanterna", "farol")):
        for node in m.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED" and "Emission Strength" in node.inputs and node.inputs["Emission Color"].default_value[0] + node.inputs["Emission Color"].default_value[1] > 0.05:
                node.inputs["Emission Strength"].default_value = max(node.inputs["Emission Strength"].default_value, lamp_k)
            if node.type == "EMISSION":
                node.inputs["Strength"].default_value = max(node.inputs["Strength"].default_value, lamp_k)
if mode == "night":
    nc = bpy.data.collections["09_Night_Lights"]
    nc.hide_render = False
    nc.hide_viewport = False
    vit = bpy.data.materials.get("vidro_vitrine")
    for mname in ("vidro_vitrine",):
        m = bpy.data.materials.get(mname)
        if m and m.use_nodes:
            for node in m.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    node.inputs["Emission Color"].default_value = (1.0, .78, .5, 1)
                    node.inputs["Emission Strength"].default_value = .55
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.image_settings.file_format = "JPEG"
for c in cams:
    sc.camera = bpy.data.objects[c]
    sc.render.filepath = f"{outdir}/{c}_{mode}.jpg"
    bpy.ops.render.render(write_still=True)
