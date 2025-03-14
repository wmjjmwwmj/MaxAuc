# -*- coding: utf-8 -*-
from networkx import dijkstra_predecessor_and_distance
import time
from .utils.logging_config import logger

# ===========================================
# optimal initial synthesis
# ===========================================
def dijkstra_plan_networkX(product):
    # 首先排除正好就在accept节点的情况，这种情况下不需要规划
    if product.graph["initial"] in product.graph["accept"]:
        return product.graph["initial"], [product.graph["initial"]], 0
    else:
        # requires a full construct of product automaton
        start = time.time()
        runs = {}

        prod_init = product.graph["initial"]

        # line_pre: 告诉你从源节点到达该节点的最短路径上，上一个节点是什么。这可以用于回溯最短路径。
        # line_dist: 从源节点到达该节点的最短路径的长度，此处用不到
        line_pre, line_dist = dijkstra_predecessor_and_distance(
            product, prod_init, weight="cost"
        )
        path = {}
        for target in product.graph["accept"]:
            # 返回到达target的最短路径
            pre_node = line_pre[target][0] if line_pre[target] else None
            cost = product.edges[pre_node, target]["cost"]
            reversed_path = [target]

            while pre_node is not None:  # 在python中，None, 0, [], {} 都会被当作False
                reversed_path.append(pre_node)
                next_node = line_pre[pre_node][0] if line_pre[pre_node] else None
                if next_node:
                    cost += product.edges[next_node, pre_node]["cost"]
                pre_node = next_node

            # print("reversed_path:", reversed_path)
            # logger.info(f"reversed_path: {reversed_path}")
            path[target] = {"path": list(reversed(reversed_path)), "cost": cost}
        min_cost = float("inf")
        opt_tar, opt_path = None, None
        for target, properties in path.items():
            if properties["cost"] < min_cost:
                min_cost = properties["cost"]
                opt_tar = target  # 如果没有提前声明，则只在循环内有效
                opt_path = properties["path"]

        # logger.info("==================")
        # logger.info(
        #     "Dijkstra_plan_networkX done within %.2fs: cost %.2f"
        #     % (time.time() - start, min_cost)
        # )
        # logger.info(f"Start: {prod_init}")
        # logger.info(f"optimal target: {opt_tar}")
        logger.info(f"optimal path node: {opt_path}")
        return opt_tar, opt_path, min_cost
