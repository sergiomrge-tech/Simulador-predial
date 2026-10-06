"""Exports the Resort Aurora build site (Praia das Palmeiras) as a terrain OBJ + site JSON for Unity.

The mesh comes from the same Terrain used for the masterplan, so the resort sits on the real coast. A flat pad is carved behind the
Avenida da Orla so the build grid can lie on a plane. Local frame: X = world X - SITE_X0, Z = world Z - site_z0, Y = world height.

Usage: python Tools/Map/export_resort_site.py [project_root]
Outputs: FacilityOps/Assets/_Game/Resources/Resort/ResortSiteHeights.bytes and ResortSite.json
"""
import json
import math
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import sa_terrain as T  # noqa: E402
from masterplan_layout import load_spec  # noqa: E402

SITE_X0, SITE_W = -160.0, 320.0          # world X extent (m)
SEA_MARGIN, LAND_DEPTH = 80.0, 440.0     # metres seaward / landward of the waterline at the site centre
STEP = 2.0
PAD_X = (-128.0, 128.0)                  # pad in world X
PAD_DZ = (235.0, 395.0)                  # pad distance from the waterline
PAD_BLEND = 28.0
CELL = 1.0

spec = load_spec(root)
terrain = T.Terrain(spec, pads=T.hero_pads(root, spec))
shore0 = T.shore_z(0.0)
z0 = shore0 - SEA_MARGIN
depth = SEA_MARGIN + LAND_DEPTH


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


pad_h = round(terrain.ground(0.0, shore0 + (PAD_DZ[0] + PAD_DZ[1]) / 2), 2)


def height(wx, wz):
    h = terrain.ground(wx, wz)
    dz = wz - shore0                      # true rectangle in world space, referenced to the waterline at x = 0
    dx_out = max(PAD_X[0] - wx, 0.0, wx - PAD_X[1])
    dz_out = max(PAD_DZ[0] - dz, 0.0, dz - PAD_DZ[1])
    d = math.hypot(dx_out, dz_out)
    if d < PAD_BLEND:
        h += (pad_h - h) * smooth(1.0 - d / PAD_BLEND)
    return h


nx, nz = int(SITE_W / STEP) + 1, int(depth / STEP) + 1
verts = [[height(SITE_X0 + i * STEP, z0 + j * STEP) for i in range(nx)] for j in range(nz)]

out_dir = root / "FacilityOps" / "Assets" / "_Game" / "Resources" / "Resort"
out_dir.mkdir(parents=True, exist_ok=True)
import struct  # noqa: E402
# row-major float32 heights, nx*nz, row j = world Z z0 + j*STEP, column i = world X SITE_X0 + i*STEP. Unity builds the mesh at runtime.
(out_dir / "ResortSiteHeights.bytes").write_bytes(b"".join(struct.pack("<%df" % nx, *row) for row in verts))

# the pad rectangle in local metres, aligned to the whole-metre grid, using the waterline at x = 0 as reference
px0 = PAD_X[0] - SITE_X0
pz0 = (shore0 + PAD_DZ[0]) - z0
site = {
    "schemaVersion": 1,
    "name": "Praia das Palmeiras",
    "worldOrigin": {"x": SITE_X0, "z": z0},
    "size": {"x": SITE_W, "z": depth},
    "step": STEP, "columns": nx, "rows": nz,
    "seaLevel": T.SEA_LEVEL,
    "pad": {"x": round(px0), "z": round(pz0), "width": int(PAD_X[1] - PAD_X[0]), "depth": int(PAD_DZ[1] - PAD_DZ[0]),
            "height": pad_h, "cell": CELL},
    "shoreLocalZ": SEA_MARGIN,
    "promenade": [{"x": round(i * 16.0, 2), "z": round(T.shore_z(SITE_X0 + i * 16.0) + 176.0 - z0, 2)} for i in range(int(SITE_W / 16.0) + 1)],
    "heights": {"min": round(min(min(r) for r in verts), 2), "max": round(max(max(r) for r in verts), 2)},
}
(out_dir / "ResortSite.json").write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
print("site exported", json.dumps(site["pad"]), site["heights"], f"verts={nx * nz}")
