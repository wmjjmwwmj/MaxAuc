# -*- coding: utf-8 -*-
import sys, time
sys.path.append('D:/Paper/code_/multi-agent')

import networkx as nx
from networkx.classes.digraph import DiGraph

from ..utils.logging_config import logger
from networkx import dijkstra_predecessor_and_distance
import ast
from collections import Counter
from itertools import product
from tqdm import tqdm

class MultiPBA(DiGraph):

    def __init__(self, MultiTS, MultiDFA):
		# 对于继承类，一定要初始化父类！
        start_time = time.time()
        super().__init__(self, type="ProdPlanner", symbols=set())
        self.MultiTS = MultiTS
        self.MultiDFA = MultiDFA
        
        self.exhaustive_product()
        
        self.consume_time = time.time() - start_time

	
    def parse_pba_node(self, pba_node):
        inner_str = pba_node.split(" & ")
        q = ast.literal_eval(inner_str[0])
        x = ast.literal_eval(inner_str[1])
        return q,x

    def find_successors(self, pba_node):
        # 重要的是，哪些不被要求但是满足了的命题，有错吗？ - 没有错，因为允许不上报，planner会直接忽视
        # 遍历所有的状态，找到所有的满足状态，然后计算cost，都记录上
        
        # 找到所有的q后继节点，以及guard
        q,x = self.parse_pba_node(pba_node)
        new_node_list = []
        new_edge_list = []
        
        successors = list(self.MultiDFA.successors(q))
        for successor in successors:
            # 检查是否是可接受节点
            is_accept = all( k[1] == 'e' for k in successor)

            guard_list = self.MultiDFA.edges[q, successor]['guard']
            # if not guard_list:
            #     raise nx.NetworkXError(f"Edge without guard exist in DFA.")
            for node in list(self.MultiTS.nodes()):
                
                # LEARN: ALL的用法
                finished_aps = [k[1] for k in node]
                
                # 另一种实现方式：一个机器人，一个时间步，可以完成属于两个任务的ap
                # is_match = all(
                #                 (not guard ) or 
                #                 (guard  and any( ap in guard for ap in finished_aps)) 
                #                 for guard in guard_list
                #                 )
                is_match = self.is_valid(guard_list, finished_aps)
                
                if is_match:
                    # TODO 是否包含了开头结尾？
                    # shortest_path_list = nx.all_shortest_paths(self.MultiTS, source=x, target=node)
                    shortest_path = nx.shortest_path(self.MultiTS, source=x, target=node)
                    weight = len(shortest_path) -1 if len(shortest_path) > 1 else 1
                else:
                    continue
                
                # 添加节点
                new_node = f"{successor} & {node}"
                if is_accept:
                    self.graph['accept'].append(new_node)

                new_node_list.append(new_node)
                new_edge_list.append((pba_node, new_node, {"weight":weight, "path":shortest_path}))
        return new_node_list, new_edge_list

    def is_valid(self, guard_list, finished_aps):
        guard_list_without_blank  = [guard for guard in guard_list if guard != ""]
        guard_comb = list(product(*guard_list_without_blank))
        
        f_count = Counter(finished_aps)
        
        for guard in guard_comb:
            g_count = Counter(guard)
            if all( f_count[k] >= g_count[k] for k in g_count.keys()):
                return True
        
        return False
        
    def exhaustive_product(self):
        # 找到初始值
        self.graph['initial'] = f"{self.MultiDFA.graph['initial']} & {self.MultiTS.graph['initial']}"
        self.graph['accept'] = []   
        # 递归地构造product
        new_wait_nodes = [self.graph['initial']]
        
        # tqdm settings
        total_nodes = 1
        
        with tqdm(total=1, desc="MultiPBA Graph construction", unit="nodes", dynamic_ncols=True) as pbar:
            while new_wait_nodes:
                wait_for_add = new_wait_nodes
                new_wait_nodes = []
                for i in wait_for_add:
                    new_node_list, new_edge_list = self.find_successors(i)
                    # add_node_count = 0
                    for new_node in new_node_list:
                        if new_node not in self.nodes():
                            # add_node_count += 1
                            new_wait_nodes.append(new_node) # TODO 好像会绕回去，形成循环，原因？
                            self.add_node(new_node)
                            pbar.update(1)
                            pbar.set_description(f"MultiPBA Nodes")
                    # self.add_nodes_from(new_node_list)
                    self.add_edges_from(new_edge_list)

                    # # print(f"new_nodes_num: {new_nodes_num}")
                    # pbar.update(add_node_count)
                    # pbar.set_description(f"MultiPBA Nodes")
        
        # logger.info(f"Number of PBA nodes: {len(self.nodes())}")

    def optimal_path(self):
        line_pre, line_dist = dijkstra_predecessor_and_distance(
            self, self.graph["initial"], weight="weight"
        )
        
        # 找到最短的路径对应的可接受节点
        min_cost = float("inf")
        target = None
        for i in self.graph["accept"]:
            # TODO: 等于最短路径的都保留着，最后只用第一个，需要保存的稍微有点多
            # 先只取最后的方案
            if line_dist[i] <= min_cost:
                min_cost = line_dist[i]
                target = i

        PBA_path_reverse = [target]
        
        final_node = self.parse_pba_node(target)[1]

        # 返回到达target的最短路径
        pre_node = line_pre[target][0] if line_pre[target] else None
        PBA_path_reverse.append(pre_node)
        
        reversed_path = [] 

        while pre_node is not None:  # 在python中，None, 0, [], {} 都会被当作False
            PBA_path_reverse.append(pre_node)
            
            reversed_path.append(self.edges[(pre_node, target)]["path"])
            target = pre_node
            pre_node = line_pre[pre_node][0] if line_pre[pre_node] else None
        
        
        # start_node = self.parse_pba_node(self.graph["initial"])[1]
        
        path = []

        for sub_path in reversed_path[::-1]:
            if len(sub_path) == 1:
                path.append(sub_path[0])
            else:
                path.extend(sub_path[:-1])
        
        path.append(final_node)

        # 统计总的路径长度
        path_all_len = 0
        env_size = self.MultiTS.env_size
        for i in range(len(path)-1):
            pre_node = path[i]
            target_node = path[i+1]
            
            for j in range(len(pre_node)):
                x1,y1 = pre_node[j][0] // env_size, pre_node[j][0] % env_size
                x2,y2 = target_node[j][0] // env_size, target_node[j][0] % env_size
                path_all_len += abs(x1-x2) + abs(y1-y2)

        logger.info(f"path_all_len: {path_all_len}")

        PBA_path = [self.parse_pba_node(node)[0] for node in PBA_path_reverse[::-1]]
        logger.info(f"PBA path: {PBA_path}")
        
        # min cost 即为最短路径的长度
        logger.info(f"make span: {min_cost}")
        logger.info(f"path: {path}")
        
        return min_cost, path_all_len