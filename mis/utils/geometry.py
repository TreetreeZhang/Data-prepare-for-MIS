import math
from typing import List


class Dot:
    def __init__(self, ID: int, x: float, y: float):
        self.ID = ID
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Dot(ID={self.ID}, x={self.x}, y={self.y})"


def discretize_platform(L: float, W: float, grid_size: float) -> List[Dot]:
    dots: List[Dot] = []
    idx = 0
    x = 0.0
    while x <= L:
        y = 0.0
        while y <= W:
            dots.append(Dot(idx, x, y))
            idx += 1
            y = round(y + grid_size, 10)
        x = round(x + grid_size, 10)
    return dots


def is_overlap(l_i: float, w_i: float, dot_i: Dot, l_j: float, w_j: float, dot_j: Dot) -> bool:
    return not (
        (dot_j.x >= dot_i.x + l_i or dot_j.x + l_j <= dot_i.x)
        or (dot_j.y >= dot_i.y + w_i or dot_j.y + w_j <= dot_i.y)
    )


def get_inner_fit_polygon(dots: List[Dot], l: float, w: float, L: float, W: float) -> List[Dot]:
    inner: List[Dot] = []
    for d in dots:
        if d.x + l <= L and d.y + w <= W:
            inner.append(d)
    return inner


def get_no_fit_polygon(dots: List[Dot], l_i: float, w_i: float, d_i: Dot, l_j: float, w_j: float) -> List[int]:
    res: List[int] = []
    for d in dots:
        if is_overlap(l_i, w_i, d_i, l_j, w_j, d):
            res.append(d.ID)
    return res


def get_Phi_jd(dots: List[Dot], bins, j: int, d: Dot):
    Phi_jd = {dot.ID for dot in dots}
    l_j, w_j = bins[j]
    for i, (l_i, w_i) in enumerate(bins):
        if i != j:
            no_fit = get_no_fit_polygon(dots, l_j, w_j, d, l_i, w_i)
            Phi_jd.intersection_update(no_fit)
    return Phi_jd

