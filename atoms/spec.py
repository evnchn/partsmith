"""PartSpec — the parsed requirement AND the objective the factory optimizes toward.

A spec is deliberately *machine-checkable*: every field maps to an assertion the attester can
run against real geometry. Natural language gets parsed into one of these; the pytest suite is
generated from it. This is the "fitness function" the agents search against.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# One place for the printer reality the whole factory reasons about.
NOZZLE_MM = 0.4
LAYER_MM = 0.2
OVERHANG_LIMIT_DEG = 45.0  # FDM: faces steeper than this off-vertical need support


@dataclass
class Interface:
    """A thing the part must fit / hold, expressed as a measurable clearance target."""

    name: str          # e.g. "cable", "shelf"
    nominal_mm: float  # the mating dimension (cable dia, shelf thickness)
    min_clearance_mm: float = 0.4   # slip fit floor
    max_clearance_mm: float | None = None  # None = no upper bound (pure clearance)


@dataclass
class PartSpec:
    """A complete, checkable part requirement.

    Every constraint here becomes one `assert` in the generated suite. If a field can't be
    expressed as a measurement, it doesn't belong in the spec — that's the discipline that keeps
    the loop honest.
    """

    name: str
    prompt: str                                   # the original NL request (provenance)
    interfaces: list[Interface] = field(default_factory=list)
    support_free: bool = True                     # must print with no supports
    min_wall_mm: float = 2 * NOZZLE_MM            # printable wall floor
    max_bbox_mm: tuple[float, float, float] | None = None  # fits the build plate / pocket
    min_retention_N: float | None = None          # snap/grip must hold at least this force

    # Optimization: among parts that PASS, prefer these (lower = better).
    minimize: tuple[str, ...] = ("material_mm3", "print_time_s")

    def interface(self, name: str) -> Interface:
        for it in self.interfaces:
            if it.name == name:
                return it
        raise KeyError(f"no interface named {name!r} in spec {self.name!r}")


# The demo spec: a shelf-lip cable clip. Small, legible, physically obvious.
CABLE_CLIP = PartSpec(
    name="cable_clip",
    prompt="a clip for a 6 mm cable that grips a 22 mm shelf lip, prints support-free",
    interfaces=[
        Interface("shelf", nominal_mm=22.0, min_clearance_mm=0.15, max_clearance_mm=0.6),
        Interface("cable", nominal_mm=6.0, min_clearance_mm=0.2),
    ],
    support_free=True,
    min_wall_mm=0.8,
    max_bbox_mm=(60.0, 60.0, 60.0),
    min_retention_N=8.0,
)
