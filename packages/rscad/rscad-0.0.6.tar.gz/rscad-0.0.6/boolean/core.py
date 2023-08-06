"""
	boolean operation implemented without thirdparty python modules
"""

# std
from typing import List, Tuple, Optional

# local
from .rboolean import pyintersect


Point = Tuple[float, float, float]
Points = List[Point]
Tri = Tuple[int, int, int]
Faces = List[Tri]
Mesh = Tuple[Points, Faces]
Tracks = List[int]

Result = Optional[Tuple[Mesh, Tracks]]


def universal(m1: Mesh, m2: Mesh, flip1: bool, flip2: bool) -> Result:
    """
    calculates boolean operation
    the flip flags determine the type of boolean operation

    returns "None" if the boolean operation fails or the input meshes have no overlap
    """
    # TODO implement exception
    return pyintersect(m1, m2, flip1, flip2)


def union(m1: Mesh, m2: Mesh) -> Result:
    """
    part in m1 or m2
    """
    flip1 = True
    flip2 = True
    return universal(m1, m2, flip1, flip2)


def common(m1: Mesh, m2: Mesh) -> Result:
    """
    part in both m1 and m2
    aka intersection
    """
    flip1 = False
    flip2 = False
    return universal(m1, m2, flip1, flip2)


intersection = common


def diff(m1: Mesh, m2: Mesh) -> Result:
    """
    the part in m1 but not in m2
    """
    flip1 = False
    flip2 = True
    return universal(m1, m2, flip1, flip2)
