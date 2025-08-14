from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from ..utils.geometry import (
    discretize_platform,
    get_inner_fit_polygon,
    get_Phi_jd,
)


class GridSolver:
    def solve(self, L: float, W: float, bins: List[Tuple[float, float]], grid_size: float | None = None, timeout: float | None = None) -> Tuple[bool, Dict[int, List[float]]]:
        if grid_size is None:
            grid_size = 1.0

        # Discretize platform and compute inner-fit polygons
        dots = discretize_platform(L, W, grid_size)
        inner_fit_polygons = {j: get_inner_fit_polygon(dots, l, w, L, W) for j, (l, w) in enumerate(bins)}

        # model
        model = cp_model.CpModel()
        J = list(range(len(bins)))
        status_list = [-1] + J

        # Gamma map
        Gamma: Dict[int, set] = {}
        for d in dots:
            Gamma[d.ID] = set()
            for bin_id, poly in inner_fit_polygons.items():
                if d.ID in [p.ID for p in poly]:
                    Gamma[d.ID].add(bin_id)

        gamma: Dict[Tuple[int, int], cp_model.IntVar] = {}
        for d in dots:
            for s in status_list:
                gamma[d.ID, s] = model.NewBoolVar(f"gamma_d{d.ID}_s{s}")

        # each bin exactly one dot
        for j in J:
            model.add_exactly_one(gamma[d.ID, j] for d in dots)

        # each dot one assignment from valid set or -1
        for d in dots:
            model.add(sum(gamma[d.ID, j] for j in J + [-1]) == 1)
            model.add(sum(gamma[d.ID, j] for j in list(Gamma[d.ID]) + [-1]) == 1)

        # Phi implications
        Phi = {}
        for d in dots:
            for j in J:
                Phi[j, d.ID] = list(get_Phi_jd(dots, bins, j, d))

        for d in dots:
            for j in J:
                for dd in dots:
                    if d.ID != dd.ID and dd.ID in Phi[j, d.ID]:
                        model.AddImplication(gamma[d.ID, j], gamma[dd.ID, -1])

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        packing: Dict[int, List[float]] = {}
        ok = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        if ok:
            for d in dots:
                for s in status_list:
                    if solver.Value(gamma[d.ID, s]) == 1 and s >= 0:
                        packing[s] = [d.x, d.y]

        return ok, packing

