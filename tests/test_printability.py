"""The printability suite = the objective, parametrized off the spec.

One `assert` per printability property, each measured from real build123d geometry via atoms.measure.
Every constraint in the spec maps to exactly one assertion here — that is the discipline that keeps
the optimization loop honest (README: "the tests are the loss function").
"""
from atoms import measure
from atoms.spec import OVERHANG_LIMIT_DEG
from parts import cable_clip


def test_bbox_fits(part, spec):
    dx, dy, dz = measure.bbox_mm(part)
    mx, my, mz = spec.max_bbox_mm
    assert dx <= mx, f"bbox X {dx} exceeds {mx}"
    assert dy <= my, f"bbox Y {dy} exceeds {my}"
    assert dz <= mz, f"bbox Z {dz} exceeds {mz}"


def test_support_free(part):
    oh = measure.max_overhang_deg(part)
    assert oh <= OVERHANG_LIMIT_DEG, f"max overhang {oh:.2f} deg > {OVERHANG_LIMIT_DEG} (needs support)"


def test_min_wall(part, spec):
    mw = measure.min_wall_mm(part)
    assert mw >= spec.min_wall_mm, f"min wall {mw:.3f} mm < {spec.min_wall_mm} mm floor"


def test_shelf_clearance(part, spec, params):
    iface = spec.interface("shelf")
    probe = cable_clip.make_shelf_probe(params)
    c = measure.clearance_mm(part, probe)
    assert c >= iface.min_clearance_mm, f"shelf clearance {c:.3f} mm < {iface.min_clearance_mm} mm (too tight)"
    assert iface.max_clearance_mm is None or c <= iface.max_clearance_mm, \
        f"shelf clearance {c:.3f} mm > {iface.max_clearance_mm} mm (too loose to grip)"


def test_cable_clearance(part, spec, params):
    iface = spec.interface("cable")
    probe = cable_clip.make_cable_probe(params)
    c = measure.clearance_mm(part, probe)
    assert c >= iface.min_clearance_mm, f"cable clearance {c:.3f} mm < {iface.min_clearance_mm} mm (won't fit)"


# NOTE: retention (does the cable HOLD?) is deliberately NOT gated here. This reference clip is a
# slip-fit guide, so there is no real retention force to measure — a snap/interference feature would
# be needed. We don't fake the number. See atoms.measure.retention_N (roadmap) and README "Honest
# scope". Knowing the difference between a measurement and an unmodelled force is the whole point.
