#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 17:43:21 2025

@author: chunlongyu
"""

from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
#from BinPacking1 import BinPackingFeasCheck1
import random
import time
import numpy as np

def solve_feasibility_disjunctive(L, W, bins):
    """
    Disjunctive non-overlap model with explicit x/y integer coordinates and rotation booleans.
    Returns: (is_feasible: int in {1,0,-1}, solution: List[dict], elapsed_time: float)
    """
    start_time = time.time()
    # ========== 模型建立 ==========
    model = cp_model.CpModel()
    n = len(bins)
    
    x = []  # x坐标变量
    y = []  # y坐标变量
    r = []  # 旋转变量 (0: 不旋转, 1: 旋转)
    
    for j in range(n):
        x_j = model.NewIntVar(0, L, f'x_{j}')
        y_j = model.NewIntVar(0, W, f'y_{j}')
        r_j = model.NewBoolVar(f'r_{j}')  # 是否旋转
        x.append(x_j)
        y.append(y_j)
        r.append(r_j)
    
    # 容器内约束
    for j in range(n):
        w_j, h_j = bins[j]
        w_eff = model.NewIntVar(0, L, f'w_eff_{j}')
        h_eff = model.NewIntVar(0, W, f'h_eff_{j}')
        
        model.Add(w_eff == w_j).OnlyEnforceIf(r[j].Not())
        model.Add(h_eff == h_j).OnlyEnforceIf(r[j].Not())
        model.Add(w_eff == h_j).OnlyEnforceIf(r[j])
        model.Add(h_eff == w_j).OnlyEnforceIf(r[j])
        
        model.Add(x[j] + w_eff <= L)
        model.Add(y[j] + h_eff <= W)
    
    # 不重叠约束
    for i in range(n):
        for j in range(i+1, n):
            wi, hi = bins[i]
            wj, hj = bins[j]
    
            wi_eff = model.NewIntVar(0, L, f'wi_eff_{i}')
            hi_eff = model.NewIntVar(0, W, f'hi_eff_{i}')
            wj_eff = model.NewIntVar(0, L, f'wj_eff_{j}')
            hj_eff = model.NewIntVar(0, W, f'hj_eff_{j}')
    
            model.Add(wi_eff == wi).OnlyEnforceIf(r[i].Not())
            model.Add(hi_eff == hi).OnlyEnforceIf(r[i].Not())
            model.Add(wi_eff == hi).OnlyEnforceIf(r[i])
            model.Add(hi_eff == wi).OnlyEnforceIf(r[i])
    
            model.Add(wj_eff == wj).OnlyEnforceIf(r[j].Not())
            model.Add(hj_eff == hj).OnlyEnforceIf(r[j].Not())
            model.Add(wj_eff == hj).OnlyEnforceIf(r[j])
            model.Add(hj_eff == wj).OnlyEnforceIf(r[j])
    
            no_overlap = [
                model.NewBoolVar(f'left_{i}_{j}'),
                model.NewBoolVar(f'right_{i}_{j}'),
                model.NewBoolVar(f'above_{i}_{j}'),
                model.NewBoolVar(f'below_{i}_{j}')
            ]
    
            model.Add(x[i] + wi_eff <= x[j]).OnlyEnforceIf(no_overlap[0])
            model.Add(x[j] + wj_eff <= x[i]).OnlyEnforceIf(no_overlap[1])
            model.Add(y[i] + hi_eff <= y[j]).OnlyEnforceIf(no_overlap[2])
            model.Add(y[j] + hj_eff <= y[i]).OnlyEnforceIf(no_overlap[3])
    
            model.AddBoolOr(no_overlap)
    
    # ========== 求解 ==========
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300  # 设置10分钟时间上限
    status = solver.Solve(model)
    
    elapsed_time = time.time() - start_time
    
    # 判定可行性状态
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        is_feasible = 1
    elif status == cp_model.INFEASIBLE:
        is_feasible = 0
    else:  # UNKNOWN, MODEL_INVALID 等
        is_feasible = -1
    
    solution = []
     
    if is_feasible:
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = plt.colormaps['tab10']
        #colors = plt.colormaps('tab10')
        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_aspect('equal')
        ax.set_title("Bin packing solution")
        ax.grid(False)
     
        for j in range(n):
            xj = solver.Value(x[j])
            yj = solver.Value(y[j])
            rot = solver.Value(r[j])
            wj, hj = bins[j]
            if rot == 1:
                wj, hj = hj, wj
        
            solution.append({"id": j, "x": xj, "y": yj, "w": wj, "h": hj, "rotated": bool(rot)})
        
            rect = patches.Rectangle((xj, yj), wj, hj, linewidth=1, edgecolor='black', facecolor=colors(j), alpha=0.5)
            ax.add_patch(rect)
            ax.text(xj + 0.1, yj + hj / 2, f"{j} {'R' if rot else ''}", fontsize=10, color='black')
        
        plt.show(block=False)
        plt.pause(1)
        #plt.close()
     
  
     
    return is_feasible, solution, elapsed_time
    
    
# Use interval and NoOverlap2D
def solve_feasibility_interval(L, W, bins):
    """
    Interval-based model using AddNoOverlap2D with rotation booleans.
    Returns: (is_feasible: int in {1,0,-1}, solution: List[dict], elapsed_time: float)
    """
    start_time = time.time()
    model = cp_model.CpModel()
    n = len(bins)

    x_starts, y_starts, x_ends, y_ends = [], [], [], []
    x_intervals, y_intervals = [], []
    rot_vars = []
    w_eff_vars, h_eff_vars = [], []

    for i, (w, h) in enumerate(bins):
        r = model.NewBoolVar(f"r_{i}")
        rot_vars.append(r)

        w_eff = model.NewIntVar(min(w, h), max(w, h), f"w_eff_{i}")
        h_eff = model.NewIntVar(min(w, h), max(w, h), f"h_eff_{i}")
        w_eff_vars.append(w_eff)
        h_eff_vars.append(h_eff)

        model.Add(w_eff == w).OnlyEnforceIf(r.Not())
        model.Add(h_eff == h).OnlyEnforceIf(r.Not())
        model.Add(w_eff == h).OnlyEnforceIf(r)
        model.Add(h_eff == w).OnlyEnforceIf(r)

        x_start = model.NewIntVar(0, L, f"x_start_{i}")
        y_start = model.NewIntVar(0, W, f"y_start_{i}")
        x_end = model.NewIntVar(0, L, f"x_end_{i}")
        y_end = model.NewIntVar(0, W, f"y_end_{i}")

        model.Add(x_end == x_start + w_eff)
        model.Add(y_end == y_start + h_eff)

        model.Add(x_end <= L)
        model.Add(y_end <= W)

        x_starts.append(x_start)
        y_starts.append(y_start)
        x_ends.append(x_end)
        y_ends.append(y_end)

        x_iv = model.NewIntervalVar(x_start, w_eff, x_end, f"x_iv_{i}")
        y_iv = model.NewIntervalVar(y_start, h_eff, y_end, f"y_iv_{i}")
        x_intervals.append(x_iv)
        y_intervals.append(y_iv)

    model.AddNoOverlap2D(x_intervals, y_intervals)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300
    status = solver.Solve(model)
    elapsed_time = time.time() - start_time

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        is_feasible = 1
    elif status == cp_model.INFEASIBLE:
        is_feasible = 0
    else:
        is_feasible = -1

    solution = []

    if is_feasible == 1:
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = plt.colormaps.get_cmap('tab10')
        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_aspect('equal')
        ax.set_title("2D Bin Packing Feasibility (Rotation Allowed)")
        ax.grid(True)

        for i in range(n):
            xj = solver.Value(x_starts[i])
            yj = solver.Value(y_starts[i])
            rot = solver.Value(rot_vars[i])
            wj = solver.Value(w_eff_vars[i])
            hj = solver.Value(h_eff_vars[i])

            solution.append({"id": i, "x": xj, "y": yj, "w": wj, "h": hj, "rotated": bool(rot)})

            rect = patches.Rectangle((xj, yj), wj, hj, linewidth=1, edgecolor='black', facecolor=colors(i % 10), alpha=0.5)
            ax.add_patch(rect)
            ax.text(xj + 0.1, yj + hj / 2, f"{i} {'R' if rot else ''}", fontsize=10, color='black')

        plt.show(block=False)
        plt.pause(1)
        plt.close()

    return is_feasible, solution, elapsed_time

# ================== 自动压力测试 ==================
def generate_random_bins(n, min_size, max_size, total_area_limit=None):
    bins = []
    total_area = 0
    for _ in range(n):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        if total_area_limit and total_area + w * h > total_area_limit:
            break
        bins.append((w, h))
        total_area += w * h
    return bins

# if __name__ == "__main__":
#     random.seed(42)  # 设置随机种子
    
#     test_cases = [
#         (25, 25, generate_random_bins(10, 3, 7)),       # 普通可行
#         (25, 25, generate_random_bins(12, 5, 9)),       # 紧凑可行
#         (25, 25, generate_random_bins(15, 6, 10)),      # 边界可行/不可行
#         (25, 25, generate_random_bins(20, 6, 12, 625)), # 面积接近平台极限
#         (25, 25, generate_random_bins(8, 12, 20)),       # 大尺寸物品挑战
#         (25, 25, generate_random_bins(15, 3, 7)),       # 大尺寸物品挑战
#         (20, 20, generate_random_bins(13, 2, 10)),       # 大尺寸物品挑战
#         #(40, 40, generate_random_bins(30, 6, 12))       # 大尺寸物品挑战
#     ]

#     for idx, (L, W, bins) in enumerate(test_cases):
#         print("\n======================")
#         print(f"测试案例 {idx+1}: 平台({L}x{W}), {len(bins)}个物品")
#         print("物品尺寸:", bins)
#         feasible, solution, runtime = BinPackingFeasCheck3(L, W, bins)
        
#         status_map = {1: "可行", 0: "不可行（已证）", -1: "未知（如超时）"}
#         print(f"可行性状态: {status_map[feasible]}")

#         print(f"运行时间: {runtime:.2f} 秒")
#         if feasible:
#             for item in solution:
#                 print(item)
#         else:
#             print("无可行装箱方案")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    random.seed(42)

    test_cases = [
        (25, 25, generate_random_bins(10, 3, 7)),       # 普通可行
        (25, 25, generate_random_bins(12, 5, 9)),       # 紧凑可行
        (25, 25, generate_random_bins(15, 6, 10)),      # 边界可行/不可行
        (25, 25, generate_random_bins(20, 6, 12, 625)), # 面积接近平台极限
        (25, 25, generate_random_bins(8, 12, 20)),       # 大尺寸物品挑战
        (25, 25, generate_random_bins(15, 3, 7)),       # 大尺寸物品挑战
        (20, 20, generate_random_bins(13, 2, 10)),       # 大尺寸物品挑战
        #(40, 40, generate_random_bins(30, 6, 12))       # 大尺寸物品挑战
    ]

    runtimes2 = []
    runtimes3 = []

    for idx, (L, W, bins) in enumerate(test_cases):
        print(f"\n=== 测试案例 {idx+1} ===")
        print(f"平台: {L}x{W}, 物品数: {len(bins)}")

        _, _, time2 = solve_feasibility_disjunctive(L, W, bins)
        _, _, time3 = solve_feasibility_interval(L, W, bins)

        print(f"模型2运行时间: {time2:.2f}s")
        print(f"模型3运行时间: {time3:.2f}s")

        runtimes2.append(time2)
        runtimes3.append(time3)

    # 绘图
    labels = [f"Case {i+1}" for i in range(len(test_cases))]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, runtimes2, width, label='Model 2')
    rects2 = ax.bar(x + width/2, runtimes3, width, label='Model 3')

    ax.set_ylabel('运行时间 (秒)')
    ax.set_title('两种模型运行时间对比')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.tight_layout()
    plt.show()
