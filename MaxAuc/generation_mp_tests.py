import random
from .class_def.mp_solver import solution
import time

def generate_random_deltas(n):
    """生成一个随机的增量列表 delta，确保所有 delta 值为正"""
    # 包含1和10
    return [random.randint(1, 10) for _ in range(n)]

def generate_random_relation(n):
    """生成一个随机的约束关系字典，确保不会产生冲突"""
    ss = []
    es = []
    ee = []
    se = []
    
    # 随机生成 ss（x_i < x_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                ss.append((i, j))
    
    # 随机生成 es（x_i + delta_i < x_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                es.append((i, j))
    
    # 随机生成 ee（x_i + delta_i < x_j + delta_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                ee.append((i, j))
    
    # 随机生成 se（x_i < x_j + delta_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                se.append((i, j))
    
    return {"ss": ss, "es": es, "ee": ee, "se": se}

def test_solver(n, multiple_times = 1000):
    deltas = generate_random_deltas(n)
    relation_dict = generate_random_relation(n)
    
    print(f"n = {n}")
    print(f"Generated deltas: {deltas}")
    print(f"Generated relation_dict: {relation_dict}")
    
    
    start_time = time.time()
    first_result = solution(n, deltas, relation_dict)
    for i in range(multiple_times):
        result = solution(n, deltas, relation_dict)
        if result != first_result:
            raise ValueError("Found different solutions in multiple runs!")

    consumed_time = time.time() - start_time
    
    if result is None:
        print("No solution found.")
    else:
        print(f"Solution: {result}")
        print(f"Time consumed: {consumed_time:.6f} seconds")
    print("="*50)
    
    return consumed_time

def test_solver_blank_relation(n, multiple_times = 1000):
    deltas = generate_random_deltas(n)
    relation_dict = {}
    
    print(f"n = {n}")
    print(f"Generated deltas: {deltas}")
    print(f"Generated relation_dict: {relation_dict}")
    
    
    start_time = time.time()
    first_result = solution(n, deltas, relation_dict)
    for i in range(multiple_times):
        result = solution(n, deltas, relation_dict)
        if result != first_result:
            raise ValueError("Found different solutions in multiple runs!")

    consumed_time = time.time() - start_time
    
    if result is None:
        print("No solution found.")
    else:
        print(f"Solution: {result}")
        print(f"Time consumed: {consumed_time:.6f} seconds")
    print("="*50)
    
    return consumed_time

if __name__ == '__main__':

    # 生成并测试多个数据集
    # for n in range(2, 100):  # 测试 n 从 2 到 5 的情况
    #     test_solver(n)
    00
    test_solver_blank_relation(5)
