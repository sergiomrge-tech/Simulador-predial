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
    """Stage 2: the kiosk. Built around the stall's play area (same origin and counter line), so the gameplay stations keep working inside it:
    an open bar under a big palapa (service counter at d -1.0..-0.3, kitchen island and back bar inside), a timber deck with tables and
    parasols, string lights and a toilet block. Frame faces the walkers (d < 0 = promenade)."""
    fr.box(-9.5, 9.5, -3.4, 9.5, z, z + 0.14, S["teca"])                                   # deck
    for px in (-4.4, 4.4):
        for pd in (-1.7, 5.4):
            fr.cyl(px, pd, z + 0.14, 0.14, 3.3, 10, S["madeira_escura"])                    # roof posts
    fr.box(-4.4, 4.4, -1.15, -0.2, z + 0.14, z + 1.12, S["teca"])                          # service counter (front)
    fr.box(-4.6, 4.6, -1.3, 0.0, z + 1.12, z + 1.2, S["marmore"])
    for k in range(9):
        fr.box(-4.2 + k * 1.05, -3.6 + k * 1.05, -1.17, -1.14, z + 0.2, z + 1.0, S["madeira_escura"], top=False)   # slatted front
    fr.box(-3.4, -0.2, 0.7, 1.6, z + 0.14, z + 0.95, S["aco_preto"])        # kitchen island
    fr.box(-3.5, -0.1, 0.6, 1.7, z + 0.95, z + 1.0, S["marmore"])
    fr.box(-3.0, -0.6, 1.1, 1.5, z + 2.2, z + 2.9, S["aco_preto"], bottom=True)           # hood over the grill
    fr.box(-4.2, 4.2, 5.2, 5.5, z + 0.14, z + 2.3, S["madeira_escura"])                      # back wall with shelves
    for k in range(3):
        fr.box(-3.8, 3.8, 4.9, 5.2, z + 0.9 + k * 0.5, z + 0.95 + k * 0.5, S["teca"])
        for j in range(12):
            fr.cyl(-3.4 + j * 0.62, 5.05, z + 0.95 + k * 0.5, 0.06, 0.3, 6, S["vidro"])      # bottles
    fr.box(2.0, 3.6, 3.0, 4.2, z + 0.14, z + 1.7, S["aco_preto"])                           # fridge
    R.thatch_roof(fr, 0, 2.6, z + 3.3, 7.8, 3.8)
    for side in (-1, 1):                                                                   # tables with parasols on the deck wings
        for k in range(3):
            tx, td = side * 7.0, 1.0 + k * 3.0
            fr.box(tx - 0.5, tx + 0.5, td - 0.5, td + 0.5, z + 0.14, z + 0.9, S["teca"])
            R.umbrella(fr, tx, td, z + 0.14, r=1.9, h=2.8)
            for dx in (-0.9, 0.9):
                fr.box(tx + dx - 0.25, tx + dx + 0.25, td - 0.25, td + 0.25, z + 0.14, z + 0.7, S["madeira_escura"])
    fr.box(5.6, 9.2, 6.2, 9.2, z + 0.14, z + 2.6, S["estuque"])                              # toilets
    fr.box(5.4, 9.4, 6.0, 9.4, z + 2.6, z + 2.8, S["terracota"])
    for k in range(7):                                                                      # string lights
        px = -9.0 + k * 3.0
        fr.cyl(px, -3.0, z + 0.14, 0.05, 3.0, 6, S["madeira_escura"])
        fr.box(px - 0.12, px + 0.12, -3.12, -2.88, z + 3.0, z + 3.24, S["luz"])


def _wall(fr, axis, pos, thick, a0, a1, z0, z1, mat, openings=()):
    """Wall segment with rectangular openings. axis u runs along u at depth pos (thickness along d); axis d runs along d at u = pos.
    openings: (a0, a1, zb, zt) in the wall own coordinate."""
    cur = a0
    for (o0, o1, zb, zt) in sorted(openings):
        if o0 > cur:
            _seg(fr, axis, pos, thick, cur, o0, z0, z1, mat)
        _seg(fr, axis, pos, thick, o0, o1, z0, zb, mat)
        _seg(fr, axis, pos, thick, o0, o1, zt, z1, mat)
        cur = o1
    if cur < a1:
        _seg(fr, axis, pos, thick, cur, a1, z0, z1, mat)


def _seg(fr, axis, pos, thick, a0, a1, z0, z1, mat):
    if a1 - a0 < 1e-3 or z1 - z0 < 1e-3:
        return
    if axis == "u":
        fr.box(a0, a1, pos, pos + thick, z0, z1, mat)
    else:
        fr.box(pos, pos + thick, a0, a1, z0, z1, mat)


def _bed(fr, u, d, z):
    """Double bed with headboard, pillows and a duvet; head against the wall at larger d."""
    fr.box(u, u + 1.6, d, d + 2.0, z + 0.05, z + 0.4, S["madeira_escura"])
    fr.box(u + 0.05, u + 1.55, d + 0.05, d + 1.95, z + 0.4, z + 0.6, S["tecido"])
    fr.box(u + 0.05, u + 1.55, d + 0.1, d + 1.2, z + 0.6, z + 0.66, S["terracota"])
    fr.box(u, u + 1.6, d + 1.9, d + 2.0, z + 0.05, z + 1.2, S["teca"])
    for k in range(2):
        fr.box(u + 0.15 + k * 0.75, u + 0.8 + k * 0.75, d + 1.45, d + 1.85, z + 0.6, z + 0.75, S["tecido"])


def sobrado(fr, z, L=16.0, D=11.0, seed=0):
    """Stage 3: the colonial sobrado of Seu Tonico, with a real interior. Ground floor: reception and breakfast room at the front, a stair
    corridor, kitchen and laundry at the back. Upper floor: a corridor and six rooms (three facing the sea). White lime walls, terracotta hip
    roof, blue shutters, timber balcony; the garden gate is open so the player can walk in."""
    T = 0.25
    zg = z + 0.5                       # ground floor level
    zs = z + 3.9                       # first-floor slab (top)
    zu = zs + 0.25                     # first-floor level
    zr = z + 7.0                       # eave
    fr.box(0, L, 0, D, z, zg, S["travertino"])                                           # plinth slab
    ground_ops = [(1.6, 2.7, zg + 0.6, zg + 2.3), (4.4, 5.5, zg + 0.6, zg + 2.3), (7.1, 8.9, zg, zg + 2.7), (10.4, 11.5, zg + 0.6, zg + 2.3), (13.3, 14.4, zg + 0.6, zg + 2.3)]
    upper_ops = [(1.6 + k * 3.4, 2.7 + k * 3.4, zu + 0.6, zu + 2.3) for k in range(4)] + [(13.4, 14.5, zu + 0.6, zu + 2.3)]
    _wall(fr, "u", 0.0, T, 0, L, zg, zs, S["estuque"], ground_ops)
    _wall(fr, "u", 0.0, T, 0, L, zu, zr + 0.3, S["estuque"], upper_ops)
    _wall(fr, "d", 0.0, T, 0, D, zg, zr + 0.3, S["estuque"])
    _wall(fr, "d", L - T, T, 0, D, zg, zr + 0.3, S["estuque"], [(5.0, 6.4, zu - 0.12, zu + 2.45)])   # upper door onto the outdoor stair (sill sunk under the floor strip below)
    _wall(fr, "u", D - T, T, 0, L, zg, zr + 0.3, S["estuque"],
          [(3.0, 4.2, zg + 0.9, zg + 2.5), (11.0, 12.2, zg + 0.9, zg + 2.5), (2.0, 3.2, zu + 0.9, zu + 2.3), (7.0, 8.2, zu + 0.9, zu + 2.3), (12.0, 13.2, zu + 0.9, zu + 2.3)])
    for (o0, o1, zb, zt) in ground_ops[:2] + ground_ops[3:] + upper_ops:                  # glass, blue shutters and sills in the front openings
        fr.box(o0, o1, 0.08, 0.14, zb, zt, S["vidro"], top=False, bottom=False, back=False, sides=False)
        fr.box(o0 - 0.5, o0 - 0.05, -0.1, 0.0, zb - 0.05, zt + 0.05, S["azulejo"])
        fr.box(o1 + 0.05, o1 + 0.5, -0.1, 0.0, zb - 0.05, zt + 0.05, S["azulejo"])
        fr.box(o0 - 0.08, o1 + 0.08, -0.1, 0.1, zt, zt + 0.1, S["travertino"])
        fr.box(o0 - 0.08, o1 + 0.08, -0.14, 0.08, zb - 0.08, zb, S["travertino"])
    fr.box(7.1, 8.9, 0.0, 0.1, zg + 2.7, zg + 2.85, S["madeira_escura"])                  # door lintel (the door itself stands open)
    # first-floor slab (the stair is outdoors, along the east wall)
    fr.box(0, L, 0, D, zs - 0.25, zs, S["concreto"], bottom=True, top=False)
    fr.box(0, L, 0, D, zs, zu, S["teca"], bottom=False)
    fr.box(0, L, 0, D, zg, zg + 0.04, S["marmore"])                                        # ground floor tiles
    fr.box(0, L, 0, D, zr - 0.2, zr, S["estuque"], bottom=True, top=False)                 # upper ceiling
    # ground floor partitions (doorways keep it walkable)
    _wall(fr, "u", 5.0, 0.15, 0.0, L, zg, zs - 0.25, S["estuque"], [(2.5, 3.7, zg, zg + 2.5), (11.0, 12.2, zg, zg + 2.5)])
    _wall(fr, "u", 6.4, 0.15, 0.0, L, zg, zs - 0.25, S["estuque"], [(3.0, 4.2, zg, zg + 2.5), (5.0, 6.2, zg, zg + 2.5)])
    _wall(fr, "d", 8.0, 0.15, 0.0, 5.0, zg, zs - 0.25, S["estuque"], [(1.6, 2.8, zg, zg + 2.5)])
    _wall(fr, "d", 8.0, 0.15, 6.4, D, zg, zs - 0.25, S["estuque"], [(8.2, 9.4, zg, zg + 2.5)])
    fr.box(0.8, 3.4, 1.4, 2.2, zg + 0.04, zg + 1.1, S["madeira_escura"])                   # reception desk
    fr.box(0.7, 3.5, 1.3, 2.3, zg + 1.1, zg + 1.16, S["marmore"])
    fr.box(5.0, 7.6, 3.4, 4.6, zg + 0.04, zg + 0.45, S["tecido"])                           # sofa
    fr.box(5.0, 7.6, 4.3, 4.6, zg + 0.45, zg + 0.95, S["tecido"])
    for k in range(3):                                                                      # breakfast tables
        tx, td = 9.5 + (k % 2) * 3.4, 1.4 + (k // 2) * 2.6
        fr.box(tx, tx + 1.2, td, td + 1.2, zg + 0.04, zg + 0.78, S["teca"])
        for dx, dd in ((-0.45, 0.3), (1.45, 0.3)):
            fr.box(tx + dx, tx + dx + 0.4, td + dd, td + dd + 0.4, zg + 0.04, zg + 0.5, S["madeira_escura"])
    fr.box(0.4, 7.6, D - 1.2, D - 0.3, zg + 0.04, zg + 0.9, S["aco_preto"])                 # kitchen counter
    fr.box(0.3, 7.7, D - 1.3, D - 0.2, zg + 0.9, zg + 0.95, S["marmore"])
    fr.box(9.0, 14.5, D - 1.2, D - 0.3, zg + 0.04, zg + 1.0, S["tecido"])                   # laundry shelves
    nst = 21                                                                                # outdoor stair along the east wall, rising toward the front
    for k in range(nst):
        dd = 13.6 - (k + 1) * (7.2 / nst)
        fr.box(L, L + 1.3, dd, dd + 7.2 / nst + 0.02, z, z + (k + 1) * (zu - z) / nst, S["travertino"])
    fr.box(L - 0.6, L + 1.6, 4.9, 6.5, zu - 0.35, zu, S["teca"])                          # landing + threshold: one continuous slab under the doorway (no seam)
    for k in range(nst):                                                                  # open guard rail following the flight
        dd = 13.6 - (k + 1) * (7.2 / nst)
        top = z + (k + 1) * (zu - z) / nst
        fr.box(L + 1.2, L + 1.3, dd, dd + 7.2 / nst + 0.02, top, top + 0.95, S["madeira_escura"], top=False)
    fr.box(L + 1.2, L + 1.3, 4.9, 6.5, zu, zu + 0.95, S["madeira_escura"], top=False)
    # upper floor: corridor d 5.0..6.4, three sea-facing rooms in front, three at the back
    for u in (5.33, 10.66):
        _wall(fr, "d", u, 0.15, 0.0, 5.0, zu, zr - 0.2, S["estuque"])
        _wall(fr, "d", u, 0.15, 6.4, D, zu, zr - 0.2, S["estuque"])
    _wall(fr, "u", 4.85, 0.15, 0.0, L, zu, zr - 0.2, S["estuque"], [(2.0, 3.0, zu, zu + 2.45), (7.4, 8.4, zu, zu + 2.45), (12.7, 13.7, zu, zu + 2.45)])
    _wall(fr, "u", 6.4, 0.15, 0.0, 10.9, zu, zr - 0.2, S["estuque"], [(2.0, 3.0, zu, zu + 2.45), (6.2, 7.2, zu, zu + 2.45)])
    for k in range(3):                                                                      # front rooms
        u0 = 0.4 + k * 5.33
        _bed(fr, u0 + 1.2, 2.4, zu)
        fr.box(u0 + 0.4, u0 + 0.9, 3.9, 4.4, zu, zu + 0.5, S["madeira_escura"])
        fr.box(u0 + 3.0, u0 + 3.5, 3.9, 4.4, zu, zu + 0.5, S["madeira_escura"])
        fr.box(u0 + 0.5, u0 + 1.6, 0.5, 1.4, zu, zu + 0.75, S["teca"])
    for k in range(3):                                                                      # back rooms
        u0 = 0.4 + k * 5.33
        _bed(fr, u0 + 1.4, 7.6, zu)
        fr.box(u0 + 0.3, u0 + 0.8, 9.6, 10.2, zu, zu + 0.5, S["madeira_escura"])
        fr.box(u0 + 3.4, u0 + 4.7, 10.1, 10.7, zu, zu + 2.1, S["madeira_escura"])
    fr.box(0.0, L, -2.2, 0.0, zs - 0.2, zs, S["teca"])                                      # balcony and outer details
    fr.box(0.0, L, -2.2, -2.1, zs, zs + 1.0, S["teca"], top=False)
    for k in range(int(L / 0.35)):
        fr.box(k * 0.35, k * 0.35 + 0.06, -2.18, -2.12, zs, zs + 1.0, S["madeira_escura"], top=False)
    for k in range(5):
        fr.cyl(k * L / 4, -2.0, zg, 0.12, zs - zg - 0.2, 10, S["teca"])
    R.hip_roof(fr, -0.8, L + 0.8, -3.2, D + 0.8, zr, 3.6, S["terracota"], ridge=0.2, drop=0.3)
    fr.box(L * 0.7, L * 0.7 + 1.0, D * 0.6, D * 0.6 + 1.0, zr, zr + 2.4, S["estuque"])      # chimney
    gx0, gx1 = L / 2 - 1.3, L / 2 + 1.3                                                     # garden wall with an open gate
    fr.box(-3, gx0, -11, -10.6, z, z + 1.6, S["estuque"])
    fr.box(gx1, L + 3, -11, -10.6, z, z + 1.6, S["estuque"])
    for gx in (gx0 - 0.15, gx1 - 0.1):
        fr.box(gx, gx + 0.25, -11.1, -10.5, z, z + 2.3, S["travertino"])
        fr.box(gx - 0.05, gx + 0.3, -11.15, -10.45, z + 2.3, z + 2.45, S["marmore"])
    fr.box(L / 2 - 0.9, L / 2 + 0.9, -10.0, 0.0, z + 0.02, z + 0.08, S["terracota"])        # path from the gate to the door


def lar(fr, z):
    """Edifício Santa Clara, Apto 12: the player's kitnet. One floor, 12 x 8 m: kitchenette, table, bed against the back wall, a small
    bathroom behind a partition. Door 1.4 x 2.5 m on the front (d = 0), windows to the sea, flat roof with parapet and a small awning.
    The bed sits at u 8.4..10.0, d 5.6..7.6 (the game places the sleep interaction there)."""
    L, D, H, T = 12.0, 8.0, 3.4, 0.25
    zf = z + 0.15
    fr.box(-0.5, L + 0.5, -2.0, D + 0.5, z, zf, S["travertino"])                          # plinth and doorstep
    fr.box(0, L, 0, D, zf, zf + 0.04, S["teca"])                                           # floor
    ops = [(1.0, 2.8, zf + 0.9, zf + 2.4), (5.4, 6.8, zf, zf + 2.5), (9.0, 11.0, zf + 0.9, zf + 2.4)]
    _wall(fr, "u", 0.0, T, 0, L, zf, zf + H, S["estuque"], ops)
    _wall(fr, "d", 0.0, T, 0, D, zf, zf + H, S["estuque"])
    _wall(fr, "d", L - T, T, 0, D, zf, zf + H, S["estuque"])
    _wall(fr, "u", D - T, T, 0, L, zf, zf + H, S["estuque"], [(7.0, 10.6, zf + 1.2, zf + 2.3)])
    for (o0, o1, zb, zt) in (ops[0], ops[2]):
        fr.box(o0, o1, 0.08, 0.14, zb, zt, S["vidro"], top=False, bottom=False, back=False, sides=False)
        fr.box(o0 - 0.4, o0 - 0.05, -0.1, 0.0, zb - 0.05, zt + 0.05, S["azulejo"])
        fr.box(o1 + 0.05, o1 + 0.4, -0.1, 0.0, zb - 0.05, zt + 0.05, S["azulejo"])
    fr.box(7.0, 10.6, D - 0.35, D - 0.28, zf + 1.2, zf + 2.3, S["vidro"], top=False, bottom=False, back=False, sides=False)
    fr.box(0, L, 0, D, zf + H - 0.2, zf + H, S["concreto"], bottom=True, top=True)         # roof slab
    fr.box(-0.2, L + 0.2, -0.2, D + 0.2, zf + H, zf + H + 0.5, S["estuque"], top=False)    # parapet ring
    fr.box(0.1, L - 0.1, 0.1, D - 0.1, zf + H, zf + H + 0.04, S["concreto"])
    fr.box(4.6, 7.6, -1.6, 0.0, zf + 2.75, zf + 2.85, S["terracota"], bottom=True)         # small awning over the door
    for px in (4.7, 7.5):
        fr.cyl(px, -1.5, zf, 0.06, 2.75, 8, S["madeira_escura"])
    # bathroom (back left) behind a partition with a door
    _wall(fr, "u", 4.5, 0.12, 0, 3.4, zf, zf + 2.9, S["estuque"], [(0.6, 1.7, zf, zf + 2.5)])
    _wall(fr, "d", 3.3, 0.12, 4.5, D, zf, zf + 2.9, S["estuque"])
    fr.box(0.1, 3.2, 4.6, D - 0.2, zf + 0.04, zf + 0.06, S["marmore"])
    fr.box(0.3, 1.1, D - 0.9, D - 0.3, zf + 0.06, zf + 0.45, S["marmore"])                  # toilet
    fr.box(2.0, 3.1, D - 0.7, D - 0.3, zf + 0.06, zf + 0.85, S["madeira_escura"])           # vanity
    fr.box(2.0, 3.1, D - 0.7, D - 0.3, zf + 0.85, zf + 0.9, S["marmore"])
    fr.box(0.1, 1.0, 5.0, 6.2, zf + 0.06, zf + 0.12, S["azulejo"])                          # shower tray
    # kitchenette on the left wall, table in the middle
    fr.box(0.3, 2.9, 0.4, 1.1, zf + 0.04, zf + 0.9, S["madeira_escura"])
    fr.box(0.2, 3.0, 0.3, 1.2, zf + 0.9, zf + 0.95, S["marmore"])
    fr.box(3.2, 4.1, 0.4, 1.1, zf + 0.04, zf + 1.8, S["aco_preto"])                          # fridge
    fr.box(4.2, 5.6, 2.2, 3.4, zf + 0.04, zf + 0.76, S["teca"])                              # table
    for dx, dd in ((-0.5, 0.4), (1.6, 0.4)):
        fr.box(4.2 + dx, 4.2 + dx + 0.4, 2.2 + dd, 2.2 + dd + 0.4, zf + 0.04, zf + 0.46, S["madeira_escura"])
    # sleeping corner: bed, nightstand, wardrobe, rug
    fr.box(7.6, 11.0, 4.6, 7.7, zf + 0.04, zf + 0.06, S["tecido"])
    fr.box(8.3, 10.1, 5.5, 7.7, zf + 0.06, zf + 0.42, S["madeira_escura"])
    fr.box(8.35, 10.05, 5.55, 7.65, zf + 0.42, zf + 0.62, S["tecido"])
    fr.box(8.3, 10.1, 7.55, 7.7, zf + 0.06, zf + 1.3, S["teca"])
    for k in range(2):
        fr.box(8.45 + k * 0.8, 9.1 + k * 0.8, 6.9, 7.4, zf + 0.62, zf + 0.78, S["tecido"])
    fr.box(7.7, 8.2, 7.1, 7.6, zf + 0.06, zf + 0.5, S["madeira_escura"])
    fr.box(10.2, 10.7, 7.1, 7.6, zf + 0.06, zf + 0.5, S["madeira_escura"])
    fr.box(10.4, 11.8, 4.4, 5.2, zf + 0.06, zf + 2.2, S["madeira_escura"])                   # wardrobe
    fr.cyl(7.9, 7.35, zf + 0.5, 0.05, 0.4, 8, S["latao"])
    fr.cyl(7.9, 7.35, zf + 0.9, 0.18, 0.25, 12, S["luz"])


def hotel_block(fr, z, L=60.0, floors=5, seed=0):
    """Stage 4: the first real hotel: a loggia-and-balcony wing plus a small gabled lobby, set around a pool court."""
    R.wing(fr, L, 16, z, floors, seed=seed, pitched=False)
    R.lobby(fr.shift(L / 2 - 14, -12), 28, 9, z, H=5.5)


# ------------------------------------------------------------------------------------------------ Grande Hotel Palmeiras

def grand_lobby(fr, u0, u1, D, zb, H=4.6):
    """Interior of the restored Grande Hotel: polished marble floor, two rows of columns, a double imperial staircase to the mezzanine,
    a reception desk, a coffered ceiling and a great brass chandelier. Faces the arcade/portico (d < 0 side is open)."""
    W = u1 - u0
    fr.box(u0, u1, 0.0, D, zb, zb + 0.06, S["marmore"])                                     # floor
    fr.box(u0 + W * 0.3, u0 + W * 0.7, 2.0, D - 6.0, zb + 0.06, zb + 0.08, S["terracota"])  # carpet runner
    fr.box(u0, u0 + 0.3, 0, D, zb, zb + H, S["travertino"], front=False)                     # side walls
    fr.box(u1 - 0.3, u1, 0, D, zb, zb + H, S["travertino"], front=False)
    fr.box(u0, u1, D - 0.3, D, zb, zb + H, S["travertino"], front=False)                      # back wall
    fr.box(u0 + 3, u1 - 3, D - 0.32, D - 0.28, zb + 1.0, zb + 3.4, S["vidro"], top=False, bottom=False)   # great mirror
    fr.box(u0, u1, 0.0, D, zb + H - 0.35, zb + H, S["teca"], top=False)                       # ceiling
    for k in range(5):
        fr.box(u0, u1, k * D / 4.0 - 0.15, k * D / 4.0 + 0.15, zb + H - 0.55, zb + H - 0.35, S["madeira_escura"])
    for row in (4.0, 12.0):                                                                    # two rows of columns
        for k in range(4):
            u = u0 + 4.0 + k * (W - 8.0) / 3.0
            fr.cyl(u, row, zb + 0.06, 0.4, H - 0.4, 16, S["marmore"])
            fr.box(u - 0.55, u + 0.55, row - 0.55, row + 0.55, zb + H - 0.4, zb + H - 0.35, S["latao"])
    # double imperial staircase: a central flight up to a landing, then two lateral flights to the mezzanine
    fr.box(u0 + W * 0.4, u0 + W * 0.6, D - 9.0, D - 6.0, zb, zb + 1.1, S["marmore"])         # landing block
    nsteps = 7
    for k in range(nsteps):
        fr.box(u0 + W * 0.38, u0 + W * 0.62, D - 12.5 + k * 0.5, D - 9.0, zb, zb + (k + 1) * 0.157, S["marmore"])
    for side, ua, ub in ((-1, u0 + W * 0.15, u0 + W * 0.38), (1, u0 + W * 0.62, u0 + W * 0.85)):
        for k in range(nsteps):
            fr.box(ua, ub, D - 9.0 + k * 0.42, D - 6.0 + 0.0, zb + 1.1, zb + 1.1 + (k + 1) * 0.157, S["marmore"])
    fr.box(u0 + 1.0, u1 - 1.0, D - 3.0, D - 0.3, zb + 2.2, zb + 2.5, S["marmore"])           # mezzanine gallery
    for k in range(int((W - 2.0) / 0.5)):
        fr.box(u0 + 1.0 + k * 0.5, u0 + 1.15 + k * 0.5, D - 3.1, D - 3.0, zb + 2.5, zb + 3.3, S["latao"], top=False)
    fr.box(u0 + 1.0, u1 - 1.0, D - 3.15, D - 2.95, zb + 3.3, zb + 3.38, S["latao"])
    fr.box(u0 + 2.0, u0 + 8.0, 3.0, 5.0, zb + 0.06, zb + 1.15, S["madeira_escura"])           # reception desk
    fr.box(u0 + 1.9, u0 + 8.1, 2.9, 5.1, zb + 1.15, zb + 1.22, S["marmore"])
    for k in range(3):                                                                        # chandelier
        fr.cyl((u0 + u1) / 2, D * 0.5, zb + H - 1.1 - k * 0.5, 2.2 - k * 0.6, 0.1, 24, S["latao"])
    fr.cyl((u0 + u1) / 2, D * 0.5, zb + H - 3.3, 0.45, 2.6, 14, S["luz"])
    for sx in (u0 + 6, u1 - 6):                                                               # sofas and palms in pots
        fr.box(sx - 1.2, sx + 1.2, 6.0, 7.2, zb + 0.06, zb + 0.5, S["tecido"])
        fr.cyl(sx, 9.5, zb + 0.06, 0.5, 0.9, 12, S["basalto"])

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
    if ruin:
        fr.box(0, L, 0, D, zb, zb + 4.6, S["estuque"], front=False, top=False)
    else:
        # restored hotel: solid ends, an open Grand Lobby in the central bays (visible through the arches and the portico doors)
        fr.box(0, 30, 0, D, zb, zb + 4.6, S["estuque"], front=False, top=False)
        fr.box(60, L, 0, D, zb, zb + 4.6, S["estuque"], front=False, top=False)
        grand_lobby(fr, 30.0, 60.0, D, zb)
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
