from fmot import fqir
from collections import defaultdict
import numpy as np

def uniquify_names(graph: fqir.GraphProto):
    try:
        arith = graph.subgraphs['ARITH']
    except:
        arith = graph

    name2tensors = defaultdict(set)

    def add_tensor(x: fqir.TensorProto):
        name2tensors[x.name].add(x)

    for node in arith.nodes:
        for x in node.inputs.values():
            add_tensor(x)
        for x in node.outputs:
            add_tensor(x)
    
    for name, tensors in name2tensors.items():
        if len(tensors) > 1:
            for i, t in enumerate(tensors):
                t.name = f'{name}.{i}'
    
    return graph

def limit_biases(graph: fqir.GraphProto):
    """Restrict biases to the symmetric range [-2**(B-1)+1, 2**(B-1)-1]"""
    for node in graph.subgraphs['ARITH'].nodes:
        if node.opname == 'addmm':
            bias = node.inputs['bias']
            if bias.dtype == 'fqint8':
                bw = 8
            else:
                bw = 16
            
            val = bias.value
            if val is not None:
                val = np.clip(val, -2**(bw) + 1, 2**(bw) - 1)
                bias.value = val

def remove_unused_params(graph: fqir.GraphProto):
    """Strips graph of unused parameters"""
    arith = graph.subgraphs['ARITH']
    unused_params = set(arith.parameters)
    
    for node in arith.nodes:
        for inp in node.inputs.values():
            if inp in unused_params:
                unused_params.remove(inp)
    
    for param in unused_params:
        arith.parameters.remove(param)
            
            
    