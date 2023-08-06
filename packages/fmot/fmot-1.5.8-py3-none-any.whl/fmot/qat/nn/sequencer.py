import torch
from torch import nn
from . import quantizers, atomics
from ..annotated_tensors import set_dim_annotations
from functools import partial

class StateInitializer(nn.Module):
    def __init__(self, state_shapes, bitwidth, batch_dim,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.state_shapes = state_shapes
        self.batch_dim = batch_dim
        self.quantizers = nn.ModuleList()
        self.requantizers = nn.ModuleList()
        self.q_groups = []
        for __ in range(len(state_shapes)):
            quant = quantizers.StateQuantizer(bitwidth, observer=observer)
            requant = atomics.Requantize(bitwidth, observer=observer)
            quantizers.share_observer(quant, requant)
            self.quantizers.append(quant)
            self.requantizers.append(requant)
            quant_group = quantizers.PrecisionConstraint()
            quant_group.add(quant)
            quant_group.add(requant.quantizer)
            self.q_groups.append(quant_group)

    def forward(self, x):
        B = x.shape[self.batch_dim]
        state = [torch.zeros(B, *shape, device=x.device) for shape in self.state_shapes]
        for y in state:
            set_dim_annotations(['B', *['F' for _ in range(len(self.state_shapes[0]))]], y)
        return [l(y) for l, y in zip(self.quantizers, state)]

    def observe_state(self, state):
        for l, x in zip(self.quantizers, state):
            l.update_statistics(x)

    def quantize_state(self, state):
        outputs = []
        for l, x in zip(self.requantizers, state):
            outputs.append(l(x))
        return outputs

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        observer = partial(observer, **kwargs)
        return cls(state_shapes=parent.state_shapes, bitwidth=bw_conf.activations,
                   batch_dim=parent.batch_dim, observer=observer)
