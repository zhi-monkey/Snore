import os

import torch
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
import torch.nn as nn

from dataset import SnoreDataset
from models import unet_cbam, unet
from utils import FocalLoss, EarlyStopping, set_seed
import matplotlib.pylab as plt
from models import DenseNet



def train(model, device, train_loader, criterion, optimizer):
    model.train()
    train_loss = 0
    n_train = len(train_loader.dataset)

    for data, label in tqdm(train_loader):
        data, label = data.to(device), label.to(device)
        outputs = model(data)
        print(outputs.size())
        optimizer.zero_grad()
        loss = criterion(outputs, label)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * len(data)

        out_t = torch.max(outputs, dim=1)[1]

    train_loss = train_loss / n_train
    return train_loss


def evaluate(model, device, test_loader, criterion):
    model.eval()
    test_loss = 0
    n_test = len(test_loader.dataset)
    for data, label in tqdm(test_loader):
        data, label = data.to(device), label.to(device)
        outputs = model(data)
        loss = criterion(outputs, label)
        test_loss += loss.item() * len(data)


    test_loss = test_loss / n_test
    return test_loss


if __name__ == '__main__':
    set_seed(3407)
    # 检查是否有可用的 GPU 设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 输出当前使用的设备
    print("Using device:", device)

    if device.type == 'cuda':
        print("Memory allocated on GPU:", torch.cuda.memory_allocated(device))
        print("Memory cached on GPU:", torch.cuda.memory_reserved(device))

    loss_path = './loss/'
    if not os.path.exists(loss_path):
        os.makedirs(loss_path)

    train_path = './data/train/'
    train_dataset = SnoreDataset(train_path)

    m = len(train_dataset)
    train_data, valid_data = random_split(train_dataset, [m - int(0.2 * m), int(0.2 * m)],
                                          generator=torch.Generator().manual_seed(3407))
    batch_size = 8
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)
    valid_loader = torch.utils.data.DataLoader(valid_data, batch_size=batch_size, shuffle=False)

    lr = 1e-5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    model = unet_cbam.ECGUNet(n_channels=32).to(device)
    criterion = FocalLoss().to(device)
    #criterion = nn.CrossEntropyLoss()
    loss_function = FocalLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-07)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50, eta_min=1e-6, verbose=True)
    early_stopping = EarlyStopping(patience=15, verbose=True, delta=1e-4,
                                   path='best_model_cbam.pt')
    train_loss_list=[]
    valid_loss_list=[]
    for epoch in range(300):
        train_loss = train(model, device, train_loader, criterion, optimizer)
        valid_loss = evaluate(model, device, valid_loader, criterion)
        train_loss_list.append(train_loss)
        valid_loss_list.append(valid_loss)
        scheduler.step()
        
        print(f'Epoch {epoch + 1} -- Train Loss: {train_loss:.4f}   Valid Loss: {valid_loss:.4f}')


        early_stopping(valid_loss, model)
        if early_stopping.early_stop:
            break
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, epoch + 2), train_loss_list, label='Train Loss')
        plt.plot(range(1, epoch + 2), valid_loss_list, label='Valid Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Loss')
        plt.legend()
        plt.savefig('./result/loss_plot.png')
        plt.close()
