"""
训练脚本：基于多通道 PSG 信号对 OSA 严重程度进行四分类。

──────────────────────────────────────────────────────
模型：ResNet50（一维卷积版本）
  in_channels = 4   （4个PSG通道）
  classes     = 4   （正常、轻度OSA、中度OSA、重度OSA）

PSG 输入通道：
  0 - 鼾声/呼吸音频  (500 Hz)
  1 - 血氧饱和度 SpO2
  2 - 口鼻气流
  3 - 胸部呼吸运动

预测类别（OSA 严重程度）：
  0 - 正常    (AHI < 5)
  1 - 轻度OSA (5 ≤ AHI < 15)
  2 - 中度OSA (15 ≤ AHI < 30)
  3 - 重度OSA (AHI ≥ 30)
──────────────────────────────────────────────────────

运行前请先执行 build_dataset_osa.py 构建数据集。
"""

import datetime
import itertools
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

from dataset_osa import OSASeverityDataset, SEVERITY_LABELS
from models.ResNet50 import ResNet50

# ── OSA 严重程度标签 ──────────────────────────────────────────────────────────
CLASS_NAMES = SEVERITY_LABELS          # ['正常', '轻度OSA', '中度OSA', '重度OSA']
NUM_CLASSES  = len(CLASS_NAMES)        # 4
IN_CHANNELS  = 4                       # PSG 通道数


# ── 早停 ──────────────────────────────────────────────────────────────────────
class EarlyStopping:
    def __init__(self, patience=50, verbose=False, delta=0,
                 path='./end_model.pth', trace_func=print):
        self.patience   = patience
        self.verbose    = verbose
        self.counter    = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.threshold  = delta
        self.path       = path
        self.trace_func = trace_func

    def __call__(self, val_loss, model):
        score = -val_loss
        if self.best_score is None:
            self.best_score = score
            self._save(val_loss, model)
        elif score < self.best_score + self.threshold:
            self.counter += 1
            self.trace_func(f'早停计数: {self.counter} / {self.patience}\n')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self._save(val_loss, model)
            self.counter = 0

    def _save(self, val_loss, model):
        if self.verbose:
            self.trace_func(
                f'验证集损失下降 ({self.val_loss_min:.5f} --> {val_loss:.5f}). 保存模型...\n'
            )
        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss


# ── 工具函数：绘制并保存混淆矩阵 ─────────────────────────────────────────────
def _plot_confusion_matrix(cm, labels, save_path, percent=False):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set_title('Confusion Matrix')
    tick_marks = np.arange(len(labels))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    thresh = cm.max() * 0.5
    fmt = '{:.1%}' if percent else 'd'
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        val = fmt.format(cm[i, j]) if percent else format(cm[i, j], 'd')
        ax.text(j, i, val, ha='center',
                color='white' if cm[i, j] > thresh else 'black')
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


# ── 主训练流程 ────────────────────────────────────────────────────────────────
def main():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f'使用设备: {device}')

    # ── 数据集 ────────────────────────────────────────────────────────────────
    train_dir = './data_osa/train/'
    dataset   = OSASeverityDataset(train_dir)

    m = len(dataset)
    train_data, valid_data = random_split(
        dataset,
        [m - int(0.2 * m), int(0.2 * m)],
        generator=torch.Generator().manual_seed(3407),
    )
    train_num = len(train_data)
    valid_num = len(valid_data)
    print(f'训练集: {train_num} 条，验证集: {valid_num} 条')

    batch_size = 32
    nw = min(os.cpu_count(), batch_size, 64)
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True,  num_workers=nw)
    valid_loader = DataLoader(valid_data, batch_size=batch_size, shuffle=False, num_workers=nw)

    # ── 模型 ──────────────────────────────────────────────────────────────────
    # 修改点：in_channels=4（PSG 通道数），classes=4（OSA 严重程度），
    #          dropout=0.5 防止在有限医疗数据上过拟合
    net = ResNet50(in_channels=IN_CHANNELS, classes=NUM_CLASSES, dropout=0.5).to(device)
    net_name    = net.__class__.__name__
    folder_name = 'osa_severity/' + net_name
    os.makedirs(folder_name, exist_ok=True)

    # ── 损失函数 ──────────────────────────────────────────────────────────────
    loss_fn = nn.CrossEntropyLoss().to(device)

    # ── 优化器 & 学习率调度 ───────────────────────────────────────────────────
    lr_init   = 1e-3
    optimizer = torch.optim.Adam(net.parameters(), lr=lr_init)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lr_lambda=lambda epoch: 1 / (epoch + 1)
    )

    # ── 早停 ──────────────────────────────────────────────────────────────────
    early_stopping = EarlyStopping(
        patience=50, verbose=True, delta=1e-4,
        path=os.path.join(folder_name, f'end_{net_name}.pth'),
    )

    epochs    = 1000
    save_path = os.path.join(folder_name, f'best_{net_name}.pth')
    best_acc  = 0.0

    train_losses, valid_losses = [], []
    train_acces, valid_acces   = [], []
    precisions, recalls, f1_scores = [], [], []

    logpath = os.path.join(folder_name, datetime.datetime.now().strftime('%Y_%m_%d_'))
    os.makedirs(logpath, exist_ok=True)
    mylog = open(os.path.join(logpath, 'logs.txt'), 'a')

    start = time.time()

    for epoch in range(epochs):
        # ── 训练阶段 ──────────────────────────────────────────────────────────
        net.train()
        running_loss = 0.0
        train_acc    = 0.0
        n = 0
        train_bar = tqdm(train_loader, file=sys.stdout)
        for data, labels in train_bar:
            data   = data.to(device,   dtype=torch.float)
            labels = labels.to(device, dtype=torch.long).view(-1)

            outputs = net(data)
            loss    = loss_fn(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            train_acc    += torch.eq(torch.max(outputs, dim=1)[1], labels).sum().item()
            train_bar.desc = f'训练 [{epoch+1}/{epochs}] Loss: {loss:.3f}'
            n += 1

        train_accurate = train_acc    / train_num
        train_loss     = running_loss / n
        train_losses.append(train_loss)
        train_acces.append(train_accurate)

        # ── 验证阶段 ──────────────────────────────────────────────────────────
        net.eval()
        predictions, true_labels = [], []
        valid_acc  = 0.0
        valid_loss = 0.0
        m_val = 0

        with torch.no_grad():
            for data, labels in tqdm(valid_loader, file=sys.stdout):
                data   = data.to(device,   dtype=torch.float)
                labels = labels.to(device, dtype=torch.long).view(-1)

                outputs  = net(data)
                loss     = loss_fn(outputs, labels)
                valid_loss += loss.item()

                predict_y = torch.max(outputs, dim=1)[1]
                valid_acc += torch.eq(predict_y, labels).sum().item()
                m_val += 1

                predictions.extend(predict_y.tolist())
                true_labels.extend(labels.tolist())

        valid_accurate = valid_acc  / valid_num
        valid_loss     = valid_loss / m_val
        valid_losses.append(valid_loss)
        valid_acces.append(valid_accurate)

        print(
            f'[epoch {epoch+1}] '
            f'训练损失: {train_loss:.4f}  训练准确率: {train_accurate:.4f}  '
            f'验证损失: {valid_loss:.4f}  验证准确率: {valid_accurate:.4f}'
        )

        # ── 混淆矩阵（计数） ──────────────────────────────────────────────────
        cm = confusion_matrix(true_labels, predictions)
        _plot_confusion_matrix(
            cm, CLASS_NAMES,
            os.path.join(folder_name, 'confusion_matrix_valid.png'),
        )

        # ── 混淆矩阵（百分比） ────────────────────────────────────────────────
        row_sums = cm.sum(axis=1, keepdims=True)
        pct = np.where(row_sums > 0, cm / row_sums, 0.0)
        _plot_confusion_matrix(
            pct, CLASS_NAMES,
            os.path.join(folder_name, 'confusion_matrix_valid_percentages.png'),
            percent=True,
        )

        # ── Precision / Recall / F1 ───────────────────────────────────────────
        tp = np.diag(cm)
        precision_per = np.where(cm.sum(axis=0) > 0, tp / cm.sum(axis=0), 0.0)
        recall_per    = np.where(cm.sum(axis=1) > 0, tp / cm.sum(axis=1), 0.0)
        denom = precision_per + recall_per
        f1_per = np.where(denom > 0,
                          2 * precision_per * recall_per / denom, 0.0)
        precision = precision_per.mean()
        recall    = recall_per.mean()
        f1        = f1_per.mean()

        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        print(f'[epoch {epoch+1}] Precision: {precision:.4f}  Recall: {recall:.4f}  F1: {f1:.4f}')

        # ── 曲线图 ────────────────────────────────────────────────────────────
        for data_a, data_b, ylabel, title, fname in [
            (train_losses, valid_losses, 'Loss',     'Train & Valid Loss',     'loss_plot.png'),
            (train_acces,  valid_acces,  'Accuracy', 'Train & Valid Accuracy', 'accuracy_plot.png'),
        ]:
            plt.figure()
            plt.plot(range(1, len(data_a) + 1), data_a, label='Train')
            plt.plot(range(1, len(data_b) + 1), data_b, label='Valid')
            plt.xlabel('Epoch')
            plt.ylabel(ylabel)
            plt.title(title)
            plt.legend()
            plt.savefig(os.path.join(folder_name, fname))
            plt.close()

        plt.figure(figsize=(8, 6))
        plt.plot(range(1, epoch + 2), f1_scores)
        plt.title('F1-Score vs Epochs')
        plt.xlabel('Epochs')
        plt.ylabel('F1-Score')
        plt.grid(True)
        plt.savefig(os.path.join(folder_name, 'f1score_vs_epochs.png'))
        plt.close()

        # ── 保存最优模型 ──────────────────────────────────────────────────────
        if valid_accurate > best_acc:
            best_acc = valid_accurate
            torch.save(net.state_dict(), save_path)

        early_stopping(valid_loss, net)
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mylog.write(
            f'[{nowtime}] [epoch {epoch+1}] '
            f'训练损失: {train_loss:.4f}  训练准确率: {train_accurate:.4f}  '
            f'验证损失: {valid_loss:.4f}  验证准确率: {valid_accurate:.4f}\n'
        )
        mylog.flush()

        scheduler.step()

        if early_stopping.early_stop:
            break

    mylog.close()
    print('训练结束')
    print(f'训练时长: {time.time() - start:.2f}s')


if __name__ == '__main__':
    main()
