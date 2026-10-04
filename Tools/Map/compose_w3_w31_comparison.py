"""Side-by-side W3 x W3.1 review sheets from real Blender captures (Reviews/W3 and Reviews/W3_1). Pillow only.

    python Tools/Map/compose_w3_w31_comparison.py --root .
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAIRS = [  # (title, W3 capture, W3.1 capture)
    ("Rua com carros (estacionamento do herói)", "w2_grocery_01_rua.jpg", "w2_grocery_01_rua.jpg"),
    ("Rua em declive", "w3_02_rua_relevo.jpg", "w31_14_rua_relevo.jpg"),
    ("Talude / arrimo", "w3_03_terreno_talude.jpg", "w31_06_talude_arrimo.jpg"),
    ("Corredor (visão geral)", "w3_01_corredor_visao_geral.jpg", "w31_12_corredor_visao_geral.jpg"),
    ("Clutter / decals", "w3_15_clutter_decals.jpg", "w31_16_clutter.jpg"),
    ("Mercearia — interior", "w2_grocery_03_interior.jpg", "w2_grocery_03_interior.jpg"),
    ("Apto 12 — interior", "w2_home_03_apto12_interior.jpg", "w2_home_03_apto12_interior.jpg"),
    ("Oficina — galpão", "w2_garage_03_galpao.jpg", "w2_garage_03_galpao.jpg"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    root = Path(ap.parse_args().root).resolve()
    rv = root / "ArtSource" / "Blender" / "World" / "Reviews"
    W, H, PAD, TH = 960, 540, 16, 44
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    rows = [(t, rv / "W3" / a, rv / "W3_1" / b) for t, a, b in PAIRS if (rv / "W3" / a).exists() and (rv / "W3_1" / b).exists()]
    for part in range(0, len(rows), 4):
        chunk = rows[part:part + 4]
        sheet = Image.new("RGB", (2 * W + 3 * PAD, len(chunk) * (H + TH + PAD) + PAD + TH), (24, 24, 26))
        d = ImageDraw.Draw(sheet)
        d.text((PAD, 8), "W3 (antes)", fill=(220, 220, 220), font=font)
        d.text((2 * PAD + W, 8), "W3.1 (depois)", fill=(220, 220, 220), font=font)
        for i, (title, a, b) in enumerate(chunk):
            y = TH + PAD + i * (H + TH + PAD)
            d.text((PAD, y), title, fill=(255, 210, 120), font=font)
            for k, src in enumerate((a, b)):
                im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
                sheet.paste(im, (PAD + k * (W + PAD), y + TH - 6))
        out = rv / "W3_1" / f"w31_13_comparacao_w3_w31_{part // 4 + 1}.jpg"
        sheet.save(out, quality=88)
        print("COMPARISON", out.name, len(chunk))


if __name__ == "__main__":
    main()
