"""Santa Aurora W1.5 terrain: smooth, drivable urban relief (pure Python).

Decision (W1.5, user): the city drains toward the drainage canal in the north; the canal is the lowest axis.
- surface(x, z): built surface used by roads, rail, lots and buildings (bridges span the canal channel).
- ground(x, z):  terrain mesh height, = surface plus the canal channel with sloped banks (taludes).
Relief is deliberately gentle (grades mostly below 4%) so every corridor stays drivable.
"""
import math
import random

from sa_geom import Noise2, point_seg, smoothstep

WATER_LEVEL = 0.8
CANAL_BED = -1.6
BANK_INNER = 17.0   # flat bed half-width
BANK_OUTER = 34.0   # top of the talude

# Named relief features (also listed in the validation report).
FEATURES = {
    "tech_plateau": {"centre": (2550.0, 2650.0), "inner": 850.0, "outer": 1500.0, "rise": 16.0,
                     "note": "Platô Tecnológico: área elevada, borda em talude suave"},
    "alto_horizonte": {"centre": (-2350.0, -1750.0), "sigma": 550.0, "rise": 9.0,
                       "note": "Colina da Cidade Antiga (Alto do Horizonte), núcleo histórico"},
    "expansion_ridge": {"note": "Expansão sobe suavemente para o sul"},
    # W2.5 urban relief of the Old Town (user: "a cidade precisa de relevo"): visible but drivable.
    "alto_aurora": {"centre": (-2250.0, -850.0), "sigma": 280.0, "rise": 20.0,
                    "note": "Alto da Aurora: colina residencial ao norte da Cidade Antiga, ponto mais alto do bairro"},
    "vale_corrego": {"road": "R02", "sigma": 130.0, "depth": 9.0, "fade_z": (-700.0, -250.0),
                     "note": "Fundo de vale da Av. do Trabalho (R02): córrego canalizado no canteiro central, segue em galeria até o canal"},
    "ondulacao_urbana": {"wavelength": 360.0, "amp": 5.2, "arterial_clear": (25.0, 140.0),
                         "note": "Ondulação entre quarteirões; zera junto às vias arteriais/coletoras (corredores nivelados)"},
}
# W4 coast (user: "praias"): the southern edge falls to the sea. Waterline curves in bays/headlands; sand slopes 1.6% up to the
# promenade (dz = COAST_PROMENADE_DZ); inland the city surface eases down to the promenade over ~930 m (about 2.5%, drivable).
SEA_LEVEL = 0.0
COAST_PROMENADE_H = 3.0
COAST_PROMENADE_DZ = 170.0
COAST_BLEND_DZ = 1100.0


def shore_z(x):
    """Waterline z at world x (metres): two superposed bays, a headland east of centre and a broad cove in the west."""
    return (-3905.0 + 38.0 * math.sin(x / 640.0) + 20.0 * math.sin(x / 235.0 + 1.3)
            + 26.0 * math.exp(-((x - 1450.0) / 380.0) ** 2) - 24.0 * math.exp(-((x + 1500.0) / 520.0) ** 2))


OLD_RELIEF = (-3950.0, -3950.0, -1150.0, -300.0)   # region of the W2.5 urban relief (soft 250 m edge)
RELIEF_STEP = 10.0


class Terrain:
    def __init__(self, spec, seed=1503, pads=None):
        self.canal = [tuple(p) for p in spec["canal"]["points"]]
        rng = random.Random(seed)
        self.roll = Noise2(rng, 1400.0, octaves=2)
        self.fine = Noise2(rng, 420.0, octaves=1)
        self.undul = Noise2(random.Random(2505), FEATURES["ondulacao_urbana"]["wavelength"], octaves=2)
        roads = {r["id"]: [tuple(p) for p in r["points"]] for r in spec["roads"]}
        self.valley_line = roads[FEATURES["vale_corrego"]["road"]]
        x0, z0, x1, z1 = OLD_RELIEF
        self.corridors = []
        for rid, pts in roads.items():
            if rid in ("R01", "R02", "R07", "R09"):
                self.corridors += [(a, b) for a, b in zip(pts, pts[1:])
                                   if min(a[0], b[0]) < x1 + 300 and max(a[0], b[0]) > x0 - 300 and min(a[1], b[1]) < z1 + 300 and max(a[1], b[1]) > z0 - 300]
        self.pads = pads or []
        self._grid = None

    # ------------------------------------------------------------ W2.5 urban relief (cached on a 10 m lattice)
    def _relief_exact(self, x, z):
        x0, z0, x1, z1 = OLD_RELIEF
        w = smoothstep(x0 - 250, x0, x) * smoothstep(x1 + 250, x1, x) * smoothstep(z0 - 250, z0, z) * smoothstep(z1 + 250, z1, z)
        if w <= 0:
            return 0.0
        au = FEATURES["alto_aurora"]
        h = au["rise"] * math.exp(-((x - au["centre"][0]) ** 2 + (z - au["centre"][1]) ** 2) / (2 * au["sigma"] ** 2))
        vc = FEATURES["vale_corrego"]
        dv = min(point_seg((x, z), a, b)[0] for a, b in zip(self.valley_line, self.valley_line[1:]))
        h -= vc["depth"] * math.exp(-dv * dv / (2 * vc["sigma"] ** 2)) * smoothstep(vc["fade_z"][1], vc["fade_z"][0], z)
        un = FEATURES["ondulacao_urbana"]
        dc = min((point_seg((x, z), a, b)[0] for a, b in self.corridors), default=1e9)
        h += un["amp"] * self.undul(x, z) * smoothstep(un["arterial_clear"][0], un["arterial_clear"][1], dc)
        return w * h

    def relief(self, x, z):
        x0, z0, x1, z1 = OLD_RELIEF
        if not (x0 - 260 <= x <= x1 + 260 and z0 - 260 <= z <= z1 + 260):
            return 0.0
        if self._grid is None:
            gx0, gz0 = x0 - 260, z0 - 260
            nx = int((x1 - x0 + 520) / RELIEF_STEP) + 2
            nz = int((z1 - z0 + 520) / RELIEF_STEP) + 2
            self._grid = (gx0, gz0, nx, nz, [[self._relief_exact(gx0 + i * RELIEF_STEP, gz0 + j * RELIEF_STEP) for j in range(nz)] for i in range(nx)])
        gx0, gz0, nx, nz, g = self._grid
        fx, fz = (x - gx0) / RELIEF_STEP, (z - gz0) / RELIEF_STEP
        i, j = min(nx - 2, max(0, int(fx))), min(nz - 2, max(0, int(fz)))
        tx, tz = fx - i, fz - j
        return (g[i][j] * (1 - tx) * (1 - tz) + g[i + 1][j] * tx * (1 - tz) + g[i][j + 1] * (1 - tx) * tz + g[i + 1][j + 1] * tx * tz)

    def valley_distance(self, x, z):
        return min(point_seg((x, z), a, b)[0] for a, b in zip(self.valley_line, self.valley_line[1:]))

    def canal_distance(self, x, z):
        best = 1e18
        p = (x, z)
        for a, b in zip(self.canal, self.canal[1:]):
            d = point_seg(p, a, b)[0]
            if d < best:
                best = d
        return best

    def surface(self, x, z):
        d = self.canal_distance(x, z)
        h = 2.6 + 21.0 * (1.0 - math.exp(-d / 1400.0))
        tp = FEATURES["tech_plateau"]
        r = math.hypot(x - tp["centre"][0], z - tp["centre"][1])
        h += tp["rise"] * smoothstep(tp["outer"], tp["inner"], r)
        ah = FEATURES["alto_horizonte"]
        h += ah["rise"] * math.exp(-((x - ah["centre"][0]) ** 2 + (z - ah["centre"][1]) ** 2) / (2 * ah["sigma"] ** 2))
        h += 4.0 * smoothstep(-1500.0, -3600.0, z) * smoothstep(-1500.0, -900.0, x)
        # Rolling variation fades out near the canal so the floodplain stays level.
        fade = smoothstep(60.0, 500.0, d)
        h += fade * (3.0 * self.roll(x, z) + 0.8 * self.fine(x, z))
        h += self.relief(x, z)
        dz = z - shore_z(x)
        if dz < COAST_BLEND_DZ:
            if dz <= 0.0:
                hc, w = SEA_LEVEL + 0.2 + dz * 0.05, 1.0                      # sea floor shelf
            elif dz <= COAST_PROMENADE_DZ:
                hc, w = SEA_LEVEL + 0.2 + dz * (COAST_PROMENADE_H - 0.2) / COAST_PROMENADE_DZ, 1.0   # beach
            else:
                hc, w = COAST_PROMENADE_H, smoothstep(COAST_BLEND_DZ, COAST_PROMENADE_DZ, dz)
            h += (hc - h) * w
        for pd in self.pads:                      # flattened building pads (hero lots), blended over a margin
            px0, pz0, px1, pz1 = pd["rect"]
            dx = max(px0 - x, 0.0, x - px1)
            dz = max(pz0 - z, 0.0, z - pz1)
            dd = math.hypot(dx, dz)
            if dd < pd["margin"]:
                h += (pd["z"] - h) * smoothstep(pd["margin"], 0.0, dd)
        return h

    def ground(self, x, z):
        h = self.surface(x, z)
        d = self.canal_distance(x, z)
        if d < BANK_OUTER:
            t = smoothstep(BANK_INNER, BANK_OUTER, d)
            h = CANAL_BED + (h - CANAL_BED) * t
        return h

    def grade(self, a, b):
        """Average grade (fraction) of the built surface between two points."""
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L == 0:
            return 0.0
        return abs(self.surface(*b) - self.surface(*a)) / L


def hero_pads(root, spec, margin=10.0):
    """Flat pads for the Old Town hero lots at the mean height of the unpadded surface (same value the hero generators use)."""
    import json
    from pathlib import Path
    data = json.loads((Path(root) / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json").read_text(encoding="utf-8"))
    t = Terrain(spec)
    pads = []
    for h in data["heroes"]:
        x0, z0, x1, z1 = h["lot"]
        pts = ((x0, z0), (x1, z0), (x1, z1), (x0, z1), ((x0 + x1) / 2, (z0 + z1) / 2))
        pads.append({"id": h["id"], "rect": (x0, z0, x1, z1), "z": sum(t.surface(*p) for p in pts) / len(pts), "margin": margin})
    return pads
