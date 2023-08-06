import torch
from torch import nn

__all__ = ['save', 'load', 'print']

def save(model, name, path='./', only_para=False):
    if isinstance(model, nn.Module):
        if only_para:
            torch.save(model.state_dict(), path + name + '.pth')
        else:
            torch.save(model.state_dict(), path + name + '.pth')
    else:
        raise TypeError('autolog目前只支持pytorch')


def load(name, frame, path='./', only_para=False, model=None):
    if frame in ['torch', 'pytorch']:
        if only_para:
            return torch.load(path + name + '.pth')
        else:
            model.load_state_dict(path + name + '.pth')
    else:
        raise TypeError('autolog目前只支持pytorch')


def print(model):
    if isinstance(model, nn.Module):
        print(model)
    else:
        raise TypeError('autolog目前只支持pytorch')