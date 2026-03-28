# Snore — 睡眠鼾声与体位识别系统

本项目基于患者的呼吸/鼾声音频信号，使用深度学习模型进行**睡眠体位（body position）分类**以及**阻塞性睡眠呼吸暂停（OSA）事件检测**。

---

## ResNet 模型说明

### 输入数据

- **数据类型**：患者的鼾声/呼吸音频信号，经采集后以 `.txt` 格式保存（每行包含时间戳与幅度值两列），再转换为 `.npy` 格式供训练使用。
- **数据形状**：一维时间序列（1D time-series），形状为 `(batch_size, channels, sequence_length)`。
- **通道数**：4 个输入通道（`in_channels=4`），对应多路传感器采集的信号。
- **原始数据来源**：`未处理患者数据/` 目录，按患者和病例组织，包含不同严重程度（如中度）的睡眠数据。

### 模型结构

`models/ResNet50.py` 实现了一个**一维 ResNet50**（`Conv1d` 版本），结构与标准 ResNet50 相同，但所有卷积层均为一维卷积，适用于时序信号处理。主要组件：

- **Bottleneck 模块**：1×1 → 3×1 → 1×1 的瓶颈卷积结构，含残差连接。
- **全局平均池化**：`AdaptiveAvgPool1d(1)`，将时序特征压缩为固定长度向量。
- **分类头**：`Linear(2048, num_classes)`，输出各类别的 logits。

### 预测任务

ResNet50 对患者的鼾声/呼吸信号进行**睡眠体位（sleep body position）多分类预测**，共 **6 个类别**：

| 类别标签   | 含义                                  |
|------------|---------------------------------------|
| `up`       | 仰卧                                  |
| `down`     | 俯卧                                  |
| `left_log` | 左侧卧（硬板，log 为硬板的英文缩写）  |
| `right_log`| 右侧卧（硬板，log 为硬板的英文缩写）  |
| `left`     | 左侧卧                                |
| `right`    | 右侧卧                                |

模型使用交叉熵损失（`CrossEntropyLoss`）进行训练，输出为 6 维 logit 向量，取 argmax 即为预测的睡眠体位类别。

---

## 其他模型

| 模型         | 文件                        | 用途                                  |
|--------------|-----------------------------|---------------------------------------|
| DenseNet     | `models/DenseNet.py`        | 睡眠体位分类（同 ResNet，6 分类）     |
| UNet (CBAM)  | `models/unet_cbam.py`       | 逐点 OSA 事件检测（二分类：正常/呼吸暂停） |

---

## 数据集与代码下载

Dataset：
通过网盘分享的文件：未处理患者数据.zip
链接: https://pan.baidu.com/s/1qUGvMGjHxkfoBp_0kWjEKA 提取码: mz4y

Codes：
通过网盘分享的文件：Snore.zip
链接: https://pan.baidu.com/s/1yqvK2uKeqZu7HRMgGT09jw 提取码: b2ff
