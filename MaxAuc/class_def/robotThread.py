# pylint: disable = E1101, E0611, C0103, c0116, c0303, E0402, c0114
import threading
import time
from queue import Queue
from ..discrete_plan import dijkstra_plan_networkX
from .option import Option
from .bid import Bid
from ..utils.logging_config import logger
import re
import math


# 定义机器人类
class RobotThread(
    threading.Thread
):  # 尽管主线程只读机器人线程的变量，由于位置更新一次涉及多个变量，所以还是需要锁的
    def __init__(
        self,
        robot_id,
        position,
        rw_lock,
        ts,
        message_queue,
        manager_option_list,
        assign_queue,
        event,
        answer_event,
        flag_queue,
        bid_bmax,
        bid_beta,
        bid_lambda,
        auction_num,
        sample_interval=0.2,
        sample_frequency=5,
    ):
        super().__init__(name=f"Robot-{robot_id}")
        
        # 进程调度相关
        self.daemon = True
        self.rw_lock = rw_lock
        self.message_queue = message_queue
        self.assign_queue = assign_queue
        self.flag_queue = flag_queue
        ## 事件
        self.event = event
        self.answer_event = answer_event
        
        # 机器人settings
        self.robot_id = robot_id
        self.ts = ts
        self.sense = 3  # 类似半径
        self.sample_interval = sample_interval
        self.sample_frequency = sample_frequency   
        
        self.v_x = 1 / sample_frequency
        self.v_y = 1 / sample_frequency
        
        # 机器人状态
        self.running = True
        self.executing = False
        self.executing_progress = 0
        self.moving = False
        
        # 机器人bid
        self.manager_option_list = manager_option_list
        self.bid_list = []
        self.bid_bmax = bid_bmax
        self.bid_beta = bid_beta
        self.bid_lambda = bid_lambda
        
        # 机器人路径规划
        
        self.option_id_list = []
        self.current_option_id = None
        self.path_planning = []
        self.toward_to = None
        
        self.position = position
        
        # 机器人的最后一个目标点
        self.final_drop_point = position
        self.path_backup = [self.position]
        
        self.robot_auction_num = -1
        self.auction_num = auction_num
        
        # 这个函数实际上是由mainThread调用的，log会被写到mainThread的log文件中

        # TODO: whether is running, 若有机器人挂了，需要把它的任务分配给其他人
        # TODO: energy
        
############################################################################################
####################### pipeline for robot thread ##########################################
############################################################################################

    def run(self):
        logger.info(f"in {self.position}")
        while self.running:
            # 检查是否有任务可以竞价
            # bid
            time.sleep(self.sample_interval)
            # 以下根据状态分类讨论
            ## 正在移动
            if self.moving:
                delta_x = self.v_x *  self.classify_input(self.toward_to[0] - self.position[0])
                delta_y = self.v_y *  self.classify_input(self.toward_to[1] - self.position[1])
                self.position = (round(self.position[0] + delta_x, 2), round(self.position[1] + delta_y, 2))
                logger.info(f"---in {self.position}, wish to {self.toward_to}")
                if self.position == self.toward_to:
                    logger.info(f"机器人 {self.robot_id} 移动到 {tuple(map(int, self.position))}, for option: {self.current_option_id}\n")
                    if self.path_planning:
                        self.toward_to = self.path_planning.pop(0)
                        logger.info(f"---wish to {self.toward_to}")
                    else:
                        self.position = self.toward_to
                        self.moving = False
                        self.toward_to = None
                        self.executing = True
                        logger.info(f"机器人 {self.robot_id} 开始执行option {self.current_option_id}\n")
            
            ## 正在执行
            if self.executing:
                self.executing_progress += 1
                logger.info(f"---load in {self.executing_progress / self.sample_frequency * 100} %")
                if self.executing_progress >= self.sample_frequency:
                    self.executing = False
                    self.executing_progress = 0
                    logger.info(f"机器人 {self.robot_id} 移动到 {tuple(map(int, self.position))}, 完成了 option: {self.current_option_id}\n")
                    # logger.info(f"机器人 {self.robot_id} 完成option {self.current_option_id}\n")
                    self.send_flag()
            
            # 如果当前option完成了，可以开始下一个option
            if not self.executing and not self.moving and self.option_id_list:
                self.current_option_id = self.option_id_list.pop(0)
                self.execute_bid(self.current_option_id)
                    
            if self.event.is_set():
                if not self.assign_queue.empty():
                    bid = self.assign_queue.get()
                    
                    # 清除事件，准备下一次循环
                    self.event.clear()
                    self.answer_event.set()
                    # 机器人重新参与拍卖
                    self.robot_auction_num = -1
                    self.store_option(bid.option_id) # 设计的是在执行的时候被阻塞了
                    
                    # 及时更新状态，不影响下一次出价
                    if self.current_option_id is None:
                        self.current_option_id = self.option_id_list.pop(0)
                        self.execute_bid(self.current_option_id)
                else:
                    logger.info(f"机器人分配队列为空，无法获取option\n")
            else:
                pass
            
            self.evaluate_available_options()
            
    def evaluate_available_options(self):
        if self.robot_auction_num == self.auction_num[0]:
            # logger.info(f"当前竞价场次{self.auction_num[0]}, 上次参与 {self.robot_auction_num}")
            return
        else:
            logger.info(f"当前竞价场次{self.auction_num[0]}, 上次参与 {self.robot_auction_num}")
            self.robot_auction_num = self.auction_num[0]

        option_list = []
        with self.rw_lock.gen_rlock():  # 生成读锁
            option_list = self.manager_option_list.copy()

        # logger.info(f"机器人 {self.robot_id} 开始评估可竞标的option{option_list}\n")
        # logger.info(f"机器人 {self.robot_id} 开始评估可竞标的option\n")
        for option_id, option  in option_list.items():
            if option.option_id in self.bid_list:
                continue
            # if self.moving:
            #     distance = self.dest_distance_to_option(option)
            # else:
            #     distance = self.current_distance_to_option(option)
            
            
            # 考虑上到达 final drop 要花的时间
            # 因为到达target 可能会很久
            # distance = self.distance_of_final_drop_points_to_option(option)  + self.current_distance_to_point(self.final_drop_point)
            distance = self.distance_of_final_drop_points_to_option(option)  + len(self.path_planning)
            
            # logger.info(f"--- distance {distance}")
            # if distance < self.sense or option.benefit > 3:
            if True:
                # 机器人把自己的所有bid都放到一起，然后再发送给manager
                prepare_bid = Bid(
                    robot_id=self.robot_id,
                    option_id=option_id,
                    bid_value = self.calc_bid_value(option.benefit, distance),
                    task_id=option.task_label,
                    position=option.position,
                )

                self.bid_list.append(prepare_bid)

        if not self.bid_list:
            # logger.info(f"机器人 {self.robot_id} 没有找到可竞标的option\n")
            return
        self.send_bid()


############################################################################################
####################### execution for robot thread #########################################
############################################################################################

############################################################################################
####################### tools / functions for robot thread #################################
############################################################################################
    
    def parse_position(self, option_id):
        match = re.search(r"\((\d+),\s*(\d+)\)", option_id)
        if match:
            tuple_values = (int(match.group(1)), int(match.group(2)))
            return tuple_values
        else:
            print("No match found.")
    
    def distance_of_final_drop_points_to_option(self, task):
        dest_pose = self.final_drop_point

        return ( abs((dest_pose[0] - task.position[0])) + abs((dest_pose[1] - task.position[1])) )

    # 判断正负
    def classify_input(self, value):
        return (value > 0) - (value < 0)



############################################################################################
####################### 暂时不用的函数 ######################################################
############################################################################################

    def achieve_option(self, option: Option):
        self.current_option = option
        self.executing = True
        self.execute_option(option)
        
    # Calculate the Euclidean distance between the robot's position and a task's position.
    def current_distance_to_point(self, point):
        # return (
        #     (self.position[0] - task.position[0]) ** 2
        #     + (self.position[1] - task.position[1]) ** 2
        # ) ** 0.5
        return ( abs((self.position[0] - point[0])) + abs((self.position[1] - point[1])) )
    
    def dest_distance_to_option(self, task):
        if self.path_planning:
            dest_pose = self.path_planning[-1]
        else:
            dest_pose = self.toward_to
        return ( abs((dest_pose[0] - task.position[0])) + abs((dest_pose[1] - task.position[1])) )


    def execute_bid(self, option_id: str):
        # 主要是切换状态，规划路径，然后设一个初状态
        self.current_option_id = option_id
        # print(f"机器人 {self.robot_id} 正在执行option {self.current_option}")
        # logger.info(f"机器人 {self.robot_id} 开始执行option {self.current_option_id}\n")
        # 获取option的 path planning
        logger.info("--- 进入执行阶段")
        position = self.parse_position(option_id)
        self.ts.graph["accept"] = [position]
        if self.moving:
            self.ts.graph["initial"] = self.path_planning[-1]
        else:
            self.ts.graph["initial"] = self.position
        opt_tar, opt_path, min_cost = dijkstra_plan_networkX(self.ts)

        # corner case: 机器人就在目标位置上，直接execute任务的情况
        if len(opt_path) == 1:
            self.executing = True
            logger.info(f"机器人 {self.robot_id} 开始执行option {self.current_option_id}\n")
            return
        
        # 机器人开始移动
        self.path_planning.extend(opt_path[1:])
        self.path_backup.extend(opt_path[1:])
        self.toward_to = self.path_planning.pop(0)
        self.moving = True

    def store_option(self, option_id):
        self.option_id_list.append(option_id)
        self.final_drop_point = self.parse_position(option_id)
        logger.info(f"机器人 {self.robot_id} 入库option {option_id}\n")
        
        


    def send_flag(self):
        message = f"Robot-{self.robot_id} completed option {self.current_option_id}"
        self.flag_queue.put(message)  # 将消息发送到主线程
        # print(f"机器人 {self.robot_id} 发送flag: {message}\n")
        logger.info(f"机器人 {self.robot_id} 发送flag: {message}\n")
        self.current_option_id = None

    def send_bid(self):
        self.message_queue.put(self.bid_list)

        # print(f"机器人 {self.robot_id} 发送bid: {'; '.join(str(bid) for bid in self.bid_list)}\n")
        logger.info(f"机器人 {self.robot_id} 发送bid:\n" + "\n".join(str(bid) for bid in self.bid_list))
        self.bid_list = []
        

    def stop(self):
        self.running = False
        
    def calculate_path (self):
        length = 0
        pre_x, pre_y = self.path_backup[0]
        for x, y in self.path_backup[1:]:
            length += abs(x - pre_x) + abs(y - pre_y)
            pre_x, pre_y = x, y
        return length
    
    def calc_bid_value(self, reward, cost):
        return self.bid_bmax * (reward ** self.bid_beta / (1 + math.exp(self.bid_lambda * cost)))
