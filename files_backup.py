from P_MAS_TG.utils.fileops import copy_folder_with_subfolder, copy_file_list

def backup_local(dest_path):
    """
    备份实验结果到本地。
    """
    # 实验结果备份到本地
    result_path = r"results.json"
    batch_result_path = r"batch_results.json"
    backup_file_paths = [result_path, batch_result_path]
    copy_file_list(backup_file_paths, dest_path)
    
    outputs_path = r"outputs"
    copy_folder_with_subfolder(outputs_path, dest_path)
    
    print("Backup done.")

if __name__ == '__main__':
    
    # # 备份到分支
    # file_path = r"outputs\20241228-230009"
    
    # copy_folder_with_subfolder(file_path, "P_MAS_outputs")
    # print("Backup done.")
    
    # 实验结果备份到本地
    dest_path = r"D:\Paper\data_backup\RAL\Baseline\4.2.5"
    
    outputs_path = r"outputs"
    copy_folder_with_subfolder(outputs_path, dest_path)
    