"""The agentic race: attest every candidate part module against ONE spec, rank by score.

Each design in `parts/` (except the reference `cable_clip`) was authored by an independent Claude
Code agent from the same brief; the attester is the impartial judge. Same spec, different
topologies — the leanest part that actually PASSES wins, and anything that can't print gets
rejected. This is the "agentic factory" in one command:  `python -m demo.race`
"""
from __future__ import annotations

from importlib import import_module

from caliper.attest import run_suite
from caliper.measure import material_mm3
from caliper.spec import CABLE_CLIP

# reference block first, then the three agent-authored designs
CANDIDATES = ["cable_clip", "cclamp_clip", "hook_clip", "mini_clip"]


def attest_module(name: str, spec):
    m = import_module(f"parts.{name}")
    p = m.DEFAULT
    part = m.make(p)
    r = run_suite(part, spec, p, m.probes(p, spec))
    return name, r, material_mm3(part)


def main() -> None:
    spec = CABLE_CLIP
    print(f"SPEC: {spec.prompt}\n")

    results = []
    for name in CANDIDATES:
        try:
            results.append(attest_module(name, spec))
        except Exception as e:  # a candidate that won't even build is a (failed) entry, not a crash
            print(f"  ! {name}: could not attest ({e})")

    # passing designs first (leanest score wins), then any failing ones
    results.sort(key=lambda t: (not t[1].passed, t[1].score))

    print(f"{'design':16} {'verdict':7} {'material':>11} {'score':>10}")
    print("-" * 48)
    for name, r, mat in results:
        print(f"{name:16} {'PASS' if r.passed else 'FAIL':7} {mat:8.0f} mm³ {r.score:10.1f}")

    winner = next((t for t in results if t[1].passed), None)
    if winner:
        print(f"\nWINNER: {winner[0]}  —  {winner[2]:.0f} mm³, score {winner[1].score:.1f}")
        ref = next((t for t in results if t[0] == "cable_clip"), None)
        if ref and ref[2] > 0:
            print(f"  {ref[2] / winner[2]:.1f}× less material than the reference block, "
                  f"same 7 assertions green.")


if __name__ == "__main__":
    main()
