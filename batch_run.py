import subprocess
import os
import json
from P_MAS_TG.utils.fileops import save_to_json, read_json, empty_file
import numpy as np
import concurrent.futures
from files_backup import backup_local
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict

def run_command(command):
    # 调用子进程运行命令，并等待命令执行完成
    # subprocess.run() 是最常用的阻塞调用，它会等待子进程执行完成，然后再返回结果。
    # check=True：这是 subprocess.run() 的一个重要参数。如果命令返回非零的退出代码，subprocess.run() 会抛出 subprocess.CalledProcessError 异常。这样你就可以捕获异常并处理错误。
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    
    # 打印子进程的输出和错误信息
    print("标准输出：", result.stdout)
    print("标准错误：", result.stderr)
    
    # 返回进程的返回码
    return result.returncode

def batch_run(script, param_combinations):
    """
    批量运行带参数的脚本，并保存结果。
    """

    # 创建一个 ProcessPoolExecutor，设置最大工作进程数为 1，确保任务按顺序执行
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        # 提交任务并按顺序获取结果
        for params in tqdm(param_combinations, desc="Processing Tasks", unit="task"):
            command = ['python', script_path] + [str(param) for param in params]
            future = executor.submit(run_command, command)
            future.result()  # 等待当前任务完成，确保按顺序执行


def generate_param_combinations(settings_list, num_seeds = 20, additional_params = [""]):
    """
    生成参数组合。
    """
    # 生成参数组合
    params = []
    for additional_param in additional_params:
        # 遍历所有 settings 和每个 setting 的种子
        for setting in settings_list:
            for seed in range(42, 42 + num_seeds):
                params.append( ['--seed', seed, "--settings_n", setting] + additional_param)
    
    return params

def average_and_std(data):
    """
    计算数据的平均值和标准差。
    """
    return (sum(data) / len(data), np.std(data))

if __name__ == '__main__':
    
    # 每个都要跑两遍，一遍抓make span，一遍抓plan time
    # run_twice = True # TODO 先不跑plan time了，因为差别不大

    # 其实只要删除就可以了
    try:
        empty_file("results.json")
        empty_file("batch_results.json")
        
        script_path = "auction_mp.py"
        settings_list = [
             "6.2.3",
            ]
        
        # additional_params = [["--sample_interval", 0.003, "--sample_frequency", 1],] # ["--sample_interval", 0.01, "--sample_frequency", 100]
        additional_params = [["--sample_interval", 0.003, "--sample_frequency", 1],]
        param_combinations = generate_param_combinations(settings_list, 20, additional_params)
        batch_run(script_path, param_combinations)
        raise KeyboardInterrupt

    except KeyboardInterrupt:
        
        # 加载结果
        results = read_json("results.json")
        
        all_batch_results = defaultdict(dict)
        # 根据settings_list打印结果
        # 要统计的变量
        
        for additional_param in additional_params:
            batch_results = all_batch_results[str(additional_param)]
            for setting in settings_list:
                make_span = []
                path_length = []
                plan_time = []
                batch_size = 0
                print(f"Setting: {setting}")
                
                for result in results:
                    if result["settings_n"] == setting and result["sample"] == [additional_param[1], additional_param[3]]:
                        # print(result)
                        batch_size += 1
                        make_span.append(result["make span"])
                        plan_time.append(result["plan time"])
                
                if batch_size>0:
                    batch_results[setting] = {
                        "make span": average_and_std(make_span),
                        "plan time": average_and_std(plan_time),
                        "batch size": batch_size,
                        "sample": [additional_param[1], additional_param[3]],
                        "auction params": "default"
                    }
            
        save_to_json(all_batch_results, "batch_results.json")
        
        # 直接备份到本地
        # 获取当前时间，格式化为字符串
        current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        # 拼接文件夹名称
        folder_name = f"{settings_list[-1]}_{current_time}"
        
        # 构造完整路径
        new_folder_path = os.path.join(r"D:\Paper\data_backup\RAL\auction_mp", folder_name)
        
        # 创建文件夹
        os.makedirs(new_folder_path, exist_ok=True)
        
        backup_local(new_folder_path)
