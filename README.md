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
- `utils/`：工具与求解脚本
  - `FeasibilityCheck.py`：
    - `check_feasi(L, W, grid_size, bins)`：原始“离散网格”可行性检查器
    - `check_feasi_interval(L, W, grid_size, bins)`：新增“区间 + NoOverlap2D + 旋转”检查器（自动小数精度整型缩放）
  - `BFS.py`、`DFS.py`、`Repetition.py`：对子集进行可行性枚举、剪枝与记录（支持命令行选择求解器）
  - `tools.py`：JSON 读写、分辨率计算、并行执行
  - `CSV2json.py`、`DataformTransfer.py`：数据格式转换工具
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
- 批量转换入口：`utils/DataformTransfer.py::convert_txt_json(input_folder, output_folder)`

示例（请先按需修改路径）：
```python
from utils.DataformTransfer import convert_txt_json
convert_txt_json(
    "/Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/txt",
    "/Users/tree/project-dom/git-tree/Data-prepare-for-MIS/TestInstances/json"
)
```

2) CSV → JSON：
- 使用 `utils/CSV2json.py`：
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/utils/CSV2json.py
```
（脚本内含基础目录示例，按需替换 `input_base_dir/output_base_dir`）

### 5. 求解运行
三种驱动脚本均支持命令行选择求解器：
- `--solver grid`：原离散网格模型（`check_feasi`）
- `--solver interval`：区间 + NoOverlap2D + 旋转（`check_feasi_interval`）
- `--solver disjunctive`：显式左/右/上/下析取不重叠模型（`check_feasi_disjunctive`）

并行执行默认使用 CPU 进程池（在 `utils/tools.py::Check_grid_Feasibility_parallel`）。

#### 5.1 BFS
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/utils/BFS.py \
  --solver interval \
  --instances n15
```

#### 5.2 DFS
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/utils/DFS.py \
  --solver interval \
  --instances n15
```

#### 5.3 Repetition（多数据集批量）
```bash
python /Users/tree/project-dom/git-tree/Data-prepare-for-MIS/utils/Repetition.py \
  --solver interval \
  --instances 10 15 n20
```

`--instances` 参数为 `TestInstances/` 下的子目录名。

### 6. 结果输出
输出位于相对路径 `../output/` 下（以脚本运行目录为基准）：
- 组织形式：`../output/{code_name}{run_id}/{instance_basename}/{machine_id}/`
  - `previous_log.json`：已成功组合的复用缓存
  - `{L}x{W}-{grid}.json`：该分辨率的求解记录（含时间、是否可行、解）
  - `{L}x{W}-{grid}-pruned.json`：剪枝日志

注意：为保持兼容性，输出 JSON 结构未被修改。

### 7. 建议与注意
- `grid` 解法依赖 `grid_size` 与边长的整除关系；`interval` 解法对小数尺寸自动缩放并允许旋转，常用于连续坐标布局。
- 大实例耗时可观，建议先在 `n15` 小规模数据上验证。
- 若需要限制并行度，可在 `tools.py::Check_grid_Feasibility_parallel` 中自定义 `Pool(processes=...)`。

### 8. 致谢
`utils/FeasibilityCheckMain_R.py` 中的思路已被抽象为 `check_feasi_interval` 并集成到当前框架，使用时仅需通过 `--solver interval` 选择新模型。

