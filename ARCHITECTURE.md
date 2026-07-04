# Architecture — build contract (for humans and build-subagents)

Clean-room, built during RAISE 2026. Compute = Claude Code (subagents), **no `claude -p`**.
Star = **Partsmith** (the factory/optimizer). **Caliper** (`caliper/`) = the verification engine,
the **objective** that makes the loop real. (Original build contract; all modules now built.)

## Module map + contracts

```
caliper/   # Partsmith Caliper — the verification engine
  spec.py      [DONE]  PartSpec + Interface + NOZZLE/LAYER/OVERHANG constants. The objective, typed.
  measure.py   [TODO]  Geometry queries over a build123d Part/Solid. THE HARD, DEFENSIBLE CORE.
                       Contract — each returns a real number, no eyeballing:
                         bbox_mm(part) -> (dx,dy,dz)
                         max_overhang_deg(part) -> float   # worst downward face angle off-vertical
                         min_wall_mm(part) -> float        # thinnest wall (trimesh voxel/proximity)
                         clearance_mm(part, probe_solid) -> float  # exact, via OCP BRepExtrema
                         hole_diameters_mm(part) -> list[float]    # cylindrical faces
                         material_mm3(part) -> float ; print_time_s(part) -> float (proxy ok)
                         retention_N(part, spec) -> float  # cantilever-snap physics proxy from geom
  attest.py    [TODO]  run_suite(part, spec) -> AttestResult(passed: bool, rows: [(name,ok,val,target)],
                       score: float). score = big penalty per failing assert + sum(minimize targets).
  tricks.py    [TODO]  Certified design tricks. Each trick = (build123d snippet) + (the assertion it
                       guarantees). Admissible ONLY if its own assertion passes. NOT a store, NOT RAG.

parts/
  cable_clip.py [TODO] Reference parametric part (hand-seeded first candidate so the pipeline runs
                       deterministically before agents enter). make(params) -> build123d Part.

tests/
  conftest.py        [TODO] fixtures: `spec`, `part` (imports a candidate program -> Part).
  test_printability.py [TODO] the suite = the objective, parametrized by spec. One assert per line.

factory/
  generate.py  [TODO]  generate(spec, feedback) -> writes parts/_candidates/cand_N.py by invoking a
                       Claude Code agent (subagent). The "agentic" step. Feedback = failing rows.
  optimize.py  [TODO]  the loop: race M candidates -> attest each -> pick best passing by score;
                       if none pass, take closest + feed failing asserts back -> repair -> repeat.
  passport.py  [TODO]  emit manufacturing passport (measured report + green suite + STL/3MF + stats).

demo/
  run_demo.py  [TODO]  spec string -> optimized part -> passport -> STL + render. The filmed path.
```

## Build order (vertical slice FIRST)
1. `measure.py` (bbox, overhang, clearance exact) + `cable_clip.py` seed + `tests/` → **run pytest, see red/green on a REAL part.** This proves the objective works.
2. `attest.py` score + `passport.py` → emit a passport for the seed part.
3. `factory/generate.py` + `optimize.py` → agents write candidates, race, auto-repair to green.
4. `tricks.py` + gallery → certified tricks the agents reuse.
5. `demo/run_demo.py` + render → the 60s film path.

## Invariants
- Every spec field ↔ one assertion. If it can't be measured, it's not a constraint.
- Numbers, not renders, decide pass/fail. Renders are for the human/video only.
- Agents = Claude Code subagents. Never `claude -p`.
