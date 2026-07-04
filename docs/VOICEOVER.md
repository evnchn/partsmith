# 60-second video — narration + asset/timing map

Assembled by `tools/video.py`: PNG/GIF frames + `say`/Gradium TTS + ffmpeg. Assets in `artifacts/`.
Total ≈ 60 s. Voice: a clean en_US (`say -v Samantha` or Gradium). Narration carries it; captions short.

Branding: **Partsmith** (the factory) · **Caliper** (its verification engine). No "pytest", no "atoms".

| # | t (s) | asset | narration (VO) | on-screen caption |
|---|---|---|---|---|
| 1 | 0–4 | `title.png` | "This is **Partsmith** — an agentic 3D-modeling factory. Describe a part, and it forges one that's verified printable." | Partsmith |
| 2 | 4–14 | `spec_agents.png` | "You describe a part in plain language; Claude Code agents write the CAD in build123d. But generating a shape is easy — the real question is: does it fit, print, and hold?" | agents forge it in build123d |
| 3 | 14–28 | `repair_before.png` → `repair_after.png` | "So **Partsmith Caliper** measures it — overhang, wall thickness, real-world fit, every check a number from the geometry. Here a broken clip fails three checks; the loop reads each failure, fixes exactly that, and re-checks until every one is green." | Caliper: ✗ ✗ ✗ → ✓ ✓ ✓ |
| 4 | 28–38 | `score_chart.png` | "The checks aren't just a gate — they're the optimization target. Partsmith keeps searching, cutting material by a third while every check stays green." | checks = the loss function |
| 5 | 38–52 | `leaderboard.png` | "Give the same spec to three agents and they solve it three different ways. Caliper judges them all against the same seven checks and ranks by material. The minimal clip wins — every check green, at eighty times less material than the naive block." | one spec · three agents · Caliper ranks by material |
| 6 | 52–58 | `winner_turntable.gif` + `passport.png` | "Out comes a verified part and a manufacturing passport — every claim a measured number." | verified part + passport |
| 7 | 58–60 | `close.png` | "**Partsmith.** From a sentence to a part that provably works." | github.com/evnchn/partsmith |

## Notes for the assembler
- Frames 3/5/6 are the highest-value — most screen time.
- `title.png`, `close.png` carry the name → regenerate with "Partsmith" (tools/frames.py). `leaderboard.png`
  suptitle should read "…Caliper ranks by material". `passport.png` title "manufacturing passport — minimal clip".
- Every on-screen number must match `demo/race.py`, `demo/repair_demo.py`, `demo/run_demo.py` (repair 3-fail→green;
  optimize 13,149→8,654 = −34%; race minimal 131 mm³ / 80×). Do not overclaim (retention + real print are roadmap).
- Real HK print footage is roadmap — if captured, it replaces frame 6's render as B-roll.
