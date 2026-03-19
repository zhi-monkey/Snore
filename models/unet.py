import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary


class se_net(nn.Module):
    def __init__(self, channel, reduction=16):
        super(se_net, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.excitation(y).view(b, c, 1)
        return x * y.expand_as(x)


class ConvBnRelu1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=9, padding=4):
        super().__init__()
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding=padding)
        self.bn = nn.BatchNorm1d(out_channels)
        self.relu = nn.LeakyReLU()
        self.do = nn.Dropout1d(0.2)

        self.se_block = se_net(out_channels)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        x = self.do(x)
        x = self.se_block(x)
        return x


class StackEncoder(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=9, padding=4):
        super().__init__()
        self.conv1 = ConvBnRelu1d(in_channels, out_channels, kernel_size=kernel_size, padding=padding)
        self.conv2 = ConvBnRelu1d(out_channels, out_channels, kernel_size=kernel_size, padding=padding)
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        return x, self.pool(x)


class StackDecoder(nn.Module):
    def __init__(self, in_channels, skip_channels, out_channels, kernel_size=9, padding=4):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels[0], skip_channels, kernel_size=kernel_size, padding=padding)
        self.conv2 = nn.Conv1d(in_channels[1], skip_channels, kernel_size=kernel_size, padding=padding)
        self.conv3 = nn.Conv1d(in_channels[2], skip_channels, kernel_size=kernel_size, padding=padding)
        self.conv4 = nn.Conv1d(in_channels[3], skip_channels, kernel_size=kernel_size, padding=padding)
        self.conv5 = nn.Conv1d(in_channels[4], skip_channels, kernel_size=kernel_size, padding=padding)
        self.aggregate = ConvBnRelu1d(skip_channels * 5, out_channels, kernel_size=kernel_size, padding=padding)

    def forward(self, x1, x2, x3, x4, x5):
        x1 = self.conv1(x1)
        x2 = self.conv2(x2)
        x3 = self.conv3(x3)
        x4 = self.conv4(x4)
        x5 = self.conv5(x5)

        x = torch.cat((x1, x2, x3, x4, x5), dim=1)
        x = self.aggregate(x)
        return x


class ECGUNet(nn.Module):
    def __init__(self, n_channels=4):
        super().__init__()

        filters = [n_channels * (2 ** n) for n in range(5)]
        filters_skip = filters[0]
        filters_decoder = filters_skip * 5

        self.down1 = StackEncoder(1, filters[0])
        self.down2 = StackEncoder(filters[0], filters[1])
        self.down3 = StackEncoder(filters[1], filters[2])
        self.down4 = StackEncoder(filters[2], filters[3])
        self.middle = nn.Sequential(ConvBnRelu1d(filters[3], filters[4]), ConvBnRelu1d(filters[4], filters[4]))

        self.up4 = StackDecoder(filters, filters_skip, filters_decoder)
        self.up3 = StackDecoder(filters[:3] + [filters_decoder] * 1 + filters[4:], filters_skip, filters_decoder)
        self.up2 = StackDecoder(filters[:2] + [filters_decoder] * 2 + filters[4:], filters_skip, filters_decoder)
        self.up1 = StackDecoder(filters[:1] + [filters_decoder] * 3 + filters[4:], filters_skip, filters_decoder)
        self.segment = nn.Conv1d(filters_decoder, 4, kernel_size=1, padding=0)

    def forward(self, x):
        X_enc1, x = self.down1(x)
        X_enc2, x = self.down2(x)
        X_enc3, x = self.down3(x)
        X_enc4, x = self.down4(x)
        X_enc5 = self.middle(x)

        X_dec5 = X_enc5
        X_dec4 = self.up4(
            F.max_pool1d(X_enc1, kernel_size=8, stride=8),
            F.max_pool1d(X_enc2, kernel_size=4, stride=4),
            F.max_pool1d(X_enc3, kernel_size=2, stride=2),
            X_enc4,
            F.interpolate(X_dec5, size=X_enc4.shape[-1], mode='linear', align_corners=False)
        )
        X_dec3 = self.up3(
            F.max_pool1d(X_enc1, kernel_size=4, stride=4),
            F.max_pool1d(X_enc2, kernel_size=2, stride=2),
            X_enc3,
            F.interpolate(X_dec4, size=X_enc3.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec5, size=X_enc3.shape[-1], mode='linear', align_corners=False)
        )
        X_dec2 = self.up2(
            F.max_pool1d(X_enc1, kernel_size=2, stride=2),
            X_enc2,
            F.interpolate(X_dec3, size=X_enc2.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec4, size=X_enc2.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec5, size=X_enc2.shape[-1], mode='linear', align_corners=False)
        )
        X_dec1 = self.up1(
            X_enc1,
            F.interpolate(X_dec2, size=X_enc1.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec3, size=X_enc1.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec4, size=X_enc1.shape[-1], mode='linear', align_corners=False),
            F.interpolate(X_dec5, size=X_enc1.shape[-1], mode='linear', align_corners=False)
        )
        return self.segment(X_dec1)


if __name__ == '__main__':
    n_channels = 16
    filters = [n_channels * (2 ** n) for n in range(5)]
    print(f'filters: {filters}')

    inputs = torch.randn(size=(1, 1, 5000))
    model = ECGUNet(n_channels=32)
    print(model(inputs).shape)

    summary(model, input_size=inputs.shape, device='cpu')
