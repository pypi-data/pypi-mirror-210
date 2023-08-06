import unittest
import torch
import fmot
from fmot import qat as Q

class TestCuda(unittest.TestCase):
    def test_to_cuda(self):
        """ Checks if tracing can be done with a model
            sent on a GPU. Gets automatically validated
            if we can't run the test on GPUs.
        """
        if not torch.cuda.is_available():
            assert True
        else:
            device = 'cuda'
            model = torch.nn.GRU(3, 4)

            qmodel = fmot.convert.convert_torch_to_qat(model).to(device)
            inputs = [torch.randn(1, 3, 2).to(device) for __ in range(2)]
            qmodel = Q.control.quantize(qmodel, inputs, dimensions=['B', 'F', 'T'])

            fqir_graph = fmot.tracing.tracing.trace_sequential_model(qmodel, torch.randn(1, 3, 2).to(device), batch_dim=0,
                                                                  seq_dim=-1)
            assert (True)
            print("Cuda test0 terminated !")

            class Net(torch.nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lin = torch.nn.Linear(3, 3)

                def forward(self, x):
                    y = self.lin(x)
                    y2 = torch.sigmoid(y)
                    return y2

            model = Net()
            inputs = [torch.randn(1, 3).to(device) for __ in range(2)]
            qmodel = fmot.convert.convert_torch_to_qat(model).to(device)
            qmodel = Q.control.quantize(qmodel, inputs, dimensions=['B', 'F', 'F'])
            fqir_graph = fmot.tracing.tracing.trace_feedforward_model(qmodel, torch.randn(1, 3).to(device), batch_dim=0)
            print("Cuda test1 terminated !")