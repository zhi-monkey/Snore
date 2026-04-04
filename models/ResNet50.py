"""
ResNet50 (1D) — 一维残差网络，支持睡眠体位分类与 OSA 严重程度分类两种任务。

输入数据：形状为 (batch, in_channels, seq_len) 的一维时序信号。

──────────────────────────────────────────────────────────────────────────────
任务一：睡眠体位分类（原始用途）
    in_channels = 4  （多路鼾声/呼吸传感器）
    classes     = 6
    标签：0-up 仰卧  1-down 俯卧  2-left_log 左侧卧(硬板)
          3-right_log 右侧卧(硬板)  4-left 左侧卧  5-right 右侧卧

──────────────────────────────────────────────────────────────────────────────
任务二：OSA 严重程度四分类
    in_channels = 1  （单通道鼾声/呼吸音频，500 Hz）
    classes     = 4
    标签：0-正常 (AHI<5)  1-轻度OSA (5≤AHI<15)
          2-中度OSA (15≤AHI<30)  3-重度OSA (AHI≥30)

    需要修改的参数（相对于体位分类任务）：
        in_channels: 4  →  1   （单通道鼾声/呼吸信号）
        classes:     6  →  4   （分类数由体位6类改为严重程度4类）
        dropout:  建议 0.5      （医疗数据量有限，Dropout 有助于防止过拟合）
──────────────────────────────────────────────────────────────────────────────
"""
import torch


class Bottlrneck(torch.nn.Module):
    def __init__(self,In_channel,Med_channel,Out_channel,downsample=False):
        super(Bottlrneck, self).__init__()
        self.stride = 1
        if downsample == True:
            self.stride = 2

        self.layer = torch.nn.Sequential(
            torch.nn.Conv1d(In_channel, Med_channel, 1, self.stride),
            torch.nn.BatchNorm1d(Med_channel),
            torch.nn.ReLU(),
            torch.nn.Conv1d(Med_channel, Med_channel, 3, padding=1),
            torch.nn.BatchNorm1d(Med_channel),
            torch.nn.ReLU(),
            torch.nn.Conv1d(Med_channel, Out_channel, 1),
            torch.nn.BatchNorm1d(Out_channel),
            torch.nn.ReLU(),
        )

        if In_channel != Out_channel:
            self.res_layer = torch.nn.Conv1d(In_channel, Out_channel,1,self.stride)
        else:
            self.res_layer = None

    def forward(self,x):
        if self.res_layer is not None:
            residual = self.res_layer(x)
        else:
            residual = x
        return self.layer(x)+residual


class ResNet50(torch.nn.Module):
    def __init__(self, in_channels, classes, dropout=0.0):
        """
        Args:
            in_channels (int): 输入信号通道数。
                体位分类任务: 4（多路传感器）
                OSA 严重程度任务: 1（单通道鼾声/呼吸音频，500 Hz）
            classes (int): 输出分类数。
                体位分类任务: 6
                OSA 严重程度任务: 4
            dropout (float): 分类头中 Dropout 的丢弃概率，默认 0.0（不丢弃）。
                体位分类任务保持默认 0.0 以与原始行为兼容。
                OSA 任务建议设为 0.5：医疗数据量通常有限，Dropout 有助于防止过拟合。
                示例：ResNet50(in_channels=1, classes=4, dropout=0.5)
        """
        super(ResNet50, self).__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels,64,kernel_size=7,stride=2,padding=3),
            torch.nn.MaxPool1d(3,2,1),

            Bottlrneck(64,64,256,False),
            Bottlrneck(256,64,256,False),
            Bottlrneck(256,64,256,False),
            #
            Bottlrneck(256,128,512, True),
            Bottlrneck(512,128,512, False),
            Bottlrneck(512,128,512, False),
            Bottlrneck(512,128,512, False),
            #
            Bottlrneck(512,256,1024, True),
            Bottlrneck(1024,256,1024, False),
            Bottlrneck(1024,256,1024, False),
            Bottlrneck(1024,256,1024, False),
            Bottlrneck(1024,256,1024, False),
            Bottlrneck(1024,256,1024, False),
            #
            Bottlrneck(1024,512,2048, True),
            Bottlrneck(2048,512,2048, False),
            Bottlrneck(2048,512,2048, False),

            torch.nn.AdaptiveAvgPool1d(1)
        )
        # 分类头：加入 Dropout，防止在医疗数据（样本量有限）上过拟合
        self.classifer = torch.nn.Sequential(
            torch.nn.Dropout(p=dropout),
            torch.nn.Linear(2048, classes)
        )

    def forward(self,x):
        x = self.features(x)
        x = x.view(x.size(0), -1)  # (batch, 2048)
        x = self.classifer(x)
        return x

if __name__ == '__main__':
    # 输入形状：(batch, in_channels, seq_len)
    # in_channels 在前（PyTorch Conv1d 约定），seq_len 在后

    # ── 任务一：睡眠体位分类 ─────────────────────────────────────────────────
    x = torch.randn(size=(2, 4, 30000))          # batch=2, 4通道, 30000采样点
    model = ResNet50(in_channels=4, classes=6)   # 6种体位，默认 dropout=0.0（不丢弃）
    print('体位分类输出形状:', model(x).shape)   # → (2, 6)

    # ── 任务二：OSA 严重程度四分类 ──────────────────────────────────────────
    # 修改点：in_channels 由 4 改为 1（单通道鼾声/呼吸信号）
    #          classes  由 6 改为 4；显式传入 dropout=0.5 防止过拟合
    x_osa = torch.randn(size=(2, 1, 30000))      # batch=2, 单通道, 30000采样点
    model_osa = ResNet50(in_channels=1, classes=4, dropout=0.5)
    print('OSA分级输出形状:', model_osa(x_osa).shape)  # → (2, 4)
