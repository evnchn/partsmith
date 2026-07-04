"""Reference parametric part: a shelf-lip cable clip.

Print orientation is Z-up and the design is **support-free by construction**: the body is a
rectangular prism and *every* removed feature is a vertical through-hole (constant cross-section
along Z). No feature ever presents a downward-facing overhang, so `max_overhang_deg` is ~0.

Two mating features, both vertical through-slots:
  * a rectangular **shelf slot** — grips a ~22 mm shelf lip. The gripping clearance is in X
    (slot is 22.4 mm wide for a 22 mm shelf → 0.2 mm/side). The shelf slides in from the top.
  * a circular **cable bore** — a ~6 mm cable drops through (radius 3.25 for a 3.0 mm-radius cable
    → 0.25 mm radial clearance), offset in +X so a real wall remains on both sides.

`make(params)` returns a `build123d.Part`. `make_shelf_probe` / `make_cable_probe` return the
mating solids at the *same* locations the features were cut, so the attester measures the real gap.
"""
from __future__ import annotations

from build123d import BuildPart, Box, Cylinder, Locations, Mode, Part

# ---------------------------------------------------------------------------
# Default parameters (the hand-seeded first candidate). All dimensions in mm.
# ---------------------------------------------------------------------------
DEFAULT: dict = {
    # body
    "L": 40.0,     # X
    "W": 18.0,     # Y
    "H": 26.0,     # Z
    "wall": 2.0,   # printable wall floor we design against

    # shelf slot (vertical rectangular through-hole in Z)
    "slot_w": 22.4,      # X: 22 mm shelf + 0.4 mm total gripping clearance (0.2/side)
    "slot_len": 12.0,    # Y: nominal depth of the shelf tongue the probe represents
    "slot_y_clear": 0.3, # Y clearance/side so the shelf slides (cut is slot_len + 2*this)
    "slot_x": -3.0,      # X of slot centre (shifted -X to leave room for the bore in +X)

    # cable bore (vertical circular through-hole in Z)
    "bore_r": 3.25,      # 6 mm cable → radius 3.0 + 0.25 mm radial clearance
    "bore_x": 14.0,      # X of bore centre (offset +X, away from the slot)

    # retention proxy tuning (see atoms.measure.retention_N — engineering estimate)
    "pinch_mm": 0.15,    # assumed elastic pinch/interference the flexing wall sees
    "mu": 0.4,           # PLA-on-cable friction coefficient
}


def _slot_cut_y(params: dict) -> float:
    """Y-dimension of the *cut* slot = tongue length + clearance on both Y faces.

    Kept strictly larger than the shelf probe's Y so the governing (smallest) clearance is the
    tight X grip, not a coincident Y face."""
    return params["slot_len"] + 2.0 * params["slot_y_clear"]


def make(params: dict | None = None) -> Part:
    p = {**DEFAULT, **(params or {})}
    L, W, H = p["L"], p["W"], p["H"]
    with BuildPart() as bp:
        Box(L, W, H)
        # shelf slot — vertical rectangular through-hole (H+2 => fully through in Z)
        with Locations((p["slot_x"], 0, 0)):
            Box(p["slot_w"], _slot_cut_y(p), H + 2, mode=Mode.SUBTRACT)
        # cable bore — vertical cylinder through-hole
        with Locations((p["bore_x"], 0, 0)):
            Cylinder(p["bore_r"], H + 2, mode=Mode.SUBTRACT)
    return bp.part


def make_shelf_probe(params: dict | None = None, shelf_nominal_mm: float = 22.0) -> Part:
    """The REAL shelf tongue as a solid, at the slot location.

    Size is the spec's *nominal* shelf thickness (a fixed real-world 22 mm), NOT derived from the
    part's `slot_w` — so the measured clearance is the genuine gap the real shelf would see. A
    too-tight slot (slot_w < nominal) interferes -> clearance 0 -> the assertion fails, as it must.
    Placement (slot_x) legitimately comes from where the part put its slot.
    """
    p = {**DEFAULT, **(params or {})}
    with BuildPart() as bp:
        with Locations((p["slot_x"], 0, 0)):
            Box(shelf_nominal_mm, p["slot_len"], p["H"])
    return bp.part


def make_cable_probe(params: dict | None = None, cable_nominal_mm: float = 6.0) -> Part:
    """The REAL cable as a solid, at the bore location.

    Radius is the spec's nominal cable radius (fixed real-world 6 mm dia), NOT derived from
    `bore_r`. A bore that's too small interferes -> clearance 0 -> fails. Honest by construction.
    """
    p = {**DEFAULT, **(params or {})}
    with BuildPart() as bp:
        with Locations((p["bore_x"], 0, 0)):
            Cylinder(cable_nominal_mm / 2.0, p["H"])
    return bp.part
