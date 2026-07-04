"""Headless part renderer for the demo video — STL -> shaded PNG and turntable GIF.

Pure matplotlib (Agg), so it runs with no display / no GPU. Reads the STL the factory emits, so it
never imports the part modules (decoupled). Usage:
    python -m tools.render artifacts/cable_clip.stl
"""
from __future__ import annotations

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

ACCENT = "#5ac8fa"   # the "green light" cyan
DARK_BG = "#0b0f14"


def _mesh(path: str) -> trimesh.Trimesh:
    m = trimesh.load(path, force="mesh")
    return m


def _draw(ax, m: trimesh.Trimesh, color: str) -> None:
    tris = m.vertices[m.faces]  # (F, 3, 3)
    nz = m.face_normals[:, 2]
    span = float(nz.max() - nz.min()) or 1.0
    shade = 0.45 + 0.55 * (nz - nz.min()) / span      # top faces brighter
    base = np.array(to_rgb(color))
    facecolors = np.clip(shade[:, None] * base[None, :], 0, 1)
    pc = Poly3DCollection(tris, facecolors=facecolors, edgecolors=(1, 1, 1, 0.06), linewidths=0.15)
    ax.add_collection3d(pc)
    v = m.vertices
    ctr = v.mean(axis=0)
    r = float((v.max(axis=0) - v.min(axis=0)).max()) / 2 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()


def render_stl(path: str, out: str, elev: float = 26, azim: float = -58,
               color: str = ACCENT, bg: str = DARK_BG) -> str:
    m = _mesh(path)
    fig = plt.figure(figsize=(6, 6), dpi=170, facecolor=bg)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(bg)
    _draw(ax, m, color)
    ax.view_init(elev=elev, azim=azim)
    fig.tight_layout(pad=0)
    fig.savefig(out, facecolor=bg)
    plt.close(fig)
    return out


def turntable(path: str, out_gif: str, frames: int = 30, elev: float = 24,
              color: str = ACCENT, bg: str = DARK_BG) -> str:
    import imageio.v2 as imageio

    m = _mesh(path)
    imgs = []
    for i in range(frames):
        azim = -180 + 360 * i / frames
        fig = plt.figure(figsize=(5, 5), dpi=120, facecolor=bg)
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(bg)
        _draw(ax, m, color)
        ax.view_init(elev=elev, azim=azim)
        fig.tight_layout(pad=0)
        fig.canvas.draw()
        imgs.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        plt.close(fig)
    imageio.mimsave(out_gif, imgs, duration=0.06, loop=0)
    return out_gif


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "artifacts/cable_clip.stl"
    png = render_stl(src, src.rsplit(".", 1)[0] + "_render.png")
    gif = turntable(src, src.rsplit(".", 1)[0] + "_turntable.gif")
    print("wrote", png)
    print("wrote", gif)
