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


def copy_txt_files(source_folder, destination_folder):
    """
    将 source_folder 下所有 .txt 文件复制到 destination_folder。

    参数:
        source_folder: 源文件夹路径
        destination_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在，不存在则创建
    os.makedirs(destination_folder, exist_ok=True)
    
    # 遍历源文件夹
    for file_name in os.listdir(source_folder):
        # 检查文件后缀是否为 .txt
        if file_name.endswith(".txt"):
            source_path = os.path.join(source_folder, file_name)
            destination_path = os.path.join(destination_folder, file_name)
            
            # 复制文件
            shutil.copy(source_path, destination_path)
            print(f"已复制文件: {source_path} -> {destination_path}")

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
    task_files_path = f'settings/task_lib/{task_num}/'
    copy_txt_files(task_files_path, output_dir)
    
    # 根据task_num, import description.py
    description_file_path = os.path.join(task_files_path, "description.py")  # 生成描述文件
    description_cls = import_module_from_path(description_file_path, "description")
    
    ap_num = description_cls.ap_num
    task_index = description_cls.task_index
    relation_dict = description_cls.relation_dict
    
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
task_index = {task_index}
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
            "4.2.6"
            ]
        
        
        for i in settings_list:
            
            output_dir = f"settings/seed{seed}/{i}"  # 输出目录
            
            n, robot_num, task_num = map(int, i.split("."))
            
            generate_settings_files(output_dir, n, robot_num, task_num)
