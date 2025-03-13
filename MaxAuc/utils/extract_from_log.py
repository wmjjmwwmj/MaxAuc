import os
import re
import json
from fileops import save_to_json

def parse_logs(root_directory):
    # 字典用于存储统计结果
    results = {}

    # 遍历指定根目录及其所有子目录
    for root, _, files in os.walk(root_directory):
        for filename in files:
            if filename == "_output_.log":  # 仅处理名为 _output_.log 的日志文件
                filepath = os.path.join(root, filename)
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    settings_n = None
                    total_time = None
                    makespan = None

                    for line in file:
                        # 匹配 settings_n 的值
                        settings_match = re.search(r"\|\s*settings_n\s*\|\s*([^\|]+)\s*\|", line)
                        if settings_match:
                            settings_n = settings_match.group(1).strip()

                        # 匹配总耗时
                        time_match = re.search(r"MainThread - INFO - 总耗时 ([\d\.]+)s", line)
                        if time_match:
                            total_time = float(time_match.group(1))

                        # 匹配 makespan
                        makespan_match = re.search(r"MainThread - INFO - make span: (\d+)", line)
                        if makespan_match:
                            makespan = int(makespan_match.group(1))
                            
                        # 匹配 seed
                        seed_match = re.search(r"\|\s*seed\s*\|\s*([^\|]+)\s*\|", line)
                        if seed_match:
                            seed = seed_match.group(1).strip()

                    # 如果找到有效数据，添加到结果中
                    if settings_n and total_time and makespan is not None:
                        # 使用日志文件的目录名作为键
                        dir_name = os.path.basename(root)
                        results[dir_name] = {
                            "settings_n": settings_n,
                            "total_time": total_time,
                            "makespan": makespan,
                            "seed": seed
                        }

    return results

if __name__ == "__main__":
    # 指定日志目录路径
    log_directory = "./outputs"  # 替换为你的根目录路径

    # 解析日志并打印结果
    log_data = parse_logs(log_directory)
    save_to_json(log_data, "extracted_results.json")  # 保存结果到 JSON 文件
