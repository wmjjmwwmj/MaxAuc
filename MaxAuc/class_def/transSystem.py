from networkx.classes.digraph import DiGraph

class TransSystem(DiGraph):
    # TODO 我之前是为啥要把ts的边的关系搞成字典的？
    def __init__(self, n, regions):
        super().__init__()
        self.n  = n
        self.regions = regions
        self.load_nodes_and_edges() # 初始化空字典来存储邻居节点关系
        
    def load_nodes_and_edges(self):
        # Add the nodes (regions)
        for node, label in self.regions.items():
            self.add_node(node, label=label)

        # Add the edges with weights
        # Create edges
        edges = []
        for i in range(self.n):
            for j in range(self.n):
                if i < self.n - 1:  # Vertical edges
                    edges.append(((i, j), (i + 1, j), 1))
                    edges.append(((i + 1, j), (i, j), 1))
                if j < self.n - 1:  # Horizontal edges
                    edges.append(((i, j), (i, j + 1), 1))
                    edges.append(((i, j + 1), (i, j), 1))
        
        for edge in edges:
            self.add_edge(edge[0], edge[1], cost=edge[2])
            
    def generate_neighbors_dict(self):
        neighbors_dict = {}
        
        for node1, node2 in self.edges():
            node1_3d = node1 + (1,)  # Add a dummy dimension
            node2_3d = node2 + (1,)
            
            if node1_3d not in neighbors_dict:
                neighbors_dict[node1_3d] = {}
            if node2_3d not in neighbors_dict:
                neighbors_dict[node2_3d] = {}

            # 添加邻居节点
            neighbors_dict[node1_3d][node2_3d] = self.edges[node1, node2]['cost']
            neighbors_dict[node2_3d][node1_3d] = self.edges[node1, node2]['cost'] # 如果边是无向的，添加这一行
        return neighbors_dict