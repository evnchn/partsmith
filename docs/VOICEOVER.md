# 60-second video — narration + asset/timing map

Auto-assembled by `tools/video.py` (planned): PNG/GIF frames + `say`/Gradium TTS + ffmpeg, captions
burned in. All assets live in `artifacts/`. Total ≈ 60 s. Voice: a clean en_US (`say -v Samantha`
or Gradium). Keep captions short; the narration carries it.

| # | t (s) | asset | narration (VO) | on-screen caption |
|---|---|---|---|---|
| 1 | 0–4 | `title.png` | "This is **pytest for atoms** — an agentic 3D-modeling factory. It only ships a part once it passes its own printability tests." | pytest for atoms |
| 2 | 4–14 | `spec_agents.png` | "You describe a part in plain language; Claude Code agents write the CAD in build123d. But generating a shape is easy — the real question is: does it actually fit, print, and hold?" | NL spec → build123d, by agents |
| 3 | 14–28 | `repair_before.png` → `repair_after.png` | "So we made that a test suite — overhang, wall thickness, real-world fit — every check a number measured from the geometry. Here a broken clip fails three checks. The loop reads each failure, fixes exactly that, and re-attests until every assertion is green." | ❌❌❌ → ✅✅✅ (the money shot) |
| 4 | 28–38 | `score_chart.png` | "The tests aren't just a gate — they're the optimization target. The factory keeps searching, cutting material by a third while every check stays green." | tests = the loss function |
| 5 | 38–52 | `leaderboard.png` | "Give the same spec to three agents and they solve it three different ways. The attester judges them all against the same seven checks and ranks by material. The minimal clip wins — every assertion green, at eighty times less material than the naive block." | one spec · three agents · all pass · the attester ranks by material |
| 6 | 52–58 | `cclamp_turntable.gif` + `passport.png` | "Out comes a verified part and a manufacturing passport — every claim a measured number." | verified part + passport |
| 7 | 58–60 | `close.png` | "pytest for atoms. From a sentence to a part that provably works." | github.com/evnchn/pytest-for-atoms |

## Notes for the assembler
- Frames 3/5/6 are the highest-value — give them the most screen time.
- `repair_before/after.png`: styled dark "terminal" panels of `demo/repair_demo.py` output (red rows → green rows). Generate from the real command output, don't fake.
- `cclamp_turntable.gif`: `python -m tools.render artifacts/race/cclamp_clip.stl` (turntable).
- Real HK print footage is roadmap — if/when captured, it replaces frame 6's render as B-roll.
- Keep it honest: the numbers on screen must match what `demo/race.py` and `demo/repair_demo.py` actually print.
