"""
Dataset for OSA (Obstructive Sleep Apnea) severity classification.

Each sample is a fixed-length multi-channel PSG signal window.
All windows from the same patient recording share the same severity label.

Expected .npy file format (produced by build_dataset_osa.py):
    {
        'data':     ndarray of shape (4, seq_len), dtype float32
        'severity': int  -- 0=正常, 1=轻度OSA, 2=中度OSA, 3=重度OSA
    }

PSG channel layout (index → signal):
    0 - 鼾声/呼吸音频  Snoring / respiratory audio   (500 Hz)
    1 - 血氧饱和度 SpO2  Blood oxygen saturation       (resampled to 500 Hz)
    2 - 口鼻气流        Nasal / oral airflow            (resampled to 500 Hz)
    3 - 胸部呼吸运动    Thoracic respiratory effort     (resampled to 500 Hz)
"""

import os

import numpy as np
import torch
from torch.utils.data import Dataset

# Human-readable labels for OSA severity classes
SEVERITY_LABELS = ['正常', '轻度OSA', '中度OSA', '重度OSA']


class OSASeverityDataset(Dataset):
    """PyTorch Dataset for OSA severity classification.

    Args:
        data_dir (str): Directory containing the pre-built .npy sample files.
    """

    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.npy_files = sorted(
            f for f in os.listdir(data_dir) if f.endswith('.npy')
        )

    def __len__(self):
        return len(self.npy_files)

    def __getitem__(self, idx):
        path = os.path.join(self.data_dir, self.npy_files[idx])
        record = np.load(path, allow_pickle=True)[()]

        data = record['data'].astype(np.float32)       # shape: (4, seq_len)
        severity = int(record['severity'])             # scalar: 0, 1, 2, or 3

        return (
            torch.from_numpy(data),
            torch.tensor(severity, dtype=torch.long),
        )
