"""Center-of-mass tip-over check — will the part stand on the bed, or topple?

Drops the part to the bed, projects its center of mass straight down to the Z=min plane, and builds
the support polygon = convex hull of the bed-contact vertices. If the CoM projection lands INSIDE
that polygon the part is statically stable (green); outside — or resting on a knife-edge / line of
zero-area support — it topples (red). Rendered as a top-down plan: footprint, support polygon, and
the CoM dot, so an agent reads stability straight off the picture.

Point-in-polygon uses matplotlib.path.Path (no shapely needed); hull via scipy. Run:
    python -m tools.tipover
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from scipy.spatial import ConvexHull, QhullError  # noqa: E402

from tools.heatmap import part_mesh  # noqa: E402

BG = "#0b0f14"


def tipover_analysis(mesh, bed_tol_frac: float = 0.02):
    """Return dict(com, footprint_xy, support_poly, area, stable) for a mesh (auto-dropped to bed)."""
    m = mesh.copy()
    m.apply_translation([0, 0, -m.vertices[:, 2].min()])
    com = np.asarray(m.center_mass, dtype=float)
    height = float(m.vertices[:, 2].max())
    tol = max(0.2, height * bed_tol_frac)
    bed = m.vertices[m.vertices[:, 2] <= tol][:, :2]
    bed = np.unique(np.round(bed, 3), axis=0)
    footprint = m.vertices[:, :2]
    try:
        hull = ConvexHull(bed)
        poly = bed[hull.vertices]
        area = float(hull.volume)  # 2D hull "volume" == area
        stable = bool(Path(poly).contains_point(com[:2])) and area > 1.0
    except QhullError:
        poly = bed          # collinear -> a line: no stable base
        area = 0.0
        stable = False
    return dict(com=com, footprint=footprint, poly=poly, area=area, stable=stable)


def render_tipover(part, out: str, title: str = "", rotate_deg_x: float = 0.0) -> str:
    mesh = part_mesh(part, rotate_deg_x=rotate_deg_x)
    a = tipover_analysis(mesh)
    stable = a["stable"]
    accent = "#2ecc71" if stable else "#e74c3c"

    fig, ax = plt.subplots(figsize=(6.5, 6), dpi=170, facecolor=BG)
    ax.set_facecolor(BG)

    fp = a["footprint"]
    ax.scatter(fp[:, 0], fp[:, 1], s=4, c="#3a4756", label="part (top-down)")

    poly = a["poly"]
    if len(poly) >= 3 and a["area"] > 1.0:
        pc = plt.Polygon(poly, closed=True, facecolor=accent, alpha=0.22,
                         edgecolor=accent, lw=2, label="support polygon")
        ax.add_patch(pc)
    else:  # degenerate line contact
        ax.plot(poly[:, 0], poly[:, 1], color=accent, lw=3, label="edge contact (no base)")

    com = a["com"]
    ax.scatter([com[0]], [com[1]], s=260, marker="o", facecolor=accent,
               edgecolor="white", lw=1.6, zorder=5, label="center of mass ↓")
    ax.annotate("CoM", (com[0], com[1]), textcoords="offset points", xytext=(10, 8),
                color="white", fontsize=11, weight="bold")

    ax.set_aspect("equal")
    ax.set_xlabel("X (mm)", color="#c9d3dd")
    ax.set_ylabel("Y (mm)", color="#c9d3dd")
    ax.tick_params(colors="#c9d3dd")
    for s in ax.spines.values():
        s.set_color("#33404d")
    verdict = "STABLE ✓" if stable else "TOPPLES ✗"
    ax.set_title(f"{title}   {verdict}   (support area {a['area']:.0f} mm²)",
                 color=accent, fontsize=13, pad=8)
    leg = ax.legend(loc="upper right", framealpha=0.15, facecolor=BG, labelcolor="#c9d3dd")
    for t in leg.get_texts():
        t.set_color("#c9d3dd")

    fig.savefig(out, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    from parts import cable_clip, mini_clip
    render_tipover(cable_clip.make(), "artifacts/viz/tipover_cable_upright.png",
                   title="cable_clip upright")
    render_tipover(cable_clip.make(), "artifacts/viz/tipover_cable_tipped60.png",
                   title="cable_clip tipped 60°", rotate_deg_x=60)
    render_tipover(mini_clip.make(), "artifacts/viz/tipover_mini_upright.png",
                   title="mini_clip upright")
    print("wrote tipover plots")
