import itertools
from typing import Iterable, List


def all_subsets(keys: List[str]) -> Iterable[List[str]]:
    for r in range(2, len(keys) + 1):
        for combo in itertools.combinations(keys, r):
            yield list(combo)


def dfs_order(keys: List[str]) -> Iterable[List[str]]:
    keys = list(keys)
    result: List[List[str]] = []

    def rec(idx: int, current: List[str]):
        if idx == len(keys):
            if len(current) >= 2:
                result.append(list(current))
            return
        rec(idx + 1, current)
        current.append(keys[idx])
        rec(idx + 1, current)
        current.pop()

    rec(0, [])
    for combo in result:
        yield combo


def bfs_order(keys: List[str]) -> Iterable[List[str]]:
    keys = list(keys)
    for r in range(2, len(keys) + 1):
        for combo in itertools.combinations(keys, r):
            yield list(combo)

