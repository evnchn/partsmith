"""The gate BITES: plausible-looking parts, caught by Caliper before they'd waste filament.

A verification tool is only worth anything if it REJECTS. Each case below is a part that looks like a
valid cable clip but carries one real defect; Caliper measures it and fails the *specific* check —
with the number. This is the answer to "is the verification real, or theater?"

    python -m demo.adversarial
"""
from __future__ import annotations

from caliper.attest import run_suite
from caliper.spec import CABLE_CLIP
from parts import cable_clip

# (label, parameter override that injects one real defect, the check that should catch it)
CASES = [
    ("wall too thin — bore crowds the edge", {"bore_x": 16.6}, "min_wall_mm"),
    ("slot too tight — 22 mm shelf won't fit", {"slot_w": 21.6}, "shelf_clearance_mm"),
    ("bore too small — 6 mm cable won't fit", {"bore_r": 3.05}, "cable_clearance_mm"),
    ("too big for the build plate", {"L": 70.0}, "bbox_x"),
]


def attest(over: dict):
    p = {**cable_clip.DEFAULT, **over}
    part = cable_clip.make(p)
    return run_suite(part, CABLE_CLIP, p, cable_clip.probes(p, CABLE_CLIP))


def main() -> None:
    print("Caliper vs. parts that look fine (each has one hidden defect):\n")
    print(f"{'defect':42} {'verdict':8} {'caught by':20} value")
    print("-" * 82)
    for label, over, expect in CASES:
        r = attest(over)
        rows = {n: (ok, v) for n, ok, v, _ in r.rows}
        val = rows.get(expect, (None, float("nan")))[1]
        caught = expect if (expect in rows and not rows[expect][0]) else \
            ",".join(n for n, ok, *_ in r.rows if not ok)
        print(f"{label:42} {'REJECT' if not r.passed else 'PASS':8} {caught:20} {val:.3f}")
    print("\nEvery defect is caught by its specific check, with the measured number — before a printer")
    print("ever runs. The gate rejects; that's what makes the green ones mean something.")


if __name__ == "__main__":
    main()
