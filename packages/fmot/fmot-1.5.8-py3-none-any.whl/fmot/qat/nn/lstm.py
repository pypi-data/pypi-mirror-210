from dataclasses import dataclass
from fmot.qat.fake_quantization import fake_quantize
from fmot.qat.nn.atomics import AtomicModule, Table
from fmot.qat.nn.quantizers import ParameterQuantizer, GaussianObserver, MinMaxObserver, DEFAULT_OBSERVERS
import torch
from torch.nn import functional as F
from torch import Tensor
from typing import *
from fmot.qat.bitwidths import fqint4, fqint8, fqint16, Bitwidth, BitwidthConfig
import math
from dataclasses import dataclass
import numpy as np
from fmot.qat.annotated_tensors import annotate, asint
from torch.nn.utils.prune import custom_from_mask, remove
from fmot.configure import CONFIG

CALIBRATE_CELL = True
CALIBRATE_MM = True
MOV_AVG_CALIBRATION = False

def remove_pruning(model: torch.nn.Module):
    r""" Remove the pruning reparametrization from all the
         modules of a model.

    Args:
        model: a PyTorch model
    """
    for name, param in list(model.named_parameters(recurse=False)):
        if name.endswith('_orig'):
            remove(model, name[:-5])

def get_masks(model: torch.nn.Module):
    masks = {}
    for name, buff in model.named_buffers(recurse=False):
        if name.endswith('_mask'):
            masks[name] = buff
    return masks

def apply_masks(model: torch.nn.Module, masks: Dict[str, Tensor]):
    for name, mask in masks.items():
        custom_from_mask(model, name[:-5], mask)
    return model

@dataclass
class LSTMConfig:
    tanh_limit: float = 4
    sigmoid_limit: float = 8
    cell_limit: float = 4
    alpha: float = 0.7
    act_bw: Bitwidth = fqint16
    lut_bw: Bitwidth = fqint8
    param_bw: Bitwidth = fqint8
    force_quantize: bool = False

    @property
    def matmul_quanta(self):
        return get_fixed_range_quanta(self.sigmoid_limit, self.act_bw.bitwidth)

    @property
    def sigmoid_addr_quanta(self):
        return get_fixed_range_quanta(self.sigmoid_limit, self.lut_bw.bitwidth)

    @property
    def tanh_addr_quanta(self):
        return get_fixed_range_quanta(self.tanh_limit, self.lut_bw.bitwidth)

    @property
    def unity_quanta(self):
        return get_fixed_range_quanta(1, self.act_bw.bitwidth)

    @property
    def cell_quanta(self):
        return get_fixed_range_quanta(self.cell_limit, self.act_bw.bitwidth)

    def act_quanta(self, maxabs: Tensor):
        if maxabs is None:
            maxabs = self.init_cell_limit
        else:
            maxabs = maxabs.detach().cpu().item()
        return get_fixed_range_quanta(maxabs, self.act_bw.bitwidth)

def get_fixed_range_quanta(maxabs: float, bits: int) -> int:
    """
    Returns optimal quanta to quantize a tensor over the range [-maxabs, +maxabs]
    with a given number of bits
    """
    if maxabs == 0:
        return 0
    else:
        return math.ceil(math.log2(maxabs) - bits + 1)

@torch.jit.ignore
def fixed_range_fake_quantize(x: Tensor, quanta: int, bits: int, quantize: bool, rounded: bool=False) -> Tensor:
    """
    If quantize = True, simulates quantization on given tensor.
    If quantize = False, saturates the tensor (but no rounding error)
    """
    if quantize:
        return fake_quantize(x, quanta, bits, rounded=rounded)
    else:
        lims = (-2**(bits + quanta -1), (2**(bits-1) - 1) * 2**quanta) 
        return x.clamp(*lims)

@torch.jit.script
def sigsigtanhsig(x: Tensor) -> Tensor:
    """
    Fused operator for sigmoid(x[:H]), sigmoid(x[H:2H]), tanh(x[2H:3H]), sigmoid(x[3H:4H]).
    """
    H = x.shape[-1] // 4
    dev = x.device

    is_tanh = torch.zeros(4*H, device=dev)
    is_tanh[2*H:3*H] = 1
    sig1_tanh2 = is_tanh + 1

    sig = torch.sigmoid(x*sig1_tanh2)
    return sig*sig1_tanh2 - is_tanh

@torch.jit.script
def lstm_pointwise(x: Tensor, c_prev: Tensor, b_act: int, b_addr: int, q_sig_addr: int, 
    q_tanh_addr: int, q_unity: int, q_c: int, quantize: bool=False, 
    interpolate: bool=False) -> Tuple[Tensor, Tensor]:
    """
    Fused operator for sigmoid(x[:H]), sigmoid(x[H:2H]), tanh(x[2H:3H]), sigmoid(x[3H:4H]).

    Args:
        x (Tensor): stacked i, f, g, o inputs, shape (*, 4H)
        b_act (int): activation bitwidth
        b_addr (int): LUT address bitwidth
        quantize (bool): if True, will quantize the output
    """
    H = x.shape[-1] // 4

    # OPTIONAL: INTERPOLATE
    if interpolate:
        y = fixed_range_fake_quantize(sigsigtanhsig(x), q_unity, b_act, quantize, True)
    else: # SIMULATE int8 LUT with floor op
        # QUANTIZE LUT INPUTS
        x_if, x_g, x_o = torch.split(x, [2*H, H, H], -1)
        x_if_q = fixed_range_fake_quantize(x_if, q_sig_addr, b_addr, quantize, False)
        x_g_q = fixed_range_fake_quantize(x_g, q_tanh_addr, b_addr, quantize, False)
        x_o_q = fixed_range_fake_quantize(x_o, q_sig_addr, b_addr, quantize, False)
        x_floor = torch.cat([x_if_q, x_g_q, x_o_q], -1)

        # APPLY NONLINEARITIES
        y_floor = sigsigtanhsig(x_floor)
        y = fixed_range_fake_quantize(y_floor, q_unity, b_act, quantize, True)

    i, f, g, o = y.chunk(4, -1)

    # COMPUTE c_next = f*c_prev + i*g
    ig_prod = fixed_range_fake_quantize(i*g, q_c, b_act, quantize, False)
    fc_prod = fixed_range_fake_quantize(f*c_prev, q_c, b_act, quantize, False)
    c = fixed_range_fake_quantize(ig_prod + fc_prod, q_c, b_act, quantize, False)

    # COMPUTE h = o * tanh(c)
    
    # OPTIONAL: INTERPOLATE
    if interpolate:
        h = fixed_range_fake_quantize(torch.tanh(c), q_unity, b_act, quantize, True)
    else:
        h_addr_floor = fixed_range_fake_quantize(c, q_tanh_addr, b_addr, quantize, False)
        h_floor = torch.tanh(h_addr_floor)
        h = fixed_range_fake_quantize(h_floor, q_unity, b_act, quantize, True)
    h_gated = fixed_range_fake_quantize(h * o, q_unity, b_act, quantize, True)

    return h_gated, c

@torch.jit.script
def lstm_step(
    x_t: Tensor, h_prev: Tensor, c_prev: Tensor, 
    weight_ih: Tensor, weight_hh: Tensor, 
    bias_ih: Optional[Tensor]=None, bias_hh: Optional[Tensor]=None,
    b_act: int=16, b_addr: int=8, q_sig_addr: int=-4, q_tanh_addr: int=-5, 
    q_unity: int=-15, q_mm_ih: int=-13, q_mm_hh: int=-13, q_c: int=-13, 
    quantize: bool=False, interpolate: bool=False) -> Tuple[Tuple[Tensor, Tensor], Tuple[Tensor, Tensor, Tensor]]:

    y_ih = F.linear(x_t, weight_ih, bias_ih)
    ih_maxabs = torch.max(torch.abs(y_ih.detach()))
    y_ih = fixed_range_fake_quantize(y_ih, q_mm_ih, b_act, quantize, False)
    
    y_hh = F.linear(h_prev, weight_hh, bias_hh)
    hh_maxabs = torch.max(torch.abs(y_hh.detach()))
    y_hh = fixed_range_fake_quantize(y_hh, q_mm_hh, b_act, quantize, False)
    
    y_t = fixed_range_fake_quantize(y_ih + y_hh, max(q_mm_ih, q_mm_hh), b_act, quantize, False)
    h, c = lstm_pointwise(y_t,
        c_prev=c_prev, b_act=b_act, b_addr=b_addr,
        q_sig_addr=q_sig_addr, q_tanh_addr=q_tanh_addr,
        q_unity=q_unity, q_c=q_c, quantize=quantize, interpolate=interpolate)
    
    cell_maxabs = torch.max(torch.abs(c.detach()))
    return (h, c), (ih_maxabs, hh_maxabs, cell_maxabs)
    

class LSTM(AtomicModule):
    """
    WARNING: will not be able to modify precision!
    """
    def __init__(self, parent: torch.nn.LSTM, config: LSTMConfig):

        assert not parent.bidirectional
        assert parent.batch_first

        self.hidden_size = parent.hidden_size
        self.input_size = parent.input_size
        self.num_layers = parent.num_layers
        self.batch_first = parent.batch_first
        self.bias = parent.bias
        self.observe = False

        super().__init__()
        self.config: LSTMConfig = config
        self.quantize = config.force_quantize

        dev = parent.weight_ih_l0.device

        self.register_buffer('input_maxabs', torch.zeros(1, device=dev))

        for i in range(parent.num_layers):
            self.register_buffer(f'mm_ih_maxabs_l{i}', torch.zeros(1, device=dev))
            self.register_buffer(f'mm_hh_maxabs_l{i}', torch.zeros(1, device=dev))
            self.register_buffer(f'cell_maxabs_l{i}',  torch.zeros(1, device=dev))
        
        self.param_quantizers = torch.nn.ModuleDict()
        for (name, param) in parent.named_parameters():
            if param.ndim == 2:
                bw = self.config.param_bw
            else:
                bw = self.config.act_bw
            pq = ParameterQuantizer(bitwidth=bw, observer=DEFAULT_OBSERVERS['lstm'])
            pq.quantize = self.quantize
            pq.observe = self.quantize
            self.param_quantizers[name] = pq
            self.register_parameter(name, param)


    def get_weights(self, layer_idx: int) -> Dict[str, Tensor]:
        keys = ['weight_ih', 'weight_hh', 'bias_ih', 'bias_hh']
        output: Dict[str, Tensor] = {}
        for k in keys:
            name = f'{k}_l{layer_idx}'
            if name in self.param_quantizers:
                quantizer: ParameterQuantizer = self.param_quantizers[name]
                param: Tensor = getattr(self, name)
                output[k] = quantizer(param)
                if not hasattr(output[k], 'quanta'):
                    print('Warning: no quanta')
            else:
                output[k] = None
        return output

    def get_quant_config(self, idx: int) -> dict:
        
        b_act=self.config.act_bw.bitwidth
        def get_quanta_from_maxabs(name, minabs):
            maxabs = getattr(self, name).detach().cpu().item()
            maxabs = max(maxabs, minabs)
            q = int(math.floor(math.log2(maxabs))) - b_act + 1
            return q

        if CALIBRATE_CELL:
            q_c = get_quanta_from_maxabs(f'cell_maxabs_l{idx}', 4)
        else:
            q_c = self.config.cell_quanta
                
        if CALIBRATE_MM:
            q_mm_ih = get_quanta_from_maxabs(f'mm_ih_maxabs_l{idx}', 16)
            q_mm_hh = get_quanta_from_maxabs(f'mm_hh_maxabs_l{idx}', 16)
        else:
            q_mm_ih = self.config.matmul_quanta
            q_mm_hh = self.config.matmul_quanta

        return dict(
            b_act=b_act,
            b_addr=self.config.lut_bw.bitwidth,
            q_sig_addr=self.config.sigmoid_addr_quanta,
            q_tanh_addr=self.config.tanh_addr_quanta,
            q_unity=self.config.unity_quanta,
            q_mm_ih=q_mm_ih,
            q_mm_hh=q_mm_hh,
            q_c=q_c,
            interpolate=CONFIG.lstm_interpolate
        )

    @torch.no_grad()
    def quantize_input(self, x: Tensor, quantize: bool=False) -> Tensor:
        x_maxabs = x.abs().max()
        if self.input_maxabs == 0:
            self.input_maxabs = x_maxabs
        else:
            if MOV_AVG_CALIBRATION:
                self.input_maxabs = self.input_maxabs * self.config.alpha + (1 - self.config.alpha) * x_maxabs
            else:
                self.input_maxabs = torch.max(self.input_maxabs, x_maxabs)
        q_input = self.config.act_quanta(self.input_maxabs)
        if quantize:
            return fixed_range_fake_quantize(x, q_input, self.config.act_bw.bitwidth, True, False)
        else:
            return x

    def run_layer(self, idx: int, x: Tensor, h: Optional[Tensor]=None, c: Optional[Tensor]=None,
        quantize: bool=False):
        """
        Runs layer at index `idx`. If in training mode, will also update cell state statistics.

        Args:
            idx (int): layer index
            x (Tensor): input sequence
            h (Tensor, optional): initial hidden state
            c (Tensor, optional): initial cell state
            quantize (bool): whether to fake-quantize during execution

        Returns:
            y, (h_f, c_f)
            y (Tensor): output sequence
            h_f (Tensor): final hidden state
            c_f (Tensor): final cell state
        """
        # quantize input to first LSTM layer
        if idx == 0:
            if not hasattr(x, 'quanta'):
                x = self.quantize_input(x, quantize=quantize)

        # initialize hidden state
        H = self.hidden_size
        if h is None:
            h = torch.zeros(H, device=x.device)
        if c is None:
            c = torch.zeros(H, device=x.device)
        
        # get quantized params, quant config
        kwargs = self.get_weights(idx)
        kwargs.update(self.get_quant_config(idx))

        ih_maxabs = torch.zeros(1, device=x.device)
        hh_maxabs = torch.zeros(1, device=x.device)
        cell_maxabs = torch.zeros(1, device=x.device)

        outputs = []
        for x_t in x.unbind(1):
            (h, c), (ih_t, hh_t, cell_t) = lstm_step(x_t=x_t, h_prev=h, c_prev=c,
                quantize=quantize, **kwargs)
            outputs.append(h)
            ih_maxabs = torch.maximum(ih_t, ih_maxabs)
            hh_maxabs = torch.maximum(hh_t, hh_maxabs)
            cell_maxabs = torch.maximum(cell_t, cell_maxabs)
        outputs = torch.stack(outputs, dim=1)

        # update cell, ih, hh maxabs:
        for name, val in zip(['mm_hh_maxabs', 'mm_ih_maxabs', 'cell_maxabs'], [hh_maxabs, ih_maxabs, cell_maxabs]):
            name = f'{name}_l{idx}'
            prev = getattr(self, name)
            if MOV_AVG_CALIBRATION:
                new = prev * self.config.alpha + (1 - self.config.alpha) * val
            else:
                new = torch.max(prev, val)
            setattr(self, f'{name}_l{idx}', new)        

        return outputs, (c, h)

    def forward(self, x: Tensor, h_c: Tuple[Tensor, Tensor]=None) -> Tuple[Tensor, Tuple[Tensor, Tensor]]:
        num_layers = self.num_layers
        if h_c is None:
            h, c = None, None
        else:
            h, c = h_c

        dims = None
        quantize = self.quantize or self.observe

        if hasattr(x, 'dimensions'):
            dims = x.dimensions

        if x.ndim == 3:

            if h is not None:
                h = h.split(num_layers, -1)
            else:
                h = [None]*num_layers
            if c is not None:
                c = c.split(num_layers, -1)
            else:
                c = [None]*num_layers

            h_f, c_f = [], []
            
            if not quantize:
                x, (h_f, c_f) = self.to_lstm()(x, h_c)
            else:
                for i in range(num_layers):
                    x, (h_l, c_l) = self.run_layer(i, x, h[i], c[i], quantize=quantize)
                    h_f.append(h_l)
                    c_f.append(c_l)
                h_f = torch.cat(h_f, -1)
                c_f = torch.cat(c_f, -1)
        
        else:
            B = x.shape[0]
            dev = x.device
            x = torch.ones(B, self.hidden_size, device=dev)
            h_f = torch.ones(B, self.num_layers * self.hidden_size, device=dev)
            c_f = torch.ones(B, self.num_layers * self.hidden_size, device=dev)

        dev = x.device

        x_q = self.config.unity_quanta
        h_q = self.config.unity_quanta
        c_q = self.get_quant_config(self.num_layers - 1)['q_c']

        x_q, h_q, c_q = map(lambda x: torch.tensor(x, device=dev, dtype=torch.float32), (x_q, h_q, c_q))

        x = annotate(x, self.config.act_bw, quanta=x_q, 
            quantized=quantize, dimensions=dims)
        h_f = annotate(h_f, self.config.act_bw, quanta=h_q, 
            quantized=quantize, dimensions=['B', 'F'])
        c_f = annotate(c_f, self.config.act_bw, 
            quanta=c_q, 
            quantized=quantize, dimensions=['B', 'F'])

        return x, (h_f, c_f)

    @classmethod
    def from_lstm(cls, parent, config=None):
        masks = get_masks(parent)
        remove_pruning(parent)
        if config is None:
            config = LSTMConfig()
        flstm = cls(parent, config=config)
        flstm = apply_masks(flstm, masks)
        parent = apply_masks(parent, masks)
        return flstm

    def to_lstm(self) -> torch.nn.LSTM:
        masks = get_masks(self)
        lstm = torch.nn.LSTM(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            batch_first=self.batch_first,
            num_layers=self.num_layers,
            bias=self.bias)
        dev = self.weight_ih_l0.device
        lstm.to(dev)
        names = ['weight_ih_l', 'weight_hh_l'] 
        if self.bias:
            names += ['bias_ih_l', 'bias_hh_l']
        for l in range(self.num_layers):
            for n in names:
                n = f'{n}{l}'
                setattr(lstm, n, torch.nn.Parameter(getattr(self, n)))
        lstm = apply_masks(lstm, masks)
        return lstm

    @classmethod
    def _from_float(cls, parent: torch.nn.LSTM, bw_conf: BitwidthConfig, interpolate: bool,
        **kwargs):
        config = LSTMConfig(
            tanh_limit=4,
            sigmoid_limit=8,
            cell_limit=16,
            alpha=0.95,
            act_bw=bw_conf.activations,
            lut_bw=bw_conf.lut,
            param_bw=bw_conf.weights,
            force_quantize=False)
        return cls(parent, config)
    
    def get_table(self, fn: Callable[[Tensor], Tensor], 
        addr_bits: int, addr_quanta: int, out_bits: int, out_quanta: int):
        levels = 2**addr_bits
        min_int = -2**(addr_bits-1)
        max_int = 2**(addr_bits-1) - 1
        scale = 2**addr_quanta
        x_float = torch.linspace(min_int*scale, max_int*scale, levels)
        y_float = fixed_range_fake_quantize(fn(x_float), out_quanta, out_bits, 
            quantize=True, rounded=True)
        y_int = (y_float/(2**out_quanta)).numpy().astype(int)
        x_int = np.arange(start=min_int, stop=max_int+1, step=1)
        return Table(x_int, y_int, fn.__name__)

    def get_tables(self):
        """
        Returns sigmoid and tanh Tables
        """
        sigmoid = self.get_table(
            fn=torch.sigmoid, 
            addr_bits=self.config.lut_bw.bitwidth, 
            addr_quanta=self.config.sigmoid_addr_quanta,
            out_bits=self.config.act_bw.bitwidth,
            out_quanta=self.config.unity_quanta)
        tanh = self.get_table(
            fn=torch.tanh, 
            addr_bits=self.config.lut_bw.bitwidth, 
            addr_quanta=self.config.tanh_addr_quanta,
            out_bits=self.config.act_bw.bitwidth,
            out_quanta=self.config.unity_quanta)
        return sigmoid, tanh

    def _get_constants(self, x, h=None, c=None) -> dict:
        
        assert h is None, 'Cannot handle initial hidden state yet for LSTM'
        assert c is None, 'Cannot handle initial cell state yet for LSTM'

        sigmoid, tanh = self.get_tables()
        constants = dict(
            num_layers=self.num_layers,
            batch_first=self.batch_first,
            sigmoid=sigmoid,
            tanh=tanh,
            input_size=self.input_size,
            hidden_size=self.hidden_size
        )
        layers = []
        for idx in range(self.num_layers):
            layer_conf = self.get_quant_config(idx)
            weights = self.get_weights(idx)
            layer_conf.update(weights)
            for name, w in weights.items():
                if w is not None:
                    assert hasattr(w, 'quanta')
                    layer_conf[f'{name}_quanta'] = w.quanta
                    layer_conf[f'{name}_int'] = asint(w).numpy()
                else:
                    layer_conf[f'{name}_quanta'] = None
                    layer_conf[f'{name}_int'] = None
            layers.append(layer_conf)
        constants['layers'] = layers
        return constants