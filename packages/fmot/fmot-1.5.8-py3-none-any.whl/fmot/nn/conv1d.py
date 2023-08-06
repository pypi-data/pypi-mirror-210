import torch
import math
from torch import nn
import torch.nn.functional as F
import warnings
from .. import torchscript_utils as tsutils
from .sequencer import Sequencer
from .super_structures import SuperStructure, ProtectedModule
from typing import List, Tuple
from torch import Tensor
from .atomics import Identity, VVAdd, Chunk
from .composites import DepthWiseConvSummer
from .sequenced_rnn import rsetattr, rgetattr
from ..qat import annotated_tensors as anno
import numpy as np
from itertools import chain
import re

from ..utils.conv1d_utils import flatten_conv_matrix_wrapper, inv_flatten_conv_matrix_wrapper, \
    inv_cat_flatten_conv_matrix_wrapper, cat_wrapper, dw_subslct_wrapper,\
    dw_F_inv

class TemporalConv1d(nn.Module):
    """Full-precision temporal conv1d layer, for user to put into their models

    Args:
        in_channels:
        out_channels:
        kernel_size:
        dilation:
    """
    def __init__(self, in_channels, out_channels, kernel_size, dilation=1, 
        stride=1, groups=1, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size 
        self.dilation = dilation
        self.stride = stride
        self.groups = groups
        self.bias = bias
        self.pad_amount = (kernel_size-stride) * dilation
        self.conv = nn.Conv1d(
            in_channels=in_channels, 
            out_channels=out_channels, 
            kernel_size=kernel_size, 
            stride=stride, 
            groups=groups,
            dilation=dilation,
            bias=bias)

    def forward(self, x):
        """
        Args:
            x (Tensor): shape (N, Cin, Lin)
        Returns
            y (Tensor): shape (N, Cout, Lin)
        """
        x = F.pad(x, (self.pad_amount, 0), mode='constant', value=0.)
        x = self.conv(x)
        return x

class OverlapAdder(SuperStructure):
    def __init__(self, stride):
        super().__init__()
        self.stride = stride
        if self.stride > 1:

            self.adder = VVAdd()
            self.chunk = Chunk(stride, dim=1)

    def forward(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        if self.stride > 1:
            chunks = self.chunk(x)
            output = self.adder(chunks[0], state[0])
            new_state = []
            for ch, st in zip(chunks[1:], state[1:]):
                new_state.append(self.adder(ch, st))
            new_state.append(chunks[-1])
            return output, new_state
        else:
            return x, []

class OverlapAddSeq(Sequencer):
    def __init__(self, in_channels, stride):
        assert in_channels % stride == 0
        self.in_channels = in_channels
        self.out_channels = in_channels // stride
        self.stride = stride
        state_shapes = [[self.out_channels]]*(self.stride-1)
        super().__init__(state_shapes, batch_dim=0, seq_dim=2)
        self.oadder = OverlapAdder(stride)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        return self.oadder(x_t, state)

class OverlapAdd(nn.Module):
    def __init__(self, in_channels, stride):
        super().__init__()
        self.oadd = OverlapAddSeq(in_channels, stride)

    def forward(self, x):
        y, __ = self.oadd(x)
        return y

    def __repr__(self):
        return 'OverlapAdd()'

def get_graph_module(graph_obj, module):
    parent = module
    node = graph_obj.node()
    attr = tsutils.get_attr_name(node)
    parent_obj = node.input()
    if parent_obj.debugName() != 'self':
        parent = get_graph_module(parent_obj, module)
    return getattr(parent, attr)

def onlydependson(node, inputs):
    if not tsutils.iscallmethod(node):
        return False
    for x in node.inputs():
        if tsutils.istensor(x):
            if x not in inputs:
                return False
    return True

def get_first_ops(model, recurse=True):
    smodel = torch.jit.script(model)
    graph = smodel.graph
    inputs = list(graph.inputs())[1:]
    first_ops = []
    for node in graph.nodes():
        if onlydependson(node, inputs):
            first_ops.append(get_graph_module(list(node.inputs())[0], model))
    if recurse:
        for op in first_ops:
            first_ops += get_first_ops(op, recurse)
    return first_ops
   
def isfrontendlayer(layer, model):
    return (layer == model) or (layer in get_first_ops(model))

class BufferRotation(SuperStructure):
    r""" Rotates the buffer. Here the buffer is kept in memory as a list of len
         (kernel_size-1)*dilation of states of shape in_channels*stride.
    """
    def __init__(self, kernel_size, dilation):
        super().__init__()
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.id = Identity()

    def forward(self, x_t: Tensor, buff: List[Tensor]) -> Tuple[List[Tensor], List[Tensor]]:
        new_buff = buff[1:] + [self.id(x_t)]
        to_cat = buff[::self.dilation] + [x_t]
        
        return new_buff, to_cat

class SequencedUnstridedTemporalConv1d(Sequencer):
    r""" Contains the actual Sequencer logic for unstrided Conv1d.
    Inputs and weight formats are preprocessed in SequencedTemporalConv1d
    to make strided convolutions fall under the unstrided category (cf documentation)
    
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int,
            dilation: int = 1,
            bias: bool = True):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.bias = bias
        buff_size = (kernel_size-1)*dilation
        state_shapes = [[in_channels]]*buff_size
        super().__init__(state_shapes, batch_dim=0, seq_dim=-1, return_hidden_state=True)

        self.buffer_rot = BufferRotation(self.kernel_size, self.dilation)
        self.conv = nn.Linear(self.kernel_size * self.in_channels, self.out_channels, bias=self.bias)
        
    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        new_state, to_cat = self.buffer_rot(x_t, state)
        stacked_input = torch.cat(to_cat, dim=1)
        o_t = self.conv(stacked_input)
        
        return o_t, new_state  

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None):
        assert type(parent) == TemporalConv1d

        if parent.groups != 1:
            raise NotImplementedError('Conv1d with groups != 1 not yet implemented')

        if parent.stride != 1:
            if not(isfrontendlayer(parent, toplevel)):
                raise Exception('Strided conv1d intermediate layers not supported')
        else:
            kernel_size = parent.kernel_size
            
            conv_layer = cls(in_channels=parent.in_channels, 
                             out_channels=parent.out_channels,
                             kernel_size=parent.kernel_size,
                             dilation=parent.dilation,
                             bias=parent.bias)
            
            # Given our computation method, the conv matrix of shape
            # (out_channels, in_channels, kernel_size) should be
            # (out_channels, in_channels * kernel_size) with tranpose weight matrix
            # For a matrix for a given channel (1, 4, 3):
            # | | |     _ _ _ _
            # | | | ->  _ _ _ _ -> ---- ---- ----
            # | | |     _ _ _ _
            # | | |
            weight = torch.transpose(parent.conv.weight,1,2).reshape(parent.out_channels, parent.in_channels * kernel_size)
            rsetattr(conv_layer, 'conv.weight', nn.Parameter(weight))
            if parent.bias:
                rsetattr(conv_layer, 'conv.bias', parent.conv.bias)
            
            return conv_layer

    def weight_init(self):
        k = math.sqrt(1 / (self.hidden_size * self.kernel_size))
        for name, param in self.named_parameters():
            torch.nn.init.uniform_(param, -k, k)


class WrappedSequencedUnstridedTemporalConv1d(nn.Module):
    r""" Wrapper to get an output signature equivalent to Pytorch
    """
    def __init__(self, 
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        dilation: int = 1,
        bias: bool = True):
        super().__init__()
        self.conv = SequencedUnstridedTemporalConv1d(
            in_channels, out_channels, kernel_size,
            dilation=dilation, bias=bias)
        
    def forward(self, x):
        output, __ = self.conv(x)
        return output


class Conv1dUnroller(SuperStructure):
    r""" Allows us to unroll all the convolution layers that constitute 
    each group of the convolution. 
    
    """
    def __init__(self,
        group_in_channels,
        group_out_channels,
        eff_kernel_size,
        dilation,
        groups,
        bias):
        self.group_in_channels = group_in_channels
        self.group_out_channels = group_out_channels
        self.eff_kernel_size = eff_kernel_size
        self.dilation = dilation
        self.groups = groups
        self.bias = bias
        super().__init__()
        self.unstrided_convs = nn.ModuleList(
            WrappedSequencedUnstridedTemporalConv1d(
                in_channels = self.group_in_channels,
                out_channels = self.group_out_channels,
                kernel_size = self.eff_kernel_size,
                dilation = self.dilation,
                bias = self.bias) for _ in range(self.groups))

    def forward(self, x: Tensor, input_groups: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        group_output = []
        for group_id, conv in enumerate(self.unstrided_convs):
            x = conv(input_groups[group_id])
            group_output.append(x)
        
        return x, group_output
        
        
class SequencedTemporalConv1d(nn.Module):
    """ Fmot version of Conv1d that can be patched and mapped.
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int,
            stride: int = 1,
            dilation: int = 1,
            groups: int = 1,
            bias: bool = True):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.groups = groups
        self.bias = bias
                    
        if not(self.kernel_size % self.stride == 0):
            raise Exception('Kernel size should be a multiple of stride: other configuraions not supported yet')
        if self.dilation > 1 and self.stride > 1:
            raise Exception('Stride with dilation are not supported yet')

        # New
        assert(in_channels%groups == 0), 'in_channels must be divisible by groups'
        assert(out_channels%groups == 0), 'out_channels must be divisible by groups'
        
        # Effective variables to go from strided to unstrided
        self.eff_kernel_size = int(self.kernel_size / self.stride)
        self.eff_in_channels = self.in_channels * self.stride
        # Effective in and out dimensions for each group-convolution
        self.group_in_channels = int(self.eff_in_channels/self.groups)
        self.group_out_channels = int(self.out_channels/self.groups)
        self.feature_dim = 1
        super().__init__()
        
        if self.stride != 1:
            self.reshaper = Conv1dReshaper(self.stride, unbind_dim=-1)
        else:
            self.reshaper = Identity()
        self.convwrapper = Conv1dUnroller(group_in_channels = self.group_in_channels,
                                                group_out_channels = self.group_out_channels,
                                                eff_kernel_size = self.eff_kernel_size,
                                                dilation = self.dilation,
                                                groups = self.groups,
                                                bias = self.bias)
        
    def forward(self, x):
        reshaped_x = self.reshaper(x)

        input_groups = torch.chunk(reshaped_x, self.groups, dim=self.feature_dim)
        
        _, group_output = self.convwrapper(reshaped_x, input_groups)

        output = torch.cat(group_output, dim=self.feature_dim)
    
        return output

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        assert type(parent) == TemporalConv1d

        if parent.stride != 1 and not(isfrontendlayer(parent, toplevel)):
            raise Exception('Strided conv1d intermediate layers not supported')
        else:
            kernel_size = parent.kernel_size


            conv_layer = cls(in_channels=parent.in_channels, 
                             out_channels=parent.out_channels,
                             kernel_size=parent.kernel_size,
                             stride=parent.stride,
                             dilation=parent.dilation,
                             groups=parent.groups,
                             bias=parent.bias)

            group_in_channels = int(parent.in_channels / parent.groups)
            K = int(parent.out_channels / parent.groups)

            # W -> W_G1: (f, f_inv), W_G2: (f, f_inv) ...
            weight_split_mapping = dict()
            bias_split_mapping = dict()
                
            # Given our computation method, the conv matrix of shape
            # (out_channels, in_channels, kernel_size) should be
            # (out_channels, in_channels * kernel_size) with tranpose weight matrix
            for group_id in range(parent.groups):
                f = flatten_conv_matrix_wrapper(K, group_in_channels, kernel_size)
                f_inv = inv_flatten_conv_matrix_wrapper(K, group_in_channels, kernel_size)
                weight = f(parent.conv.weight[K*group_id:K*(group_id+1),])
                rsetattr(conv_layer, 'convwrapper.unstrided_convs.' + str(group_id) + '.conv.conv.weight', nn.Parameter(weight))
                sub_param_name = "model." + inherited_name + 'convwrapper.unstrided_convs.' + str(group_id) + '.conv.conv.weight'
                weight_split_mapping[sub_param_name] = (f, f_inv)
                if parent.bias:
                    rsetattr(conv_layer, 'convwrapper.unstrided_convs.' + str(group_id) + '.conv.conv.bias',
                                nn.Parameter(parent.conv.bias[K*group_id:K*(group_id+1),]))
                    sub_param_name = "model." + inherited_name + 'convwrapper.unstrided_convs.' + str(group_id) + '.conv.conv.bias'
                    bias_split_mapping[sub_param_name] = None
            
            F_inv_weight = inv_cat_flatten_conv_matrix_wrapper(K, group_in_channels, kernel_size)
            inherited_dict[inherited_name + 'conv.weight'] = (weight_split_mapping, F_inv_weight)
            if parent.bias:
                F_inv_bias = cat_wrapper()
                inherited_dict[inherited_name + 'conv.bias'] = (bias_split_mapping, F_inv_bias)
            
            return conv_layer

    def weight_init(self):
        k = math.sqrt(1 / (self.hidden_size * self.kernel_size))
        for name, param in self.named_parameters():
            torch.nn.init.uniform_(param, -k, k)

class Conv1dReshaper(SuperStructure):
    """Transforms inputs to match our internal Conv1d computations when we have strides. 

    x.shape changes from (B, F, T) to (B, F*stride, T') where T' is the new sequence length
    (see :doc:strides)
    
    Args:
        stride (int):
        unbind_dim:

    Attributes:
        tracing_mode: if True, then we are tracing the model for FQIR; in this conditions
            the input does not have a time dimension -> no need to reshape
    """
    def __init__(self, stride, unbind_dim):
        super().__init__()
        self.stride = stride
        self.unbind_dim = unbind_dim
        self.id = Identity()
        self.tracing_mode = False
    
    @torch.jit.ignore
    def forward(self, x: Tensor):
        if self.tracing_mode:
            return x
        else:
            x_init = x
            x = x.clone()
            # Number of zeros to add to complete the initial new state
            if self.unbind_dim != -1:
                x = torch.transpose(x, -1, self.unbind_dim)
            # left_padding = self.stride - 1
            # seq_length = x.shape[-1]
            # x_padded = F.pad(x, (left_padding, 0), mode='constant', value=0.)
            # new_length = seq_length + left_padding - (seq_length + left_padding)%self.stride
            # x_trimmed = x_padded[:,:,:new_length]
            new_length = x.shape[-1]  - (x.shape[-1]% self.stride)
            x_trimmed = x[:,:,:new_length]
            chunks = new_length // self.stride
            x_list = []
            for x_t in torch.chunk(x_trimmed, chunks, -1):
                x_list.append(torch.cat(torch.unbind(x_t, -1), -1))

            new_x = torch.stack(x_list, -1)

            if self.unbind_dim != -1:
                new_x = torch.transpose(new_x, -1, self.unbind_dim)
            
            if hasattr(new_x, 'annotated'):
                return new_x
            elif hasattr(x_init, 'annotated'):
                return anno.copy_annotations(x_init, new_x)
            else:
                return new_x

    def to_numpy(self):
        return NumpyConv1dReshaper._from_torch(self)

class NumpyConv1dReshaper:
    def __init__(self, stride, unbind_dim):
        self.stride = stride
        self.unbind_dim = unbind_dim

    def __call__(self, x):
        left_padding = 0
        padding = [[left_padding, 0]] + [[0,0]]*(x.ndim-1)
        seq_length = x.shape[self.unbind_dim]
        x = np.swapaxes(x, 0, self.unbind_dim)
        x = np.pad(x, padding, mode='constant')
        new_length = seq_length + left_padding - (seq_length + left_padding) % self.stride
        x = x[:new_length]
        x = np.swapaxes(x, self.unbind_dim, 0)

        num_chunks = new_length // self.stride
        x_list = []
        for x_t in np.split(x, num_chunks, axis=self.unbind_dim):
            to_cat = list(np.swapaxes(x_t, 0, self.unbind_dim))
            x_list.append(np.concatenate(to_cat, -1))

        x = np.stack(x_list, self.unbind_dim)
        return x

    @classmethod
    def _from_torch(cls, parent):
        return cls(stride=parent.stride, unbind_dim=parent.unbind_dim)

    def __repr__(self):
        return f'Sequence Reshaper: Strided Conv1d[stride={self.stride}] -> Unstrided Conv1d'


class Split(nn.Module):
    def __init__(self, stride):
        super().__init__()
        self.stride = stride
        self.id = Identity()
    
    def forward(self, x):
        return torch.chunk(self.id(x), chunks=self.stride, dim=1)
       
    
class DWBufferRotation(SuperStructure):
    r""" Rotates the buffer. Here the buffer is kept in memory as a list of len
         (kernel_size-1)*dilation of states of shape in_channels.
    """
    def __init__(self, kernel_size, stride, dilation):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.split = Split(self.stride)

    def forward(self, x_t: Tensor, buff: List[Tensor]) -> Tuple[List[Tensor], List[Tensor]]:
        new_inputs = list(self.split(x_t))
        new_buff = buff[self.stride:] + new_inputs
        to_cat = buff[::self.dilation] + new_inputs[::self.dilation]
        
        return new_buff, to_cat


class SequencedDepthWiseTemporalConv1d(Sequencer):

    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int,
            stride: int = 1,
            dilation: int = 1,
            bias: bool = True):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.bias = bias
        buff_size = (kernel_size-1)*dilation
        state_shapes = [[in_channels]]*buff_size
        super().__init__(state_shapes, batch_dim=0, seq_dim=-1, return_hidden_state=True)

        self.buffer_rot = DWBufferRotation(self.kernel_size, self.stride, self.dilation)
        self.conv = DepthWiseConvSummer(self.in_channels, self.out_channels, self.kernel_size,
                                        self.bias)
        
    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        new_state, full_buffer = self.buffer_rot(x_t, state)
        
        _, to_cat = self.conv(full_buffer)
        o_t = torch.cat(to_cat, -1)
        
        return o_t, new_state

    def weight_init(self):
        k = math.sqrt(1 / (self.in_channels * self.kernel_size))
        for name, param in self.named_parameters():
            torch.nn.init.uniform_(param, -k, k)
            
class DepthWiseTemporalConv1d(nn.Module):
    """ Fmot optimized version of Depthwise Conv1d that can be patched and mapped.
    Equivalent of Conv1d with group = in_channels.
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int,
            stride: int = 1,
            dilation: int = 1,
            bias: bool = True):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.bias = bias
        self.K = int(out_channels/in_channels)
                    
        if self.K > 1:
            warnings.warn(
                'The number of out_channels per group is 2 or larger: ' +
                'the output of the Depthwise Conv1d will not match Pytorch ordering')

        if not(self.kernel_size % self.stride == 0):
            raise Exception('Kernel size should be a multiple of stride: other configuraions not supported yet')

        assert(out_channels%in_channels == 0), 'out_channels must be divisible by groups = in_channels'
        
        self.feature_dim = 1
        super().__init__()
        if self.stride != 1:
            self.reshaper = Conv1dReshaper(self.stride, unbind_dim=-1)
        else:
            self.reshaper = Identity()
        self.conv = SequencedDepthWiseTemporalConv1d(in_channels = self.in_channels,
                                                out_channels = self.out_channels,
                                                kernel_size = self.kernel_size,
                                                stride=self.stride,
                                                dilation = self.dilation,
                                                bias = self.bias)
        
    def forward(self, x):
        reshaped_x = self.reshaper(x)
        output, _ = self.conv(reshaped_x)
    
        return output
    
    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        assert type(parent) == TemporalConv1d
        assert(parent.groups == parent.in_channels), "This is not a Depthwise Conv1d"
        
        if parent.stride != 1 and not(isfrontendlayer(parent, toplevel)):
            raise Exception('Strided conv1d intermediate layers not supported')
        else:
            kernel_size = parent.kernel_size


            conv_layer = cls(in_channels=parent.in_channels, 
                             out_channels=parent.out_channels,
                             kernel_size=parent.kernel_size,
                             stride=parent.stride,
                             dilation=parent.dilation,
                             bias=parent.bias)

            group_in_channels = int(parent.in_channels / parent.groups)
            # K is the number of times we go through input channels
            K = int(parent.out_channels / parent.groups)

            # Given our computation method, the conv matrix of shape
            # (out_channels, in_channels, kernel_size) should be
            # (out_channels, in_channels * kernel_size) with tranpose weight matrix
            # Get a list of K weights of shape (in_channels, 1, kernel_size)
            weight_list = [parent.conv.weight[i::K] for i in range(K)] #list of weight
            # For each of these elem, unbind it along the kernel dimension to get column-weights
            weight_list = list(chain.from_iterable([torch.unbind(w, dim=-1) for w in weight_list]))
            if parent.bias:
                bias_list = [parent.conv.bias[i::K] for i in range(K)]

            weight_split_mapping = dict()
            bias_split_mapping = dict()
            for i, weight in enumerate(weight_list):
                rsetattr(conv_layer, 'conv.conv.lin_list.' + str(i) + '.weight', nn.Parameter(weight))
                new_param_name = 'model.' + inherited_name + 'conv.conv.lin_list.' + str(i) + '.weight'
                f = dw_subslct_wrapper(int(i/parent.kernel_size), K, i % parent.kernel_size)
                assert(torch.sum(f(parent.conv.weight) - weight) < 1e-5)
                f_inv = None
                weight_split_mapping[new_param_name] = (f, f_inv)

                if parent.bias and (i % parent.kernel_size == 0):
                    filter_set = i // parent.kernel_size
                    rsetattr(conv_layer, 'conv.conv.lin_list.' + str(i) + '.bias', nn.Parameter(bias_list[filter_set]))
                    new_param_name = 'model.' + inherited_name + 'conv.conv.lin_list.' + str(i) + '.bias'
                    bias_split_mapping[new_param_name] = None

            F_inv = dw_F_inv(parent.conv.weight.shape, K, kernel_size)
            inherited_dict[inherited_name + 'conv.weight'] = (weight_split_mapping, F_inv)
            if parent.bias:
                inherited_dict[inherited_name + 'conv.bias'] = (bias_split_mapping, F_inv)
            return conv_layer

    def weight_init(self):
        k = math.sqrt(1 / (self.hidden_size * self.kernel_size))
        for name, param in self.named_parameters():
            torch.nn.init.uniform_(param, -k, k)

class FmotConv1dWrapper():
    r""" 
    Wrapper for Conv1d. Maps the Torch TCN layer to its Sequencer version.
    
    In the case where in_channels = groups, we implement a particular version of the TCN
    in order to manage internally vector memory utilization and computations in an efficient manner. 
    This holds true only when the number of input channels in_channels is larger enough (>= 8).
    
    """
    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        internal_vector_length = 8
        if parent.in_channels == parent.groups and (parent.in_channels >= internal_vector_length):
            return DepthWiseTemporalConv1d._from_torchmodule(parent=parent,
                                                             toplevel=toplevel,
                                                             inherited_name=inherited_name,
                                                             inherited_dict=inherited_dict)
        else:
            return SequencedTemporalConv1d._from_torchmodule(parent=parent,
                                                             toplevel=toplevel,
                                                             inherited_name=inherited_name,
                                                             inherited_dict=inherited_dict)
        
    
