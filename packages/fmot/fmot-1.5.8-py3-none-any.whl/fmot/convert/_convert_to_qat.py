from . import patching, mapping, substitution, prune_reparametrization
from fmot.qat import bitwidths
import warnings

def convert_torch_to_qat(model, bw_conf='double', interpolate=True, extra_patchings=None,
                         extra_mappings=None, extra_substitutions=None, quant_wrap=True,
                         verbose=False, remove_pruners=True, dimensions=None):
    """Convert a PyTorch model to fmot.qat format

    Args:
        model (:class:`torch.nn.Module`): PyTorch model to be converted
        bw_conf (str): Bitwidth configuration. Must be one of
            ``["double", "standard", "eights"]``. Default is ``"double"``. See
            :doc:`precision` for more information.
        interpolate (bool): Whether to use interpolation (and other approximation methods)
            to improve the accuracy of LUT-based nonlinearities.
        extra_patchings (dict): Optional dictionary of supplemental patching rules.
        extra_mappings (dict): Optional dictionary of supplemental mapping rules.
        quant_wrap (bool): Whether to wrap the model with input quantizers.
            Default is True.
        verbose (bool): Whether to print a status report during conversion.
        remove_pruners (bool): whether to remove (and reapply) pruning
            reparametrization during conversion, default True.
        dimensions (list[str]): dimension tags for the model input. Not a 
            required argument.
    """
    # Get bitwidth conf as a BitwidthConfig object
    if isinstance(bw_conf, str):
        bw_conf = bitwidths.bw_conf_dict[bw_conf]

    # Remove pruning reparametrizations
    if remove_pruners:
        if verbose:
            print('REMOVING PRUNING REPARAMETRIZATION')
        pinfo = prune_reparametrization.remove_all_pruners(model, verbose=verbose)

    # Substitute
    if verbose:
        print('-'*55)
        print('SUBSTITUTION:')
    substitutions_dict = dict()
    smodel = substitution.torch_to_sequencer(model, extra_substitutions=extra_substitutions,
        substitutions_dict=substitutions_dict, verbose=verbose)

    # Patch
    if verbose:
        print('-'*55)
        print('PATCHING:')
    pmodel = patching.patch(smodel, extra_patchings=extra_patchings,
        extra_mappings=extra_mappings, verbose=verbose)
    if verbose:
        print('-'*55)
        print('MAPPING:')

    # Map
    qmodel = mapping.map_to_qat(
        pmodel, bw_conf=bw_conf, interpolate=interpolate, extra_mappings=extra_mappings,
        quant_wrap=quant_wrap, deepcopy=True, verbose=verbose, dimensions=dimensions)
    qmodel.substitutions_dict = substitutions_dict

    if remove_pruners:
        if verbose:
            print('-'*55)
            print('REAPPLYING PRUNING REPARAMETRIZATION')
        pinfo = prune_reparametrization.reapply_all_pruners(qmodel, model,
            pinfo, substitutions_dict, verbose=verbose)
    return qmodel
