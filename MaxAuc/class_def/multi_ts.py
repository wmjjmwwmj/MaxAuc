# -*- coding: utf-8 -*-
from math import sqrt
import networkx as nx
from itertools import product
from ..utils.logging_config import logger
import time
from tqdm import tqdm
from networkx.classes.digraph import DiGraph

# 是否应该用多个机器人去叉乘？
# 其实一个机器人的转移系统，就是上下左右+条件限制
class MultiTS(DiGraph):
    def __init__(self, N, regions, robot_initial_pos):
        start_time = time.time()
        super().__init__(self)
        self.robot_num = len(robot_initial_pos)
        self.env_size = N
        self.regions = regions
        self.index_regions = {} # 字典的键可以是int
        self.robot_initial_pos = robot_initial_pos
        
        self.region_indexing()
        
        # self.index_region = {str(x* self.env_size + y)  for x, y in regions.keys()}
        
        # 构建完整的图
        self.initial_graph()
        
        self.initial_pos = None
        self.initial_robots()
        
        self.consume_time = time.time() - start_time
    
    def region_indexing(self):
        for key, value in self.regions.items():
            x, y = key
            index = x * self.env_size + y
            self.index_regions[index] = value
    
    # 对于坐标 (x,y)，对应的节点编号是 x * self.env_size + y
    def neighbors_index(self, index):
        x,y = index // self.env_size, index % self.env_size
        neighbors = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x+dx, y+dy
            if nx >= 0 and nx < self.env_size and ny >= 0 and ny < self.env_size:
                neighbors.append(nx * self.env_size + ny) 
        return neighbors

    def neighbors(self, node):
        
        neighbors = []
        for index, ap in node:
            item_list = [(index, ap)] # 部分机器人可以不动
            
            # 判断是否要完成节点
            if index in self.index_regions.keys():
                # 当前节点包含了ap
                if ap:
                    item_list.append((index, ""))
                else:
                    item_list.append((index, self.index_regions[index]))
            
            # 找临近节点
            for neighbor_index in self.neighbors_index(index):
                # 第一次转移一定没有ap
                # 这里很多时候不能有双向边
                item_list.append((neighbor_index, ""))
            neighbors.append(item_list)
                
        # 排列组合，笛卡尔积
        all_combinations = list(product(*neighbors))
        # 不考虑自身了，因为就是全员等待，不考虑这种情况了 - TODO: 删掉自己
        
        return [tuple(comb) for comb in all_combinations if tuple(comb) != node]
    
    def check_if_one_way_edge(self, node1, node2):
        is_bi_edge = True
        for i in range(self.robot_num):
            if node1[i][0] != node2[i][0] and node2[i][1] != "":
                is_bi_edge = False
                break
        return is_bi_edge

    def initial_graph(self):
        # 从 0,0,0, ... 开始增长
        initial_node = tuple((0, "") for _ in range(self.robot_num))
        self.add_node(initial_node)
        
        wait_for_add_node = [initial_node] 
        
        # tqdm settings
        total_nodes = 1
        update_frequency = 100 
        
        with tqdm(total=1, desc="MultiTS Graph construction", unit="node", dynamic_ncols=True) as pbar:
            while wait_for_add_node:
                batch = wait_for_add_node.copy()
                wait_for_add_node.clear()
                for p_node in batch:
                    
                    for c_node in self.neighbors(p_node):
                        if c_node == p_node:
                            continue
                        if c_node not in self.nodes():
                            self.add_node(c_node)
                            
                            self.add_edge(p_node, c_node, weight=1)
                            
                            if self.check_if_one_way_edge(c_node, p_node):
                                self.add_edge(c_node, p_node, weight=1)
                            wait_for_add_node.append(c_node)
                            
                            total_nodes += 1  # 更新已添加节点数
                            if total_nodes % update_frequency == 0:
                                pbar.update(update_frequency)  # 更新进度条
                                pbar.set_description(f"MultiTS Nodes")
                            
                        else:
                            self.add_edge(p_node, c_node, weight=1)
                            if self.check_if_one_way_edge(c_node, p_node):
                                self.add_edge(c_node, p_node, weight=1)
                
        # 最后更新一次，确保进度条显示最新的节点数
        remaining_updates = total_nodes % update_frequency
        if remaining_updates > 0:
            pbar.update(remaining_updates)
            pbar.set_description(f"MultiTS Nodes")
                
        logger.info(f"Initial MultiTS graph has {len(self.nodes())} nodes and {len(self.edges())} edges")

    def initial_robots(self):
        pos = []
        for x,y in self.robot_initial_pos:
            pos.append((x * self.env_size + y, ""))
        self.graph["initial"] = tuple(pos)
