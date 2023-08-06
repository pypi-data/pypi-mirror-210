import torch
from .. import torchscript_utils as utils
from fmot.functional import cos_arctan

class LUTConfig:
    r"""
    Lookup table configuration object.

    Container for lookup-table configuration for an elementwise nonlinearity (like sigmoid, tanh, etc.)

    Args:

        function: the callable elementwise nonlinearity

        limits (tuple[float]): Constraint on the input domain, of the form (minimum, maximum), to be used if 
            for saturating nonlinearities like sigmoid and tanh. Default is None.

        interpolate (bool): Whether to interpolate between lookup table elements when activations are 16bit.
            Default is True.

        telescope (bool): Whether to telescope when activations are 16bit. This means that the nonlinearity
            will be evaluated twice -- once for small-magnitude entries and once for large-magnitude entries.
            This is important for nonlinearities that have significant slope close to zero, like log
            and reciprocal. Default is False.

        add_identity (bool): True if :math:`f(a*b) = f(a) + f(b)`, for example :math:`f(x)=\log(x)`.

        mul_identity (bool): True if :math:`f(a*b) = f(a) * f(b)`, for example :math:`f(x)=x^N`.
    """
    def __init__(self, function, limits=None, interpolate=True, telescope=False, 
        add_identity=False, mul_identity=False):
        self.function = function
        self.limits = limits
        self.interpolate = interpolate
        self.telescope = telescope
        self.add_identity = add_identity
        self.mul_identity = mul_identity
        self.name = function.__name__

    def __repr__(self):
        return f'<{self.name} config>'

def get_fn_key(function):
    """
    Returns the patching key for a given callable function.

    Args:
        function: the callable elementwise nonlinearity
    Returns:
        A string key like 'aten::tanh' that will identify the function
            during the patching phase.
    """
    class Model(torch.nn.Module):
        def forward(self, x):
            return function(x)

    graph = torch.jit.script(Model()).graph
    nodes = list(graph.nodes())
    node = nodes[-1]

    if utils.isaten(node):
        key = node.kind()
    elif utils.isfunctional(node):
        key = utils.getfunctionalname(node)
    elif utils.isuserfunction(node):
        key = utils.getuserfuncname(node)
    else:
        raise Exception(f'Cannot convert node {node} into a patching key')

    return key

LUT_REGISTRY = {}

def register_lut(function, limits=None, interpolate=True, telescope=False, add_identity=False,
    mul_identity=False):
    r"""
    Register a new elementwise nonlinearity with optional settings.

    The function will be added to the LUT_REGISTRY dictionary.

    Args:

        function: the callable elementwise nonlinearity

        limits (tuple[float]): Constraint on the input domain, of the form (minimum, maximum), to be used if 
            for saturating nonlinearities like sigmoid and tanh. Default is None.

        interpolate (bool): Whether to interpolate between lookup table elements when activations are 16bit.
            Default is True.

        telescope (bool): Whether to telescope when activations are 16bit. This means that the nonlinearity
            will be evaluated twice -- once for small-magnitude entries and once for large-magnitude entries.
            This is important for nonlinearities that have significant slope close to zero, like log
            and reciprocal. Default is False.

        add_identity (bool): True if :math:`f(a*b) = f(a) + f(b)`, for example :math:`f(x)=\log(x)`.
        
        mul_identity (bool): True if :math:`f(a*b) = f(a) * f(b)`, for example :math:`f(x)=x^N`.
    """
    key = get_fn_key(function)
    config = LUTConfig(function, limits=limits, interpolate=interpolate, telescope=telescope,
        add_identity=add_identity, mul_identity=mul_identity)
    LUT_REGISTRY[key] = config

register_lut(torch.sigmoid, limits=(-8., 7.9375), interpolate=True)
register_lut(torch.tanh, limits=(-4., 3.96875), interpolate=True)
register_lut(torch.reciprocal, telescope=True, mul_identity=True)
register_lut(torch.sqrt, telescope=True, mul_identity=True)
register_lut(torch.rsqrt, telescope=True, mul_identity=True)
register_lut(torch.log, telescope=True, add_identity=True)
register_lut(torch.log2, telescope=True, add_identity=True)
register_lut(torch.log10, telescope=True, add_identity=True)
register_lut(torch.log1p, telescope=True)
register_lut(torch.exp)
register_lut(cos_arctan)