import torch
from torch import nn
import numpy as np
from .conv1d import TemporalConv1d
from typing import List, Tuple
from torch import Tensor
from fmot.functional import cos_arctan
from . import atomics
from . import Sequencer
from .composites import TuningEpsilon
from python_speech_features.base import get_filterbanks

def _get_norm(normalized):
    norm = None
    if normalized:
        norm = 'ortho'
    return norm

def get_rfft_matrix(size, normalized=False):
    weight = np.fft.rfft(np.eye(size), norm=_get_norm(normalized))
    w_real, w_imag = np.real(weight), np.imag(weight)
    return torch.tensor(w_real).float(), torch.tensor(w_imag).float()

def get_irfft_matrix(size, normalized=False):
    in_size = size//2 + 1
    w_real = np.fft.irfft(np.eye(in_size), n=size, norm=_get_norm(normalized))
    w_imag = np.fft.irfft(np.eye(in_size)*1j, n=size, norm=_get_norm(normalized))
    return torch.tensor(w_real).float(), torch.tensor(w_imag).float()

def get_mel_matrix(sr, n_dft, n_mels=128, fmin=0.0, fmax=None, **kwargs):
    mel_matrix = get_filterbanks(
        nfilt=n_mels, 
        nfft=n_dft, 
        samplerate=sr, 
        lowfreq=fmin,
        highfreq=fmax)
    return torch.tensor(mel_matrix, dtype=torch.float32)

def get_dct_matrix(n, n_out=None, dct_type=2, normalized=False):
    N = n
    if n_out is None:
        n_out = n
    K = n_out

    if K > N:
        raise ValueError(f"DCT cannot have more output features ({K}) than input features ({N})")
    matrix = None
    if dct_type == 1:
        ns = np.arange(1, N-1)
        ks = np.arange(K)
        matrix = np.zeros((N, K))
        matrix[0, :] = 1
        matrix[-1, :] = -1**ks
        matrix[1:-1, :] = 2*np.cos((np.pi*ks.reshape(1,-1)*ns.reshape(-1,1))/(N-1))
    elif dct_type == 2:
        ns = np.arange(N).reshape(-1,1)
        ks = np.arange(K).reshape(1,-1)
        matrix = 2*np.cos(np.pi*ks*(2*ns+1)/(2*N))
        if normalized:
            matrix[:,0] /= np.sqrt(4*N)
            matrix[:,1:] /= np.sqrt(2*N)
    elif dct_type == 3:
        ns = np.arange(1, N).reshape(-1,1)
        ks = np.arange(K).reshape(1,-1)
        matrix = np.zeros((N, K))
        matrix[0, :] = 1
        matrix[1:, :] = 2*np.cos(np.pi*(2*ks+1)*ns/(2*N))
        if normalized:
            matrix[0, :] /= np.sqrt(N)
            matrix[1:, :] /= np.sqrt(2*N)
    elif dct_type == 4:
        ns = np.arange(N).reshape(-1,1)
        ks = np.arange(K).reshape(1,-1)
        matrix = 2*np.cos(np.pi*(2*ks+1)*(2*ns+1)/(4*N))
        if normalized:
            matrix /= np.sqrt(2*N)
    else:
        raise ValueError(f'DCT type {dct_type} is not defined.')
    return torch.tensor(matrix).float()

class RFFT(nn.Module):
    r"""DEPRECATED!

    Real-to-complex 1D Discrete Fourier Transform.

    Returns the real and imaginary parts as two separate tensors.

    Args:
        size (int): length of input signal
        normalized (bool): whether to use a normalized DFT matrix. Default is False

    Shape:
            - Input: :math:`(*, N)` where :math:`*` can be any number of additional dimensions.
              :math:`N` must match the :attr:`size` argument.
            - Output:
                - Real Part: :math:`(*, \lfloor N/2 \rfloor + 1)`
                - Imaginary Part: :math:`(*, \lfloor N/2 \rfloor + 1)`

    .. seealso::

        - :class:`IRFFT`
    """
    def __init__(self, size, normalized=False):
        super().__init__()
        w_real, w_imag = get_rfft_matrix(size, normalized)
        self.w_real = nn.Parameter(w_real, requires_grad=False)
        self.w_imag = nn.Parameter(w_imag, requires_grad=False)

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        r"""
        Args:
            x (Tensor): Input, of shape :math:`(*, N)`

        Returns:
            - Real part, of shape :math:`(*, \lfloor N/2 \rfloor + 1)`
            - Imaginary part, of shape :math:`(*, \lfloor N/2 \rfloor + 1)`
        """
        real = torch.matmul(x, self.w_real)
        imag = torch.matmul(x, self.w_imag)
        return real, imag

class IRFFT(nn.Module):
    r"""DEPRECATED!
    Inverse of the real-to-complex 1D Discrete Fourier Transform.

    Inverse to :class:`RFFT`. Requires two input tensors for the real and imaginary
    part of the RFFT.

    Args:
        size (int): length of original real-valued input signal
        normalized (bool): whether to use a normalized DFT matrix. Default is False.

    Shape:
        - Re: :math:`(*, \lfloor N/2 \rfloor + 1)` where :math:`*` can be any number
          of additional dimensions. :math:`N` must match the :attr:`size` argument.
        - Im: :math:`(*, \lfloor N/2 \rfloor + 1)`
        - Output: :math:`(*, N)`

    .. seealso::

        - :class:`RFFT`
    """
    def __init__(self, size, normalized=False):
        super().__init__()
        w_real, w_imag = get_irfft_matrix(size, normalized)
        self.w_real = nn.Parameter(w_real, requires_grad=False)
        self.w_imag = nn.Parameter(w_imag, requires_grad=False)

    def forward(self, real: Tensor, imag: Tensor) -> Tensor:
        r"""
        Args:
            real (Tensor): Real part of the input, of shape :math:`(*, \lfloor N/2 \rfloor + 1)`
            imag (Tensor): Imaginary part of the input,
                of shape :math:`(*, \lfloor N/2 \rfloor + 1)`.

        Returns:
            - Output, of shape :math:`(*, N)`
        """
        return torch.matmul(real, self.w_real) + torch.matmul(imag, self.w_imag)

class DCT(nn.Module):
    r"""
    Discrete Cosine Transformation.

    Performs the DCT on an input by multiplying it with the DCT matrix.
    DCT Types :attr:`1`, :attr:`2`, :attr:`3`, and :attr:`4` are implemented. See
    `scipy.fftpack.dct <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.dct.html>`_
    for reference about the different DCT types. Type :attr:`2` is default.

    Args:
        in_features (int): Length of input signal that is going through the DCT
        out_features (int): Number of desired output DCT features. Default is :attr:`in_features`.
            Must satisfy :math:`\text{out_features} \leq \text{in_features}`
        dct_type (int): Select between types :attr:`1`, :attr:`2`, :attr:`3`, and :attr:`4`.
            Default is :attr:`2`.
        normalized (bool): If True and :attr:`dct_type` is :attr:`2`, :attr:`3`, or :attr:`4`,
            the DCT matrix will be normalized. Has no effect for :attr:`dct_type=1`.
            Setting normalized to True is equivalent to :attr:`norm="orth"` in
            `scipy.fftpack.dct <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.dct.html>`_

    Shape:
        - Input: :math:`(*, N)` where :math:`N` is :attr:`in_features`
        - Output: :math:`(*, K)` where :math:`K` is :attr:`out_features`, or :attr:`in_features` if
          :attr:`out_features` is not specified.
    """
    def __init__(self, in_features, out_features=None, dct_type=2, normalized=True):
        super().__init__()
        weight = get_dct_matrix(n=in_features, n_out=out_features, dct_type=dct_type,
            normalized=normalized)
        self.weight = nn.Parameter(weight, requires_grad=False)

    def forward(self, x):
        r"""
        Args:
            x (Tensor): Input, of shape :math:`(*, N)`
        Returns:
            - Output, of shape :math:`(*, K)` where :math:`K` is :attr:`out_features`,
                or :attr:`in_features` if :attr:`out_features` is not specified.
        """
        return torch.matmul(x, self.weight)

class MaxMin(nn.Module):
    def __init__(self):
        super().__init__()
        self.gt0 = atomics.Gt0()

    def forward(self, x, y):
        x_g = self.gt0(x - y)
        y_g = 1 - x_g
        max_els = x_g*x + y_g*y
        min_els = y_g*x + x_g*y
        return max_els, min_els

class LogEps(nn.Module):
    r"""
    Natural logarithm with a minimum floor. Minimum floor is automatically
    tuned when exposed to data. The minimum floor ensures numerical stability.

    Returns:

        .. math::

            \text{output} = \begin{cases}
                \log(x) & x > \epsilon \\
                \log(\epsilon) & x \leq \epsilon
            \end{cases}
    """
    def __init__(self):
        super().__init__()
        self.add_eps = TuningEpsilon()

    def forward(self, x):
        """
        """
        x = self.add_eps(x)
        return torch.log(x)

class Magnitude(nn.Module):
    r"""
    Computes magnitude from real and imaginary parts.

    Mathematically equivalent to

    .. math::

        \text{mag} = \sqrt{\text{Re}^2 + \text{Im}^2},

    but designed to compress the signal as minimally as possible when quantized:

    .. math::

        &a_{max} = \text{max}(|\text{Re}|, |\text{Im}|) \\
        &a_{min} = \text{min}(|\text{Re}|, |\text{Im}|) \\
        &\text{mag} = a_{max}\sqrt{1 + \frac{a_{min}}{a_{max}}^2}

    .. note::

        .. math::

            \sqrt{1 + x^2} = \cos{\arctan{x}}
    """
    def __init__(self):
        super().__init__()
        self.add_epsilon = TuningEpsilon()
        self.max_min = MaxMin()
        self.mul = atomics.VVMul()

    def forward(self, real, imag):
        """
        Args:
            real (Tensor): Real part of input
            imag (Tensor): Imaginary part of input

        Returns:
            - Magnitude
        """
        a, b = self.max_min(real.abs(), imag.abs())
        eta = b / self.add_epsilon(a)
        eta_p = cos_arctan(eta)
        return self.mul(a, eta_p)
    
class _EMA(Sequencer):
    """Sequencer implementation of EMA"""
    def __init__(self, features: int, alpha: float, dim: int):
        super().__init__([[features]], 0, seq_dim=dim)
        assert 0 < alpha < 1
        self.alpha = alpha
        self.om_alpha = 1 - alpha

    @torch.jit.export
    def step(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        y, = state
        y = self.alpha * y + self.om_alpha * x
        return y, [y]

class EMA(nn.Module):
    """Exponential Moving Average
    
    Arguments:
        features (int): number of input features
        alpha (float): smoothing coefficient, between 0 and 1. Time constant is ``-1/log(alpha)`` frames
        dim (int): dimension to apply exponential moving average to. Should be the temporal/sequential dimension
    """
    def __init__(self, features: int, alpha: float, dim: int):
        super().__init__()
        self.ema = _EMA(features, alpha, dim)

    def forward(self, x):
        x, __ = self.ema(x)
        return x

class MelFilterBank(nn.Module):
    r"""
    Project FFT bins into Mel-Frequency bins.

    Applies a linear transformation to project FFT bins into Mel-frequency bins.

    Args:
        sr (int): audio sampling rate (in Hz)
        n_fft (int): number of FFT frequencies
        n_mels (int): number of mel-frequencies to create
        fmin (float): lowest frequency (in Hz), default is 0
        fmax (float): maximum frequency (in Hz). If :attr:`None`, the Nyquist frequency
            :attr:`sr/2.0` is used. Default is :attr:`None`.
        **kwargs: keyword arguments to pass to
            `librosa.filters.mel <https://librosa.org/doc/latest/generated/librosa.filters.mel.html>`_
            when generating the mel transform matrix

    Shape:
        - Input: :math:`(*, C_{in})` where :math:`*` is any number of dimensions and
          :math:`C_{in} = \lfloor \text{n_dft}/2 + 1 \rfloor`
        - Output: :math:`(*, \text{n_mels})`

    .. seealso::

        - :class:`MelSpectrogram`

    .. todo::

        Compute the Mel transform matrix internally, getting rid of librosa
        dependency?
    """
    def __init__(self, sr, n_fft, n_mels=128, fmin=0.0, fmax=None, **kwargs):
        super().__init__()
        weight = get_mel_matrix(sr, n_fft, n_mels, fmin, fmax, **kwargs)
        self.weight = nn.Parameter(weight.t(), requires_grad=False)

    def forward(self, x):
        """"""
        return torch.matmul(x, self.weight)

class MelTranspose(nn.Linear):
    r"""
    Project Mel-Frequency bins back into FFT bins.

    Args:
        sr (int): audio sampling rate (in Hz)
        n_fft (int): number of FFT frequencies
        n_mels (int): number of mel-frequencies to create
        fmin (float): lowest frequency (in Hz), default is 0
        fmax (float): maximum frequency (in Hz). If :attr:`None`, the Nyquist frequency
            :attr:`sr/2.0` is used. Default is :attr:`None`.

    Shape:
        - Input: :math:`(*, C_{in})` where :math:`*` is any number of dimensions and
          :math:`C_{in} = \lfloor \text{n_dft}/2 + 1 \rfloor`
        - Output: :math:`(*, \text{n_mels})`
    """
    def __init__(self, sr, n_fft, n_mels, fmin=0.0, fmax=None):
        super().__init__(
            out_features=n_fft//2 + 1,
            in_features=n_mels,
            bias=False)
        mat = get_mel_matrix(sr, n_fft, n_mels, fmin, fmax).T
        self.weight = nn.Parameter(mat, requires_grad=False)
