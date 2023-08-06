from fmot.convert.default_patchings import DEFAULT_PATCHINGS, PatchRule
from fmot.convert.default_mappings import DEFAULT_MAPPINGS
import inspect

def supported_ops():
    """
    Returns a list of supported operations.
    """
    sops = []
    # iterate over all of the patchings, ensuring that there is an available mapping
    for k, v in DEFAULT_PATCHINGS.items():
        if isinstance(v, PatchRule):
            patchings = v.options
        else:
            patchings = [v]
        # for p in patchings:
            # assert p in DEFAULT_MAPPINGS, f'Not found: {p}'
        sops += [k]
    # iterate over all of the mappings, add mappings that start with builtin modules
    for m in DEFAULT_MAPPINGS:
        if m.__module__.startswith('torch'):
            sops += [m]
    return sops

def typename(x):
    if isinstance(x, type):
        s = str(x)
        return s.split("'")[1]
    else:
        return x

def conversion_branch(op):
    branch = [op]
    if inspect.isfunction(op):
        assert op.__module__ == 'torch.nn.functional'
        op = 'F.' + op.__name__
        branch = [op]
    elif type(op).__name__ == 'builtin_function_or_method':
        name = op.__name__
        op = 'aten::' + name
        branch = ['torch.' + name, op]
    if op in DEFAULT_PATCHINGS:
        op = DEFAULT_PATCHINGS[op]
        if isinstance(op, PatchRule):
            op = op.options[0]
        branch += [op]
    if op in DEFAULT_MAPPINGS:
        op = DEFAULT_MAPPINGS[op]
        branch += [op]
    else:
        branch += ['patched', 'mapped']
    return ' -> '.join([typename(n) for n in branch])

