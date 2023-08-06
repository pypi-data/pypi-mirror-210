"""This module defines functions for tracing torch graphs and writing out fqir"""
from .utils import combine_iterators, getargnames, store_hierarchical_names, \
    get_hierarchical_name, allhaveprotos
import warnings
import copy
import inspect
import logging
import torch

from fmot.fqir import TensorProto, NodeProto, GraphProto, registry_v1, passes
import fmot
import fmot.qat as Q
from fmot.qat.annotated_tensors import copy_annotations
from fmot.nn.conv1d import Conv1dReshaper
from fmot.tracing.tracing_blacklist import TRACING_BLACKLIST
from fmot.tracing.oplinks_v1 import oplinks_v1
from fmot.nn.sequencer import unbind as seq_unbind
from fmot.nn.sequencer import stack as seq_stack
from typing import *

logger = logging.getLogger(__name__)

def dimension_index(dim, dims):
    """Extract the index of dim in dims list

    Raises:
        ValueError: if dim is not found in dims
    """
    try:
        return dims.index(dim)
    except ValueError as err:
        logger.error('Dimension %d not in dimension list', dim)
        raise err

def trace(model, *inputs, batch_dim=None, seq_dim=None):
    """Trace a model and generate FQIR

    Args:
        model (QAT Model): Model to be traced
        inputs: inputs to use to trace the model; as many non-keyword arguments as is necessary
        batch_dim (int): input batch dimension. Default is None
        seq_dim (int): input sequential dimension. If not None, the model will be traced as a
            sequential model
    Returns:
        :class:`fqir.GraphProto`: An FQIR graph representation of the model
    """
    if seq_dim is not None:
        if batch_dim is None:
            batch_dim = 0
        graph, tsrc_dict = trace_sequential_model(model, *inputs, batch_dim=batch_dim, seq_dim=seq_dim)
    else:
        graph, tsrc_dict = trace_feedforward_model(model, *inputs, batch_dim=batch_dim)
    return graph, tsrc_dict

COUNT = 0

def get_count():
    global COUNT
    COUNT += 1
    return COUNT

def reset_count():
    global COUNT
    COUNT = 0

###############################################################
# > GRAPH_MOD_RULES
# >   graph modification rules, a set of forward hook functions.
# >   Do something to the graph whenever a submodule is called.

def register_inputs_immediately(module, graph):
    """Register inputs with the graph immediately (cf. when the node is done executing)

    This needs to be done with the model's top-level module. Tensors without
    protos will be given protos.
    """
    def hook_fn(module, xin):
        for x in combine_iterators(xin, types=torch.Tensor):
            if not hasattr(x, 'proto'):
                x.proto = TensorProto.from_tensor(x, f'%i.{get_count()}')
            graph.add_input(x.proto)
    return module.register_forward_pre_hook(hook_fn)

def register_inputs(module, graph):
    """When this module is called, the inputs will be registered to the graph"""
    def hook_fn(module, xin, xout):
        for x in combine_iterators(xin, types=torch.Tensor):
            if not hasattr(x, 'proto'):
                x.proto = TensorProto.from_tensor(x, f'%i.{get_count()}')
            graph.add_input(x.proto)
    return module.register_forward_hook(hook_fn)

def register_param(module, graph):
    """
    Should only be applied to ParameterQuantizer modules.
    When called, will register parameters with the graph.
    """
    assert isinstance(module, (Q.nn.ParameterQuantizer, fmot.nn.ParameterQuantizer)), (
            'register_param can only take ParameterQuantizer nodes')
    def hook_fn(module, xin, xout):
        xin, = xin
        if not hasattr(xin, 'proto'):
            xin.proto = TensorProto.from_tensor(xout, f'%p.{get_count()}',
                store_value=True)
            graph.add_parameter(xin.proto)
        xout.proto = xin.proto
    return module.register_forward_hook(hook_fn)

def register_node(module, graph, tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]]=None):
    """Register a forward hook to add a node to the computational graph if the node is a leaf"""
    hname = get_hierarchical_name(module)
    module.traced = False
    def hook_fn(module, xin, xout):
        # Get flat list of inputs and outputs
        xin_c = combine_iterators(xin, types=torch.Tensor)
        xout_c = combine_iterators(xout, types=torch.Tensor)
        if not allhaveprotos(xin_c):
            raise ValueError('Inputs to self.{} were not annotated'.format(hname))

        # Add a node to the graph if any of the outputs are not annotated with
        # a proto (this indicates that we've reached a leaf module)
        if not allhaveprotos(xout_c):
            module.traced = True

            # Get constants for the node
            if hasattr(module, '_get_constants'):
                constants = module._get_constants(*xin)
            else:
                constants = {}

            # Create TensorProtos for all of the outputs
            for idx, x in enumerate(xout_c):
                if not hasattr(x, 'proto'):
                    x.proto = TensorProto.from_tensor(x, f'%x.{get_count()}')
                    if tsrc_dict is not None:
                        tsrc_dict[x.proto.name] = (module, idx)

            # Get source code reference
            sourceref = ''
            if hasattr(module, '_sourceref'):
                sourceref = module._sourceref

            # Construct an input operand dictionary
            argnames = getargnames(module)
            inputs = {k : x.proto for k, x in zip(argnames, xin_c)}

            # Get operator name and link
            if type(module) in oplinks_v1:
                optype = oplinks_v1[type(module)]
            else:
                warnings.warn(f'Oplink not found for leaf module of type {type(module)}')
                optype = None

            # Construct node and add to graph:
            node = NodeProto(
                name=hname,
                optype=optype,
                inputs=inputs,
                outputs=[x.proto for x in xout_c],
                constants=constants,
                sourceref=sourceref)
            graph.add_node(node)

    return module.register_forward_hook(hook_fn)

def register_outputs(module, graph, dequant_graph=None):
    """Register forward hook function to add the outputs to the graph

    This hook should be applied *after* nodes have been registered
    """
    hname = get_hierarchical_name(module)
    def hook_fn(module, xin, xout):
        for x in combine_iterators(xout, types=torch.Tensor):
            assert hasattr(x, 'proto')
            graph.add_output(x.proto)
            if dequant_graph is not None and hasattr(x, 'quanta'):
                proto = TensorProto.from_tensor(x, f'%x.{get_count()}')
                proto.dtype = 'float'
                optype = registry_v1['dequantize']
                constants = {'quanta': int(x.quanta)}
                node = NodeProto(
                    name=hname,
                    optype=optype,
                    inputs={'x': x.proto},
                    outputs=[proto],
                    constants=constants)
                dequant_graph.add_node(node)
                dequant_graph.add_input(x.proto)
                dequant_graph.add_output(proto)
                x.proto = proto
    return module.register_forward_hook(hook_fn)

def attach_subgraph(module, graph, subgraph, subgraph_name,
                      register_inputs=True, register_outputs=True):
    """Register forward hook function to add a subgraph to the graph

    Subgraph is also registered as a node for execution purposes
    """
    hname = get_hierarchical_name(module)
    def hook_fn(module, xin, xout):
        xin_c = combine_iterators(xin, types=torch.Tensor)
        xout_c = combine_iterators(xout, types=torch.Tensor)

        if register_inputs:
            for x in xin_c:
                subgraph.add_input(x.proto)
        if register_outputs:
            for x in xout_c:
                if not hasattr(x, 'proto'):
                    raise ValueError(
                        f'Output from {module} does not have a proto. Shape: {x.shape} \n{subgraph}\n{x}')
                subgraph.add_output(x.proto)

        sig_dict = {f'x{i+1}': x.proto for i, x in enumerate(combine_iterators(xin_c))}

        node = NodeProto(
            name=hname,
            optype=None,
            inputs=sig_dict if register_inputs else {},
            outputs=[x.proto for x in xout_c] if register_outputs else [],
            subgraph=subgraph)
        graph.add_node(node)
        graph.add_subgraph(subgraph_name, subgraph)
    return module.register_forward_hook(hook_fn)

def register_zeros_init(module, graph):
    hname = get_hierarchical_name(module)
    def hook_fn(module, xin, xout):
        xout_c = combine_iterators(xout, types=torch.Tensor)
        for x in xout_c:
            x.proto = TensorProto.from_tensor(x, f'%x.{get_count()}')
            node = NodeProto(
                name=hname,
                optype=registry_v1['zeros'],
                inputs={},
                outputs=[x.proto],
                constants={'shape': tuple(x.shape)})
            graph.add_node(node)
    return module.register_forward_hook(hook_fn)

def register_state_assign(module, graph):
    hname = get_hierarchical_name(module)
    def hook_fn(module, xin, output):
        assert isinstance(module, fmot.nn.Sequencer)
        state_in = module.prev_state
        state_out = module.state
        if isinstance(output, (list, tuple)):
            out_proto = output[0].proto
        else:
            out_proto = output.proto
        copied_output = None

        for s_in, s_out in zip(state_in, state_out):
            if s_in.proto == out_proto:
                new_out_proto = TensorProto.from_tensor(output[0], f'%x.{get_count()}')
                copy_node = NodeProto(
                    name=hname,
                    optype=registry_v1['copy'],
                    inputs={'x': out_proto},
                    outputs=[new_out_proto],
                    constants=None)
                copied_output = copy.deepcopy(output[0])
                copied_output = copy_annotations(output[0], copied_output)
                copied_output.proto = new_out_proto
                out_proto = new_out_proto
                graph.add_node(copy_node)
            node = NodeProto(
                name=hname,
                optype=registry_v1['assign'],
                inputs={'y': s_in.proto, 'x': s_out.proto},
                outputs=[],
                constants=None)
            graph.add_node(node)
        if copied_output is not None:
            ret = (copied_output, output[1])
        else:
            ret = None
        return ret
    return module.register_forward_hook(hook_fn)

def clean_params(model):
    for p in model.parameters():
        if hasattr(p, 'proto'):
            delattr(p, 'proto')

############################
# > TRACE FUNCTIONS
@torch.no_grad()
def trace_feedforward_model(model, *inputs, batch_dim=0, seq_dim=1,
    remove_batchdim=True):
    """Trace a feedforward model (i.e. a model without any sequential operators)

    Args:
        model (:class:`torch.nn.Module`): The model to be traced (should be quantized beforehand)
        inputs (:class:`torch.Tensor`): Input(s) to use to trace the model
        batchdim (int, optional): Batch dimension to remove from computational graph
    """
    reset_count()
    store_hierarchical_names(model)

    #####################################
    # > SET RULES FOR GRAPH CONSTRUCTION
    graph = GraphProto(name='MAIN')
    # Register inputs and outputs
    dequant_graph = GraphProto(name='DEQUANT')
    handles = [register_inputs_immediately(model, graph), \
        register_outputs(model, graph, dequant_graph=dequant_graph),
        attach_subgraph(model, graph, dequant_graph, 'DEQUANT',
            register_inputs=False, register_outputs=False)]
    
    # construct a tensor-source-dict for tracing
    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = {}

    # Create a quant/dequant subgraphs if the root node is a QuantWrapper
    if isinstance(model, Q.nn.QuantWrapper):
        # Create and attach a quant subgraph
        qgraph = GraphProto(name='QUANT')
        handles += [attach_subgraph(model.quantizers, graph, qgraph, 'QUANT')]
        # Register quantizers as nodes
        handles += [register_node(m, qgraph, tsrc_dict) for m in model.quantizers.quantizers]

        amodel = model.model
    else:
        amodel = model
    # Create and attach subgraph for arithmetic operations
    agraph = GraphProto(name='ARITH')
    handles += [attach_subgraph(amodel, graph, agraph, 'ARITH')]
    # Register non-blacklisted arithmetic modules and parameters
    for m in list(amodel.modules()) + [amodel]:
        if type(m) not in TRACING_BLACKLIST:
            handles += [register_node(m, agraph, tsrc_dict)]
        if isinstance(m, Q.nn.ParameterQuantizer):
            handles += [register_param(m, agraph)]

    ################################################
    # > CONSTRUCT GRAPH -- just call on test input
    if not(hasattr(inputs[0], 'dimensions')):
        input_dimensions = ['F', 'F', 'F']
        input_dimensions[batch_dim] = 'B'
        input_dimensions[seq_dim] = 'T'
        for inp in inputs:
            inp.dimensions = input_dimensions
    outputs = model(*inputs)

    # for input in inputs:
    #     input.dimensions = None
    # outputs = model(*inputs)
    ####################
    # > REMOVE HANDLES
    for handle in handles:
        handle.remove()
    reset_count()
    clean_params(model)

    if remove_batchdim:
        graph = passes.remove_batchdim(graph, dim=batch_dim)

    passes.run_passes(graph)
    return graph, tsrc_dict

def prep_model_for_streaming(model, xin):
    """Set model into streaming mode"""
    for module in [model] + list(model.modules()):
        if isinstance(module, fmot.nn.Sequencer):
            # module.state = module.get_init_state(xin)
            module._streaming = True
        if isinstance(module, Q.nn.Dropout):
            module.training = False
    return model

def clean_model_from_streaming(model):
    """Reset model from streaming mode"""
    for module in [model] + list(model.modules()):
        if isinstance(module, fmot.nn.Sequencer):
            module.state = None
            module.prev_state = None
            module._streaming = False
        if hasattr(module, 'tracing_mode'):
            module.tracing_mode = False
    return model

@torch.no_grad()
def trace_sequential_model(model, *inputs, batch_dim=0, seq_dim=-1):
    """Trace a sequential model and generate fqir"""
    reset_count()
    store_hierarchical_names(model)

    #####################################
    # > SET RULES FOR GRAPH CONSTRUCTION
    main = GraphProto(name='MAIN')
    init = GraphProto(name='INIT')
    quant = GraphProto(name='QUANT')
    dequant = GraphProto(name='DEQUANT')
    arith = GraphProto(name='ARITH')

    ##########
    # > Construct a tensor-source dictionary for debugging
    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = {}

    ### MAIN LEVEL

    # Register inputs and outputs to MAIN
    handles = []
    handles += [register_inputs_immediately(model, main)]
    handles += [register_outputs(model, main, dequant_graph=dequant)]

    # Attach INIT to MAIN
    handles += [attach_subgraph(model, main, init, 'INIT',
        register_inputs=False, register_outputs=False)]

    # Attach dequant to MAIN
    handles += [attach_subgraph(model, main, dequant, 'DEQUANT',
            register_inputs=False, register_outputs=False)]

    ### INIT LEVEL
    # register state init to INIT
    for m in model.modules():
        if isinstance(m, Q.nn.StateInitializer):
            handles += [register_zeros_init(m, init)]

    ### LOOP LEVEL
    # QUANT
    handles += [attach_subgraph(model.quantizers, main, quant, 'QUANT')]
    handles += [register_node(m, quant, tsrc_dict) for m in model.quantizers.quantizers]

    # ARITH
    amodel = model.model
    handles += [attach_subgraph(amodel, main, arith, 'ARITH')]
    for m in amodel.modules():
        if type(m) not in TRACING_BLACKLIST:
            handles += [register_node(m, arith, tsrc_dict)]
        if isinstance(m, fmot.nn.Sequencer):
            handles += [register_state_assign(m, arith)]
        if isinstance(m, Q.nn.ParameterQuantizer):
            handles += [register_param(m, arith)]

    ### IN and OUT dimensions
    input_dimensions = ['F', 'F', 'F']
    input_dimensions[batch_dim] = 'B'
    input_dimensions[seq_dim] = 'T'

    ################################################
    # > CONSTRUCT GRAPH -- just call on test input
    tracing_inputs = []
    for inp in inputs:
        x = prepare_for_tracing(model, inp, main)
        if x.dim() == 3:
            if dimension_index('T', input_dimensions) == 2:
                y = x[:,:,0]
                y.dimensions = input_dimensions[:-1]
            else:
                if dimension_index('B', input_dimensions) == 0:
                    y = x[:, 0]
                    y.dimensions = ['B', 'F']
                else:
                    y = x[0]
                    y.dimensions = ['F', 'B']
        else:
            y = x
        x.dimensions = input_dimensions
        tracing_inputs.append(y)

    model = prep_model_for_streaming(model, inputs[0])
    model(*tracing_inputs)
    model = clean_model_from_streaming(model)

    ####################
    # > REMOVE HANDLES
    for handle in handles:
        handle.remove()

    reset_count()
    if 0 <= seq_dim < batch_dim:
        batch_dim -= 1
    main = passes.remove_batchdim(main, dim=batch_dim)
    passes.run_passes(main)
    clean_params(model)

    if batch_dim == 0 and seq_dim == 1:
        main.unbind_dim = 0
    elif batch_dim == 1 and seq_dim == 0:
        main.unbind_dim = 0
    elif seq_dim in (2, -1):
        main.unbind_dim = -1
    return main, tsrc_dict

def prepare_for_tracing(model, x, main_graph):
    for submodule in model.modules():
        if isinstance(submodule, Conv1dReshaper):
            x = submodule.forward(x)
            submodule.tracing_mode = True
            main_graph.register_reshaper(submodule.to_numpy())
        if isinstance(submodule, Q.nn.atomics.FTranspose):
            submodule.tracing_mode = True
    return x

def hook_mixed(model, graph, init_graph, tsrc_dict=None):
    handles = []
    _hook_ff(model, graph, init_graph, handles, tsrc_dict)
    return handles

def _hook_ff(module, graph, init_graph, handles, 
             tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]]=None):
    for m in module.children():
        if isinstance(m, fmot.nn.Sequencer):
            handles += _hook_seq(m, graph, init_graph, tsrc_dict)
        elif type(m) not in TRACING_BLACKLIST:
            handles += [register_node(m, graph, tsrc_dict)]
            _hook_ff(m, graph, init_graph, handles)
        if isinstance(m, Q.nn.ParameterQuantizer):
            handles += [register_param(m, graph)]

def _hook_seq(module, graph, init_graph, 
              tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]]=None):
    assert isinstance(module, fmot.nn.Sequencer)

    internal_handles = []
    external_handles = []

    for m in module.modules():
        if m != module and type(m) not in TRACING_BLACKLIST:
            internal_handles += [register_node(m, register_node(m, graph, tsrc_dict), tsrc_dict)]
        elif isinstance(m, Q.nn.StateInitializer):
            internal_handles += [register_zeros_init(m, init_graph)]
        elif isinstance(m, Q.nn.ParameterQuantizer):
            internal_handles += [register_param(m, graph)]
    internal_handles += [register_state_assign(module, graph)]

    def seq_prehook_fn(seq, xin):
        """
        - Enables streaming mode 
        - Takes just first input from sequence
        - Sets SEQ_LEN to the sequence length
        """
        unbind_dim = seq.seq_dim
        seq.set_streaming(True)
        return_state = False
        if isinstance(xin, tuple):
            if len(xin) == 2:
                return_state = True
                x, state = xin
            else:
                x,  = xin
        else:
            x = xin
        seq.SEQ_LEN = x.shape[unbind_dim]

        new_x = seq_unbind(x, unbind_dim)[0]
        new_x.proto = x.proto

        if return_state:
            return new_x, state
        else:
            return new_x

    def seq_posthook_fn(seq, xin, xout):
        """
        - Disables streaming mode
        - Removes internal hooks
        - Repeats output SEQ_LEN times; 
        """
        unbind_dim = seq.seq_dim
        seq.set_streaming(False)
        output, final_state = xout
        new_output = seq_stack([output]*seq.SEQ_LEN, unbind_dim)
        new_output.proto = output.proto
        del seq.SEQ_LEN

        for handle in internal_handles:
            handle.remove()

        return new_output, final_state

    external_handles += [module.register_forward_pre_hook(seq_prehook_fn)]
    external_handles += [module.register_forward_hook(seq_posthook_fn)]
    return external_handles

@torch.no_grad()
def trace_hybrid(model, *inputs, named_dims=None, batch_dim=0, seq_dim=-1, remove_dims=True):
    """Trace a sequential model and generate fqir"""
    reset_count()
    store_hierarchical_names(model)

    #####################################
    # > SET RULES FOR GRAPH CONSTRUCTION
    main = GraphProto(name='MAIN')
    init = GraphProto(name='INIT')
    quant = GraphProto(name='QUANT')
    dequant = GraphProto(name='DEQUANT')
    arith = GraphProto(name='ARITH')

    tsrc_dict: Dict[str, Tuple[torch.nn.Module, int]] = {}

    ### MAIN LEVEL

    # Register inputs and outputs to MAIN
    handles = []
    handles += [register_inputs_immediately(model, main)]
    handles += [register_outputs(model, main, dequant_graph=dequant)]

    # Attach INIT to MAIN
    handles += [attach_subgraph(model, main, init, 'INIT',
        register_inputs=False, register_outputs=False)]

    # Attach dequant to MAIN
    handles += [attach_subgraph(model, main, dequant, 'DEQUANT',
            register_inputs=False, register_outputs=False)]

    ### LOOP LEVEL
    # QUANT
    handles += [attach_subgraph(model.quantizers, main, quant, 'QUANT')]
    handles += [register_node(m, quant, tsrc_dict) for m in model.quantizers.quantizers]

    # ARITH
    amodel = model.model
    handles += [attach_subgraph(amodel, main, arith, 'ARITH')]
    handles += hook_mixed(amodel, arith, init, tsrc_dict)

    ### IN and OUT dimensions
    if named_dims is not None:
        input_dimensions = named_dims
    else:
        if seq_dim is not None:
            input_dimensions = ['F', 'F', 'F']
        else:
            input_dimensions = ['F', 'F']
        input_dimensions[batch_dim] = 'B'
        if seq_dim is not None:
            input_dimensions[seq_dim] = 'T'

    ################################################
    # > CONSTRUCT GRAPH -- just call on test input
    tracing_inputs = []
    for x in inputs:
        x.dimensions = input_dimensions
        tracing_inputs.append(x)

    model(*tracing_inputs)

    ####################
    # > REMOVE HANDLES
    for handle in handles:
        try:
            handle.remove()
        except Exception as e:
            print(handle)
            raise e
    clean_params(model)

    if batch_dim == 0 and seq_dim == 1:
        main.unbind_dim = 0
    elif batch_dim == 1 and seq_dim == 0:
        main.unbind_dim = 0
    elif seq_dim in (2, -1):
        main.unbind_dim = -1

    reset_count()
    if remove_dims:
        passes.remove_named_dims(main, ['B', 'T', 'H', 'W'])

    passes.run_passes(main)
    return main