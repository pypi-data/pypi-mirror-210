import torch
from copy import deepcopy
from ..utils import rgetattr

def get_id2name_dict(model):
    id2name_dict = dict()
    for param_id, (name, param) in enumerate(model.named_parameters()):
        id2name_dict[param_id] = name
    
    return id2name_dict

# This is to create the equivalent generator
def new_param_generator(model, qmodel):
    ''' Create a Module.parameters generator for the quantized model qmodel
        with the same parameter ordering as the initial model
    '''
    for name, param in model.named_parameters():
        if name in qmodel.substitutions_dict.keys():
            children_dict, _ = qmodel.substitutions_dict[name]
            new_param_name = next(iter(children_dict))
        else:
            new_param_name = 'model.' + name
        yield rgetattr(qmodel, new_param_name)
    
# Only valid for one group
def inherit_optimizer(optimizer, model, qmodel):
    ''' Returns a new optimizer inherited from the optimizer for the original
        model: it will operate on the weights of the new quantized model and
        apply the same transformations to the optimizer parameters that
        were applied to tensor parameter 
    
    '''
    id2name = get_id2name_dict(model)
    temp_state_dict = {}
    new_optimizer = type(optimizer)(new_param_generator(model, qmodel))
    new_optimizer.defaults = optimizer.defaults
    new_state_dict = dict()
    new_state_dict['param_groups'] = list()
    for group_id in range(len(optimizer.state_dict()['param_groups'])):
        new_state_dict['param_groups'] .append(optimizer.state_dict()['param_groups'][group_id])
        for param_id in optimizer.state_dict()['param_groups'][group_id]['params']:
            param_name = id2name[param_id]
            param_dict = optimizer.state_dict()['state'][param_id]
            new_param_dict = {}
            if param_name in qmodel.substitutions_dict.keys():
                for feature_name, feature_value in param_dict.items():
                    if type(feature_value) == torch.Tensor:
                        children_dict, _ = qmodel.substitutions_dict[param_name]
                        new_param_name, param_transfo = next(iter(children_dict.items()))
                        if param_transfo is None:
                            new_param_dict[feature_name] = feature_value
                        else:
                            f, inv_f = param_transfo
                            new_param_dict[feature_name] = f(feature_value)
                    else:
                        new_param_dict[feature_name] = feature_value

        temp_state_dict[param_id] = new_param_dict

    new_state_dict['state'] = temp_state_dict
    new_state_dict['param_groups'] = optimizer.state_dict()['param_groups']
    
    new_optimizer.load_state_dict(new_state_dict)

    return new_optimizer