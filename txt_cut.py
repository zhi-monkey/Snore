import os
from tqdm import tqdm
import openpyxl
import numpy as np

# 每个文件的秒数
sec = 60
# 每个文件的行数
chunk_size = 500 * sec

# 数据根目录
top_folder = '未处理患者数据'


def process_file(file_path, previous_time):
    '''
    处理单个 txt 文件，生成对应的标签数组，并返回当前文件结束时的时间长度

    Parameters:
        file_path (str): 文件路径
        previous_time (int): 前面文件已经计算的时间长度

    Returns:
        numpy.ndarray: 标签数组
        int: 当前文件结束时的时间长度
    '''
    # 设置文件秒数
    sec = 60
    # 读取文件内容
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()

        # 如果第一行就是 "0,[NA,NA]"，则直接返回全零数组
        if first_line == '0,[NA,NA]':
            return np.zeros(sec * 500), previous_time + sec

        # 否则，提取第一行中的起始时间和终止时间
        time_str = first_line.split('[')[1].split(']')[0]
        start_time, end_time = time_str.split(',')
        start_time = float(start_time)
        end_time = float(end_time)
        start_index = int(float(start_time) * 500) - previous_time * 500
        end_index = int(float(end_time) * 500) - previous_time * 500

        # 生成标签数组
        label_array = np.zeros(sec * 500)  # 每个文件120秒，每秒500个采样点
        label_array[start_index:end_index + 1] = 1

        # 继续处理剩余行（如果有）
        for line in file:
            start_time, end_time = line.strip().split('[')[1].split(']')[0].split(',')
            start_index = int(float(start_time) * 500) - previous_time * 500
            end_index = int(float(end_time) * 500) - previous_time * 500
            label_array[start_index:end_index + 1] = 1

    return label_array, previous_time + sec


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
                txt_file_base_name = txt_file_name.split('_')[0]

            # 计数器，用于生成输出文件名
            file_count = 1

            # 输入数据文件
            input_file_path = txt_file_path

            # 数据输出文件夹路径
            data_cut_folder_path = os.path.join(data_folder_path, 'data/txt')
            # 标签目录下的输出文件夹路径
            label_array_folder_path = os.path.join(data_folder_path, 'label/txt_array')
            label_folder_path = os.path.join(data_folder_path, 'label/txt')

            # 创建输出文件夹
            os.makedirs(data_cut_folder_path, exist_ok=True)
            os.makedirs(label_array_folder_path, exist_ok=True)
            os.makedirs(label_folder_path, exist_ok=True)
            # 打开输入文件
            with open(input_file_path, 'r') as input_file:
                # 初始化行计数器
                line_count = 0

                # 初始化输出文件
                file_name = f"{txt_file_base_name}_{file_count}.txt"
                output_file = open(os.path.join(data_cut_folder_path, file_name), 'w')

                # 创建标签目录下的空txt文档
                # open(os.path.join(label_array_folder_path, file_name), 'w').close()
                # open(os.path.join(label_folder_path, file_name), 'w').close()

                # 遍历输入文件的每一行
                for line in tqdm(input_file):
                    # 写入当前行到输出文件
                    output_file.write(line)

                    # 增加行计数器
                    line_count += 1

                    # 如果达到了指定的行数，关闭当前输出文件，并创建新文件
                    if line_count == chunk_size:
                        output_file.close()
                        file_count += 1
                        file_name = f"{txt_file_base_name}_{file_count}.txt"
                        output_file = open(os.path.join(data_cut_folder_path, file_name), 'w')
                        # open(os.path.join(label_array_folder_path, file_name), 'w').close()
                        # open(os.path.join(label_folder_path, file_name), 'w').close()
                        line_count = 0

                line_count = 0
                # 关闭最后一个输出文件
                output_file.close()
            print(f"\n{txt_file_base_name} Files split successfully!\n")

            ######### 生成label文件 #########
            # 遍历文件夹中的每个文件
            for filename in os.listdir(data_folder_path):
                # 检查文件是否以特定后缀结尾
                if filename.endswith('.reports'):
                    # 输入文件路径和文件名
                    input_file_dir = os.path.join(data_folder_path, filename)
            input_file_path = os.path.join(input_file_dir, 'data.xlsx')
            # 打开 Excel 文件
            workbook = openpyxl.load_workbook(input_file_path)
            sheet = workbook.active

            # 遍历每行数据
            for row in sheet.iter_rows(min_row=1, values_only=True):  # 从第1行开始遍历
                # 读取每行数据
                start_time = row[3]  # 第四列是起始时间
                end_time = row[4]  # 第五列是终止时间
                start_file = int(row[5])  # 第六列是起始文件名
                end_file = int(row[6])  # 第七列是终止文件名

                # 格式化写入内容
                content = f"1,[{int(start_time)},{int(end_time)}]"

                # 遍历起始文件到终止文件的所有文件
                for file_name_num in range(start_file, end_file + 1):
                    # 计算当前文件应该写入的时间范围
                    current_start_time = max(start_time, (file_name_num - 1) * sec)
                    current_end_time = min(end_time, file_name_num * sec)

                    # 格式化写入内容
                    content = f"1,[{int(current_start_time)},{int(current_end_time)}]"

                    # 写入文件
                    file_name = f"{txt_file_base_name}_{file_name_num}.txt"
                    file_path = os.path.join(label_folder_path, file_name)
                    with open(file_path, 'a') as file:
                        file.write(content + '\n')


            # 遍历文件夹下的所有文件
            for filename in tqdm(os.listdir(label_folder_path)):
            # 检查文件是否为 txt 文件
                if filename.endswith('.txt'):
                    file_path = os.path.join(label_folder_path, filename)

                # 检查文件是否为空
                if os.path.getsize(file_path) == 0:
                    # 写入内容到空文件中
                    with open(file_path, 'w') as file:
                        file.write('0,[NA,NA]\n')
            print(f"\n{txt_file_base_name} Label files written successfully!\n")

            ######### 将label文件转换为数组 #########
            # 初始化标签数组和前面文件已经计算的时间长度
            labels = []
            previous_time = 0

            # 获取文件夹下所有文件名列表
            file_names = os.listdir(label_folder_path)

            # 遍历文件夹中的每个文件
            for file_name in tqdm(file_names):
                file_number = int(file_name.split('.')[0].split('_')[1])
                file_path = os.path.join(label_folder_path, file_name)
                # 处理单个文件并将结果添加到标签数组中
                label_array, previous_time = process_file(file_path, (file_number - 1) * 60)
                labels.append(label_array)

                save_path = label_array_folder_path
                # 将结果保存到对应的文件中
                result_file_path = os.path.join(save_path, file_name)
                with open(result_file_path, 'w') as result_file:
                    result_file.write('[' + ','.join(map(str, label_array.astype(int))) + ']')

                # 清空数组中的值
                label_array = []
            print(f"\n{txt_file_base_name} Write labels successfully!\n")

print("Files split successfully!")