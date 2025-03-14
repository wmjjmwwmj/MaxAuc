"""_summary_

Returns:
    _type_: _description_
"""


class Option:  # pylint: disable=too-few-public-methods
    """_summary_"""

    def __init__(self, benefit, q_state, position, task_label, elements = None):
        self.benefit = benefit
        
        # 以下只用 option_id 就可以
        self.q_state = q_state
        self.position = position
        self.task_label = task_label
        self.option_id = f"{task_label}_{q_state}_{position}"
        
        # 包含的是option id的列表
        self.elements = elements

    def __str__(self):
        return f"task_{self.task_label}_in_q{self.q_state} with benefit {self.benefit:.2f}, in position {self.position}{'.' if self.elements is None else f' with elements {self.elements}'}"
