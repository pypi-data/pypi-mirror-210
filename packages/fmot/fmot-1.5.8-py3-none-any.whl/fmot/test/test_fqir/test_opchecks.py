import pytest
import numpy as np
from fmot import fqir

def test_opchecks():
    """Test that OpTypes are raising exceptions when appropriate"""
    # define the input tensors
    x = fqir.TensorProto("x", int, [2])
    y = fqir.TensorProto("y", int, [2])
    # define the output tensor
    z = fqir.TensorProto("z", int, [2])
    
    # put the tensors and op into a graph
    graph = fqir.GraphProto()
    graph.add_input(x)
    graph.add_input(y)
    with pytest.raises(ValueError): # check that mismatches of input are caught
        graph.add_node(fqir.NodeProto(
            name="op", optype=fqir.registry_v1["vvadd"],
            inputs={"notx":x, "noty":y}, outputs=[z],
            constants={"shamt_x":0, "shamt_y":0, "shamt_bwred":0, "bw":8, "bw_x":8, "bw_y":8}))
    with pytest.raises(ValueError): # check that mismatches of constants are caught
        graph.add_node(fqir.NodeProto(
            name="op", optype=fqir.registry_v1["vvadd"],
            inputs={"x":x, "y":y}, outputs=[z],
            constants={"not_shamt_x":0, "not_shamt_y":0, "not_shamt_bwred":0, "not_bw":8}))
    graph.add_node(fqir.NodeProto( # should pass
        name="op", optype=fqir.registry_v1["vvadd"],
        inputs={"x":x, "y":y}, outputs=[z],
        constants={"shamt_x":0, "shamt_y":0, "shamt_bwred":0, "bw":8, "bw_x":8, "bw_y":8}))
    graph.add_output(z)
    
    # create some values for the inputs
    x_val = np.array([1, 2])
    y_val = np.array([1, 2])
    # pass the inputs through the graph and generate the output
    z_val = graph.run(x_val, y_val)
    np.testing.assert_equal(z_val, x_val+y_val)

if __name__ == "__main__":
    test_opchecks()
