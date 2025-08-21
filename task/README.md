## Task utilities

本目录提供两类“离线批量生成”工具，便于在另一台机器进行大规模求解：

- prepare_tasks.py：生成“待求解组合清单”（JSON 数组，每项一条任务）
- export_combos.py：导出“与 TestInstances 相同 schema 的组合实例 JSON”（每个组合一个实例文件）

两者都只依赖项目已有模块（不需要 pandas/tqdm），适合在求解端机器上直接使用。

### 1) 生成待求解组合清单（prepare_tasks.py）

用途：根据现有实例，枚举零件组合（BFS/DFS/ALL），输出为单个 JSON 文件（数组）。

命令示例：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/task/prepare_tasks.py \
  --strategy bfs \
  --instances n15 \
  --max-comb-size 8
```

参数：
- `--strategy {bfs,dfs,all}`：组合生成策略
- `--instances <names...>`：实例子目录（位于 `TestInstances/` 下，如 `n15 n20`）
- `--max-comb-size N`：可选，限制组合最大尺寸，避免组合爆炸

输出：写入项目根目录下 `tasks/` 目录，文件名格式：`<实例名>_<策略>.json`

JSON 结构（数组，示例前两项）：
```json
[
  {
    "instance": "15parts_1.json",
    "machine_id": 1,
    "L": 10.0,
    "W": 10.0,
    "combination": ["1-1", "2-1"]
  },
  {
    "instance": "15parts_1.json",
    "machine_id": 1,
    "L": 10.0,
    "W": 10.0,
    "combination": ["1-1", "3-1"]
  }
]
```

说明：`combination` 中的键格式为 `part_id-副本序号`，基于原始 JSON 的 `num_part` 展开。

### 2) 导出与 TestInstances 相同 schema 的组合实例（export_combos.py）

用途：按给定策略枚举组合，并将每个组合导出成一个“独立实例 JSON”，其顶层结构与 `TestInstances/*.json` 完全一致，可直接被现有求解流程消费。

命令示例：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/task/export_combos.py \
  --strategy bfs \
  --instances n15 \
  --max-comb-size 4 \
  --out-dir /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/exports
```

参数：
- `--strategy {bfs,dfs,all}`：组合生成策略
- `--instances <names...>`：实例子目录（如 `n15 n20`）
- `--max-comb-size N`：限制组合大小
- `--out-dir PATH`：导出根目录（默认 `exports/`）

输出：`exports/<实例子目录>/<原文件名>_<策略>_<组合大小>_<序号>.json`

导出实例的顶层结构（与 TestInstances 相同）：
```json
{
  "machines": [ { "machine_id": 1, "num_machine": 1, "V": 0.03, "U": 0.7, "S": 2.0, "L": 10.0, "W": 10.0, "H": 32.5 } ],
  "parts": [
    { "part_id": 1, "num_part": 1, "num_orientation": 1, "volume": 90.0, "orientations": [ {"l":3.3,"w":6.0,"h":32.0,"support":0.0} ] },
    { "part_id": 2, "num_part": 1, "num_orientation": 1, "volume": 150.0, "orientations": [ {"l":10.0,"w":6.0,"h":8.0,"support":0.0} ] }
  ],
  "types_machine": 1,
  "types_parts": 2,
  "num_machine": 1,
  "num_parts": 2
}
```

说明：
- `parts` 中的 `part_id` 将按 1..m 重新编号，`num_part` 固定为 1（每个组合仅保留一个副本）。
- `machines` 将继承原始实例内容；顶层统计字段会同步更新。

### 建议与注意
- 组合数量可能呈指数增长。建议合理设置 `--max-comb-size`，并按实例规模分批导出。
- 生成的任务 JSON（prepare_tasks.py）适合分发给自定义调度/求解器；导出实例 JSON（export_combos.py）可直接用于现有求解入口（例如 `main.py solve`）。
- 如需自定义过滤（按面积、长宽阈值等），可在脚本中插入预筛选逻辑。


