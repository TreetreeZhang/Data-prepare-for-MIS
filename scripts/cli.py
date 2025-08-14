import argparse
import os

from mis.runner import RunConfig, run_instances
from utils.Logcount import log_run


def main():
    parser = argparse.ArgumentParser(description='MIS unified CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    run_p = sub.add_parser('run', help='Run feasibility on instances')
    run_p.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='grid')
    run_p.add_argument('--strategy', choices=['all', 'bfs', 'dfs'], default='all')
    run_p.add_argument('--instances', nargs='+', default=['n15'])
    run_p.add_argument('--instances-dir', default=None, help='Override TestInstances subdir, absolute or relative')
    run_p.add_argument('--processes', type=int, default=None)
    run_p.add_argument('--timeout', type=float, default=None)

    args = parser.parse_args()

    if args.command == 'run':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_parent = os.path.join(base_dir, '..', 'TestInstances')
        instance_dirs = []
        if args.instances_dir:
            instance_dirs = [args.instances_dir]
        else:
            instance_dirs = [os.path.join(default_parent, name) for name in args.instances]

        cfg = RunConfig(solver=args.solver, strategy=args.strategy, code_name='CLI')
        num_run = log_run(code_name='CLI')
        for d in instance_dirs:
            run_instances(d, num_run=num_run, config=cfg, processes=args.processes)


if __name__ == '__main__':
    main()

