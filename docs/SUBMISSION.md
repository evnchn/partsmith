# Submission — pytest for atoms

RAISE Summit Hackathon 2026 · **Cursor track** · remote · solo · clean-room.
Judging: **Demo 50% · Impact 25% · Creativity 15% · Pitch 10%.**

---

## One-liner (for the form)
**pytest for atoms** — an agentic 3D-modeling factory that only ships a part once it *passes its
own printability tests*. You describe a part; Claude Code agents write build123d; a `pytest`-style
suite is the **optimization target** that turns generative CAD from a dice-roll into an engineering
loop — measured, not eyeballed.

## The problem (Cursor track: "a problem you or someone you know has")
I 3D-print functional parts. Generative CAD tools happily emit a mesh — but *does it actually fit
the shelf? print without supports? have walls thick enough to survive?* You find out after wasting
filament. The missing primitive isn't generation. It's a **build-time test** that a part is real.

## What it does
1. **Spec → objective.** A natural-language request becomes a `PartSpec` **and** a printability
   suite: overhang ≤ 45°, min-wall ≥ 2×nozzle, the *real* 22 mm shelf and 6 mm cable fit within
   clearance, fits the build plate. Every constraint is one `assert`.
2. **Agents write the CAD.** Claude Code agents author build123d programs (compute = Claude Code,
   never `claude -p`). A parametric optimizer is the runnable, no-LLM fallback.
3. **The attester measures real geometry.** Exact B-rep clearance (OpenCascade `BRepExtrema`),
   overhang from face normals, min-wall by ray-casting the mesh. Numbers decide, not renders.
4. **Red → green.** A failing assertion *names* the defect; the loop repairs exactly that and
   re-attests until the suite is green — then keeps optimizing for the leanest part that still passes.
5. **Ships a passport.** Measured report + green suite + a watertight STL. (Real HK print: roadmap.)

## Why it wins its rubric
- **Demo (50%) — does it work?** Yes, live: a broken clip goes red→green in 2 rounds; the optimizer
  drops the attester score ~35% while every assertion stays green; out comes a watertight STL. Real
  measurements, real solid.
- **Impact (25%).** Trustworthy generative manufacturing: the reusable primitive is "a part isn't
  done until it passes physical tests." Fits any printable part, not one demo.
- **Creativity (15%).** "CI/CD for atoms" — the test suite is the loss function; agents are the
  search operators; the attester is the judge.
- **Pitch (10%).** One honest 60-second cut, no slides.

## Honesty (this is the point, not a caveat)
- Clearance probes are the **real-world** shelf/cable, not derived from the part — a too-tight slot
  genuinely fails.
- **Retention is not faked.** A slip-fit guide has no grip force to measure, so we don't assert one;
  it's explicit roadmap behind a snap-fit part. Knowing a measurement from an unmodelled force is
  the credibility.

## 60-second storyboard
| t | beat | on screen |
|---|---|---|
| 0–8s | hook | "AI makes 3D models. Do they actually print? fit? hold? We made that a test." tagline card |
| 8–20s | spec → agents write CAD | the NL spec; a Claude Code agent authoring build123d (real capture) |
| 20–36s | **red → green** | attester rows flip ❌→✅ as the loop repairs the broken clip (the money shot) |
| 36–48s | optimize | score ticking **13148 → 8654** while all rows stay green; material −35% |
| 48–58s | the part | turntable render of the clip + the passport table (all ✅) |
| 58–60s | close | "From a sentence to a proven, printable part. **pytest for atoms.**" |

## Links
- Repo: github.com/evnchn/pytest-for-atoms  ·  License: MIT
- Submit: cerebralvalley.ai/e/raise-summit-hackathon/hackathon/submit  (≤60s video + repo + description)
