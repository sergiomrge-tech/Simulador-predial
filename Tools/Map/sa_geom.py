"""Pure-Python 2D geometry helpers for the Santa Aurora layout (no Blender, no third-party packages).

Coordinates are spec metres: x = east, z = north.
"""
import math


# ---------------------------------------------------------------- vectors / segments

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, s):
    return (a[0] * s, a[1] * s)


def length(a):
    return math.hypot(a[0], a[1])


def norm(a):
    L = length(a)
    return (a[0] / L, a[1] / L) if L else (0.0, 0.0)


def perp(a):
    """Left-hand normal (rotate +90 degrees)."""
    return (-a[1], a[0])


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_seg(p, a, b):
    """Distance from p to segment ab, closest point and parameter t."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dz * dz
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / L))
    q = (a[0] + t * dx, a[1] + t * dz)
    return math.hypot(q[0] - p[0], q[1] - p[1]), q, t


def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def segs_cross(a, b, c, d):
    d1, d2, d3, d4 = _ccw(c, d, a), _ccw(c, d, b), _ccw(a, b, c), _ccw(a, b, d)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def seg_intersection(a, b, c, d):
    """Intersection point of segments ab and cd, with parameters (t on ab, u on cd), or None."""
    rx, rz = b[0] - a[0], b[1] - a[1]
    sx, sz = d[0] - c[0], d[1] - c[1]
    den = rx * sz - rz * sx
    if abs(den) < 1e-9:
        return None
    qpx, qpz = c[0] - a[0], c[1] - a[1]
    t = (qpx * sz - qpz * sx) / den
    u = (qpx * rz - qpz * rx) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (a[0] + t * rx, a[1] + t * rz), t, u
    return None


def seg_seg_dist(a, b, c, d):
    if segs_cross(a, b, c, d):
        return 0.0
    return min(point_seg(a, c, d)[0], point_seg(b, c, d)[0], point_seg(c, a, b)[0], point_seg(d, a, b)[0])


def polyline_segments(pts):
    return list(zip(pts, pts[1:]))


def polyline_length(pts):
    return sum(dist(a, b) for a, b in zip(pts, pts[1:]))


def resample(pts, step):
    """Resample a polyline at roughly constant spacing (keeps end points)."""
    out = [tuple(pts[0])]
    for a, b in zip(pts, pts[1:]):
        L = dist(a, b)
        n = max(1, int(math.ceil(L / step)))
        for k in range(1, n + 1):
            out.append(lerp(a, b, k / n))
    return out


def fillet_polyline(pts, radius, seg_len=12.0):
    """Replace each interior corner by a circular arc of the given radius (clamped to fit)."""
    if len(pts) < 3:
        return [tuple(p) for p in pts]
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d1, d2 = norm(sub(p0, p1)), norm(sub(p2, p1))
        cosang = max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))
        ang = math.acos(cosang)  # interior angle
        if ang > math.pi - 1e-3 or ang < 1e-3:
            out.append(tuple(p1))
            continue
        tan_len = radius / math.tan(ang / 2)
        max_tan = 0.45 * min(dist(p0, p1), dist(p1, p2))
        if tan_len > max_tan:
            tan_len = max_tan
        r = tan_len * math.tan(ang / 2)
        t1 = add(p1, mul(d1, tan_len))
        t2 = add(p1, mul(d2, tan_len))
        bis = norm(add(d1, d2))
        centre = add(p1, mul(bis, r / math.sin(ang / 2)))
        a1 = math.atan2(t1[1] - centre[1], t1[0] - centre[0])
        a2 = math.atan2(t2[1] - centre[1], t2[0] - centre[0])
        da = a2 - a1
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        n = max(2, int(abs(da) * r / seg_len))
        for k in range(n + 1):
            a = a1 + da * k / n
            out.append((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)))
    out.append(tuple(pts[-1]))
    return out


def chaikin(pts, iterations=2):
    for _ in range(iterations):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            new.append(lerp(a, b, .25))
            new.append(lerp(a, b, .75))
        new.append(pts[-1])
        pts = new
    return pts


def offset_polyline(pts, off):
    """Offset to the left (positive) using mitred joints."""
    out = []
    n = len(pts)
    for i in range(n):
        ns = []
        if i > 0:
            ns.append(perp(norm(sub(pts[i], pts[i - 1]))))
        if i < n - 1:
            ns.append(perp(norm(sub(pts[i + 1], pts[i]))))
        nx = sum(v[0] for v in ns)
        nz = sum(v[1] for v in ns)
        L = math.hypot(nx, nz) or 1.0
        nx, nz = nx / L, nz / L
        cos = max(.35, nx * ns[0][0] + nz * ns[0][1])
        out.append((pts[i][0] + nx * off / cos, pts[i][1] + nz * off / cos))
    return out


# ---------------------------------------------------------------- oriented rectangles

class OBB:
    """Oriented rectangle: centre c, unit axis u (frontage direction), half sizes hw (along u), hd (along v)."""
    __slots__ = ("c", "u", "v", "hw", "hd", "_corners", "_aabb")

    def __init__(self, c, u, hw, hd):
        self.c = (float(c[0]), float(c[1]))
        self.u = norm(u)
        self.v = perp(self.u)
        self.hw = hw
        self.hd = hd
        self._corners = None
        self._aabb = None

    @staticmethod
    def axis_aligned(cx, cz, w, d):
        return OBB((cx, cz), (1.0, 0.0), w / 2, d / 2)

    def corners(self):
        if self._corners is None:
            c, u, v = self.c, self.u, self.v
            self._corners = [
                (c[0] - u[0] * self.hw - v[0] * self.hd, c[1] - u[1] * self.hw - v[1] * self.hd),
                (c[0] + u[0] * self.hw - v[0] * self.hd, c[1] + u[1] * self.hw - v[1] * self.hd),
                (c[0] + u[0] * self.hw + v[0] * self.hd, c[1] + u[1] * self.hw + v[1] * self.hd),
                (c[0] - u[0] * self.hw + v[0] * self.hd, c[1] - u[1] * self.hw + v[1] * self.hd),
            ]
        return self._corners

    def aabb(self):
        if self._aabb is None:
            cs = self.corners()
            xs = [p[0] for p in cs]
            zs = [p[1] for p in cs]
            self._aabb = (min(xs), min(zs), max(xs), max(zs))
        return self._aabb

    def grown(self, pad):
        return OBB(self.c, self.u, self.hw + pad, self.hd + pad)

    def angle(self):
        return math.atan2(self.u[1], self.u[0])

    def contains(self, p):
        d = sub(p, self.c)
        return abs(d[0] * self.u[0] + d[1] * self.u[1]) <= self.hw and abs(d[0] * self.v[0] + d[1] * self.v[1]) <= self.hd


def _project(corners, axis):
    vals = [p[0] * axis[0] + p[1] * axis[1] for p in corners]
    return min(vals), max(vals)


def obb_overlap(a, b, eps=1e-6):
    A, B = a.aabb(), b.aabb()
    if A[2] <= B[0] or B[2] <= A[0] or A[3] <= B[1] or B[3] <= A[1]:
        return False
    ca, cb = a.corners(), b.corners()
    for axis in (a.u, a.v, b.u, b.v):
        a0, a1 = _project(ca, axis)
        b0, b1 = _project(cb, axis)
        if a1 <= b0 + eps or b1 <= a0 + eps:
            return False
    return True


def segment_obb(a, b, width):
    """Rectangle covering a segment with the given total width."""
    d = sub(b, a)
    L = length(d)
    if L == 0:
        d, L = (1.0, 0.0), 0.0
    return OBB(lerp(a, b, .5), d, L / 2, width / 2)


# ---------------------------------------------------------------- spatial hash

class SpatialHash:
    def __init__(self, cell=100.0):
        self.cell = cell
        self.buckets = {}

    def _keys(self, aabb):
        c = self.cell
        for ix in range(int(math.floor(aabb[0] / c)), int(math.floor(aabb[2] / c)) + 1):
            for iz in range(int(math.floor(aabb[1] / c)), int(math.floor(aabb[3] / c)) + 1):
                yield (ix, iz)

    def insert(self, aabb, item):
        for k in self._keys(aabb):
            self.buckets.setdefault(k, []).append(item)

    def query(self, aabb):
        seen = set()
        for k in self._keys(aabb):
            for item in self.buckets.get(k, ()):
                if id(item) not in seen:
                    seen.add(id(item))
                    yield item


# ---------------------------------------------------------------- deterministic smooth noise

class Noise2:
    """Sum of randomly oriented sinusoids: smooth, deterministic, cheap (value in roughly [-1, 1])."""

    def __init__(self, rng, wavelength, octaves=3):
        self.waves = []
        for o in range(octaves):
            wl = wavelength / (1.9 ** o)
            for _ in range(2):
                ang = rng.uniform(0, math.pi)
                k = 2 * math.pi / (wl * rng.uniform(.8, 1.25))
                self.waves.append((math.cos(ang) * k, math.sin(ang) * k, rng.uniform(0, 2 * math.pi), .5 ** o))
        self.norm = sum(w[3] for w in self.waves) / 1.6

    def __call__(self, x, z):
        return sum(a * math.sin(kx * x + kz * z + ph) for kx, kz, ph, a in self.waves) / self.norm


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)
