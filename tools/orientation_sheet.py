"""Orientation-search contact sheet — the "agent glances at a grid and picks the printable pose".

Rotates a part over ~12 candidate build orientations. For each, computes (from the rotated mesh):
  * max overhang angle (deg past the 45deg FDM support limit shows red), and
  * a support-area proxy = total area of downward faces steeper than the limit (mm^2).
Renders a GRID of small overhang-heatmap thumbnails (green = support-free, red = overhang), with
the best orientation (lowest support area, tie-broken by lowest max-overhang) marked with a ★.

Matplotlib-only (Agg). Run:
    python -m tools.orientation_sheet
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib import cm  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from caliper.spec import OVERHANG_LIMIT_DEG  # noqa: E402
from tools.heatmap import overhang_severity, part_mesh  # noqa: E402

BG = "#0b0f14"

# 12 candidate build orientations as (rx, ry) rotations in degrees. Covers each cube face down
# plus 45deg tips — the poses a slicer would actually consider.
ORIENTATIONS = [
    (0, 0), (90, 0), (180, 0), (270, 0),
    (0, 90), (0, 180), (0, 270),
    (45, 0), (135, 0), (0, 45), (45, 45), (90, 90),
]


def _drop_to_bed(mesh):
    m = mesh.copy()
    m.apply_translation([0, 0, -m.vertices[:, 2].min()])
    return m


def _oriented(base_mesh, rx, ry):
    m = base_mesh.copy()
    if rx:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rx), [1, 0, 0]))
    if ry:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ry), [0, 1, 0]))
    return _drop_to_bed(m)


def orientation_metrics(mesh) -> tuple[float, float]:
    """(max_overhang_deg, support_area_mm2) for a mesh already dropped to the bed.

    Overhang = 90 - angle(normal, -Z) for downward faces; bed-contact faces (first layer) excluded.
    Support area = sum of areas of downward faces whose overhang exceeds the FDM limit.
    """
    nz = mesh.face_normals[:, 2]
    phi = np.degrees(np.arccos(np.clip(-nz, -1.0, 1.0)))
    overhang = np.where(nz < -1e-6, 90.0 - phi, 0.0)
    zc = mesh.triangles_center[:, 2]
    zmin = mesh.vertices[:, 2].min()
    bed = zc <= zmin + 1e-3
    overhang = np.where(bed, 0.0, overhang)
    need_support = overhang > OVERHANG_LIMIT_DEG
    support_area = float(mesh.area_faces[need_support].sum())
    return float(overhang.max()), support_area


def _thumb(ax, mesh, best: bool):
    sev = overhang_severity(mesh)
    colors = cm.RdYlGn_r(sev)
    tris = mesh.vertices[mesh.faces]
    pc = Poly3DCollection(tris, facecolors=colors, edgecolors=(1, 1, 1, 0.04), linewidths=0.05)
    ax.add_collection3d(pc)
    v = mesh.vertices
    ctr = v.mean(axis=0)
    r = float((v.max(axis=0) - v.min(axis=0)).max()) / 2 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=22, azim=-58)


def render_sheet(part, out: str, title: str = "", orientations=ORIENTATIONS) -> str:
    base = part_mesh(part)
    results = []
    for (rx, ry) in orientations:
        m = _oriented(base, rx, ry)
        mo, sa = orientation_metrics(m)
        results.append(dict(rx=rx, ry=ry, mesh=m, max_overhang=mo, support_area=sa))

    best_i = min(range(len(results)), key=lambda i: (round(results[i]["support_area"], 1),
                                                     results[i]["max_overhang"]))

    n = len(results)
    cols = 4
    rows = (n + cols - 1) // cols
    fig = plt.figure(figsize=(cols * 3.0, rows * 3.2), dpi=150, facecolor=BG)
    for i, res in enumerate(results):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        ax.set_facecolor(BG)
        _thumb(ax, res["mesh"], i == best_i)
        star = " ★ BEST" if i == best_i else ""
        col = "#8ef58e" if i == best_i else "#c9d3dd"
        ax.set_title(
            f"rx={res['rx']:>3} ry={res['ry']:>3}{star}\n"
            f"overhang {res['max_overhang']:.0f}°  support {res['support_area']:.0f} mm²",
            color=col, fontsize=9, pad=-2)
    sup = f"{title}  —  orientation search (green = support-free)"
    fig.suptitle(sup, color="#eef2f6", fontsize=14, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    return out


if __name__ == "__main__":
    from parts import cable_clip, mini_clip
    render_sheet(cable_clip.make(), "artifacts/viz/orientation_sheet_cable_clip.png",
                 title="cable_clip")
    render_sheet(mini_clip.make(), "artifacts/viz/orientation_sheet_mini_clip.png",
                 title="mini_clip")
    print("wrote orientation sheets")
