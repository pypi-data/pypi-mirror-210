from .unittest_objects import UTM, SUTM, TestSet, TestLibrary
import torch
from torch import nn
from itertools import product as iterprod
import numpy as np
from fmot.nn import RNNCell, LSTMCell, GRUCell, RNN, LSTM, GRU, MultiLayerRNN, Sequential
from fmot.nn import map_param_name, get_trailing_number
from fmot.nn import default_torch2seq_param_mapping
from fmot.nn import BasicRNN, SuperBasic, Sequencer
from fmot.nn import TemporalConv1d, AdaptiveFemtoGRU
import fmot
from .. import ds_tc_resnet
from torch import Tensor, nn
from typing import List, Tuple, Optional

rnn_library = TestLibrary('rnn')

class PrevStateSeq(Sequencer):
    def __init__(self, size):
        super().__init__(state_shapes=[[size]], batch_dim=0, seq_dim=1)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        prev, = state
        return prev, [x_t]

class PrevStateUTM(SUTM):
    def __init__(self, nb_timesteps, size):
        super().__init__()
        self.nb_timesteps = nb_timesteps
        self.input_size = size
        self.net = PrevStateSeq(size)

rnn_library['prev_state'] = TestSet(
    utm=PrevStateUTM,
    par_sets=[dict(size=S, nb_timesteps=N) for S, N in iterprod([32, 16], [6])])

class PrevStateAddOne(Sequencer):
    def __init__(self, size):
        super().__init__(state_shapes=[[size]], batch_dim=0, seq_dim=1)

    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        prev, = state
        return prev + 1, [x_t]

class PrevStateAddOneUTM(SUTM):
    def __init__(self, nb_timesteps, size):
        super().__init__()
        self.nb_timesteps = nb_timesteps
        self.input_size = size
        self.net = PrevStateAddOne(size)

rnn_library['prev_state_add_one'] = TestSet(
    utm=PrevStateAddOneUTM,
    par_sets=[dict(size=S, nb_timesteps=N) for S, N in iterprod([32, 16], [6])])

"""
MultiLayer RNN Unit Tests
"""
class RNNUTM(SUTM):
    def __init__(self, nb_timesteps: int, input_size: int, hidden_size:int, num_layers: int,
                 bias=True, batch_first=True, nonlinearity='tanh', dropout=0):
        super().__init__()
        self.nb_timesteps = nb_timesteps
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.net = torch.nn.RNN(input_size=input_size, 
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        bias=bias, 
                        batch_first=batch_first,
                        nonlinearity=nonlinearity,
                        dropout=dropout)


rnn_set = TestSet(
    utm=RNNUTM, 
    par_sets=[dict(nb_timesteps=nb_timesteps,
                   input_size=input_size, 
                   hidden_size=hidden_size, 
                   num_layers=num_layers,
                   bias=bias, 
                   batch_first=True,
                   dropout=0,
                   nonlinearity=nonlinearity) 
              for nb_timesteps, input_size, hidden_size, num_layers, bias, nonlinearity in 
              iterprod([6], [32], [32], [1,2], [True, False], ['tanh', 'relu'])]
    )
rnn_library['rnn'] = rnn_set

"""
MultiLayer GRU Unit Tests
"""
class GRUUTM(SUTM):
    def __init__(self, nb_timesteps: int, input_size: int, hidden_size:int, num_layers: int,
                 bias=True, batch_first=True, nonlinearity='tanh', dropout=0):
        super().__init__()
        self.nb_timesteps = nb_timesteps
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.net = torch.nn.GRU(input_size=input_size, 
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        bias=bias, 
                        batch_first=batch_first,
                        dropout=dropout,
                        bidirectional=False)


gru_set = TestSet(
    utm=GRUUTM, 
    par_sets=[dict(nb_timesteps=nb_timesteps,
                   input_size=input_size,
                   hidden_size=hidden_size,
                   num_layers=num_layers,
                   bias=bias,
                   batch_first=True,
                   dropout=0)
              for nb_timesteps, input_size, hidden_size, num_layers, bias in 
              iterprod([6], [32], [32], [1,2], [True, False])]
    )
rnn_library['gru'] = gru_set

"""
MultiLayer LSTM Unit Tests
"""
class LSTMUTM(SUTM):
    def __init__(self, nb_timesteps: int, input_size: int, hidden_size:int, num_layers: int,
                 bias=True, batch_first=True, nonlinearity='tanh', dropout=0):
        super().__init__(converted_rtol=1e-2, allow_fqir_offby=10)
        self.nb_timesteps = nb_timesteps
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.net = torch.nn.LSTM(input_size=input_size, 
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        bias=bias, 
                        batch_first=batch_first,
                        dropout=dropout)


lstm_set = TestSet(
    utm=LSTMUTM, 
    par_sets=[dict(nb_timesteps=nb_timesteps,
                   input_size=input_size,
                   hidden_size=hidden_size,
                   num_layers=num_layers,
                   bias=bias,
                   batch_first=True,
                   dropout=0)
              for nb_timesteps, input_size, hidden_size, num_layers, bias in 
              iterprod([6], [32, 64], [32, 64], [1,2], [True, False])]
    )
rnn_library['lstm'] = lstm_set

class TemporalConv1dUTM(SUTM):
     def __init__(self, nb_timesteps, in_channels, out_channels, kernel_size,
          dilation, stride):
          super().__init__(batch_dim=0, seq_dim=2, skip_mixed=True)
          self.nb_timesteps = nb_timesteps
          self.in_channels = in_channels
          self.out_channels = out_channels
          self.kernel_size = kernel_size
          self.dilation = dilation
          self.stride = stride
          self.net = TemporalConv1d(
               in_channels=in_channels,
               out_channels=out_channels,
               kernel_size=kernel_size,
               dilation=dilation,
               stride=stride)

     def forward(self, x):
          return self.net(x)

     def _get_random_inputs(self, batch_size):
        random_inputs = torch.randn(batch_size, self.in_channels, self.nb_timesteps)
        return random_inputs

rnn_library['temporal_conv1d'] = TestSet(
     utm=TemporalConv1dUTM,
     par_sets=[dict(
          nb_timesteps=T,
          in_channels=Cin,
          out_channels=Cout,
          kernel_size=K,
          dilation=D,
          stride=S)
     for T, Cin, Cout, K, D, S in
     iterprod([16], [32], [32], [3, 4], [1, 2], [1])])

rnn_library['big_conv1d'] = TestSet(
     utm=TemporalConv1dUTM,
     par_sets=[dict(
          nb_timesteps=T,
          in_channels=Cin,
          out_channels=Cout,
          kernel_size=K,
          dilation=D,
          stride=S)
     for T, Cin, Cout, K, D, S in
     iterprod([16], [64, 128], [64, 128], [3], [1, 2], [1])])

class LinGRULinUTM(SUTM):
    def __init__(self, nb_timesteps, Din, H, Dout):
        super().__init__()
        self.nb_timesteps = nb_timesteps
        self.input_size = Din
        self.hidden_size = H
        self.lin_in = nn.Linear(Din, H)
        self.gru = nn.GRU(H, H, batch_first=True)
        self.lin_out = nn.Linear(H, Dout)
        self.relu0 = nn.ReLU()
        self.relu1 = nn.ReLU()

    def forward(self, x):
        x = self.relu0(self.lin_in(x))
        x, __ = self.gru(x)
        x = self.relu1(self.lin_out(x))
        return x
rnn_library['lin_gru_lin'] = TestSet(
     utm=LinGRULinUTM,
     par_sets=[dict(
          nb_timesteps=T,
          Din=Din,
          H=H,
          Dout=Dout)
     for T, Din, H, Dout in
     iterprod([16], [64], [128], [64, 128])])

class DWConv1dUTM(SUTM):
    def __init__(self, nb_timesteps, D, kernel_size):
        super().__init__(batch_dim=0, seq_dim=2, skip_mixed=True)
        self.nb_timesteps = nb_timesteps
        self.D = D
        self.kernel_size = kernel_size
        self.net = TemporalConv1d(
            in_channels=D,
            out_channels=D,
            groups=D,
            kernel_size=kernel_size)

    def forward(self, x):
        return self.net(x)

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.D, self.nb_timesteps)

rnn_library['dw_conv1d'] = TestSet(
    utm=DWConv1dUTM,
    par_sets=[dict(nb_timesteps=T, D=D, kernel_size=K) 
        for T, D, K in iterprod([10], [32], [2,4,8])])

class TCResNetUTM(SUTM):
    def __init__(self, nb_timesteps, input_size, model_fn):
        super().__init__(batch_dim=0, seq_dim=2, skip_mixed=True)
        self.nb_timesteps = nb_timesteps
        self.input_size = input_size
        self.net = model_fn(input_size=input_size)

    def forward(self, x):
        return self.net(x)

    def _get_random_inputs(self, batch_size):
        return torch.randn(batch_size, self.input_size, self.nb_timesteps)

rnn_library['tc_resnet'] = TestSet(
    utm = TCResNetUTM,
    par_sets=[dict(nb_timesteps=10, input_size=20, model_fn=ds_tc_resnet.model)])

rnn_library['small_tc_resnet'] = TestSet(
    utm = TCResNetUTM,
    par_sets=[dict(nb_timesteps=10, input_size=20, model_fn=ds_tc_resnet.small_model)])

rnn_library['tiny_tc_resnet'] = TestSet(
    utm = TCResNetUTM,
    par_sets=[dict(nb_timesteps=10, input_size=20, model_fn=ds_tc_resnet.tiny_model)])

large_rnn_set = TestSet(
    utm=GRUUTM, 
    par_sets=[dict(nb_timesteps=nb_timesteps,
                   input_size=input_size,
                   hidden_size=hidden_size,
                   num_layers=num_layers,
                   bias=bias,
                   batch_first=True,
                   dropout=0)
              for nb_timesteps, input_size, hidden_size, num_layers, bias in 
              iterprod([1], [128, 256], [128, 256], [1], [True])]
    )
rnn_library['large_rnn'] = gru_set