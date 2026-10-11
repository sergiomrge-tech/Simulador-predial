"""Promote only approved local Renderpeople Unity FBXs; preserve source archives.

Existing runtime assets are never overwritten. Run from any working directory.
"""
from pathlib import Path
from PIL import Image
import hashlib, json, shutil, zipfile

ROOT = Path(__file__).resolve().parents[2]
LIB = Path('D:/ProjectResort_AssetLibrary')
DEST = ROOT / 'FacilityOps/Assets/_Game/ThirdParty/Resources/RealisticHumans'
DEST.mkdir(parents=True, exist_ok=True)
entries = []
for name, stem in [('Eric', 'rp_eric_rigged_001'), ('Carla', 'rp_carla_rigged_001'), ('Claudia', 'rp_claudia_rigged_002')]:
    source = LIB / 'Renderpeople_Free_Rigged/Source' / (stem + '_FBX')
    fbx = source / (stem + '_u3d.fbx')
    target = DEST / (name + '.fbx')
    if not target.exists():
        shutil.copyfile(fbx, target)
    for channel, suffix in [('dif', 'BaseColor'), ('norm', 'Normal'), ('gloss', 'MetallicGloss')]:
        out = DEST / (name + '_' + suffix + '.png')
        if out.exists():
            continue
        img = Image.open(source / 'tex' / (stem + '_' + channel + '.jpg'))
        img = img.resize((2048, 2048), Image.Resampling.LANCZOS)
        if channel == 'gloss':
            gloss = img.convert('L')
            zero = Image.new('L', gloss.size, 0)
            img = Image.merge('RGBA', (zero, zero, zero, gloss))
        else:
            img = img.convert('RGB')
        img.save(out)
    entries.append(dict(name=name, source=str(fbx), sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),
                        runtime=str(target.relative_to(ROOT)), textures='2048px, original UV atlas; nonmetallic RGB + source gloss alpha'))
archives = {}
for folder in ['Renderpeople_Free_Animated', 'Renderpeople_Free_Posed']:
    for archive in (LIB / folder).glob('*.zip'):
        with zipfile.ZipFile(archive) as z:
            archives[str(archive)] = z.namelist()
manifest = dict(assets=entries, reviewed_archives=archives,
                license='Renderpeople free license; local archive: D:/ProjectResort_AssetLibrary/Licenses/Renderpeople_Free_Rigged. NOT CC0. Do not redistribute raw assets.',
                decision='Only rigged u3d FBXs promoted. Animated/posed archives are inventoried, not runtime locomotion candidates without a verified Humanoid avatar.')
(DEST / 'PROMOTION_LOCAL_ONLY.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(entries, indent=2))
