import os
import shutil

def move_files_from_subfolders(source_folder_path, destination_folder):
    """
    将源文件夹中所有子文件夹内的文件移动到目标文件夹。

    参数:
        source_folder_path (str): 包含子文件夹的源文件夹路径。
        destination_folder (str): 目标文件夹路径。
    """
    # 确保目标文件夹存在
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # 遍历源文件夹中的所有子文件夹和文件
    for root, dirs, files in os.walk(source_folder_path):
        for file in files:
            # 构造文件的完整路径
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)
            
            try:
                # 移动文件到目标文件夹
                shutil.move(source_file_path, destination_folder)
                print(f"移动文件: {source_file_path} 到 {destination_file_path}")
            except Exception as e:
                print(f"移动文件 {source_file_path} 时出错: {e}")

# 示例用法
source_folder = "/home/tianqo/Pictures/test"  # 替换为源文件夹路径
destination_folder = "/home/tianqo/Pictures/basketball"  # 替换为目标文件夹路径

move_files_from_subfolders(source_folder, destination_folder)