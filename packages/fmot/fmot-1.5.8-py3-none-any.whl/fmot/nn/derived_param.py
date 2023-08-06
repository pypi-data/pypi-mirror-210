import torch
from torch import nn, Tensor
from fmot.nn import SuperStructure
from typing import *

class DerivedParameter(SuperStructure):
    """A parameter that is statically transformed before being used.
    Static transformation usually used to enforce a constraint.
    
    Overwrite the "derive" method for specific instantiations
    """
    def __init__(self, weight: Tensor, requires_grad=True):
        super().__init__()
        self.weight = nn.Parameter(weight, requires_grad=requires_grad)
        self.is_weight = False
        self.requires_grad = requires_grad

    def derive(self, x: Tensor) -> Tensor:
        raise NotImplementedError
    
    @torch.jit.ignore
    def forward(self):
        x = self.weight
        self.is_weight = x.ndim == 2
        return self.derive(x)
    
class SigmoidConstraintParameter(DerivedParameter):
    def derive(self, x: Tensor) -> Tensor:
        return x.sigmoid()
    
class MultiDerivedParameter(SuperStructure):
    def __init__(self, *weights: List[Tensor], requires_grad=True):
        super().__init__()
        self.weights = nn.ParameterList()
        for w in weights:
            self.weights.append(nn.Parameter(w, requires_grad=requires_grad))
        self.requires_grad = requires_grad
    
    def derive(self, *x: Tensor):
        raise NotImplementedError
    
    @torch.jit.ignore
    def forward(self):
        x = [w for w in self.weights]
        out = self.derive(*x)
        self.is_weight = [y.ndim==2 for y in out]
        return out
    
class AffineMatrix(MultiDerivedParameter):
    def derive(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        mv = x.abs().max()
        return (x / mv, mv)
    
    @torch.jit.ignore
    def forward(self) -> Tuple[Tensor, Tensor]:
        x = [w for w in self.weights][0]
        out = self.derive(x)
        return out