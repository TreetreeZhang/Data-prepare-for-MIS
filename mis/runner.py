import itertools
import json
import os
import time
from dataclasses import dataclass
from multiprocessing import Pool
from typing import Dict, List, Tuple, Iterable

from .solvers import get_solver
from .strategies.combinations import all_subsets, dfs_order, bfs_order
from .strategies.pruning import Pruner
from .io.reader import read_instance
from .io.outputs import machine_dir, load_previous_log, save_json
from utils.tools import calculate_resolution


@dataclass
class RunConfig:
    solver: str
    strategy: str
    base_output: str = '../output'
    code_name: str = 'RUN'
    timeout: float | None = None


def _combinations(keys: List[str], strategy: str) -> Iterable[List[str]]:
    s = strategy.lower()
    if s == 'dfs':
        return dfs_order(keys)
    if s == 'bfs':
        return bfs_order(keys)
    return all_subsets(keys)


def _process_file(file_name: str, num_run: int, input_folder: str, config: RunConfig) -> None:
    if not file_name.endswith('.json'):
        return
    input_json_path = os.path.join(input_folder, file_name)
    result = read_instance(input_json_path)
    if result is None:
        return
    machines_count, machines_info, bins_info = result

    solver = get_solver(config.solver)

    for machine in machines_info:
        L = machine[1]
        W = machine[2]

        mdir = machine_dir(config.base_output, config.code_name, num_run, file_name.split('.')[0], machine[0])
        previous_log, log_path = load_previous_log(mdir)

        resolutions = calculate_resolution(L, W)
        for grid_size in resolutions:
            resolution_log = {
                "Bins Info": bins_info,
                "Grid Size": grid_size,
                "Container Dimensions": {"Length": L, "Width": W},
                "Results": []
            }
            pruned_log: List[Dict] = []
            pruner = Pruner()

            keys = list(bins_info.keys())
            for combo in _combinations(keys, config.strategy):
                combo_key = str(combo)

                # reuse existing successful results
                if combo_key in previous_log and previous_log[combo_key].get("Is Feasible"):
                    resolution_log["Results"].append({
                        "Combination": list(combo),
                        "Is Feasible": True,
                        "Packing Solution": previous_log[combo_key]["Packing Solution"],
                        "Max Resolution": previous_log[combo_key]["Max Resolution"]
                    })
                    continue

                if pruner.should_prune(combo):
                    pruned_log.append({
                        "Combination": list(combo),
                        "Reason": "Pruned due to failed sub-combination"
                    })
                    resolution_log["Results"].append({
                        "Combination": list(combo),
                        "Is Feasible": False,
                        "Packing Solution": None,
                        "Reason": "Pruned due to failed sub-combination"
                    })
                    continue

                start = time.time()
                IsFeasible, PackingSol = solver.solve(L, W, [bins_info[k] for k in combo], grid_size=grid_size, timeout=config.timeout)
                elapsed = time.time() - start

                resolution_log["Results"].append({
                    "Combination": list(combo),
                    "Is Feasible": IsFeasible,
                    "Packing Solution": PackingSol,
                    "Time Taken (seconds)": elapsed,
                    "Max Resolution": grid_size if IsFeasible else None
                })

                if not IsFeasible:
                    pruner.add_failed(combo)
                else:
                    previous_log[combo_key] = {
                        "Is Feasible": True,
                        "Packing Solution": PackingSol,
                        "Max Resolution": grid_size
                    }

            save_json(os.path.join(mdir, f"{L}x{W}-{grid_size}.json"), resolution_log)
            save_json(os.path.join(mdir, f"{L}x{W}-{grid_size}-pruned.json"), pruned_log)

        save_json(os.path.join(mdir, "previous_log.json"), previous_log)


def run_instances(input_folder: str, num_run: int, config: RunConfig, processes: int | None = None) -> None:
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    tasks = [(f, num_run, input_folder, config) for f in files]
    with Pool(processes=processes) as pool:
        pool.starmap(_process_file, tasks)

