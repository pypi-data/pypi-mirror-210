from .batchdim_removal import remove_batchdim
from .dimtag_removal import remove_named_dims
from .kernelize_lstm import kernelize_lstm
from .kernelize_temporal_unfold import kernelize_temporal_unfold
from .cleanup import uniquify_names, limit_biases, remove_unused_params
from .kernelize_red_broad import kernelize_sum, kernelize_broadcast


PASS_ORDER = [
    kernelize_lstm,
    kernelize_temporal_unfold,
    kernelize_sum,
    kernelize_broadcast,
    uniquify_names,
    limit_biases,
    remove_unused_params
]

def run_passes(graph):
    for p in PASS_ORDER:
        p(graph)
