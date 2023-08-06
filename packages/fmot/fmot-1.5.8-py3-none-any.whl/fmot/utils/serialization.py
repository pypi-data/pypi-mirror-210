import torch

def save(cmodel, path):
    """
    Saves a ConvertedModel to a path location.

    Args:
        cmodel (fmot.nn.ConvertedModel): converted model
            to save
        path (string): path to the file  where the cmodel
            will be saved

    Returns:

    """
    torch.save(cmodel, path)


def load(model_path, device='cpu'):
    """
    Loads a ConvertedModel to a path location.

    Args:
        cmodel (fmot.nn.ConvertedModel): converted model
            to save
        path (string): path to the file where the cmodel state_dict
            is be saved

    Returns:
        cmodel_state_dict: the state_dict of the cmodel
            stored in the file
    """
    cmodel_state_dict = torch.load(model_path, device)

    return cmodel_state_dict


def load_state_dict(cmodel, cmodel_state_dict):
    """
    Loads the parameter from a PyTorch state_dict
    object to a Femtostack

    Args:
        cmodel (fmot.nn.ConvertedModel): converted model
            to update
        cmodel_state_dict: a state_dict from a different
            Converted Model (for example a pretrained one)

    Returns:
        cmodel (fmot.nn.ConvertedModel): the updated
            Converted Model

    """
    cmodel_dict_orig = cmodel.state_dict()
    trunc_pretrained_dict = dict()

    # If null tensor are saved in the pretrained
    # dict, just skip over it
    for k, v in cmodel_state_dict.items():
        if not(v.shape == torch.Size([0])):
            trunc_pretrained_dict[k] = v

    try:
        cmodel_dict_orig.update(trunc_pretrained_dict)
    except:
        raise Exception("Couldn't load cmodel state_dict. If the state_dict " +
                        "comes from a ConvertedModel that has been quantized, "
                        "then the cmodel itself should be quantized, and vice versa. "
                        "Otherwise, check that models architectures are matching.")
    cmodel.load_state_dict(cmodel_dict_orig)

    return cmodel