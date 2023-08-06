from functools import partial
import torch
from .quantizers import DEFAULT_OBSERVERS, Quantizer
from ..annotated_tensors import tag_dim
# from fmot.utils import reset_counters

class QuantCollection(torch.nn.Module):
    def __init__(self, bitwidth, observer=DEFAULT_OBSERVERS['default'], **kwargs):
        super().__init__()
        self.quantizers = torch.nn.ModuleList()
        self.bitwidth = bitwidth
        self.obs_class = partial(observer, **kwargs)

    def forward(self, *args):
        new_args = []
        for i, arg in enumerate(args):
            if (i+1) > len(self.quantizers):
                self.add_quantizer()
            arg = self.quantizers[i](arg)
            new_args.append(arg)
        return new_args

    def add_quantizer(self):
        self.quantizers.append(Quantizer(self.bitwidth, observer=self.obs_class))

class QuantWrapper(torch.nn.Module):
    def __init__(self, model, bitwidth, observer=DEFAULT_OBSERVERS['default'],
                 dimensions=None, **kwargs):
        super().__init__()
        self.quantizers = QuantCollection(bitwidth, observer=observer, **kwargs)
        self.bitwidth = bitwidth
        self.model = model
        self.dimensions = dimensions

    @tag_dim
    # @reset_counters
    def forward(self, *args):
        args = self.quantizers(*args)
        return self.model(*args)
