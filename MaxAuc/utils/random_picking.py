import random
import math

import matplotlib.pyplot as plt

# 绘制地图和点
def plot_map(n, points):
    plt.figure(figsize=(8, 8))
    plt.xlim(-1, n)
    plt.ylim(-1, n)
    plt.grid(True)
    for x, y in points:
        plt.scatter(x, y, c='red')
    plt.title("Randomly Selected Points")
    plt.show()


def select_points(n, x):
    """
    从 n x n 的地图中随机挑选 x 个不重复的点，尽量均匀分布。
    
    参数:
        n: 地图大小 (n x n)
        x: 随机点的数量
    返回:
        坐标列表 [(x1, y1), (x2, y2), ...]
    """
    if x > n * n:
        raise ValueError("点的数量 x 不能超过地图的总格子数 n x n")
    
    # 计算网格划分
    grid_size = math.sqrt(x)  # 尝试划分为 grid_size x grid_size 的网格
    grid_rows = math.ceil(grid_size)  # 行数
    grid_cols = math.ceil(grid_size)  # 列数

    # 每个网格的大小
    grid_height = n / grid_rows
    grid_width = n / grid_cols

    # 在每个网格中随机挑选一个点
    selected_points = set()
    for i in range(grid_rows):
        for j in range(grid_cols):
            if len(selected_points) >= x:
                break
            # 当前网格的范围
            x_min = int(i * grid_height)
            x_max = int((i + 1) * grid_height) - 1
            y_min = int(j * grid_width)
            y_max = int((j + 1) * grid_width) - 1

            # 防止越界
            x_max = min(x_max, n - 1)
            y_max = min(y_max, n - 1)

            # 在网格内随机选择一个点
            random_point = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            while random_point in selected_points:
                random_point = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            selected_points.add(random_point)
    
    return list(selected_points)

if __name__ == "__main__":
    # 示例使用
    n = 10  # 地图大小 10x10
    x = 8   # 挑选 8 个点

    points = select_points(n, x)
    print("随机挑选的点：", points)
    plot_map(n, points)
    