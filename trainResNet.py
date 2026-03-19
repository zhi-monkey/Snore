import datetime
import os
import sys
import time
import torch
import matplotlib.pyplot as plt
import numpy as np
import itertools
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from models import DenseNet
from dataset import SnoreDataset
from torch.utils.data import DataLoader, random_split



def main():
    # 定义训练的设备
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    train_path = './data/train/'
    train_dataset = SnoreDataset(train_path)

    m = len(train_dataset)
    train_data, valid_data = random_split(train_dataset, [m - int(0.2 * m), int(0.2 * m)],
                                          generator=torch.Generator().manual_seed(3407))

    # length 长度
    train_num = len(train_data)
    valid_num = len(valid_data)
    print("训练数据集的长度为：{}".format(train_num))
    print("验证数据集的长度为：{}".format(valid_num))

    # 利用 DataLoader 来加载数据集
    batch_size = 32  # 即一次加载数据的数目
    nw = min([os.cpu_count(), batch_size if batch_size > 0 else 0, 64]) #进程数
    print('使用 {} 个进程同时进行训练'.format(nw))
    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=nw)
    valid_dataloader = DataLoader(valid_data, batch_size=batch_size, shuffle=False, num_workers=nw)

    # 创建网络模型
    # net = ResNet34().to(device)
    net = DenseNet().to(device)
    # net = VGG19().to(device)
    # net = PointNet().to(device)
    # net = PointNet_breath().to(device)
    net = PointNet1().to(device)
    # net = blstm().to(device)
    
    net_name = net.__class__.__name__
    folder_name = 'breath_point/' + net_name
    os.makedirs(folder_name, exist_ok=True)
    
    # 损失函数
    loss_fn = nn.CrossEntropyLoss().to(device)
    
    # 优化器
    lr_init =1e-3
    # optimizer = torch.optim.SGD(net.parameters(), lr=lr_init, weight_decay=1e-3, momentum=0.9) 
    optimizer = torch.optim.Adam(net.parameters(), lr=lr_init) 
    # optimizer = torch.optim.RAdam(net.parameters(), lr=lr_init, weight_decay=6e-5) 
    # optimizer = torch.optim.NAdam(net.parameters(), lr=lr_init ,weight_decay=6e-6) 
    # 优化器衰减策略
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda epoch: 1/(epoch+1))
    # scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9) #指数 
    # scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[10], gamma=0.5)
    # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100, eta_min=0) #余弦退火
    # 早停配置
    early_stopping = EarlyStopping(patience=50, verbose=True, delta=1e-4, path=os.path.join(folder_name, 'end_' + net_name + '.pth'))

    epochs = 1000  # 训练的次数
    save_path = os.path.join(folder_name, 'best_' + net_name + '.pth')  # 保存训练权重文件
    best_acc = 0.0    #最佳的准确率

    train_acces = []    #训练集准确率
    train_losses = []   #训练集损失
    valid_acces = []     #验证集准确率
    valid_losses = []    #验证集损失
    precisions = []
    recalls = []
    f1_scores = []
    
    current_data = datetime.datetime.now().strftime('%Y_%m_%d_')
    logpath = os.path.join(folder_name, current_data)
    os.makedirs(logpath, exist_ok=True)
    logsavename = 'logs.txt'
    mylog = open(os.path.join(logpath, logsavename), 'a')
    
    # model_path = os.path.join(folder_name, 'best1_' + net_name + '.pth')
    # net.load_state_dict(torch.load(model_path))  
################################################################################
    # 模型开始训练
    start = time.time() #开始时间
    for epoch in range(epochs):
        n = 0
        net.train()
        running_loss = 0.0
        train_acc = 0.0 #训练集准确率
        train_bar = tqdm(train_dataloader, file=sys.stdout)
        for data in train_bar:
            datas, labels = data['data'], data['label']
            datas = datas.to(device, dtype=torch.float)
            labels = labels.to(device, dtype=torch.long)
            labels = labels.view(-1)
            outputs1 = net(datas)  #调用模型
            # outputs1, _, _ = net(datas)
            # print(outputs1.size())
            loss = loss_fn(outputs1, labels)  #损失
            # 优化器优化模型
            optimizer.zero_grad()  # 先将梯度归零
            loss.backward()  #然后反向传播计算得到每个参数的梯度值
            optimizer.step()  #通过梯度下降执行一步参数更新

            running_loss += loss.item()  #存下每一次的损失
            out_t = torch.max(outputs1, dim=1)[1]
            train_acc += torch.eq(out_t, labels.to(device)).sum().item()
            train_bar.desc = "训练次数:[{}/{}] 损失:{:.3f}".format(epoch + 1,epochs,loss)
            n +=1

        train_accurate = train_acc / train_num #训练集准确率
        train_loss = running_loss / n #训练集损失
        train_losses.append(train_loss)
        train_acces.append(train_accurate)

########################################################################
        # 用验证集验证模型的性能
        # 计算混淆矩阵
        predictions = []
        true_labels = []
        m = 0
        net.eval()
        valid_acc = 0.0  #验证集准确率
        valid_loss = 0.0
        with torch.no_grad():
            valid_bar = tqdm(valid_dataloader, file=sys.stdout)
            for valid_data in valid_bar:
                valid_data, valid_labels = valid_data['data'], valid_data['label']
                valid_data = valid_data.to(device, dtype=torch.float)
                valid_labels = valid_labels.to(device, dtype=torch.long)
                valid_labels = valid_labels.view(-1)
                outputs2 = net(valid_data)
                # outputs2, _, _ = net(valid_data)
                loss = loss_fn(outputs2, valid_labels)  # 损失

                valid_loss += loss.item()
                predict_y = torch.max(outputs2, dim=1)[1]
                valid_acc += torch.eq(predict_y, valid_labels.to(device)).sum().item()
                m +=1
                
                #混淆矩阵预测及标签
                predictions.extend(predict_y.tolist())
                true_labels.extend(valid_labels.tolist())
                
        valid_accurate = valid_acc / valid_num
        valid_loss = valid_loss / m
        print('[epoch %d] 训练集损失: %.4f  训练集准确率: %.4f 验证集损失: %.4f  验证集准确率: %.4f' %(epoch + 1, train_loss, train_accurate, valid_loss, valid_accurate))
        valid_losses.append(valid_loss)
        valid_acces.append(valid_accurate)

        # 绘制混淆矩阵图像
        cm = confusion_matrix(true_labels, predictions)
        labels = ['up', 'down', 'left_log', 'right_log', 'left', 'right']  # 标签列表
        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()
        tick_marks = np.arange(len(labels))
        plt.xticks(tick_marks, labels)
        plt.yticks(tick_marks, labels)
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        # 在每个格子中添加数值标签
        thresh = cm.max() / 2.0
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], 'd'),
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black")
        # 保存混淆矩阵图像
        plt.tight_layout()
        plt.savefig(os.path.join(folder_name, 'confusion_matrix_valid.png'))
        plt.show()
        plt.close()  # 关闭当前图形窗口
        
        cm = confusion_matrix(true_labels, predictions)
        labels = ['up', 'down', 'leftlog', 'rightlog', 'left', 'right']
        row_sums = cm.sum(axis=1)
        # 计算每一行（真实类别）的比例
        percentages = cm / row_sums[:, np.newaxis]
        plt.figure(figsize=(8, 6))
        plt.imshow(percentages, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar(ticks=np.linspace(0.0, 1.0, 11), format='%.1f')
        tick_marks = np.arange(len(labels))
        plt.xticks(tick_marks, labels)
        plt.yticks(tick_marks, labels)
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        # 在每个格子中添加百分比标签
        thresh = percentages.max() * 0.5
        fmt = '{:.1%}'  # 格式化字符串为百分比形式
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, fmt.format(percentages[i, j]),
                    horizontalalignment="center",
                    color="white" if percentages[i, j] > thresh else "black")
        plt.tight_layout()
        plt.savefig(os.path.join(folder_name, 'confusion_matrix_valid_percentages.png'))
        plt.show()
        plt.close()

    
        #自适应调整lr
        scheduler.step()
        # print('lr: %.20f' %(scheduler.get_last_lr()[0]))
        # print('lr: %.20f' %(optimizer.param_groups[0]['lr']))
       
        # 保存最好的参数
        if valid_accurate > best_acc:
            best_acc = valid_accurate
            torch.save(net.state_dict(), save_path)

        early_stopping(valid_loss, net)
        nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mylog.write('[%s] [epoch %d] 训练集损失: %.4f  训练集准确率: %.4f 验证集损失: %.4f  验证集准确率: %.4f\n' %(nowtime, epoch + 1, train_loss, train_accurate, valid_loss, valid_accurate))
        mylog.flush()
        
        # 在每个epoch结束后计算Precision、Recall和F1-Score
        # 计算每个类别的真正例数（TP）
        true_positives = np.diag(cm)
        # 计算每个类别的实际正样本数（TP + FN）
        possible_true = cm.sum(axis=1)
        # 计算每个类别的召回率
        recall_per_class = true_positives / possible_true
        # 计算加权平均召回率
        recall = recall_per_class.mean()
        # 计算每个类别的预测为正的样本数（TP + FP）
        predicted_positives = cm.sum(axis=0)
        # 计算每个类别的精确率
        precision_per_class = true_positives / predicted_positives
        # 计算加权平均精确率
        precision = precision_per_class.mean()
        # 计算每个类别的F1分数
        f1_scores_per_class = 2 * (precision_per_class * recall_per_class) / (precision_per_class + recall_per_class)
        # 计算加权平均F1分数
        f1= f1_scores_per_class.mean()
        
        # 将这些值添加到相应的列表中用于后续绘制曲线图
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        print('[epoch %d] Precision: %.4f  Recall: %.4f  F1-Score: %.4f' %(epoch + 1, precision, recall, f1))
        # 绘制并保存Precision-Recall曲线
        plt.figure(figsize=(8, 6))
        plt.plot(recalls, precisions)
        plt.title('Precision-Recall Curve')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.grid(True)
        plt.savefig(os.path.join(folder_name, 'precision_recall_curve.png'))
        plt.show()
        plt.close()

        # 绘制并保存F1-Score随epoch变化的曲线
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, epoch+2), f1_scores)
        plt.title('F1-Score vs Epochs')
        plt.xlabel('Epochs')
        plt.ylabel('F1-Score')
        plt.grid(True)
        plt.savefig(os.path.join(folder_name, 'f1score_vs_epochs.png'))
        plt.show()
        plt.close()

########################################################################
        # 绘制损失值的图
        plt.figure()
        plt.plot(range(1, len(train_losses) + 1), train_losses, label='Train Loss')
        plt.plot(range(1, len(valid_losses) + 1), valid_losses, label='Valid Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validing Loss')
        plt.legend()
        plt.savefig(os.path.join(folder_name, 'loss_plot.png'))
        plt.show()
        plt.close()  # 关闭当前图形窗口

########################################################################
        # 绘制准确率的图
        plt.figure()
        plt.plot(range(1, len(train_acces) + 1), train_acces, label='Train Accuracy')
        plt.plot(range(1, len(valid_acces) + 1), valid_acces, label='Valid Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.title('Training and Validing Accuracy')
        plt.legend()
        plt.savefig(os.path.join(folder_name, 'accuracy_plot.png'))
        plt.show()
        plt.close()  # 关闭当前图形窗口
        
        if  early_stopping.early_stop:
            break
        
    print('结束训练')
    finish = time.time()
    print('训练时长{:.2f}s'.format(finish - start))
    
########################################################################    
#早停函数
class EarlyStopping:
    def __init__(self, patience=50, verbose=False, delta=0, path='./end_model.pth', trace_func=print):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.threshold = delta
        self.path = path
        self.trace_func = trace_func

    def __call__(self, val_loss, model):
        score = -val_loss
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.threshold:
            self.counter += 1
            self.trace_func(f'早停计数: {self.counter} / {self.patience}\n')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            self.trace_func(
                f'训练集损失下降 ({self.val_loss_min:.5f} --> {val_loss:.5f}).  保存模型 ...\n')

        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss
        
if __name__ == '__main__':
        main()
