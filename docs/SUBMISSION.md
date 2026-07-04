# Submission — Partsmith

RAISE Summit Hackathon 2026 · **Cursor track** · remote · solo · clean-room.
Judging: **Demo 50% · Impact 25% · Creativity 15% · Pitch 10%.**

---

## One-liner (for the form)
**Partsmith** — an agentic 3D-modeling factory. You describe a part; Claude Code agents write
build123d, and it only ships once **Partsmith Caliper** verifies it's printable — overhang, wall
thickness, real-world fit, every check a number measured from the geometry. Those checks are the
optimization target that turns generative CAD from a dice-roll into an engineering loop.

## The problem (Cursor track: "a problem you or someone you know has")
I 3D-print functional parts. Generative CAD tools happily emit a mesh — but *does it fit the shelf?
print without supports? have walls thick enough to survive?* You find out after wasting filament.
The missing primitive isn't generation. It's a **build-time gate** that proves a part is real.

## What it does
1. **Spec → objective.** A natural-language request becomes a `PartSpec` **and** the checks Caliper
   will measure: overhang ≤ 45°, min-wall ≥ 2×nozzle, the *real* 22 mm shelf and 6 mm cable fit,
   fits the build plate. Every constraint is one assertion.
2. **Agents forge the CAD.** Claude Code agents author build123d (compute = Claude Code, never
   `claude -p`). A parametric optimizer is the runnable, no-LLM fallback.
3. **Caliper measures real geometry.** Exact B-rep clearance (OpenCascade), overhang from face
   normals, min-wall by ray-casting the mesh. Numbers decide, not renders.
4. **Red → green.** A failing assertion *names* the defect; the loop repairs exactly that and
   re-checks until green — then keeps optimizing for the leanest part that still passes.
5. **Ships a passport.** Measured report + green checks + a watertight STL. (Real print: roadmap.)

## Why it wins its rubric
- **Demo (50%) — does it work?** Live: a broken clip goes red→green in 2 rounds; the optimizer drops
  the score ~35% while every check stays green; out comes a watertight STL. Real measurements.
- **Impact (25%).** Trustworthy generative manufacturing, and a *platform* (Partsmith Caliper today,
  Partsmith Tricks next) — the reusable primitive is "a part isn't done until it passes physical checks."
- **Creativity (15%).** Verification as the optimization target: agents are search operators, Caliper
  is the judge, and three agents racing one spec land 80× apart on material — all still passing.
- **Pitch (10%).** One honest 60-second cut, no slides.

## Honesty (this is the point, not a caveat)
- Caliper's clearance probes are the **real-world** shelf/cable, not derived from the part — a
  too-tight slot genuinely fails.
- **Retention is not faked.** A slip-fit guide has no grip force to measure, so we don't assert one;
  it's explicit roadmap behind a snap-fit part.

## 60-second storyboard
See `docs/VOICEOVER.md` for the beat-by-beat narration + timing. Beats: title → agents forge → Caliper
red→green → optimize → the 3-agent race (Caliper ranks) → verified part + passport → close.

## Links
- Repo: github.com/evnchn/partsmith  ·  License: MIT
- Submit: cerebralvalley.ai/e/raise-summit-hackathon/hackathon/submit  (≤60s video + repo + description)
