import torch
from torch import nn

class _diffable_round(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)
    
    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            return grad
        else:
            return None

class _diffable_mod(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, m):
        return x - m*torch.floor(x/float(m))

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            return grad, None
        else:
            return None, None

class _diffable_floor(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        return torch.floor(x)

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            return grad
        else:
            return None

def diff_round(x):
    return _diffable_round.apply(x)

def diff_floor(x):
    return _diffable_floor.apply(x)

def diff_mod(x, m):
    return _diffable_mod.apply(x, m)

class _fake_quantize_floor(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, quanta, bits):
        scale = 2**quanta
        edge = 2**(bits-1)
        R = torch.floor(x/scale)
        ctx.save_for_backward(torch.logical_or(R < -edge, R > edge-1))
        return scale * torch.clamp(R, -edge, edge-1)

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            mask, = ctx.saved_tensors
            grad = grad.masked_fill(mask, 0)
            return grad, None, None
        else:
            return None, None, None

class _fake_quantize_round(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, quanta, bits):
        scale = 2**quanta
        edge = 2**(bits-1)
        x = torch.round(x/scale)
        ctx.save_for_backward(torch.logical_or(x < -edge, x > edge-1))
        return scale * torch.clamp(x, -edge, edge-1)

    @staticmethod
    def backward(ctx, grad):
        if ctx.needs_input_grad[0]:
            mask, = ctx.saved_tensors
            grad = grad.masked_fill(mask, 0)
            return grad, None, None
        else:
            return None, None, None

def fake_quantize(x, quanta, bits, rounded=False):
    """
    Fake-quantize an activation or parameter tensor.
    
    scale = 2**quanta
    xfq = 2**quanta * Clamp(Round_fn(x/(2**quanta)), -2**(bits-1), 2**(bits-1)-1)

    By default, Round_fn(x) = Floor(x)
    However, for parameter tensors, it may be preferred for Round_fn(x) = Round(x)
    """
    if rounded:
        return _fake_quantize_round.apply(x, quanta, bits)
    else:
        return _fake_quantize_floor.apply(x, quanta, bits)