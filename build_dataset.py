import os
import random
import shutil

from tqdm import tqdm
from utils import set_seed

if __name__ == '__main__':
    set_seed(3407)

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
                data_path = os.path.join(data_folder_path, 'data/npy/')
                npy_files = os.listdir(data_path)
                random.shuffle(npy_files)

                train_path = './data/train/'
                test_path = './data/test/'

                for i in [train_path, test_path]:
                    if not os.path.exists(i):
                        os.makedirs(i, exist_ok=True)

                train_files = npy_files[:int(0.8 * len(npy_files))]
                test_files = npy_files[int(0.8 * len(npy_files)):]

                for train_file in tqdm(train_files):
                    shutil.copy(os.path.join(data_path, train_file), os.path.join(train_path, train_file))

                for test_file in tqdm(test_files):
                    shutil.copy(os.path.join(data_path, test_file), os.path.join(test_path, test_file))
