from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from ..utils.scaling import compute_scale_factor


class DisjunctiveSolver:
    def solve(self, L: float, W: float, bins: List[Tuple[float, float]], grid_size: float | None = None, timeout: float | None = None) -> Tuple[bool, Dict[int, List[float]]]:
        all_numbers: List[float] = [L, W]
        for l_i, w_i in bins:
            all_numbers.extend([l_i, w_i])
        scale = compute_scale_factor(all_numbers)

        L_i = int(round(L * scale))
        W_i = int(round(W * scale))
        bins_i = [(int(round(l * scale)), int(round(w * scale))) for (l, w) in bins]

        model = cp_model.CpModel()
        n = len(bins_i)

        x: List[cp_model.IntVar] = []
        y: List[cp_model.IntVar] = []
        r: List[cp_model.IntVar] = []
        w_eff: List[cp_model.IntVar] = []
        h_eff: List[cp_model.IntVar] = []

        for j in range(n):
            x_j = model.NewIntVar(0, L_i, f"x_{j}")
            y_j = model.NewIntVar(0, W_i, f"y_{j}")
            r_j = model.NewBoolVar(f"r_{j}")
            x.append(x_j)
            y.append(y_j)
            r.append(r_j)

            w_j, h_j = bins_i[j]
            w_eff_j = model.NewIntVar(min(w_j, h_j), max(w_j, h_j), f"w_eff_{j}")
            h_eff_j = model.NewIntVar(min(w_j, h_j), max(w_j, h_j), f"h_eff_{j}")
            w_eff.append(w_eff_j)
            h_eff.append(h_eff_j)

            model.Add(w_eff_j == w_j).OnlyEnforceIf(r_j.Not())
            model.Add(h_eff_j == h_j).OnlyEnforceIf(r_j.Not())
            model.Add(w_eff_j == h_j).OnlyEnforceIf(r_j)
            model.Add(h_eff_j == w_j).OnlyEnforceIf(r_j)

            model.Add(x_j + w_eff_j <= L_i)
            model.Add(y_j + h_eff_j <= W_i)

        for i in range(n):
            for j in range(i + 1, n):
                left = model.NewBoolVar(f"left_{i}_{j}")
                right = model.NewBoolVar(f"right_{i}_{j}")
                above = model.NewBoolVar(f"above_{i}_{j}")
                below = model.NewBoolVar(f"below_{i}_{j}")

                model.Add(x[i] + w_eff[i] <= x[j]).OnlyEnforceIf(left)
                model.Add(x[j] + w_eff[j] <= x[i]).OnlyEnforceIf(right)
                model.Add(y[i] + h_eff[i] <= y[j]).OnlyEnforceIf(above)
                model.Add(y[j] + h_eff[j] <= y[i]).OnlyEnforceIf(below)

                model.AddBoolOr([left, right, above, below])

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        packing: Dict[int, List[float]] = {}
        ok = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        if ok:
            inv_scale = 1.0 / float(scale)
            for j in range(n):
                x_val = solver.Value(x[j]) * inv_scale
                y_val = solver.Value(y[j]) * inv_scale
                packing[j] = [x_val, y_val]

        return ok, packing

