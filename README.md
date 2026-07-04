# pytest for atoms

**An agentic 3D-modeling factory.** You describe a part in plain language. Claude Code agents
write [build123d](https://github.com/gumyr/build123d) code to make it — and it **only ships when
it passes a `pytest`-style printability suite.** Those tests aren't an afterthought: they're the
**optimization target** that turns generative CAD from a dice-roll into an *engineering loop*.

> Generating a mesh is easy. Generating a part that **provably fits, prints support-free, and holds**
> is the hard part. So we made the "does it actually work?" checkable — `assert`, not eyeball.

Built **entirely during the RAISE Summit Hackathon 2026** (Cursor track), clean-room. 🇫🇷

---

## The idea in one loop

```
 "a clip for a 6 mm cable on a 22 mm shelf lip, support-free"
                      │
                      ▼
        ┌─────────  spec → objective  ─────────┐
        │  parse into a PartSpec + a pytest     │
        │  suite (the fitness function)         │
        └───────────────────┬───────────────────┘
                            ▼
      ┌──────  agents race to satisfy it  ──────┐
      │  N Claude Code agents each write a       │
      │  build123d program (candidates)          │
      └───────────────────┬──────────────────────┘
                          ▼
      ┌──────────  the attester  ────────────────┐
      │  MEASURE the geometry, run the suite:     │
      │  overhang ≤ 45° · min-wall ≥ 0.8 mm ·     │
      │  real 22 mm shelf + 6 mm cable fit ·      │
      │  fits the plate → per-assertion pass/fail │
      │  + a score (leanest passing part wins)    │
      └───────────────────┬──────────────────────┘
                 red │            │ green
                     ▼            ▼
             auto-repair     manufacturing passport
          (feed the failing   (measured report +
           assertion back)     green tests + STL/3MF)
```

The tests are the **loss function**. The agents are the **search operators**. The factory is the
**optimizer**. That's why it's not a toy.

## Why it is *not* …

- **… a mesh generator.** The output is verified against numbers, not vibes.
- **… a dashboard.** The engine (measure + attest + optimize) is the product; any UI is a lens.
- **… RAG.** The design "tricks" library is admissible only when each trick *ships the assertion
  that proves it* — knowledge that's tested, not retrieved.

## The attester (sample)

```python
def test_cable_clip(part, spec):
    assert bbox_fits(part, spec.max_bbox_mm)        # fits the build plate
    assert max_overhang_deg(part) <= 45             # prints support-free
    assert min_wall_mm(part)      >= spec.min_wall  # printable walls
    assert 0.15 <= shelf_clearance(part) <= 0.6     # grips the *real* 22 mm shelf
    assert cable_clearance(part)  >= 0.2            # the *real* 6 mm cable fits
```

Every number is measured from real geometry (exact B-rep distance, tessellated-mesh ray-casting,
face-normal overhang) against a **real-world probe** — a fixed 22 mm shelf, a 6 mm cable — not a
value derived from the part's own parameters. A too-tight slot *fails*.

> **Honest scope.** Retention ("does it *hold*?") is **not** gated: the reference clip is a slip-fit
> guide with no interference, so there's no real force to measure — and we refuse to fake one. It's
> on the roadmap behind a snap-fit part type. Knowing a measurement from an unmodelled force is the
> point, not a footnote.

## The agentic race

Give the same spec to three independent Claude Code agents and they design it three different ways.
The part-agnostic attester judges them all — `python -m demo.race`:

| design | verdict | material | vs. naive block |
|---|:--:|---:|---:|
| **minimal** — twin-wall + collar ★ | ✅ PASS | **131 mm³** | **80× leaner** |
| C-clamp — lateral grip | ✅ PASS | 215 mm³ | 49× |
| hook-over-lip | ✅ PASS | 374 mm³ | 28× |
| reference block (naive) | ✅ PASS | 10 519 mm³ | 1× |

Same seven assertions green on every one — the attester just ranks by material. Along the way it
caught the minimal design's collar feathering to a **0.013 mm wall** (min-wall fail); the agent fixed
it with a closed ring, verified stable across 400→8000 mesh samples. The tests bite, and the agent
responds. Each design is a `parts/*.py` module exposing the same `make / DEFAULT / probes` contract,
so the engine never knows which part it's judging.

## Run it

```bash
uv venv && uv pip install build123d pytest numpy trimesh rtree matplotlib pillow imageio
source .venv/bin/activate      # then run everything below from the repo root
python -m pytest -q            # the printability suite (the objective) on the reference clip
python -m demo.run_demo        # optimize: attester score falls while every check stays green
python -m demo.repair_demo     # red → green: a broken clip repaired assertion-by-assertion
python -m demo.race            # the agentic race: 3 agent-authored designs, ranked by the engine
python -m tools.render artifacts/race/mini_clip.stl   # render any result to PNG + turntable GIF
```

## Status

Built live during the hackathon. **Done:** the part-agnostic attester (7 real assertions), the
optimizer (tests as loss function), red→green auto-repair, and the 3-agent race. **Roadmap:** a
certified-tricks gallery, a snap-fit part type (which makes retention a real assertion), and
real-print capture.

## License

MIT (see `LICENSE`).
