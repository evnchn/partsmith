"""Hook-over-lip cable bracket — a DISTINCT design for `atoms.spec.CABLE_CLIP`.

Where the reference `cable_clip` cuts a fully-*enclosed* vertical slot through a solid box, this
part is an **open hook**: an inverted-U / C-clamp that drapes over the edge of the shelf lip and
grips it on three sides (both faces + the top), open on the fourth so it hooks *over* rather than
swallowing the lip. The opposite face of the shared back wall carries a second, smaller C-channel
that cradles the 6 mm cable — the "eyelet hanging below" the hook.

Support-free by construction, the SAME way the reference is: the entire body is a constant
cross-section **extrusion along +Z** (the print direction). Every wall is therefore vertical
(overhang 0 deg), the only up-facing faces point straight up (not overhangs), and the only
down-facing faces rest on the bed (excluded from the overhang check). There is no interior
ceiling to bridge, so `max_overhang_deg` is ~0 without a single support or chamfer.

Orientation: +Z is up / the print & extrusion axis. The clip grips the shelf across **X** (the
22 mm dimension), the C-channels open along **Y**, and both the shelf and the cable run along **Z**
(matching the reference's Z-axis cable bore). `probes()` returns real mating solids placed at these
exact feature locations so the attester measures the genuine gap.
"""
from __future__ import annotations

from build123d import BuildPart, Box, Cylinder, Locations, Part

# ---------------------------------------------------------------------------
# Default parameters (all mm). Tuned to PASS then trimmed for minimal material.
# ---------------------------------------------------------------------------
DEFAULT: dict = {
    "shelf_nom": 22.0,   # real shelf-lip thickness the hook grips (spec nominal, across X)
    "cable_dia": 6.0,    # real cable diameter the channel cradles (spec nominal)

    "wall": 0.9,         # wall thickness — design floor is 0.8; 0.9 keeps ~0.1 mm margin
    "s_clear": 0.30,     # shelf clearance PER SIDE -> total in the [0.15, 0.6] band
    "c_clear": 0.30,     # cable clearance per side -> >= 0.2 slip fit
    "z": 8.0,            # extrusion height (clip width along the shelf edge, the print Z)

    "grip": 4.0,         # how far the side walls reach down the shelf face (Y, from the top wall)
    "mouth": 3.5,        # how far the open mouth extends the other way (Y)
}


def _geom(p: dict) -> dict:
    """Derive every load-bearing coordinate from the params, ONCE, so `make()` and `probes()`
    can never drift apart. Returns a flat dict of the key X/Y edges (Z is always [0, z])."""
    t = p["wall"]
    z = p["z"]
    # --- shelf C-channel (opens toward -Y) ---
    inner_hx = p["shelf_nom"] / 2.0 + p["s_clear"]   # half inner width across X
    outer_hx = inner_hx + t
    top_in = p["grip"]           # inner Y face of the top (back) wall
    top_out = top_in + t         # outer Y face of the top wall
    mouth_y = -p["mouth"]        # open mouth of the C
    # --- cable C-channel (opens toward +Y, shares the same back wall) ---
    c_r = p["cable_dia"] / 2.0
    c_in_hx = c_r + p["c_clear"]         # half inner width across X
    c_out_hx = c_in_hx + t
    cable_cy = top_out + p["c_clear"] + c_r   # cable centre: c_clear gap to the shared wall
    c_wall_top = cable_cy + c_r          # side walls flank the full cable, open beyond
    return dict(
        t=t, z=z,
        inner_hx=inner_hx, outer_hx=outer_hx, top_in=top_in, top_out=top_out, mouth_y=mouth_y,
        c_r=c_r, c_in_hx=c_in_hx, c_out_hx=c_out_hx, cable_cy=cable_cy, c_wall_top=c_wall_top,
    )


def _box(bp, cx, cy, sx, sy, z):
    """Add an axis-aligned box spanning X:[cx-sx/2,cx+sx/2], Y:[cy-sy/2,cy+sy/2], Z:[0,z]."""
    with Locations((cx, cy, z / 2.0)):
        Box(sx, sy, z)


def make(params: dict | None = None) -> Part:
    p = {**DEFAULT, **(params or {})}
    g = _geom(p)
    t, z = g["t"], g["z"]

    with BuildPart() as bp:
        # --- shelf hook: back (top) wall + two side walls forming a C open toward -Y ---
        # top wall spans the full outer width in X, thickness t in Y
        _box(bp, 0.0, (g["top_in"] + g["top_out"]) / 2.0,
             2.0 * g["outer_hx"], t, z)
        # two side walls run down both faces of the lip; overlap the top wall so it's one solid
        side_cy = (g["mouth_y"] + g["top_out"]) / 2.0
        side_sy = g["top_out"] - g["mouth_y"]
        for sx_sign in (-1.0, +1.0):
            _box(bp, sx_sign * (g["inner_hx"] + t / 2.0), side_cy, t, side_sy, z)

        # --- cable cradle: second C open toward +Y, reusing the top wall as its back ---
        c_cy = (g["top_out"] + g["c_wall_top"]) / 2.0
        c_sy = g["c_wall_top"] - g["top_out"]
        for sx_sign in (-1.0, +1.0):
            _box(bp, sx_sign * (g["c_in_hx"] + t / 2.0), c_cy, t, c_sy, z)

    return bp.part


def make_shelf_probe(params: dict | None = None, shelf_nominal_mm: float = 22.0) -> Part:
    """The REAL shelf lip as a solid, seated in the hook at the exact grip location.

    Size is the spec nominal (fixed real-world 22 mm across X), NOT derived from the channel
    width — so a hook cut too tight interferes -> clearance 0 -> the assertion fails honestly.
    The probe protrudes past the open mouth (there is no wall there), so the governing clearance
    is the genuine 3-sided grip, never a coincident face.
    """
    p = {**DEFAULT, **(params or {})}
    g = _geom(p)
    top_face = g["top_in"] - p["s_clear"]     # probe top: s_clear below the inner back wall
    bottom_face = g["mouth_y"] - 2.0          # protrudes 2 mm past the open mouth
    depth = top_face - bottom_face
    cy = (top_face + bottom_face) / 2.0
    with BuildPart() as bp:
        _box(bp, 0.0, cy, shelf_nominal_mm, depth, g["z"])
    return bp.part


def make_cable_probe(params: dict | None = None, cable_nominal_mm: float = 6.0) -> Part:
    """The REAL cable as a Z-axis cylinder, seated in the cradle at the exact channel location.

    Radius is the spec nominal (fixed real-world 6 mm dia), NOT derived from the channel — a
    cradle squeezed too tight interferes -> clearance 0 -> fails. Honest by construction.
    """
    p = {**DEFAULT, **(params or {})}
    g = _geom(p)
    with BuildPart() as bp:
        with Locations((0.0, g["cable_cy"], g["z"] / 2.0)):
            Cylinder(cable_nominal_mm / 2.0, g["z"])
    return bp.part


def probes(params: dict, spec) -> dict:
    """Part-agnostic contract: map each spec interface name -> its real-world probe solid, sized
    from the interface nominal and placed at THIS design's actual feature location."""
    return {
        "shelf": make_shelf_probe(params, spec.interface("shelf").nominal_mm),
        "cable": make_cable_probe(params, spec.interface("cable").nominal_mm),
    }
