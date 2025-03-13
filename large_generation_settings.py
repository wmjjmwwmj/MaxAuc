import os
import random
from P_MAS_TG.utils.args_config import set_seed
from P_MAS_TG.utils.random_picking import select_points
from P_MAS_TG.utils.import_module import import_module_from_path
import os
import shutil

def ensure_empty_folder(destination_folder):
    """
    确保目标文件夹存在，如果存在就清空，否则创建一个新的文件夹。
    """
    if os.path.exists(destination_folder):
        # 如果文件夹存在，清空文件夹内容
        shutil.rmtree(destination_folder)
    # 重新创建空文件夹
    os.makedirs(destination_folder, exist_ok=True)


def copy_txt_files(source_folder, destination_folder,  task_num):
    """
    将 source_folder 下所有 .txt 文件复制到 destination_folder。

    参数:
        source_folder: 源文件夹路径
        destination_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在，不存在则创建
    os.makedirs(destination_folder, exist_ok=True)
    
    # 遍历源文件夹
    for i in range(task_num):
        # # 检查文件后缀是否为 .txt
        # if file_name.endswith(".txt"):
        file_name = f"{i}.txt"
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)
        
        # 复制文件
        shutil.copy(source_path, destination_path)
        print(f"已复制文件: {source_path} -> {destination_path}")

def generate_random_relation(n):
    """生成一个随机的约束关系字典，确保不会产生冲突"""
    ss = []
    es = []
    ee = []
    se = []
    
    # 随机生成 ss（x_i < x_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                ss.append((i, j))
    
    # 随机生成 es（x_i + delta_i < x_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                es.append((i, j))
    
    # 随机生成 ee（x_i + delta_i < x_j + delta_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                ee.append((i, j))
    
    # 随机生成 se（x_i < x_j + delta_j）的约束
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.3:  # 30%的概率产生约束
                se.append((i, j))
    
    return {"ss": ss, "es": es, "ee": ee, "se": se}

def generate_settings_files(output_dir, n, robot_num, task_num):
    """
    根据不同的随机种子生成一系列 settings 文件。

    参数：
        output_dir: 输出目录
        n: 环境大小
        robot_num: 机器人数量
        file_count: 生成文件的数量
    """
    ensure_empty_folder(output_dir)  # 确保输出目录为空
    
    # 根据task_num, 把相应的task文件复制到output_dir下
    task_files_path = f'settings/task_lib/20tasks/'
    copy_txt_files(task_files_path, output_dir, task_num)
    
    # # 根据task_num, import description.py
    # description_file_path = os.path.join(task_files_path, "description.py")  # 生成描述文件
    # description_cls = import_module_from_path(description_file_path, "description")
    
    ap_num = 40

    relation_dict = generate_random_relation(task_num)  # 生成约束关系字典
    
    # 生成机器人初始位置
    robot_initial_position = select_points(n, robot_num)  # 采样得到初始位置
    
    # 生成regions
    regions = {point: f"r{i + 1}" for i, point in enumerate(select_points(n, ap_num))}

    # 生成文件内容
    content = f"""
##########################################################################
# 环境size
n = {n}

# 机器人设置
robot_num = {robot_num}

robot_initial_position = {robot_initial_position}

##########################################################################
# 任务相关
task_num = {task_num}
task_index = {list(range(task_num))}
task_files_path = {repr(output_dir)}
relation_dict = {relation_dict}
# 特殊区域
regions = {regions}

##########################################################################
# 画图设置

fps = 1

marker_shapes = {{
    'Robot-0': 'o',  # 圆形
    'Robot-1': '^',  # 上三角形
    'Robot-2': 's',  # 正方形
    'Robot-3': 'D'   # 菱形
}}
"""
    # 保存文件
    file_path = os.path.join(output_dir, "settings.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"文件生成完成: {file_path}")

if __name__ == "__main__":
    seed_list = [42, 43, 44, 45, 46, 
                 47, 48, 49, 50, 51,
                 52, 53, 54, 55, 56,
                 57, 58, 59, 60, 61,]
    for seed in seed_list:
        set_seed(seed)  # 固定随机种子
        

        settings_list = [
            "10.5.10", "10.6.10", "10.7.10", "10.8.10", "10.9.10", "10.10.10", "10.11.10", "10.12.10", "10.13.10", "10.14.10", "10.15.10",
            "10.5.11", "10.6.11", "10.7.11", "10.8.11", "10.9.11", "10.10.11", "10.11.11", "10.12.11", "10.13.11", "10.14.11", "10.15.11",
            "10.5.12", "10.6.12", "10.7.12", "10.8.12", "10.9.12", "10.10.12", "10.11.12", "10.12.12", "10.13.12", "10.14.12", "10.15.12",
            "10.5.13", "10.6.13", "10.7.13", "10.8.13", "10.9.13", "10.10.13", "10.11.13", "10.12.13", "10.13.13", "10.14.13", "10.15.13",
            "10.5.14", "10.6.14", "10.7.14", "10.8.14", "10.9.14", "10.10.14", "10.11.14", "10.12.14", "10.13.14", "10.14.14", "10.15.14",
            "10.5.15", "10.6.15", "10.7.15", "10.8.15", "10.9.15", "10.10.15", "10.11.15", "10.12.15", "10.13.15", "10.14.15", "10.15.15",
            "10.5.16", "10.6.16", "10.7.16", "10.8.16", "10.9.16", "10.10.16", "10.11.16", "10.12.16", "10.13.16", "10.14.16", "10.15.16",
            "10.5.17", "10.6.17", "10.7.17", "10.8.17", "10.9.17", "10.10.17", "10.11.17", "10.12.17", "10.13.17", "10.14.17", "10.15.17",
            "10.5.18", "10.6.18", "10.7.18", "10.8.18", "10.9.18", "10.10.18", "10.11.18", "10.12.18", "10.13.18", "10.14.18", "10.15.18",
            "10.5.19", "10.6.19", "10.7.19", "10.8.19", "10.9.19", "10.10.19", "10.11.19", "10.12.19", "10.13.19", "10.14.19", "10.15.19",
            "10.5.20", "10.6.20", "10.7.20", "10.8.20", "10.9.20", "10.10.20", "10.11.20", "10.12.20", "10.13.20", "10.14.20", "10.15.20",
            ]
        
        
        for i in settings_list:
            
            output_dir = f"settings/seed{seed}/{i}"  # 输出目录
            
            n, robot_num, task_num = map(int, i.split("."))
            
            generate_settings_files(output_dir, n, robot_num, task_num)
