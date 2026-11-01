from build123d import Box, Cylinder

from caliper import measure


def test_probe_embedded_in_solid_is_interference():
    # No bore at all: the 6 mm cable probe sits inside solid material. Boundary-only distance
    # reads 10 mm of "clearance" here and would pass the fit gate; it must be interference.
    block = Box(30, 30, 30)
    probe = Cylinder(3, 10)
    assert measure.clearance_mm(block, probe) == 0.0


def test_probe_in_real_bore_keeps_its_clearance():
    part = Box(30, 30, 30) - Cylinder(3.5, 40)
    probe = Cylinder(3, 10)
    assert abs(measure.clearance_mm(part, probe) - 0.5) < 1e-6


def test_disjoint_solids_do_not_crash():
    # Solid (not Part) operands: a disjoint boolean returns None, not an empty shape.
    part = (Box(30, 30, 30) - Cylinder(3.5, 40)).solid()
    probe = Cylinder(3, 10).solid()
    assert abs(measure.clearance_mm(part, probe) - 0.5) < 1e-6
