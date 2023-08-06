

def get_all_tensors(graph):
    """
    Returns a set of all TensorProtos in a GraphProto

    Args:
        graph (GraphProto)
    Returns:
        Set[TensorProto]: A set of all tensors in the graph
    """
    tprotos = set(graph.inputs)
    tprotos.update(set(graph.parameters))
    for node in graph.nodes:
        tprotos.update(set(node.outputs))
        if node.subgraph is not None:
            tprotos.update(get_all_tensors(node.subgraph))
    return tprotos

def isroot(tensor):
    return len(tensor.parents) == 0

def isleaf(tensor):
    return len(tensor.children) == 0

def get_root_parents(tensor):
    roots = set()
    for parent in tensor.parents:
        if isroot(parent):
            roots.add(parent)
        else:
            roots.update(get_root_parents(parent))
    return roots

def isinput(tensor, graph):
    return tensor in graph.inputs

def isoutput(tensor, graph):
    return tensor in graph.outputs

def isparam(tensor, graph, recurse=True):
    ip = tensor in graph.parameters
    if recurse:
        for subgraph in graph.subgraphs.values():
            ip = ip or isparam(tensor, subgraph, recurse=True)
    return ip

