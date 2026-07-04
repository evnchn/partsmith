"""Cantilever bending-stress proxy — ROADMAP / ILLUSTRATIVE, not a certified FEA.

Treats the part as a cantilever beam clamped at one end of its longest axis with a unit transverse
tip load, and colors it by the resulting bending stress sigma(x) = M(x)*c / I along that axis:
  * M(x) = F * (x_tip - x)                 bending moment (max at the clamped root)
  * I, c come from each axial slice's real cross-section (second moment of area of the slice
    vertices about their transverse centroid; c = max fiber distance).
Red = highest stress (likely-failure zone). This is a strength-of-materials PROXY with an ASSUMED
load case the spec does not actually specify — kept to show the tier, NOT to gate on. Treat as
illustrative only. Matplotlib-only (Agg). Run:
    python -m tools.bending
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import cm  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from tools.heatmap import part_mesh  # noqa: E402

BG = "#0b0f14"


def bending_stress_field(mesh, axis: int = 0, load_axis: int = 2, bins: int = 40):
    """Per-face relative bending stress under a unit tip load. axis = beam length axis (0=X).

    Returns (stress_per_face, x_centers, sigma_profile) with stress normalized to its own max
    (dimensionless — this is a *relative* proxy, absolute N/mm^2 would need a real load).
    """
    v = mesh.vertices
    fc = mesh.triangles_center
    xa = v[:, axis]
    x0, x1 = float(xa.min()), float(xa.max())
    L = x1 - x0 or 1.0
    edges = np.linspace(x0, x1, bins + 1)
    xc = 0.5 * (edges[:-1] + edges[1:])
    F = 1.0
    sigma = np.zeros(bins)
    transverse = [i for i in range(3) if i != axis]
    for b in range(bins):
        sel = (xa >= edges[b]) & (xa <= edges[b + 1])
        if sel.sum() < 3:
            continue
        pts = v[sel][:, transverse]           # cross-section point cloud (2D)
        y = pts[:, load_axis == transverse[1] and 1 or 0]  # fiber coord along the load axis
        # use the load-direction transverse coordinate for c and I
        li = transverse.index(load_axis) if load_axis in transverse else 0
        yc = pts[:, li]
        c = float(np.abs(yc - yc.mean()).max()) or 1e-3
        I = float(np.var(yc) * len(yc)) or 1e-6    # ~ sum (y-ybar)^2, a section-2nd-moment proxy
        M = F * (x1 - xc[b])                        # moment grows toward the clamped root at x1
        sigma[b] = M * c / I
    if sigma.max() > 0:
        sigma = sigma / sigma.max()
    # map each face to its axial bin
    idx = np.clip(np.digitize(fc[:, axis], edges) - 1, 0, bins - 1)
    return sigma[idx], xc, sigma


def render_bending(part, out: str, title: str = "", axis: int = 0, rotate_deg_x: float = 0.0) -> str:
    mesh = part_mesh(part, rotate_deg_x=rotate_deg_x)
    stress, xc, profile = bending_stress_field(mesh, axis=axis)
    norm = Normalize(0.0, 1.0)
    colors = cm.turbo(norm(stress))

    tris = mesh.vertices[mesh.faces]
    fig = plt.figure(figsize=(7, 6), dpi=170, facecolor=BG)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(BG)
    pc = Poly3DCollection(tris, facecolors=colors, edgecolors=(1, 1, 1, 0.05), linewidths=0.1)
    ax.add_collection3d(pc)
    v = mesh.vertices
    ctr = v.mean(axis=0)
    r = float((v.max(axis=0) - v.min(axis=0)).max()) / 2 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=26, azim=-58)
    ax.set_title(f"{title}   bending-stress PROXY (assumed tip load — illustrative)",
                 color="#eef2f6", fontsize=11, pad=2)

    sm = cm.ScalarMappable(norm=norm, cmap="turbo")
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("relative bending stress (red = highest)", color="#eef2f6")
    plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="#eef2f6")
    cb.ax.yaxis.set_tick_params(color="#eef2f6")

    fig.savefig(out, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    from parts import mini_clip
    render_bending(mini_clip.make(), "artifacts/viz/bending_mini_clip.png",
                   title="mini_clip (beam along X)", axis=0)
    print("wrote bending proxy")
