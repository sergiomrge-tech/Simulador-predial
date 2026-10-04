"""W3.2: side-by-side W3.1 x W3.2 comparison sheets (Pillow). Usage: python compose_w32_comparison.py ROOT REF_DIR
REF_DIR holds the W3.1 renders of the same cameras as ref31_<camera>.jpg (rendered from a checkout of commit ebeff56)."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

root, ref = Path(sys.argv[1]), Path(sys.argv[2])
rev = root / "ArtSource" / "Blender" / "World" / "Reviews" / "W3_2"
PAIRS = [("w32_13_comparacao_carros_w31_w32.jpg", [("CAM_W32_Hatch", "w32_01_carro_hatch_3m.jpg"), ("CAM_W32_Sedan", "w32_02_carro_sedan_3m.jpg")]),
         ("w32_14_comparacao_aerea_w31_w32.jpg", [("CAM_W32_Aereo_Telhados", "w32_06_aerea_telhados.jpg"), ("CAM_W32_Quadra_Obliqua", "w32_07_quadra_obliqua.jpg")])]
W, H = 1200, 675
for out, rows in PAIRS:
    sheet = Image.new("RGB", (2 * W, len(rows) * H), (20, 20, 20))
    for r, (cam, new) in enumerate(rows):
        for c, (path, label) in enumerate(((ref / f"ref31_{cam}.jpg", "W3.1 (ebeff56)"), (rev / new, "W3.2"))):
            im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, 190, 26), fill=(0, 0, 0))
            d.text((8, 7), label, fill=(255, 255, 255))
            sheet.paste(im, (c * W, r * H))
    sheet.save(rev / out, quality=88)
    print("WROTE", out)
