#!/usr/bin/env python3
import argparse
import json
import os
from typing import List

from mis.strategies.combinations import bfs_order, dfs_order, all_subsets


def export_combos(instances: List[str], strategy: str, max_comb_size: int, out_dir: str | None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instances_parent = os.path.join(base_dir, 'TestInstances')
    out_root = out_dir or os.path.join(base_dir, 'exports')
    os.makedirs(out_root, exist_ok=True)

    def gen(keys: List[str]):
        if strategy == 'bfs':
            return bfs_order(keys)
        if strategy == 'dfs':
            return dfs_order(keys)
        return all_subsets(keys)

    for name in instances:
        inst_dir = os.path.join(instances_parent, name)
        if not os.path.isdir(inst_dir):
            print(f"Skip {name}: not a directory under TestInstances")
            continue
        out_sub = os.path.join(out_root, name)
        os.makedirs(out_sub, exist_ok=True)

        for file in os.listdir(inst_dir):
            if not file.endswith('.json'):
                continue
            json_path = os.path.join(inst_dir, file)
            with open(json_path, 'r') as f:
                original = json.load(f)

            # expand parts by num_part into keys pid-k
            expanded = []
            for part in original.get('parts', []):
                pid = part.get('part_id')
                count = int(part.get('num_part', 1))
                for k in range(1, count + 1):
                    expanded.append({'key': f"{pid}-{k}", 'part': part})

            keys = [e['key'] for e in expanded]
            combos_written = 0
            for combo in gen(keys):
                if max_comb_size is not None and len(combo) > max_comb_size:
                    continue

                selected = []
                for key in combo:
                    e = next(x for x in expanded if x['key'] == key)
                    p = e['part']
                    selected.append({
                        'part_id': 0,
                        'num_part': 1,
                        'num_orientation': p.get('num_orientation', 1),
                        'volume': p.get('volume', 0.0),
                        'orientations': p.get('orientations', [])
                    })
                for idx, p in enumerate(selected, start=1):
                    p['part_id'] = idx

                out_json = {
                    'machines': original.get('machines', []),
                    'parts': selected,
                    'types_machine': len(original.get('machines', [])),
                    'types_parts': len(selected),
                    'num_machine': sum(m.get('num_machine', 1) for m in original.get('machines', [])),
                    'num_parts': len(selected)
                }

                base = os.path.splitext(file)[0]
                out_name = f"{base}_{strategy}_{len(combo)}_{combos_written+1}.json"
                out_path = os.path.join(out_sub, out_name)
                with open(out_path, 'w') as out_f:
                    json.dump(out_json, out_f, ensure_ascii=False, indent=2)
                combos_written += 1

            print(f"Exported {combos_written} combos for {file} into {out_sub}")


def main():
    parser = argparse.ArgumentParser(description='Export JSON instances matching TestInstances schema with combos')
    parser.add_argument('--strategy', choices=['bfs', 'dfs', 'all'], default='bfs')
    parser.add_argument('--instances', nargs='+', required=True)
    parser.add_argument('--max-comb-size', type=int, default=5)
    parser.add_argument('--out-dir', default=None)
    args = parser.parse_args()

    export_combos(args.instances, args.strategy, args.max_comb_size, args.out_dir)


if __name__ == '__main__':
    main()


