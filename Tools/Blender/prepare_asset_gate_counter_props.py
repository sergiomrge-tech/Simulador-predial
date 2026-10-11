import bpy,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(sys.argv[sys.argv.index('--')+1]);library=Path('D:/ProjectResort_AssetLibrary/PolyHaven_CC0');out=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Props'
for folder,name,prefix in [('CashRegister_01_2K','CashRegister','CashRegister_01'),('plastic_crate_02_2K','PlasticCrate','plastic_crate_02')]:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    source=library/folder;bpy.ops.import_scene.fbx(filepath=str(next(source.glob('*.fbx'))))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);origin=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for obj in meshes:
        pts=[obj.matrix_world@v.co for v in obj.data.vertices];obj.matrix_world=Matrix.Identity(4)
        for v,p in zip(obj.data.vertices,pts):v.co=p-origin
        obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',bake_space_transform=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    sets=[prefix,prefix+'_glass'] if name=='CashRegister' else [prefix]
    for index,s in enumerate(sets):
        files=list((source/'textures').glob(s+'_*'));files=[p for p in files if s.endswith('_glass') or '_glass_' not in p.name]
        def channel(token):
            f=next((p for p in files if token in p.name),None)
            if f is None:return None
            im=bpy.data.images.load(str(f),check_existing=False);im.colorspace_settings.name='Non-Color';im.scale(1024,1024);return list(im.pixels[:])
        color=channel('_diff_');normal=channel('_nor_gl_');rough=channel('_rough');metal=channel('_metallic_');opacity=channel('_opacity_')
        stem=name+str(index)
        bpy.context.scene.view_settings.view_transform='Raw'
        for suffix,values in [('BaseColor',color),('Normal',normal),('MetallicGloss',None)]:
            if suffix=='MetallicGloss':
                values=[]
                for i in range(0,1024*1024*4,4):
                    m=metal[i] if metal else 0;values.extend((m,m,m,1-(rough[i] if rough else .7)))
            elif suffix=='BaseColor' and opacity:
                for i in range(0,len(values),4):values[i+3]=opacity[i]
            if values is None:continue
            image=bpy.data.images.new(stem+suffix,1024,1024,alpha=True);image.colorspace_settings.name='Non-Color';image.pixels=values
            image.save_render(str(out/(stem+'_'+suffix+'.png')))
    print(json.dumps({'asset':name,'size':list(hi-lo),'materials':[[m.name for m in o.data.materials] for o in meshes],'polygons':sum(len(o.data.polygons) for o in meshes)}))
