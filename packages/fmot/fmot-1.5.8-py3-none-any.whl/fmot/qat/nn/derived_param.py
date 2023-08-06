import torch
from torch import nn, Tensor
from .import quantizers
from functools import partial
from typing import *

class QDerivedParameter(nn.Module):
    def __init__(self, bitwidth, parent: nn.Module, dimensions=None,
                 observer=quantizers.DEFAULT_OBSERVERS['param']):
        super().__init__()
        self.weight_quant = quantizers.ParameterQuantizer(bitwidth,
            observer=observer, dimensions=dimensions)
        self.parent = parent
        self.weight = nn.Parameter(self.parent.weight, requires_grad=self.parent.requires_grad)

    def forward(self):
        x_deriv = self.parent.derive(self.weight)
        y = self.weight_quant(x_deriv)
        return y
    
    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['param'], **kwargs):
        observer = partial(observer, **kwargs)
        if parent.is_weight:
            bw = bw_conf.weights
            dimensions = ['F', 'F']
        else:
            bw = bw_conf.activations
            dimensions = ['F']
        return cls(bitwidth=bw, dimensions=dimensions, observer=observer,
                   parent=parent)
    
class QMultiDerivedParameter(nn.Module):
    def __init__(self, bitwidth, parent: nn.Module, is_weight: List[bool]):
        super().__init__()
        self.weight_quants = nn.ModuleList()
        for iw in is_weight:
            if iw:
                obs = quantizers.DEFAULT_OBSERVERS['param']
            else:
                obs = quantizers.DEFAULT_OBSERVERS['default']
            self.weight_quants.append(
                quantizers.ParameterQuantizer(bitwidth=bitwidth, observer=obs)
            )
        self.parent = parent

        self.weights = nn.ParameterList()
        for w in self.parent.weights:
            self.weights.append(nn.Parameter(w, requires_grad=self.parent.requires_grad))

    def forward(self) -> List[Tensor]:
        x = [w for w in self.weights]
        y_deriv = self.parent.derive(*x)
        y_quant = [q(y) for q, y in zip(self.weight_quants, y_deriv)]
        return y_quant




