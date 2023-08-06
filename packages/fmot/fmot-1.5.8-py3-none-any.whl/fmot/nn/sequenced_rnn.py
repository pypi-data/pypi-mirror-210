import torch
import math
from torch import nn
from ..utils import rsetattr, rgetattr
from .sequencer import Sequencer, unbind, stack, chunk, cat
from .super_structures import SuperStructure
from .atomics import Identity
from fmot.utils import ActivationCountingReLU
from fmot import CONFIG

# We need to import these for explicit type annotations
from typing import List, Tuple, Optional, Any
from torch import Tensor

# TODO: For Conv1d, Padding (left padding by default now), stride, dilatation, padding_mode

# TODO: Move that part to another file
import re
import functools

default_torch2seq_param_mapping = {
    'weight_ih_l': ('layers.', '.linear_ih.weight'),
    'weight_hh_l': ('layers.', '.linear_hh.weight'),
    'bias_ih_l': ('layers.', '.linear_ih.bias'),
    'bias_hh_l': ('layers.', '.linear_hh.bias'),
}


def get_trailing_number(s):
    # Find the integers at the end of a string
    m = re.search(r'\d+$', s)
    return m.group() if m else None


def map_param_name(torch_name, param_mapping=default_torch2seq_param_mapping):
    # Find the layer number from string
    l = get_trailing_number(torch_name)
    torch_key = torch_name.replace(l, "")
    s_start, s_end = param_mapping[torch_key]
    seq_name = s_start + l + s_end

    return seq_name


def transfer_param(parent, sequencer, inherited_name, inherited_dict):
    for name, param in parent.named_parameters():
        rsetattr(sequencer, map_param_name(name), param)
        new_param_name = "model." + inherited_name + map_param_name(name)
        inherited_dict[inherited_name + name] = ({new_param_name: None}, None)


# TODO: Add Dropout


class RNNCell(Sequencer):
    r''' Define a logic unit for baseline RNNs
    '''

    def __init__(self, input_size: int, hidden_size: int, bias=True, batch_first=False,
                 nonlinearity='tanh', dropout=0):
        # state_shapes is a list of hidden-state shapes
        state_shapes = [[hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.nonlinearity = nonlinearity
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        # Base class must be initialized with state-shape and optionally batch_first attributes
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, self.hidden_size, self.bias)

        if self.nonlinearity == 'tanh':
            self.nonlinearity_layer = torch.nn.Tanh()
            if CONFIG.rnn_mm_limits:
                self.linear_ih.limits = (-4, 4)
                self.linear_hh.limits = (-4, 4)
        elif self.nonlinearity == 'relu':
            self.nonlinearity_layer = torch.nn.ReLU()
        elif self.nonlinearity == 'identity':
            self.nonlinearity_layer = torch.nn.Identity()
        else:
            raise ValueError("Unknown nonlinearity '{}'".format(self.nonlinearity))

        self.weight_init()

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, = state
        n = self.linear_ih(x_t) + self.linear_hh(h_t)
        h_t = self.nonlinearity_layer(n)

        return h_t, [h_t]

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        sequencer = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                        bias=parent.bias, batch_first=parent.batch_first,
                        nonlinearity=parent.nonlinearity, dropout=parent.dropout)

        transfer_param(parent, sequencer, inherited_name, inherited_dict)

        return sequencer


class LSTMCell(Sequencer):
    r''' Define a logic unit for baseline LSTMs
    '''

    def __init__(self, input_size: int, hidden_size: int, bias=True, batch_first=False,
                 dropout=0):
        # state_shapes is a list of hidden-state shapes
        state_shapes = [[hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        # Base class must be initialized with state-shape and optionally batch_first attributes
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 4 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 4 * self.hidden_size, self.bias)

        if CONFIG.rnn_mm_limits:
            self.linear_ih.limits = (-8, 8)
            self.linear_hh.limits = (-8, 8)

        self.weight_init()

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t = state
        stacked_layer = self.linear_ih(x_t) + self.linear_hh(h_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t)
        f_t = torch.sigmoid(f_t)
        g_t = torch.tanh(g_t)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)

        return h_t, [h_t, c_t]

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        sequencer = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                        bias=parent.bias, batch_first=parent.batch_first, dropout=parent.dropout)

        transfer_param(parent, sequencer, inherited_name, inherited_dict)

        return sequencer
    
class FusedLSTMCell(Sequencer):
    r'''FusedLSTMCell performs matrix-fusion, combining the forward and recurrent matrices into one
    matrix. This allows better quantization, since partial ih and hh products are added together at
    i32 precision, instead of being serialized at i16 or i8 before adding.
    '''

    def __init__(self, input_size: int, hidden_size: int, bias=True, batch_first=False,
                 dropout=0):
        # state_shapes is a list of hidden-state shapes
        state_shapes = [[hidden_size], [hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        # Base class must be initialized with state-shape and optionally batch_first attributes
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear = nn.Linear(self.input_size + self.hidden_size, 4 * self.hidden_size, self.bias)

        self.linear.limits = (-8, 8)

        self.weight_init()

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t = state
        e_t = torch.cat([x_t, h_t], dim=-1)
        stacked_layer = self.linear(e_t)

        i_t, f_t, g_t, o_t = stacked_layer.chunk(4, 1)
        i_t = torch.sigmoid(i_t)
        f_t = torch.sigmoid(f_t)
        g_t = torch.tanh(g_t)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_t + i_t * g_t
        h_t = o_t * torch.tanh(c_t)

        return h_t, [h_t, c_t]
    
    def transfer_lstm_params(self, parent: torch.nn.LSTM, layer_idx=0):
        w_ih = getattr(parent, f'weight_ih_l{layer_idx}').data
        w_hh = getattr(parent, f'weight_hh_l{layer_idx}').data
        weight = torch.cat([w_ih, w_hh], dim=-1)

        self.linear.weight.data = weight

        if parent.bias:
            b_ih = getattr(parent, f'bias_ih_l{layer_idx}').data
            b_hh = getattr(parent, f'bias_hh_l{layer_idx}').data
            bias = b_ih + b_hh

            self.linear.bias.data = bias


class GRUCell(Sequencer):
    r''' Define a logic unit for baseline GRU
    '''

    def __init__(self, input_size: int, hidden_size: int, bias=True, batch_first=False,
                 dropout=0):
        state_shapes = [[hidden_size]]
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        # Base class must be initialized with state-shape and optionally batch_first attributes
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)
        self.linear_ih = nn.Linear(self.input_size, 3 * self.hidden_size, self.bias)
        self.linear_hh = nn.Linear(self.hidden_size, 3 * self.hidden_size, self.bias)

        if CONFIG.rnn_mm_limits:
            self.linear_ih.limits = (-8, 8)
            self.linear_hh.limits = (-8, 8)
            
        self.weight_init()

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, = state

        stacked_layer_i = self.linear_ih(x_t)
        stacked_layer_h = self.linear_hh(h_t)

        # Dim 0 = Batch Dim
        r_t, z_t, n_t = stacked_layer_i.chunk(3, 1)
        r_t_h, z_t_h, n_t_h = stacked_layer_h.chunk(3, 1)

        r_t = torch.sigmoid(r_t + r_t_h)
        z_t = torch.sigmoid(z_t + z_t_h)
        n_t = torch.tanh(n_t + r_t * n_t_h)

        h_t = (1 - z_t) * n_t + z_t * h_t

        return h_t, [h_t]

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        sequencer = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                        bias=parent.bias, batch_first=parent.batch_first, dropout=parent.dropout)
        transfer_param(parent, sequencer, inherited_name, inherited_dict)
        return sequencer    


class MultiLayerRNN(SuperStructure):
    def __init__(self, layers: List[Sequencer]):
        r"""MultiLayers RNNs are a super structures from which custom multi-layers RNN should be subclassed. 
        They allow the user to define control-flows in the forward method at training time, but these control 
        flows will be frozem in the final FQIR graph (see FQIR documentation).
        
        Args:
            layers (List[Sequencer]): list of the sequencers that we stack together, and that are
                going to be applied to the input at each time step.

    Inputs: input, h_0
        - **input** (Tensor): Input tensor
        - **h_0** (List[Tensor]): List of hidden states

    Outputs: output, h_n
        - **output** (Tensor): Output tensor

        - **h_n** (List(Tensor)): List of new hidden states
          
        """
        super().__init__()
        self.layers = nn.ModuleList(layers)

    @torch.jit.export
    def forward(self, x, state: Optional[List[Tensor]] = None) -> Tuple[Tensor, List[Tensor]]:
        state_out = []
        for l, layer in enumerate(self.layers):
            if state is None:
                state_tprev_l = None
            else:
                state_tprev_l = [state[l]]
            x, state_l = layer(x, state_tprev_l)
            state_out.append(state_l[0])
        return x, state_out


class Sequential(nn.Sequential):
    """Equivalent to PyTorch's :class:`nn.Sequential`
    but working with Sequencers and MultiLayerRNN instead of nn.Modules. 
    We override torch's sequential because its forward method signature does not match ours

    Modules will be added to it in the order they are passed in the constructor.
    The user can define a model by providing the sequencers that are going to be applied
    to the input at each time step.
    """

    @torch.jit.export
    def forward(self, input):
        for module in self:
            input, _ = module(input)
        return input


class RNN(MultiLayerRNN):
    r"""Generate a MultiLayerRNN equivalent of a PyTorch multi-layer Elman RNN. Can be applied
    it to an input sequence with :math:`\tanh` or :math:`\text{ReLU}` non-linearity. 

    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        h_t = \tanh(W_{ih} x_t + b_{ih} + W_{hh} h_{(t-1)} + b_{hh})

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is
    the input at time `t`, and :math:`h_{(t-1)}` is the hidden state of the
    previous layer at time `t-1` or the initial hidden state at time `0`.
    If :attr:`nonlinearity` is ``'relu'``, then :math:`\text{ReLU}` is used instead of :math:`\tanh`.

    Args:
        input_size (int): The number of expected features in the input `x`
        hidden_size (int): The number of features in the hidden state `h`
        num_layer (int)s: Number of recurrent layers. E.g., setting ``num_layers=2``
            would mean stacking two RNNs together to form a `stacked RNN`,
            with the second RNN taking in outputs of the first RNN and
            computing the final results. Default: 1
        nonlinearity (str): The non-linearity to use. Can be either ``'tanh'`` or ``'relu'``. Default: ``'tanh'``
        bias: If ``False``, then the layer does not use bias weights `b_ih` and `b_hh`.
            Default: ``True``
        batch_first (bool): If ``True``, then the input and output tensors are provided
            as `(batch, seq, feature)`. Default: ``True``
        dropout (float): If non-zero, introduces a `Dropout` layer on the outputs of each
            RNN layer except the last layer, with dropout probability equal to
            :attr:`dropout`. Default: 0

    Inputs: input, h_0
        - **input** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, input_size)`: 
          tensor containing the features of the input sequence. If ``self._streaming = False``, tensor of
          shape `(batch, input_size)` representing the input only one time step.
        - **h_0** (List[Tensor]): list of shape ``num_layers`` where each element is
          a Tensor of shape `(batch, hidden_size)`: tensor containing the initial hidden state for each element in the batch.
          Defaults to zero if not provided.

    Outputs: output, h_n
        - **output** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, hidden_size)`: tensor
          containing the output features (`h_t`) from the last layer of the RNN, for each `t`.
          If ``self._streaming = False``, tensor of shape `(batch, hidden_size)` representing the output after
          only one time step.

        - **h_n** (List(Tensor)): If ``self.return_hidden_state = True``, a list of length `num_layers`, where
          each element is a tensor of shape `(batch, hidden_size)` is also returned: tensor
          containing the hidden state for the last time step `t = seq_len`. 
          If ``self.return_hidden_state = False``, this term is not returned.

    Shape:
        - Input1: If we are in streaming mode, :math:`(B, L, H_{in})` (otherwise :math:`(B, H_{in})`)
          tensor containing input features where
          :math:`H_{in}=\text{input\_size}` and `L` represents a sequence length,
          and `B` represents the number of batches.
        - Input2: List(:math:`(B, H_{out})`) list of length :math:`S=num_layers`
          of tensors containing the initial hidden state for each element in the batch
          and for each layer.
          :math:`H_{out}=hidden\_size`
          Defaults to zero if not provided.
        - Output1: If we are in streaming mode, :math:`(B, L, H_{all})` (otherwise math:`(B, H_{all})`)
          where :math:`H_{all}=hidden_size`
        - Output2: List(:math:`(B, H_{out})`) list of tensors containing the next hidden state
          for each element in the batch for each layer.

    Attributes:
        layers.[k].linear_ih: the learnable input-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights of shape `(hidden_size, input_size)` for `k = 0`. Otherwise, the shape is
            `(hidden_size, hidden_size)`. Bias of the k-th layer of shape `(hidden_size)`.
        layers.[k].linear_hh: the learnable input-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights of shape `(hidden_size, hidden_size)`. Bias of the k-th layer of shape `(hidden_size)`.

    .. note::
        All the weights and biases are initialized from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})`
        where :math:`k = \frac{1}{\text{hidden\_size}}`

    """

    def __init__(self, input_size: int, hidden_size: int, num_layers=1,
                 bias=True, batch_first=False, nonlinearity='tanh',
                 dropout=0):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.nonlinearity = nonlinearity
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        layers = [
            RNNCell(self.input_size, self.hidden_size, self.bias, self.batch_first, \
                    self.nonlinearity, self.dropout), \
            *[RNNCell(self.hidden_size, self.hidden_size, self.bias, self.batch_first, \
                      self.nonlinearity, self.dropout) for _ in range(num_layers - 1)]
        ]

        super().__init__(layers)

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        multilayer_rnn = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                             num_layers=parent.num_layers, bias=parent.bias,
                             batch_first=parent.batch_first, nonlinearity=parent.nonlinearity,
                             dropout=parent.dropout)

        transfer_param(parent, multilayer_rnn, inherited_name, inherited_dict)

        return multilayer_rnn


class LSTM(MultiLayerRNN):
    r"""Generate a MultiLayerRNN equivalent of a PyTorch multi-layer long short-term memory (LSTM) RNN. Can be applied
    it to an input sequence. 


    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \begin{array}{ll} \\
            i_t = \sigma(W_{ii} x_t + b_{ii} + W_{hi} h_{t-1} + b_{hi}) \\
            f_t = \sigma(W_{if} x_t + b_{if} + W_{hf} h_{t-1} + b_{hf}) \\
            g_t = \tanh(W_{ig} x_t + b_{ig} + W_{hg} h_{t-1} + b_{hg}) \\
            o_t = \sigma(W_{io} x_t + b_{io} + W_{ho} h_{t-1} + b_{ho}) \\
            c_t = f_t \odot c_{t-1} + i_t \odot g_t \\
            h_t = o_t \odot \tanh(c_t) \\
        \end{array}

    where :math:`h_t` is the hidden state at time `t`, :math:`c_t` is the cell
    state at time `t`, :math:`x_t` is the input at time `t`, :math:`h_{t-1}`
    is the hidden state of the layer at time `t-1` or the initial hidden
    state at time `0`, and :math:`i_t`, :math:`f_t`, :math:`g_t`,
    :math:`o_t` are the input, forget, cell, and output gates, respectively.
    :math:`\sigma` is the sigmoid function, and :math:`\odot` is the Hadamard product.

    In a multilayer LSTM, the input :math:`x^{(l)}_t` of the :math:`l` -th layer
    (:math:`l >= 2`) is the hidden state :math:`h^{(l-1)}_t` of the previous layer multiplied by
    dropout :math:`\delta^{(l-1)}_t` where each :math:`\delta^{(l-1)}_t` is a Bernoulli random
    variable which is :math:`0` with probability :attr:`dropout`.
    
    Args:
        input_size (int): The number of expected features in the input `x`
        hidden_size (int): The number of features in the hidden state `h`
        num_layer (int): Number of recurrent layers. E.g., setting ``num_layers=2``
            would mean stacking two LSTMs together to form a `stacked LSTM`,
            with the second LSTM taking in outputs of the first LSTM and
            computing the final results. Default: 1
        bias: If ``False``, then the layer does not use bias weights `b_ih` and `b_hh`.
            Default: ``True``
        batch_first (bool): If ``True``, then the input and output tensors are provided
            as `(batch, seq, feature)`. Default: ``True``
        dropout (float): If non-zero, introduces a `Dropout` layer on the outputs of each
            RNN layer except the last layer, with dropout probability equal to
            :attr:`dropout`. Default: 0

    Inputs: input, hc_0
        - **input** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, input_size)`: 
          tensor containing the features of the input sequence. If ``self._streaming = False``, tensor of
          shape `(batch, input_size)` representing only one time step.
        - **hc_0** (List[Tensor]): list of shape ``2*num_layers`` where each element is
          a Tensor of shape `(batch, hidden_size)`: the list contains a tensor representing 
          the initial hidden state followed by the intial cell state for each element in the batch for each layer.
          Defaults to zero if not provided.

    Outputs: output, hc_n
        - **output** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, hidden_size)`: tensor
          containing the output features (`h_t`) from the last layer of the LSTM, for each `t`.
          If ``self._streaming = False``, tensor of shape `(batch, hidden_size)` representing the output fter
          only one time step.

        - **hc_n** (List(Tensor)): If ``self.return_hidden_state = True``, a list of length `2*num_layers`, where
          each element is a tensor of shape `(batch, hidden_size)` is also returned: list of tensors
          containing the hidden state followed by the cell state for the last time step `t = seq_len` for each layer.
          If ``self.return_hidden_state = False``, this term is not returned.

    Shape:
        - Input1: If we are in streaming mode, :math:`(B, L, H_{in})` (otehrwise :math:`(B, H_{in})`)
          tensor containing input features where
          :math:`H_{in}=input_size` and `L` represents a sequence length,
          and `B` represents the number of batches.
        - Input2: List(:math:`(B, 2*H_{out})`) list of length :math:`S=num_layers` 
          of tensors containing the initial hidden state stacked with the intial cell state
          for each element in the batch and for each layer.
          :math:`H_{out}=hidden_size`
          Defaults to zero if not provided.
        - Output1: If we are in streaming mode, :math:`(B, L, H_{all})` (otherwise :math:`(B, H_{all})`)
          where :math:`H_{all}=hidden_size`
        - Output2: List(:math:`(B, 2*H_{out})`) list of tensors containing the next hidden state
          stacked with next cell state for each element in the batch for each layer.

    Attributes:
        layers.[k].linear_ih: the learnable input-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights `(W_ii|W_if|W_ig|W_io)`, of shape `(4*hidden_size, input_size)` for `k = 0`. Otherwise, the shape is
            `(4*hidden_size, hidden_size)`. Bias `(b_ii|b_if|b_ig|b_io)` of the k-th layer of shape `(4*hidden_size)`.
        layers.[k].linear_hh: the learnable hidden-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights `(W_ii|W_if|W_ig|W_io)`, of shape `(4*hidden_size, hidden_size)` for `k = 0`.
            Bias `(b_ii|b_if|b_ig|b_io)` of the k-th layer of shape `(4*hidden_size)`.

    .. note::
        All the weights and biases are initialized from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})`
        where :math:`k = \frac{1}{\text{hidden\_size}}`

    """

    def __init__(self, input_size: int, hidden_size: int, num_layers=1,
                 bias=True, batch_first=False, dropout=0):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        if CONFIG.fused_lstm:
            cell_cls = FusedLSTMCell
        else:
            cell_cls = LSTMCell

        layers = [
            cell_cls(self.input_size, self.hidden_size, self.bias, self.batch_first, \
                     self.dropout), \
            *[cell_cls(self.hidden_size, self.hidden_size, self.bias, self.batch_first, \
                       self.dropout) for _ in range(num_layers - 1)]
        ]

        super().__init__(layers)

    @torch.jit.export
    def forward(self, x, state: Optional[List[Tensor]] = None) -> Tuple[Tensor, List[Tensor]]:
        state_out = []
        for l, layer in enumerate(self.layers):
            if state is None:
                state_tprev_l = None
            else:
                state_tprev_l = [state[2 * l], state[2 * l + 1]]
            x, state_l = layer(x, state_tprev_l)
            state_out.append(state_l[0])
            state_out.append(state_l[1])
        return x, state_out

    @classmethod
    def _from_torchmodule(cls, parent: torch.nn.LSTM, toplevel=None, inherited_name="", inherited_dict=dict()):
        multilayer_rnn = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                             bias=parent.bias, num_layers=parent.num_layers,
                             batch_first=parent.batch_first, dropout=parent.dropout)
        if CONFIG.fused_lstm:
            for idx in range(parent.num_layers):
                layer: FusedLSTMCell = multilayer_rnn.layers[idx]
                layer.transfer_lstm_params(parent, idx)
        else:
            transfer_param(parent, multilayer_rnn, inherited_name, inherited_dict)

        return multilayer_rnn


class GRU(MultiLayerRNN):
    r"""Generate a MultiLayerRNN equivalent of a PyTorch multi-layer gated recurrent unit (GRU) RNN. Can be applied
    it to an input sequence. 


    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \begin{array}{ll}
            r_t = \sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{(t-1)} + b_{hr}) \\
            z_t = \sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{(t-1)} + b_{hz}) \\
            n_t = \tanh(W_{in} x_t + b_{in} + r_t * (W_{hn} h_{(t-1)}+ b_{hn})) \\
            h_t = (1 - z_t) * n_t + z_t * h_{(t-1)}
        \end{array}

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is the input
    at time `t`, :math:`h_{(t-1)}` is the hidden state of the layer
    at time `t-1` or the initial hidden state at time `0`, and :math:`r_t`,
    :math:`z_t`, :math:`n_t` are the reset, update, and new gates, respectively.
    :math:`\sigma` is the sigmoid function, and :math:`*` is the Hadamard product.

    In a multilayer GRU, the input :math:`x^{(l)}_t` of the :math:`l` -th layer
    (:math:`l >= 2`) is the hidden state :math:`h^{(l-1)}_t` of the previous layer multiplied by
    dropout :math:`\delta^{(l-1)}_t` where each :math:`\delta^{(l-1)}_t` is a Bernoulli random
    variable which is :math:`0` with probability :attr:`dropout`.

    Args:
        input_size (int): The number of expected features in the input `x`
        hidden_size (int): The number of features in the hidden state `h`
        num_layer (int)s: Number of recurrent layers. E.g., setting ``num_layers=2``
            would mean stacking two GRUs together to form a `stacked GRU`,
            with the second GRU taking in outputs of the first GRU and
            computing the final results. Default: 1
        nonlinearity (str): The non-linearity to use. Can be either ``'tanh'`` or ``'relu'``. Default: ``'tanh'``
        bias: If ``False``, then the layer does not use bias weights `b_ih` and `b_hh`.
            Default: ``True``
        batch_first (bool): If ``True``, then the input and output tensors are provided
            as `(batch, seq, feature)`. Default: ``True``
        dropout (float): If non-zero, introduces a `Dropout` layer on the outputs of each
            RNN layer except the last layer, with dropout probability equal to
            :attr:`dropout`. Default: 0

    Inputs: input, h_0
        - **input** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, input_size)`: 
          tensor containing the features of the input sequence. If ``self._streaming = False``, tensor of
          shape `(batch, input_size)` representing only one time step.
        - **h_0** (List[Tensor]): list of shape ``num_layers`` where each element is
          a Tensor of shape `(batch, hidden_size)`: tensor containing the initial hidden state for each element in the batch.
          Defaults to zero if not provided.

    Outputs: output, h_n
        - **output** (Tensor): If ``self._streaming = True``, tensor of shape `(batch, seq_len, hidden_size)`: tensor
          containing the output features (`h_t`) from the last layer of the RNN, for each `t`.
          If ``self._streaming = False``, tensor of shape `(batch, hidden_size)` representing the output after
          only one time step.

        - **h_n** (List(Tensor)): If ``self.return_hidden_state = True``, a list of length `num_layers`, where
          each element is a tensor of shape `(batch, hidden_size)` is also returned: tensor
          containing the hidden state for the last time step `t = seq_len`. 
          If ``self.return_hidden_state = False``, this term is not returned.

    Shape:
        - Input1: If we are in streaming mode, :math:`(B, L, H_{in})` (otherwise :math:`(B, H_{in})`)
          tensor containing input features where
          :math:`H_{in}=\text{input\_size}` and `L` represents a sequence length,
          and `B` represents the number of batches.
        - Input2: List(:math:`(B, H_{out})`) list of length :math:`S=\text{num\_layers}` 
          of tensors containing the initial hidden state for each element in the batch
          and for each layer.
          :math:`H_{out}=\text{hidden\_size}`
          Defaults to zero if not provided.
        - Output1: If we are in streaming mode, :math:`(B, L, H_{all})` (otherwise `(B, H_{all})`)
          where :math:`H_{all}=\text{hidden\_size}`
        - Output2: List(:math:`(B, H_{out})`) list of tensors containing the next hidden state
          for each element in the batch for each layer.

    Attributes:
        layers.[k].linear_ih: the learnable input-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights `(W_ir|W_iz|W_in)`, of shape `(3*hidden_size, input_size)` for `k = 0`. Otherwise, the shape is
            `(3*hidden_size, hidden_size)`. Bias `(b_ir|b_iz|b_in)`, of the :math:`\text{k}^{th}` layer of shape `(3*hidden_size)`.
        layers.[k].linear_hh: the learnable hidden-hidden linear layer (weights and bias) of the :math:`\text{k}^{th}` layer.
            Weights `(W_hr|W_hz|W_hn)`, of shape `(3*hidden_size, hidden_size)`. Bias `(b_hr|b_hz|b_hn)`, of the :math:`\text{k}^{th}` 
            layer of shape `(3*hidden_size)`.

    .. note::
        All the weights and biases are initialized from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})`
        where :math:`k = \frac{1}{\text{hidden\_size}}`

    """

    def __init__(self, input_size: int, hidden_size: int, num_layers=1,
                 bias=True, batch_first=False,
                 dropout=0):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bias = bias
        self.batch_first = batch_first
        self.dropout = dropout

        layers = [
            GRUCell(self.input_size, self.hidden_size, self.bias, self.batch_first, 
                    self.dropout), 
            *[GRUCell(self.hidden_size, self.hidden_size, self.bias, self.batch_first, 
                      self.dropout) for _ in range(num_layers - 1)]
        ]

        super().__init__(layers)

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        multilayer_rnn = cls(input_size=parent.input_size, hidden_size=parent.hidden_size,
                             bias=parent.bias, num_layers=parent.num_layers,
                             batch_first=parent.batch_first, dropout=parent.dropout)

        transfer_param(parent, multilayer_rnn, inherited_name, inherited_dict)

        return multilayer_rnn


def sru_transfer_param(parent, sequencer, inherited_name, inherited_dict):
    for name, param in parent.named_parameters():
        rsetattr(sequencer, name, param)
        new_param_name = "model." + inherited_name + name
        inherited_dict[inherited_name + name] = ({new_param_name: None}, None)


class SRUSequencer(Sequencer):
    r''' Define a logic unit for a Simple Recurrent Unit network.
    '''

    def __init__(self, hidden_size: int, batch_first: bool = True):
        state_shapes = [[hidden_size], [hidden_size]]
        self.hidden_size = hidden_size
        self.batch_first = batch_first

        # Base class must be initialized with state-shape and optionally batch_first attributes
        assert (batch_first == True)  # assume seq_dim = 1, feat_dim =2
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim, seq_dim)

        self.u = nn.Linear(hidden_size, 3 * hidden_size, bias=False)

        self.vf = nn.Parameter(torch.randn(hidden_size))
        self.vr = nn.Parameter(torch.randn(hidden_size))
        self.bf = nn.Parameter(torch.zeros(hidden_size))
        self.br = nn.Parameter(torch.zeros(hidden_size))

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h_t, c_t = state
        ux_t = self.u(x_t)

        xf_t, xc_t, xr_t = ux_t.chunk(3, dim=1)

        xf_t = xf_t + self.bf
        xr_t = xr_t + self.br

        f_t = torch.sigmoid(xf_t + self.vf * c_t)
        r_t = torch.sigmoid(xr_t + self.vr * c_t)
        c_t = f_t * c_t + (1 - f_t) * xc_t
        h_t = r_t * c_t + (1 - r_t) * x_t

        return h_t, [h_t, c_t]

    @classmethod
    def _from_torchmodule(cls, parent, toplevel=None, inherited_name="", inherited_dict=dict()):
        sequencer = cls(hidden_size=parent.hidden_size,
                        batch_first=parent.batch_first, )

        sru_transfer_param(parent, sequencer, inherited_name, inherited_dict)

        return sequencer
