import os
import json
from typing import List, Dict, Any

import pandas as pd
from tqdm import tqdm


class CSVToJSONConverter:
    """将CSV文件转换为JSON格式的转换器"""

    def __init__(self, input_base_dir: str, output_base_dir: str):
        self.input_base_dir = input_base_dir
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)

    def get_machines_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
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
        parts: List[Dict[str, Any]] = []
        part_id = 1
        for _, row in df.iterrows():
            if pd.notna(row['length_part']) and pd.notna(row['width_part']):
                parts.append({
                    "part_id": part_id,
                    "num_part": 1,
                    "num_orientation": 1,
                    "volume": float(row['volume_part']),
                    "orientations": [
                        {
                            "l": float(row['length_part']),
                            "w": float(row['width_part']),
                            "h": float(row['height_part']),
                            "support": 0.0
                        }
                    ]
                })
                part_id += 1
        return parts

    def convert_file(self, csv_path: str, json_path: str):
        df = pd.read_csv(csv_path)
        machines = self.get_machines_info(df)
        parts = self.process_parts(df)
        json_data = {
            "machines": machines,
            "parts": parts,
            "types_machine": len(machines),
            "types_parts": len(parts),
            "num_machine": sum(m["num_machine"] for m in machines),
            "num_parts": sum(p["num_part"] for p in parts)
        }
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)

    def convert_all(self, n_values: List[int]):
        for n in n_values:
            output_subdir = os.path.join(self.output_base_dir, f"n{n}")
            os.makedirs(output_subdir, exist_ok=True)
            input_dir = os.path.join(self.input_base_dir, f"n={n}")
            csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
            for csv_file in tqdm(csv_files, desc=f"Converting n={n} files"):
                csv_path = os.path.join(input_dir, csv_file)
                json_file = csv_file.replace('.csv', '.json')
                json_path = os.path.join(output_subdir, json_file)
                self.convert_file(csv_path, json_path)


def convert_csv_dir(input_base_dir: str, output_base_dir: str, n_values: List[int] | None = None) -> None:
    converter = CSVToJSONConverter(input_base_dir, output_base_dir)
    if n_values:
        converter.convert_all(n_values)
        return
    for f in os.listdir(input_base_dir):
        if f.endswith('.csv'):
            csv_path = os.path.join(input_base_dir, f)
            json_path = os.path.join(output_base_dir, f.replace('.csv', '.json'))
            converter.convert_file(csv_path, json_path)


if __name__ == '__main__':
    convert_csv_dir('/path/to/input', '/path/to/output', n_values=[15, 20, 30])

