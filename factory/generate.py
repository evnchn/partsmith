"""Generators — the factory's search operators.

The factory is an OPTIMIZER over build123d programs; a Generator proposes the next candidate.
Two kinds, both honest:

- `ParametricGenerator` — perturbs a part's parameters (hill-climb). No LLM, runs anywhere.
  It makes the thesis literally executable: the pytest suite is the loss function, and this
  searches parameter space to minimize it while staying green.
- `AgentGenerator` — a Claude Code agent writes/patches the build123d code itself, given the
  spec and the failing assertions. The headline agentic path. Compute = Claude Code
  (subagent / terminal window). NEVER `claude -p`.
"""
from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Callable, Protocol


class Generator(Protocol):
    def propose(self, feedback: list | None = None) -> dict:
        """Return a params dict for parts.<part>.make(). `feedback` = failing attest rows."""
        ...


@dataclass
class ParametricGenerator:
    """Hill-climb over numeric params, starting from a known-good base.

    Perturbs every numeric parameter by up to ±`scale`. Infeasible proposals (geometry that
    fails to build) are dropped by the optimizer, so this explores toward lower material while
    the attester keeps it honest.
    """

    base: dict
    scale: float = 0.12
    rng: random.Random = field(default_factory=lambda: random.Random(0))

    def propose(self, feedback: list | None = None) -> dict:
        p = copy.deepcopy(self.base)
        for k, v in p.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            jitter = 1.0 + self.rng.uniform(-self.scale, self.scale)
            p[k] = int(round(v * jitter)) if isinstance(v, int) else v * jitter
        return p


@dataclass
class AgentGenerator:
    """Ask a Claude Code agent to author a build123d candidate from spec + failing assertions.

    This is the headline "agentic" path. Wire `spawn` to your orchestrator's agent-spawn — it
    receives the failing attest rows and must write a candidate part program, returning its
    params. The RAISE demo drives this with Claude Code subagents (compute = Claude Code, never
    `claude -p`). Left as a hook so the repo runs without an LLM in the loop.
    """

    spawn: Callable[[list | None], dict] | None = None

    def propose(self, feedback: list | None = None) -> dict:
        if self.spawn is None:
            raise NotImplementedError(
                "AgentGenerator needs a `spawn` callback. It should ask a Claude Code agent to "
                "write parts/_candidates/cand_N.py from the spec + failing rows and return its "
                "params dict. See ARCHITECTURE.md. Never use `claude -p`."
            )
        return self.spawn(feedback)
