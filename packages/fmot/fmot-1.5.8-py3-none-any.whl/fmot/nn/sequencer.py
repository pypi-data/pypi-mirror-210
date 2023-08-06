import torch
import math
import warnings
from torch import Tensor, nn
from typing import List, Tuple, Optional
from torch.jit import Final
from fmot.qat import annotated_tensors as anno
from fmot.qat.control import cache_parameters, decache_parameters

def unbind(x, dim):
    y = torch.unbind(x, dim)
    if not hasattr(x, 'annotated'):
        return y
    else:
        unbind_x = []
        for yy in y:
            z = anno.copy_annotations(x, yy)
            try:
                dimensions = list(x.dimensions)
                dimensions.pop(dim)
                anno.set_dim_annotations(dimensions, z)
            except:
                warnings.warn('Input dimensions are missing: ' +
                              'dimension information has not been propagated correctly')
            unbind_x.append(z)
        return unbind_x

def cat(x, dim):
    x0 = x[0]
    y = torch.cat(x, dim)
    if not hasattr(x[0], 'annotated'):
        return y
    else:
        return anno.copy_annotations(x0, y)

def stack(x, dim):
    x0 = x[0]
    y = torch.stack(x, dim)
    if not hasattr(x[0], 'annotated'):
        return y
    else:
        z = anno.copy_annotations(x0, y)
        try:
            if dim < 0:
                insert_dim = len(x0.dimensions) + dim + 1
            else:
                insert_dim = dim
            z.dimensions.insert(insert_dim, 'T')
        except:
            warnings.warn('Input dimensions are missing: ' +
                          'dimension information has not been propagated correctly')
        return z

def chunk(x, chunks, dim):
    y = torch.chunk(x, chunks, dim)
    if not hasattr(x, 'annotated'):
        return y
    else:
        return [anno.copy_annotations(x, yy) for yy in y]

class StateInitializer(nn.Module):
    def __init__(self, state_shapes, batch_dim):
        super().__init__()
        self.state_shapes = state_shapes
        self.batch_dim = batch_dim

    @torch.jit.ignore
    def forward(self, x) -> List[Tensor]:
        B = x.shape[self.batch_dim]
        return [torch.zeros(B, *shape, device=x.device) for shape in self.state_shapes]

    @torch.jit.ignore
    def observe_state(self, state):
        pass

    @torch.jit.ignore
    def quantize_state(self, state):
        return state

class Sequencer(nn.Module):
    state: Final[Optional[List[Tensor]]]
    def __init__(self, state_shapes, batch_dim=0, seq_dim=1,
                 return_hidden_state=True):
        super().__init__()
        self.seq_dim = seq_dim
        self.batch_dim = batch_dim
        self.state_initializer = StateInitializer(state_shapes, batch_dim)
        self.state_shapes = state_shapes
        self._streaming = False
        self.return_hidden_state = return_hidden_state
        self.state = None

    def weight_init(self):
        k = math.sqrt(1/self.hidden_size)
        for name, param in self.named_parameters():
            torch.nn.init.uniform_(param, -k, k)

    @torch.jit.ignore
    def get_init_state(self, x) -> List[Tensor]:
        return self.state_initializer(x)

    def forward(self, x: Tensor, state: Optional[List[Tensor]]=None)->Tuple[Tensor,List[Tensor]]:
        if self._streaming:
            return self._forward_streaming_internal_state(x)
        else:
            if state is None:
                state = self.get_init_state(x)
            return self._forward_training(x, state)

    @torch.jit.ignore
    def _forward_training(self, x: Tensor, state: List[Tensor]) -> Tuple[Tensor,List[Tensor]]:
        """
        Optionally overwrite this with base looped equation
        """
        cache_parameters(self)
        output = []
        for x_t in unbind(x, self.seq_dim):
            out, state = self.step(x_t, state)
            self.state_initializer.observe_state(state)
            state = self.state_initializer.quantize_state(state)
            output.append(out)
        decache_parameters(self)
        if self.return_hidden_state:
            return stack(output, self.seq_dim), state
        else:
            # Rk: in this case signature is Tensor, but Union is not supported
            return stack(output, self.seq_dim)

    @torch.jit.ignore
    def _forward_streaming_internal_state(self, x) -> Tuple[Tensor,List[Tensor]]:
        if self.state == None:
            self.batch_dim = 0
            self.state = self.get_init_state(x)
        self.prev_state = self.state
        out, self.state = self.step(x, self.state)
        self.state = self.state_initializer.quantize_state(self.state)
        if self.return_hidden_state:
            return out, self.state
        else:
            return out

    def step(self, x_t: Tensor, state: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        """
        Overwrite this with base update equation. Annotations are required (for now)...
        """
        raise NotImplementedError
        return out_t, state

    def set_streaming(self, stream=True):
        if stream:
            self._streaming = True
        else:
            self._streaming = False
            self.state = None
            self.prev_state = None

    def to(self, device, *args, **kwargs):
        super().to(device=device, *args, **kwargs)
        if state is not None:
            state = [x.to(device) for x in state]
            print('state to device')

