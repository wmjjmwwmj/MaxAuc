# pylint: disable = E1101, E0611, C0103. c0116, c0303, E0402, c0114

import networkx as nx
from ..utils.logging_config import logger
import matplotlib.pyplot as plt


# 定义任务类
class Task:
    def __init__(self, DFA):
        self.task_label = DFA.graph["task_label"]
        # self.position = (
        #     {}
        # )  # key: 可以实现q转移的位置; value: 该位置的收益，只考虑DFA上的转移次数

        self.cumulate_benefit = 0  # 累计收益
        # 对应task网络的层级，得出sub-task的状态
        self.status = (
            "unpublished"  # 状态：unpublished, published, assigning, completed
        )

        self.DFA = DFA
        # DFA的初始状态和接受状态：str
        self.q_current = DFA.graph["initial"]
        self.q_accept = DFA.graph["accept"]
        self.prune_DFA()
        # self.get_progress_level()
        logger.info(f"Task {self.task_label} initialized")

    def __repr__(self):  # 可以用
        return f"Task-{self.task_label}, with {len(self.DFA)} states"

    def get_progress_level(self):
        # 遍历有向图自动机，根据距离q_accept的距离，得出任务的进度
        for node in self.DFA.nodes:
            distance = nx.shortest_path_length(self.DFA, node, self.q_accept)
            self.DFA.nodes[node]["distance"] = distance
            # 探究这个有没有道理？
            progress = 1 - (distance / (len(self.DFA) - 1))
            # progress = distance
            self.DFA.nodes[node]["progress_level"] = progress


    def prune_guard(self, guard):
        
        # 删掉否命题, 并把剩下的命题列表化

        '''
		sample of guard: " ( r1 & !r2 ) | ( r3 )"
		'''
		# 第一步，根据 | 将str分成列表，去掉小括号
        guard_list = guard.replace("(", "").replace(")", "").split("|")

        # 第二步，根据 & 将str分成列表
        guard_list = [sub_guard.split("&") for sub_guard in guard_list]

        # 第三步，去掉以 ! 开头的元素
        guard_list = [[sub_guard.strip() for sub_guard in sub_list if not sub_guard.strip().startswith("!")] for sub_list in guard_list]

        pruned_guard_list = [ap[0] for ap in guard_list if len(ap) == 1]

        return pruned_guard_list
    
    def prune_DFA(self):
        edges_to_remove = []
        nodes_to_remove = []
        edges_to_add = []

        # 遍历有向图 G 的所有边
        for parent, child in list(self.DFA.edges()):
            if parent == child:
                edges_to_remove.append((parent, child))
                continue

            original_guard = self.DFA.edges[parent,child]["guard"]
            # 对每条边执行函数，处理返回结果
            result = self.prune_guard(original_guard)
            
            self.DFA.edges[parent,child]["guard"] = result
            
            # 将原子命题数转换为权重，并作为DFA边的属性
            self.DFA.edges[parent,child]["weight"] = len(result)
                
        self.DFA.remove_edges_from(edges_to_remove)
        self.DFA.remove_nodes_from(nodes_to_remove)
        self.DFA.add_edges_from(edges_to_add)
        
    def draw_DFA(self,):
        plt.clf()
        # 设置图的布局
        pos = nx.spring_layout(self.DFA, k=0.5, seed=42)  # 采用spring_layout布局算法

        # 绘制节点和边
        nx.draw(self.DFA, pos, with_labels=True, node_size=200, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)

        # 获取边的标签并绘制
        edge_labels = nx.get_edge_attributes(self.DFA, 'guard')
        nx.draw_networkx_edge_labels(self.DFA, pos, edge_labels=edge_labels)
        
        # 重点标注初始节点：画箭头指向该节点
        x, y = pos[self.DFA.graph['initial']]  # 获取该节点的坐标
        plt.annotate("", xy=(x, y), xytext=(x-0.2, y+0.2),  # 设置箭头的起始和目标位置
                    arrowprops=dict(facecolor='red', shrink=0.05))

        # 重点标注可接受节点：双圈, 方式：# 再绘制一次相同节点，稍微增大半径，形成双圈效果
        nx.draw_networkx_nodes(self.DFA, pos, nodelist=self.DFA.graph['accept'], node_size=300, node_color='lightblue', linewidths=2.5, edgecolors='black')
        
        # 标注task_label
        plt.suptitle(f"Current Task: {self.task_label}", fontsize=14, fontweight='bold')

        # 保存图像
        plt.savefig(f".\\P_MAS_TG\\boolean_formulas\\spot\\HOA\\{self.task_label}_DFA.png")

    def calc_duration(self):
        # 计算任务持续时间，即到达可接受状态的最短路径长度
        duration = nx.shortest_path_length(self.DFA, self.q_current, self.q_accept)
        return duration