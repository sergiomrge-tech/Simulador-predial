"""Evolution stages of the Resort Aurora site (requires sa_resort): beach stall, kiosk, colonial pousada, hotel block, the Grande Hotel
Palmeiras (ruin and restored), the lighthouse, a tower crane. All geometry is emitted into sa_bl.MeshBuilders using sa_resort slots.
Frames face -Y (the sea) like the rest of the resort kit: u along the facade, d depth inward, z absolute.
"""
import math
import random

import sa_resort as R
from sa_resort import S

# extra slots reuse the resort list; shutters use "azulejo" (blue), slate uses "basalto", red paint uses "terracota"


def stall(fr, z):
    """Stage 1: the beach snack stall: wooden deck, counter, red-and-white awning, cooler, sign. 5.2 x 3.8 m."""
    fr.box(-2.6, 2.6, -1.9, 1.9, z, z + 0.1, S["teca"])
    for px in (-2.4, 2.4):
        for pd in (-1.6, 1.6):
            fr.box(px - 0.06, px + 0.06, pd - 0.06, pd + 0.06, z + 0.1, z + 2.7, S["madeira_escura"])
    for i in range(6):                                                                   # striped awning
        m = S["terracota"] if i % 2 == 0 else S["tecido"]
        fr.box(-2.6 + i * 0.88, -2.6 + (i + 1) * 0.88, -2.2, 2.2, z + 2.65, z + 2.72, m, bottom=True)
    fr.box(-2.1, 2.1, -1.0, -0.3, z + 0.1, z + 1.2, S["teca"])                          # counter (front faces -d: the customers are at d < 0)
    fr.box(-2.2, 2.2, -1.1, -0.2, z + 1.2, z + 1.26, S["marmore"])
    fr.box(-1.9, -0.7, 0.7, 1.4, z + 0.1, z + 1.0, S["aco_preto"])                       # grill
    fr.box(0.9, 2.0, 0.8, 1.5, z + 0.1, z + 0.85, S["azulejo"])                          # cooler
    fr.box(-1.0, 1.0, -1.5, -1.4, z + 2.8, z + 3.3, S["latao"])                           # sign board


def kiosk(fr, z):
    """Stage 2: kiosk with a masonry bar, a big palapa, a timber deck with tables and string lights, a toilet block."""
    fr.box(-11, 11, -9, 5, z, z + 0.25, S["teca"])                                       # deck
    fr.box(-5.5, 5.5, 0.0, 5.0, z + 0.25, z + 3.2, S["estuque"])                         # bar building
    fr.box(-4.0, 4.0, -0.15, 0.15, z + 1.0, z + 2.6, S["vidro"], top=False, back=False, sides=False)
    fr.box(-5.8, 5.8, -1.4, 0.0, z + 0.25, z + 1.15, S["teca"])                          # service counter
    fr.box(-6.0, 6.0, -1.5, 0.1, z + 1.15, z + 1.22, S["marmore"])
    R.thatch_roof(fr, 0, 2.5, z + 3.2, 8.5, 3.6)
    for k in range(4):
        tx = -7.5 + k * 5.0
        fr.box(tx - 0.5, tx + 0.5, -6.0, -5.0, z + 0.25, z + 0.95, S["teca"])
        R.umbrella(fr, tx, -5.5, z + 0.25, r=1.9, h=2.8)
        for dx, dd in ((-0.9, 0), (0.9, 0)):
            fr.box(tx + dx - 0.25, tx + dx + 0.25, -5.75, -5.25, z + 0.25, z + 0.7, S["madeira_escura"])
    fr.box(6.5, 10.0, 0.5, 4.0, z + 0.25, z + 2.6, S["estuque"])                         # toilets
    fr.box(6.3, 10.2, 0.3, 4.2, z + 2.6, z + 2.8, S["terracota"])
    for k in range(7):                                                                    # string lights on posts
        px = -10.5 + k * 3.5
        fr.cyl(px, -8.4, z + 0.25, 0.05, 3.0, 6, S["madeira_escura"])
        fr.box(px - 0.12, px + 0.12, -8.52, -8.28, z + 3.0, z + 3.24, S["luz"])


def sobrado(fr, z, L=16.0, D=11.0, seed=0):
    """Stage 3: the colonial sobrado of Seu Tonico: two floors, white lime walls, terracotta hip roof, blue shutters, timber balcony, garden wall."""
    rng = random.Random(seed)
    fr.box(0, L, 0, D, z, z + 0.5, S["travertino"])                                      # plinth
    fr.box(0, L, 0, D, z + 0.5, z + 7.0, S["estuque"])
    for fl, zb in ((0, z + 0.5), (1, z + 3.9)):
        for k in range(4):                                                                # windows with blue shutters
            u = 1.6 + k * 3.5
            fr.box(u, u + 1.1, -0.04, 0.04, zb + 0.6, zb + 2.2, S["vidro"], top=False, back=False, sides=False)
            fr.box(u - 0.5, u - 0.05, -0.12, 0.0, zb + 0.55, zb + 2.25, S["azulejo"])
            fr.box(u + 1.15, u + 1.6, -0.12, 0.0, zb + 0.55, zb + 2.25, S["azulejo"])
            fr.box(u - 0.08, u + 1.2, -0.1, 0.05, zb + 2.2, zb + 2.3, S["travertino"])
    fr.box(L / 2 - 0.9, L / 2 + 0.9, -0.1, 0.1, z + 0.5, z + 2.9, S["madeira_escura"])   # arched front door (rectangular read)
    fr.box(0.0, L, -2.2, 0.0, z + 3.7, z + 3.9, S["teca"])                               # first-floor balcony slab
    fr.box(0.0, L, -2.2, -2.1, z + 3.9, z + 4.9, S["teca"], top=False)
    for k in range(int(L / 0.35)):
        fr.box(k * 0.35, k * 0.35 + 0.06, -2.18, -2.12, z + 3.9, z + 4.9, S["madeira_escura"], top=False)
    for k in range(5):
        fr.cyl(k * L / 4, -2.0, z + 0.5, 0.12, 3.2, 10, S["teca"])                       # turned posts
    R.hip_roof(fr, -0.8, L + 0.8, -3.2, D + 0.8, z + 7.0, 3.6, S["terracota"], ridge=0.2)
    fr.box(L * 0.7, L * 0.7 + 1.0, D * 0.6, D * 0.6 + 1.0, z + 7.0, z + 9.4, S["estuque"])   # chimney
    fr.box(-3, L + 3, -11, -10.5, z, z + 1.6, S["estuque"])                              # garden wall with gate
    fr.box(L / 2 - 1.2, L / 2 + 1.2, -11.1, -10.4, z, z + 2.2, S["aco_preto"], top=False)


def hotel_block(fr, z, L=60.0, floors=5, seed=0):
    """Stage 4: the first real hotel: a loggia-and-balcony wing plus a small gabled lobby, set around a pool court."""
    R.wing(fr, L, 16, z, floors, seed=seed, pitched=False)
    R.lobby(fr.shift(L / 2 - 14, -12), 28, 9, z, H=5.5)


# ------------------------------------------------------------------------------------------------ Grande Hotel Palmeiras

def grand_hotel(fr, z, ruin=False, seed=3):
    """Grande Hotel Palmeiras (1968): 90 x 26 m, three floors on an arcaded plinth, central portico with pediment and clock tower, mansard roof
    with dormers, projecting end pavilions. ruin=True removes bays, collapses roof planes and the tower, boards windows and grows vines."""
    rng = random.Random(seed)
    L, D = 90.0, 26.0
    zb = z + 0.9
    fr.box(-1, L + 1, -9, D + 1, z, zb, S["travertino"], bottom=True)                    # plinth / terrace
    # ground floor: arcade (open loggia) along the full length
    keep = lambda p: (not ruin) or rng.random() > p
    arc = fr.shift(0.0, -3.0)
    R.arcade(arc, L, 20, zb, zb + 4.6, depth=1.0, pier=1.0)
    fr.box(0, L, 0, D, zb, zb + 4.6, S["estuque"], front=False, top=False)
    # upper floors: pilasters, tall windows with marble frames, balconies on the central bays
    for fl in range(2):
        z0 = zb + 4.6 + fl * 4.6
        fr.box(-0.6, L + 0.6, -3.1, D + 0.6, z0, z0 + 0.35, S["marmore"], bottom=True)   # cornice / floor band
        fr.box(0, L, 0, D, z0 + 0.35, z0 + 4.6, S["estuque"])
        for k in range(20):
            u = (k + 0.5) * L / 20
            if ruin and rng.random() < 0.22:
                continue                                                                     # a missing bay (collapsed facade)
            boarded = ruin and rng.random() < 0.55
            fr.box(u - 0.9, u + 0.9, -0.12, 0.05, z0 + 0.8, z0 + 3.7, S["madeira_escura"] if boarded else S["vidro"], top=False, back=False, sides=False)
            fr.box(u - 1.1, u - 0.9, -0.18, 0.05, z0 + 0.7, z0 + 3.8, S["marmore"])
            fr.box(u + 0.9, u + 1.1, -0.18, 0.05, z0 + 0.7, z0 + 3.8, S["marmore"])
            fr.box(u - 1.1, u + 1.1, -0.2, 0.05, z0 + 3.7, z0 + 3.9, S["marmore"])
            if fl == 0 and 32 < u < 58 and keep(0.3):                                       # balconies with balusters on the central bays
                fr.box(u - 1.2, u + 1.2, -1.2, 0.0, z0 + 0.35, z0 + 0.55, S["marmore"])
                for b in range(8):
                    fr.box(u - 1.1 + b * 0.3, u - 0.95 + b * 0.3, -1.15, -1.05, z0 + 0.55, z0 + 1.3, S["marmore"], top=False)
                fr.box(u - 1.25, u + 1.25, -1.25, -1.0, z0 + 1.3, z0 + 1.4, S["marmore"])
        for k in range(21):                                                                  # pilasters between the bays
            u = k * L / 20
            fr.box(u - 0.4, u + 0.4, -0.35, 0.0, z0 + 0.35, z0 + 4.6, S["travertino"])
    zt = zb + 4.6 + 9.2 + 0.35
    fr.box(-0.8, L + 0.8, -1.2, D + 1.0, zt, zt + 0.5, S["marmore"], bottom=True)        # main cornice
    # central portico: eight columns, entablature, triangular pediment
    pu0 = L / 2 - 14
    for k in range(8):
        u = pu0 + k * 28 / 7
        if ruin and rng.random() < 0.3:
            fr.cyl(u, -6.5, zb, 0.62, rng.uniform(2.5, 6.0), 18, S["travertino"])           # broken column stump
            continue
        fr.cyl(u, -6.5, zb, 0.62, 9.6, 18, S["marmore"])
        fr.box(u - 0.85, u + 0.85, -7.35, -5.65, zb + 9.6, zb + 10.2, S["travertino"])   # capital
        fr.box(u - 0.8, u + 0.8, -7.3, -5.7, zb, zb + 0.4, S["travertino"])
    if not ruin or rng.random() > 0.35:
        fr.box(pu0 - 1.2, pu0 + 29.2, -8.0, 0.0, zb + 10.2, zb + 11.4, S["marmore"], bottom=True)
        peak = zb + 11.4 + 4.6
        fr.mb.add_face([fr.P(pu0 - 1.2, -8.0, zb + 11.4), fr.P(pu0 + 29.2, -8.0, zb + 11.4), fr.P(L / 2, -8.0, peak)], S["estuque"])
        fr.mb.add_face([fr.P(pu0 + 29.2, 0.0, zb + 11.4), fr.P(pu0 - 1.2, 0.0, zb + 11.4), fr.P(L / 2, 0.0, peak)], S["estuque"])
        fr.quad((pu0 - 1.2, -8.0, zb + 11.4), (pu0 + 29.2, -8.0, zb + 11.4), (L / 2 + 0, -8.0 + 0.0, peak), (L / 2, -8.0, peak), S["terracota"])
        fr.mb.add_face([fr.P(pu0 - 1.2, 0.0, zb + 11.4), fr.P(pu0 - 1.2, -8.0, zb + 11.4), fr.P(L / 2, -8.0, peak), fr.P(L / 2, 0.0, peak)], S["basalto"])
        fr.mb.add_face([fr.P(pu0 + 29.2, -8.0, zb + 11.4), fr.P(pu0 + 29.2, 0.0, zb + 11.4), fr.P(L / 2, 0.0, peak), fr.P(L / 2, -8.0, peak)], S["basalto"])
    for k in range(5):
        fr.box(pu0 - 1.0, pu0 + 29.0, -9.5 - (4 - k) * 0.6, -7.0, z + k * 0.18, z + (k + 1) * 0.18, S["travertino"])
    # mansard roof: slate planes with dormers; terracotta ridge cap; collapses in ruin
    rz = zt + 0.5
    rise = 5.2
    planes = [((-0.8, -1.2), (L + 0.8, -1.2), (L - 6, 6.0), (6, 6.0)), ((L + 0.8, D + 1.0), (-0.8, D + 1.0), (6, D - 6.0), (L - 6, D - 6.0))]
    for (a, b, c, d) in planes:
        if ruin and rng.random() < 0.5:
            for r_ in range(7):                                                              # bare rafters where the roof fell in
                u = a[0] + (b[0] - a[0]) * (r_ / 6)
                fr.box(u - 0.08, u + 0.08, a[1] if a[1] < 5 else 18.0, a[1] + 3.2 if a[1] < 5 else 24.0, rz, rz + 3.0, S["madeira_escura"])
            continue
        fr.quad((a[0], a[1], rz), (b[0], b[1], rz), (c[0], c[1], rz + rise), (d[0], d[1], rz + rise), S["basalto"])
    for (a, b, c, d) in ((( -0.8, D + 1.0), (-0.8, -1.2), (6, 6.0), (6, D - 6.0)), ((L + 0.8, -1.2), (L + 0.8, D + 1.0), (L - 6, D - 6.0), (L - 6, 6.0))):
        fr.quad((a[0], a[1], rz), (b[0], b[1], rz), (c[0], c[1], rz + rise), (d[0], d[1], rz + rise), S["basalto"])
    fr.quad((6, 6.0, rz + rise), (L - 6, 6.0, rz + rise), (L - 6, D - 6.0, rz + rise), (6, D - 6.0, rz + rise), S["basalto"])
    for k in range(9):
        u = 8 + k * 9.2
        if ruin and rng.random() < 0.4:
            continue
        fr.box(u - 0.9, u + 0.9, 0.0, 1.8, rz + 0.8, rz + 3.0, S["estuque"])
        fr.box(u - 0.5, u + 0.5, -0.05, 0.0, rz + 1.2, rz + 2.6, S["madeira_escura"] if ruin else S["vidro"], top=False, back=False, sides=False)
        fr.box(u - 1.1, u + 1.1, -0.2, 2.0, rz + 3.0, rz + 3.25, S["terracota"])
    # central clock tower with a dome (collapsed in ruin)
    tu, td = L / 2, 12.0
    if not ruin:
        fr.box(tu - 4, tu + 4, td - 4, td + 4, rz, rz + 12.0, S["estuque"])
        fr.box(tu - 4.4, tu + 4.4, td - 4.4, td + 4.4, rz + 12.0, rz + 12.6, S["marmore"])
        fr.cyl(tu, td - 4.05, rz + 8.0, 1.3, 0.1, 20, S["marmore"])                         # clock face (disc on the south side)
        R.dome(fr, tu, td, rz + 12.6, r=3.6, drum_h=2.6, mat=S["basalto"])
    else:
        fr.box(tu - 4, tu + 4, td - 4, td + 4, rz, rz + rng.uniform(4.0, 7.0), S["estuque"])
    # end pavilions with hip roofs
    for ua in (-6.0, L - 6.0):
        fr.box(ua + 2, ua + 12, -2.0, D + 1, zb + 4.6 + 9.2, zb + 4.6 + 9.2 + 0.3, S["marmore"])
    if ruin:                                                                                 # vines and rubble
        for k in range(45):
            u = rng.uniform(0, L)
            R.blob(fr.mb, fr.P(u, -0.3, zb + rng.uniform(0.5, 12.0)), rng.uniform(0.5, 1.4), S["verde"], seed=k, rings=4, segs=7)
        for k in range(14):
            u = rng.uniform(5, L - 5)
            fr.box(u - 1.2, u + 1.2, -5 - rng.uniform(0, 3), -3 - rng.uniform(0, 3), zb, zb + rng.uniform(0.4, 1.1), S["concreto"])


# ------------------------------------------------------------------------------------------------ lighthouse + crane

def lighthouse(fr, u, d, z, lit=False):
    """Farol de Santa Aurora: 38 m tapered tower in red and white bands, gallery, lantern room and dome, plus the keeper's house."""
    x, y, _ = fr.P(u, d, z)
    mb = fr.mb
    mb.cylinder(x, y, z, 6.6, 1.6, 24, S["travertino"], top=True)                         # base platform
    h, segs, bands = 38.0, 28, 9
    for b in range(bands):
        r0 = 4.2 - 1.6 * (b / bands)
        r1 = 4.2 - 1.6 * ((b + 1) / bands)
        zb0, zb1 = z + 1.6 + b * h / bands, z + 1.6 + (b + 1) * h / bands
        m = S["terracota"] if b % 2 == 0 else S["estuque"]
        ring0 = [(x + r0 * math.cos(2 * math.pi * k / segs), y + r0 * math.sin(2 * math.pi * k / segs), zb0) for k in range(segs)]
        ring1 = [(x + r1 * math.cos(2 * math.pi * k / segs), y + r1 * math.sin(2 * math.pi * k / segs), zb1) for k in range(segs)]
        for k in range(segs):
            j = (k + 1) % segs
            mb.quad(ring0[k], ring0[j], ring1[j], ring1[k], m)
    zg = z + 1.6 + h
    mb.cylinder(x, y, zg, 3.6, 0.5, 28, S["aco_preto"])
    for k in range(24):                                                                   # gallery railing
        a = 2 * math.pi * k / 24
        mb.cylinder(x + 3.4 * math.cos(a), y + 3.4 * math.sin(a), zg + 0.5, 0.04, 1.1, 5, S["aco_preto"])
    mb.cylinder(x, y, zg + 0.5, 2.0, 3.4, 20, S["luz"] if lit else S["vidro"], top=False)
    for k in range(8):
        a = 2 * math.pi * k / 8
        mb.cylinder(x + 2.02 * math.cos(a), y + 2.02 * math.sin(a), zg + 0.5, 0.06, 3.4, 5, S["latao"])
    mb.cylinder(x, y, zg + 3.9, 2.4, 0.3, 24, S["aco_preto"])
    prev = [(x + 2.2 * math.cos(2 * math.pi * k / 20), y + 2.2 * math.sin(2 * math.pi * k / 20), zg + 4.2) for k in range(20)]
    for i in range(1, 6):
        phi = (math.pi / 2) * i / 6
        cur = [(x + 2.2 * math.cos(phi) * math.cos(2 * math.pi * k / 20), y + 2.2 * math.cos(phi) * math.sin(2 * math.pi * k / 20), zg + 4.2 + 2.0 * math.sin(phi)) for k in range(20)]
        for k in range(20):
            mb.quad(prev[k], prev[(k + 1) % 20], cur[(k + 1) % 20], cur[k], S["aco_preto"])
        prev = cur
    mb.cylinder(x, y, zg + 6.2, 0.06, 1.6, 6, S["latao"])
    kh = R.Frame(mb, (x + 9.0, y - 3.0), 0.0)                                              # keeper's house
    kh.box(0, 11, 0, 7, z, z + 3.6, S["estuque"])
    R.hip_roof(kh, -0.8, 11.8, -0.8, 7.8, z + 3.6, 2.4, S["terracota"], ridge=0.25)
    kh.box(1.0, 2.2, -0.05, 0.05, z + 0.4, z + 2.6, S["madeira_escura"])
    for k in range(3):
        kh.box(4 + k * 2.2, 5.4 + k * 2.2, -0.05, 0.05, z + 1.0, z + 2.5, S["vidro"], top=False, back=False, sides=False)


def crane(fr, u, d, z, h=46.0, boom=42.0):
    """Tower crane for the construction stage: lattice mast (four chords + diagonals), slewing unit, jib with counterweight and hook."""
    for dx in (-1.0, 1.0):
        for dd in (-1.0, 1.0):
            fr.box(u + dx - 0.1, u + dx + 0.1, d + dd - 0.1, d + dd + 0.1, z, z + h, S["latao"])
    steps = int(h / 3.0)
    for k in range(steps):
        zz = z + k * 3.0
        for dx, dd, ex, ed in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
            fr.box(min(u + dx, u + ex) - 0.04, max(u + dx, u + ex) + 0.04, min(d + dd, d + ed) - 0.04, max(d + dd, d + ed) + 0.04, zz + 2.9, zz + 3.0, S["latao"])
        fr.box(u - 1.0, u + 1.0, d - 1.0, d + 1.0, zz + 1.4, zz + 1.5, S["latao"], top=False)
    zt = z + h
    fr.box(u - 1.5, u + 1.5, d - 1.5, d + 1.5, zt, zt + 2.0, S["latao"])                  # slewing unit + cab
    fr.box(u - 0.8, u + 0.8, d - 2.2, d - 1.4, zt + 0.4, zt + 1.8, S["vidro"], top=True)
    fr.box(u - 0.5, u + 0.5, d - 0.5, d + boom, zt + 2.0, zt + 2.5, S["latao"])             # jib
    fr.box(u - 0.4, u + 0.4, d - 12.0, d - 0.5, zt + 2.0, zt + 2.4, S["latao"])             # counter-jib
    fr.box(u - 1.2, u + 1.2, d - 12.0, d - 9.0, zt + 0.6, zt + 2.6, S["concreto"])          # counterweight
    fr.box(u - 0.05, u + 0.05, d + boom * 0.75 - 0.05, d + boom * 0.75 + 0.05, zt - 12.0, zt + 2.0, S["aco_preto"])   # hoist cable
    fr.box(u - 0.4, u + 0.4, d + boom * 0.75 - 0.4, d + boom * 0.75 + 0.4, zt - 13.0, zt - 12.0, S["aco_preto"])      # hook block
