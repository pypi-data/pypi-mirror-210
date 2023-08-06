import fmot
import torch
from ..nn.sru import SRU

DEFAULT_SUBSTITUTIONS = {
    torch.nn.modules.rnn.RNN: fmot.nn.RNN,
    torch.nn.modules.rnn.GRU: fmot.nn.GRU,
    fmot.nn.TemporalConv1d: fmot.nn.conv1d.FmotConv1dWrapper,
    SRU: fmot.nn.SRUSequencer
}

def get_default_substitutions():
    """Apply config settings (e.g. turn on/off LSTM substitution mapping)
    """
    substitutions = DEFAULT_SUBSTITUTIONS.copy()
    if fmot.CONFIG.sequenced_lstm:
        substitutions[torch.nn.modules.rnn.LSTM] = fmot.nn.LSTM
    return substitutions

