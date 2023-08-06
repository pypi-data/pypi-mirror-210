import torch
from torch.nn.utils import prune
import inspect
from collections import namedtuple
from fmot.qat.nn import QuantWrapper
from torch.nn.utils.prune import CustomFromMask, PruningContainer, BasePruningMethod
from fmot.nn.sequenced_rnn import default_torch2seq_param_mapping, \
    get_trailing_number, map_param_name, rsetattr, rgetattr
from .default_substitutions import get_default_substitutions

def get_pruner_kwargs(pruner):
    kwargs = {}
    arg_names = list(inspect.signature(pruner.apply).parameters.keys())
    for name in arg_names:
        if hasattr(pruner, name):
            kwargs[name] = getattr(pruner, name)
    return kwargs

PruningInfo = namedtuple('PruningInfo', ['module_name', 'tensor_name', 'mask', 'pruner', 'kwargs', 'is_substituted'])

def remove_all_pruners(model, verbose=False):
    """
    Remove all pruning reparametrizations before converting the model. The model
    is modified in-place.

    Args:
        model (Module): Model to have pruning reparametrizations removed

    """
    pruning_info = [] 

    for mname, module in list(model.named_modules()) + [('', model)]:
        for hook in list(module._forward_pre_hooks.values()):
            if isinstance(hook, prune.BasePruningMethod):
                tname = hook._tensor_name
                mask = getattr(module, tname + '_mask')
                # remove pruning reparametrization
                prune.remove(module, tname)
                if verbose:
                    print(f'Removing pruning reparametrization for {mname}.{tname}')

                # get pruning info so that the pruner can be reapplied
                if isinstance(hook, prune.PruningContainer):
                    pm = hook._pruning_methods[-1]
                else:
                    pm = hook
                pinfo = PruningInfo(
                    module_name=mname,
                    tensor_name=tname,
                    mask=mask,
                    pruner=pm,
                    kwargs=get_pruner_kwargs(pm),
                    is_substituted=type(module) in get_default_substitutions())
                pruning_info.append(pinfo)

    return pruning_info

def reapply_all_pruners(qmodel, model, pruning_info, substitution_dict, verbose=False):
    if isinstance(qmodel, QuantWrapper):
        qmodel = qmodel.model

    for info in pruning_info:
        if info.module_name != '':
            full_name = f'{info.module_name}.{info.tensor_name}'
        else:
            full_name = info.tensor_name
        if full_name in substitution_dict:
            full_name = substitution_dict[full_name][0].rsplit('model.')[1]
        if '.' in full_name:
            module_name, param_name = full_name.rsplit('.', 1)
        else:
            module_name, param_name = '', full_name
        try:
            module = rgetattr(qmodel, module_name)
        except:
            raise Exception(f'Could not find submodule with name {module_name} in converted model.')
        prune.custom_from_mask(module, param_name, info.mask)
        if verbose:
            print(f'Reapplying pruning reparametrization for {info.module_name}.{info.tensor_name}')

        prune.custom_from_mask(rgetattr(model, info.module_name), info.tensor_name, info.mask)
