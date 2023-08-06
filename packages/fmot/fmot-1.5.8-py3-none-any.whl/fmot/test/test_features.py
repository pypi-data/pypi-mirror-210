import unittest
import torch
from torch import nn
import fmot
from fmot import ConvertedModel
from fmot.utils import rsetattr, rgetattr

# We need to import these for explicit type annotations
from typing import List, Tuple
from torch import Tensor

from fmot.nn import RNNCell, LSTMCell, GRUCell, RNN, LSTM, GRU, MultiLayerRNN, Sequential
from fmot.nn.conv1d import TemporalConv1d, SequencedTemporalConv1d
from fmot.nn import map_param_name, get_trailing_number
from fmot.nn import default_torch2seq_param_mapping
from fmot.nn import BasicRNN, SuperBasic
from fmot.nn.conv1d import TemporalConv1d
from fmot.nn import rgetattr
from fmot.convert.optimizer import inherit_optimizer
from fmot import qat as Q
from fmot import ConvertedModel
from fmot.convert import generate_param2quantizer
import torch.nn.utils.prune as prune

# def check_sync(cmodel, orig_model):
#     orig_dict = dict()
#     for name, param in orig_model.named_parameters():
#         orig_dict[name] = param*1.

#     for name, param in cmodel.named_parameters():
#         new_param = torch.nn.Parameter(param*2)
#         rsetattr(cmodel, name, new_param)

#     synchronize(orig_model, cmodel)

#     for name, param in orig_model.named_parameters():
#         new_orig_param = rgetattr(orig_model, name)
#         assert(torch.sum(orig_dict[name]*2 - new_orig_param) < 1e-5)

class TestFeatures(unittest.TestCase):
    def test_substitutions_dict(self):
        """ Check that the subsitutions dict allows
            to access quant model params as expected
        """
        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.tcn = TemporalConv1d(8, 6, 4) #output: B*6
                self.linear = nn.Linear(6, 3)

            def forward(self, x):
                y = self.tcn(x)
                y = torch.transpose(y, 1, 2)
                output = self.linear(y)

                return output

        model = Net()
        batch_size = 5
        timesteps = 10
        n_features = 8

        qmodel = fmot.convert.convert_torch_to_qat(model)
        inputs = [torch.randn(batch_size, n_features, timesteps) for _ in range(5)]
        qmodel = Q.control.quantize(qmodel, inputs, dimensions = ['B', 'F', 'T'])

        for name, param in model.named_parameters():
            if name in qmodel.substitutions_dict:
                children_dict, F_inv = qmodel.substitutions_dict[name]
                for new_pname in children_dict:
                    param = rgetattr(qmodel, new_pname)

        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.lin = nn.Linear(8, 6)
                self.rnn = torch.nn.RNN(6,4, batch_first=True)
                self.gru = torch.nn.GRU(4,4, batch_first=True)
                self.lstm = torch.nn.LSTM(4,4, batch_first=True)

            def forward(self, x):
                y = self.lin(x)
                y, _ = self.rnn(y)
                y, _ = self.gru(y)
                y, _ = self.lstm(y)

                return y

        model = Net()
        batch_size = 5
        timesteps = 10
        n_features = 8

        qmodel = fmot.convert.convert_torch_to_qat(model)
        inputs = [torch.randn(batch_size, timesteps, n_features) for _ in range(5)]
        qmodel = Q.control.quantize(qmodel, inputs, dimensions = ['B', 'T', 'F'])

        for name, param in model.named_parameters():
            if name in qmodel.substitutions_dict:
                children_dict, F_inv = qmodel.substitutions_dict[name]
                for new_pname in children_dict:
                    param = rgetattr(qmodel, new_pname)

        assert(True)

    def test_optimizer_inheritance_rnn(self):
        """ Check that the optimizer inheritance is working
            and that we can resume training after inheriting it
        """
        # N is batch size; D_in is input dimension;
        # H is hidden dimension; D_out is output dimension.
        N, D_in, H, D_out = 5, 8, 3, 3
        timesteps = 10

        # Create random Tensors to hold inputs and outputs
        x = torch.randn(N, timesteps, D_in)
        y = torch.randn(N, timesteps, D_out)

        loss_fn = torch.nn.MSELoss(reduction='sum')
        learning_rate = 1e-4

        model = torch.nn.RNN(D_in, H)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        y_pred, _ = model(x)
        loss = loss_fn(y_pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        qmodel = fmot.convert.convert_torch_to_qat(model)
        new_optimizer = inherit_optimizer(optimizer, model, qmodel)

        inputs = [torch.randn(N, timesteps, D_in) for _ in range(5)]
        qmodel = Q.control.quantize(qmodel, inputs, dimensions=['B', 'T', 'F'])


        for t in range(30):
            x.dimensions = ['B', 'T', 'F']
            y_pred, _ = qmodel(x)

            # Compute and print loss.
            loss = loss_fn(y_pred, y)
            if t % 10 == 9:
                print(t, loss.item())
            new_optimizer.zero_grad()
            loss.backward()
            new_optimizer.step()

        assert(True)

    # def test_optimizer_inheritance_tcn(self):
    #     """ Check that the optimizer inheritance is working
    #         on TCN
    #     """
    #     loss_fn = torch.nn.MSELoss(reduction='sum')
    #     learning_rate = 1e-4

    #     in_channels = 8
    #     out_channels = 5
    #     kernel_size = 3

    #     batch_size = 5
    #     time_steps = 10

    #     model = TemporalConv1d(in_channels, out_channels, kernel_size)

    #     qmodel = fmot.convert.convert_torch_to_qat(model)
    #     inputs = [torch.randn(batch_size, in_channels, time_steps) for __ in range(5)]
    #     qmodel = Q.control.quantize(qmodel, inputs, dimensions = ['B', 'F', 'T'])

    #     # Create random Tensors to hold inputs and outputs
    #     x = torch.randn(batch_size, in_channels, time_steps)
    #     y = torch.randn(batch_size, out_channels, time_steps)

    #     optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    #     y_pred = model(x)
    #     loss = loss_fn(y_pred, y)
    #     optimizer.zero_grad()
    #     loss.backward()
    #     optimizer.step()

    #     new_optimizer = inherit_optimizer(optimizer, model, qmodel)

    #     for t in range(30):
    #         x.dimensions = ['B', 'F', 'T']
    #         y_pred = qmodel(x)

    #         loss = loss_fn(y_pred, y)
    #         if t % 10 == 9:
    #             print(t, loss.item())

    #         new_optimizer.zero_grad()
    #         loss.backward()
    #         new_optimizer.step()

    #     assert(True)

    def test_converter_check(self):
        """ Check that the errors are correclty raised when
            we convert sequential models without feeding
            a seq_dim to the converter
        """
        model = torch.nn.Sequential(TemporalConv1d(4,4,4), torch.nn.Linear(4, 4))
        with self.assertRaises(Exception):
            ConvertedModel(model, batch_dim=0, seq_dim=None)
        ConvertedModel(model, batch_dim=0, seq_dim=1)
        assert(True)

        model = torch.nn.Sequential(model, torch.nn.Linear(4, 4))
        with self.assertRaises(Exception):
            ConvertedModel(model, batch_dim=0, seq_dim=None)

        ConvertedModel(model, batch_dim=0, seq_dim=1)
        assert(True)

        model = torch.nn.Linear(4, 4)
        ConvertedModel(model, batch_dim=0, seq_dim=None)
        assert(True)

    # def test_weight_sync(self):
    #     ''' Test weight synchronization on a simple module without
    #         substitutions
    #     '''
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(), 
    #         torch.nn.Linear(32, 64), 
    #         torch.nn.ReLU(), 
    #         torch.nn.Linear(64, 32))
    #     inputs = [torch.randn(32, 32) for __ in range(10)]
    #     cmodel = fmot.ConvertedModel(model, precision='double', batch_dim=0,
    #         interpolate=False)
    #     cmodel.quantize(inputs)
        
    #     check_sync(cmodel, model)
        
    # def test_weight_sync_rnn(self):
    #     ''' Test weight synchronization on a simple module with RNN
    #         subsitutions, no split, F_inv = None
    #     '''
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(), 
    #         torch.nn.RNN(32, 64, batch_first=True), )
    #     inputs = [torch.randn(1, 32, 32) for __ in range(10)]
    #     converter = fmot.ConvertedModel(model, precision='double', seq_dim=1, batch_dim=0,
    #         interpolate=False)
    #     converter.quantize(inputs)
    
    #     check_sync(converter, model)
    
    # def test_weight_sync_conv(self):
    #     ''' Test weight synchronization on Conv layer with group =2,
    #         testing that one-to-many param split works
    #     '''
    #     conv_model = fmot.nn.TemporalConv1d(8, 4, 3, groups=2)
    #     inputs = [torch.randn(1, 8, 5) for __ in range(10)]
    #     cmodel = fmot.ConvertedModel(conv_model, precision='double', seq_dim=2, batch_dim=0,
    #         interpolate=False)
    #     cmodel.quantize(inputs)
        
    #     check_sync(cmodel, conv_model)

    # def test_weight_sync_dwconv(self):
    #     ''' Tests weight synchronization on DWConv1d
    #     '''
    #     import numpy as np
    #     conv_model = fmot.nn.TemporalConv1d(8, 16, 3, groups=8, bias=False)
    #     w = torch.nn.Parameter((torch.tensor(np.arange(16*3))*1.).reshape(16, 1, 3))
    #     conv_model.conv.weight = w
    #     inputs = [torch.randn(1, 8, 5) for __ in range(10)]
    #     cmodel = fmot.ConvertedModel(conv_model, precision='double', seq_dim=2, batch_dim=0,
    #         interpolate=False)
    #     cmodel.quantize(inputs)
        
    #     check_sync(cmodel, conv_model)

    # def test_change_bitwidth(self):
    #     ''' Tests if we can switch precision as expected'''
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(),
    #         torch.nn.Linear(32, 64))
    #     inputs = [torch.randn(32, 32) for __ in range(10)]
    #     cmodel = fmot.ConvertedModel(model, precision='double', batch_dim=0,
    #                                          interpolate=False)
    #     cmodel.quantize(inputs)
    #
    #     new_qmodel = cmodel.modify_precision('standard', in_place=False)
    #     for name, param in new_qmodel.named_parameters():
    #         if len(param.shape) == 2:
    #             assert(str(param.bitwidth) == 'fqint4')
    #         else:
    #             assert(str(param.bitwidth) == 'fqint8')
    #
    #     inputs = [torch.randn(32, 32) for __ in range(10)]
    #     converter = fmot.ConvertedModel(model, precision='double', batch_dim=0,
    #                                          interpolate=False)
    #     with self.assertRaises(Exception):
    #         _ = converter.modify_precision('standard', in_place=False)

    def test_param2quant(self):
        model = torch.nn.Sequential(
            torch.nn.ReLU(),
            torch.nn.Linear(4, 2))
        inputs = [torch.randn(4, 4) for __ in range(10)]
        cmodel = ConvertedModel(model, precision='double', batch_dim=0,
                                interpolate=False)
        cmodel.quantize(inputs)
        _ = generate_param2quantizer(cmodel, inputs[0])

    # def test_parameter_table(self):
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(),
    #         torch.nn.Linear(4, 2))
    #     torch.manual_seed(0)
    #     inputs = [torch.randn(4, 4) for __ in range(10)]
    #     cmodel = ConvertedModel(model, precision='double', batch_dim=0,
    #                             interpolate=False)

    #     param_table = cmodel.get_parameter_table()
    #     for name, _ in cmodel.named_parameters():
    #         assert (param_table[name]['memory'] == 'N/A')
    #     cmodel.quantize(inputs)
    #     param_table = cmodel.get_parameter_table()
    #     assert (param_table['model.model.1.weight']['memory'] == 8.)

    # def test_set_param_precision(self):
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(),
    #         torch.nn.Linear(4, 2))
    #     inputs = [torch.randn(4, 4) for __ in range(10)]
    #     cmodel = ConvertedModel(model, precision='double', batch_dim=0,
    #                             interpolate=False)
    #     cmodel.quantize(inputs)

    #     cmodel.set_param_precision('model.model.1.weight', 'double')

    # def test_param2_quant_prunedmodel(self):
    #     ''' Tests if param2quant is working as expected on
    #         models for which a parameter has been pruned (as pruned
    #         parameters are regenerated on-the-fly by PyTorch)
    #     '''
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(),
    #         torch.nn.Linear(4, 2))
    #     inputs = [torch.randn(4, 4) for __ in range(10)]
    #     cmodel = ConvertedModel(model, precision='double', batch_dim=0,
    #                             interpolate=False)
    #     prune.l1_unstructured(cmodel.model.model[1], 'weight', 0.5)
    #     cmodel.quantize(inputs)
    #     cmodel.modify_precision('standard')
    #     assert (str(cmodel.param2quant['model.model.1.weight'].bitwidth) == 'fqint4')

    # def test_logic_param2quant(self):
    #     ''' Tests on a simple model if the Parameter to Quantizer
    #         utilities are working as expected.
    #     '''
    #     torch.manual_seed(0)
    #     model = torch.nn.Sequential(
    #         torch.nn.ReLU(),
    #         torch.nn.Linear(4, 2))
    #     inputs = [torch.randn(4, 4) for __ in range(10)]
    #     cmodel = ConvertedModel(model, precision='double', batch_dim=0,
    #                             interpolate=False)
    #     cmodel.quantize(inputs)
    #     table = cmodel.get_parameter_table()
    #     assert(table['model.model.1.weight']['density'] == 1.)
    #     assert(table['model.model.1.weight']['memory'] == 8 * 8 / 8) # nb_param * bitwidth / 8
    #     prune.l1_unstructured(cmodel.model.model[1], 'weight', 0.5)
    #     table = cmodel.get_parameter_table()
    #     assert(table['model.model.1.weight']['density'] == .5)
    #     assert(table['model.model.1.weight']['memory'] == 4.0)

    def test_tuneps_eval(self):
        """ Tests that TuningEpsilon running_mean only gets updated during training.
        """
        tuneps = fmot.nn.TuningEpsilon(eps=0.25)
        input = torch.tensor([8, 8, 8])
        _ = tuneps(input)
        assert(tuneps.epsilon() == 2.)
        tuneps.eval()
        _ = tuneps(torch.tensor([10, 10, 10]))
        assert (tuneps.epsilon() == 2.)


if __name__ == "__main__":
    test = TestFeatures()
    test.test_logic_param2quant()