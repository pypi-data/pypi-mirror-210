"""Defines the FQIR Atomic Operator Registry V1"""
import numpy as np
from .optype_base import OpType, OpRegistry
from .node_base import NodeReprSettings
import math
from .opcounters import VVCounter, VCounter, ConvCounter, \
    MatmulCounter, VLUTCounter, NullCounter, CopyCounter, ShiftCounter, ReductionCounter

ST_LD_pessimism = 0.5
B_ACC_ENTRY = 32

def lshift(x, shamt):
    """Performs a left-shift on x

    Args:
        x (:obj:`numpy.ndarray`): Integer numpy array
        shamt (int): Shift amount (can be negative for right shift)
    """
    if shamt >= 0:
        return x << shamt
    else:
        return x >> -shamt

def truncate(x, bw):
    """Truncate an integer tensor to a certain bitwidth"""
    vmin = -2**(bw-1)
    vmax = 2**(bw-1)-1
    return np.clip(x, vmin, vmax)

def _add(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x=None, bw_y=None):
    """Add two vectors together

    Args:
        x: First addend
        y: Second addend
        shamt_x: Left-shift-amount for x before adding
        shamt_y: Left-shift-amount for y before adding
        shamt_bwred: Left-shift-amount for resultant
        bw: Bitwidth of output
        bw_x: bitwidth of x
        bw_y: bitwidth of y
    """
    assert not (shamt_x != 0 and shamt_y != 0), "x or y can have nonzero shamt but not both"
    if not ((bw_x is None) or (bw_y is None)):
        bw_operand = max(bw_x, bw_y)
    else:
        bw_operand = bw
    x = truncate(lshift(x, shamt_x), bw_operand)
    y = truncate(lshift(y, shamt_y), bw_operand)
    z_buff = x + y
    z_bwred = truncate(lshift(z_buff, shamt_bwred), bw)
    return z_bwred

class VVADD(OpType):
    def __init__(self):
        super().__init__(
            name='vvadd',
            inputs=['x', 'y'],
            constants=['shamt_x', 'shamt_y', 'shamt_bwred', 'bw', 'bw_x', 'bw_y'],
            repr_settings=NodeReprSettings(
                # operator_symbol='+',
                use_var_names=False),
            opcounter=VVCounter(op='add'),
            can_bcast_in=True)

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y):
        """Add two vectors together

        Runtime Signature:
            vvadd(x, y)

        Arguments:
            x: First addend
            y: Second addend
        Constants:
            shamt_x: Left-shift-amount for x before adding
            shamt_y: Left-shift-amount for y before adding
            shamt_bwred: Left-shift-amount for resultant
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Addends are decimal aligned (by integer shift and truncation)
            2. Decimal-aligned addends are added together
            3. Result of adding is bitwidth reduced (by integer shift and truncation)

        """
        return _add(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y)

class VIADD(OpType):
    def __init__(self):
        super().__init__(
            name='viadd',
            inputs=["x"], 
            constants=["y", "shamt_x", "shamt_y", "shamt_bwred", "bw", "bw_x", "bw_y"],
            opcounter=VCounter(op='add'),
            repr_settings=NodeReprSettings(
                # operator_symbol='+', 
                use_var_names=False,
                constants_to_rep=['y']),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y):
        """Add a vector to an immediate

        Runtime Signature:
            viadd(x)
        Arguments:
            x: Vector addend
        Constants:
            y: Immediate addend (stored as an integer)
            shamt_x: Left-shift-amount for x before adding
            shamt_y: Left-shift-amount for y (immediate) before adding
            shamt_bwred: Left-shift-amount for resultant
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Addends are decimal aligned (by integer shift and truncation)
            2. Decimal-aligned addends are added together
            3. Result of adding is bitwidth reduced (by integer shift and truncation)
        """
        return _add(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y)

class VVSUB(OpType):
    def __init__(self):
        super().__init__(
            name='vvsub',
            inputs=["x", "y"], 
            constants=["shamt_x", "shamt_y", "shamt_bwred", "bw", "bw_x", "bw_y"],
            opcounter=VVCounter(op='add'),
            repr_settings=NodeReprSettings(
                # operator_symbol='-',
                use_var_names=False),
            can_bcast_in=True)

    @staticmethod
    def runtime(x, y, shamt_x, shamt_y, shamt_bwred, bw, bw_x, bw_y):
        """Subtracts one vector from another

        Runtime Signature:
            vvsub(x, y)

        Arguments:
            x: First argument
            y: Second argument (to be subtracted)
        Constants:
            shamt_x: Left-shift-amount for x before subtracting
            shamt_y: Left-shift-amount for y before subtracting
            shamt_bwred: Left-shift-amount for resulting difference
            bw: Bitwidth of x, y, and output
        Guarantees:
            At least one shamt_x and shamt_y will be 0.

        Description:
            1. Operands are decimal aligned (by integer shift and truncation).
            2. Decimal-aligned operands are subtracted.
            3. Resulting difference is bitwidth reduced (by integer shift and truncation).

        """
        assert not (shamt_x != 0 and shamt_y != 0), "x or y can have nonzero shamt but not both"
        if not ((bw_x is None) or (bw_y is None)):
            bw_operand = max(bw_x, bw_y)
        else:
            bw_operand = bw
        x = truncate(lshift(x, shamt_x), bw_operand)
        y = truncate(lshift(y, shamt_y), bw_operand)
        z_buff = x - y
        z_bwred = truncate(lshift(z_buff, shamt_bwred), bw)
        return z_bwred

class VNEG(OpType):
    def __init__(self):
        super().__init__(
            name='vneg',
            inputs=['x'],
            constants=['bw'],
            opcounter=VCounter(op='add'),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, bw):
        """Multiply a vector by -1

        Runtime Signature:
            vneg(x)
        Arguments:
            x: Vector to be negated
        Constants:
            bw: Bitwidth of x and output

        Description:
            1. Input is negated
            2. Output is truncated
                Truncation can produce off-by-1s from mathematically expected at the negative extrema
                because of asymmetry the signed representation. For example, in 8bits, -128 negates to
                127 after trunction.
        """
        return truncate(-x, bw)

def _mul(x, y, shamt_bwred, bw):
    """Multiplies two vectors element-wise

    Args:
        x: First argument
        y: Second argument
        shamt_bwred: Left-shift-amount for resulting product
        bw: Bitwidth of output
    """
    z_buff = x * y
    z_bwred = truncate(lshift(z_buff, shamt_bwred), bw)
    return z_bwred

class VVMUL(OpType):
    def __init__(self):
        super().__init__(
            name='vvmul',
            inputs=['x', 'y'],
            constants=['shamt_bwred', 'bw'],
            opcounter=VVCounter(op='mul'),
            repr_settings=NodeReprSettings(
                # operator_symbol='*',
                use_var_names=False),
            can_bcast_in=True)

    @staticmethod
    def runtime(x, y, shamt_bwred, bw):
        """Multiplies two vectors element-wise

        Runtime Signature:
            vvmul(x, y)
        Arguments:
            x: First argument
            y: Second argument
        Constants:
            shamt_bwred: Left-shift-amount for resulting product
            bw: Bitwidth of output

        Description:
            1. Operands are multipled
            2. Resulting product is left-shifted and truncated to bw
        """
        return _mul(x, y, shamt_bwred, bw)

class VIMUL(OpType):
    def __init__(self):
        super().__init__(
            name='vimul',
            inputs=["x"], 
            constants=["y", "shamt_bwred", "bw"], 
            opcounter=VCounter(op='mul'),
            repr_settings=NodeReprSettings(
                # operator_symbol='*', 
                constants_to_rep=['y'],
                use_var_names=False),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, y, shamt_bwred, bw):
        """Multiplies a vectors element-wise with an immediate

        Runtime Signature:
            vimul(x)
        Arguments:
            x: Operand
        Constants:
            y: Immediate (represented as an integer)
            shamt_bwred: Left-shift-amount for resulting product
            bw: Bitwidth of output

        Description:
            1. Operand is element-wise multipled with the immediate
            2. Resulting product is left-shifted and truncated to bw
        """
        return _mul(x, y, shamt_bwred, bw)

class MATMUL(OpType):
    def __init__(self):
        super().__init__(
            name='matmul', 
            inputs=["x", "y"], 
            constants=["shamt_bwred", "bw_out"],
            opcounter=MatmulCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, y, shamt_bwred, bw_out):
        """Matrix product

        Runtime Signature:
            matmul(x, y)
        Arguments:
            x: First argument
            y: Second argument
        Constants:
            shamt_bwred: Left-shift-amount for resulting product
            bw_out: Bitwidth of output

        Description:
            1. Matmul between input operands
            2. Resulting product is left-shifted and truncated
        """
        z_buff = x @ y
        z_bwred = truncate(lshift(z_buff, shamt_bwred), bw_out)
        return z_bwred

class ADDMM(OpType):
    def __init__(self):
        super().__init__(
            name='addmm',
            inputs=["bias", "x", "y"], 
            constants=["shamt_bias", "shamt_bwred", "bw_out"],
            opcounter=MatmulCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(bias, x, y, shamt_bias, shamt_bwred, bw_out):
        """Matrix product with bias

        Runtime Signature:
            addmm(bias, mat1, mat2)
        Arguments:
            bias: constant vector to add to the product
            x: first matmul operand
            y: second matmul operand
        Constants:
            shamt_bias: left-shift-amount for bias, for shift without accumulation (step 1.)
            shamt_bwred: left-shift-amount for resulting product
            bw_out: output bitwidth

        Description:
            1. Bias is shifted (without truncation) to match the scale of the
                accumulating buffer (scale_buffer = scale_mat1 * scale_mat2)
            2. The matrix-vector product between mat1 and mat2 is accumulated into the
                buffer, on top of the bias
            3. Resulting product is left-shifted and truncated
        """
        buff = x @ y
        buff += truncate(lshift(bias, shamt_bias), B_ACC_ENTRY)
        z = truncate(lshift(buff, shamt_bwred), bw_out)
        return z

class RELU(OpType):
    def __init__(self):
        super().__init__(
            name='relu',
            inputs=["x"], 
            constants=[], 
            opcounter=VCounter(op=None, sparse_out=True),
            can_bcast_in=False)

    @staticmethod
    def runtime(x):
        """Element-wise rectified nonlinearity on the input vector

        Runtime Signature:
            relu(x)
        Arguments:
            x: Input

        Description:
            Relu clamps negative values to zero, and leaves positive entries unchanged.
                relu(x) = x * {x > 0}
            Because relu does not have an effect on the quantization scale, it does not involve any
            shamt constants.
        """
        return np.clip(x, 0, None)

class LUT(OpType):
    def __init__(self):
        super().__init__(
            name='lut', 
            inputs=["x"], 
            constants=["shamt_address", "bw_address", "table", "function"],
            opcounter=VLUTCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=['function']),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, shamt_address, bw_address, table, function):
        """Performs an elementwise lookup table based nonlinearity on the input vector.

        Runtime Signature:
            lut(x)
        Arguments:
            x: Input
        Constants:
            shamt_address: Left-shift amount for truncating input to address bitwidth
            bw_address: Bitwidth of the LUT address space. Used during address truncation.
            table: An fmot.qat.nn.Table object. table.x is an integer array of input addresses.
                table.y is an integer array of output values.
            function: String, name of the function. Not used during computation, just a useful
                annotation.

        Description:
            1. Input vector is bitwidth-reduced to match the bitwidth of the LUT's address space
               This is done with a truncating left-shift, parametrized by `shamt_address` and
               `bits_address`. The LSBs up to `bw_address` are used during truncation.
            2. Outputs are generated element-by-element by querying the table with the truncated
               input values.
        """
        address = truncate(lshift(x, shamt_address), bw_address) - np.min(table.x)
        z = table.y[address]
        return z

class TRANSPOSE(OpType):
    def __init__(self):
        super().__init__(
            name='transpose', 
            inputs=["x"], 
            constants=["dim0", "dim1"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, dim0, dim1):
        """Performs a (hopefully) virtual transpose on a matrix.

        Runtime Signature:
            transpose(x)
        Arguments:
                x: input

        Description:
            The last two dimensions in a tensor are permuted.
            A matrix M that is row-major will be indexed as:
                (row_index, column_index) such that M[i, j] will be the entry in row-i and column-j.
            The matrix W = TRANSPOSE(M) will be column-major, with indexing as:
                (column_index, row_index) such that M[i,j] = W[j, i]
            If a tensor only has 1 dimension, this operation is identity
        """
        if x.ndim >= 2:
            return np.transpose(x, (max(dim0, dim1), min(dim0, dim1)))
        else:
            return x

class RESHAPE(OpType):
    def __init__(self):
        super().__init__(
            name='reshape',
            inputs=["x"], 
            constants=["shape"],
            opcounter=NullCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=['shape']),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, shape):
        """Reshape the input tensor

        Runtime Signature:
            reshape(x)
        Arguments:
            x: The tensor to be reshaped
        Constants:
            shape: the shape for the new tensor

        Description:
            Returns a tensor with same data but with the specified shape.
        """
        return np.reshape(x, shape)

class QUANTIZE(OpType):
    def __init__(self):
        super().__init__(
            name='quantize',
            inputs=["x"], 
            constants=["quanta", "bw"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, quanta, bw):
        """Convert a floating-point tensor into a quantized integer tensor, according to:

        Runtime Signature:
            quantize(x)
        Arguments:
            x: Input
        Constants:
            quanta: Integer quanta, related to scale as scale = 2**quanta
            bw: Integer bitwidth

        Description:
            1. Divide input by scale = 2**quanta
            2. Floor
            3. Clip between -2**(bitwidth-1), 2**(bitwidth-1) - 1
        """
        scale = 2**quanta
        boundaries = -2**(bw-1), 2**(bw-1)-1
        z = np.clip(np.floor(x/scale), *boundaries)
        z = z.astype(int)
        return z

class DEQUANTIZE(OpType):
    def __init__(self):
        super().__init__(
            name='dequantize',
            inputs=["x"], 
            constants=["quanta"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, quanta):
        """Convert an integer tensor into a rounded floating-point tensor

        Runtime Signature:
            dequantize(x)
        Arguments:
            x: Onput
        Constants:
            quanta: Integer quanta, related to scale as scale = 2**quanta

        Description:
            1. Cast integer input to floating point
            2. Multiply by scale = 2**quanta
        """
        scale = 2**quanta
        x = x.astype(float)
        return x * scale

class CHUNK(OpType):
    def __init__(self):
        super().__init__(
            name='chunk', 
            inputs=["x"], 
            constants=["chunks", "dim"],
            opcounter=CopyCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, chunks, dim):
        """Split a tensor into a tuple of `chunks` tensors along a dimension `dim`.

        Runtime Signature:
            chunk(x)
        Arguments:
            x: Input
        Constants:
            chunks: Number of chunks
            dim: Dimension to split

        Description:
            Tensor dimension `dim` is evenly divided into `chunks` equal-length segments.
        """
        return tuple(np.array_split(x, chunks, dim))

class SPLIT(OpType):
    def __init__(self):
        super().__init__(
            name='split',
            inputs=["x"],
            constants=["lengths", "dim"],
            opcounter=CopyCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, lengths, dim):
        """Split a tensor into a tuple of tensors along a dimension `dim`.

        Runtime Signature:
            split(x)
        Arguments:
            x: Input
        Constants:
            lengths (list[int]): lengths of each split
            dim: Dimension to split

        Description:
            Tensor dimension `dim` is divided into segments, with lengths given by `lengths`.
        """

        inds = np.cumsum(lengths)[:-1]
        return tuple(np.split(x, inds, dim))

class CAT(OpType):
    def __init__(self):
        super().__init__(
            name='cat', 
            inputs=["kwargs"], 
            constants=["dim"],
            opcounter=CopyCounter(),
            repr_settings=NodeReprSettings(use_var_names=False),
            can_bcast_in=False)

    @staticmethod
    def runtime(dim, **kwargs):
        """Concatenate tensors along `dim`, in order.

        Runtime Signature:
            cat(x0, x1, x2, ...)
        Arguments:
            x0, x1, ... : Variable number of input vectors to concatenate in index-order.
                Names must start with 'x0' and increment
        Constants:
            dim: Dimension to concatenate
        """
        to_cat = []
        i = 0
        while f'x{i}' in kwargs:
            to_cat.append(kwargs[f'x{i}'])
            i += 1
        return np.concatenate(to_cat, axis=dim)

class STACK(OpType):
    def __init__(self):
        super().__init__(
            name='stack', 
            inputs=["kwargs"], 
            constants=["dim"],
            opcounter=CopyCounter(),
            repr_settings=NodeReprSettings(use_var_names=False),
            can_bcast_in=False)

    @staticmethod
    def runtime(dim, **kwargs):
        """Stack tensors along dim

        Runtime Signature:
            stack(x0, x1, x2, ...)
        Arguments:
            x0, x1, ... : Variable number of input vectors to stack in index-order
                Names must start with 'x0' and increment
        Constants:
            dim: Dimension to stack
        """
        to_stack = []
        i = 0
        while f'x{i}' in kwargs:
            to_stack.append(kwargs[f'x{i}'])
            i += 1
        return np.stack(to_stack, axis=dim)

class SQUEEZE(OpType):
    def __init__(self):
        super().__init__(
            name='squeeze', 
            inputs=["x"], 
            constants=["dim"], 
            opcounter=NullCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, dim):
        raise NotImplementedError

class ZEROS(OpType):
    def __init__(self):
        super().__init__(
            name='zeros', 
            inputs=[], 
            constants=["shape"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(shape):
        """Init a zeros vector of shape `shape`

        Runtime Signature:
            zeros()
        Constants:
            shape (tuple): Shape of zeros vector
        """
        return np.zeros(shape).astype(int)

class CONSTANT(OpType):
    def __init__(self):
        super().__init__(
           name='constant',
            inputs=[], 
            constants=["shape", "value"],
            opcounter=NullCounter(),
            repr_settings=NodeReprSettings(constants_to_rep=['value']),
            can_bcast_in=False)

    @staticmethod
    def runtime(shape, value):
        """Init a constant vector of shape `shape`

        Runtime Signature:
            zeros()
        Constants:
            shape (tuple): Shape of vector
            value (int): constant value for tensor
        """
        return np.ones(shape).astype(int)*value

class ASSIGN(OpType):
    def __init__(self):
        super().__init__(
            name='assign',
            inputs=["y", "x"], 
            constants=[],
            opcounter=CopyCounter(),
            can_bcast_in=False)

    def runtime(self, y, x):
        """Assign y to hold the value stored by x (i.e. y = x)

        Runtime Signature:
            assign(y, x)
        Arguments:
            y: Variable to copy to
            x: Variable to copy from
        """
        return {self._inputs['y'].name: x}

class TEMPORAL_UNFOLD_UNKERNELIZED(OpType):
    def __init__(self):
        super().__init__(
            name='temporal_unfold_unkernelized',
            inputs=["x"], 
            constants=["kernel_size", "dilation", "buffer_length"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    def runtime(self, x, kernel_size, dilation, buffer_length):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Returns a concatenation of the in-frame vectors 
        at each time-step.

        Runtime Signature:
            temporal_unfold(x, buffer)

        Arguments:
            x: new input frame
            buffer: not added here -- will be added after kernelization
        Constants:
            kernel_size: kernel size of sliding window
            dilation: dilation of sliding window
            buffer_length: number of vectors stored in buffer
        """
        pass

class TEMPORAL_UNFOLD(OpType):
    def __init__(self):
        super().__init__(
            name='temporal_unfold',
            inputs=["x", "buffer"], 
            constants=["kernel_size", "dilation", "buffer_length"],
            opcounter=NullCounter(),
            can_bcast_in=False)

    def runtime(self, x, buffer, kernel_size, dilation, buffer_length):
        """Internally manages the state of a rolling buffer with a sliding
        dilated temporal window. Returns a concatenation of the in-frame vectors 
        at each time-step.

        Runtime Signature:
            temporal_unfold(x, buffer)

        Arguments:
            x: new input frame
            buffer: stateful buffer storing past frames
        Constants:
            kernel_size: kernel size of sliding window
            dilation: dilation of sliding window
            buffer_length: number of vectors stored in buffer
        """
        buffer = np.concatenate([buffer, x])
        buffer = buffer.reshape(-1, len(x))
        outs = buffer[::dilation]
        outs = outs.flatten()
        buffer = buffer[1:].flatten()

        return {
            self._outputs[0].name: outs,
            self._inputs['buffer'].name: buffer
        }

class SUM(OpType):
    def __init__(self):
        super().__init__(
            name='sum',
            inputs=["x"], 
            constants=["dim", "keepdim", "shamt_bwred", "bw"],
            opcounter=ReductionCounter(),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, dim, keepdim, shamt_bwred, bw):
        """Sum the elements of x along a dim

        Runtime Signature:
            sum(x)
        Arguments:
            x: Input
        Constants:
            dim (int or List[int]): Dimension(s) to reduce
            keepdim (bool): Whether output has "dim" retained
            shamt_bwred (int): Left-shift-amount for resultant sum
            bw: Output bitwidth

        Description:
            1. Accumulate entries along dimension(s) "dim"
            2. Reduce bitwidth with a saturating left-shift according to "shamt_bwred"
        """
        z = np.sum(x, axis=dim, keepdims=keepdim)
        return truncate(lshift(z, shamt_bwred), bw)

class CONSTANT_LIKE(OpType):
    def __init__(self):
        super().__init__(
            name='constant_like', 
            inputs=["x"], 
            constants=["imm"],
            opcounter=CopyCounter(),
            can_bcast_in=False)
    
    @staticmethod
    def runtime(x, imm):
        """Return a tensor of the same shape as the input, filled with constant "imm".

        Runtime Signature:
            constant_like(x)
        Arguments:
            x: Input
        Constants:
            imm: Integer immediate with which to fill the vector
        """
        return np.ones_like(x) * imm

class COPY(OpType):
    def __init__(self):
        super().__init__(
            name='copy', 
            inputs=["x"], 
            constants=[],
            opcounter=CopyCounter(),
            can_bcast_in=False)
    
    @staticmethod
    def runtime(x):
        """Copies a tensor

        Runtime Signature:
            copy(x)
        Arguments:
            x: Input
        """
        return x

class SHIFT(OpType):
    def __init__(self):
        super().__init__(
            name='shift',
            inputs=["x"], 
            constants=["shamt", "bw"],
            opcounter=ShiftCounter(),
            repr_settings=NodeReprSettings(
                # operator_symbol='<<', 
                constants_to_rep=['shamt'],
                use_var_names=False),
            can_bcast_in=False
        )
    
    @staticmethod
    def runtime(x, shamt, bw):
        """Shift and saturate a vector

        Runtime Signature:
            shift(x)
        Arguments:
            x: Input
        Constants:
            shamt: Left-shift amount
            bw: Output bitwidth

        Description:
            Applies a saturating integer shift to a tensor. May also change the bitwidth/datatype.
        """
        return truncate(lshift(x, shamt), bw)

class GT0(OpType):
    def __init__(self):
        super().__init__(
            name='gt0', 
            inputs=["x"], 
            constants=["bw"],
            opcounter=VCounter(op=None),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, bw):
        """Elementwise greater than zero. Returns a masking tensor of 0/1's.

        Runtime Signature:
            gt0(x)
        Arguments:
            x: Input
        Constants:
            bw: The output bitwidth, decides what the shift-amounts should be.
                With bw=<BW>, the pseudo-fqir is:
                    x1: fqint<BW> = relu(x=x0)
                    x2: fqint<BW> = shift[shamt=<BW>-1, bw=<BW>](x=x1)
                    x3: fqint<BW> = shift[shamt=-<BW>+1, bw=<BW>](x=x2)

        Description:
            This operation is equivalent to the following (in pseudo-fqir):
                x1: fqint8 = relu(x=x0)
                x2: fqint8 = shift[shamt=7, bw=8](x=x1)
                x3: fqint8 = shift[shamt=-7, bw=8](x=x2)
            The first shift saturates the output of the relu so that the vector elements are either 0
            or 125. The second shift results in elements that are either 0 or 1.
        """
        return (x > 0).astype(int)

class PRINT(OpType):
    def __init__(self):
        super().__init__(
            name='print', 
            inputs=["x"], 
            constants=["func"],
            opcounter=VCounter(op=None),
            can_bcast_in=False)

    @staticmethod
    def runtime(x, func):
        """Prints a string given by func(x), where x in a numpy array
        """
        print(func(x))

class LSTM(OpType):
    def __init__(self):
        super().__init__(
            name='lstm',
            inputs=["x"],
            constants=[
                "num_layers",
                "input_size",
                "hidden_size", 
                "batch_first", 
                "sigmoid",
                "tanh",
                "layers" # layers contains layer-specific constants
            ],
            opcounter=NullCounter(),
            can_bcast_in=False
        )
    
    @staticmethod
    def runtime(x, num_layers, input_size, hidden_size, batch_first, sigmoid, tanh, layers):
        raise NotImplementedError

registry_v1 = OpRegistry('fmot_atomics_v1.2')

def register(*optypes):
    for optype in optypes:
        op = optype()
        assert isinstance(op, OpType)
        registry_v1.register_op(op)

register(
    VVADD, VIADD, VVSUB, VNEG, VVMUL, VIMUL, MATMUL, ADDMM, RELU, LUT, TRANSPOSE,
    RESHAPE, QUANTIZE, DEQUANTIZE, CHUNK, SPLIT, CAT, STACK, SQUEEZE, ZEROS, CONSTANT, ASSIGN,
    SUM, CONSTANT_LIKE, COPY, SHIFT, GT0,
    LSTM, TEMPORAL_UNFOLD, TEMPORAL_UNFOLD_UNKERNELIZED, PRINT)