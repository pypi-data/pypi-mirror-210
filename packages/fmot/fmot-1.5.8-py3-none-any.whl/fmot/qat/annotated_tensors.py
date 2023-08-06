import torch
from functools import wraps, partial
import warnings

ANNOS = ['bitwidth', 'quanta', 'quantized', 'avg_sparsity', 'annotated', 'prev_relu',
    'density_per_element']#,'dimensions']


def tag_dim(forward_func):
    ''' Decorator for any forward method that tags the dimensions
        of the inputs with the class dimensions attribute
        If inputs have a dimensions attribute already, it's left unchanged
    '''
    def dim_tagged_forward(self, *args):
        for arg in args:
            if not hasattr(arg, 'dimensions'):
                set_dim_annotations(self.dimensions, arg)
        return forward_func(self, *args)

    return dim_tagged_forward

def annotate(x, bitwidth, quanta, quantized=False, avg_sparsity=None, dimensions=None,
    prev_relu=False, density_per_element=None):
    x.bitwidth = bitwidth
    x.quanta = quanta
    x.quantized = quantized
    if avg_sparsity is None:
        avg_sparsity = 0.
    x.avg_sparsity = avg_sparsity
    x.prev_relu = prev_relu
    set_dim_annotations(dimensions, x)
    x.annotated = True
    x.density_per_element = density_per_element
    return x

def copy_annotations(x, y):
    """copy x's annotations to y"""
    for anno in ANNOS:
        y.__setattr__(anno, x.__getattribute__(anno))
    try:
        y.__setattr__('dimensions', x.__getattribute__('dimensions'))
    except:
        warnings.warn('Input dimensions are missing: dimension information has not been propagated correctly')
    return y

def copy_dim_annotations(x, y):
    """copy x's dimensions annotations to y"""
    try:
        dimensions = x.__getattribute__('dimensions')
        if dimensions is not None:
            y.__setattr__('dimensions', list(dimensions))
    except:
        warnings.warn('Input dimensions are missing: dimension information has not been propagated correctly')
    return y

def set_dim_annotations(dim, y):
    """set y's dimensions annotation to dim"""
    try:
        if type(y) == tuple:
            for yy in y:
                yy.__setattr__('dimensions', dim)
        else:
            y.__setattr__('dimensions', dim)
    except:
        warnings.warn('Could not propagte dimension to input')
    return y

def get_dim_annotations(*args):
    """get arg's dimensions annotation
        We assume that longest dimension = last dimension
        to support broadcasting
    """
    try:
        max_len_dim = 0
        for arg in args:
            try:
                if len(arg.dimensions) > max_len_dim:
                    max_len_dim = len(arg.dimensions)
                    dimensions = arg.__getattribute__('dimensions')
            except:
                pass #we discard if one of the inputs is not annotated
        return dimensions
    except:
        warnings.warn('Input dimensions are missing: dimension information has not been propagated correctly')
        return None

def asint(x):
    if x.quantized:
        z = (x / 2**x.quanta).int()
        bits = x.bitwidth.bitwidth
        z = torch.clamp(z, -2**(bits-1), 2**(bits-1)-1)
        return z
    else:
        raise ValueError('Cannot convert unquantized tensor to integer')

def check_for_annotations(obj):
    if isinstance(obj, torch.Tensor):
        if not hasattr(obj, 'annotated'):
            warnings.warn(
                'input tensor has not been passed through a quantizer, ' +
                'indicating that an operation has not been properly quantized',
                stacklevel=4)
    elif callable(obj):
        f = obj
        @wraps(f)
        def wrapped(*args, **kwargs):
            layer = args[0]
            for arg in args:
                check_for_annotations(arg)
            for k, v in kwargs.items():
                check_for_annotations(v)
            outputs = f(*args, **kwargs)
            if isinstance(outputs, torch.Tensor):
                check_for_annotations(outputs)
            else:
                for output in outputs:
                    check_for_annotations(output)
            return outputs
        return wrapped
    else:
        pass
