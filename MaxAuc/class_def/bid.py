class Bid:
    def __init__(self, robot_id, option_id, bid_value, task_id, position):
        self.robot_id = robot_id
        self.option_id = option_id  # 这里可以链接到option的properties
        self.bid = bid_value
        self.task_id = task_id
        self.position = position

    def __str__(self): # 把类的实例转换成字符串时的输出格式
        return f"robot {self.robot_id} bid {self.bid:.3e}, for option {self.option_id}"
    
    def __lt__(self, other):
        # 比较两个 Bid 实例，以 bid 值进行比较
        return self.bid < other.bid