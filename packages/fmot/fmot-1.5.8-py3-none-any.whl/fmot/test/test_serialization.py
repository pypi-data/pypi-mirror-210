import unittest
import torch
import os
from torch import nn

import fmot
from fmot import ConvertedModel

class TestSerialization(unittest.TestCase):

    def test_save_load_feedforward(self):
        r''' Tests if saving and loading models works correctly
        '''
        model = nn.Linear(3, 4)
        cmodel = ConvertedModel(model, batch_dim=0)
        fmot.save(cmodel, 'test_save_model.pth')

        loaded_model = fmot.load('test_save_model.pth')
        for p_name, param in cmodel.named_parameters():
            assert(abs(param - fmot.utils.rgetattr(loaded_model, p_name)).sum() == 0.)

        os.remove('test_save_model.pth')


    def test_save_load_state_dict(self):
        r''' Tests if saving and loading through state_dict works correctly
        '''
        model_orig = nn.Linear(3, 4)
        cmodel_orig = ConvertedModel(model_orig, batch_dim=0)
        fmot.save(cmodel_orig.state_dict(), 'test_save_state_dict.pth')

        # Load the saved state dict
        pretrained_dict = fmot.load('test_save_state_dict.pth')

        # Initialize a new random model
        model = nn.Linear(3, 4)
        cmodel = ConvertedModel(model, batch_dim=0)
        cmodel = fmot.load_state_dict(cmodel, pretrained_dict)
        for p_name, param in cmodel_orig.named_parameters():
            assert(abs(param - fmot.utils.rgetattr(cmodel, p_name)).sum() == 0.)

        os.remove('test_save_state_dict.pth')


    def test_mismatch(self):
        r''' Tests that an error is raised the cmodel is not quantized, but the state_dict comes from
             a quantized model, an error is raised.
        '''
        model_orig = nn.Linear(3, 4)
        cmodel_orig = ConvertedModel(model_orig, batch_dim=0)
        quant_inputs = [torch.randn(1, 3) for _ in range(2)]
        cmodel_orig.quantize(quant_inputs)
        pretrained_dict = cmodel_orig.state_dict()

        cmodel = ConvertedModel(model_orig, batch_dim=0)
        self.assertRaises(Exception, fmot.load_state_dict, cmodel, pretrained_dict)

    def test_tuneps(self):
        r''' Tests that TuningEpsilon running max appears in the state dict
        '''
        tuneps = fmot.nn.TuningEpsilon(eps=0.25)
        input = torch.tensor([8, 8, 8])
        with torch.no_grad():
            _ = tuneps(input)
        assert('running_max' in tuneps.state_dict().keys())
        assert(tuneps.epsilon() == 2.)
