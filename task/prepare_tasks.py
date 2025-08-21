#!/usr/bin/env python3
import argparse
import json
import os
from typing import List

from mis.io.reader import read_instance
from mis.strategies.combinations import bfs_order, dfs_order, all_subsets


def generate_tasks(instances: List[str], strategy: str, max_comb_size: int | None) -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instances_parent = os.path.join(base_dir, 'TestInstances')
    tasks_dir = os.path.join(base_dir, 'tasks')
    os.makedirs(tasks_dir, exist_ok=True)

    def gen(keys: List[str]):
        if strategy == 'bfs':
            return bfs_order(keys)
        if strategy == 'dfs':
            return dfs_order(keys)
        return all_subsets(keys)

    for name in instances:
        inst_dir = os.path.join(instances_parent, name)
        if not os.path.isdir(inst_dir):
            print(f"Skip {name}: not a directory under TestInstances")
            continue
        for file in os.listdir(inst_dir):
            if not file.endswith('.json'):
                continue
            json_path = os.path.join(inst_dir, file)
            result = read_instance(json_path)
            if result is None:
                print(f"Skip {file}: read None")
                continue
            _, machines_info, bins_info = result
            keys = list(bins_info.keys())
            task_path = os.path.join(tasks_dir, f"{os.path.splitext(file)[0]}_{strategy}.json")
            tasks = []
            for machine_id, L, W in machines_info:
                for combo in gen(keys):
                    if max_comb_size is not None and len(combo) > max_comb_size:
                        continue
                    tasks.append({
                        'instance': file,
                        'machine_id': machine_id,
                        'L': L,
                        'W': W,
                        'combination': combo
                    })
            with open(task_path, 'w') as out:
                json.dump(tasks, out, ensure_ascii=False, indent=2)
            print(f"Wrote tasks: {task_path}")


def main():
    parser = argparse.ArgumentParser(description='Prepare combination tasks JSON files (to solve elsewhere)')
    parser.add_argument('--strategy', choices=['bfs', 'dfs', 'all'], default='bfs')
    parser.add_argument('--instances', nargs='+', required=True, help='Subfolders under TestInstances (e.g., n15 n20)')
    parser.add_argument('--max-comb-size', type=int, default=None, help='Optional: limit maximum combination size (e.g., 5)')
    args = parser.parse_args()

    generate_tasks(args.instances, args.strategy, args.max_comb_size)


if __name__ == '__main__':
    main()


