import torch
from torch import nn
import fmot
from typing import *
from fmot.nn.stft import STFTBuffer, STFT
from fmot.nn.fft import DFTFromRFFT, DFT
import pytest

@pytest.mark.xfail
def test_bad_size_buff():
    buff = STFTBuffer(130, 128)

def test_good_size_buff():
    buff = STFTBuffer(256, 128)

@torch.no_grad()
def test_buffer_runs():
    buff = STFTBuffer(256, 128)
    x = torch.randn(1, 5, 128)
    y, __ = buff(x)
    assert y.shape[0] == 1
    assert y.shape[1] == 5
    assert y.shape[2] == 256

    cmodel = fmot.ConvertedModel(buff, seq_dim=1)
    y, __ = cmodel(x)
    cmodel.quantize([torch.randn(1, 5, 128) for _ in range(4)])
    graph = cmodel.trace()
    print(graph)
    
    assert True

@torch.no_grad()
def test_stft():
    stft = STFT(256, 128, 1, window_fn=torch.hann_window(256))
    x = torch.randn(1, 5, 128)
    y, __ = stft(x)
    assert y.shape[0] == 1
    assert y.shape[1] == 5
    assert y.shape[2] == 129

    cmodel = fmot.ConvertedModel(stft, seq_dim=1)
    print(cmodel)
    y, __ = cmodel(x)
    cmodel.quantize([torch.randn(1, 5, 128) for _ in range(4)])
    graph = cmodel.trace()
    print(graph)
    
    assert True

@torch.no_grad()
def measure_stft(hop=128, n_stages=3, dyn_only=False):
    window=hop*2
    window_fn = torch.hann_window(window)
    
    stft = STFT(window, hop, n_stages, window_fn=window_fn)
    cmodel = fmot.ConvertedModel(stft, seq_dim=1)
    cmodel.quantize([torch.randn(1, 4, hop) for _ in range(3)])
    graph = cmodel.trace()

    import femtostack as fs
    import numpy as np
    hw_model = fs.compile(graph=graph, seq_dim=1)
    if dyn_only:
        input_period = None
    else:
        input_period = hop/16000
    __, metrics = hw_model.run_behavioral_sim(np.random.randn(1, hop), input_period=input_period)
    print(metrics)

@torch.no_grad()
def measure_dft_from_rfft():
    model_a = DFTFromRFFT(128)
    model_b = DFT(128)

    x = torch.randn(1, 128)
    yr0, yi0 = model_a(x)
    yr1, yi1 = model_b(x)

    print(yr0 - yr1)
    print(yi0 - yi1)

    cmodel = fmot.ConvertedModel(model_a)
    cmodel.quantize([torch.randn(2, 128) for _ in range(5)])

    graph = cmodel.trace()

    import femtostack as fs
    import numpy as np
    hw_model = fs.compile(graph=graph, seq_dim=1)
    __, metrics = hw_model.run_behavioral_sim(np.random.randn(128), input_period=None)
    print(metrics)

def measure_sparse_reuse(relu=False):
    class Model(nn.Module):
        def __init__(self, relu=False):
            super().__init__()
            self.weight = nn.Parameter(torch.randn(64, 64))
            if relu:
                self.relu1 = nn.ReLU()
                self.relu2 = nn.ReLU()
            else:
                self.relu1 = fmot.nn.Identity()
                self.relu2 = fmot.nn.Identity()
            

        def forward(self, x):
            x = self.relu1(x)
            x = torch.matmul(x, self.weight.T)
            x = self.relu2(x)
            x = torch.matmul(x, self.weight.T)
            return x

    model = Model(relu=relu)
    fmot.utils.prune_model_parameters(model, 0.9)

    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.randn(1, 64) for _ in range(4)])
    graph = cmodel.trace()
    print(graph)

    import femtostack as fs
    hw_model = fs.compile(graph=graph)
    hw_model.draw_compiled_graph(fname='last_graph.png')
    print('Success')

        



if __name__ == '__main__':
    
    # test_stft()
    measure_stft(256, 4, dyn_only=True)
    
    # measure_sparse_reuse(relu=True)
    # measure_dft_from_rfft()
    
    # test_buffer_runs()
