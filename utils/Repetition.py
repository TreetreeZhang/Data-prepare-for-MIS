import itertools
import time

from FeasibilityCheck import *
from Logcount import log_run
from tools import *


def load_previous_log(machine_dir):
    """
    加载或初始化指定机器目录下的 previous_log.json。e
    """
    log_path = os.path.join(machine_dir, "previous_log.json")
    if os.path.exists(log_path):
        with open(log_path, 'r') as json_file:
            return json.load(json_file), log_path
    return {}, log_path


def save_previous_log(log_data, log_path):
    """
    保存 updated 的 previous_log 到文件。
    """
    with open(log_path, 'w') as json_file:
        json.dump(log_data, json_file, indent=4)


def load_previous_log(machine_dir):
    """
    加载或初始化指定机器目录下的 previous_log.json。
    """
    log_path = os.path.join(machine_dir, "previous_log.json")
    if os.path.exists(log_path):
        with open(log_path, 'r') as json_file:
            return json.load(json_file), log_path
    return {}, log_path


def Check_grid_Feasibility(input_folder, num_run):
    for file_name in os.listdir(input_folder):
        check_start_time = time.time()
        print(file_name)
        if file_name.endswith('.json'):
            input_json_path = os.path.join(input_folder, file_name)
            result = json_read(input_json_path)

            if result is None:
                print(f"文件{file_name}.json读取为空")
                continue
            machines_count, machines_info, bins_info = result

            for machine in machines_info:
                L = machine[1]
                W = machine[2]

                # 机器目录路径
                machine_dir = f'../output/repetition{num_run}/{file_name.split(".")[0]}/{machine[0]}'
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

                                # 可行性检查
                                IsFeasible, PackingSol = check_feasi(L, W, grid_size,
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

                with open(log_path, 'w') as json_file:
                    json.dump(previous_log, json_file, indent=4)

        check_end_time = time.time()
        check_time = check_end_time - check_start_time
        with open(f'../output/repetition{num_run}/total_time.txt', "w") as file:
            file.write(f'total time {file_name}:{check_time} s')


if __name__ == '__main__':

    code_name = 'repetition'
    num_run = log_run(code_name='repetition')
    for instance_name in ['10', '15', 'inst', '20']:
        input_folder = f'../TestInstances/{instance_name}'
        Check_grid_Feasibility(input_folder, num_run=num_run)
