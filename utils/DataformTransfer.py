import os

from tools import *


def convert_txt_json(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有 txt 文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_txt_path = os.path.join(input_folder, filename)
            output_json_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.json")

            try:
                convert_txt_to_json(input_txt_path, output_json_path)
            except ValueError as e:
                print(f"处理文件 {filename} 时出错：{e}")


if __name__ == '__main__':
    # 使用示例
    convert_txt_json('/home/chaorui.zhang/vscode/personal/MIS/Data-prepare-for-MIS/TestInstances/txt', '/home/chaorui.zhang/vscode/personal/MIS/Data-prepare-for-MIS/TestInstances/json')
