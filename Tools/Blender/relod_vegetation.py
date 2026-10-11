"""Re-derive lighter vegetation LODs from the committed LOD0 FBX (decimate collapse), same FBX export convention.

LOD0 is kept as authored (the close-up canopy density matters); only LOD1 and LOD2 are re-derived.

Usage: blender --background --python Tools/Blender/relod_vegetation.py -- <vegetation_dir> <out_dir>
The 2026-10-07 LODs were 128k/37k/11k (island_tree_02) and 144k/50k/50k (tree_small_02) triangles, which cost ~15 ms of GPU/CPU
per frame near the parcels; targets here are LOD0 as authored, ~22k LOD1 and ~8k LOD2 (collapse cannot go below ~8k because the leaf cards are disconnected).
"""
import bpy, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
veg_dir, out_dir = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

# fraction of the LOD0 triangles kept for LOD1 and LOD2 (index 0 of the output is LOD1)
PLAN = {
    "island_tree_02": [0.17, 0.032],
    "tree_small_02": [0.15, 0.027],
}

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for b in list(block):
            block.remove(b)

for asset, ratios in PLAN.items():
    src = os.path.join(veg_dir, asset, asset + "_LOD0.fbx")
    for lod, ratio in enumerate(ratios, start=1):
        clear()
        bpy.ops.import_scene.fbx(filepath=src)
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        before = after = 0
        for o in meshes:
            before += len(o.data.polygons)
            bpy.context.view_layer.objects.active = o
            m = o.modifiers.new("lod", 'DECIMATE')
            m.decimate_type = 'COLLAPSE'
            m.ratio = ratio
            m.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=m.name)
            after += len(o.data.polygons)
        print("RELOD", asset, "LOD", lod, "polys", before, "->", after)
        bpy.ops.object.select_all(action='SELECT')
        out = os.path.join(out_dir, "%s_LOD%d.fbx" % (asset, lod))
        bpy.ops.export_scene.fbx(filepath=out, use_selection=True, path_mode='COPY', embed_textures=False,
                                 object_types={'MESH'}, use_mesh_modifiers=True)
