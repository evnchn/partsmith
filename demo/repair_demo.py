"""Red -> green: start from a genuinely broken design and repair it to passing.

The money shot. A failing assertion NAMES the defect (shelf won't fit, cable won't fit, part
too big for the plate); the repair operator fixes exactly that and re-attests, until the whole
suite is green. Run from the repo root:  `python -m demo.repair_demo`
"""
from __future__ import annotations

from caliper.attest import run_suite
from caliper.spec import CABLE_CLIP
from factory.generate import RepairGenerator
from parts import cable_clip

# A deliberately broken clip: slot too tight (shelf jams), bore too small (cable jams),
# and the body overruns the build plate in X.
BROKEN = {**cable_clip.DEFAULT, "slot_w": 22.05, "bore_r": 3.05, "L": 66.0}


def attest(params: dict):
    part = cable_clip.make(params)
    probes = cable_clip.probes(params, CABLE_CLIP)
    return run_suite(part, CABLE_CLIP, params, probes)


def show(tag: str, res) -> None:
    verdict = "✅ PASS" if res.passed else "❌ FAIL"
    print(f"\n{tag}: {verdict}   score={res.score:,.1f}")
    for name, ok, val, target in res.rows:
        if not ok:  # show only what's still broken (green rows are the absence of red)
            print(f"    ❌ {name:20} = {val:8.3f}   needs {target}")


def main() -> None:
    params = dict(BROKEN)
    res = attest(params)
    show("BROKEN start", res)

    gen = RepairGenerator(base=params)
    for i in range(1, 9):
        if res.passed:
            break
        failing = [r for r in res.rows if not r[1]]
        params = gen.propose(feedback=failing)
        res = attest(params)
        show(f"repair round {i}", res)

    print(f"\n{'='*48}")
    print(f"REPAIRED: passed={res.passed}   final score={res.score:,.1f}")
    print("all assertions:")
    for name, ok, val, target in res.rows:
        print(f"    {'✅' if ok else '❌'} {name:20} = {val:8.3f}   ({target})")


if __name__ == "__main__":
    main()
