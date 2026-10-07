"""Pack downloaded furniture and project-owned maps for URP (metallic RGB, smoothness alpha).
Usage: python Tools/Map/prepare_resort_pbr_textures.py SOURCE_DIRECTORY [PROJECT_ROOT]
Original 2K textures remain untouched; runtime furniture maps are 1K with mipmaps.
"""
from pathlib import Path
from PIL import Image, ImageOps
import shutil, sys
root=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path(__file__).resolve().parents[2]
source=Path(sys.argv[1]).resolve()
tex=root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Textures'
for kind in ('chair','table'):
 stem='outdoor_table_chair_set_01_'+kind
 for src,suffix in [('diff','BaseColor'),('nor_gl','Normal')]:
  image=Image.open(source/'Textures'/(stem+'_'+src+'_2k.png')).convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
  image.save(tex/('furniture_'+kind+'_'+suffix+'.png'))
 metal=Image.open(source/'Textures'/(stem+'_metal_2k.png')).convert('L').resize((1024,1024),Image.Resampling.LANCZOS)
 rough=Image.open(source/'Textures'/(stem+'_rough_2k.png')).convert('L').resize((1024,1024),Image.Resampling.LANCZOS)
 Image.merge('RGBA',(metal,metal,metal,ImageOps.invert(rough))).save(tex/('furniture_'+kind+'_MetallicGloss.png'))
shutil.copyfile(source/'LICENSE_SOURCE.txt',root/'FacilityOps/Assets/_Game/Resources/Art/Resort/Furniture/LICENSE_SOURCE.txt')
for mat in ('galvanizado','pedra_portuguesa'):
 for channel in ('BaseColor','Normal','AO'):
  shutil.copyfile(root/'ArtSource/Textures'/mat/(mat+'_'+channel+'.jpg'),tex/(mat+'_'+channel+'.jpg'))
 rough=Image.open(root/'ArtSource/Textures'/mat/(mat+'_Roughness.jpg')).convert('L')
 metal=Image.open(root/'ArtSource/Textures'/mat/(mat+'_Metallic.jpg')).convert('L') if mat=='galvanizado' else Image.new('L',rough.size,0)
 Image.merge('RGBA',(metal,metal,metal,ImageOps.invert(rough))).save(tex/(mat+'_MetallicGloss.png'))
