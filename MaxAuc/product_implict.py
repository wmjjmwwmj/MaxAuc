# -*- coding: utf-8 -*-

from .buchi_0718 import check_label_for_buchi_edge
from networkx.classes.digraph import DiGraph

# 继承类，父类是DiGraph
class ProdAut_multi(DiGraph):
	"""
	用于表示基于邻接矩阵和Buchi自动机的产品自动机的类。
	
	参数:
	env: 包含邻接矩阵，元素表示转移的成本，初始状态，机器人数目。
	buchi: Buchi自动机，用于表示接受条件。
	alpha: 参数用于调整某些计算，具体用途根据实际情况定义。
	"""

	def __init__(self, ts, buchi, alpha=100):
		DiGraph.__init__(self, ts=ts, buchi=buchi, alpha=alpha, initial=set(), accept=set(), type='ProdAut')

	# # TODO: √ 7.31
	def build_full(self):
		for f_ts_node in self.graph['ts'].nodes():
			for f_buchi_node in self.graph['buchi'].nodes():
				f_prod_node = self.composition(f_ts_node, f_buchi_node)
				for t_ts_node in self.graph['ts'].successors(f_ts_node):
					for t_buchi_node in self.graph['buchi'].successors(f_buchi_node):
							t_prod_node = self.composition(t_ts_node, t_buchi_node)
							
							label = self.graph['ts'].nodes[f_ts_node]['label']
							cost = self.graph['ts'][f_ts_node][t_ts_node]['weight']
							# check if the label is valid for the buchi edge
							truth, dist = check_label_for_buchi_edge(self.graph['buchi'], label, f_buchi_node, t_buchi_node)
							print ('label,truth,total_weight:', label,truth,total_weight)
							if truth:
								total_weight = cost + self.graph['alpha']*dist
								self.add_edge(f_prod_node, t_prod_node, weight=total_weight)
								print ('add edge', (f_prod_node, t_prod_node))
		print ('full product constructed with %d states and %s transitions' %(len(self.nodes()), len(self.edges())))                         
	# def build_full(self):
		

	# def build_full_single(buchi, env_start):
	# 	"""
	# 	Builds the full product tree for a single agent in a multi-agent system.

	# 	Args:
	# 		buchi (BuchiAutomaton): The Buchi automaton representing the agent's behavior.
	# 		env_start (EnvironmentState): The initial state of the environment.

	# 	Returns:
	# 		product_tree (ProductTree): The full product tree representing the interaction between the agent and the environment.
	# 	"""
	# 	product_state_queue = [[buchi_initial, env_initial]]
	# 	buchi_accept_flag = False

	# 	while product_state_queue:
	# 		product_state_queue_new = []
	# 		for buchi_state, env_state in product_state_queue:
	# 			env_successor_list = find_next_env_state(env_state)
	# 			for env_successor in env_successor_list:
	# 				buchi_successor = check_label_for_buchi_edge(buchi_state, env_state, env_successor)
	# 				if not is_accept(buchi_successor):
	# 					add_edge_for_product(buchi_state, env_state, buchi_successor, env_successor)
	# 					product_state_queue_new.append([buchi_successor, env_successor])
	# 		product_state_queue = product_state_queue_new

	# 	return product_tree

	# def build_full_multi_root(product, buchi, ):
	# 	root_list = leaf(profuct)
	# 	for root in root_list:
	# 		product_new = build_full_single(buchi, root[1])
	# 		tree_extend(product, product_new, root) 

	def composition(self, ts_node, buchi_node):
		prod_node = (ts_node, buchi_node)
		if not self.has_node(prod_node):
			self.add_node(prod_node, ts=ts_node, buchi=buchi_node, marker='unvisited')
			if ((ts_node in self.graph['ts'].graph['initial']) and
				(buchi_node in self.graph['buchi'].graph['initial'])):
				self.graph['initial'].add(prod_node)
			if (buchi_node in self.graph['buchi'].graph['accept']):
				self.graph['accept'].add(prod_node)
		return prod_node

	# 返回规划
	def projection(self, prod_node):
		ts_node = self.node[prod_node]['ts']
		buchi_node = self.node[prod_node]['buchi']
		return ts_node, buchi_node

	def build_initial(self):
		self.graph['ts'].build_initial()
		for ts_init in self.graph['ts'].graph['initial']:
			for buchi_init in self.graph['buchi'].graph['initial']:
				init_prod_node = self.composition(ts_init, buchi_init)

	def build_accept(self):
		self.graph['ts'].build_full()
		accept = set()
		for ts_node in self.graph['ts'].nodes():
			for buchi_accept in self.graph['buchi'].graph['accept']:
				accept_prod_node = self.composition(ts_node, buchi_accept)

	def accept_predecessors(self, accept_node):
		pre_set = set()
		t_ts_node, t_buchi_node = self.projection(accept_node)
		for f_ts_node, cost in self.graph['ts'].fly_predecessors(t_ts_node):
			for f_buchi_node in self.graph['buchi'].predecessors(t_buchi_node):
				f_prod_node = self.composition(f_ts_node, f_buchi_node)
				label = self.graph['ts'].node[f_ts_node]['label']
				truth, dist = check_label_for_buchi_edge(self.graph['buchi'], label, f_buchi_node, t_buchi_node)
				total_weight = cost + self.graph['alpha']*dist
				if truth:
					pre_set.add(f_prod_node)
					self.add_edge(f_prod_node, accept_node, weight=total_weight)
		return pre_set

	def fly_successors(self, f_prod_node):
		f_ts_node, f_buchi_node = self.projection(f_prod_node)
		# been visited before, and hasn't changed 
		if ((self.node[f_prod_node]['marker'] == 'visited') and 
			(self.graph['ts'].graph['region'].node[
				self.graph['ts'].node[self.node[f_prod_node]['ts']]['region']]['status'] == 'confirmed')):
			for t_prod_node in self.successors(f_prod_node):
				yield t_prod_node, self.edges[f_prod_node,t_prod_node]['weight']
		else:
			self.remove_edges_from(self.out_edges(f_prod_node))
			for t_ts_node,cost in self.graph['ts'].fly_successors(f_ts_node):
				for t_buchi_node in self.graph['buchi'].successors(f_buchi_node):
					t_prod_node = self.composition(t_ts_node, t_buchi_node)
					label = self.graph['ts'].node[f_ts_node]['label']
					truth, dist = check_label_for_buchi_edge(self.graph['buchi'], label, f_buchi_node, t_buchi_node)
					total_weight = cost + self.graph['alpha']*dist
					if truth:
						self.add_edge(f_prod_node, t_prod_node, weight=total_weight)
						yield t_prod_node, total_weight
			self.node[f_prod_node]['marker'] = 'visited'


class ProdAut_Run(object):
	# prefix, suffix in product run
	# prefix: init --> accept, suffix accept --> accept
	# line, loop in ts
	def __init__(self, product, prefix, precost, suffix, sufcost, totalcost):
		self.prefix = prefix
		self.precost = precost
		self.suffix = suffix
		self.sufcost = sufcost
		self.totalcost = totalcost
		#self.prod_run_to_prod_edges(product)
		self.plan_output(product)
		#self.plan = chain(self.line, cycle(self.loop))
		#self.plan = chain(self.loop)

	def prod_run_to_prod_edges(self, product):
		self.pre_prod_edges = zip(self.prefix[0:-2], self.prefix[1:-1])
		self.suf_prod_edges = zip(self.suffix[0:-2], self.suffix[1:-1])

	def plan_output(self, product):
		self.line = [product.node[node]['ts'] for node in self.prefix]
		self.loop = [product.node[node]['ts'] for node in self.suffix]
		if len(self.line) == 2:
			self.pre_ts_edges = [(self.line[0], self.line[1])]
		else:
			self.pre_ts_edges = zip(self.line[0:-1], self.line[1:])
			if len(self.loop) == 2:
					self.suf_ts_edges = [(self.loop[0], self.loop[1])]
			else:
				self.suf_ts_edges = zip(self.loop[0:-1], self.loop[1:])
				self.suf_ts_edges.append((self.loop[-1],self.loop[0]))
		# output plan
		self.pre_plan = []
		self.pre_plan.append(self.line[0][0]) 
		for ts_edge in self.pre_ts_edges:
			if product.graph['ts'][ts_edge[0]][ts_edge[1]]['label'] == 'goto':
				self.pre_plan.append(ts_edge[1][0]) # motion 
			else:
				self.pre_plan.append(ts_edge[1][1]) # action
				bridge = (self.line[-1],self.loop[0])
				if product.graph['ts'][bridge[0]][bridge[1]]['label'] == 'goto':
					self.pre_plan.append(bridge[1][0]) # motion 
		else:
			self.pre_plan.append(bridge[1][1]) # action
		self.suf_plan = []		
		for ts_edge in self.suf_ts_edges:
			if product.graph['ts'][ts_edge[0]][ts_edge[1]]['label'] == 'goto':
				self.suf_plan.append(ts_edge[1][0]) # motion 
			else:
				self.suf_plan.append(ts_edge[1][1]) # action










