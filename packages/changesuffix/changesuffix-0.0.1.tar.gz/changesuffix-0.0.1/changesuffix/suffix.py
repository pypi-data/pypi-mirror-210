
import os

def rename_file_extension(directory, old_extension, new_extension):
    for filename in os.listdir(directory):
        if filename.endswith(old_extension):
            current_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, os.path.splitext(filename)[0] + new_extension)
            os.rename(current_path, new_path)
            print(f"Renamed {current_path} to {new_path}")

# 替换文件后缀名
directory = "G:\PythonPrjs\changesuffix\images"  # 目标文件夹路径
old_extension = ".webp"  # 原文件后缀名
new_extension = ".jpg"  # 新文件后缀名
rename_file_extension(directory, old_extension, new_extension)