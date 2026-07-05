"""Generate the static video frames (title, spec, red->green panels, close).

Dark styled 1280x720 panels via matplotlib (Agg, headless). Content is real (the repair rows are
the actual demo output). Run:  python -m tools.frames
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BG = "#0b0f14"
FG = "#eef2f6"
DIM = "#8a97a6"
CYAN = "#5ac8fa"
GREEN = "#4ade80"
RED = "#ff6b6b"
MONO = {"family": "monospace"}
W, H = 1280, 720
OUT = "artifacts"


def _canvas():
    fig = plt.figure(figsize=(W / 160, H / 160), dpi=160, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig, ax


def _save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=BG); plt.close(fig)
    return p


def title():
    fig, ax = _canvas()
    ax.text(0.5, 0.60, "Partsmith", color=CYAN, fontsize=54, ha="center", va="center",
            fontweight="bold", **MONO)
    ax.text(0.5, 0.44, "the printability gate for generative CAD", color=FG, fontsize=22, ha="center")
    ax.text(0.5, 0.34, "a part ships only when it passes its own printability tests", color=DIM,
            fontsize=16, ha="center")
    return _save(fig, "title.png")


def cold_open_caption():
    """Transparent lower-third caption burned over the winner turntable for the cold-open (beat 0).

    Numbers match demo/race.py: mini_clip = 131 mm³, 80.6× leaner than the reference block,
    all 7 assertions green.
    """
    fig = plt.figure(figsize=(W / 160, H / 160), dpi=160)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.patch.set_alpha(0)
    ax.add_patch(plt.Rectangle((0, 0.05), 1, 0.17, color=BG, alpha=0.72, zorder=1))
    ax.text(0.5, 0.135, "131 mm³ · 80× leaner · 7/7 checks green", color=GREEN, fontsize=22,
            ha="center", va="center", fontweight="bold", zorder=2, **MONO)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "cold_open_caption.png")
    fig.savefig(p, transparent=True); plt.close(fig)
    return p


def spec_agents():
    fig, ax = _canvas()
    ax.text(0.5, 0.78, "you describe a part", color=DIM, fontsize=18, ha="center")
    ax.text(0.5, 0.66, '"a clip for a 6 mm cable that grips a 22 mm shelf lip,\nprints support-free"',
            color=FG, fontsize=22, ha="center", **MONO)
    ax.text(0.5, 0.42, "→ Claude Code agents write build123d", color=CYAN, fontsize=22, ha="center")
    ax.text(0.5, 0.28, "generating a shape is easy.\ndoes it fit, and does it print?", color=DIM,
            fontsize=18, ha="center")
    return _save(fig, "spec_agents.png")


def _repair_panel(name, title_txt, rows, title_color):
    fig, ax = _canvas()
    ax.text(0.08, 0.88, title_txt, color=title_color, fontsize=26, ha="left", va="center",
            fontweight="bold", **MONO)
    y = 0.72
    for label, ok, val, target in rows:
        mark, col = ("✓", GREEN) if ok else ("✗", RED)
        ax.text(0.10, y, mark, color=col, fontsize=22, ha="left", va="center",
                fontweight="bold", **MONO)
        ax.text(0.16, y, f"{label:<20}", color=FG, fontsize=19, ha="left", va="center", **MONO)
        ax.text(0.62, y, f"{val:>8}", color=col, fontsize=19, ha="left", va="center", **MONO)
        ax.text(0.80, y, target, color=DIM, fontsize=16, ha="left", va="center", **MONO)
        y -= 0.095
    return _save(fig, name)


def repair_frames():
    before = [
        ("bbox_x", False, "66.000", "<= 60"),
        ("shelf_clearance", False, "0.025", "[0.15,0.6]"),
        ("cable_clearance", False, "0.050", ">= 0.2"),
        ("max_overhang", True, "0.000", "<= 45"),
        ("min_wall", True, "2.475", ">= 0.8"),
    ]
    after = [
        ("bbox_x", True, "58.800", "<= 60"),
        ("shelf_clearance", True, "0.275", "[0.15,0.6]"),
        ("cable_clearance", True, "0.250", ">= 0.2"),
        ("max_overhang", True, "0.000", "<= 45"),
        ("min_wall", True, "2.475", ">= 0.8"),
    ]
    a = _repair_panel("repair_before.png", "attest: FAIL  (3 broken)", before, RED)
    b = _repair_panel("repair_after.png", "repaired: PASS  (all green)", after, GREEN)
    return a, b


def close():
    fig, ax = _canvas()
    ax.text(0.5, 0.58, "Partsmith", color=CYAN, fontsize=44, ha="center", fontweight="bold",
            **MONO)
    ax.text(0.5, 0.44, "from a sentence to a part that's proven to fit and print", color=FG,
            fontsize=19, ha="center")
    ax.text(0.5, 0.30, "github.com/evnchn/partsmith", color=DIM, fontsize=18, ha="center",
            **MONO)
    return _save(fig, "close.png")


if __name__ == "__main__":
    for p in [title(), cold_open_caption(), spec_agents(), *repair_frames(), close()]:
        print("wrote", p)
