import torch
from torch import nn

from fmot.utils.quant_tools.diagnosis import get_diagnosis
from fmot import ConvertedModel


class LinNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(128, 64)

    def forward(self, x):
        y = self.lin(x)

        return y


class RnnNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.LSTM(128, 64, batch_first=True)

    def forward(self, x):
        y, _ = self.layer(x)

        return y


def test_qact_diagnosis():
    model = RnnNet()

    cmodel = ConvertedModel(model, batch_dim=0, seq_dim=1)
    quant_inputs = [torch.randn(5, 10, 128) for _ in range(3)]

    cmodel.quantize(quant_inputs)

    sample_input = quant_inputs[0]
    get_diagnosis(model, cmodel, sample_input, plot=False)


def test_layer_diagnosis():
    model = LinNet()

    cmodel = ConvertedModel(model)
    quant_inputs = [torch.randn(5, 128) for _ in range(3)]

    cmodel.quantize(quant_inputs)

    sample_input = quant_inputs[0]
    get_diagnosis(model, cmodel, sample_input, to_register={'lin'}, kind='output', plot=False)
