import pandas as pd
import json
import os
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm

class CSVToJSONConverter:
    """将CSV文件转换为JSON格式的转换器"""
    
    def __init__(self, input_base_dir: str, output_base_dir: str):
        """
        初始化转换器
        
        Args:
            input_base_dir: CSV文件的基础目录
            output_base_dir: JSON文件的输出目录
        """
        self.input_base_dir = input_base_dir
        self.output_base_dir = output_base_dir
        
        # 创建输出目录
        os.makedirs(output_base_dir, exist_ok=True)
    
    def get_machines_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """从CSV文件中获取机器信息"""
        first_row = df.iloc[0]
        return [
            {
                "machine_id": 1,
                "num_machine": 1,
                "V": float(first_row['scanning_speed']),
                "U": float(first_row['recoator_speed']),
                "S": float(first_row['setup_m']),
                "L": float(first_row['length_m']),
                "W": float(first_row['width_m']),
                "H": float(first_row['height_m'])
            }
        ]
    
    def process_parts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """处理零件数据"""
        parts = []
        part_id = 1
        
        for _, row in df.iterrows():
            if pd.notna(row['length_part']) and pd.notna(row['width_part']):
                part = {
                    "part_id": part_id,
                    "num_part": 1,  # 每个零件的数量，可以根据需要修改
                    "num_orientation": 1,  # 可能的方向数，可以根据需要修改
                    "volume": float(row['volume_part']),
                    "orientations": [
                        {
                            "l": float(row['length_part']),
                            "w": float(row['width_part']),
                            "h": float(row['height_part']),
                            "support": 0.0  # 支撑值，可以根据需要修改
                        }
                    ]
                }
                parts.append(part)
                part_id += 1
        return parts
    
    def convert_file(self, csv_path: str, json_path: str):
        """转换单个文件"""
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 获取机器和零件信息
        machines = self.get_machines_info(df)
        parts = self.process_parts(df)
        
        # 创建JSON数据
        json_data = {
            "machines": machines,
            "parts": parts,
            "types_machine": len(machines),
            "types_parts": len(parts),
            "num_machine": sum(m["num_machine"] for m in machines),
            "num_parts": sum(p["num_part"] for p in parts)
        }
        
        # 保存JSON文件
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)
    
    def convert_all(self, n_values: List[int]):
        """转换所有文件"""
        for n in n_values:
            print(f"\n处理 n={n} 的数据...")
            
            # 创建输出子目录
            output_subdir = os.path.join(self.output_base_dir, f"n{n}")
            os.makedirs(output_subdir, exist_ok=True)
            
            # 获取所有相关的CSV文件
            input_dir = os.path.join(self.input_base_dir, f"n={n}")
            csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
            
            # 处理每个文件
            for csv_file in tqdm(csv_files, desc=f"Converting n={n} files"):
                csv_path = os.path.join(input_dir, csv_file)
                # 保持原始文件名，只改变扩展名
                json_file = csv_file.replace('.csv', '.json')
                json_path = os.path.join(output_subdir, json_file)
                
                try:
                    self.convert_file(csv_path, json_path)
                except Exception as e:
                    print(f"处理文件 {csv_file} 时出错: {str(e)}")

def main():
    # 设置基础目录
    input_base_dir = "/home/chaorui.zhang/vscode/personal/MIS/Data-prepare-for-MIS/TestInstances/txt/SingleAM_data"
    output_base_dir = "/home/chaorui.zhang/vscode/personal/MIS/Data-prepare-for-MIS/TestInstances/json/SingleAM_data"
    
    # 创建转换器
    converter = CSVToJSONConverter(input_base_dir, output_base_dir)
    
    # 转换所有文件
    n_values = [15, 20, 30, 40]
    converter.convert_all(n_values)

if __name__ == "__main__":
    main()
