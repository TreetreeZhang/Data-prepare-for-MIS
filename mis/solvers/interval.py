from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from ..utils.scaling import compute_scale_factor


class IntervalSolver:
    def solve(self, L: float, W: float, bins: List[Tuple[float, float]], grid_size: float | None = None, timeout: float | None = None) -> Tuple[bool, Dict[int, List[float]]]:
        all_numbers: List[float] = [L, W]
        for l_i, w_i in bins:
            all_numbers.extend([l_i, w_i])
        scale = compute_scale_factor(all_numbers)

        L_i = int(round(L * scale))
        W_i = int(round(W * scale))
        bins_i = [(int(round(l * scale)), int(round(w * scale))) for (l, w) in bins]

        model = cp_model.CpModel()
        num_bins = len(bins_i)

        x_starts: List[cp_model.IntVar] = []
        y_starts: List[cp_model.IntVar] = []
        x_ends: List[cp_model.IntVar] = []
        y_ends: List[cp_model.IntVar] = []
        x_intervals: List[cp_model.IntervalVar] = []
        y_intervals: List[cp_model.IntervalVar] = []
        rot_vars: List[cp_model.IntVar] = []
        w_eff_vars: List[cp_model.IntVar] = []
        h_eff_vars: List[cp_model.IntVar] = []

        for i, (w, h) in enumerate(bins_i):
            r = model.NewBoolVar(f"r_{i}")
            rot_vars.append(r)

            w_eff = model.NewIntVar(min(w, h), max(w, h), f"w_eff_{i}")
            h_eff = model.NewIntVar(min(w, h), max(w, h), f"h_eff_{i}")
            w_eff_vars.append(w_eff)
            h_eff_vars.append(h_eff)

            model.Add(w_eff == w).OnlyEnforceIf(r.Not())
            model.Add(h_eff == h).OnlyEnforceIf(r.Not())
            model.Add(w_eff == h).OnlyEnforceIf(r)
            model.Add(h_eff == w).OnlyEnforceIf(r)

            x_start = model.NewIntVar(0, L_i, f"x_start_{i}")
            y_start = model.NewIntVar(0, W_i, f"y_start_{i}")
            x_end = model.NewIntVar(0, L_i, f"x_end_{i}")
            y_end = model.NewIntVar(0, W_i, f"y_end_{i}")

            model.Add(x_end == x_start + w_eff)
            model.Add(y_end == y_start + h_eff)
            model.Add(x_end <= L_i)
            model.Add(y_end <= W_i)

            x_starts.append(x_start)
            y_starts.append(y_start)
            x_ends.append(x_end)
            y_ends.append(y_end)

            x_iv = model.NewIntervalVar(x_start, w_eff, x_end, f"x_iv_{i}")
            y_iv = model.NewIntervalVar(y_start, h_eff, y_end, f"y_iv_{i}")
            x_intervals.append(x_iv)
            y_intervals.append(y_iv)

        model.AddNoOverlap2D(x_intervals, y_intervals)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        packing: Dict[int, List[float]] = {}
        ok = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        if ok:
            inv_scale = 1.0 / float(scale)
            for i in range(num_bins):
                x_val = solver.Value(x_starts[i]) * inv_scale
                y_val = solver.Value(y_starts[i]) * inv_scale
                packing[i] = [x_val, y_val]

        return ok, packing

