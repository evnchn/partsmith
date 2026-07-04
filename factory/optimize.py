"""The factory loop — search build123d programs against the pytest objective.

This is the "engineering" in the pitch: generation isn't done when a mesh exists, it's done
when the part PASSES. The attester's `score` is the loss; generators are search operators;
this is the optimizer that closes the loop (race candidates, keep the best passing one, feed
failing assertions back for repair).
"""
from __future__ import annotations

from dataclasses import dataclass

from caliper.attest import run_suite
from parts import cable_clip


@dataclass
class Candidate:
    params: dict
    result: object  # caliper.attest.AttestResult

    @property
    def score(self) -> float:
        return self.result.score

    @property
    def passed(self) -> bool:
        return self.result.passed


def evaluate(params: dict, spec, part_module=cable_clip) -> Candidate | None:
    """Build + attest one candidate. Infeasible geometry -> None (dropped from the race).

    `part_module` is any module exposing make/DEFAULT/probes — the optimizer is part-agnostic.
    """
    try:
        part = part_module.make(params)
        probes = part_module.probes(params, spec)
        res = run_suite(part, spec, params, probes)
        return Candidate(params, res)
    except Exception:
        return None


def optimize(spec, generator, *, rounds: int = 6, per_round: int = 6,
             seed_params: dict | None = None, part_module=cable_clip):
    """Race `per_round` candidates for `rounds`; return (best, history).

    Best = lowest-score PASSING candidate; if none pass yet, the closest (lowest score) is kept
    and its failing rows become the feedback the generator repairs against next round.
    """
    history: list[Candidate] = []
    best: Candidate | None = None

    if seed_params is not None:
        best = evaluate(seed_params, spec, part_module)
        if best is not None:
            history.append(best)

    for _ in range(rounds):
        feedback = None if best is None else [r for r in best.result.rows if not r[1]]
        pool: list[Candidate] = [best] if best is not None else []
        for _ in range(per_round):
            c = evaluate(generator.propose(feedback=feedback), spec, part_module)
            if c is not None:
                pool.append(c)
        if not pool:
            continue
        passing = [c for c in pool if c.passed]
        best = min(passing or pool, key=lambda c: c.score)
        history.append(best)

    return best, history
