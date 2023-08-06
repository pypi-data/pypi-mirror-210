"""
Defining the atomic operators. These operators are generally parameter-less,
instead taking as input activation/parameter tensors.
"""
from typing import List
from functools import partial
import torch
from torch import nn, Tensor
import numpy as np
from copy import copy
import fmot

from ..annotated_tensors import check_for_annotations, copy_annotations, annotate, \
    copy_dim_annotations, set_dim_annotations, get_dim_annotations, asint
from . import quantizers
from ..fake_quantization import fake_quantize
from ...nn import atomics as nn_atomics
from ._utils import intitem
from ..bitwidths import fqint4, fqint8, fqint16
import torch.nn.functional as F

class AtomicModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.quantize = False

    @check_for_annotations
    def forward(self, *args):
        """
        All atomic modules should implement this
        """
        raise NotImplementedError

    def __repr__(self):
        inset = ''
        if hasattr(self, '_extra_repr'):
            inset += self._extra_repr
        if hasattr(self, 'quantizer'):
            if len(inset) > 0:
                inset += ', '
            inset += f'bw={self.quantizer.bitwidth}'
        return f'Quant{type(self).__name__}({inset})'

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate, observer,
        **observer_kwargs):
        raise NotImplementedError

    def _get_constants(self, *args):
        return {}

ACC_BW = 32

def transpose_dim(x, dim0, dim1):
    dimensions = list(x.dimensions)
    dimensions[dim0], dimensions[dim1] = dimensions[dim1], dimensions[dim0]
    x.__setattr__('dimensions', dimensions)
    return

######################################
"""
Addition Operators
"""

def _get_add_constants(x, y, z):
    """
    Get constants for expression:
    z = x + y

    shamt_x: (left) shift amount for operand x
    shamt_y: (left) shift amount for operand y
    shamt_bwred: (left) shift amount for output buffer when reducing bitwidth
    """
    constants = {}
    if all([w.quantized for w in [x,y,z]]):
        xq, yq, zq = x.quanta, y.quanta, z.quanta
        q = torch.max(xq, yq)
        constants['shamt_x'] = intitem(xq - q)
        constants['shamt_y'] = intitem(yq - q)
        constants['shamt_bwred'] = intitem(q - zq)
        constants['bw'] = z.bitwidth.bitwidth
        constants['bw_x'] = x.bitwidth.bitwidth
        constants['bw_y'] = y.bitwidth.bitwidth
    return constants

class VVAdd(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        if self.quantize:
            xq, yq = x.quanta, y.quanta
            q = torch.max(xq, yq)
            if xq > yq:
                y = fake_quantize(y, q, y.bitwidth.bitwidth)
            elif yq > xq:
                x = fake_quantize(x, q, x.bitwidth.bitwidth)
        return self.quantizer(set_dim_annotations(dimensions, x + y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        constants = _get_add_constants(x, y, z)
        return constants

class VIAdd(AtomicModule):
    def __init__(self, imm, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.imm = nn.Parameter(torch.tensor(imm), requires_grad=False)
        self.imm_quantizer = quantizers.ParameterQuantizer(bitwidth)
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    def forward(self, x):
        dimensions = get_dim_annotations(x)
        device = x.device
        y = self.imm_quantizer(copy_dim_annotations(x, self.imm.to(device)))
        if self.quantize:
            xq, yq = x.quanta, y.quanta
            if xq > yq:
                y = fake_quantize(y, xq, y.bitwidth.bitwidth)
            elif yq > xq:
                x = fake_quantize(x, yq, x.bitwidth.bitwidth)
            q = torch.max(xq, yq)
        return self.quantizer(set_dim_annotations(dimensions, x + y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(imm=parent.imm, bitwidth=bw_conf.activations,
            observer=observer)

    @property
    def _extra_repr(self):
        return f'imm={self.imm.item():.3f}'

    def _get_constants(self, x):
        y = self.imm_quantizer(self.imm)
        z = self.forward(x)
        constants = _get_add_constants(x, y, z)
        if y.quantized:
            constants['y'] = asint(y).cpu().item()
        return constants

class VVSub(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        if self.quantize:
            xq, yq = x.quanta, y.quanta
            if xq > yq:
                y = fake_quantize(y, xq, x.bitwidth.bitwidth)
            elif yq > xq:
                x = fake_quantize(x, yq, y.bitwidth.bitwidth)
        return self.quantizer(set_dim_annotations(dimensions, x - y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        return _get_add_constants(x, y, z)

class Neg(AtomicModule):
    @check_for_annotations
    def forward(self, x):
        y = -x
        if self.quantize:
            y = fake_quantize(y, x.quanta, x.bitwidth.bitwidth)
        copy_annotations(x, y)
        y.avg_sparsity = 0.
        y.density_per_element = None
        y.prev_relu = False
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls()

    def _get_constants(self, x):
        constants = {}
        if x.quantized:
            constants['bw'] = x.bitwidth.bitwidth
        return constants

#######################################
"""
Multiply Operators
"""

def _get_mul_constants(x, y, z):
    constants = {}
    if all([w.quantized for w in [x,y,z]]):
        xq, yq, zq = [w.quanta for w in [x,y,z]]
        buffer_quanta = xq + yq
        constants['shamt_bwred'] = intitem(buffer_quanta - zq)
        constants['bw'] = z.bitwidth.bitwidth
    return constants

class VVMul(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    def forward(self, x, y):
        dimensions = get_dim_annotations(x, y)
        return self.quantizer(set_dim_annotations(dimensions, x * y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x, y):
        z = self.forward(x, y)
        constants = _get_mul_constants(x, y, z)
        return constants

class VIMul(AtomicModule):
    def __init__(self, imm, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.imm = nn.Parameter(torch.tensor(imm), requires_grad=False)
        self.imm_quantizer = quantizers.ParameterQuantizer(bitwidth, observer=quantizers.MinMaxObserver)
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    def forward(self, x):
        device = x.device
        y = self.imm_quantizer(copy_dim_annotations(x, self.imm.to(device)))
        return self.quantizer(copy_dim_annotations(x, x * y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(imm=parent.imm, bitwidth=bw_conf.activations,
            observer=observer)

    def _get_constants(self, x):
        z = self.forward(x)
        y = self.imm_quantizer(self.imm)
        constants = _get_mul_constants(x, y, z)
        if y.quantized:
            constants['y'] = asint(y).cpu().item()
        return constants

def is_sparse(*tensors):
    return [x.avg_sparsity != 0 for x in tensors]

class _diffable_pos(torch.autograd.Function):
    """
    Returns the mask x > 0 as a FloatTensor.
    Uses a surrogate gradient equivalent to the gradient w.r.t. ReLU
    """
    @staticmethod
    def forward(ctx, x):
        nz = x > 0
        ctx.save_for_backward(nz)
        return nz.float()

    @staticmethod
    def backward(ctx, grad):
        grad_nz = None
        if ctx.needs_input_grad[0]:
            nz, = ctx.saved_tensors
            grad_nz = nz.float()*grad
        return grad_nz

####################################
"""
Reduction
"""

class Sum(AtomicModule):
    def __init__(self, dim, keepdim, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)
        self.dim = dim
        self.keepdim = keepdim

    @check_for_annotations
    def forward(self, x):
        y = torch.sum(x, dim=self.dim, keepdim=self.keepdim)
        y = self.quantizer(copy_dim_annotations(x, y))
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(dim=parent.dim, keepdim=parent.keepdim,
            bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        dim = self.dim
        if isinstance(dim, list):
            dim = tuple(dim)
        constants = {'dim': dim, 'keepdim': self.keepdim}
        y = self.forward(x)
        if x.quantized and y.quantized:
            xq, yq = x.quanta, y.quanta
            constants['shamt_bwred'] = intitem(xq - yq)
            constants['bw'] = y.bitwidth.bitwidth
        return constants

    @property
    def _extra_repr(self):
        return f'dim={self.dim}'


####################################
"""
Activation Functions
"""

class ReLU(AtomicModule):
    def __init__(self, alpha=0.95):
        super().__init__()
        self.alpha = alpha
        self.register_buffer('avg_sparsity', None)
        self.register_buffer('density_per_element', None)

    @torch.no_grad()
    def update_sparsity(self, x):
        if x.dimensions is not None:
            f_dim = x.dimensions.index('F')
            dims = list(range(x.ndim))
            dims.remove(f_dim)
            density_per_element = (x != 0).float().mean(dims)
            sparsity = 1 - density_per_element.mean()
            if self.avg_sparsity is None:
                self.avg_sparsity = sparsity
                self.density_per_element = density_per_element
            else:
                self.avg_sparsity = ReLU._lpf_update(
                    self.alpha, self.avg_sparsity, sparsity)
                self.density_per_element = ReLU._lpf_update(
                    self.alpha, self.density_per_element, density_per_element)
        else:
            sparsity = (x == 0).float().mean()
            if self.avg_sparsity is None:
                self.avg_sparsity = sparsity
            else:
                self.avg_sparsity = ReLU._lpf_update(
                    self.alpha, self.avg_sparsity, sparsity)

    @staticmethod
    def _lpf_update(s, old, new):
        return s * old + (1-s) * new

    @check_for_annotations
    def forward(self, x):
        y = x.relu()
        y.dimensions = x.dimensions
        self.update_sparsity(y)
        y = copy_annotations(x, y)
        y.avg_sparsity = self.avg_sparsity
        y.density_per_element = self.density_per_element
        y.prev_relu = True
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls()

    def __repr__(self):
        repr = super().__repr__()
        if self.avg_sparsity is not None:
            repr += ' (Act. Sparsity: {:.0f}%)'.format(self.avg_sparsity * 100)

        return repr

class Identity(AtomicModule):
    @check_for_annotations
    def forward(self, x):
        return x

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls()

class OnesLike(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    def forward(self, x):
        y = torch.ones_like(x)
        return self.quantizer(copy_dim_annotations(x, y))

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        y = self.forward(x)
        constants = {}
        if x.quantized:
            constants = {'imm': asint(y).flatten()[0].cpu().item()}
        return constants

class Table:
    def __init__(self, x, y, name):
        assert len(x) == len(y)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        self.name = name
        self.x = x
        self.y = y
        self.N = len(self.x)

    def __eq__(self, other):
        assert isinstance(other, Table)
        if self.N == other.N:
            return np.all(self.y == other.y)
        else:
            return False

    def __lt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.name < other.name

    def __gt__(self, other):
        if self.__eq__(other):
            return False
        else:
            return self.name > other.name

    def __repr__(self):
        return f'<{self.name}>'

class BareLUT(AtomicModule):
    def __init__(self, function, bitwidth, limits=None, observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.function = function
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer)

    @check_for_annotations
    def forward(self, x):
        if x.quantized:
            assert x.bitwidth == fqint8
        y = self.function(x)
        return self.quantizer(copy_dim_annotations(x, y))

    def get_table(self, x):
        bits, quanta = x.bitwidth.bitwidth, x.quanta
        levels = 2**bits
        min_x = -2**(bits+quanta-1)
        max_x = (2**(bits-1) - 1)*2**quanta
        y = torch.linspace(min_x, max_x, levels, device=x.device)
        y = self.quantizer(copy_dim_annotations(x, self.function(y)))
        x_int = np.linspace(-levels//2, levels//2-1, levels, dtype=int)
        y_int = asint(y).cpu().numpy()
        return Table(x=x_int, y=y_int, name=self.function.__name__)

    def _get_constants(self, x):
        constants = {}
        if x.quantized:
            constants['shamt_address'] = 0
            constants['bw_address'] = 8
            constants['table'] = self.get_table(x)
        constants['function'] = self.function.__name__
        return constants

####################
"""
Tensor slicing and joining
"""

class Chunk(nn.Module):
    def __init__(self, chunks, dim=0):
        super().__init__()
        self.chunks = chunks
        self.dim = dim

    @check_for_annotations
    def forward(self, x):
        z = torch.chunk(x, self.chunks, self.dim)
        return [copy_annotations(x, zz) for zz in z]

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(chunks=parent.chunks, dim=parent.dim)

    def _get_constants(self, x):
        return {
            'chunks': self.chunks,
            'dim': self.dim
        }

    @property
    def _extra_repr(self):
        return f'chunks={self.chunks}, dim={self.dim}'

class Split(AtomicModule):
    def __init__(self, split_sizes: List[int], dim=0):
        super().__init__()
        self.split_sizes = split_sizes
        self.dim = dim

    @check_for_annotations
    def forward(self, x):
        z = torch.split(x, self.split_sizes, self.dim)
        return [copy_annotations(x, zz) for zz in z]

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(split_sizes=parent.split_sizes, dim=parent.dim)

    def _get_constants(self, x):
        return {
            'lengths': self.split_sizes,
            'dim': self.dim
        }

    @property
    def _extra_repr(self):
        return f'split_sizes={self.split_sizes}, dim={self.dim}'

class BareCat(AtomicModule):
    def __init__(self, dim=0):
        super().__init__()
        self.dim = dim

    @check_for_annotations
    def forward(self, *tensors):
        z = torch.cat(tensors, self.dim)
        return copy_annotations(tensors[0], z)

    def _get_constants(self, *x):
        return {
            'dim': self.dim
        }

    def _getargnames(self):
        i = 0
        while True:
            yield f'x{i}'
            i += 1

class Cat(nn.Module):
    def __init__(self, dim, bitwidth, observer):
        super().__init__()
        self.cat = BareCat(dim)
        self.requantizers = nn.ModuleList()
        self.q_group = quantizers.PrecisionConstraint()
        self._built = False
        self._obs = observer
        self._bw = bitwidth

    def _build(self, N):
        for __ in range(N):
            req = Requantize(self._bw, self._obs)
            self.requantizers.append(req)
            self.q_group.recursively_add(req)
        quantizers.share_observer(self.requantizers)
        self._built = True

    @check_for_annotations
    def forward(self, tensors):
        if not self._built:
            N = len(tensors)
            self._build(N)
        new_tensors = [req(t) for req, t in zip(self.requantizers, tensors)]
        return self.cat(*new_tensors)

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(dim=parent.dim, bitwidth=bw_conf.activations,
            observer=observer)

class Stack(AtomicModule):
    def __init__(self, dim=0):
        super().__init__()
        self.dim = dim

    @check_for_annotations
    def forward(self, tensors: List[Tensor]):
        t0 = tensors[0]
        if t0.quantized:
            assert all([t.quanta == t0.quanta for t in tensors]), (
                "Cannot concatenate tensors with different quanta")
        z = torch.stack(tensors, self.dim)
        return copy_annotations(tensors[0], z)

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(dim=parent.dim)

    def _get_constants(self, x):
        return {
            'dim': self.dim
        }

    @property
    def _extra_repr(self):
        return f'dim={self.dim}'

    def _getargnames(self):
        i = 0
        while True:
            yield f'x{i}'
            i += 1

class Transpose(AtomicModule):
    """
    Performs a transpose on a matrix.
    """
    def __init__(self):
        super().__init__()

    @check_for_annotations
    def forward(self, x):
        z = x.t()
        return copy_annotations(x, z)

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls()

    def _get_constants(self, x):
        return {
            'dim0': 0,
            'dim1': 1
        }

class Reshape(AtomicModule):
    """
    Performs a transpose on a matrix.
    """
    def __init__(self, shape):
        super().__init__()
        self.shape = shape

    @check_for_annotations
    def forward(self, x):
        z = torch.reshape(x, self.shape)
        return copy_annotations(x, z)

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(parent.shape)

    def _get_constants(self, x):
        return {
            'shape': self.shape
        }

"""
Requantize
"""

class Requantize(AtomicModule):
    def __init__(self, bitwidth, observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        super().__init__()
        self.quantizer = quantizers.Quantizer(bitwidth, observer=observer,
            **kwargs)

    @check_for_annotations
    def forward(self, x):
        prev_relu = x.prev_relu
        avg_sparsity = x.avg_sparsity
        y = self.quantizer(x)
        y.avg_sparsity = avg_sparsity
        y.prev_relu = prev_relu
        y.density_per_element = x.density_per_element
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(bitwidth=bw_conf.activations, observer=observer)

    def _get_constants(self, x):
        y = self.forward(x)
        return {
            'shamt': intitem(x.quanta - y.quanta),
            'bw': y.bitwidth.bitwidth
        }

class Shift(AtomicModule):
    def __init__(self, shamt, bitwidth):
        super().__init__()
        self.shamt = shamt
        self.bitwidth = bitwidth

    @check_for_annotations
    def forward(self, x):
        prev_relu = x.prev_relu
        quanta = x.quanta
        avg_sparsity = x.avg_sparsity
        density_per_element = x.density_per_element
        if self.quantize:
            quanta = quanta - self.shamt
            y = fake_quantize(x, quanta, self.bitwidth.bitwidth)
        else:
            mv = torch.max(torch.abs(x))
            mvq = torch.ceil(torch.log2(mv))
            mv = 2. ** mvq
            y = torch.clamp(x, -mv * 2**-self.shamt, mv * 2**-self.shamt)
        y = annotate(y,
            bitwidth=self.bitwidth,
            quanta=quanta,
            quantized=True,
            avg_sparsity=avg_sparsity,
            density_per_element=density_per_element,
            prev_relu=prev_relu)
        copy_dim_annotations(x, y)
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(shamt=parent.shamt, bitwidth=bw_conf.activations)

    def _get_constants(self, x):
        return {
            'shamt': self.shamt,
            'bw': self.bitwidth.bitwidth
        }

class Gt0(AtomicModule):
    def __init__(self, bitwidth):
        super().__init__()
        self.bitwidth = bitwidth

    @check_for_annotations
    def forward(self, x):
        y = nn_atomics._diffable_gt0.apply(x)
        quanta = x.quanta
        if self.quantize:
            quanta = quanta * 0
        y = annotate(y,
            bitwidth=self.bitwidth,
            quanta=quanta,
            quantized=x.quantized,
            avg_sparsity=x.avg_sparsity,
            prev_relu=True)
        copy_dim_annotations(x, y)
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(bitwidth=bw_conf.activations)

    def _get_constants(self, x):
        return {
            'bw': self.bitwidth.bitwidth
        }

class FTranspose(AtomicModule):
    """
    Performs a functional transpose on a matrix.
    """
    def __init__(self, dim0, dim1):
        super().__init__()
        self.dim0 = dim0
        self.dim1 = dim1
        self.tracing_mode = False

    @check_for_annotations
    def forward(self, x):
        # In tracing mode, we assume that we only have an input of shape
        # (batch_size, feature_size)
        if self.tracing_mode:
            z = x
        else:
            dimensions = list(x.dimensions)
            if set([dimensions[self.dim0], dimensions[self.dim1]]) == {'B', 'F'}:
                raise Exception("We don't support Batch-Feature dimension swap")
            z = torch.transpose(x, self.dim0, self.dim1)
            z = copy_annotations(x, z)
            transpose_dim(z, self.dim0, self.dim1)
        return z

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(parent.dim0, parent.dim1)

    def _get_constants(self, x):
        return {
            'dim0': self.dim0,
            'dim1': self.dim1
        }

class Permute(AtomicModule):
    """
    Performs a permutation on a tensor.
    """
    def __init__(self, dims):
        super().__init__()
        self.dims = dims
        self.tracing_mode = False

    @check_for_annotations
    def forward(self, x):
        # In tracing mode, we assume that we only have an input of shape
        # (batch_size, feature_size)
        if self.tracing_mode:
            z = x
        else:
            dimensions = x.dimensions
            if set([dimensions[self.dim0], dimensions[self.dim1]]) == {'B', 'F'}:
                raise Exception("We don't support Batch-Feature dimension swap")
            z = torch.transpose(x, self.dim0, self.dim1)
            z = copy_annotations(x, z)
            transpose_dim(z, self.dim0, self.dim1)
        return z

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(parent.dim0, parent.dim1)

    def _get_constants(self, x):
        return {
            'dim0': self.dim0,
            'dim1': self.dim1
        }

class Dropout(AtomicModule):
    def __init__(self, p, training, inplace):
        super().__init__()
        self.p = p
        self.training = training
        self.inplace = inplace

    @check_for_annotations
    def forward(self, x):
        if self.training:
            device = x.device
            mask = torch.bernoulli(torch.zeros(x.shape) + (1-self.p)).to(device)
            z = mask * x / (1-self.p)
            return copy_annotations(x, z)
        else:
            return x

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(p=parent.p,
                   training=parent.training,
                   inplace=parent.inplace)

class Squeeze(AtomicModule):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        y = x.squeeze(self.dim)
        y = copy_annotations(x, y)
        dims = copy(get_dim_annotations(x))
        if dims is not None:
            del dims[self.dim]
            set_dim_annotations(dims, y)
        return y

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        return cls(parent.dim)

    def _get_constants(self, x):
        return {'dim': self.dim}