import torch
from torch import nn
from typing import List, Tuple
from torch import Tensor
from fmot.nn import Sequencer

class BasicRNN(Sequencer):
    def __init__(self, input_size, hidden_size, batch_first=True):
        # state_shapes is a list of hidden-state shapes
        state_shapes = [[hidden_size]]
        batch_dim = 0 if batch_first else 1
        seq_dim = 1 if batch_first else 0
        super().__init__(state_shapes, batch_dim=batch_dim, seq_dim=seq_dim)
        
        self.linear_ih = nn.Linear(input_size, hidden_size)
        self.linear_hh = nn.Linear(hidden_size, hidden_size)
        self.relu = nn.ReLU()
    
    @torch.jit.export
    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        h, = state
        n = self.linear_ih(x_t) + self.linear_hh(h)
        h = torch.tanh(n)
        h = self.relu(h)
        
        return h, [h]
        
# This is a dummy class used for testing purposes
class SuperBasic(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        
        self.layer = BasicRNN(input_size, hidden_size)
    
    @torch.jit.export
    def forward(self, x):
        if x.sum(0) > 0:
            return x, [x]
        #x = torch.tanh(x)
        return self.layer(x)

class SuperStructure(nn.Module):
    def __init__(self):
        super().__init__()

class ProtectedModule(nn.Module):
    def __init__(self):
        super().__init__()
        
SUPERSTRUCT_DIC = {
    SuperBasic,
    SuperStructure,
}

