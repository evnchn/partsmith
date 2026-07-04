"""End-to-end factory demo: NL spec -> optimized, attested part -> passport + STL.

The filmed path. Prints the round-by-round best score so the optimization-against-the-tests is
visible on camera. Run from the repo root:  `python -m demo.run_demo`
"""
from __future__ import annotations

from atoms.spec import CABLE_CLIP
from factory.generate import ParametricGenerator
from factory.optimize import optimize
from factory.passport import write_passport
from parts import cable_clip


def main() -> None:
    spec = CABLE_CLIP
    print(f"SPEC: {spec.prompt}\n")

    base = getattr(cable_clip, "DEFAULT", None)
    if base is None:
        raise SystemExit("parts.cable_clip.DEFAULT is missing — cannot seed the optimizer.")

    gen = ParametricGenerator(base=base, scale=0.10)
    best, history = optimize(spec, gen, rounds=6, per_round=8, seed_params=base)

    print("round-by-round best (score = attester loss; lower is better):")
    for i, c in enumerate(history):
        print(f"  {i:>2}  score={c.score:8.2f}  passed={c.passed}")

    part = cable_clip.make(best.params)
    path = write_passport(part, spec, best.result)
    print(f"\nBEST: passed={best.passed}  score={best.result.score:.2f}")
    print(f"passport -> {path}")


if __name__ == "__main__":
    main()
