import torch
from torch import nn
from torch import Tensor
from .atomics import *
from typing import *

class TemporalUnfold1d(AtomicModule):
    """
    Extract sliding window from an input tensor.

    Applies temporal padding as appropriate for TemporalConv1d and 
    SlidingWindowCausalAttention

    `input` is a tensor of shape `(N, C, T)`, where `N` is the
    batch size, `C` is the channel dimension, and `T` is the sequence length.

    It outputs a tensor of shape `(N, C*kernel_size, T)`. Each output flattens
    each `kernel_size`-sized sliding block over the input sequence.
    """
    def __init__(self, kernel_size: int, dilation: int=1):
        super().__init__()
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.buffsize = (self.kernel_size - 1) * self.dilation
        self._unfold = torch.nn.Unfold((1, kernel_size), (1, dilation))

    @check_for_annotations
    def forward(self, x: Tensor) -> Tensor:
        input = x
        dimensions = get_dim_annotations(input)
        unsqueeze = x.ndim == 2
        if x.ndim == 2:
            x = x.unsqueeze(-1)

        B, C, T = x.shape

        gathers = [self.kernel_size * torch.arange(0, C, device=x.device) + k for k in range(self.kernel_size)]
        gathers = torch.cat(gathers, 0)
        gathers = gathers.reshape(1, -1, 1)
        gathers = gathers.expand(B, self.kernel_size*C, T)

        buffer = torch.zeros((B, C, self.buffsize), device=x.device)

        x = torch.cat([buffer, x], dim=-1)
        if self.kernel_size > 1:
            buffer = x[:,:,-self.buffsize:]
        else:
            buffer = None
        x = torch.unsqueeze(x, -2)
        x = self._unfold(x)
        x = x.gather(1, gathers)

        if unsqueeze:
            x = x.squeeze(-1)

        x = set_dim_annotations(dimensions, x)
        x = copy_annotations(input, x)
        return x

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate, observer,
        **observer_kwargs):
        return TemporalUnfold1d(kernel_size=parent.kernel_size, 
            dilation=parent.dilation)

    def _get_constants(self, *args):
        return {
            'kernel_size': self.kernel_size,
            'dilation': self.dilation,
            'buffer_length': self.buffsize}

