"""Exports the Bairro das Palmeiras (Resort Aurora's playable map) as heightfield + JSON for Unity.

The terrain comes from the masterplan Terrain, so the bairro sits on the real coast of Praia das Palmeiras. Parcels (buyable land) are
flattened into terraces; streets and the vila lots are laid out here and rendered by Unity. Local frame: X = world X - SITE_X0,
Z = world Z - z0 (z0 is SEA_MARGIN seaward of the waterline at world x = 0), Y = height.

Usage: python Tools/Map/export_resort_site.py [project_root]
Outputs (FacilityOps/Assets/_Game/Resources/Resort/): ResortSiteHeights.bytes, ResortSite.json
"""
import json
import math
import random
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import sa_terrain as T  # noqa: E402
from masterplan_layout import load_spec  # noqa: E402

SITE_X0, SITE_W = -450.0, 900.0
SEA_MARGIN, LAND_DEPTH = 80.0, 640.0
STEP = 1.5
BLEND = 14.0                       # terrace skirt, metres
BEACH_WATER_DZ = 114.0             # the masterplan beach is 170 m deep; the playable bairro compresses it so the waterline is ~55 m from the kiosk (REF 01)

spec = load_spec(root)
terrain = T.Terrain(spec, pads=T.hero_pads(root, spec))
shore0 = T.shore_z(0.0)
z0 = shore0 - SEA_MARGIN
depth = SEA_MARGIN + LAND_DEPTH


def lx(wx):  # world x -> local x
    return wx - SITE_X0


def lz(dz):  # distance from the waterline at x = 0 -> local z
    return SEA_MARGIN + dz


# Parcels: world x range, dz range (distance from the waterline at x = 0), price. Ids are stable (saves reference them).
PARCELS = [
    dict(id="P0", name="Ponto da barraca", x=(-3, 3), dz=(158, 170), price=0, owned=True, note="Licença de ambulante (prólogo)"),
    dict(id="P1", name="Faixa do quiosque", x=(-14, 14), dz=(146, 170), price=2500, note="Concessão municipal do quiosque"),
    dict(id="P2", name="Sobrado do Seu Tonico", x=(-70, -30), dz=(250, 290), price=6000, note="Futura pousada"),
    dict(id="P3", name="Quarteirão vizinho", x=(-25, 45), dz=(250, 310), price=15000, note="Hotel"),
    dict(id="P4", name="Grande Hotel Palmeiras", x=(55, 145), dz=(250, 330), price=40000, locked="story", note="Ruínas; exige a escritura (história)"),
    dict(id="P5", name="Platô das Palmeiras", x=(-120, 120), dz=(400, 590), price=90000, terraces=4, heights=[6.5, 11.0, 15.5, 20.0], splits=[0, 39, 81, 120, 189], note="Resort em terraços"),
    dict(id="P6", name="Ponta do Farol", x=(330, 440), dz=(250, 350), price=150000, locked="stage", note="Ala exclusiva e farol"),
    dict(id="P7", name="Marina", x=(250, 350), dz=(110, 150), price=120000, locked="stage", note="Marina e píer leste"),
]
FLAT_PARCELS = {"P2", "P3", "P4", "P5", "P6"}              # P0/P1 are on the promenade/beach edge and keep the natural height

STREETS_NS = [-390, -300, -210, 170, 260, 350]            # world x of north-south streets
STREETS_EW = [(345, 10), (600, 10)]                         # (dz, width) of east-west streets
AVENUE = (215, 22)                                          # Avenida da Orla
PROM = (176, 12)                                            # promenade centre, width


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


terraces, pad_height = [], {}
for p in PARCELS:
    if p["id"] not in FLAT_PARCELS:
        continue
    x0, x1 = p["x"]; d0, d1 = p["dz"]
    n = p.get("terraces", 1)
    for k in range(n):
        if "splits" in p:
            a, b = d0 + p["splits"][k], d0 + p["splits"][k + 1]
        else:
            a = d0 + (d1 - d0) * k / n
            b = d0 + (d1 - d0) * (k + 1) / n
        h = round(terrain.ground((x0 + x1) / 2, shore0 + (a + b) / 2) * 20) / 20     # natural height at the centre, 5 cm steps
        if "heights" in p:
            h = p["heights"][k]                                                       # authored terraces (dramatic hillside amphitheatre)
        terraces.append(dict(parcel=p["id"], x=(x0, x1), dz=(a, b), h=h))
        pad_height.setdefault(p["id"], []).append(h)


def beach_ground(wx, wz):
    """Natural ground with the beach compressed: the waterline (dz = -4 on the masterplan) moves inland to dz = BEACH_WATER_DZ, the promenade (dz = 170) stays put."""
    sz = T.shore_z(wx)
    dz = wz - sz
    top = T.COAST_PROMENADE_DZ
    if dz < top:
        if dz >= BEACH_WATER_DZ:
            g = -4.0 + (dz - BEACH_WATER_DZ) * (top + 4.0) / (top - BEACH_WATER_DZ)
        else:
            g = -4.0 + (dz - BEACH_WATER_DZ)
        wz = sz + g
    return terrain.ground(wx, wz)


def height(wx, wz, skip=()):
    """Terraces are exactly flat inside their rectangles (so steps sit on the boundary); outside, the natural ground blends toward the nearest terrace."""
    h = beach_ground(wx, wz)
    dz = wz - shore0
    by_parcel = {}
    for t in terraces:
        by_parcel.setdefault(t["parcel"], []).append(t)
    for pid, ts in by_parcel.items():
        if pid in skip:
            continue
        x0 = min(t["x"][0] for t in ts); x1 = max(t["x"][1] for t in ts)
        d0 = min(t["dz"][0] for t in ts); d1 = max(t["dz"][1] for t in ts)
        cx, cd = min(max(wx, x0), x1), min(max(dz, d0), d1)
        dist = math.hypot(wx - cx, dz - cd)
        if dist >= BLEND:
            continue
        near = next((t for t in ts if t["dz"][0] <= cd <= t["dz"][1] and t["x"][0] <= cx <= t["x"][1]), ts[0])
        for t in ts:                                   # prefer the terrace whose half-open range contains the point (upper one at the shared edge)
            if t["dz"][0] <= cd < t["dz"][1]:
                near = t
        w = 1.0 if dist == 0.0 else smooth(1.0 - dist / BLEND)
        h += (near["h"] - h) * w
    return h


nx, nz = int(SITE_W / STEP) + 1, int(depth / STEP) + 1
verts = [[height(SITE_X0 + i * STEP, z0 + j * STEP) for i in range(nx)] for j in range(nz)]

out_dir = root / "FacilityOps" / "Assets" / "_Game" / "Resources" / "Resort"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "ResortSiteHeights.bytes").write_bytes(b"".join(struct.pack("<%df" % nx, *row) for row in verts))
# the same land before the platô is graded (stages 1-5 of the evolution): P5 left natural
natural = [[height(SITE_X0 + i * STEP, z0 + j * STEP, skip=("P5",)) for i in range(nx)] for j in range(nz)]
(out_dir / "ResortSiteHeights_natural.bytes").write_bytes(b"".join(struct.pack("<%df" % nx, *row) for row in natural))

# ---- vila lots: frontage along the east-west streets, skipping parcels, streets, the avenue and the home building
fam = json.loads((root / "ArtSource/Blender/World/OldTown/oldtown_streaming_manifest_v1.json").read_text(encoding="utf-8"))["families"]
HOUSES = [(v["w"], v["d"], v["height"]) for v in fam.values() if v["height"] <= 10.5 and v["w"] <= 14 and v["d"] <= 20] or [(7, 14, 6)]
rng = random.Random(1994)
LAR = dict(x=-120.0, dz=265.0, w=12.0, d=8.0, h=3.4)         # Apto 12 kitnet: ~150 m from the stall, door faces the avenue


def blocked(x, dzc, w, d):
    ax0, ax1, az0, az1 = x - w / 2, x + w / 2, dzc - d / 2, dzc + d / 2
    for p in PARCELS:
        bx0, bx1 = p["x"][0] - 6, p["x"][1] + 6
        bz0, bz1 = p["dz"][0] - 6, p["dz"][1] + 6
        if ax1 > bx0 and ax0 < bx1 and az1 > bz0 and az0 < bz1:
            return True
    if az1 > AVENUE[0] - AVENUE[1] / 2 - 4 and az0 < AVENUE[0] + AVENUE[1] / 2 + 4:
        return True
    for sx in STREETS_NS:
        if ax1 > sx - 9 and ax0 < sx + 9 and az0 > 235:
            return True
    for sd, sw in STREETS_EW:
        if az1 > sd - sw / 2 - 2 and az0 < sd + sw / 2 + 2:
            return True
    if abs(x - LAR["x"]) < LAR["w"] / 2 + 8 + w / 2 and abs(dzc - LAR["dz"]) < LAR["d"] / 2 + 8 + d / 2:
        return True
    return az0 < 238 or az1 > LAND_DEPTH - 6 or ax0 < SITE_X0 + 8 or ax1 > SITE_X0 + SITE_W - 8


lots = []
for sd, sw in STREETS_EW:
    for side in (-1, 1):                                  # south side faces north, north side faces south
        x = SITE_X0 + 14
        while x < SITE_X0 + SITE_W - 14:
            w, d, h = rng.choice(HOUSES)
            w = max(6.0, min(w, 12.0)); d = max(10.0, min(d, 16.0)); h = max(4.5, min(h, 9.0))
            dzc = sd + side * (sw / 2 + 2 + d / 2)
            if not blocked(x + w / 2, dzc, w, d):
                lots.append(dict(x=round(lx(x + w / 2), 2), z=round(lz(dzc), 2), w=round(w, 1), d=round(d, 1), h=round(h, 1),
                                 rot=0 if side < 0 else 180, c=rng.randrange(8)))
            x += w + rng.choice((0.0, 0.0, 1.5, 3.0))

site = {
    "schemaVersion": 2,
    "name": "Bairro das Palmeiras",
    "worldOrigin": {"x": SITE_X0, "z": z0},
    "size": {"x": SITE_W, "z": depth},
    "step": STEP, "columns": nx, "rows": nz,
    "seaLevel": T.SEA_LEVEL,
    "shoreLocalZ": SEA_MARGIN,
    "promenade": [{"x": round(i * 12.0, 2), "z": round(T.shore_z(SITE_X0 + i * 12.0) + PROM[0] - z0, 2)} for i in range(int(SITE_W / 12.0) + 1)],
    "avenue": {"z": lz(AVENUE[0]), "width": AVENUE[1]},
    "streetsNS": [{"x": lx(sx), "from": lz(235), "to": lz(LAND_DEPTH - 6), "width": 9} for sx in STREETS_NS],
    "streetsEW": [{"z": lz(sd), "width": sw} for sd, sw in STREETS_EW],
    "parcels": [dict(id=p["id"], name=p["name"], note=p["note"], price=p["price"], owned=bool(p.get("owned")), locked=p.get("locked", ""),
                     x=round(lx(p["x"][0]), 2), z=round(lz(p["dz"][0]), 2), width=p["x"][1] - p["x"][0], depth=p["dz"][1] - p["dz"][0])
                for p in PARCELS],
    "terraces": [dict(parcel=t["parcel"], x=round(lx(t["x"][0]), 2), z=round(lz(t["dz"][0]), 2), width=t["x"][1] - t["x"][0],
                      depth=round(t["dz"][1] - t["dz"][0], 2), height=t["h"]) for t in terraces],
    "lots": lots,
    "home": dict(name="Edifício Santa Clara", unit="Apto 12", x=round(lx(LAR["x"]), 2), z=round(lz(LAR["dz"]), 2), width=LAR["w"], depth=LAR["d"],
                 height=LAR["h"], doorZ=round(lz(LAR["dz"]) - LAR["d"] / 2 - 2.5, 2)),
    "stall": dict(x=round(lx(0.0), 2)),
    "heights": {"min": round(min(min(r) for r in verts), 2), "max": round(max(max(r) for r in verts), 2)},
}
(out_dir / "ResortSite.json").write_text(json.dumps(site, indent=1) + "\n", encoding="utf-8")
print("bairro exported:", f"{nx}x{nz} verts, {len(lots)} lots, {len(terraces)} terraces,", site["heights"])
