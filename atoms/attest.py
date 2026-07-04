"""The attester: run the printability suite as data and score the result.

`run_suite(part, spec, params)` measures the real geometry, evaluates every spec-derived
assertion, and returns an `AttestResult`. This is the same objective the pytest suite checks — one
callable for the optimizer loop, one parametrized suite for humans/CI. `score` is designed so
lower is better: a big penalty per failing assertion plus the sum of the minimize targets, so a
passing part always scores below any failing part, and among passing parts the leanest wins.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import measure

FAIL_PENALTY = 1e6  # per failing assertion — dominates any material/time term


@dataclass
class AttestResult:
    passed: bool
    rows: list[tuple[str, bool, float, str]]  # (assert_name, ok, measured_value, target_str)
    score: float


def run_suite(part, spec, params: dict) -> AttestResult:
    from parts import cable_clip

    rows: list[tuple[str, bool, float, str]] = []

    # --- bounding box fits ---
    dx, dy, dz = measure.bbox_mm(part)
    if spec.max_bbox_mm is not None:
        mx, my, mz = spec.max_bbox_mm
        rows.append(("bbox_x", dx <= mx, dx, f"<= {mx}"))
        rows.append(("bbox_y", dy <= my, dy, f"<= {my}"))
        rows.append(("bbox_z", dz <= mz, dz, f"<= {mz}"))

    # --- support-free: worst downward overhang ---
    from .spec import OVERHANG_LIMIT_DEG
    oh = measure.max_overhang_deg(part)
    rows.append(("max_overhang_deg", oh <= OVERHANG_LIMIT_DEG, oh, f"<= {OVERHANG_LIMIT_DEG}"))

    # --- printable walls ---
    mw = measure.min_wall_mm(part)
    rows.append(("min_wall_mm", mw >= spec.min_wall_mm, mw, f">= {spec.min_wall_mm}"))

    # --- shelf clearance (bounded) ---
    shelf = spec.interface("shelf")
    shelf_probe = cable_clip.make_shelf_probe(params, shelf.nominal_mm)
    sc = measure.clearance_mm(part, shelf_probe)
    lo, hi = shelf.min_clearance_mm, shelf.max_clearance_mm
    ok_shelf = sc >= lo and (hi is None or sc <= hi)
    rows.append(("shelf_clearance_mm", ok_shelf, sc, f"[{lo}, {hi}]"))

    # --- cable clearance (floor) ---
    cable = spec.interface("cable")
    cable_probe = cable_clip.make_cable_probe(params, cable.nominal_mm)
    cc = measure.clearance_mm(part, cable_probe)
    rows.append(("cable_clearance_mm", cc >= cable.min_clearance_mm, cc,
                 f">= {cable.min_clearance_mm}"))

    # --- retention ---
    if spec.min_retention_N is not None:
        rn = measure.retention_N(part, spec, params)
        rows.append(("retention_N", rn >= spec.min_retention_N, rn,
                     f">= {spec.min_retention_N}"))

    passed = all(ok for _, ok, _, _ in rows)
    n_fail = sum(1 for _, ok, _, _ in rows if not ok)
    score = n_fail * FAIL_PENALTY + measure.material_mm3(part) + measure.print_time_s(part)
    return AttestResult(passed=passed, rows=rows, score=float(score))
