"""The attester: run the printability suite as data and score the result.

`run_suite(part, spec, params, probes)` measures the real geometry, evaluates every spec-derived
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


def run_suite(part, spec, params: dict, probes: dict) -> AttestResult:
    """Attest a part against its spec. `probes` maps each `spec.interface` name to the
    real-world mating solid (from `part_module.probes(params, spec)`) — this is what keeps the
    attester PART-AGNOSTIC: it never imports a specific part, it just measures the gap to the
    probe the part module handed it."""
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

    # --- interface clearances (part-agnostic: one row per spec interface) ---
    for iface in spec.interfaces:
        sc = measure.clearance_mm(part, probes[iface.name])
        lo, hi = iface.min_clearance_mm, iface.max_clearance_mm
        ok = sc >= lo and (hi is None or sc <= hi)
        target = f">= {lo}" if hi is None else f"[{lo}, {hi}]"
        rows.append((f"{iface.name}_clearance_mm", ok, sc, target))

    # --- retention ---
    if spec.min_retention_N is not None:
        rn = measure.retention_N(part, spec, params)
        rows.append(("retention_N", rn >= spec.min_retention_N, rn,
                     f">= {spec.min_retention_N}"))

    passed = all(ok for _, ok, _, _ in rows)
    n_fail = sum(1 for _, ok, _, _ in rows if not ok)
    score = n_fail * FAIL_PENALTY + measure.material_mm3(part) + measure.print_time_s(part)
    return AttestResult(passed=passed, rows=rows, score=float(score))
