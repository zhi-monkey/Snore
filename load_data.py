import os
import numpy as np
from tqdm import tqdm

if __name__ == '__main__':
    # 数据根目录
    top_folder = '未处理患者数据'

    for folder_name in os.listdir(top_folder):
        folder_path = os.path.join(top_folder, folder_name)

        # 检查是否是文件夹
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")

            # 遍历每个数据文件夹内
            for data_folder_name in os.listdir(folder_path):
                data_folder_path = os.path.join(folder_path, data_folder_name)

                data_path = os.path.join(data_folder_path, 'data/txt')
                label_path = os.path.join(data_folder_path, 'label/txt_array')
                file_names = os.listdir(label_path)

                npy_path = os.path.join(data_folder_path, 'data/npy/')
                if not os.path.exists(npy_path):
                    os.makedirs(npy_path, exist_ok=True)

                for name in tqdm(file_names):
                    time = []
                    amplify = []
                    label = []
                    with open(os.path.join(label_path, name), 'r') as file:
                        # 读取整个文件内容并去除首尾空白字符
                        content = file.read().strip()
                        # 去除方括号并按逗号分割数据
                        data = content[1:-1].split(',')
                        # 将每个元素转换为整数并添加到label数组中
                        label = [int(x) for x in data]

                    with open(os.path.join(data_path, name), 'r') as file:
                        for line in file:
                            data = line.strip().split(',')  # 去除行末的换行符并按逗号分割数据
                            # 将两列数据转换为浮点数，并分别添加到time和amplify数组中
                            time.append(float(data[0]))
                            amplify.append(float(data[1]))
                    snore_dict = {'data': np.array(amplify), 'label': np.array(label)}
                    np.save(os.path.join(npy_path, name), snore_dict, allow_pickle=True)