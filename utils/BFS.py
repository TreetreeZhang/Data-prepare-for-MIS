import itertools
import time
import os
import json
import argparse

from FeasibilityCheck import *
from Logcount import log_run
from tools import *


def load_previous_log(machine_dir):
    """
    加载或初始化指定机器目录下的 previous_log.json。
    """
    log_path = os.path.join(machine_dir, "previous_log.json")
    if os.path.exists(log_path):
        with open(log_path, 'r') as json_file:
            return json.load(json_file), log_path
    return {}, log_path


def Check_BFS(file_name, num_run, input_folder, solver='grid', code_name='BFS'):
    print(file_name)
    if file_name.endswith('.json'):
        input_json_path = os.path.join(input_folder, file_name)
        result = json_read(input_json_path)

        if result is None:
            print(f"文件{file_name}.json读取为空")

        machines_count, machines_info, bins_info = result

        for machine in machines_info:
            L = machine[1]
            W = machine[2]

            # 机器目录路径
            machine_dir = f'../output/{code_name}{num_run}/{file_name.split(".")[0]}/{machine[0]}'
            if not os.path.exists(machine_dir):
                os.makedirs(machine_dir)

            # 加载 previous_log.json
            previous_log, log_path = load_previous_log(machine_dir)

            # 计算动态分辨率
            resolution = calculate_resolution(L, W)

            for grid_size in resolution:
                # 当前分辨率日志初始化
                resolution_log = {
                    "Bins Info": bins_info,
                    "Grid Size": grid_size,
                    "Container Dimensions": {"Length": L, "Width": W},
                    "Results": []
                }

                # 剪枝日志初始化
                pruned_log = []

                # 记录当前分辨率下失败的组合
                failed_combinations = set()

                # 获取所有可能的组合
                for i in range(2, len(bins_info) + 1):
                    for combination in itertools.combinations(bins_info.keys(), i):
                        combination_key = str(combination)

                        # 检查是否在 previous_log 中已完成求解
                        if combination_key in previous_log and previous_log[combination_key]["Is Feasible"]:
                            # 如果已成功求解，直接复用结果
                            resolution_log["Results"].append({
                                "Combination": list(combination),
                                "Is Feasible": True,
                                "Packing Solution": previous_log[combination_key]["Packing Solution"],
                                "Max Resolution": previous_log[combination_key]["Max Resolution"]
                            })
                            continue  # 跳过求解

                        # 剪枝逻辑：跳过包含任何失败子组合的组合
                        for failed_combination in failed_combinations:
                            if failed_combination.issubset(combination):
                                # 检查是否已经记录过该组合
                                if any(
                                        log_entry["Combination"] == list(combination)
                                        for log_entry in resolution_log["Results"]
                                ):
                                    break  # 如果已记录，直接跳过
                                # 否则记录剪枝日志
                                pruned_log.append({
                                    "Combination": list(combination),
                                    "Reason": "Pruned due to failed sub-combination",
                                    "Failed Sub-combination": list(failed_combination)
                                })
                                resolution_log["Results"].append({
                                    "Combination": list(combination),
                                    "Is Feasible": False,
                                    "Packing Solution": None,
                                    "Reason": "Pruned due to failed sub-combination"
                                })
                                break
                        else:
                            # 如果没有被剪枝，则继续求解
                            start_time = time.time()

                            # 可行性检查（由命令行开关控制求解器）
                            s = str(solver).lower()
                            if s == 'interval':
                                solver_fn = check_feasi_interval
                            elif s == 'disjunctive':
                                solver_fn = check_feasi_disjunctive
                            else:
                                solver_fn = check_feasi
                            IsFeasible, PackingSol = solver_fn(L, W, grid_size,
                                                               [bins_info[key] for key in combination])

                            end_time = time.time()
                            elapsed_time = end_time - start_time

                            result = {
                                "Combination": list(combination),
                                "Is Feasible": IsFeasible,
                                "Packing Solution": PackingSol,
                                "Time Taken (seconds)": elapsed_time,
                                "Max Resolution": grid_size if IsFeasible else None
                            }
                            resolution_log["Results"].append(result)

                            # 更新失败组合
                            if not IsFeasible:
                                failed_combinations.add(frozenset(combination))

                            # 更新 previous_log
                            if IsFeasible:
                                previous_log[combination_key] = {
                                    "Is Feasible": True,
                                    "Packing Solution": PackingSol,
                                    "Max Resolution": grid_size
                                }

                # 保存当前分辨率日志到 JSON 文件
                resolution_log_path = os.path.join(machine_dir, f"{L}x{W}-{grid_size}.json")
                with open(resolution_log_path, 'w') as resolution_file:
                    json.dump(resolution_log, resolution_file, indent=4)

                # 保存剪枝日志到 JSON 文件
                pruned_log_path = os.path.join(machine_dir, f"{L}x{W}-{grid_size}-pruned.json")
                with open(pruned_log_path, 'w') as pruned_file:
                    json.dump(pruned_log, pruned_file, indent=4)

            # 保存 updated 的 previous_log
            with open(log_path, 'w') as json_file:
                json.dump(previous_log, json_file, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BFS feasibility checker')
    parser.add_argument('--solver', choices=['grid', 'interval', 'disjunctive'], default='grid', help='Choose solver: grid, interval, or disjunctive')
    parser.add_argument('--instances', default='n15', help='TestInstances subfolder name (e.g., n15, n20)')
    args = parser.parse_args()

    # 获取脚本所在的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建输入文件夹的绝对路径
    input_folder = os.path.join(current_dir, '..', 'TestInstances', args.instances)

    code_name = 'BFS'
    num_run = log_run(code_name=code_name)
    Check_grid_Feasibility_parallel(input_folder, task_name=Check_BFS, num_run=num_run, extra_args=(args.solver,))
    print("ALL THE CALCULATION HAVE BEEN FINISHED")
