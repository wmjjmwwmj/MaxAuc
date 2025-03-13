
from P_MAS_TG.boolean_formulas.spot.convert import parse_hoa_to_digraph

import os
import time
# from settings.default_fix_small import robot_initial_position, regions, n, relation_dict

from P_MAS_TG.class_def.multi_ts import MultiTS
from P_MAS_TG.class_def.multi_PBA import MultiPBA
from P_MAS_TG.class_def.multi_DFA import MultiDFA

# logger import 在 argparse 之后才可以正常输出 args_print
from P_MAS_TG.utils.args_config import *
from P_MAS_TG.utils.logging_config import logger
import argparse

import pickle
from P_MAS_TG.class_def.task import Task
from pathlib import Path
from P_MAS_TG.utils.import_module import import_module_from_path
from P_MAS_TG.utils.random_picking import select_points
from P_MAS_TG.utils.fileops import save_to_json

def parse_arguments():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument(
        "--settings_n",
        default="4.2.2",
        type=str,
        help="Choose the settings source.",
    )
    
    parser.add_argument(
        "--seed",
        default=42,
        type=int,
        help="Choose the seed for randomly generate settings.",
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
    # set_seed(42) # TODO 在这里固定seed有用吗，哪里还有随机的地方吗？
    
    # args
    args = parse_arguments()
    args_print(args, logger)
    
    # 根据传入参数的环境大小来设置变量
    settings_n = args.settings_n
    setting_file_path = Path(f"./settings/seed{args.seed}/{settings_n}/settings.py")
    
    # 导入settings模块
    try:
        logger.info(f"导入task description模块: {setting_file_path}")
        settings_cls = import_module_from_path(setting_file_path)
    except Exception as e:
        logger.error(f"导入settings模块失败: {e}")
        return
    
    # 环境size
    n = settings_cls.n
    robot_initial_position = settings_cls.robot_initial_position
    regions = settings_cls.regions
    
    relation_dict = settings_cls.relation_dict
    task_index = settings_cls.task_index
    task_files_path = settings_cls.task_files_path

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
    min_cost, path_all_len = multi_pba.optimal_path()
    
    
    logger.info(f"最短路径规划完毕，耗时 {time.time() - optimal_path_calc_time:.2f}s")
    plan_time = time.time() - start_time
    logger.info(f"总耗时 {plan_time:.2f}s")
    
    
    ############################### 保存结果 ################################
    results = {}
    results["seed"] = args.seed
    results["settings_n"] = settings_n  
    
    results["make span"] = min_cost
    results["path length"] = path_all_len
    
    results["plan time"] = plan_time
    results["log path"] = last_folder
    
    save_to_json(results, 'results.json')
    

# 判断当前模块是否是主模块
if __name__ == "__main__":
    main()