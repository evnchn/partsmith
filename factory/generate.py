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


@dataclass
class RepairGenerator:
    """Deterministic repair operator: read the FAILING assertions and nudge the responsible
    parameter toward passing.

    This is the legible, reliable form of the loop's central idea — a failing test *names* what's
    wrong, so the fix is directed, not a random walk. It's a runnable stand-in for the agentic
    repair path (AgentGenerator, where a Claude Code agent reads the same failing rows and rewrites
    the CAD). Accumulates repairs across rounds via its own `base`.
    """

    base: dict

    # assertion name -> (param, how to nudge it toward passing)
    def propose(self, feedback: list | None = None) -> dict:
        p = dict(self.base)
        for row in feedback or []:
            name = row[0]
            if name == "shelf_clearance_mm":
                p["slot_w"] = p["slot_w"] + 0.5          # widen the slot so the shelf fits
            elif name == "cable_clearance_mm":
                p["bore_r"] = p["bore_r"] + 0.1          # widen the bore so the cable fits
            elif name == "bbox_x":
                p["L"] = min(p["L"], 60.0) * 0.98        # shrink to the build volume
            elif name == "bbox_y":
                p["W"] = min(p["W"], 60.0) * 0.98
            elif name == "bbox_z":
                p["H"] = min(p["H"], 60.0) * 0.98
            elif name == "min_wall_mm":
                p["bore_x"] = p["bore_x"] - 0.5          # pull the bore inward, grow the outer wall
            elif name == "max_overhang_deg":
                p["H"] = p["H"] + 0.5                    # (topology here is vertical; nudge anyway)
            elif name == "retention_N":
                p["wall"] = p["wall"] + 0.3              # thicker flexing wall grips harder
        self.base = p
        return p
