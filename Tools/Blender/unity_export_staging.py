"""Evaluate static export meshes in disposable objects, never save the authoring file."""
import bpy
from mathutils import Vector


def stage_meshes(objects):
    staged = []
    groups = []
    for source in objects:
        if source.type == 'EMPTY':
            continue
        temp = source.copy()
        temp.data = source.data.copy()
        bpy.context.scene.collection.objects.link(temp)
        temp.parent = None
        temp.matrix_world = source.matrix_world.copy()
        temp.hide_set(False)
        temp.hide_viewport = False
        for modifier in temp.modifiers:
            if modifier.type != 'NODES' or modifier.node_group is None:
                continue
            group = modifier.node_group.copy()
            groups.append(group)
            modifier.node_group = group
            for output in [n for n in group.nodes if n.type == 'GROUP_OUTPUT']:
                for socket in output.inputs:
                    if socket.type != 'GEOMETRY' or not socket.is_linked:
                        continue
                    link = socket.links[0]
                    original = link.from_socket
                    group.links.remove(link)
                    realize = group.nodes.new('GeometryNodeRealizeInstances')
                    group.links.new(original, realize.inputs['Geometry'])
                    group.links.new(realize.outputs['Geometry'], socket)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = bpy.data.meshes.new_from_object(temp.evaluated_get(depsgraph),
                                               preserve_all_data_layers=True, depsgraph=depsgraph)
        if mesh is None or not mesh.polygons:
            bpy.data.objects.remove(temp, do_unlink=True)
            raise RuntimeError(f'No evaluated geometry for {source.name}')
        old_data = temp.data
        temp.modifiers.clear()
        temp.data = mesh
        if old_data.users == 0:
            bpy.data.meshes.remove(old_data) if isinstance(old_data, bpy.types.Mesh) else None
        temp.name = 'EXPORT_' + source.name
        staged.append(temp)
    return staged, groups


def bounds(objects):
    points = [o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    if not points:
        raise RuntimeError('Export has no mesh bounds')
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def cleanup(objects, groups):
    for obj in objects:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for group in groups:
        if group.users == 0:
            bpy.data.node_groups.remove(group)
