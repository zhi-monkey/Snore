import numpy as np
import torch

from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset import SnoreDataset
from models import unet_cbam
from utils import set_seed


def post_processing(outputs):
    Duration_points = 8000

    outputs_np = np.array(outputs)

    OSA_indexs = np.where(outputs_np == 1)[0]
    OSA_diffs = np.diff(np.array(OSA_indexs))
    OSA_dists = np.where(OSA_diffs == 1)[0] + 1

    p_segments = np.split(OSA_indexs, OSA_dists)
    if len(p_segments) > 1:
        for i, segment in enumerate(p_segments):
            if segment[-1] - segment[0] < Duration_points:
                outputs_np[segment[0]: segment[-1] + 1] = 0

    outputs = outputs_np.tolist()

    return outputs


def get_results(label, outputs):
    true_OSA_number = 0
    predicted_OSA_number = 0

    for index in range(len(label) - 1):
        # 0
        if label[index] == 0 and label[index + 1] == 0:
            continue
        # OSA开始
        elif label[index] != 1 and label[index + 1] == 1:
            true_OSA_number += 1

    for index in range(len(outputs) - 1):
        # 0
        if outputs[index] == 0 and outputs[index + 1] == 0:
            continue
        # OSA开始
        elif outputs[index] != 1 and outputs[index + 1] == 1:
            predicted_OSA_number += 1
    return true_OSA_number, predicted_OSA_number

def predict(modelpath, testpath):
    set_seed(3407)
    device = 'cuda:0'

    model = unet_cbam.UNet(n_channels=32).to(device)
    model.load_state_dict(torch.load(modelpath, map_location=device))

    test_path = testpath

    test_dataset = SnoreDataset(test_path)

    batch_size = 1
    shuffle = False
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=shuffle)

    # 存储正确标签与预测标签
    label_list = []
    output_list = []

    for data, label in tqdm(test_dataloader):
        data, label = data.to(device, dtype=torch.float), label.to(device, dtype=torch.long)
        outputs = model(data)

        # 输出处理
        out_t = torch.max(outputs, dim=1)[1]
        # print(out_t.type)
        # print(out_t.shape)
        # print(out_t.view(-1).tolist())
        # 存储到数组中
        label_list.extend(label.view(-1).tolist())
        output_list.extend(out_t.view(-1).tolist())

    output_list = post_processing(output_list)
    true_OSA_number, predicted_OSA_number = get_results(label_list, output_list)

    print('Result of Testset: ')
    print(f'True OSA number: {true_OSA_number}, Predicted OSA number: {predicted_OSA_number}')

    return true_OSA_number, predicted_OSA_number


if __name__ == '__main__':
    predict('best_model_cbam_2024-05-07 174201.pt', 'data/test')