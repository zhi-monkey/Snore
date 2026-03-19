import torch
import torch.nn as nn
import torch.nn.functional as F

    
class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


class ChannelAttention(nn.Module):
    def __init__(self, input_channels, reduction_ratio=16):
        super(ChannelAttention, self).__init__()
        self.input_channels = input_channels
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.max_pool = nn.AdaptiveMaxPool1d(1)

        self.MLP = nn.Sequential(
            Flatten(),
            nn.Linear(input_channels, input_channels // reduction_ratio),
            nn.ReLU(),
            nn.Linear(input_channels // reduction_ratio, input_channels),
        )

    def forward(self, x):
        # Take the input and apply average and max pooling
        avg_values = self.avg_pool(x)
        max_values = self.max_pool(x)
        out = self.MLP(avg_values) + self.MLP(max_values)
        scale = x * torch.sigmoid(out).unsqueeze(-1).expand_as(x)
        return scale


class SpatialAttention(nn.Module):
    def __init__(self):
        super(SpatialAttention, self).__init__()
        self.conv = nn.Conv1d(2, 1, kernel_size=9, padding=4, bias=False)
        self.bn = nn.BatchNorm1d(1)

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        out = torch.cat([avg_out, max_out], dim=1)
        out = self.conv(out)
        out = self.bn(out)
        scale = x * torch.sigmoid(out)
        return scale


class CBAM(nn.Module):
    def __init__(self, input_channels, reduction_ratio=16):
        super(CBAM, self).__init__()
        self.channel_att = ChannelAttention(input_channels, reduction_ratio=reduction_ratio)
        self.spatial_att = SpatialAttention()

    def forward(self, x):
        out = self.channel_att(x)
        out = self.spatial_att(out)
        return out

class Residual(nn.Module):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def forward(self, x):
        return self.fn(x) + x
class ConvMixerBlock(nn.Module):
    def __init__(self, dim, depth=3):
        super(ConvMixerBlock, self).__init__()
        self.block = nn.Sequential(
            *[nn.Sequential(
                Residual(nn.Sequential(
                    nn.Conv1d(dim,dim,kernel_size=3,stride=1,padding=1),
                    nn.ReLU(),
                    nn.BatchNorm1d(dim)
                )),
                nn.Conv1d(dim, dim, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.BatchNorm1d(dim)
            ) for i in range(depth)]
        )

    def forward(self, x):
        x = self.block(x)
        return x
    

class ConvBnRelu1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=9, padding=4):
        super().__init__()

        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding=padding)
        self.bn = nn.BatchNorm1d(out_channels)
        self.relu = nn.LeakyReLU()
        self.do = nn.Dropout1d(0.2)
        self.conv1 = nn.Conv1d(out_channels,out_channels,kernel_size=3,stride=1,padding=1)
        self.conv2 = ConvMixerBlock(out_channels)

        self.cbam = CBAM(out_channels)

    def forward(self, x):
        x1 = self.conv(x)
        x2 = self.bn(x1)
        x2 = self.relu(x2)
        
        x2_1 = self.do(x1+x2)
        x3 = self.conv2(x1)
        x = self.cbam(x2_1+x3)
        
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


class UNet(nn.Module):
    def __init__(self, n_channels=2):
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
        self.segment = nn.Conv1d(filters_decoder, 2, kernel_size=1, padding=0)

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

        x = self.segment(X_dec1)
        return x

