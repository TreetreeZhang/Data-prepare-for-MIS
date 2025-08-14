#!/usr/bin/env python3
import argparse
import os
from typing import List

from mis.runner import RunConfig, run_instances
from utils.Logcount import log_run


def prepare_txt(input_dir: str, output_dir: str) -> None:
    # Lazy import to avoid pandas/tqdm dependency when not needed
    from utils.data_transfer import convert_txt_json
    convert_txt_json(input_dir, output_dir)


def _detect_n_values(input_base_dir: str) -> List[int]:
    n_values: List[int] = []
    if not os.path.isdir(input_base_dir):
        return n_values
    for name in os.listdir(input_base_dir):
        if name.startswith('n='):
            try:
                n_values.append(int(name.split('=')[1]))
            except ValueError:
                continue
    return sorted(list(set(n_values)))


def prepare_csv(input_base_dir: str, output_base_dir: str, n_values: List[int] | None = None) -> None:
    # Lazy import to avoid pandas/tqdm dependency when not preparing CSV
    from utils.csv_to_json import convert_csv_dir
    convert_csv_dir(input_base_dir, output_base_dir, n_values=n_values)


def solve(strategy: str, solver: str, instances: list[str] | None, instances_dir: str | None, processes: int | None, timeout: float | None) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_parent = os.path.join(base_dir, 'TestInstances')
    default_output = os.path.join(base_dir, 'output')
    instance_dirs: List[str] = []
    if instances_dir:
        instance_dirs = [instances_dir]
    else:
        if not instances:
            instances = ['n15']
        instance_dirs = [os.path.join(default_parent, name) for name in instances]

    cfg = RunConfig(solver=solver, strategy=strategy, code_name='MAIN', timeout=timeout, base_output=default_output)
    num_run = log_run(code_name='MAIN')
    for d in instance_dirs:
        run_instances(d, num_run=num_run, config=cfg, processes=processes)


def main():
    parser = argparse.ArgumentParser(description='MIS main entry')
    sub = parser.add_subparsers(dest='command', required=True)

    p_prep = sub.add_parser('prepare', help='Prepare data (TXT/CSV to JSON)')
    p_prep.add_argument('--from', dest='src', choices=['txt', 'csv'], required=True)
    p_prep.add_argument('--in', dest='input', required=True, help='Input path (dir)')
    p_prep.add_argument('--out', dest='output', required=True, help='Output directory for JSON files')
    p_prep.add_argument('--n-values', nargs='+', type=int, default=None, help='Only for CSV: list of n values (e.g., 15 20 30)')

    p_run = sub.add_parser('solve', help='Run feasibility solving')
    p_run.add_argument('--strategy', choices=['bfs', 'dfs', 'all'], default='bfs')
    p_run.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='interval')
    p_run.add_argument('--instances', nargs='+', default=None, help='Subfolders under TestInstances (e.g., n15 n20)')
    p_run.add_argument('--instances-dir', default=None, help='Override TestInstances directory (absolute or relative)')
    p_run.add_argument('--processes', type=int, default=None)
    p_run.add_argument('--timeout', type=float, default=None)

    args = parser.parse_args()

    if args.command == 'prepare':
        if args.src == 'txt':
            prepare_txt(args.input, args.output)
        else:
            prepare_csv(args.input, args.output, n_values=args.n_values)
    elif args.command == 'solve':
        solve(strategy=args.strategy, solver=args.solver, instances=args.instances, instances_dir=args.instances_dir, processes=args.processes, timeout=args.timeout)


if __name__ == '__main__':
    main()

