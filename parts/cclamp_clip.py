"""C-clamp / edge-grip cable clip — a DISTINCT design from the enclosed-slot reference.

Instead of a fully-enclosed vertical slot the shelf drops into, this is an open **"["-bracket
(C-clamp)**: a back *spine* with a *top arm* and a *bottom arm* that pinch the shelf lip from one
EDGE. The shelf slides in **laterally** (along +X) into the mouth of the C. A vertical **cable
bore** lives in a small cylindrical *boss* fused to the back of the spine.

Print orientation is Z-up and the design is **support-free by construction** exactly like the
reference, but for a different reason: the whole outer body is one **constant cross-section extruded
along Z** (spine + two arms + round boss), and the only subtraction is a vertical through-bore. No
face ever points downward, so `max_overhang_deg` is ~0 — the C-mouth opens *sideways* (+X), never
up, so there is no flat ceiling to bridge.

Contract (mirrors `cable_clip`):
  * `make(params) -> Part`
  * `DEFAULT: dict`
  * `probes(params, spec) -> {"shelf": <22 mm probe>, "cable": <6 mm probe>}` placed at THIS
    design's feature locations (the channel mouth / the bore).
"""
from __future__ import annotations

from build123d import BuildPart, Box, Cylinder, Locations, Mode, Part

# ---------------------------------------------------------------------------
# Default parameters. All dimensions in mm.  Coordinate convention:
#   +X  = the direction the shelf slides IN from (the C mouth opens toward +X)
#   +Y  = shelf-thickness axis (the 22 mm gap is measured in Y, between the two arms)
#   +Z  = print/up axis; the whole body is extruded along Z -> support-free
# The body is centred on Z=0 (z in [-H/2, H/2]) like the reference part.
# ---------------------------------------------------------------------------
DEFAULT: dict = {
    "H": 4.0,          # Z: clip height (extrusion length). Smaller = less material.

    # C-channel that grips the shelf lip (22 mm nominal, gap measured in Y)
    "gap_clear": 0.30, # per-side Y clearance -> channel gap = 22 + 2*gap_clear
    "arm_t": 1.1,      # Y thickness of each arm (wall)
    "arm_len": 5.0,    # X length the arms reach out over the shelf (the grip overlap)
    "spine_t": 1.0,    # X thickness of the back spine (wall)

    # cable bore: a vertical through-hole in a round boss fused to the spine's back (-X)
    "bore_r": 3.25,    # 6 mm cable -> radius 3.0 + 0.25 mm radial clearance
    "boss_r": 4.15,    # boss outer radius -> ~0.9 mm wall around the bore
    "boss_x": -3.3,    # X centre of boss/bore (in -X, behind the spine)

    # where the shelf probe sits in the mouth (X span of the represented lip)
    "shelf_x0": 3.0,   # probe near (back) face X — kept off the spine so the Y grip governs
    "shelf_x1": 20.0,  # probe far face X (sticks out of the mouth)
}


def _half_gap(p: dict) -> float:
    """Half the Y channel gap: 11 mm (half a 22 mm shelf) + the per-side clearance."""
    return 22.0 / 2.0 + p["gap_clear"]


def make(params: dict | None = None) -> Part:
    p = {**DEFAULT, **(params or {})}
    H = p["H"]
    hg = _half_gap(p)                 # inner Y face of each arm
    arm_t = p["arm_t"]
    y_out = hg + arm_t               # outer Y face of each arm
    y_total = 2.0 * y_out            # full Y extent of the spine
    ts = p["spine_t"]
    La = p["arm_len"]
    arm_cx = ts + La / 2.0           # X centre of an arm (spine sits x in [0, ts])
    arm_cy = (hg + y_out) / 2.0      # Y centre of the top arm

    with BuildPart() as bp:
        # back spine (x in [0, ts], full Y, full Z)
        with Locations((ts / 2.0, 0, 0)):
            Box(ts, y_total, H)
        # top + bottom grip arms (reach out over +X)
        with Locations((arm_cx, arm_cy, 0), (arm_cx, -arm_cy, 0)):
            Box(La, arm_t, H)
        # round boss on the back of the spine to house the cable bore
        with Locations((p["boss_x"], 0, 0)):
            Cylinder(p["boss_r"], H)
        # cable bore — vertical through-hole (constant cross-section => no overhang)
        with Locations((p["boss_x"], 0, 0)):
            Cylinder(p["bore_r"], H + 2, mode=Mode.SUBTRACT)
    return bp.part


def make_shelf_probe(params: dict | None = None, shelf_nominal_mm: float = 22.0) -> Part:
    """The REAL shelf lip as a solid, sitting in the C mouth at this design's grip location.

    The gripped dimension is the shelf THICKNESS = `shelf_nominal_mm` (fixed real-world 22 mm),
    oriented along Y (the axis the two arms pinch). Placement in X comes from where this design's
    mouth is. A channel gap that's too tight interferes -> clearance 0 -> the assertion fails, as it
    must. Honest by construction: the probe size is the spec nominal, not the part's own gap.
    """
    p = {**DEFAULT, **(params or {})}
    x0, x1 = p["shelf_x0"], p["shelf_x1"]
    length_x = x1 - x0
    with BuildPart() as bp:
        with Locations(((x0 + x1) / 2.0, 0, 0)):
            Box(length_x, shelf_nominal_mm, p["H"])
    return bp.part


def make_cable_probe(params: dict | None = None, cable_nominal_mm: float = 6.0) -> Part:
    """The REAL cable as a solid, at the bore location.

    Radius is the spec nominal (fixed 6 mm dia), NOT derived from `bore_r`; a bore that's too small
    interferes -> clearance 0 -> fails.
    """
    p = {**DEFAULT, **(params or {})}
    with BuildPart() as bp:
        with Locations((p["boss_x"], 0, 0)):
            Cylinder(cable_nominal_mm / 2.0, p["H"])
    return bp.part


def probes(params: dict, spec) -> dict:
    """Part-agnostic contract: map each spec interface name -> its real-world probe solid, sized
    from the interface nominal and placed at THIS design's actual feature location."""
    return {
        "shelf": make_shelf_probe(params, spec.interface("shelf").nominal_mm),
        "cable": make_cable_probe(params, spec.interface("cable").nominal_mm),
    }
