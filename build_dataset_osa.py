"""
构建 OSA 严重程度分类数据集（多通道PSG信号）。

===== 所需的 PSG 信号（医院 PSG 设备采集）=====

| 通道 | 信号名称               | 临床意义                                          |
|------|------------------------|---------------------------------------------------|
|  0   | 鼾声/呼吸音频          | 反映上气道狭窄程度，与打鼾及低通气直接相关        |
|  1   | 血氧饱和度（SpO2）     | 呼吸暂停时出现特征性氧饱和度下降，是最关键的指标  |
|  2   | 口鼻气流（Airflow）    | 直接判断呼吸暂停/低通气，是事件检测的金标准       |
|  3   | 胸部呼吸运动（Effort） | 区分阻塞性（有努力无气流）与中枢性（无努力无气流）|

注：以上信号均统一重采样至 500 Hz，与鼾声信号保持一致。

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
            spo2/          # [可选] SpO2 分段文件（CSV格式：时间,饱和度，重采样至 500 Hz）
            airflow/       # [可选] 口鼻气流分段文件（CSV格式：时间,气流值，重采样至 500 Hz）
            effort/        # [可选] 胸部呼吸运动分段文件（CSV格式：时间,努力值，重采样至 500 Hz）

若某通道文件不存在，该通道将以全零填充（占位符），方便以单通道数据先行训练。

===== 输出目录结构 =====

    ./data_osa/train/   和   ./data_osa/test/
    每个 .npy 文件：{'data': ndarray(4, 30000), 'severity': int}
"""

import os
import random

import numpy as np
from scipy.signal import resample
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
SAMPLE_RATE = 500    # Hz（鼾声音频采样率；其他通道将被重采样至此频率）
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


def _load_or_zeros(file_path, target_len):
    """载入信号文件并重采样至 target_len，若文件不存在则返回全零数组。"""
    if file_path is not None and os.path.isfile(file_path):
        signal = _load_signal_txt(file_path)
        if len(signal) != target_len:
            signal = resample(signal, target_len).astype(np.float32)
        return signal
    return np.zeros(target_len, dtype=np.float32)


def build_chunk(snoring_path, spo2_path, airflow_path, effort_path):
    """
    载入并叠加 4 个 PSG 通道，返回形状为 (4, CHUNK_SAMPLES) 的数组。

    通道顺序：
        0 - 鼾声/呼吸音频  (snoring_path)
        1 - 血氧饱和度 SpO2 (spo2_path，可为 None)
        2 - 口鼻气流        (airflow_path，可为 None)
        3 - 胸部呼吸运动    (effort_path，可为 None)
    """
    snoring = _load_or_zeros(snoring_path, CHUNK_SAMPLES)
    spo2    = _load_or_zeros(spo2_path,    CHUNK_SAMPLES)
    airflow = _load_or_zeros(airflow_path, CHUNK_SAMPLES)
    effort  = _load_or_zeros(effort_path,  CHUNK_SAMPLES)
    return np.stack([snoring, spo2, airflow, effort], axis=0)  # (4, 30000)


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

            # ── 信号路径 ──────────────────────────────────────────────────────
            # 通道 0：鼾声（已有，必须存在）
            snoring_dir = os.path.join(patient_dir, 'data', 'txt')
            # 通道 1：SpO2（可选，PSG 设备导出后放入 data/spo2/ 目录）
            spo2_dir    = os.path.join(patient_dir, 'data', 'spo2')
            # 通道 2：口鼻气流（可选，PSG 设备导出后放入 data/airflow/ 目录）
            airflow_dir = os.path.join(patient_dir, 'data', 'airflow')
            # 通道 3：胸部呼吸运动（可选，PSG 设备导出后放入 data/effort/ 目录）
            effort_dir  = os.path.join(patient_dir, 'data', 'effort')

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
                    spo2_path    = os.path.join(spo2_dir,    fname) if os.path.isdir(spo2_dir)    else None
                    airflow_path = os.path.join(airflow_dir, fname) if os.path.isdir(airflow_dir) else None
                    effort_path  = os.path.join(effort_dir,  fname) if os.path.isdir(effort_dir)  else None

                    data = build_chunk(snoring_path, spo2_path, airflow_path, effort_path)
                    record = {'data': data, 'severity': severity_label}

                    # 文件名：<严重程度>_<患者ID>_<分段名>.npy
                    save_name = f'{severity_name}_{patient_id}_{base}.npy'
                    np.save(os.path.join(out_dir, save_name), record, allow_pickle=True)

    print('\n数据集构建完成。')
    print(f'训练集: {train_path}')
    print(f'测试集: {test_path}')
