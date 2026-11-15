"""max_overhang_deg must see the worst point of a CURVED face, not just its center."""
from math import radians, tan

from build123d import Cone, Cylinder, Pos, Rot, Sphere

from caliper import measure
from caliper.spec import OVERHANG_LIMIT_DEG


def test_lying_cylinder_needs_support():
    # underside of a horizontal cylinder curls back under itself: a real overhang
    part = Pos(0, 0, 5) * Rot(0, 90, 0) * Cylinder(5, 30)
    assert measure.max_overhang_deg(part) > OVERHANG_LIMIT_DEG


def test_sphere_needs_support():
    assert measure.max_overhang_deg(Pos(0, 0, 10) * Sphere(10)) > OVERHANG_LIMIT_DEG


def test_standing_cylinder_is_support_free():
    # vertical side wall, flat top, flat bottom on the bed: nothing to support
    assert measure.max_overhang_deg(Pos(0, 0, 15) * Cylinder(5, 30)) < 1.0


def test_cone_just_under_limit_passes():
    # exact surface normals: a 44.8 deg flare must not read past 45 from faceting
    part = Cone(5, 5 + 5 * tan(radians(44.8)), 5)
    assert measure.max_overhang_deg(part) <= OVERHANG_LIMIT_DEG
