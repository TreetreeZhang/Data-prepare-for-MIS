from typing import FrozenSet, Iterable, List, Set


class Pruner:
    def __init__(self) -> None:
        self.failed: Set[FrozenSet[str]] = set()

    def should_prune(self, combo: List[str]) -> bool:
        combo_set = frozenset(combo)
        for failed in self.failed:
            if failed.issubset(combo_set):
                return True
        return False

    def add_failed(self, combo: List[str]) -> None:
        self.failed.add(frozenset(combo))

