"""Wall-thickness heatmap — turn Caliper's inward ray-cast into an agent-readable color image.

`measure.wall_thickness_field` returns the FULL field of local wall thicknesses (not just the
`min_wall_mm` scalar). Here we render the part faintly and overlay the sampled surface points
colored by local thickness (turbo_r: RED = thin, blue = thick), with a colorbar carrying real mm
numbers. An agent glances at the red patches to see *where* the part is dangerously thin.

Matplotlib-only (Agg) — no GL / no pyvista needed. Run:
    python -m tools.wall_field
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import cm  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from caliper import measure  # noqa: E402
from tools.heatmap import part_mesh  # noqa: E402

BG = "#0b0f14"


def render_wall_field(part, out: str, title: str = "", samples: int = 2000,
                      floor_mm: float | None = None, elev: float = 26, azim: float = -58,
                      rotate_deg_x: float = 0.0) -> str:
    pts, thk = measure.wall_thickness_field(part, samples=samples)
    mesh = part_mesh(part, rotate_deg_x=rotate_deg_x)
    if rotate_deg_x:
        # rotate the sampled points to match the rotated mesh (field is computed in part frame)
        import trimesh
        T = trimesh.transformations.rotation_matrix(np.radians(rotate_deg_x), [1, 0, 0])
        pts = trimesh.transformations.transform_points(pts, T)

    vmin = float(thk.min())
    # Focus the color range on the PRINTABILITY-relevant thin end. Anything comfortably thick
    # (> ~5x the wall floor) is saturated blue; without this cap a solid block's huge thickness
    # range (tens of mm) washes genuinely-thin zones into the same red-orange as safe material.
    if floor_mm is not None:
        vmax = floor_mm * 5.0
    else:
        vmax = float(np.percentile(thk, 90))
    norm = Normalize(vmin=vmin, vmax=max(vmax, vmin + 1e-6))
    colors = cm.turbo_r(norm(thk))       # turbo_r: low thickness -> red

    fig = plt.figure(figsize=(7, 6), dpi=170, facecolor=BG)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(BG)

    # faint ghost mesh for shape context
    tris = mesh.vertices[mesh.faces]
    ghost = Poly3DCollection(tris, facecolors=(1, 1, 1, 0.04),
                             edgecolors=(1, 1, 1, 0.05), linewidths=0.1)
    ax.add_collection3d(ghost)
    # thickness point cloud on top
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=colors, s=9, depthshade=True)

    v = mesh.vertices
    ctr = v.mean(axis=0)
    r = float((v.max(axis=0) - v.min(axis=0)).max()) / 2 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=elev, azim=azim)

    thinnest = float(thk.min())
    ttl = title or "wall thickness"
    ax.set_title(f"{ttl}   min wall = {thinnest:.2f} mm", color="#eef2f6", fontsize=12, pad=2)

    sm = cm.ScalarMappable(norm=norm, cmap="turbo_r")
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("local wall thickness (mm)  — red = thin", color="#eef2f6")
    cb.ax.yaxis.set_tick_params(color="#eef2f6")
    plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="#eef2f6")
    if floor_mm is not None:
        cb.ax.axhline(norm(floor_mm), color="w", lw=1.2, ls="--")

    fig.savefig(out, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    from parts import cable_clip, mini_clip
    render_wall_field(cable_clip.make(), "artifacts/viz/wall_field_cable_clip.png",
                      title="cable_clip", floor_mm=0.8)
    render_wall_field(mini_clip.make(), "artifacts/viz/wall_field_mini_clip.png",
                      title="mini_clip (thin-wall design)", floor_mm=0.8)
    print("wrote wall_field PNGs")
