import math
import os

"""
Legacy utilities kept for data IO compatibility. Parallel execution and previous_log
are now handled in mis.runner and mis.io.outputs.
"""


def json_read(json_path):
    '''
    :param json_path: json数据的路径
    :return:
    machines_count：机器的数量,
    machines_info:[(id, L, W)],
    parts_info:[(id,[(L, W, H)])],
    bins_info:{id:[L, W]}
    '''
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error in {json_path}: {e}")
        return None

    # 读取 machines 字段的数量
    machines_count = len(data.get('machines', []))

    # 获取每个 machine_id 对应的 L 和 W
    machines_info = [(machine.get('machine_id'), machine.get('L'), machine.get('W')) for machine in
                     data.get('machines', [])]

    # 获取 parts 字段中的每个 part_id，并根据 num_part 重复每个零件的 l、w 和 h，且对重复的 part_id 进行重新命名
    part_id_counts = {}
    bins_info = {}
    for part in data.get('parts', []):
        part_id = part.get('part_id')
        num_part = part.get('num_part')
        orientations = part.get('orientations', [])
        lwh_triplets = [(orientation.get('l'), orientation.get('w'), orientation.get('h')) for orientation in
                        orientations]

        if part_id not in part_id_counts:
            part_id_counts[part_id] = 0

        for i in range(num_part):
            part_id_counts[part_id] += 1
            unique_part_id = f"{part_id}-{part_id_counts[part_id]}"
            if orientations:
                bins_info[unique_part_id] = (orientations[0].get('l'), orientations[0].get('w'))

    return machines_count, machines_info, bins_info


import json
import os


def convert_txt_to_json(input_txt_path, output_json_path):
    # 读取输入文件内容
    with open(input_txt_path, 'r') as file:
        lines = file.readlines()

    # 移除空行或仅包含换行符的行
    lines = [line.strip() for line in lines if line.strip()]

    # 解析数据
    data = {
        "machines": [],
        "parts": []
    }

    line_index = 0

    # 获取 types_machine 和 types_parts
    if line_index >= len(lines):
        raise ValueError("输入文件格式错误：缺少 types_machine 和 types_parts 数据。")

    types_machine, types_parts = map(int, lines[line_index].split())
    line_index += 1
    data["types_machine"] = types_machine
    data["types_parts"] = types_parts

    # 获取 num_machine 和 num_parts
    if line_index >= len(lines):
        raise ValueError("输入文件格式错误：缺少 num_machine 和 num_parts 数据。")

    num_machine, num_parts = map(int, lines[line_index].split())
    line_index += 1
    data["num_machine"] = num_machine
    data["num_parts"] = num_parts

    # 获取 machine 数据
    for machine_index in range(types_machine):
        if line_index >= len(lines):
            raise ValueError(
                f"输入文件格式错误：缺少机器数据（machine 数据），当前行索引：{line_index}, 当前机器序号：{machine_index + 1}")

        parts = lines[line_index].split()
        if len(parts) < 8:
            raise ValueError(f"输入文件格式错误：机器数据行格式错误，行索引：{line_index}, 行内容：{lines[line_index]}")

        machine_id = int(parts[0])
        num_machine = int(parts[1])
        V, U, S, L, W, H = map(float, parts[2:])
        machine = {
            "machine_id": machine_id,
            "num_machine": num_machine,
            "V": V,
            "U": U,
            "S": S,
            "L": L,
            "W": W,
            "H": H
        }
        data["machines"].append(machine)
        line_index += 1

    # 获取 part 数据
    for part_index in range(types_parts):
        if line_index >= len(lines):
            raise ValueError(
                f"输入文件格式错误：缺少零件数据（part 数据），当前行索引：{line_index}, 当前零件序号：{part_index + 1}")

        parts = lines[line_index].split()
        if len(parts) < 4:
            raise ValueError(f"输入文件格式错误：零件数据行格式错误，行索引：{line_index}, 行内容：{lines[line_index]}")

        part_id = int(parts[0])
        num_part = int(parts[1])
        num_orientation = int(parts[2])
        volume = float(parts[3])
        orientations = []
        line_index += 1

        for orientation_index in range(num_orientation):
            if line_index >= len(lines):
                raise ValueError(
                    f"输入文件格式错误：缺少 orientation 数据，当前行索引：{line_index}, 当前零件序号：{part_index + 1}, 当前 orientation 序号：{orientation_index + 1}")

            orientation_data = list(map(float, lines[line_index].split()))
            if len(orientation_data) < 4:
                raise ValueError(
                    f"输入文件格式错误：orientation 数据行格式错误，行索引：{line_index}, 行内容：{lines[line_index]}")

            orientations.append({
                "l": orientation_data[0],
                "w": orientation_data[1],
                "h": orientation_data[2],
                "support": orientation_data[3]
            })
            line_index += 1

        part = {
            "part_id": part_id,
            "num_part": num_part,
            "num_orientation": num_orientation,
            "volume": volume,
            "orientations": orientations
        }
        data["parts"].append(part)

    # 转换为 JSON 格式
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # 将 JSON 数据写入文件
    with open(output_json_path, 'w') as json_file:
        json_file.write(json_data)

    print(f"转换完成，JSON 数据已保存为 {output_json_path}")


def calculate_resolution(L, W):
    """
    计算从GCD开始的分辨率列表，并降序排序。
    :param L: 托盘长度
    :param W: 托盘宽度
    :return: 递减的分辨率列表（包含0.5）
    """
    # 计算最大公约数
    gcd = math.gcd(int(L), int(W))

    # 找出GCD的所有因子
    factors = [i for i in range(1, gcd + 1) if gcd % i == 0]

    # 降序排列因子并追加0.5
    resolution_list = sorted(factors, reverse=True)
    return resolution_list


# Note: Check_grid_Feasibility_parallel is deprecated and replaced by mis.runner.run_instances
