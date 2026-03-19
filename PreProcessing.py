import os
from tqdm import tqdm


def preprocess_normalize(input_file, output_file):
    # 读取输入文件
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 预加重和归一化处理
    preprocessed_lines = []
    prev_y = None
    for line in tqdm(lines):
        x, y = map(float, line.strip().split(','))
        if prev_y is not None:
            y = y - 0.98 * prev_y
        prev_y = y
        preprocessed_lines.append((x, y))

    # 写入输出文件
    with open(output_file, 'w') as f:
        for x, y in preprocessed_lines:
            f.write(f"{x},{y}\n")

    print(f'{input_file} Done!')

# 数据根目录
top_folder = '未处理患者数据'

# 遍历第一层文件夹
for folder_name in os.listdir(top_folder):
    folder_path = os.path.join(top_folder, folder_name)

    # 检查是否是文件夹
    if os.path.isdir(folder_path):
        print(f"Processing folder: {folder_path}")

        # 遍历每个数据文件夹内
        for data_folder_name in os.listdir(folder_path):
            data_folder_path = os.path.join(folder_path, data_folder_name)

            ######### 生成data文件 #########
            # 获取txt文档目录
            txt_files = [file for file in os.listdir(data_folder_path) if file.endswith(".txt")]
            # 检查.txt文件数量
            if len(txt_files) == 1:
                txt_file_name = txt_files[0]
                txt_file_path = os.path.join(data_folder_path, txt_file_name)

                # 分割文件名和后缀名
                file_parts = txt_file_name.split('.')
                file_name = '.'.join(file_parts[:-1])  # 获取除后缀名外的部分
                output_file = file_name + ".preprocessed"  # 添加新的后缀名
                output_file_path = os.path.join(data_folder_path, output_file)
                # 调用函数进行处理
                preprocess_normalize(txt_file_path, output_file_path)