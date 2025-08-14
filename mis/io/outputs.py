import json
import os
from typing import Dict, Any


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def machine_dir(base_output: str, code_name: str, num_run: int, instance_basename: str, machine_id: int) -> str:
    path = os.path.join(base_output, f"{code_name}{num_run}", instance_basename, str(machine_id))
    ensure_dir(path)
    return path


def load_previous_log(machine_dir_path: str) -> tuple[Dict[str, Any], str]:
    log_path = os.path.join(machine_dir_path, "previous_log.json")
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return json.load(f), log_path
    return {}, log_path


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

