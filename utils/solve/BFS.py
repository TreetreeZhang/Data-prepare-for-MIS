import os
import argparse
from mis.runner import RunConfig, run_instances
from utils.Logcount import log_run


def main():
    parser = argparse.ArgumentParser(description='BFS feasibility checker')
    parser.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='grid')
    parser.add_argument('--instances', default='n15', help='TestInstances subfolder name (e.g., n15, n20)')
    args = parser.parse_args()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(current_dir, '..', '..', 'TestInstances', args.instances)

    cfg = RunConfig(solver=args.solver, strategy='bfs', code_name='BFS')
    num_run = log_run(code_name='BFS')
    run_instances(input_folder, num_run=num_run, config=cfg)
    print('ALL THE CALCULATION HAVE BEEN FINISHED')


if __name__ == '__main__':
    main()

