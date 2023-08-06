import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
import datashader as ds
from datashader.mpl_ext import dsshow, alpha_colormap
import pandas as pd
import colorcet as cc
from torch import nn


def get_diagnosis(model, cmodel, sample_input, to_register=None, kind='output', plot: bool=True,
                  how='log'):
    ''' Prints a diagnosis for all layers of the model, comparing the activations
        for the torch model and for the ConvertedModel, for a given sample_input.

    Args:
        model (torch.nn.Module): a PyTorch Model
        cmodel (fmot.ConvertedModel): its converted/quantized equivalent
        sample_input (torch.Tensor): sample input on which the comparison is carried out
        to_register (set(str)): if None, the comparison will be carried out on all layers.
            If a set of strings is used, the comparison will only be carried out on the
            layer with these names.
        kind (str): 'output' or 'input', so that the comparison will be carried out on outputs
            or inputs of the layers respectively.
        plot (bool): default True, determines whether a plot will be generated for each layer
        how (str): default True. Can be 'log' or 'linear'. Defines the kind of scale that is used for color-mapping.
    '''
    acts = get_activations(model, sample_input, to_register, kind=kind)
    qacts = get_activations(cmodel, sample_input, to_register=set(acts.keys()), kind=kind)
    if plot:
        plot_acts(model, acts, qacts, kind=kind, how=how)


def act_hook_fn(name: str, activations: dict, kind='output'):
    if kind == 'output':
        def reg_act(model, input, output):
            if type(output) in {tuple, list}:
                activations[name] = output[0].detach()
            else:
                activations[name] = output.detach()
    elif kind == 'input':
        def reg_act(model, input, output):
            if type(input) in {tuple, list}:
                activations[name] = input[0].detach()
            else:
                activations[name] = input.detach()
    else:
        raise Exception('Unknown kind.')

    return reg_act


def register_act_hooks(net, activations:dict, handles: list, to_register=None, kind='output'):
    for name, layer in net._modules.items():
        if isinstance(layer, nn.Sequential):
            register_act_hooks(layer, activations, handles, to_register, kind=kind)
        else:
            hook_fn = act_hook_fn(name, activations, kind=kind)

            if to_register is not None:
                if name in to_register:
                    hdl = layer.register_forward_hook(hook_fn)
                    handles.append(hdl)
            else:
                hdl = layer.register_forward_hook(hook_fn)
                handles.append(hdl)


def get_activations(model, sample_input, to_register=None, kind='output'):
    activations = dict()
    handles = []
    if hasattr(model, 'param2quant'): #aims at testing if we have a ConvertedModel
        register_act_hooks(model.model.model, activations, handles, to_register, kind=kind)
    else:
        register_act_hooks(model, activations, handles, to_register, kind=kind)
    model(sample_input)
    for handle in handles:
        handle.remove()

    # TODO: need to handle substitutions

    return activations


def plot_acts(net, acts:dict, qacts:dict, kind='output', how='log'):
    for name, layer in net._modules.items():
        if isinstance(layer, nn.Sequential):
            plot_acts(net, acts, qacts)
        else:
            if name in set(acts.keys()):
                x = acts[name].reshape(1, -1).squeeze().numpy()
                y = qacts[name].reshape(1, -1).squeeze().numpy()
                df = pd.DataFrame(data=np.stack([x, y], axis=-1), columns=["x", "y"])

                fig = plt.figure(figsize=(5.5, 5.5))
                grid = ImageGrid(fig, 111, nrows_ncols=(1, 1), axes_pad=0.5, share_all=True,
                                 cbar_location="right", cbar_mode="each", cbar_size="5%", cbar_pad="2%")

                artist3 = dsshow(df, ds.Point('x', 'y'), ds.count(), norm=how, cmap='inferno', aspect='equal',
                                 ax=grid[0])
                plt.colorbar(artist3, cax=grid.cbar_axes[0])
                grid[0].set_facecolor('#000000')
                grid[0].set_title(f'{name}: {kind}')
                plt.xlabel('acts')
                plt.ylabel('qacts')
                plt.show()
