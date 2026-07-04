"""Clearance / interference map — color the part by signed distance to a mating probe solid.

For every point on the part surface we compute the signed distance to the probe (the real shelf
tongue / cable). `trimesh` signs distance POSITIVE *inside* the probe, so we negate it into a
clearance value: clearance < 0 means the part material overlaps the probe -> INTERFERENCE (red).
A slip-fit part shows a thin comfortable band; a too-tight slot lights up red exactly where it bites.

Matplotlib-only (Agg). Run:
    python -m tools.clearance_map
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib import cm  # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from caliper import measure  # noqa: E402

BG = "#0b0f14"


def clearance_field(part, probe):
    """Per-face clearance (mm) of the part to a probe solid. Negative = interference (overlap)."""
    pm = measure._to_trimesh(part)
    prm = measure._to_trimesh(probe)
    d = trimesh.proximity.ProximityQuery(prm).signed_distance(pm.triangles_center)
    return pm, -np.asarray(d, dtype=float)   # negate: + inside probe -> - clearance


def render_clearance(part, probe, out: str, title: str = "", clip_mm: float = 2.0,
                     elev: float = 26, azim: float = -58) -> str:
    mesh, clr = clearance_field(part, probe)
    interf = clr[clr < 0]
    # diverging scale centered at 0: red = interference, white ~ contact, blue = clearance.
    lo = float(min(clr.min(), -1e-3))
    hi = float(min(clr.max(), clip_mm))
    norm = TwoSlopeNorm(vmin=lo, vcenter=0.0, vmax=max(hi, 1e-3))
    colors = cm.RdBu(norm(np.clip(clr, lo, hi)))   # RdBu: low(interf) red, high(clear) blue

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
    ax.view_init(elev=elev, azim=azim)

    worst = float(clr.min())
    verdict = f"INTERFERENCE {(-worst):.2f} mm" if worst < -1e-3 else f"min clearance {worst:.2f} mm"
    ax.set_title(f"{title}   {verdict}", color="#eef2f6", fontsize=12, pad=2)

    sm = cm.ScalarMappable(norm=norm, cmap="RdBu")
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("clearance to probe (mm)  — red = interference", color="#eef2f6")
    plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="#eef2f6")
    cb.ax.yaxis.set_tick_params(color="#eef2f6")

    fig.savefig(out, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    from parts import cable_clip
    # good slip-fit vs a too-tight slot that bites the 22 mm shelf
    good = cable_clip.make()
    render_clearance(good, cable_clip.make_shelf_probe(), "artifacts/viz/clearance_good.png",
                     title="cable_clip slot_w=22.4 (slip fit)")
    for sw, tag in [(21.6, "21p6"), (21.0, "21p0")]:
        tight = cable_clip.make({"slot_w": sw})
        probe = cable_clip.make_shelf_probe({"slot_w": sw})
        render_clearance(tight, probe, f"artifacts/viz/clearance_tight_{tag}.png",
                         title=f"cable_clip slot_w={sw} (too tight)")
    print("wrote clearance maps")
