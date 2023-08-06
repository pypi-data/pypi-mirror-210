"""Moving into its own file to avoid circ import"""
import torch 
from torch import nn
from . import quantizers, atomics

class TuningEpsilon(nn.Module):
    def __init__(self, bitwidth, running_max=0, observer=quantizers.DEFAULT_OBSERVERS['default'],
        eps=1/128, alpha=.99):
        super().__init__()
        self.eps = eps
        self.alpha = alpha
        self.running_max = running_max
        self.add = atomics.VIAdd(self.epsilon(), bitwidth, observer=observer)
    
    @torch.jit.ignore()
    def epsilon(self):
        return self.running_max * self.eps

    @torch.jit.ignore()
    @torch.no_grad()
    def update(self, x):
        xmax = torch.max(x).cpu().item()
        if self.running_max == 0:
            self.running_max = xmax
        else:
            self.running_max = self.alpha * self.running_max + (1-self.alpha) * xmax

    def forward(self, x):
        self.update(x)
        self.add.imm.data = torch.ones_like(self.add.imm.data)*self.epsilon()
        return self.add(x)