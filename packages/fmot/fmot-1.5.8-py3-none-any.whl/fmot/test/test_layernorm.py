import torch
import fmot
import numpy as np

def test_layernorm():
    model = torch.nn.LayerNorm(64)
    cmodel = fmot.ConvertedModel(model)
    cmodel.quantize([torch.randn(8, 64) for _ in range(4)])
    graph = cmodel.trace()

    x = torch.randn(1, 64)
    y0 = cmodel(x).detach().numpy()[0]

    y1 = graph.run(x.numpy()[0], dequant=True)

    assert np.array_equal(y0, y1)