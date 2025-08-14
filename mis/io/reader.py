from typing import Dict, List, Tuple

from utils.tools import json_read


def read_instance(json_path: str) -> Tuple[int, List[Tuple[int, float, float]], Dict[str, Tuple[float, float]]]:
    return json_read(json_path)

