#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 15:04:24 2024

@author: chunlongyu
"""
import math

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model


class Dot:
    def __init__(self, ID, x, y):
        self.ID = ID
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Dot(ID={self.ID}, x={self.x}, y={self.y})"


# def discretize_platform(L, W, grid_size):
#     dots = []
#     ID = 0
#     for x in range(0, L+1, grid_size):
#         for y in range(0, W+1, grid_size):
#             dots.append(Dot(ID, x, y))
#             ID += 1
#     return dots

# 修改后增添了浮点数支持
def discretize_platform(L, W, grid_size):
    dots = []
    ID = 0
    x = 0.0
    while x <= L:
        y = 0.0
        while y <= W:
            dots.append(Dot(ID, x, y))
            ID += 1
            y = round(y + grid_size, 10)  # 使用round确保浮点运算精度
        x = round(x + grid_size, 10)
    return dots


def discretize_bin(l, w, grid_size):
    # Calculate the number of grids needed along the length and width
    num_grids_length = math.ceil(l / grid_size)
    num_grids_width = math.ceil(w / grid_size)

    # Calculate the actual discretized length and width
    new_length = num_grids_length * grid_size
    new_width = num_grids_width * grid_size

    return new_length, new_width, num_grids_length, num_grids_width


def get_inner_fit_polygon(dots, l, w, L, W):
    """Get the set of dots representing the inner fit polygon where the bin can be placed."""
    # Discretize the platform
    # dots = discretize_platform(L, W, grid_size)

    # Filter the dots to ensure the bin fits within the platform when placed at the dot
    inner_fit_polygon = []
    for dot in dots:
        if dot.x + l <= L and dot.y + w <= W:
            inner_fit_polygon.append(dot)

    return inner_fit_polygon


def is_overlap(l_i, w_i, dot_i, l_j, w_j, dot_j):
    """Check if bin j placed at dot_j would overlap with bin i placed at dot_i."""
    # Check if the two bins overlap
    return not (
            (dot_j.x >= dot_i.x + l_i or dot_j.x + l_j <= dot_i.x) or (
                dot_j.y >= dot_i.y + w_i or dot_j.y + w_j <= dot_i.y)
    )


def get_no_fit_polygon(dots, l_i, w_i, d_i, l_j, w_j):
    """Get the set of dots representing the no-fit polygon for bin j after placing bin i at dot d_i."""
    # Discretize the platform
    # dots = discretize_platform(L, W, grid_size)

    # Find the dots where placing bin j would overlap with bin i placed at dot d
    no_fit_polygon = []
    for dot in dots:
        if is_overlap(l_i, w_i, d_i, l_j, w_j, dot):
            no_fit_polygon.append(dot.ID)

    return no_fit_polygon


def get_Phi_jd(dots, bins, j, d):
    """
    Calculate the set Phi_jd, which is the set of dots where no other bins can be placed 
    after bin j has been placed at dot d.
    
    bins: List of bins where each bin is represented as a tuple (l_i, w_i) for bin i.
    j: Index of the bin j being placed at dot d.
    d: The dot where bin j is placed.
    """
    # Initialize Phi_jd as a set of all dot IDs (starting with all dots, which we'll refine by intersection)
    Phi_jd = {dot.ID for dot in dots}

    # Get the dimensions of bin j
    l_j, w_j = bins[j]

    # Iterate over all bins except j to compute no-fit polygons
    for i, (l_i, w_i) in enumerate(bins):
        if i != j:
            # Compute no-fit polygon for bin i after placing bin j at dot d
            no_fit_polygon = get_no_fit_polygon(dots, l_j, w_j, d, l_i, w_i)
            # Intersection: keep only the dots that are in both the current Phi_jd and the new no-fit polygon
            Phi_jd.intersection_update(no_fit_polygon)

    return Phi_jd


def get_Gamma_d(d, inner_fit_polygons):
    """
    Calculate the set Gamma_d, which is the set of bin IDs whose positioning point 
    can be assigned to dot d while keeping the bin inside the platform.
    
    d: The dot under consideration (a Dot object).
    inner_fit_polygons: A dictionary where the key is the bin ID, and the value is 
                        a list of dots representing the inner-fit polygon for that bin.
    """
    Gamma_d = set()

    # Iterate over the inner-fit polygons for each bin
    for bin_id, polygon in inner_fit_polygons.items():
        # If dot d is part of the inner-fit polygon of this bin, add the bin ID to Gamma_d
        polygon_ID = [p.ID for p in polygon]
        if d.ID in polygon_ID:
            Gamma_d.add(bin_id)

    return Gamma_d


def visualize_bin_packing(dots, bins, gamma, L, W, solver, save_bool=False):
    '''
    :param dots:
    :param bins:
    :param gamma:
    :param L:
    :param W:
    :param solver:
    :return:
    '''
    fig, ax = plt.subplots(1, figsize=(10, 6))

    # Define a color map for bins
    colors = plt.get_cmap('tab20', len(bins))  # 'tab10' is a color map with 10 distinct colors

    # Draw platform boundaries
    ax.set_xlim(0, L)
    ax.set_ylim(0, W)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Bin-Packing Visualization")

    # Set equal scaling for both axes
    ax.set_aspect('equal', 'box')

    # Add platform boundary rectangle
    platform = patches.Rectangle((0, 0), L, W, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(platform)

    # # Plot each dot on the platform
    for dot in dots:
        ax.plot(dot.x, dot.y, 'ro', markersize=2)  # 'ro' stands for red dots
        # ax.text(dot.x + 0.1, dot.y + 0.1, f"ID:{dot.ID}", fontsize=8)

    # Visualize the bins based on the solution gamma
    for dot in dots:
        dot_id = dot.ID
        status = -1  # Default to -1, meaning no bin is assigned

        # Check all possible statuses (-1, 0, 1, 2, etc.) to find the one assigned to the dot
        for s in range(-1, len(bins)):  # Status ranges from -1 to the number of bins
            if solver.value(gamma[dot_id, s]) == 1:  # If gamma[d, s] is 1, dot d is assigned to status s
                status = s
                break

        if status >= 0:  # Bin is placed at the dot
            bin_width, bin_height = bins[status]
            bottom_left_x = dot.x
            bottom_left_y = dot.y
            # Add bin rectangle with different colors
            bin_rect = patches.Rectangle((bottom_left_x, bottom_left_y), bin_width, bin_height,
                                         linewidth=1, edgecolor='black', facecolor=colors(status), alpha=0.5)
            ax.add_patch(bin_rect)
            ax.text(bottom_left_x + 0.1, bottom_left_y + bin_height / 2, f"Bin {status}", fontsize=8, color='black')

    plt.grid(True)
    # plt.show()
    if save_bool:
        plt.draw()  # 确保图形已渲染
        # plt.savefig("bin_packing_visualization.png")
        plt.close(fig)
        return fig


def check_is_times(L, W, grid_size):
    errors = []
    if L % grid_size != 0:
        errors.append(f"Error: L ({L}) is not an integer multiple of grid_size ({grid_size}).")
    if W % grid_size != 0:
        errors.append(f"Error: W ({W}) is not an integer multiple of grid_size ({grid_size}).")
    if errors:
        raise ValueError("\n".join(errors))


def check_feasi(L, W, grid_size, bins):
    '''
    :param L：托盘的长度 浮点数
    :param W: 托盘的宽度 浮点数
    :param grid_size: 网格的尺寸 浮点数
    :param bins: 物体的尺寸 列表
    :return:IsFeasible：是否可行, PackingSol：物体的放置方式
    '''
    check_is_times(L, W, grid_size)
    # Define set of Jobs
    J = [j for j in range(len(bins))]

    # Create the CP-SAT model
    model = cp_model.CpModel()

    # Discretize the platform
    dots = discretize_platform(L, W, grid_size)

    # Calculate the inner fit polygons for each bin
    inner_fit_polygons = {}
    # bin_info = {}
    for bin_id, (l, w) in enumerate(bins):
        # bin_info[bin_id] = (l, w)
        inner_fit_polygons[bin_id] = get_inner_fit_polygon(dots, l, w, L, W)

    # Obtain the list of Gamma_d 
    Gamma = {}  # List of Gaama_d
    status_list = [-1] + J
    for d in dots:
        Gamma_d = get_Gamma_d(d, inner_fit_polygons)
        dot_id = d.ID
        Gamma[dot_id] = Gamma_d

    # Create decision variables for each dot
    gamma = {}  # Decision variable
    for d in dots:
        for s in status_list:
            # gamma[dot_id] = model.NewIntVar(-1, len(J)-1, f'gamma_{dot_id}')
            gamma[d.ID, s] = model.NewBoolVar(f"gamma_d{dot_id}_s{s}")

    # Add constraints to ensure that each bin can only be assigned to one dot
    for j in J:
        model.add_exactly_one(gamma[d.ID, j] for d in dots)

    # Add constraints to ensure that each dot can only be assigned with one bin from the Gamma_d set, or left empty
    for d in dots:
        valid_values = list(Gamma[d.ID]) + [-1]
        model.add(sum([gamma[d.ID, j] for j in J + [-1]]) == 1)
        model.add(sum([gamma[d.ID, j] for j in valid_values]) == 1)

    # Obtain the Phi dictionary
    Phi = {}
    for d in dots:
        for j in J:
            Phi_jd = get_Phi_jd(dots, bins, j, d)
            Phi[j, d.ID] = list(Phi_jd)

    # Add constraints to ensure that if bin j is placed at d, then:
    # all dots within Phi_jd should take the values of -1

    for d in dots:
        for j in J:
            for dd in dots:
                if d.ID != dd.ID and dd.ID in Phi[j, d.ID]:
                    model.AddImplication(gamma[d.ID, j], gamma[dd.ID, -1])

    # Obtain the no-fit polygons
    NFPs = {}

    for d in dots:
        for j in Gamma[d.ID]:
            for jj in J:
                if jj != j:
                    l_j = bins[j][0]
                    w_j = bins[j][1]
                    l_jj = bins[jj][0]
                    w_jj = bins[jj][1]
                    NFPs[j, d.ID, jj] = get_no_fit_polygon(dots, l_j, w_j, d, l_jj, w_jj)

    # Add constraints to ensure that if bin j is placed at d, then:
    # for any bin jj, it cannot be placed at dot dd if dd is included in the no-fit polygon set of NFP^d_j,jj
    for [j, d, jj], nfp in NFPs.items():
        for dd in nfp:
            model.AddImplication(gamma[d, j], gamma[dd, jj].Not())

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    PackingSol = {}  # Dictionary of part coordinates
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for d in dots:
            for s in status_list:
                if solver.value(gamma[d.ID, s]) == 1:
                    if s >= 0:
                        PackingSol[s] = [d.x, d.y]
                        # print("Dot", d.ID, "x", d.x, "y", d.y, "is placed with bin ", s, ".")

    IsFeasible = False
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        IsFeasible = True
        # visualize_bin_packing(dots, bins, gamma, L, W, solver)
        # num_bins = len(bins)

        # if save_path!=None:
        # 图片保存
        # fig = visualize_bin_packing(dots, bins, gamma, L, W, solver, save_bool=True)
        # # plt.show()
        # image_folder_name = f"{L}*{W}-{grid_size}-{num_bins}"
        # image_path = os.path.join(save_path, image_folder_name)
        # os.makedirs(image_path, exist_ok=True)
        # # 获取当前文件夹中已有的图片数量
        # existing_files = os.listdir(image_path)
        # existing_images = [f for f in existing_files if f.endswith('.png')]
        # count = len(existing_images) + 1  # 从已有文件数量 + 1 开始编号
        # # 保存图片，并命名为 1.png, 2.png, ...
        # fig.savefig(os.path.join(image_path,f"{count}.png"))

        # with open(str(os.path.join(save_path,f"{L}*{W}-{grid_size}.txt")),'a') as f:
        #
        #     f.write(f"IsFeasible: {IsFeasible},\t")
        #     f.write(f"PackingSol: {PackingSol},\t")
        #     f.write('\n')

    return IsFeasible, PackingSol


if __name__ == '__main__':
    # ============
    # Define the platform dimensions and grid size
    L = 5
    W = 6
    grid_size = 1.5  # the size of the grid

    # Define bins as tuples of (length, width)
    bins = [
        (4, 3),  # Bin 0
        (2, 2),  # Bin 1
        (3, 2),  # Bin 2
    ]

    IsFeasible, Solution = check_feasi(L, W, grid_size, bins, save_path='../')

    print(IsFeasible)
    print(Solution)
