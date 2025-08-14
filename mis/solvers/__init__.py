from typing import Protocol, Dict, Any, Tuple, List


class Solver(Protocol):
    def solve(self, L: float, W: float, bins: List[Tuple[float, float]], grid_size: float | None = None, timeout: float | None = None) -> Tuple[bool, Dict[int, List[float]]]:
        ...


def get_solver(name: str):
    name = str(name).lower()
    if name == 'grid':
        from .grid import GridSolver
        return GridSolver()
    if name == 'interval':
        from .interval import IntervalSolver
        return IntervalSolver()
    if name == 'disjunctive':
        from .disjunctive import DisjunctiveSolver
        return DisjunctiveSolver()
    raise ValueError(f"Unknown solver: {name}")

