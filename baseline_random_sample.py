
from P_MAS_TG.boolean_formulas.spot.convert import parse_hoa_to_digraph

import os
import time
# from settings.default_fix_small import robot_initial_position, regions, n, relation_dict

from P_MAS_TG.class_def.multi_ts import MultiTS
from P_MAS_TG.class_def.multi_PBA import MultiPBA
from P_MAS_TG.class_def.multi_DFA import MultiDFA

from P_MAS_TG.utils.logging_config import logger
from P_MAS_TG.utils.args_config import *
import argparse
import pickle
from P_MAS_TG.class_def.task import Task
from pathlib import Path
from P_MAS_TG.utils.import_module import import_module_from_path
from P_MAS_TG.utils.random_picking import select_points

def parse_arguments():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument(
        "--settings_n",
        default="4.2.2",
        type=str,
        help="Choose the environment size.",
    )
    
    # 添加一个新参数，检测是否存在该参数
    parser.add_argument(
        "-T",
        action="store_true",  # 如果该参数存在，值为 True，否则为 False
        help="If provided, execute after TS built.",
    )
    
    # 添加一个新参数，检测是否存在该参数
    parser.add_argument(
        "-D",
        action="store_true",  # 如果该参数存在，值为 True，否则为 False
        help="If provided, execute after DFA built.",
    )
    
    # 添加一个新参数，检测是否存在该参数
    parser.add_argument(
        "-P",
        action="store_true",  # 如果该参数存在，值为 True，否则为 False
        help="If provided, execute after PBA built.",
    )
    

    parser.add_argument(
        "--history",
        default=None,
        type=str,
        help="If provided, execute after PBA built.",
    )

    args = parser.parse_args()

    return args


def main():
    # 
    set_seed(42) # TODO 在这里固定seed有用吗，哪里还有随机的地方吗？
    
    # args
    args = parse_arguments()
    args_print(args, logger)
    
    # 根据传入参数的环境大小来设置变量
    settings_n = args.settings_n
    # setting_file_path = Path(f"./settings/n={settings_n}/settings.py")
    
    # 环境size
    n = int(settings_n.split('.')[0])  
    
    task_num = int(settings_n.split('.')[2])
    task_files_path = Path(f"./settings/task_lib/{task_num}/")
    task_description_file_path = task_files_path / 'description.py'
    # 导入settings模块
    try:
        logger.info(f"导入task description模块: {task_description_file_path}")
        task_settings_cls = import_module_from_path(task_description_file_path, "task_settings")
    except Exception as e:
        logger.error(f"导入settings模块失败: {e}")
        return
    
    ap_num = task_settings_cls.ap_num
    relation_dict = task_settings_cls.relation_dict
    task_index = task_settings_cls.task_index
    
    
    # 从 settings_cls 还原参数
    robot_num = int(settings_n.split('.')[1])
    robot_initial_position = select_points(n, robot_num)
    
    regions = {point: f"r{i + 1}" for i, point in enumerate(select_points(n, ap_num))}

    logger.info(f"Environment size: {n} x {n}")
    logger.info(f"Regions: {regions}")
    logger.info(f"Initial robot positions: {robot_initial_position}")

    ##############################
    # 获得 outputs中，字典序的最后一个文件夹的文件地址
    # 设置输出目录的路径
    output_dir = 'outputs'

    # 获取outputs目录中所有文件夹（不包括文件）
    folders = [f for f in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, f))]

    # 对文件夹名称按字典序排序
    folders_sorted = sorted(folders)

    # 获取字典序最后一个文件夹的路径
    if folders_sorted:
        last_folder = folders_sorted[-1]
        history_folder = folders_sorted[-2]
        
        last_folder_path = Path(output_dir) / last_folder 
        history_folder_path = Path(output_dir) / history_folder
        
        logger.info(f"字典序最后一个文件夹的路径: {last_folder_path}")
    else:
        logger.info("没有找到文件夹")
    
    if args.history:
        history_folder_path = Path(output_dir) / args.history
        logger.info(f"指定的历史文件夹路径: {history_folder_path}")
    
    #######################################################
    start_time = time.time()
    
    if args.T or args.D or args.P:
        logger.info(f"从文件{history_folder_path}加载 MultiTS 实例")
        with open(history_folder_path / 'multi_ts.pkl', 'rb') as f:
            multi_ts = pickle.load(f)
    else:
        multi_ts = MultiTS(N=n, regions=regions, robot_initial_pos=robot_initial_position)
        logger.info("多机器人转移系统建模完毕，耗时 {:.2f}s".format(multi_ts.consume_time))
        logger.info("MultiTS has {} nodes, {} edges".format(len(multi_ts.nodes), len(multi_ts.edges)))


        # 当你从 pickle 文件加载类的实例时，Python 需要能够找到类的定义。如果类的定义发生了改变（例如类名或属性名），恢复时可能会出错。
        with open(last_folder_path / 'multi_ts.pkl', 'wb') as f:
            pickle.dump(multi_ts, f)
    
    ####################################################################################
    
    if args.D or args.P:
        logger.info(f"从文件{history_folder_path}加载 MultiDFA 实例")
        with open(history_folder_path / 'multi_dfa.pkl', 'rb') as f:
            multi_dfa = pickle.load(f)
    else:
    
        ## convert all the test to G
        DFA_list = {} 
        
        for index in task_index:
            file_name = f"{index}.txt"
            file_path = os.path.join(task_files_path, file_name)
            
            # 判断文件是否存在
            if os.path.exists(file_path):
                task = Task(DFA=parse_hoa_to_digraph(file_path))
                DFA_list[str(index)] = task.DFA.copy()

        logger.info("任务转换完毕, 共有{}个任务".format(len(task_index)))
        
        logger.info("开始构造MultiDFA=====================")
        multi_dfa = MultiDFA(DFA_list = DFA_list, cascade_constraints = relation_dict)
        logger.info("MultiDFA 构造完毕，耗时 {:.2f}s".format(multi_dfa.consume_time))
        logger.info("MultiDFA has {} nodes, {} edges".format(len(multi_dfa.nodes), len(multi_dfa.edges)))

        with open(last_folder_path / 'multi_dfa.pkl', 'wb') as f:
            pickle.dump(multi_dfa, f)

    ##############################
    # 自动机叉乘 for baseline only
    if args.P:
        logger.info(f"从文件{history_folder_path}加载 MultiPBA 实例")
        with open(history_folder_path / 'multi_pba.pkl', 'rb') as f:
            multi_pba = pickle.load(f)
    else:
        logger.info("开始构造乘积自动机=====================")
        multi_pba = MultiPBA(multi_ts, multi_dfa)
        logger.info("乘积自动机构造完毕，耗时 {:.2f}s".format(multi_pba.consume_time))
        logger.info("MultiPBA has {} nodes, {} edges".format(len(multi_pba.nodes), len(multi_pba.edges)))
        
        with open(last_folder_path / 'multi_pba.pkl', 'wb') as f:
            pickle.dump(multi_pba, f)
    
    optimal_path_calc_time = time.time()
    
    multi_pba.optimal_path()
    
    logger.info(f"最短路径规划完毕，耗时 {time.time() - optimal_path_calc_time:.2f}s")
    
    logger.info(f"总耗时 {time.time() - start_time:.2f}s")
        

# 判断当前模块是否是主模块
if __name__ == "__main__":
    main()