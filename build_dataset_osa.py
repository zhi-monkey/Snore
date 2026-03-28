"""
构建 OSA 严重程度分类数据集（单通道鼾声/呼吸音频信号）。

===== 输入信号 =====

仅使用鼾声/呼吸音频（500 Hz），不依赖 PSG 其他通道。
该信号反映上气道狭窄程度，与打鼾及低通气直接相关。

===== OSA 严重程度分级标准（AHI）=====

| 标签 | 严重程度 | AHI 范围          |
|------|----------|-------------------|
|  0   | 正常     | AHI < 5           |
|  1   | 轻度     | 5  ≤ AHI < 15     |
|  2   | 中度     | 15 ≤ AHI < 30     |
|  3   | 重度     | AHI ≥ 30          |

===== 原始数据目录结构 =====

    未处理患者数据/
      <severity>/          # 文件夹名即为严重程度，例如：正常、轻度、中度、重度
        <patient_id>/
          data/
            txt/           # 60秒鼾声分段文件（CSV格式：时间,幅度，500 Hz）

===== 输出目录结构 =====

    ./data_osa/train/   和   ./data_osa/test/
    每个 .npy 文件：{'data': ndarray(1, 30000), 'severity': int}
"""

import os
import random

import numpy as np
from tqdm import tqdm

from utils import set_seed


# ── 严重程度文件夹名称 → 整数标签的映射 ──────────────────────────────────────
SEVERITY_MAP = {
    '正常': 0,   # Normal:    AHI < 5
    '轻度': 1,   # Mild:    5 ≤ AHI < 15
    '中度': 2,   # Moderate: 15 ≤ AHI < 30
    '重度': 3,   # Severe: AHI ≥ 30
}

# ── 信号参数 ──────────────────────────────────────────────────────────────────
SAMPLE_RATE = 500    # Hz（鼾声音频采样率）
CHUNK_SECONDS = 60   # 每个窗口的时长（秒）
CHUNK_SAMPLES = SAMPLE_RATE * CHUNK_SECONDS  # 每窗口样本数 = 30 000


def _load_signal_txt(file_path):
    """读取两列 CSV 文件（时间,幅度），返回幅度数组。"""
    values = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                values.append(float(parts[1]))
    return np.array(values, dtype=np.float32)


def build_chunk(snoring_path):
    """
    载入单通道鼾声/呼吸音频，截断或零填充至 CHUNK_SAMPLES 个采样点，
    返回形状为 (1, CHUNK_SAMPLES) 的数组。
    """
    signal = _load_signal_txt(snoring_path)
    # 截断或零填充，保证长度固定
    if len(signal) >= CHUNK_SAMPLES:
        signal = signal[:CHUNK_SAMPLES]
    else:
        signal = np.pad(signal, (0, CHUNK_SAMPLES - len(signal)))
    return signal[np.newaxis, :]  # (1, 30000)


if __name__ == '__main__':
    set_seed(3407)

    top_folder = '未处理患者数据'
    train_path = './data_osa/train/'
    test_path  = './data_osa/test/'
    for p in [train_path, test_path]:
        os.makedirs(p, exist_ok=True)

    for severity_name in os.listdir(top_folder):
        severity_dir = os.path.join(top_folder, severity_name)
        if not os.path.isdir(severity_dir):
            continue

        severity_label = SEVERITY_MAP.get(severity_name)
        if severity_label is None:
            print(f'[警告] 未知严重程度文件夹: "{severity_name}"，跳过')
            continue

        print(f'\n处理严重程度: {severity_name}（标签={severity_label}）')

        for patient_id in os.listdir(severity_dir):
            patient_dir = os.path.join(severity_dir, patient_id)
            if not os.path.isdir(patient_dir):
                continue

            snoring_dir = os.path.join(patient_dir, 'data', 'txt')
            if not os.path.isdir(snoring_dir):
                print(f'  [警告] 未找到鼾声数据目录: {snoring_dir}，跳过患者 {patient_id}')
                continue

            chunk_files = sorted(f for f in os.listdir(snoring_dir) if f.endswith('.txt'))
            random.shuffle(chunk_files)

            # 按 8:2 划分训练集/测试集
            split_idx = int(0.8 * len(chunk_files))
            splits = [
                ('train', chunk_files[:split_idx], train_path),
                ('test',  chunk_files[split_idx:], test_path),
            ]

            for split_name, files, out_dir in splits:
                for fname in tqdm(files, desc=f'  {patient_id}/{split_name}'):
                    base = os.path.splitext(fname)[0]
                    snoring_path = os.path.join(snoring_dir, fname)

                    data = build_chunk(snoring_path)
                    record = {'data': data, 'severity': severity_label}

                    # 文件名：<严重程度>_<患者ID>_<分段名>.npy
                    save_name = f'{severity_name}_{patient_id}_{base}.npy'
                    np.save(os.path.join(out_dir, save_name), record, allow_pickle=True)

    print('\n数据集构建完成。')
    print(f'训练集: {train_path}')
    print(f'测试集: {test_path}')
