# std
from typing import Optional

# thirdparty
import numpy as np
import pyvista as pv

# local
from . import core


def overhangs(mesh: pv.PolyData, ref_normal):
    assert mesh.is_all_triangles, "overhangs expect triangulted mesh"
    tris = mesh.faces.reshape((-1, 4))[:, 1:]
    res = core.overhangs(mesh.points, tris, ref_normal)
    return np.array(res)


def draft_angles(mesh, ref_normal, degrees=False, face=True):
    if face:
        normals = mesh.face_normals
    else:
        normals = mesh.point_normals

    res = core.normals2angles(normals, ref_normal, degrees)
    return np.array(res)


def draft_mask(mesh, ref_normal, value, invert=False, degrees=False, face=True):
    if face:
        normals = mesh.face_normals
    else:
        normals = mesh.point_normals

    if degrees:
        value = np.deg2rad(value)

    res = core.draft_mask(normals, ref_normal, value, invert)
    return np.array(res)
