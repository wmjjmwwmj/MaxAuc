# pylint: disable = E1101, E0611, C0103. c0116, c0303, E0402, c0114, c0115, w0511, r0902, r0913, w1203, c0411

from ..construct_task_tree import topological_sort
from .option import Option
from .bid import Bid
from queue import PriorityQueue
from ..utils.logging_config import logger
import re
from readerwriterlock import rwlock
from collections import defaultdict
from .mp_solver import solution
import math
import copy



# 定义任务管理器
class TaskManager:
    # 使用多线程的一个缺点是，没法半路给一个线程加锁，只能在初始化的时候就加锁；同理，没法半路创建线程之间的通道，必须在开始之前就铺好

    def __init__(
        self, ts, message_queue, assign_queue, event_list, answer_event, flag_queue, price_umax, price_alpha, N, cascade_cons
    ):
        # setting
        self.ts = ts

        # 字典类型的变量
        self.tasks = {}  # 存储所有任务
        self.options_list = {}  # 有问题，option没上架
        self.task_index_options_list = {}
        self.finished_task_list = []  # 用来存储已经完成的任务

        # 锁 + 信号
        self.rw_lock = rwlock.RWLockFair()
        self.event_list = event_list
        self.answer_event = answer_event

        # 通信相关
        self.message_queue = message_queue
        self.assign_queue = assign_queue
        self.flag_queue = flag_queue

        # task level相关, task 的类实例存储于tasks字典中
        self.N = N # TODO:task count
        self.cascade_constraints = cascade_cons
        self.task_remain_deltas = []  # 任务进度
        
        # task 状态相关，存储task label
        self.task_status = {
            "pending": [],
            "not stared": [],
            "in progress": [], 
            "pend for finish": [],
            "finished": [], # 目前只利用到这个状态，用来判断任务是否全部结束
            "assigned": [], # 表示目前已经有atom分配出去了 
        }

        # bid
        self.task_bid_p_queue = PriorityQueue()
        self.bids_backup = {}  # 用来存储所有的bid信息 TODO how to update? -> 这个是task_bid_p_queue的副本,随着task_bid_p_queue的更新而更新
        self.delta = 2  # 随着寿命增长，value增加的速度

        # 线程状态相关
        self.complete_all_tasks = False
        
        # price & bid params
        self.price_umax = price_umax
        self.price_alpha = price_alpha

################################################################
###################### constraint 相关的函数 ####################
################################################################

# 先搞成标准化的，任务都开始，然后再审查，最好论证以下，审查会很快，跟具体的依赖复杂度相关

    def update_constraints(self, task_label, is_start, is_end):
        """_summary_

        Args:
            task_index (_type_): _description_
            is_start (bool): _description_
            is_end (bool): _description_
        """
        logger.info(f"因为 {task_label} 的 开始_{is_start} / 结束_{is_end} 而更新约束")
        logger.info(f"之前的约束: {self.cascade_constraints}")
        # 遍历约束，检查任务是否有依赖关系
        if is_start:
            self.cascade_constraints["ss"] = [i for i in self.cascade_constraints["ss"] if str(i[0])!=task_label]
            self.cascade_constraints["se"] = [i for i in self.cascade_constraints["se"] if str(i[0])!=task_label]
        if is_end:
            self.cascade_constraints["ss"] = [i for i in self.cascade_constraints["ss"] if str(i[0])!=task_label]
            self.cascade_constraints["se"] = [i for i in self.cascade_constraints["se"] if str(i[0])!=task_label]
            self.cascade_constraints["es"] = [i for i in self.cascade_constraints["es"] if str(i[0])!=task_label]
            self.cascade_constraints["ee"] = [i for i in self.cascade_constraints["ee"] if str(i[0])!=task_label]
        logger.info(f"更新后的约束: {self.cascade_constraints}")

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
        is_independent = True

        # 遍历约束，检查任务是否有依赖关系
        for relation, tasks in constraints.items():
            for task1, task2 in tasks:
                if task2 == int(task_label):
                    is_independent = False
                    dependent_tasks[relation].append((task1, task2))

        # 返回是否有依赖关系以及具体依赖的任务
        if not is_independent:
            return dependent_tasks
        else:
            return 

    def check_atomic_constraints(self, q_state, is_start, is_end, task_label, constraints=None):
        """_summary_

        Args:
            q_state (_type_): _description_
            task_label (_type_): _description_
            constraints (_type_, optional): _description_. Defaults to None.

        Returns:
            is_free (str): a bool variable
        """
        if not is_start and not is_end:
            return True
        
        if task_label == "1":
            pass
        
        dependent_tasks = self.check_task_cascade(task_label, constraints)
        if dependent_tasks:
            # 依次检查 ss，es，再判断是否属于
            if is_start and (dependent_tasks["ss"] or dependent_tasks["es"] ):
                return False
            if is_end and (dependent_tasks["ee"] or dependent_tasks["se"] ):
                return False
            
        return True

#################################################################
###################### mp 相关的函数 ############################
#################################################################

    # mp求解启发项，是把所有delta不为0【需要去完成】的任务都计算的
    def mp_solver(self):
        """
        Args:
        n = 4
        deltas=[9,8,6,2]
        relation_dict = {"ss":[(2,3),(1,2)],"es":[],"ee":[(0,2),(2,3)],"se":[(3,2),(0,1)]} #(0,1)<=>x_0<x_1
        
        Return:
        start time list
        """
        # 获取任务的 remain delta
        self.task_remain_deltas = [task.DFA.nodes[task.q_current]["distance"] for _, task in self.tasks.items()]
        logger.info(f"任务的剩余时间: {self.task_remain_deltas}")
        logger.info(f"任务的约束: {self.cascade_constraints}")

        return solution(self.N, self.task_remain_deltas, self.cascade_constraints)

################################################################
###################### atom发布与更新 ###########################
################################################################

    def add_to_shelves(self):
        # 清空 options list
        with self.rw_lock.gen_wlock():  # 生成写锁
            self.options_list.clear()
        self.task_index_options_list.clear()

        area_options_list = defaultdict(list)

        x_start_list = self.mp_solver()
        price_list = self.pricing(x_start_list)
        
        for task_label, task in self.tasks.items():
            if task_label in self.task_status["finished"] + self.task_status["assigned"]:
                continue
            # form：自动机状态的列表
            new_q_states = list(task.DFA.successors(task.q_current))
            
            # 上架到所有的竞品区
            for q_state in new_q_states:
                if q_state == task.q_current:
                    continue  # 不要走回头路
                
                # 检查合法性
                is_start = task.q_current == task.DFA.graph["initial"]
                is_end = q_state == task.DFA.graph["accept"]
                if not self.check_atomic_constraints(q_state, is_start, is_end, task_label, self.cascade_constraints):
                    continue
                
                if is_start:
                    logger.info(f"任务 {task_label}'s start atom prepare to broadcast")
                if is_end:
                    logger.info(f"任务 {task_label}'s end atom prepare to broadcast")
                
                guard = task.DFA.edges[task.q_current, q_state]["guard"]
                if guard:
                    area_to_broadcast = self.label_to_position(guard[0])
                else:
                    continue
                
                logger.info(f"任务 {task_label} 的 options 已更新{area_to_broadcast}")
                for area in area_to_broadcast:
                    new_option = Option(
                        q_state=q_state,
                        position=area,
                        benefit=price_list[int(task_label)],
                        task_label=task_label,
                    )

                    # 把task - option的对应关系加入到task_index_options_list
                    if task_label not in self.task_index_options_list:
                        self.task_index_options_list[task_label] = [new_option.option_id]
                    else:
                        self.task_index_options_list[task_label].append(
                            new_option.option_id
                        )
                        
                    # TODO: 把 area - option的对应关系加入到area_option_list
                    # 我们的打包，希望不仅仅是在定价、bid阶段，
                    # 是否需要在完成了所有的option时，才去发起flag？ 有好有坏
                    # 给option 加一个properties
                    if area not in area_options_list:
                        area_options_list[area] = [new_option]
                    else:
                        area_options_list[area].append(new_option)
                        
                    with self.rw_lock.gen_wlock():  # 生成写锁
                        self.options_list[new_option.option_id] = new_option

                    logger.info(f"Atom ++ {str(new_option)}")
                    
        # 尝试打包，但是工作量有点大
        # packaged_option_list = self.package_options(area_options_list)

        # with self.rw_lock.gen_wlock():  # 生成写锁
        #     for new_option in packaged_option_list:
        #         self.options_list[new_option.option_id] = new_option

        #         logger.info(f"Atom ++ {str(new_option)}")

                # TODO:
                # 要更仿真一点，就要让机器人根据感知范围搜索任务，然后根据收益和距离来竞标
                # 但是我感觉队列会更方便一点，直接按照距离来区分可见的权限就很简单
                # 这样的话，线程锁是不是就很必要了？ -> Yes

            # logger.info(f"任务 {task_label} 的 options 已更新")
            # 以及自动机的类型，state_based 是否有具体的定义
    
    def package_options(self, area_options_list):
        # 为每个区域的option打包
        packaged_option_list = []
        for area, options in area_options_list.items():
            if len(options) == 1:
                packaged_option_list.append(options[0])
            else:
                # 为每个区域的option打包
                new_option = copy.copy(options[0])
                new_option.benefit = sum([o.benefit for o in options])
                new_option.elements = [o.option_id for o in options]
            
                logger.info(f"Option for area {area} 已打包")
                packaged_option_list.append(new_option)
        return packaged_option_list

    def finished_option_update(self, finished_option_id: list[str]):
        """option级别的更新

        Args:
            finished_option_id (list[str]): _description_
        """
        logger.info(f"option {finished_option_id} 已完成")
        
        # 之前的bid数据都无效了，所以直接清空bid队列 - > 所以bid选取优先级队列就可以了，因为删除操作涉及的因素太多了 任务进度的更新+robot位置的更新
        # 这里可以直接替换，因为这个队列只在类内调用

        for option_id in finished_option_id:
            task_label, q_state, _ = option_id.split("_")
            
            # 先把任务的状态更新了
            self.task_status["assigned"].remove(task_label)

            # 找到对应的任务，并在DFA上跳转一步，
            task = self.tasks[task_label]
            if q_state == task.q_accept:
                logger.info(f"task {task_label} finished")
                self.task_status["finished"].append(task_label)
                if len(self.task_status["finished"]) == self.N:
                    self.complete_all_tasks = True
                    logger.info("All task have finished")
                    return
                
                self.update_constraints(task_label=task_label, is_start=False, is_end=True)
            else:
                # 这里转移之后的状态，一定不是initial状态
                if task.q_current == task.DFA.graph["initial"]:
                    logger.info(f"task {task_label} started")
                    self.update_constraints(task_label=task_label, is_start=True, is_end=False)

            task.q_current = q_state


################################################################
###################### auction #################################
################################################################

    def pick_over_multi(self, num: int):
        # 确保在一次pick over中，一个任务只能被选取一次
        executing_tasks = []
        assigned_robots = []

        # 用作什么计数呢？
        bid_num = 1

        while bid_num <= num:
            if self.task_bid_p_queue.empty():
                # logger.info("当前没有出价")
                return
            winner_bid_value, winner_bid = self.task_bid_p_queue.get()
            if (
                winner_bid.task_id in executing_tasks
                or winner_bid.robot_id in assigned_robots
            ):
                continue  # 去掉一个任务中重复的option，并且避免一个机器人中重复的option
            logger.info(
                f"--{bid_num} th-- : {winner_bid}"
            )
            self.assign_option(winner_bid)
            executing_tasks.append(winner_bid.task_id)
            assigned_robots.append(winner_bid.robot_id)
            bid_num += 1
            
        # 删除所有竞标数据
        logger.info("清空bid队列")
        self.task_bid_p_queue = PriorityQueue() 
        self.bids_backup = {}
        # 不仅要清空已经处理的bid消息，还要清空massage_queue里的bid消息
        while not self.message_queue.empty():
            self.message_queue.get()
            


################################################################
###################### 任务分配 ################################
################################################################

    def assign_option(self, bid: Bid):
        # 添加bid到assign_queue
        self.assign_queue.put(bid)
        # 发送信号给对应的机器人
        self.event_list[bid.robot_id].set()
        logger.info(f"发送信号: {bid}")
        # 阻塞直到收到回信
        logger.info(f"等待机器人 {bid.robot_id} 的回信")
        self.answer_event.wait()
        logger.info(f"机器人 {bid.robot_id} 已回信")
        self.answer_event.clear()
        
        # assign 完了之后要及时更新options
        # 首先下架当前任务的所有options
        with self.rw_lock.gen_wlock():  # 生成写锁
            for del_option_id in self.task_index_options_list[bid.task_id]:
                del self.options_list[del_option_id]  # NOTE del的用法

        self.task_index_options_list[bid.task_id] = []
        # task 的状态更新
        self.task_status["assigned"].append(bid.task_id)


##################################################################################
################################ Tools ###########################################
##################################################################################

    def pricing(self, x_start_list):
        # 为可以拍卖的任务定价
        price_list = []
        for i in x_start_list:
            price_list.append(self.price_umax * math.exp(-1 * self.price_alpha * i))
        logger.info(f"任务定价完成: {price_list}")
        return price_list

    def label_to_position(self, label):
        pos_list = []
        for node, label_of_node in self.ts.regions.items():
            if label_of_node == label:
                pos_list.append(node)
        return pos_list

##################################################################################
######################## 通信相关的函数 ###########################################
##################################################################################

    def handle_bid_message(self, bid: Bid):
        """
        bid_message的类型：
        由机器人发给manager，包含了机器人的id、option_id、bid，格式： {task_id: {bid: robot_id}}
        """
        # 用来收集来自机器人的bid信息
        if bid.robot_id not in self.bids_backup.keys():
            # logger.info(f"收到新的竞标信息: {bid}")
            # 如果第一个元素相等，则会比较第二个！
            # 综上，还是把bid函数放到机器人里比较靠谱
            # 优先级队列：首先弹出优先级最小（高）的元素
            self.task_bid_p_queue.put((-1*bid.bid, bid))
            self.bids_backup[bid.robot_id] = [bid.option_id]
        elif bid.option_id in self.bids_backup[bid.robot_id]:
            return
        else:
            # logger.info(f"收到新的竞标信息: {bid}")
            self.task_bid_p_queue.put((-1*bid.bid, bid))
            self.bids_backup[bid.robot_id].append(bid.option_id)

    def handle_flag(self, flag: str):
        logger.info(f"收到flag: {flag}")
        # 任务完成后，更新任务进度
        # 正确: 从 "机器人 1 发送flag: Robot-1 completed option 1_0_(7, 8)" 中提取出option id
        finished_option_id = re.search(r"option (\S+_\(\d+, \d+\))", flag).group(1)
        if not finished_option_id:
            logger.info("No option id found in flag")
            return

        self.finished_option_update([finished_option_id])
        # logger.info(f"option {finished_option_id} 已完成")

##################################################################################
################## 周期性更新相关的函数 ###########################################
##################################################################################

    # 有机器人竞标的时候，就意味着有人能满足这个任务，这个只是用来使得更早的options
    def update_bids_benefits(self):
        # 避免同时取出和清空队列，使用新的入队逻辑时更新优先级
        new_queue = PriorityQueue()

        while not self.options_list.empty():
            item = self.task_bid_p_queue.get()
            if isinstance(item, tuple) and len(item) == 2:
                value, bid = item
            else:
                logger.info(f"Unexpected item in queue: {item}")
            value, bid = item
            # 直接更新优先级值
            updated_value = value + self.delta
            logger.info(f"Updating priority of {str(bid)} to {updated_value:.2e}")
            # 将更新后的bid重新入队
            new_queue.put((updated_value, bid)) # BUG bid内部的value没改！！

        # 用新的队列替换旧队列
        self.task_bid_p_queue = new_queue
        logger.info("所有bid的优先级已更新")

    def update_options_benefits(self):
        # 更新所有option的收益
        with self.rw_lock.gen_wlock():
            for option_id, option in self.options_list.items():
                option.benefit += self.delta
                logger.info(f"Option {option_id} 的收益已更新为 {option.benefit:.2e}")