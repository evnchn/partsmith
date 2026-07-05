# 60-second video — narration + asset/timing map

Assembled by `tools/video.py`: PNG/GIF frames + `say`/Gradium TTS + ffmpeg. Assets in `artifacts/`.
Total ≈ 67 s. Voice: a clean en_US (`say -v Samantha` or Gradium). Narration carries it; captions short.

Branding: **Partsmith** (the printability gate) · **Caliper** (its verification engine). No "pytest", no "atoms".

Re-cut (judge fix #1): the video now **leads with the verification gate**. A cold-open puts the
gasp — the finished winner part + its numbers — at t≈0, then the title reframes Partsmith as *the
printability gate*, not a "factory". A scrubbing judge sees the payoff before deciding to skip.

| # | t (s) | asset | narration (VO) | on-screen caption |
|---|---|---|---|---|
| 0 | 0–9 | `winner_turntable.gif` + burned caption | "One sentence, and this part exists — a hundred and thirty-one cubic millimetres, eighty times leaner than a solid block, every check green." | 131 mm³ · 80× leaner · 7/7 checks green |
| 1 | 9–13 | `title.png` | "This is **Partsmith** — the printability gate for generative CAD." | Partsmith · the printability gate for generative CAD |
| 2 | 13–23 | `spec_agents.png` | "You describe a part; Claude Code agents write the CAD in build123d. Generating a shape is easy — the hard part: does it fit, and does it print?" | does it fit, and does it print? |
| 3 | 23–36 | `repair_before.png` → `repair_after.png` | "So **Caliper** measures it — overhang, wall thickness, fit — every check a number from the geometry. A broken clip fails three checks; the loop reads each failure, fixes it, and re-checks until every one is green." | Caliper: ✗ ✗ ✗ → ✓ ✓ ✓ |
| 4 | 36–45 | `score_chart.png` | "The checks aren't just a gate — they're the optimization target. Partsmith keeps searching, cutting material by a third while every check stays green." | checks = the loss function |
| 5 | 45–59 | `leaderboard.png` | "Give the same spec to three agents and they solve it three different ways. Caliper judges them all against the same seven checks and ranks by material. The minimal clip wins — every check green, at eighty times less material than the naive block." | one spec · three agents · Caliper ranks by material |
| 6 | 59–64 | `winner_turntable.gif` + `passport.png` | "Out comes a verified part and a manufacturing passport — every claim a measured number." | verified part + passport |
| 7 | 64–67 | `close.png` | "**Partsmith.** From a sentence to a part that's proven to fit and print." | github.com/evnchn/partsmith |

## Notes for the assembler
- Beat 0 (cold-open) + frames 3/5 are the highest-value — the gasp up front, then most screen time.
- Beat 0 caption is a transparent lower-third PNG (`cold_open_caption()` in tools/frames.py) burned over
  `winner_turntable.gif` via ffmpeg `overlay`; its numbers (131 mm³ · 80× · 7/7) match `demo/race.py`.
- `title.png`, `close.png` carry the name → regenerate with "Partsmith" (tools/frames.py). `leaderboard.png`
  suptitle should read "…Caliper ranks by material". `passport.png` title "manufacturing passport — minimal clip".
- Every on-screen number must match `demo/race.py`, `demo/repair_demo.py`, `demo/run_demo.py` (repair 3-fail→green;
  optimize 13,149→8,654 = −34%; race minimal 131 mm³ / 80×). Do not overclaim (retention + real print are roadmap).
- Real HK print footage is roadmap — if captured, it replaces frame 6's render as B-roll.
