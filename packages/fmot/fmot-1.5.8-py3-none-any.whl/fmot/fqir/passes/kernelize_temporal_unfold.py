from fmot import fqir

def kernelize_temporal_unfold(graph: fqir.GraphProto):
    """
    Adds init node for temporal unfold, and utilizes a buffer variable.
    """

    arith = graph.subgraphs["ARITH"]
    if 'INIT' in graph.subgraphs:
        no_init = False
        init = graph.subgraphs['INIT']
    else:
        no_init = True
        init = fqir.GraphProto(name='INIT')

    replace_dict = {}

    for node in arith.nodes:
        if node.opname == "temporal_unfold_unkernelized":
            new_node = get_unfold(node)
            replace_dict[node] = new_node

    if len(replace_dict) > 0:
        if no_init:
            init_node = fqir.NodeProto(
                name='INIT',
                optype=None,
                inputs={},
                outputs=[],
                subgraph=init
            )
            graph.add_node(init_node)
            graph.add_subgraph('INIT', init)
        nodes = []
        for orig in arith.nodes:
            if orig in replace_dict:
                new = replace_dict[orig]
                nodes.append(new)
                
                buff = new.inputs['buffer']
                zero_node = fqir.NodeProto(
                    name=f'init_{buff.name}',
                    optype=fqir.registry_v1['zeros'],
                    inputs={},
                    outputs=[buff],
                    constants={'shape': buff.shape})
                init.add_node(zero_node)
            else:
                nodes.append(orig)
        arith.nodes = nodes
    
    return graph

def get_unfold(node):
    buffer_length = node.constants["buffer_length"]
    x = node.inputs['x']
    in_length = x.shape[0]
    buff_size = in_length * buffer_length

    buffer = fqir.TensorProto(name=f'buffer_{x.name}', dtype=x.dtype, 
        shape=[buff_size])
    node = fqir.NodeProto(name=node.name, optype=fqir.registry_v1['temporal_unfold'],
        inputs={'x': x, 'buffer': buffer},
        constants=node.constants, outputs=node.outputs, sourceref=node.sourceref)
    
    return node
    