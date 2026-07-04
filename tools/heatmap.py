"""Grounded proof-of-concept: turn Caliper's geometric analysis into an AGENT-READABLE color image.

Colors every mesh triangle by its overhang severity (green = prints support-free, red = would need
support), so an agent can *read printability off the picture* — not just the scalar max_overhang_deg.
This is the "crank the visual encoder" idea at its cheapest: zero new physics, data Caliper already
computes. Same trick generalizes to a wall-thickness heatmap, a clearance/interference map, etc.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import cm  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from caliper import measure  # noqa: E402

BG = "#0b0f14"


def overhang_severity(mesh) -> np.ndarray:
    """Per-triangle overhang, 0 (safe: vertical/up-facing) .. 1 (at/over the 45deg support limit)."""
    nz = mesh.face_normals[:, 2]
    phi = np.degrees(np.arccos(np.clip(-nz, -1.0, 1.0)))   # angle of normal from straight-down
    overhang = np.where(nz < -1e-6, 90.0 - phi, 0.0)       # only downward faces overhang
    return np.clip(overhang / 45.0, 0.0, 1.0)


def render_overhang(mesh, out: str, title: str = "", elev: float = 26, azim: float = -58) -> str:
    sev = overhang_severity(mesh)
    colors = cm.RdYlGn_r(sev)                              # green (safe) -> red (overhang)
    tris = mesh.vertices[mesh.faces]
    fig = plt.figure(figsize=(6, 6), dpi=170, facecolor=BG)
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
    ax.view_init(elev=elev, azim=azim)
    if title:
        ax.set_title(title, color="#eef2f6", fontsize=13, pad=2)
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    return out


def part_mesh(part, rotate_deg_x: float = 0.0):
    """Caliper's watertight mesh, optionally rotated about X to change which faces point down."""
    import trimesh

    m = measure._to_trimesh(part)
    if rotate_deg_x:
        m = m.copy()
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rotate_deg_x), [1, 0, 0]))
    return m
