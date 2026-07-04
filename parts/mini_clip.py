"""Minimal-material shelf-lip cable clip — the LEANEST viable design.

Strategy: strip everything non-structural. Instead of a solid block, the part is built from a
handful of thin (>= min-wall) vertical extrusions:

  * two **thin twin walls** whose inner faces straddle the 22 mm shelf lip in X, forming an
    open-top slot the shelf slides down into (grip clearance is the X gap);
  * a **thin bottom rail** behind the shelf that ties the two walls into one solid — kept at bed
    level so its down-face is the excluded first layer (no overhang), and kept clear of the shelf
    probe in Y so it never governs the shelf clearance;
  * a **thin closed collar** on the outboard side that guides the 6 mm cable — a vertical tube
    rising from the bed, tied to the right wall by a short strut, hollowed to a 0.25 mm slip fit.

Everything is a constant-Z cross-section (walls, rail, collar) so `max_overhang_deg` is ~0 by
construction — support-free. Every wall is `wt` (>= 0.8 mm) so `min_wall_mm` clears the floor.
There is no solid body anywhere: material is pushed as low as the clearances/wall/overhang
assertions allow.

Contract (mirrors `parts.cable_clip`): `make(params) -> Part`, `DEFAULT`, `probes(params, spec)`.
The probes are the *real* mating solids (22 mm shelf tongue, 6 mm cable) placed at THIS design's
own feature locations, so the attester measures the genuine gap.
"""
from __future__ import annotations

from build123d import BuildPart, Box, Cylinder, Locations, Mode, Part

# ---------------------------------------------------------------------------
# Default parameters (mm). Tuned for minimum material while every assertion holds.
# ---------------------------------------------------------------------------
DEFAULT: dict = {
    # nominal mating dimensions (fixed real-world sizes, from the spec)
    "shelf_nom": 22.0,   # shelf lip thickness (X)
    "cable_nom": 6.0,    # cable diameter

    # clearances (targets: shelf in [0.15, 0.6] per side, cable >= 0.2 radial)
    "clr_shelf": 0.25,   # X gap per side between wall and shelf
    "clr_cable": 0.25,   # radial gap between collar bore and cable

    # thin-wall floor we design against (spec min_wall_mm = 0.8)
    "wt": 0.9,           # thickness of every structural wall

    # overall envelope — pushed low; every feature still overlaps its probe / stays >= min wall
    "H": 5.0,            # height of the twin walls (Z)
    "grip_depth": 4.0,   # Y depth over which the walls embrace the shelf (probe depth)
    "bridge_clear": 0.3, # Y gap between shelf-probe back face and the tie rail
    "rail_h": 0.9,       # Z height of the bottom tie rail (sits on the bed)

    # cable collar (thin closed ring)
    "ring_h": 3.0,       # collar height (rises from the bed)
    "ring_wt": 0.9,      # collar wall thickness
    "strut_len": 1.0,    # clear gap between right wall and collar, bridged by the strut
    "strut_embed": 0.4,  # how far the strut sinks into the wall and collar (clean fusion)

    "slot_x": 0.0,       # X centre of the shelf slot
}


# ---------------------------------------------------------------------------
# Derived geometry helpers
# ---------------------------------------------------------------------------

def _geom(p: dict) -> dict:
    shelf_half = p["shelf_nom"] / 2.0
    inner_x = shelf_half + p["clr_shelf"]          # inner face of each wall
    wall_cx = inner_x + p["wt"] / 2.0              # wall centre X
    wall_outer = inner_x + p["wt"]                 # outer face of each wall

    grip = p["grip_depth"]
    # walls span Y from the shelf front to just past the tie rail behind the shelf
    y_front = -grip / 2.0
    y_back = grip / 2.0 + p["bridge_clear"] + p["wt"]
    wall_ly = y_back - y_front
    wall_cy = (y_front + y_back) / 2.0

    # tie rail: thin bar spanning the full X, behind the shelf, on the bed
    rail_cy = grip / 2.0 + p["bridge_clear"] + p["wt"] / 2.0
    rail_x = 2.0 * wall_outer                       # wall-outer to wall-outer
    rail_cz = -p["H"] / 2.0 + p["rail_h"] / 2.0

    # cable collar, sitting OUTBOARD of the right wall (no curved overlap into the wall — that
    # tangential graze made a sub-wt fusion sliver). The collar is tied to the wall by a clean
    # rectangular strut instead, so every junction is box-on-box and min_wall is wt-governed.
    r_in = p["cable_nom"] / 2.0 + p["clr_cable"]
    r_out = r_in + p["ring_wt"]
    bx = wall_outer + p["strut_len"] + r_out        # collar centre X (fully outboard)
    ring_cz = -p["H"] / 2.0 + p["ring_h"] / 2.0

    # strut: box from just inside the wall to just inside the collar's inboard face
    embed = p["strut_embed"]
    strut_x0 = wall_outer - embed
    strut_x1 = (bx - r_out) + embed
    strut_lx = strut_x1 - strut_x0
    strut_cx = (strut_x0 + strut_x1) / 2.0

    return dict(
        inner_x=inner_x, wall_cx=wall_cx, wall_outer=wall_outer,
        wall_ly=wall_ly, wall_cy=wall_cy,
        rail_cy=rail_cy, rail_x=rail_x, rail_cz=rail_cz,
        r_in=r_in, r_out=r_out, bx=bx, ring_cz=ring_cz,
        strut_lx=strut_lx, strut_cx=strut_cx,
    )


def make(params: dict | None = None) -> Part:
    p = {**DEFAULT, **(params or {})}
    g = _geom(p)
    H, wt = p["H"], p["wt"]
    sx = p["slot_x"]

    with BuildPart() as bp:
        # --- twin walls straddling the shelf slot (vertical, full height) ---
        with Locations((sx - g["wall_cx"], g["wall_cy"], 0.0),
                       (sx + g["wall_cx"], g["wall_cy"], 0.0)):
            Box(wt, g["wall_ly"], H)

        # --- bottom tie rail behind the shelf (on the bed, no overhang) ---
        with Locations((sx, g["rail_cy"], g["rail_cz"])):
            Box(g["rail_x"], wt, p["rail_h"])

        # --- strut tying the collar to the right wall (clean box-on-box junction) ---
        with Locations((sx + g["strut_cx"], 0.0, g["ring_cz"])):
            Box(g["strut_lx"], wt, p["ring_h"])

        # --- cable collar: a thin closed ring (tube) rising from the bed ---
        # A CLOSED ring is deliberate: an open C, cut on any plane, feathers to zero thickness at
        # the outer corners where the flat end meets the round wall (the sampler reads that as a
        # ~0 wall). The closed ring has no end faces, so every inward ray is the clean radial
        # thickness `ring_wt` -> min_wall is rock-solid. The extra arc costs little at this size.
        with Locations((sx + g["bx"], 0.0, g["ring_cz"])):
            Cylinder(g["r_out"], p["ring_h"])
        with Locations((sx + g["bx"], 0.0, g["ring_cz"])):
            Cylinder(g["r_in"], p["ring_h"] + 2.0, mode=Mode.SUBTRACT)

    return bp.part


# ---------------------------------------------------------------------------
# Probes — the REAL mating solids at THIS design's feature locations
# ---------------------------------------------------------------------------

def make_shelf_probe(params: dict | None = None, shelf_nominal_mm: float = 22.0) -> Part:
    """The real 22 mm shelf tongue as a solid, at the slot location."""
    p = {**DEFAULT, **(params or {})}
    with BuildPart() as bp:
        with Locations((p["slot_x"], 0.0, 0.0)):
            Box(shelf_nominal_mm, p["grip_depth"], p["H"])
    return bp.part


def make_cable_probe(params: dict | None = None, cable_nominal_mm: float = 6.0) -> Part:
    """The real 6 mm cable as a solid, at the collar location."""
    p = {**DEFAULT, **(params or {})}
    g = _geom(p)
    with BuildPart() as bp:
        with Locations((p["slot_x"] + g["bx"], 0.0, 0.0)):
            Cylinder(cable_nominal_mm / 2.0, p["H"])
    return bp.part


def probes(params: dict, spec) -> dict:
    return {
        "shelf": make_shelf_probe(params, spec.interface("shelf").nominal_mm),
        "cable": make_cable_probe(params, spec.interface("cable").nominal_mm),
    }
