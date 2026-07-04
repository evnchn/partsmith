# Partsmith

**Agents that forge parts that fit.** Describe a part in plain language; Claude Code agents write
[build123d](https://github.com/gumyr/build123d) to make it — and it **only ships once it's verified
printable.** Verification isn't an afterthought: it's the **optimization target** the agents design
against, which turns generative CAD from a dice-roll into an engineering loop.

> Generating a mesh is easy. Generating one that **provably fits and prints support-free** is the
> hard part. So Partsmith makes "will it print, and will it fit?" checkable — measured, not eyeballed.

Built **entirely during the RAISE Summit Hackathon 2026** (Cursor track), clean-room. 🇫🇷

## The family

Partsmith is a small platform, not a monolith:

- **Partsmith Caliper** — the verification engine (this repo's core, package [`caliper/`](caliper)).
  It measures real geometry and *gates* every part: overhang, wall thickness, real-world fit — the
  numbers, not vibes. It's the reason you can trust the output, and the objective the agents optimize
  toward. Named for the instrument you'd actually check a printed part with.
- **Partsmith Tricks** *(roadmap)* — a certified library of design tricks (support-free teardrops,
  snap-off support bridges) the agents draw from, each admissible only when it ships the Caliper
  assertion that *proves* it. Tested knowledge, not retrieved.

More `Partsmith X` tools slot under the same umbrella.

---

## The loop

```
 "a clip for a 6 mm cable on a 22 mm shelf lip, support-free"
                      │
       Partsmith ──── ▼
        ┌─────────  spec → objective  ─────────┐
        │  parse into a PartSpec + the checks   │
        │  Caliper will measure against         │
        └───────────────────┬──────────────────┘
                            ▼
      ┌──────  agents forge candidates  ────────┐
      │  Claude Code agents write build123d      │
      └───────────────────┬──────────────────────┘
                          ▼
      ┌────────  Caliper — the gate  ────────────┐
      │  MEASURE real geometry, judge the suite:  │
      │  overhang ≤ 45° · min-wall ≥ 0.8 mm ·     │
      │  real 22 mm shelf + 6 mm cable fit ·      │
      │  fits the plate → pass/fail + a score     │
      └───────────────────┬──────────────────────┘
                 red │            │ green
                     ▼            ▼
             repair to green   ship: part + passport
```

The checks are the **loss function**. The agents are the **search operators**. Partsmith is the
**optimizer**; Caliper is the **judge**. That's why it's not a toy.

## Why it is *not* …

- **… a mesh generator.** The output is verified against numbers, not vibes.
- **… a dashboard.** The engine (Caliper measure + gate + the optimizer) is the product; any UI is a lens.
- **… RAG.** Partsmith Tricks is admissible only when each trick *ships the assertion that proves it* —
  knowledge that's tested, not retrieved.

## Caliper — the gate (sample)

```python
def check(part, spec):                              # every number MEASURED from real geometry
    assert bbox_fits(part, spec.max_bbox_mm)        # fits the build plate
    assert max_overhang_deg(part) <= 45             # prints support-free
    assert min_wall_mm(part)      >= spec.min_wall  # printable walls
    assert 0.15 <= shelf_clearance(part) <= 0.6     # grips the *real* 22 mm shelf
    assert cable_clearance(part)  >= 0.2            # the *real* 6 mm cable fits
```

Exact B-rep distance (OpenCascade), tessellated-mesh ray-casting, face-normal overhang — each check
run against a **real-world probe** (a fixed 22 mm shelf, a 6 mm cable), not a value derived from the
part's own parameters. A too-tight slot *fails*.

**What each check is (no overclaiming):** clearance is *exact* (OpenCascade distance); overhang is a
per-face **normal proxy**; min-wall is a **sampled** inward ray-cast on the watertight mesh — stable
across 400→20 000 samples (`python -m demo.min_wall_convergence`), a solid heuristic, not a certified
gauge. The exported STL is checked **watertight / slicable** in the passport. These are geometric
printability + fit checks — not a claim of physical function.

> **Honest scope.** Retention ("does it *hold*?") is **not** gated: the reference clip is a slip-fit
> guide with no interference, so there's no real force to measure — and Partsmith won't fake one. It's
> on the roadmap behind a snap-fit part. Knowing a measurement from an unmodelled force is the point.

## The agentic race

Give the same spec to three independent Claude Code agents and they forge it three different ways.
Caliper judges them all — `python -m demo.race`:

| design | verdict | material | vs. naive block |
|---|:--:|---:|---:|
| **minimal** — twin-wall + collar ★ | ✅ PASS | **131 mm³** | **80× leaner** |
| C-clamp — lateral grip | ✅ PASS | 215 mm³ | 49× |
| hook-over-lip | ✅ PASS | 374 mm³ | 28× |
| reference block (naive) | ✅ PASS | 10 519 mm³ | 1× |

Same seven checks green on every one — Caliper just ranks by material. Along the way it caught the
minimal design's collar feathering to a **0.013 mm wall** (min-wall fail); the agent fixed it with a
closed ring (`demo/min_wall_convergence.py` shows the final wall stable across 400→20 000 samples).
The checks bite, and the agent responds. Each design is a `parts/*.py` module exposing the same
`make / DEFAULT / probes` contract, so Caliper never knows which part it's judging.

> **Provenance (honest).** The three designs were authored by three separate Claude Code subagents
> during the build, from the shared brief in [`docs/AGENT_RACE.md`](docs/AGENT_RACE.md) — the repo
> ships the resulting static `parts/*.py` modules and Caliper's ranking, **not** a live
> agent-spawning loop. `demo/run_demo.py`'s optimizer tunes a design's *parameters*
> (`ParametricGenerator`); wiring a Claude Code agent as the in-loop generator (`AgentGenerator`, a
> documented hook in `factory/generate.py`) is the next integration, not something this repo claims to
> already do at runtime.

## Run it

```bash
uv venv && uv pip install build123d pytest numpy trimesh rtree matplotlib pillow imageio
source .venv/bin/activate      # then run everything below from the repo root
python -m pytest -q            # Caliper's suite (the objective) on the reference clip
python -m demo.run_demo        # optimize: the score falls while every check stays green
python -m demo.repair_demo     # red → green: a broken clip repaired assertion-by-assertion
python -m demo.race            # the agentic race: 3 agent-forged designs, ranked by Caliper
python -m tools.render artifacts/race/mini_clip.stl   # render any result to PNG + turntable GIF
```

## Status

Built live during the hackathon. **Done:** Partsmith Caliper (7 real checks, part-agnostic), the
optimizer (checks as loss function), red→green auto-repair, and the 3-agent race. **Roadmap:**
Partsmith Tricks (certified gallery), a snap-fit part type (which makes retention a real check), and
real-print capture.

## License

MIT (see `LICENSE`).
