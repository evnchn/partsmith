"""Geometry queries over a build123d Part/Solid — THE HARD, DEFENSIBLE CORE.

Every function returns a real number computed from real geometry (B-rep via OpenCascade, or a
tessellated mesh via trimesh). Nothing here eyeballs or fabricates a value. Two functions are
explicitly documented *proxies* (`print_time_s`, `retention_N`) — they are labelled engineering
estimates, not measurements, and say so in their docstrings.
"""
from __future__ import annotations

from math import acos, degrees

import numpy as np

from .spec import NOZZLE_MM, LAYER_MM

# ---------------------------------------------------------------------------
# Pure geometry (measured)
# ---------------------------------------------------------------------------

def bbox_mm(part) -> tuple[float, float, float]:
    """Axis-aligned bounding-box size (dx, dy, dz) from the real B-rep."""
    s = part.bounding_box().size
    return (float(s.X), float(s.Y), float(s.Z))


def material_mm3(part) -> float:
    """Solid volume of the part (mm^3)."""
    return float(part.volume)


def print_time_s(part) -> float:
    """PROXY (not a measurement): rough FDM print time.

    Estimate = extruded_volume / volumetric_flow, where volumetric_flow = nozzle cross-section
    (NOZZLE_MM * LAYER_MM) * print_speed. This ignores travel, infill %, perimeters and accel;
    it is a monotone-in-material stand-in good enough to *rank* candidates, nothing more.
    """
    print_speed = 50.0  # mm/s
    flow = (NOZZLE_MM * LAYER_MM) * print_speed  # mm^3/s
    return float(material_mm3(part) / flow)


def max_overhang_deg(part) -> float:
    """Worst overhang angle (deg above horizontal) among downward-facing, non-bed faces.

    Convention: vertical wall -> 0, horizontal ceiling -> 90, a 45deg facet -> 45. FDM needs
    support when this exceeds OVERHANG_LIMIT_DEG. Bed-contact faces are excluded (the first layer
    is not an overhang). Returns 0.0 if there are no downward faces above the bed.
    """
    zmin = part.bounding_box().min.Z
    worst = 0.0
    for face in part.faces():
        try:
            c = face.center()
            n = face.normal_at(c)
        except Exception:
            continue  # degenerate / unparametrised face — skip, don't fabricate
        # normalise
        mag = (n.X ** 2 + n.Y ** 2 + n.Z ** 2) ** 0.5
        if mag == 0:
            continue
        nz = n.Z / mag
        if nz >= -1e-6:
            continue  # not a downward-facing face
        if c.Z <= zmin + 1e-3:
            continue  # resting on the bed — excluded
        phi = degrees(acos(max(-1.0, min(1.0, -nz))))  # angle of normal below -Z
        overhang = 90.0 - phi
        worst = max(worst, overhang)
    return float(worst)


def clearance_mm(part, probe) -> float:
    """Exact minimum distance between two solids (mm), via OCC BRepExtrema.

    `part` and `probe` are build123d objects; `.wrapped` is the underlying TopoDS shape.
    Returns 0.0 when the solids touch or interpenetrate (BRepExtrema clamps at 0).
    """
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape

    d = BRepExtrema_DistShapeShape(part.wrapped, probe.wrapped)
    return float(d.Value())


def _to_trimesh(part):
    import trimesh

    verts, tris = part.tessellate(0.1)
    v = np.array([(p.X, p.Y, p.Z) for p in verts], dtype=float)
    f = np.array(tris, dtype=np.int64)
    return trimesh.Trimesh(vertices=v, faces=f, process=False)


def min_wall_mm(part, samples: int = 400) -> float:
    """Thinnest wall (mm), estimated by inward ray-casting on a tessellated mesh.

    Sample surface points + their outward normals, nudge each origin just inside the surface, cast
    a ray inward, and take the nearest forward hit distance as the local wall thickness. The
    minimum positive thickness over all samples is returned. Raises if no backend can cast rays
    (never returns a fake large number).
    """
    import trimesh

    mesh = _to_trimesh(part)
    try:
        pts, face_idx = trimesh.sample.sample_surface(mesh, samples, seed=0)  # deterministic
    except TypeError:
        pts, face_idx = trimesh.sample.sample_surface(mesh, samples)
    normals = mesh.face_normals[face_idx]

    eps = 1e-3
    origins = pts - normals * eps      # nudge just inside the surface
    directions = -normals              # cast inward

    intersector = mesh.ray  # rtree/pyembree if available, else pure-python fallback
    locations, index_ray, _ = intersector.intersects_location(
        origins, directions, multiple_hits=False
    )
    if len(locations) == 0:
        raise RuntimeError(
            "min_wall_mm: ray-caster returned no hits — cannot measure wall thickness. "
            "Install a ray backend (`uv pip install rtree`) or check the mesh is watertight."
        )
    dist = np.linalg.norm(locations - origins[index_ray], axis=1)
    dist = dist[dist > 1e-6]
    if dist.size == 0:
        raise RuntimeError("min_wall_mm: no positive-distance hits — degenerate measurement.")
    return float(dist.min())


def hole_diameters_mm(part) -> list[float]:
    """Best-effort diameters of cylindrical faces (mm). Returns [] if none/unreliable.

    Not load-bearing for the spine; the exact cable fit is checked with clearance_mm against a
    real probe instead.
    """
    from build123d import GeomType

    out: list[float] = []
    for face in part.faces():
        try:
            if face.geom_type != GeomType.CYLINDER:
                continue
            r = float(face.radius)
        except Exception:
            continue
        out.append(2.0 * r)
    return out


def retention_N(part, spec, params: dict) -> float:
    """PROXY (engineering estimate, NOT a measurement): how hard the cable is held, in newtons.

    Model: the wall of material between the cable bore and the nearest outer edge acts as a short
    fixed beam. Pressing the cable in flexes it by a small assumed elastic pinch `pinch_mm`; the
    beam reacts with a normal force F = k * pinch, and friction holds the cable with mu * F.

        k = E * b * t^3 / (4 * L^3)     (fixed-beam-like flexural stiffness)

    with PLA E = 2000 MPa (N/mm^2), b = slot_len (contact height stand-in), t = the *real* wall
    thickness between bore and outer edge (measured from geometry, not a nominal), and L = a short
    effective free arm (~ bore diameter + wall). Every input is geometry-derived except the two
    labelled tuning assumptions (`pinch_mm`, `mu`). This is a ranking/estimation proxy, not a
    certified pull-test — treat it as such.
    """
    p = params
    E = 2000.0  # MPa == N/mm^2, PLA
    b = float(p["slot_len"])                       # mm, contact-height stand-in
    # real wall between bore outer surface and the +X outer face, measured from as-built geometry
    xmax = part.bounding_box().max.X
    t = float(xmax - (p["bore_x"] + p["bore_r"]))  # mm, geometry-derived wall thickness
    L = float(2.0 * p["bore_r"] + p["wall"])       # mm, short effective cantilever arm
    k = E * b * t ** 3 / (4.0 * L ** 3)            # N/mm
    F_normal = k * float(p["pinch_mm"])            # N
    return float(p["mu"] * F_normal)
