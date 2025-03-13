
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

def generate_settings_files(output_dir, list):
    # 确保输出目录存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i in range(len(list)):
        # 生成文件内容
        content = f"""
HOA: v1
name: "F(r{list[i][0]} & XF(r{list[i][1]} & XFr{list[i][2]}))"
States: 4
Start: 2
AP: 3 "r{list[i][0]}" "r{list[i][1]}" "r{list[i][2]}"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels state-acc complete
properties: deterministic terminal very-weak
Label: {i}
--BODY--
State: 0 {0}
[t] 0
State: 1
[2] 0
[!2] 1
State: 2
[!0] 2
[0] 3
State: 3
[1] 1
[!1] 3
--END--
"""
        # 保存文件
        file_path = os.path.join(output_dir, f"{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"文件生成完成: {file_path}")

if __name__ == "__main__":
    list = [[3, 4, 7], [5, 4, 2], [4, 6, 7], [4, 8, 2], [6, 8, 3], [1, 4, 7]]
    
            
    output_dir = "./settings/task_lib/6/"  # 输出目录
    
    generate_settings_files(output_dir, list)
