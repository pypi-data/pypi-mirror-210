import random
random.seed(0)
import numpy as np
np.random.seed(0)
import tensorflow as tf
import onnx_graphsurgeon as gs
from onnx2tf.utils.common_functions import (
    get_constant_or_variable,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
    get_replacement_parameter,
    pre_process_transpose,
    post_process_transpose,
    transpose_with_flexing_deterrence,
)
from onnx2tf.utils.enums import NUMPY_DTYPES_TO_TF_DTYPES


@print_node_info
@inverted_operation_enable_disable
@get_replacement_parameter
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """InstanceNormalization

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    before_op_output_shape_trans_1 = \
        tf_layers_dict.get(graph_node.inputs[0].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans_2 = \
        tf_layers_dict.get(graph_node.inputs[1].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans_3 = \
        tf_layers_dict.get(graph_node.inputs[2].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans = \
        before_op_output_shape_trans_1 \
        and before_op_output_shape_trans_2 \
        and before_op_output_shape_trans_3

    graph_node_input = get_constant_or_variable(
        graph_node.inputs[0],
        before_op_output_shape_trans,
    )

    input_tensor = tf_layers_dict[graph_node_input.name]['tf_node'] \
        if isinstance(graph_node_input, gs.Variable) else graph_node_input

    # Pre-process transpose
    input_tensor = pre_process_transpose(
        value_before_transpose=input_tensor,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )

    input_tensor_shape = input_tensor.shape
    input_tensor_rank = len(input_tensor_shape)

    scale = get_constant_or_variable(
        graph_node.inputs[1],
        before_op_output_shape_trans,
        is_bias=True,
    )
    scale_dtype = NUMPY_DTYPES_TO_TF_DTYPES[scale.dtype] \
        if isinstance(scale.dtype, np.dtype) else scale.dtype
    scale = tf.convert_to_tensor(scale, dtype=scale_dtype) \
        if isinstance(scale, np.ndarray) else scale

    B = get_constant_or_variable(
        graph_node.inputs[2],
        before_op_output_shape_trans,
        is_bias=True,
    )
    B_dtype = NUMPY_DTYPES_TO_TF_DTYPES[B.dtype] \
        if isinstance(B.dtype, np.dtype) else B.dtype
    B = tf.convert_to_tensor(B, dtype=B_dtype) \
        if isinstance(B, np.ndarray) else B

    graph_node_output: gs.Variable = graph_node.outputs[0]
    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    epsilon = graph_node.attrs.get('epsilon', 1e-05)
    epsilon = tf.convert_to_tensor(epsilon, dtype=tf.float32)

    # Preserving Graph Structure (Dict)
    tf_layers_dict[graph_node_output.name] = {
        'optype': graph_node.op,
        'shape': shape,
        'dtype': dtype,
        'nhwc': tf_layers_dict[graph_node_input.name]['nhwc'] \
            if isinstance(graph_node_input, gs.Variable) \
                and 'nhwc' in tf_layers_dict[graph_node_input.name].keys() else False
    }

    # ONNX   : N,C,W
    # TF     : N,W,C
    # TF-axes: [1]
    #
    # ONNX: N,C,H,W
    # TF  : N,H,W,C
    # TF-axes: [1,2]
    #
    # ONNX: N,C,D,H,W
    # TF  : N,D,H,W,C
    # TF-axes: [1,2,3]

    # NCHW -> NHWC
    onnx_input_shape = [
        dim if isinstance(dim, int) else None for dim in graph_node.inputs[0].shape
    ]
    tf_input_shape = [
        dim if isinstance(dim, int) else None for dim in input_tensor_shape
    ]
    if onnx_input_shape == tf_input_shape:
        input_tensor = transpose_with_flexing_deterrence(
            input_tensor=input_tensor,
            perm=[0] + [i+2 for i in range(input_tensor_rank-2)] + [1],
            **kwargs,
        )

    # Generation of TF OP
    axes = [idx for idx in range(1, input_tensor_rank - 1)]
    mean, variance = tf.nn.moments(input_tensor, axes=axes, keepdims=True)

    tf_layers_dict[graph_node_output.name]['tf_node'] = \
        scale * (input_tensor - mean) * tf.math.rsqrt(variance + epsilon) + B

    # Post-process transpose
    tf_layers_dict[graph_node_output.name]['tf_node'] = post_process_transpose(
        value_before_transpose=tf_layers_dict[graph_node_output.name]['tf_node'],
        param_target='outputs',
        param_name=graph_node.outputs[0].name,
        **kwargs,
    )

    # Generation of Debug Info
    tf_layers_dict[graph_node_output.name]['tf_node_info'] = \
        make_tf_node_info(
            node_info={
                'tf_op_type': 'InstanceNormalization',
                'tf_inputs': {
                    'x': input_tensor,
                    'mean': mean,
                    'variance': variance,
                    'offset': B,
                    'scale': scale,
                    'variance_epsilon': epsilon,
                },
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
