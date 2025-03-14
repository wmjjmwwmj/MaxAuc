# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import networkx as nx
from networkx.classes.digraph import DiGraph
from itertools import product

from collections import defaultdict

from ..utils.logging_config import logger

import time
from tqdm import tqdm

class MultiDFA(DiGraph):
    def __init__(self, DFA_list, cascade_constraints):
        # super(): 这个调用返回了父类 DiGraph 的一个代理对象，通过这个代理对象，你可以调用 DiGraph 中的方法。
        
        start_time = time.time()
        
        super().__init__(self, type="MultiDFA", symbols=set())
        """ DFA_list = {
            "0": DFA0, # 0是task_label
        }
        """
        self.DFA_list = DFA_list
        self.task_num = len(DFA_list)
        self.cascade_constraints = cascade_constraints
        # 暂时先不传入task了，之后再看是否需要
        self.task_cascade_constraints = self.task_dependent_constraints_convert()
        
        self.exhaustive_product()
        
        self.check_cascade_constraints()
        
        self.consume_time = time.time() - start_time  
######################################################################
################# constraint 检查/更新工具 ############################
######################################################################
        
    def task_dependent_constraints_convert(self, constraints=None):
        convert_constraints = defaultdict(dict)
        for i in range(self.task_num):
            convert_constraints[str(i)] = self.check_task_cascade(str(i), constraints)
        return convert_constraints
        
    def check_task_cascade(self, task_label, constraints=None): 
        """检查任务是否被具有其他依赖

        Args:
            task_label (_type_): _description_
            constraints (_type_): _description_

        Returns:
            constraints (dict): 
        """
        # 如果传入了约束信息，则使用传入的约束
        if constraints is None:
            constraints = self.cascade_constraints
        
        dependent_tasks = {
                            "ss": [],
                            "es": [],
                            "ee": [],
                            "se": [],
                        }
        # 遍历约束，检查任务是否有依赖关系
        for relation, tasks in constraints.items():
            for task1, task2 in tasks:
                if task2 == int(task_label):
                    dependent_tasks[relation].append((task1, task2))

        # 依赖关系
        return dependent_tasks

    # for normal format
    def update_constraints(self, task_label, is_start, is_end, constraints):
        """_summary_

        Args:
            task_index (_type_): _description_
            is_start (bool): _description_
            is_end (bool): _description_
        """
        # logger.info(f"因为 {task_label} 的 开始_{is_start} / 结束_{is_end} 而更新约束")
        # logger.info(f"之前的约束: {constraints}")
        # 遍历约束，检查任务是否有依赖关系
        if is_start:
            constraints["ss"] = [i for i in constraints["ss"] if str(i[0])!=task_label]
            constraints["se"] = [i for i in constraints["se"] if str(i[0])!=task_label]
        if is_end:
            constraints["ss"] = [i for i in constraints["ss"] if str(i[0])!=task_label]
            constraints["se"] = [i for i in constraints["se"] if str(i[0])!=task_label]
            constraints["ee"] = [i for i in constraints["ee"] if str(i[0])!=task_label]
            constraints["es"] = [i for i in constraints["es"] if str(i[0])!=task_label]
        # logger.info(f"更新后的约束: {constraints}")

######################################################################
################# 乘积构造 ############################################
######################################################################
        
    # 只需要看各个DFA的节点，不需要考虑状态
    def exhaustive_neighbor(self, m_DFA_node):
        # 结尾记得检查状态是否是 accept
        e_neighbors = []
        
        # 访问不存在的value也不会报错，会返回 None
        neighbor_with_guard = defaultdict(dict)
        for index, (node, state) in enumerate(m_DFA_node) :
            # 分开处理每个人物的后继状态
            # 如果是可接受节点，就返回自己
            task_label = str(index)
            
            if state == "e":
                e_neighbors.append([node])
                neighbor_with_guard[task_label][node] = ""
            else:
                # neighbor库，[[], [], []...] 包含了所有的候选结果

                raw_neighbors = list(self.DFA_list[str(index)].successors(node))
                

                for successor in raw_neighbors:
                    neighbor_with_guard[task_label][successor] = self.DFA_list[task_label].edges[node, successor]['guard']
                
                # 由于DFA已经处理掉了自环，所以要补一个自环，并补上guard为 ""
                raw_neighbors.append(node)
                e_neighbors.append(raw_neighbors)
                neighbor_with_guard[task_label][node] = ""
            
        # 生成所有节点
        all_combinations = list(product(*e_neighbors))
        node_only_state = tuple([i[0] for i in m_DFA_node]) 
        
        successors_with_self = [tuple(comb) for comb in all_combinations]
        # 记得要删除自身，不然会无限循环
        successors_with_self.remove(node_only_state)
        
        return successors_with_self, neighbor_with_guard
        
    def exhaustive_product(self):
        # 把所有的节点标识符都利用起来
        """_summary_
        Args:
            buchi_list (_type_): DiGraph的列表，每个DiGraph代表一个buchi自动机
        """
        # 初始化
        self.acquire_initial_state() # 可接受节点自然生成，就先不考虑了
        
        # initial_successors, neighbor_with_guard = self.exhaustive_neighbor(self.graph['initial'])
        
        new_wait_nodes = [self.graph['initial']]
        
        # tqdm settings
        total_nodes = 1
        update_frequency = 1
        
        with tqdm(total=1, desc="MultiDFA Graph construction", unit="node", dynamic_ncols=True) as pbar:
        
            while new_wait_nodes:
                wait_for_add_nodes = new_wait_nodes
                new_wait_nodes = []
                for wait_for_add_node in wait_for_add_nodes:
                    successors, neighbor_with_guard = self.exhaustive_neighbor(wait_for_add_node)
                    # 依次添加
                    # 应该是没有重复的
                    for successor in successors:
                        new_node = []
                        guard_compound = []
                        # 检查状态并添加节点 （不用担心重复，添加的时候会自动跳过）
                        for i in range(len(successor)):
                            # 合成guard
                            guard_compound.append(neighbor_with_guard[str(i)][successor[i]])
                            # 检查节点状态
                            if successor[i] == self.DFA_list[str(i)].graph['accept']:
                                new_node.append((successor[i], "e"))
                            # 这种情况应该是存在的，因为部分DFA可能还停留在初始阶段
                            elif successor[i] == self.DFA_list[str(i)].graph['initial']:
                                new_node.append((successor[i], "s"))
                                # raise nx.NetworkXError(f"Initial state should not be reached after initial.")
                            else:
                                new_node.append((successor[i], ""))

                        # 要注意保证节点都是 tuple
                        new_node = tuple(new_node)
                        if new_node not in self.nodes():
                            new_wait_nodes.append(new_node) # 应该是不存在循环，如果有的话检查这里
                            self.add_node(new_node)
                        self.add_edge(wait_for_add_node, new_node, guard = guard_compound)
                        
                        
                        if total_nodes % update_frequency == 0:
                            pbar.update(update_frequency)  # 更新进度条
                            pbar.set_description(f"MultiDFA Nodes")
                        
                    
        # 最后更新一次，确保进度条显示最新的节点数
        remaining_updates = total_nodes % update_frequency
        if remaining_updates > 0:
            pbar.update(remaining_updates)
            pbar.set_description(f"MultiDFA Nodes")
                    
        logger.info(" MultiDFA 初始化构造完毕")
        
######################################################################
################# 基于cascade的pruning ################################
######################################################################

    def check_valid_and_update_constraints(self, node1, node2):
        node1_task_constraints = self.nodes[node1]['task_constraint']
        # 生成不同的task constraints 的字典
        """
        self.task_cascade_constraints = {
            task_label:{
                "ss": [],
                "es": [],
                "ee": [],
                "se": [],
            }
        }
        """
        node2_constraints = self.nodes[node1]['constraint'].copy() # 不能直接赋值，会导致两个变量指向同一个对象

        for i in range(len(node1)):
            if node2[i][1] == "e":
                # 检查是否合理
                if node1_task_constraints[str(i)]["se"] +  node1_task_constraints[str(i)]["ee"]:
                    return False
                else:
                    # 更新约束
                    self.update_constraints(str(i), False, True, node2_constraints)
            elif node1[i][1] == "s" and node2[i][1] != "s":
                if node1_task_constraints[str(i)]["ss"] +  node1_task_constraints[str(i)]["es"]:
                    return False
                else:
                    self.update_constraints(str(i), True, False, node2_constraints)
                
        # 整理约束
        self.nodes[node2]['constraint'] = node2_constraints
        self.nodes[node2]['task_constraint'] = self.task_dependent_constraints_convert(node2_constraints)
        return True
        
    # Prompt：我有一个有向图，以及一个合法路径的判定函数，可以判断某个边是否合法。我想使用DFS去搜索，从根节点出发，删掉不合法的边。当删掉了某一条边 (a,b) 之后，b节点之后的边就不用管了。注意的是，我在遍历的时候，会给每个节点标记一些标签，便于之后检查边的合法性。我想问一下，这个问题该怎么解决？
    def check_cascade_constraints(self):
        # 给每个节点一个当前所受的约束集合
        # 根节点是最全的集合
        self.nodes[self.graph['initial']]['constraint'] = self.cascade_constraints
        self.nodes[self.graph['initial']]['task_constraint'] = self.task_cascade_constraints
        # DFS 搜索
        # 需要被裁剪的边存储起来，之后一起删掉
        edges_to_remove = []
        def dfs(node, visited, edges_to_remove, phar):
            visited.add(node)
            phar.update(1)
            for succ in self.successors(node):
                if succ not in visited:
                    # 更新约束
                    if self.check_valid_and_update_constraints(node, succ):
                        dfs(succ, visited,edges_to_remove, phar)
                    else:
                        edges_to_remove.append((node, succ))
        
        # 使用 tqdm 显示进度条
        with tqdm(total=len(self.nodes()), desc="DFS Progress", unit="node", dynamic_ncols=True) as pbar:
            dfs(self.graph['initial'], set(), edges_to_remove, pbar)
        self.remove_edges_from(edges_to_remove)
        logger.info("cascade约束检查完毕")

        # TODO: 考虑删掉除了initial_node之外，所有入度为0的节点

######################################################################
################# 初始化 #############################################
######################################################################

    def acquire_initial_state(self):
        # 在这里，再次假设所有的task_label都是按序的序号
        # 为了后序判断constraint方便，我们也采用二元组 (("0", "s"), ("1", "e"), ("2", "")) 的形式 
        # "s" 何时取到？ - 代表初始状态最方便赋值，判定的时候再说
        initial_prod_state = []
        for i in range(self.task_num):
            DFA = self.DFA_list[str(i)]
        # for DFA in self.DFA_list: 
            initial_prod_state.append((DFA.graph['initial'], "s"))

        self.graph['initial'] = tuple(initial_prod_state)

        # logger.info("Initial state: {}".format(self.graph['initial']))
        self.add_node(self.graph['initial'])
    


######################################################################
################# 辅助函数 ############################################
######################################################################

# 暂时没用
def check_label_for_buchi_edge(buchi, label, f_buchi_node, t_buchi_node):
    truth = buchi.edges[f_buchi_node, t_buchi_node]['guard'].check(label)
    if truth:
        dist = buchi.edges[f_buchi_node, t_buchi_node]['guard'].distance(label)
    else:
        dist = -1
    return truth, dist