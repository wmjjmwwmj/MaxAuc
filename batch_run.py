import subprocess
import os
import json
from P_MAS_TG.utils.fileops import save_to_json, read_json, empty_file
import numpy as np
import concurrent.futures
from datetime import datetime
from files_backup import backup_local
from tqdm import tqdm

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


def generate_param_combinations(settings_list, num_seeds = 20):
    """
    生成参数组合。
    """
    # 生成参数组合
    params = []
    
    # 遍历所有 settings 和每个 setting 的种子
    for setting in settings_list:
        for seed in range(42, 42 + num_seeds):
            params.append(('--seed', seed, "--settings_n", setting))
    
    return params

def average_and_std(data):
    """
    计算数据的平均值和标准差。
    """
    return (sum(data) / len(data), np.std(data))

if __name__ == '__main__':
    
    empty_file("results.json")
    
    script_path = "baseline_refer_settings.py"
    settings_list = ["4.2.2", "4.2.5", "4.2.4", "4.2.3", "4.1.5", "5.2.2", "6.2.2", "7.2.2", "8.2.2"]
    param_combinations = generate_param_combinations(settings_list,20)
    batch_run(script_path, param_combinations)
    
    # 加载结果
    results = read_json("results.json")
    
    batch_results = {}
    # 根据settings_list打印结果
    # 要统计的变量
    
    for setting in settings_list:
        make_span = []
        path_length = []
        plan_time = []
        batch_size = 0
        print(f"Setting: {setting}")
        
        for result in results:
            if result["settings_n"] == setting:
                # print(result)
                batch_size += 1
                make_span.append(result["make span"])
                path_length.append(result["path length"])
                plan_time.append(result["plan time"])
        
        batch_results[setting] = {
            "make span": average_and_std(make_span),
            "path length": average_and_std(path_length),
            "plan time": average_and_std(plan_time),
            "batch size": batch_size
        }
        
    save_to_json(batch_results, "batch_results.json")

    # 直接备份到本地
    # 获取当前时间，格式化为字符串
    current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # 拼接文件夹名称
    folder_name = f"{settings_list[-1]}_{current_time}"
    
    # 构造完整路径
    new_folder_path = os.path.join(r"D:\Paper\data_backup\RAL\Baseline", folder_name)
    
    # 创建文件夹
    os.makedirs(new_folder_path, exist_ok=True)
    
    backup_local(new_folder_path)