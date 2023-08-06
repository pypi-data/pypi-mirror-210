from .atomics import *
from . import quantizers
from functools import partial
from fmot import CONFIG

class LUT(nn.Module):
    def __init__(self, function, bitwidth, lut_bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits
        self.function = function
        self.input_requantizer = Requantize(
            bitwidth=lut_bitwidth,
            observer=quantizers.FixedRangeObserver,
            limits=self.limits)
        self.lut = BareLUT(function, bitwidth, observer=observer)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    @check_for_annotations
    def forward(self, x):
        return self.lut(self.input_requantizer(x))

    def __repr__(self):
        return f'{self.function.__name__}LUT'

    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        """
        Regardless of what observer is passed in, a FixedRangeObserver
        is always used.
        """
        observer = partial(observer, **kwargs)
        if type(parent) == fmot.nn.LUT:
            kwargs = dict(
                function=parent.function,
                lut_bitwidth=bw_conf.lut,
                bitwidth=bw_conf.activations,
                limits=parent.limits,
                observer=observer)
            if bw_conf.activations == fqint16:
                if parent.telescope:
                    if parent.add_identity:
                        return AddIdentityTLUT(**kwargs)
                    elif parent.mul_identity:
                        return MulIdentityTLUT(**kwargs)
                    elif parent.interpolate:
                        return TILUT(**kwargs)
                    else:
                        return TLUT(**kwargs)
                elif interpolate & parent.interpolate:
                    return ILUT(**kwargs)
                else:
                    return cls(**kwargs)
            else:
                return cls(**kwargs)
        else:
            return cls(
                bitwidth=bw_conf.activations, 
                lut_bitwidth=bw_conf.lut)


class ILUT(nn.Module):
    """
    Interpolating Lookup Table
    Technically a composite -- defined here to avoid circular imports
    """
    def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits
        lim_obs = partial(quantizers.FixedRangeObserver, limits=limits,
            hard_maximum=True)
        if CONFIG.ilut_requant:
            self.requant = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_down = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_up = Requantize(bitwidth, observer=lim_obs)
        quantizers.share_observer(self.shift_up, self.shift_down)
        self.obs_in = self.shift_up.quantizer.observer
        self.add_one = VIAdd(0., lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.rem_muli = VIMul(1., bitwidth)
        self.mux_neg = Neg()
        self.mux_op = VIAdd(1., bitwidth)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)

        # Group all submodules into a single quantization group
        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        if CONFIG.ilut_requant:
            x = self.requant(x)
        if x.quantized:
            bw = self.shift_down.quantizer.bitwidth.bitwidth
            q_addr = self.obs_in.calculate_quanta(bw)
            self.add_one.imm.data = 2.**(q_addr).detach()
            self.rem_muli.imm.data = 2.**(-q_addr).detach()
        addr = copy_dim_annotations(x, self.shift_down(x))
        addr_p = self.add_one(addr)
        y0 = self.lut(addr)
        y1 = self.lut(addr_p)
        rem1 = self.rem_muli(self.rem_sub(x, self.shift_up(addr)))
        rem0 = self.mux_op(self.mux_neg(rem1))
        y = self.add(self.mul0(rem0, y0), self.mul1(rem1, y1))
        return y

    def to_simple_lut(self):
        kwargs = dict(
            function=self.lut.function,
            lut_bitwidth=self.shift_down.quantizer.bitwidth,
            bitwidth=self.shift_up.quantizer.bitwidth,
            limits=self.limits
            )
        obs_in = self.shift_down.quantizer.observer
        obs_out = self.lut.quantizer.observer
        lut = LUT(**kwargs)
        lut.input_requantizer.quantizer.observer = obs_in
        lut.lut.quantizer.observer = obs_out

        quantizers.enable_quantization(lut, 
            quantizers.is_quantized(self))
        return lut

class TLUT(nn.Module):
    """
    Telescoping Lookup Table -- technically a composite, defined here
    to avoid circular imports
    """
    def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        if limits is None:
            limits = (None, None)
        self.limits = limits

        lim_obs = partial(quantizers.FixedRangeObserver, limits=limits)
        self.shift_down = Requantize(lut_bitwidth, observer=lim_obs)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.coarse_lut = BareLUT(function, bitwidth)
        self.fine_lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.not_neg = Neg()
        self.not_addi = VIAdd(1., lut_bitwidth)
        self.gate_shift = Shift(0, bitwidth)
        self.gt = Gt0(lut_bitwidth)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        addr = self.shift_down(x)
        y_coarse = self.coarse_lut(addr)
        rem = self.shift_rem(x)
        if x.quantized:
            y_fine = self.fine_lut(rem)
        else:
            y_fine = self.fine_lut(copy_annotations(x, x*0))
        coarse = self.gt(addr)
        fine = self.not_addi(self.not_neg(coarse))
        coarse = self.gate_shift(coarse)
        fine = self.gate_shift(fine)
        y = self.add(self.mul0(coarse, y_coarse), self.mul1(fine, y_fine))
        if x.quantized:
            return y
        else:
            return y_coarse

class AddIdentityTLUT(nn.Module):
    """
    Telescoping Lookup Table; leveraging an additive identity

    Applicable when the following identity holds for all positive a, b:

    .. math::

        f(a * b) = f(a) + f(b)
    """
    def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.function = function
        self.shift_down = Shift(0, lut_bitwidth)
        self.gt = Gt0(lut_bitwidth)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.mul_alpha = VIMul(1., lut_bitwidth)
        self.is_small_neg = Neg()
        self.is_small_op = VIAdd(1., lut_bitwidth)
        self.mux_mul0 = VVMul(lut_bitwidth)
        self.mux_mul1 = VVMul(lut_bitwidth)
        self.mux_add = VVAdd(lut_bitwidth)
        self.is_small_shift = Shift(0, bitwidth)
        self.mul_falpha = VIMul(0., bitwidth)
        self.demixer = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        is_large = self.gt(addr)
        is_small = self.is_small_op(self.is_small_neg(is_large))
        rem = self.shift_rem(x)
        if x.quantized:
            alpha = 2**(addr.quanta - rem.quanta).detach()
            self.mul_alpha.imm.data = alpha
            self.mul_falpha.imm.data = -self.function(alpha).detach()
        rem = self.mul_alpha(rem)
        mixed_addr = self.mux_add(self.mux_mul0(addr, is_large), self.mux_mul1(rem, is_small))
        mixed_y = self.lut(mixed_addr)
        to_add = self.mul_falpha(self.is_small_shift(is_small))
        unmixed_y = self.demixer(mixed_y, to_add)
        return unmixed_y

class MulIdentityTLUT(nn.Module):
    """
    Telescoping Lookup Table, leveraging a multiplicative identity

    Applicable when the following identity holds for all positive a, b:

    .. math::

        f(a * b) = f(a) * f(b)
    """
    def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.function = function
        self.shift_down = Shift(0, lut_bitwidth)
        self.gt = Gt0(lut_bitwidth)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.lut = BareLUT(function, bitwidth)
        self.mul_alpha = VIMul(1., lut_bitwidth)
        self.is_small_neg = Neg()
        self.is_small_op = VIAdd(1., lut_bitwidth)
        self.mux_mul0 = VVMul(lut_bitwidth)
        self.mux_mul1 = VVMul(lut_bitwidth)
        self.mux_add = VVAdd(lut_bitwidth)
        self.is_small_shift = Shift(0, bitwidth)
        self.mul_falpha = VIMul(0., bitwidth)
        self.add_multipliers = VIAdd(1., bitwidth)
        self.demixer = VVMul(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        is_large = self.gt(addr)
        is_small = self.is_small_op(self.is_small_neg(is_large))
        rem = self.shift_rem(x)
        if x.quantized:
            alpha = 2**(addr.quanta - rem.quanta).detach()
            self.mul_alpha.imm.data = alpha
            self.mul_falpha.imm.data = 1/self.function(alpha).detach() - 1
        rem = self.mul_alpha(rem)
        mixed_addr = self.mux_add(self.mux_mul0(addr, is_large), self.mux_mul1(rem, is_small))
        mixed_y = self.lut(mixed_addr)
        to_mul = self.add_multipliers(self.mul_falpha(self.is_small_shift(is_small)))
        unmixed_y = self.demixer(mixed_y, to_mul)
        return unmixed_y

# class AddIdentityTILUT(nn.Module):
#     """Telescoping & Interpolating Lookup Table, 
#     for functions that satisfy 
#     .. math::

#         f(a * b) = f(a) * f(b)
        
#     for positive a and b"""
#     def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
#                  observer=quantizers.DEFAULT_OBSERVERS['default']):
#         super().__init__()
#         self.tele = Shift(-8, bitwidth=bitwidth)
#         self.gt0 = Gt0(bitwidth)


class TILUT(nn.Module):
    """
    Telescoping & Interpolating Lookup Table
    """
    def __init__(self, function, lut_bitwidth, bitwidth, limits=None,
        observer=quantizers.DEFAULT_OBSERVERS['default']):
        super().__init__()
        self.shift_down = Shift(0, lut_bitwidth)
        self.shift_rem = Shift(-1, lut_bitwidth)
        self.coarse_lut = ILUT(function, lut_bitwidth, bitwidth, limits)
        self.fine_lut = BareLUT(function, bitwidth)
        self.rem_sub = VVSub(bitwidth)
        self.not_neg = Neg()
        self.not_addi = VIAdd(1., lut_bitwidth)
        self.gate_shift = Shift(0, bitwidth)
        self.gt = Gt0(lut_bitwidth)
        self.mul0 = VVMul(bitwidth)
        self.mul1 = VVMul(bitwidth)
        self.add = VVAdd(bitwidth)
        self.observer = quantizers.FixedRangeObserver(limits)

        self.q_group = quantizers.PrecisionConstraint()
        self.q_group.recursively_add(self)

    def forward(self, x):
        self.observer(x)
        if x.quantized:
            q_addr = self.observer.calculate_quanta(self.shift_down.bitwidth.bitwidth)
            q_x = x.quanta
            shamt = intitem(q_x - q_addr)
            self.shift_down.shamt = shamt
        addr = self.shift_down(x)
        y_coarse = self.coarse_lut(x)
        rem = self.shift_rem(x)
        if x.quantized:
            y_fine = self.fine_lut(rem)
        else:
            y_fine = self.fine_lut(copy_annotations(x, x*0))
        coarse = self.gt(addr)
        fine = self.not_addi(self.not_neg(coarse))
        coarse = self.gate_shift(coarse)
        fine = self.gate_shift(fine)
        y = self.add(self.mul0(coarse, y_coarse), self.mul1(fine, y_fine))
        if x.quantized:
            return y
        else:
            return y_coarse

"""
TODO: AddIdentity and MulIdentity TILUTs
"""

class RSqrtPlusEps(LUT):
    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        eps = parent.eps
        def rsqrt_peps(x):
            return torch.rsqrt(x + eps)
        config = fmot.LUTConfig(rsqrt_peps, limits=None, 
            interpolate=fmot.LUT_REGISTRY['aten::reciprocal'].interpolate)
        parent_obj = fmot.nn.LUT(config)
        return LUT._from_float(parent_obj, bw_conf, interpolate)

class PowFrac(LUT):
    @classmethod
    def _from_float(cls, parent, bw_conf, interpolate,
        observer=quantizers.DEFAULT_OBSERVERS['default'], **kwargs):
        power = parent.power
        def pow_frac(x):
            return torch.pow(x, power)
        if power > 1:
            config = fmot.LUTConfig(pow_frac, limits=None, 
                interpolate=fmot.LUT_REGISTRY['aten::sqrt'].interpolate)
        else:
            config = fmot.LUTConfig(pow_frac, limits=None,
                telescope=True, mul_identity=True)
        parent_obj = fmot.nn.LUT(config)
        return LUT._from_float(parent_obj, bw_conf, interpolate)