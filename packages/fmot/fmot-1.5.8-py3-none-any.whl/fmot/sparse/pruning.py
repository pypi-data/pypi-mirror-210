import torch
import torch.nn.utils.prune as prune
import torch.nn.functional as F
from ..utils.conv1d_utils import flatten_conv_matrix, inv_flatten_conv_matrix


class PencilPruning(prune.BasePruningMethod):
    ''' This is a Local Pruning class made to prune
        a weight matrix in a pencil-sparse manner (along the column dimension).
        
    '''
    PRUNING_TYPE = "global"

    def __init__(self, amount, pencil_size):
        """

        Args:
            amount (float): percent of the model to prune out
            pencil_size (int): size of the pencils
        """
        super().__init__()
        self.amount = amount
        self.pencil_size = pencil_size

    def compute_mask(self, tensor, default_mask):
        # Rk: if we take 30% and the matrix has 3 pencils -> we round up to 33%
        
        # Verify that the tensor is 2D
        assert(tensor.dim() == 2)
            
        nrows, ncols = tensor.shape
        padding = (self.pencil_size - (nrows%self.pencil_size))%self.pencil_size
        mask = F.pad(default_mask, (0,0,0,padding))

        # We slice the tensor h*w in x*pencil_size, slicing is done column-wise
        # We want to collapse on the last axis of this vector, this is shallow copy. Verify flatten
        # Thus we get the mean values per pencil-slice
        padded_tensor = F.pad(tensor, (0,0,0,padding))
        sliced_tensor = padded_tensor.t().flatten().view(-1, self.pencil_size)
        pencil_shrunk_tensor = torch.mean(torch.abs(sliced_tensor),-1).flatten()

        tensor_size = pencil_shrunk_tensor.nelement()
        nparams_toprune = prune._compute_nparams_toprune(self.amount, tensor_size)
        # This should raise an error if the number of units to prune is larger
        # than the number of units in the tensor
        prune._validate_pruning_amount(nparams_toprune, tensor_size)  
    
        if nparams_toprune != 0:  # k=0 not supported
            bottom_k = torch.topk(
                pencil_shrunk_tensor.flatten(), k=nparams_toprune, largest=False
            )
            pencil_indices_toprune = bottom_k.indices
        else:
            pencil_indices_toprune = []
        
        # The indices to prune are the indices of the pencil once the
        # matrix is pencil-flat, so we don't have to 'expand' the mask
        mask = mask.t().flatten().view(-1, self.pencil_size)
        mask[pencil_indices_toprune,:] = 0
        
        #Because of the padding we need to cut off the additional rows
        mask = mask.view(padded_tensor.t().shape).t()
        mask = mask[:nrows,:ncols]
        
        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(PencilPruning, cls).apply(module, name, amount=amount, pencil_size=pencil_size)


def _pencil_linear_pruning(module, name, amount, pencil_size=8):
    PencilPruning.apply(module, name, amount, pencil_size)
    
    return module


class Conv1dPencilPruning(PencilPruning):
    ''' This is a Local Pruning class made to prune
        a weight matrix in a pencil-sparse manner
        
    '''
    PRUNING_TYPE = "global"

    def compute_mask(self, tensor, default_mask):
        assert(tensor.dim() == 3)
        
        out_channels, in_channels, kernel_size = tensor.shape
        flatten_tensor = flatten_conv_matrix(tensor, out_channels, in_channels, kernel_size)
        flatten_mask = flatten_conv_matrix(default_mask, out_channels, in_channels, kernel_size)
        
        # Apply the new mask
        flatten_mask = super().compute_mask(flatten_tensor, flatten_mask)
        
        mask = inv_flatten_conv_matrix(flatten_mask, out_channels, in_channels, kernel_size)
        
        return mask.contiguous()


    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(Conv1dPencilPruning, cls).apply(module, name, amount=amount, pencil_size=pencil_size)


def _pencil_conv1d_pruning(module, name, amount, pencil_size=8):
    Conv1dPencilPruning.apply(module, name, amount, pencil_size)
    
    return module


class Conv2dPencilPruning(prune.BasePruningMethod):
    ''' This is a Local Pruning class made to prune
        a weight matrix in a pencil-sparse manner (along the column dimension).

    '''
    PRUNING_TYPE = "global"

    def __init__(self, amount, pencil_size):
        """

        Args:
            amount (float): percent of the model to prune out
            pencil_size (int): size of the pencils
        """
        super().__init__()
        self.amount = amount
        self.pencil_size = pencil_size

    def compute_mask(self, tensor, default_mask):
        # Rk: if we take 30% and the matrix has 3 pencils -> we round up to 33%

        assert (tensor.dim() == 4)

        o, i, kw, kh = tensor.shape
        padding = (self.pencil_size - (i % self.pencil_size)) % self.pencil_size
        mask = F.pad(default_mask, (0, 0, 0, 0, 0, padding))

        # We slice the tensor h*w in x*pencil_size, slicing is done column-wise
        # We want to collapse on the last axis of this vector, this is shallow copy. Verify flatten
        # Thus we get the mean values per pencil-slice
        padded_tensor = F.pad(tensor, (0, 0, 0, 0, 0, padding))
        sliced_tensor = padded_tensor.permute(0,2,3,1).flatten().view(-1, self.pencil_size)
        pencil_shrunk_tensor = torch.mean(torch.abs(sliced_tensor), -1).flatten()

        tensor_size = pencil_shrunk_tensor.nelement()
        nparams_toprune = prune._compute_nparams_toprune(self.amount, tensor_size)
        # This should raise an error if the number of units to prune is larger
        # than the number of units in the tensor
        prune._validate_pruning_amount(nparams_toprune, tensor_size)

        if nparams_toprune != 0:  # k=0 not supported
            bottom_k = torch.topk(
                pencil_shrunk_tensor.flatten(), k=nparams_toprune, largest=False
            )
            pencil_indices_toprune = bottom_k.indices
        else:
            pencil_indices_toprune = []

        # The indices to prune are the indices of the pencil once the
        # matrix is pencil-flat, so we don't have to 'expand' the mask
        mask = mask.permute(0,3,2,1).flatten().view(-1, self.pencil_size)
        mask[pencil_indices_toprune, :] = 0

        # Because of the padding we need to cut off the additional rows
        mask = mask.view(o, kw, kh, i+padding).permute(0,3,1,2)
        mask = mask[:, :i, :, :]

        return mask.contiguous()

    @classmethod
    def apply(cls, module, name, amount, pencil_size):
        return super(Conv2dPencilPruning, cls).apply(module, name, amount=amount, pencil_size=pencil_size)


def _pencil_conv2d_pruning(module, name, amount, pencil_size=8):
    Conv2dPencilPruning.apply(module, name, amount, pencil_size)

    return module


def pencil_pruning(module, name, amount, pencil_size=8):
    param = getattr(module, name)
    if param.dim() == 2:
        _pencil_linear_pruning(module, name, amount, pencil_size)
    elif param.dim() == 3:
        _pencil_conv1d_pruning(module, name, amount, pencil_size)
    elif param.dim() == 4:
        _pencil_conv2d_pruning(module, name, amount, pencil_size)
    else:
        raise Exception('Femtostack does not support pruning ' +
                        'for parameters of dimension {}'.format(param.dim()))
