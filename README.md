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
      │  overhang ≤ 45° · min-wall ≥ 2·nozzle ·   │
      │  clearance ≥ 0.4 mm · retention ≥ 8 N     │
      │  → per-assertion pass/fail + a scalar     │
      │    score (passing + least material wins)  │
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
    assert part.max_overhang_deg() <= 45          # prints support-free
    assert part.min_wall_mm()      >= 2 * NOZZLE  # printable walls
    assert part.clearance_mm("cable") >= 0.4      # cable actually fits
    assert part.retention_N()      >= 8           # …and is held
```

## Status

Live build log during the hackathon. Vertical slice first (one part type, real assertions,
end-to-end), then auto-repair → multi-agent race → certified-tricks gallery.

## License

MIT (see `LICENSE`).
