# pylint: disable = E1101, E0611, C0103. c0116, c0303, E0402, c0114, c0115, w0511, r0902, r0913, w1203, c0411

import queue
import random
from P_MAS_TG.class_def.robotThread import RobotThread
from P_MAS_TG.class_def.task import Task
from P_MAS_TG.class_def.taskManager import TaskManager
from P_MAS_TG.class_def.transSystem import TransSystem

# from settings.default import TransSystem, robot_num, robot_initial_position, matrix, regions, n
import threading
import time
import os
from P_MAS_TG.boolean_formulas.spot.convert import parse_hoa_to_digraph
import numpy as np
from P_MAS_TG.utils.args_config import *
from P_MAS_TG.utils.args_parse import parse_arguments
from P_MAS_TG.utils.logging_config import logger
from P_MAS_TG.utils.fileops import save_to_json

from datetime import datetime
import logging
import sys
import importlib.util
from pathlib import Path


auction_num = [0]
calc_time = [0]

# import settings
def import_module_from_path(module_name, file_path):
    # 创建模块的规范
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Cannot find module {module_name} at {file_path}")

    # 从规范创建模块
    module = importlib.util.module_from_spec(spec)

    # 将模块添加到sys.modules
    sys.modules[module_name] = module

    # 执行模块
    spec.loader.exec_module(module)

    return module

# 主线程定期更新任务收益，并处理消息
def main_thread(task_manager, beginning_time, sample_interval=0.2, sample_frequency=5, assign_bid_num=3, ):
    global auction_num
    global calc_time
    task_manager.add_to_shelves()

    try:
        while not task_manager.complete_all_tasks:
            # 主线程循环
            # 原来的逻辑是：先检查完成的信号，对任务状态更新，等待0.5s，然后检查是否有来自其他线程的竞标消息，然后开始拍卖
            # 修改成 发布-接收竞标信息-然后assign的步骤，花费0.02秒之内
            # 是否要让非空闲的机器人参与拍卖？要的吧，不然会导致绕长长的远路了。
            # 检查是否有来自其他线程的flag

            # logger.info("检查是否有来自其他线程的flag")
            has_flag = False
            try:
                while True:
                    flag = task_manager.flag_queue.get_nowait()
                    has_flag = True
                    task_manager.handle_flag(flag)
                    

            except queue.Empty:
                # logger.info("flag队列为空，停止处理")
                pass

            # 在处理了全部flag之后再上架 atom
            if has_flag:
                # 统计每一次拍卖的时间，包含了上架、路径规划
                once_auction_time = time.time()
                # auction_num[0] += 1
                logger.info(f"第{auction_num[0]}次拍卖")
                task_manager.add_to_shelves()
                auction_num[0] += 1
                
                time.sleep(sample_interval*2)  # 更新完之后等待机器人的最新竞标 # 需要比一个机器人的interval长，才足够所有机器人出价

            # # 检查“定时器”，判断是否需要更新任务收益
            # end_time = time.time()
            # if end_time - start_time > args.update_options_interval:
            #     task_manager.update_options_benefits()
            #     start_time = end_time

            # 检查是否有来自其他线程的flag
            # logger.info("检查是否有来自其他线程的flag")
            # try:
            #     while True:
            #         flag = task_manager.flag_queue.get_nowait()
            #         task_manager.handle_flag(flag)
            # except queue.Empty:
            #     logger.info("flag队列为空，停止处理")
            #     pass

            # 检查是否有来自其他线程的竞标消息
            # logger.info("检查是否有来自其他线程的竞标消息")
            try:
                while True:
                    message_list_of_one_robot = task_manager.message_queue.get_nowait()
                    for message in message_list_of_one_robot:
                        task_manager.handle_bid_message(message)
                        logger.info(f"处理竞标消息 {str(message)}")

            except queue.Empty:
                pass
                
                # 当消息队列取空了之后，就会调用以下输出函数了
                # 打印竞标队列的前五个元素
                # for _, bid in list(task_manager.task_bid_p_queue.queue)[:5]:
                #     logger.info(f"当前竞标排序 {str(bid)}")

            # TODO 加一个检查是否有机器人空闲的函数
            # logger.info("开始拍卖")
            if task_manager.assign_queue.empty():
                # 检查是否有任务可以竞价
                task_manager.pick_over_multi(assign_bid_num)
                if has_flag:
                    calc_time[0] += time.time() - once_auction_time
                time.sleep(sample_interval) # TODO：这个是否需要？ 首先，加了之后就会make span会降低
        logger.info(f"规划时间：{calc_time[0]}")
        logger.info("所有任务完成，停止主线程")
        raise KeyboardInterrupt

    except KeyboardInterrupt:
        logger.info("主线程捕获到中断信号，准备停止...")

    return KeyboardInterrupt


# 主程序
def main():
    global auction_num
    global calc_time
    
    # record exp results
    datetime_now = datetime.now().strftime("%Y%m%d-%H%M%S")
    exp_name = f"{datetime_now}"
    exp_dir = os.path.join("outputs", exp_name)
    os.makedirs(exp_dir, exist_ok=True)

    # args
    args = parse_arguments()
    args_print(args, logger)
    # set_seed(42)

    # 根据传入参数的环境大小来设置变量
    settings_n = args.settings_n
    setting_file_path = Path(f"./settings/seed{args.seed}/{settings_n}/settings.py")
    
    # 导入settings模块
    try:
        logger.info(f"导入task description模块: {setting_file_path}")
        settings_cls = import_module_from_path("settings", setting_file_path)
    except Exception as e:
        logger.error(f"导入settings模块失败: {e}")
        return
    
    # 环境size
    n = settings_cls.n
    robot_num = settings_cls.robot_num
    robot_initial_position = settings_cls.robot_initial_position
    regions = settings_cls.regions
    
    task_num = settings_cls.task_num
    relation_dict = settings_cls.relation_dict
    task_index = settings_cls.task_index
    task_files_path = settings_cls.task_files_path

    logger.info(f"Environment size: {n} x {n}")
    logger.info(f"Regions: {regions}")
    logger.info(f"Initial robot positions: {robot_initial_position}")

    begging_time = time.time()

    message_queue = queue.Queue()
    assign_queue = queue.Queue()
    flag_queue = queue.Queue()

    logging.info("创建环境 ts, for each robot")
    # 创建环境 ts, for each robot
    ts = TransSystem(n, regions)

    logging.info("创建任务管理器 task_manager")
    task_manager = TaskManager(
        ts=ts,
        message_queue=message_queue,
        assign_queue=assign_queue,
        event_list=[threading.Event() for _ in range(robot_num)],
        answer_event=threading.Event(),
        flag_queue=flag_queue,
        # 计算部分都放到manager中
        price_umax=args.price_umax,
        price_alpha=args.price_alpha,

        N=task_num,
        cascade_cons=relation_dict,
    )

    # 创建任务
    # convert all the test to G
    # 需要读取的任务列表
    files = task_index

    for index in files:
        # 构造文件名（假设文件名格式是 '序号.txt'）
        file_name = f"{index}.txt"
        file_path = os.path.join(task_files_path, file_name)

        # 判断文件是否存在
        if os.path.exists(file_path):
            task = Task(DFA=parse_hoa_to_digraph(file_path))
            # task.draw_DFA()
            task_manager.tasks[str(index)] = task  # 按顺序存储 -> 按label存储

        else:
            print(f"文件 {file_name} 不存在")

    # 创建机器人
    robots = []
    for i in range(robot_num):
        robot = RobotThread(
            robot_id=i,
            position=robot_initial_position[i],
            rw_lock=task_manager.rw_lock,
            ts=ts,
            message_queue=message_queue,
            manager_option_list=task_manager.options_list,
            assign_queue=assign_queue,
            event=task_manager.event_list[i],
            answer_event=task_manager.answer_event,
            flag_queue=flag_queue,
            bid_bmax=args.bid_bmax,
            bid_beta=args.bid_beta,
            bid_lambda=args.bid_lambda,
            auction_num = auction_num,
            sample_interval=args.sample_interval,
            sample_frequency=args.sample_frequency,
        )
        robot.daemon = True
        robot.start()
        robots.append(robot)

    # 时间调度，定期更新任务收益
    # 以下其实不会执行，只能捕获被main_thread遗漏的中断信号，而main_thread执行完之后就结束了，
    # 实际上中断机器人进程的是守护进程的设置，更简单
    try:
        main_thread(task_manager=task_manager, beginning_time=begging_time, sample_interval=args.sample_interval, sample_frequency=args.sample_frequency, assign_bid_num=args.assign_bid_num)

        make_span = time.time() - begging_time
        logger.info(f"=======make span: {make_span}=======")
        
        ############################### 保存结果 ################################
        results = {}
        results["seed"] = args.seed
        results["settings_n"] = settings_n  
        results["sample"] = (args.sample_interval, args.sample_frequency)
        
        # 参数
        results["auction params"] = (args.price_umax, args.price_alpha, args.bid_bmax, args.bid_beta, args.bid_lambda)
        results["make span"] = make_span
        # results["path length"] = path_all_len
        results["plan time"] = calc_time[0]
        results["log path"] = exp_name
        
        save_to_json(results, 'results.json')
        
        

    except KeyboardInterrupt:
        # 停止所有机器人
        for robot in robots:
            robot.stop()

        for robot in robots:
            robot.join()
            # 停止机器人：当用户通过 Ctrl+C 终止程序时，机器人线程会被依次停止并结束，主线程确保所有机器人都干净退出才会结束程序，避免潜在的资源泄漏或线程问题。


if __name__ == "__main__":
    main()
