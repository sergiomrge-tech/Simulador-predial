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
}


class Terrain:
    def __init__(self, spec, seed=1503):
        self.canal = [tuple(p) for p in spec["canal"]["points"]]
        rng = random.Random(seed)
        self.roll = Noise2(rng, 1400.0, octaves=2)
        self.fine = Noise2(rng, 420.0, octaves=1)

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
