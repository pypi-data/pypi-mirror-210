import torch
from torch import nn
import numpy as np
from typing import List, Tuple
from torch import Tensor

class VVAdd(nn.Module):
    """
    Add two vectors together. 

    .. math::

        z = x + y

    Serves as a patch node for ``aten::add`` when two vectors are added.
    """
    def forward(self, x, y):
        """
        Args:
            x (Tensor)
            y (Tensor)

        Returns:
            Tensor: x + y
        """
        return x + y

class VIAdd(nn.Module):
    """
    Add a vector to a scalar immediate. 

    .. math::

        z = x + imm

    Serves as a patch node for ``aten::add`` when a vector is added to a scalar
    e.g. ``z = x + 3``
    """
    def __init__(self, imm):
        super().__init__()
        self.imm = float(imm)

    def forward(self, x):
        """
        Args:
            x (Tensor)

        Returns:
            Tensor: x + self.imm
        """
        return x + self.imm

class VVSub(nn.Module):
    """
    Subtract a vector from another. 

    .. math::
    
        z = x - y

    Serves as a patch node for ``aten::sub``
    """
    def forward(self, x, y):
        """
        Args:
            x (Tensor)
            y (Tensor)

        Returns:
            Tensor: x - y
        """
        return x - y

class Neg(nn.Module):
    """
    Negate a vector

    .. math::
    
        z = -x
    """
    def forward(self, x):
        """
        Args:
            x (Tensor)
        
        Returns:
            Tensor: -x
        """
        return -x

class Matmul(nn.Module):
    """Perform a broadcasted matmul between two tensors. 

    .. math::

        z = x @ y

    Serves as a patch node for ``aten::matmul``
    """
    def forward(self, x, y):
        """
        Args:
            x (Tensor): shape (..., N, M)
            y (Tensor): shape (..., M, L)

        Returns:
            Tensor: x @ y, shape (..., N, L)
        """
        return torch.matmul(x, y)

class AddMM(nn.Module):
    """Fuse matmul with addition. :math:`z = bias + mat1 @ mat2`

    Serves as a patch node for ``aten::addmm``
    """
    def forward(self, bias, mat1, mat2):
        """
        Args:
            bias (Tensor): vector offset
            mat1 (Tensor)
            mat2 (Tensor)

        Returns:
            Tensor
        """
        if mat1.dim() == 2 and mat2.dim() == 2:
            z = torch.addmm(bias, mat1, mat2)
        else:
            z = torch.matmul(mat1, mat2) + bias
        return z

class VVMul(nn.Module):
    def forward(self, x, y):
        return x * y

class VIMul(nn.Module):
    def __init__(self, imm):
        super().__init__()
        self.imm = float(imm)

    def forward(self, x):
        return x * self.imm

class Reciprocal(nn.Module):
    def forward(self, x):
        return 1/x

# class Abs(nn.Module):
#     def forward(self, x):
#         return torch.abs(x)

class Sqrt(nn.Module):
    def forward(self, x):
        return torch.sqrt(x)

class Exp(nn.Module):
    def forward(self, x):
        return torch.exp(x)

class Log(nn.Module):
    def forward(self, x):
        return torch.log(x)

class Log1p(nn.Module):
    def forward(self, x):
        return torch.log1p(x)

class Log10(nn.Module):
    def forward(self, x):
        return torch.log10(x)

class Log2(nn.Module):
    def forward(self, x):
        return torch.log2(x)

class RSqrt(nn.Module):
    def forward(self, x):
        return torch.rsqrt(x)

class PowFrac(nn.Module):
    def __init__(self, power):
        super().__init__()
        self.power = power

    def forward(self, x):
        return torch.pow(x, self.power)

class ParameterQuantizer(nn.Module):
    def __init__(self, is_weight):
        super().__init__()
        self.is_weight = is_weight
        
    def forward(self, x):
        return x

class Chunk(nn.Module):
    def __init__(self, chunks, dim=0):
        super().__init__()
        self.chunks = chunks
        self.dim = dim

    def forward(self, x: Tensor) -> List[Tensor]:
        return [xx for xx in torch.chunk(x, self.chunks, self.dim)]

class Split(nn.Module):
    def __init__(self, split_sizes: List[int], dim: int):
        super().__init__()
        self.split_sizes: List[int] = split_sizes
        self.dim = dim

    def forward(self, x: Tensor) -> List[Tensor]:
        return [xx for xx in torch.split(x, self.split_sizes, self.dim)]

class Identity(nn.Module):
    def forward(self, x):
        return x

class Cat(nn.Module):
    def __init__(self, dim=0):
        super().__init__()
        self.dim = dim

    def forward(self, tensors: List[Tensor]) -> Tensor:
        return torch.cat(tensors, dim=self.dim)
    
class Stack(nn.Module):
    def __init__(self, dim=0):
        super().__init__()
        self.dim = dim

    def forward(self, tensors: List[Tensor]):
        return torch.stack(tensors, dim=self.dim)

class Transpose(nn.Module):
    def forward(self, x):
        return x.t()
    
class Reshape(nn.Module):
    def __init__(self, shape):
        super().__init__()
        self.shape = shape
        
    def forward(self, x):
        return torch.reshape(x, self.shape)

class Div(nn.Module):
    def forward(self, x, y):
        return x / y

class Mean(nn.Module):
    def __init__(self, dim=0, keepdim=False, biased=False):
        super().__init__()
        if isinstance(dim, int):
            dim = [dim]
        self.dim = dim
        self.keepdim = keepdim
        self.biased = biased

    @torch.jit.ignore
    def get_numel(self, x):
        shape = x.shape
        return np.product([shape[d] for d in self.dim])

    def forward(self, x):
        if self.biased:
            return torch.mean(x, dim=self.dim, keepdim=self.keepdim)
        else:
            N = self.get_numel(x)
            return torch.sum(x, dim=self.dim, keepdim=self.keepdim) / (N-1)

class OnesLike(nn.Module):
    def forward(self, x):
        return torch.ones_like(x)

class Dropout(nn.Module):
    def __init__(self, p:float, training:bool, inplace:bool):
        super().__init__()
        self.p = p
        self.training = training
        self.inplace = inplace
    
    def forward(self, x):
        return torch.nn.functional.dropout(input=x, p=self.p, training=self.training, inplace=self.inplace)

class Shift(nn.Module):
    def __init__(self, shamt: int):
        super().__init__()
        self.shamt = shamt

    def forward(self, x):
        mv = torch.max(torch.abs(x))
        mvq = torch.ceil(torch.log2(mv))
        mv = 2. ** mvq
        return torch.clamp(x, -mv * 2**-self.shamt, mv * 2**-self.shamt)

class _diffable_gt0(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        gt0 = x > 0
        ctx.save_for_backward(gt0)
        return gt0.float()

    @staticmethod
    def backward(ctx, grad_output):
        gt0, = ctx.saved_tensors
        grad_input = grad_output * gt0.float()
        return grad_input

class Gt0(nn.Module):
    @torch.jit.ignore
    def forward(self, x):
        return _diffable_gt0.apply(x)

class LUT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.function = config.function
        self.name = config.name
        self.limits = config.limits
        self.interpolate = config.interpolate
        self.telescope = config.telescope
        self.add_identity = config.add_identity
        self.mul_identity = config.mul_identity

    def forward(self, x):
        return self.function(x)

    def __repr__(self):
        return f'{self.name}LUT'

class FTranspose(nn.Module):
    def __init__(self, dim0, dim1):
        super().__init__()
        self.dim0 = dim0
        self.dim1 = dim1

    def forward(self, x):
        return torch.transpose(x, self.dim0, self.dim1)

class Permute(nn.Module):
    def __init__(self, *dims):
        super().__init__()
        self.dims = list(dims)

    def forward(self, x):
        return x.permute(*self.dims)

class Squeeze(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        return x.squeeze(self.dim)

class Sum(nn.Module):
    def __init__(self, keepdim: bool, dim=-1):
        super().__init__()
        self.dim = dim
        self.keepdim = keepdim

    def forward(self, x: torch.Tensor):
        return torch.sum(x, dim=self.dim, keepdim=self.keepdim)

class Expand(nn.Module):
    def __init__(self, repeats: int, dim=-1):
        super().__init__()
        self.repeats = repeats
        self.dim = dim

    def forward(self, x):
        assert x.shape[self.dim] == 1
        repeat_cfg = [-1]*x.ndim
        repeat_cfg[self.dim] = self.repeats
        return x.expand(*repeat_cfg)