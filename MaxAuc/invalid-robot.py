import random

class Robot:
    def __init__(self, robot_id, position, single_robot_graph):
        """
        初始化机器人对象
        
        :param robot_id: 机器人的唯一标识符
        :param position: 机器人的初始位置，使用 (x, y) 坐标表示
        """
        self.robot_id = robot_id
        self.position = position  # 机器人的位置 (x, y)
        self.options = []  # 分配给机器人的任务列表
        self.current_option = None  # 当前任务
        self.energy = 100  # 机器人的初始能量
        self.single_robot_graph = single_robot_graph
        
        self.
    
    def distance_to_option(self, option):
        """
        计算机器人当前位置到任务位置的距离
        
        :param task: 任务的目标位置 (x, y)
        :return: 距离
        """
        # 其实我希望这个auction发布的时候，可以根据地形/障碍物分布，携带着一些“路径长度”信息，这样机器人就可以根据这个信息来决定出价
        # 但是就会有点像是wifi，乱发信号，不是很节约
        # return ((self.position[0] - option[0]) ** 2 + (self.position[1] - task[1]) ** 2) ** 0.5
        
        # 选择图的转移距离为cost
        

    def bid_for_task(self, task):
        """
        计算机器人对某个任务的出价。出价可以基于到任务的距离，能量等因素。
        
        :param task: 任务的目标位置 (x, y)
        :return: 该机器人的出价值
        """
        distance = self.distance_to_task(task)
        # 假设出价和距离成正比，距离越短，出价越低
        bid = distance + random.uniform(0, 1)  # 随机值用来防止出价相同
        return bid

    def assign_task(self, task):
        """
        给机器人分配一个任务
        
        :param task: 任务的目标位置 (x, y)
        """
        self.tasks.append(task)
        if not self.current_task:
            self.current_task = task
        print(f"机器人 {self.robot_id} 分配到任务 {task}")

    def execute_task(self):
        """
        执行当前任务。机器人会向任务位置移动并完成任务。
        """
        if not self.current_task:
            print(f"机器人 {self.robot_id} 没有当前任务")
            return

        print(f"机器人 {self.robot_id} 正在执行任务 {self.current_task}")
        # 移动到任务位置
        self.move_to(self.current_task)
        # 任务完成后，清除当前任务
        self.tasks.remove(self.current_task)
        self.current_task = None
        print(f"机器人 {self.robot_id} 完成了任务")

    def move_to(self, target_position):
        """
        将机器人移动到目标位置
        
        :param target_position: 目标位置 (x, y)
        """
        print(f"机器人 {self.robot_id} 从 {self.position} 移动到 {target_position}")
        self.position = target_position

    def __repr__(self):
        return f"Robot(id={self.robot_id}, position={self.position}, energy={self.energy})"
