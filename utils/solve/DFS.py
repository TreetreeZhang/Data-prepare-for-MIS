import os
import argparse
from mis.runner import RunConfig, run_instances
from utils.Logcount import log_run


def main():
    parser = argparse.ArgumentParser(description='DFS feasibility checker')
    parser.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='grid')
    parser.add_argument('--instances', default='10', help='TestInstances subfolder name (e.g., 10, n15, n20)')
    args = parser.parse_args()

    input_folder = f'../TestInstances/{args.instances}'
    cfg = RunConfig(solver=args.solver, strategy='dfs', code_name='DFS')
    num_run = log_run(code_name='DFS')
    run_instances(input_folder, num_run=num_run, config=cfg)
    print('ALL THE CALCULATION HAVE BEEN FINISHED')


if __name__ == '__main__':
    main()

