from collections import defaultdict, deque
import numpy as np

def int2char_2DList(matrix):
    return [[str(i) for i in row] for row in matrix]

def topological_sort(matrix):
    # 如果矩阵为空，返回全列表：用不到 -> 必须有num of tasks
    # if not matrix:
    #     return [str(i) for i in range(len(matrix[0]))]
    
    # 初始化图
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    num_tasks = len(matrix)
    
    # 构建图和入度表
    for i in range(num_tasks):
        for j in range(num_tasks):
            if i == j:
                continue
            
            if matrix[i,j] == 1:
                graph[i].append(j)
                in_degree[j] += 1
    
    # 找到所有入度为0的节点
    zero_in_degree_queue = deque([k for k in range(num_tasks) if k not in in_degree])
    
    # 初始化层级列表
    layers = []
    
    # 执行拓扑排序
    while zero_in_degree_queue:
        current_layer = []
        for _ in range(len(zero_in_degree_queue)):
            u = zero_in_degree_queue.popleft()
            current_layer.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    zero_in_degree_queue.append(v)
        layers.append(current_layer)
    
    return int2char_2DList(layers)