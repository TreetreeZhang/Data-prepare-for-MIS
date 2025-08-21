## Data-prepare-for-MIS 使用说明

本工程用于二维装箱/排样（矩形在托盘上布局）的数据准备与可行性检验，支撑 MIS（Minimum Infeasible Subset）相关研究。

### 1. 环境依赖
- Python 3.8+
- 主要第三方库：
  - ortools
  - matplotlib
  - pandas（仅 CSV→JSON 转换需要）
  - numpy（仅 CSV→JSON 转换需要）
  - tqdm（仅 CSV→JSON 转换需要）

安装示例：
```bash
pip install ortools matplotlib pandas numpy tqdm
```

### 2. 目录结构（关键）
- `mis/`（核心库）
  - `solvers/`: `grid.py`、`interval.py`、`disjunctive.py`（三种求解方法）
  - `strategies/`: 组合生成与剪枝（`combinations.py`、`pruning.py`）
  - `io/`: 实例读取与输出（`reader.py` 等）
  - `utils/`: 通用工具（`geometry.py`、`scaling.py`）
  - `runner.py`: 并行执行、剪枝、结果写盘
- `utils/`（实用脚本）
  - 数据转换：`csv_to_json.py`、`data_transfer.py`
  - 求解入口脚本：`solve/BFS.py`、`solve/DFS.py`、`solve/Repetition.py`
  - 其它：`tools.py`（JSON 读写、分辨率计算）、`Logcount.py`
- `task/`：离线批量任务/实例生成工具（见 `task/README.md`）
- `TestInstances/`：测试实例数据（`n15`、`n20` 等）

### 3. 数据格式（JSON）
标准 JSON 结构包含：
- `machines`: [{`machine_id`,`num_machine`,`V`,`U`,`S`,`L`,`W`,`H`}, ...]
- `parts`: [{`part_id`,`num_part`,`num_orientation`,`volume`,`orientations`:[{`l`,`w`,`h`,`support`}]}]

求解前会被解析为：
- `machines_info`: [(machine_id, L, W), ...]
- `bins_info`: {唯一零件编号: (l, w), ...}

### 4. 数据转换
1) TXT → JSON：
- 文本行格式按 `utils/tools.py::convert_txt_to_json` 约定
- 批量转换入口：`utils/data_transfer.py::convert_txt_json(input_folder, output_folder)`

示例（请先按需修改路径）：
```python
from utils.data_transfer import convert_txt_json
convert_txt_json(
    "/Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/txt",
    "/Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/json"
)
```

2) CSV → JSON：
- 使用 `utils/csv_to_json.py`：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/utils/csv_to_json.py
```
（脚本内含基础目录示例，按需替换 `input_base_dir/output_base_dir`）

### 5. 顶层主入口（推荐）
自顶层运行 `main.py`，实现“数据准备（TXT/CSV→JSON）”与“求解（并行+剪枝，BFS/DFS+三求解器）”分离。

#### 5.1 数据准备
- TXT → JSON：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/main.py prepare --from txt \
  --in /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/txt \
  --out /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/json
```

- CSV → JSON：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/main.py prepare --from csv \
  --in /path/to/SingleAM_data \
  --out /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/json/SingleAM_data \
  --n-values 15 20 30 40
```

不提供 `--n-values` 时，脚本会尝试自动遍历顶层 CSV 文件，并探测 `n=15` 这类子目录批量转换。

#### 5.2 求解运行（并行 + 剪枝）
三种求解器均可选择：
- `--solver grid`：原离散网格模型
- `--solver interval`：区间 + NoOverlap2D + 旋转
- `--solver disjunctive`：显式左/右/上/下析取不重叠模型

策略可选：`--strategy bfs|dfs|all`。

示例：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/main.py solve \
  --strategy bfs \
  --solver interval \
  --instances n15 \
  --processes 8 \
  --timeout 300
```

或指定目录：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/main.py solve \
  --strategy dfs \
  --solver disjunctive \
  --instances-dir /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/n15
```

### 6. 结果输出
输出位于与 `main.py` 同级的 `output/` 目录下：
- 组织形式：`output/{code_name}{run_id}/{instance_basename}/{machine_id}/`
  - `previous_log.json`：已成功组合的复用缓存
  - `{L}x{W}-{grid}.json`：该分辨率的求解记录（含时间、是否可行、解）
  - `{L}x{W}-{grid}-pruned.json`：剪枝日志

注意：输出 JSON 结构未被修改。

### 7. 建议与注意
- `grid` 解法依赖 `grid_size` 与边长的整除关系；`interval` 解法对小数尺寸自动缩放并允许旋转，常用于连续坐标布局。
- 大实例耗时可观，建议先在 `n15` 小规模数据上验证。
- 并行度可通过 `--processes` 参数控制。

