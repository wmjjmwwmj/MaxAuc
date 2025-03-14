import os
import shutil
import json

def ensure_empty_folder(destination_folder):
    """
    确保目标文件夹存在，如果存在就清空，否则创建一个新的文件夹。
    """
    if os.path.exists(destination_folder):
        # 如果文件夹存在，清空文件夹内容
        shutil.rmtree(destination_folder)
    # 重新创建空文件夹
    os.makedirs(destination_folder, exist_ok=True)

def empty_file(file_path):
    """
    检查文件是否存在，如果存在则删除并重新创建，
    如果文件不存在，则直接创建。
    """
    # 检查文件是否存在
    if os.path.exists(file_path):
        print(f"文件 {file_path} 已存在，正在删除...")
        os.remove(file_path)  # 删除文件
    else:
        print(f"文件 {file_path} 不存在，正在创建...")

    # 创建文件（即使是空文件）
    with open(file_path, 'w') as f:
        pass  # 仅创建文件，不写入任何内容

    print(f"文件 {file_path} 已创建。")

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
            shutil.copy2(source_path, destination_path)
            print(f"已复制文件: {source_path} -> {destination_path}")
            
def save_to_json(data, file_path, ):
    # 检查文件是否存在
    if os.path.exists(file_path):
        try:
            # 尝试读取现有的文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                # 如果文件为空，直接初始化一个空列表
                if f.read().strip() == "":
                    existing_data = []
                else:
                    f.seek(0)  # 重置文件指针位置
                    existing_data = json.load(f)
        except json.decoder.JSONDecodeError:
            # 如果解析失败，初始化为空列表
            existing_data = []
    else:
        # 如果文件不存在，创建一个空列表
        existing_data = []

    # 将新的结果追加到现有内容后面
    existing_data.append(data)

    # 将结果写回 JSON 文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"结果已保存到 '{file_path}'。")
        
def read_json(file_path):
    """
    读取 JSON 文件并返回字典格式的数据
    :param file_path: JSON 文件的路径
    :return: 解析后的字典
    """
    try:
        # 打开并读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 将 JSON 数据解析为字典
        return data
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在。")
        return None
    except json.JSONDecodeError:
        print(f"文件 '{file_path}' 的内容不是有效的 JSON 格式。")
        return None
        
def copy_file_list(src_list, dest):
    """
    将源文件列表中的文件复制到目标文件夹。如果目标文件夹不存在，则先创建目标文件夹。
    
    :param src_list: 包含源文件路径的列表
    :param dest: 目标文件夹路径
    """
    try:
        # 如果目标文件夹不存在，创建目标文件夹
        if not os.path.exists(dest):
            os.makedirs(dest)
        
        # 遍历源文件列表并复制每个文件到目标文件夹
        for src in src_list:
            if os.path.isfile(src):
                # 构造目标文件路径
                dest_file = os.path.join(dest, os.path.basename(src))
                shutil.copy2(src, dest_file)  # 使用copy2保留文件的元数据
                print(f"文件 {src} 已成功复制到 {dest_file}")
            else:
                print(f"源文件 {src} 不存在或不是有效文件")
    
    except Exception as e:
        print(f"复制文件时发生错误: {e}")


def copy_folder_with_subfolder(src, dest):
    """
    将 src 文件夹复制到 dest 路径，在 dest 路径下创建一个同名文件夹，然后复制内容。
    
    :param src: 源文件夹路径
    :param dest: 目标文件夹路径
    """
    try:
        # 获取源文件夹的名称（不含路径）
        folder_name = os.path.basename(src)

        # 在目标文件夹下创建一个同名文件夹
        target_folder = os.path.join(dest, folder_name)
        
        copy_folder_content(src, target_folder)
    
    except Exception as e:
        print(f"复制文件夹时发生错误: {e}")
        
def copy_folder_content(src, dest):
    """
    将 src 文件夹复制到 dest 路径。如果目标文件夹已经存在且不为空，询问用户是否清空。
    
    :param src: 源文件夹路径
    :param dest: 目标文件夹路径
    """
    try:
        if os.path.exists(dest) and os.listdir(dest):  # 检查目标文件夹是否非空
            # 询问用户是否清空目标文件夹
            user_input = input(f"目标文件夹 {dest} 已经存在且不为空。是否清空该文件夹并继续？(y/n): ")
            if user_input.lower() == 'y':
                delete_and_copy(src, dest)
            else:
                copy_files_one_by_one(src, dest)
        else:
            delete_and_copy(src, dest)
        
        print(f"文件夹已成功从 {src} 复制到 {dest}")
    
    except Exception as e:
        print(f"复制文件夹时发生错误: {e}")
        
def delete_and_copy(src, dest):
    """
    将 src 文件夹复制到 dest 路径。
    
    :param src: 源文件夹路径
    :param dest: 目标文件夹路径
    """
    try:
        # 如果目标文件夹已经存在，则先删除再创建
        if os.path.exists(dest):
            print(f"删除目标文件夹 {dest} ...")
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

    except Exception as e:
        print(f"复制文件夹时发生错误: {e}")
    
def copy_files_one_by_one(src, dest):
    """
    逐个复制 src 文件夹下的文件到 dest 文件夹。
    
    :param src: 源文件夹路径
    """
    # 遍历源文件夹中的内容
    for item in os.listdir(src):
        source_item = os.path.join(src, item)
        destination_item = os.path.join(dest, item)

        # 如果是文件，直接复制
        if os.path.isfile(source_item):
            if not os.path.exists(destination_item):  # 如果目标文件夹没有这个文件
                shutil.copy2(source_item, destination_item)  # 保持文件的原始时间戳
                print(f"文件 {source_item} 已复制到 {destination_item}")
            else:
                print(f"文件 {destination_item} 已存在，跳过复制。")
        # 如果是文件夹，递归复制
        elif os.path.isdir(source_item):
            # 创建目标文件夹
            os.makedirs(destination_item, exist_ok=True)
            # 递归复制文件夹
            copy_files_one_by_one(source_item, destination_item)
        else:
            print(f"未知类型的文件: {source_item}")


if __name__ == "__main__":
    # 测试 ensure_empty_folder 函数
    # ensure_empty_folder("test_folder")
    
    # # 测试 copy_txt_files 函数
    # copy_txt_files("source_folder", "destination_folder")
    
    # 测试 save_to_json 函数
    data = {"key1": "value1", "key2": "value2"}
    save_to_json(data,  "results.json")