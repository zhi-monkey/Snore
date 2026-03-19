import os
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F



def load_data(npy_file):
    file = np.load(npy_file, allow_pickle=True)[()]

    data = file['data']
    label = file['label']

    return data, label


def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = False


class EarlyStopping:
    def __init__(self, patience=10, verbose=False, delta=0, path='./best-model.pt', trace_func=print):
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
            self.trace_func(f'EarlyStopping counter: {self.counter} out of {self.patience}\n')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            self.trace_func(
                f'Val Loss decreased ({self.val_loss_min:.5f} --> {val_loss:.5f}).  Saving model ...\n')

        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss


class FocalLoss(nn.Module):
    def __init__(self, gamma=1.0):
        super().__init__()
        self.gamma = gamma

    def forward(self, input, target):
        CE_loss = F.cross_entropy(input, target, reduction='none')
        y_pred = torch.exp(-CE_loss)
        Focal_loss = torch.mean((1 - y_pred) ** self.gamma * CE_loss)

        return Focal_loss
