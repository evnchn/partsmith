"""Manufacturing passport — the artifact the factory ships beside the part.

Not a render: a measured, test-backed report. Every claim is a number the attester computed,
so a human or a judge can trust the part before any printer runs.
"""
from __future__ import annotations

import os

from caliper import measure


def write_passport(part, spec, result, outdir: str = "artifacts", name: str | None = None) -> str:
    os.makedirs(outdir, exist_ok=True)
    name = name or spec.name
    stl = os.path.join(outdir, f"{name}.stl")
    try:
        from build123d import export_stl

        export_stl(part, stl)
    except Exception as e:  # noqa: BLE001 - report, don't crash the demo
        stl = f"(STL export failed: {e})"

    dx, dy, dz = measure.bbox_mm(part)
    verdict = "PASSES" if result.passed else "FAILS"
    rows = "\n".join(
        f"| {n} | {'✅' if ok else '❌'} | {val:.3f} | {target} |"
        for (n, ok, val, target) in result.rows
    )
    md = f"""# Manufacturing Passport — {name}

> {spec.prompt}

**Attestation: {'✅ ' if result.passed else '❌ '}{verdict}**  ·  score `{result.score:.2f}`  ·  \
material `{measure.material_mm3(part):.0f} mm³`

| Assertion | OK | Measured | Target |
|---|:--:|---|---|
{rows}

Bounding box: {dx:.1f} × {dy:.1f} × {dz:.1f} mm  ·  STL: `{stl}`
"""
    path = os.path.join(outdir, f"{name}_passport.md")
    with open(path, "w") as f:
        f.write(md)
    return path
