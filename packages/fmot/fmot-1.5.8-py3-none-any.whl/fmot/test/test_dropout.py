import torch
from torch import nn
import fmot
from fmot import qat as Q

def test_dropout():
    class Net(nn.Module):
        def __init__(self, input_size, hidden_size):
            super().__init__()
            self.linear = nn.Linear(input_size, hidden_size)
            self.dropout = nn.Dropout(0.5, inplace=False)

        def forward(self, x):
            z = self.linear(x)
            z = self.dropout(z)
            return z

    input_size = 8
    hidden_size = 4
    batch_size = 5
    time_steps = 10

    model = Net(input_size, hidden_size)
    qmodel = fmot.convert.convert_torch_to_qat(model)
    inputs = [torch.randn(batch_size, time_steps, input_size) for __ in range(5)]
    qmodel = Q.control.quantize(qmodel, inputs)

    fqir_graph = fmot.tracing.tracing.trace_sequential_model(
        qmodel, torch.randn(batch_size, time_steps, input_size), batch_dim=0, seq_dim=1)
    assert(True)

if __name__ == "__main__":
    test_dropout()
