import os

import numpy as np
import torch
from torch.utils.data import Dataset

from utils import load_data


class SnoreDataset(Dataset):
    def __init__(self, data_dir):
        super(SnoreDataset, self).__init__()

        self.data_dir = data_dir
        self.npy_files = [f for f in os.listdir(self.data_dir) if f.endswith('.npy')]

    def __getitem__(self, item):
        data, label = load_data(os.path.join(self.data_dir, self.npy_files[item]))
        data = np.expand_dims(data, axis=0)

        return torch.from_numpy(data).float(), torch.from_numpy(label).type(torch.LongTensor)

    def __len__(self):
        return len(self.npy_files)