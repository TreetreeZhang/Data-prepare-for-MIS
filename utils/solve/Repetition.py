import argparse
from mis.runner import RunConfig, run_instances
from utils.Logcount import log_run


def main():
    parser = argparse.ArgumentParser(description='Repetition feasibility checker')
    parser.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='grid')
    parser.add_argument('--instances', nargs='+', default=['10', '15', 'inst', '20'])
    args = parser.parse_args()

    cfg = RunConfig(solver=args.solver, strategy='all', code_name='repetition')
    num_run = log_run(code_name='repetition')
    for instance_name in args.instances:
        input_folder = f'../TestInstances/{instance_name}'
        run_instances(input_folder, num_run=num_run, config=cfg)
    print('ALL THE CALCULATION HAVE BEEN FINISHED')


if __name__ == '__main__':
    main()

