"""Assemble the 60-second demo video for Partsmith (verification engine: Caliper).

Builds two remaining frames (manufacturing passport + a corrected leaderboard), synthesizes the
seven-beat narration with macOS `say`, and muxes everything with ffmpeg into
`artifacts/partsmith_demo.mp4`.

Every on-screen number comes from the real attester (see demo/race.py, demo/repair_demo.py); the
narration is kept honest against that output. Run:  .venv/bin/python -m tools.video
"""
from __future__ import annotations

import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.image as mpimg  # noqa: E402

from tools.frames import BG, FG, DIM, CYAN, GREEN, RED, MONO, _canvas, _save, W, H  # noqa: E402

OUT = "artifacts"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
VOICE = "Samantha"
TMP = "artifacts/_video_tmp"


# --------------------------------------------------------------------------- frames

def passport():
    """Manufacturing passport for the race winner (parts/mini_clip), real attester rows."""
    from caliper.spec import CABLE_CLIP
    from caliper.attest import run_suite
    import parts.mini_clip as m

    p = m.DEFAULT
    r = run_suite(m.make(p), CABLE_CLIP, p, m.probes(p, CABLE_CLIP))
    assert r.passed, "winner must pass — refusing to render a dishonest passport"

    fig, ax = _canvas()
    ax.text(0.08, 0.90, "manufacturing passport — minimal clip", color=GREEN, fontsize=19,
            ha="left", va="center", fontweight="bold", **MONO)
    ax.text(0.08, 0.815, f"PASS  ·  all 7 assertions green  ·  score {r.score:.1f}", color=DIM,
            fontsize=16, ha="left", va="center", **MONO)
    y = 0.68
    for label, ok, val, target in r.rows:
        col = GREEN if ok else RED
        ax.text(0.10, y, "✓" if ok else "✗", color=col, fontsize=20, ha="left", va="center",
                fontweight="bold", **MONO)
        ax.text(0.16, y, f"{label:<20}", color=FG, fontsize=18, ha="left", va="center", **MONO)
        ax.text(0.66, y, f"{val:>8.3f}", color=col, fontsize=18, ha="left", va="center", **MONO)
        ax.text(0.82, y, str(target), color=DIM, fontsize=15, ha="left", va="center", **MONO)
        y -= 0.088
    return _save(fig, "passport.png")


def leaderboard():
    """Clean 2x2 leaderboard from the real race renders + real material numbers."""
    from demo.race import attest_module
    from caliper.spec import CABLE_CLIP

    # (module, render png, pretty name, subtitle)
    order = [
        ("cable_clip", "reference block", "naive baseline"),
        ("cclamp_clip", "C-clamp", None),
        ("hook_clip", "hook-over-lip", None),
        ("mini_clip", "minimal clip", "★ WINNER"),
    ]
    mats = {n: attest_module(n, CABLE_CLIP)[2] for n, _, _ in order}
    ref = mats["cable_clip"]

    fig = plt.figure(figsize=(W / 160, H / 160), dpi=160, facecolor=BG)
    fig.text(0.5, 0.955, "one spec · three agents · Caliper ranks by material",
             color=FG, fontsize=16, ha="center", va="center")

    # manual 2x2 grid in figure coords (auto subplot layout scrambles the labels)
    centers = [(0.29, 0.62), (0.71, 0.62), (0.29, 0.15), (0.71, 0.15)]
    iw, ih = 0.26, 0.24
    for (mod, name, sub), (cx, cy) in zip(order, centers):
        axim = fig.add_axes([cx - iw / 2, cy, iw, ih])
        axim.set_facecolor(BG)
        axim.imshow(mpimg.imread(os.path.join(OUT, "race", f"{mod}_render.png")))
        axim.axis("off")
        mat = mats[mod]
        winner = mod == "mini_clip"
        title_col = CYAN if winner else (DIM if mod == "cable_clip" else FG)
        head = name + (f"   {sub}" if sub else "")
        fig.text(cx, cy + ih + 0.035, head, color=title_col, fontsize=15, ha="center", va="center",
                 fontweight="bold" if winner else "normal")
        lean = f"  ·  {int(ref / mat)}× leaner" if winner else ""
        fig.text(cx, cy - 0.045, f"PASS · {mat:.0f} mm³{lean}", color=GREEN if winner else DIM,
                 fontsize=14, ha="center", va="center", **MONO)
    p = os.path.join(OUT, "leaderboard.png")
    fig.savefig(p, facecolor=BG)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- narration

# Honest against demo/race.py + demo/repair_demo.py output (all 4 designs PASS; winner=mini_clip,
# 80.6× leaner; optimize 13,149 -> 8,654 = -34% material). No "it rejects" claim — nothing rejects.
NARRATION = {
    1: "This is Partsmith — an agentic 3D-modeling factory. Describe a part, and it forges one "
       "that's verified printable.",
    2: "You describe a part in plain language; Claude Code agents write the CAD in build123d. But "
       "generating a shape is easy — the real question is: does it fit, print, and hold?",
    3: "So Partsmith Caliper measures it — overhang, wall thickness, real-world fit, every check a "
       "number from the geometry. Here a broken clip fails three checks; the loop reads each "
       "failure, fixes exactly that, and re-checks until every one is green.",
    4: "The checks aren't just a gate — they're the optimization target. Partsmith keeps "
       "searching, cutting material by a third while every check stays green.",
    5: "Give the same spec to three agents and they solve it three different ways. Caliper judges "
       "them all against the same seven checks and ranks by material. The minimal clip wins — "
       "every check green, at eighty times less material than the naive block.",
    6: "Out comes a verified part and a manufacturing passport — every claim a measured number.",
    7: "Partsmith. From a sentence to a part that provably works.",
}

# each beat -> list of (visual asset, fraction of the beat's screen time)
VISUALS = {
    1: [("title.png", 1.0)],
    2: [("spec_agents.png", 1.0)],
    3: [("repair_before.png", 0.45), ("repair_after.png", 0.55)],
    4: [("score_chart.png", 1.0)],
    5: [("leaderboard.png", 1.0)],
    6: [("winner_turntable.gif", 0.55), ("passport.png", 0.45)],
    7: [("close.png", 1.0)],
}

PAD = 0.4      # seconds of tail silence after each VO line
MIN_SEG = 3.0  # floor on any beat's duration
FPS = 30


def _run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def _dur(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", path],
                         check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


VF = ("scale=1280:720:force_original_aspect_ratio=decrease,"
      "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0b0f14,setsar=1,format=yuv420p")


def _still_segment(img, dur, out):
    _run([FFMPEG, "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", img,
          "-vf", VF, "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", out])


def _gif_segment(gif, dur, out):
    _run([FFMPEG, "-y", "-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", gif,
          "-vf", VF, "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", out])


def build():
    os.makedirs(TMP, exist_ok=True)
    print("passport ->", passport())
    print("leaderboard ->", leaderboard())

    video_parts, audio_parts, timing = [], [], []
    for beat in range(1, 8):
        aiff = os.path.join(TMP, f"beat{beat}.aiff")
        subprocess.run(["say", "-v", VOICE, "-o", aiff, NARRATION[beat]], check=True)
        vo = _dur(aiff)
        seg = max(vo + PAD, MIN_SEG)
        timing.append((beat, vo, seg))

        # audio: VO then silence to fill the beat slot, as m4a
        beat_audio = os.path.join(TMP, f"beat{beat}_audio.m4a")
        _run([FFMPEG, "-y", "-i", aiff, "-af", f"apad=whole_dur={seg:.3f}",
              "-c:a", "aac", "-b:a", "192k", beat_audio])
        audio_parts.append(beat_audio)

        # video: split the beat slot across its sub-visuals
        subs = VISUALS[beat]
        for j, (asset, frac) in enumerate(subs):
            sub_dur = seg * frac if j < len(subs) - 1 else seg - sum(seg * f for _, f in subs[:-1])
            src = os.path.join(OUT, asset)
            outv = os.path.join(TMP, f"seg{beat}_{j}.mp4")
            if asset.endswith(".gif"):
                _gif_segment(src, sub_dur, outv)
            else:
                _still_segment(src, sub_dur, outv)
            video_parts.append(outv)

    # concat video, concat audio, then mux
    vlist = os.path.join(TMP, "vlist.txt")
    with open(vlist, "w") as f:
        for p in video_parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    alist = os.path.join(TMP, "alist.txt")
    with open(alist, "w") as f:
        for p in audio_parts:
            f.write(f"file '{os.path.abspath(p)}'\n")

    video_cat = os.path.join(TMP, "video.mp4")
    audio_cat = os.path.join(TMP, "audio.m4a")
    _run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", vlist, "-c", "copy", video_cat])
    _run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", alist, "-c", "copy", audio_cat])

    final = os.path.join(OUT, "partsmith_demo.mp4")
    _run([FFMPEG, "-y", "-i", video_cat, "-i", audio_cat, "-c:v", "copy", "-c:a", "aac",
          "-shortest", final])

    print("\nper-beat timing (beat, vo_s, seg_s):")
    for beat, vo, seg in timing:
        print(f"  beat {beat}: vo={vo:5.2f}s  seg={seg:5.2f}s")
    print(f"total seg = {sum(s for _, _, s in timing):.2f}s")
    print("wrote", final)
    return final


if __name__ == "__main__":
    build()
