import warnings
from typing import Any, Dict, Optional, Tuple

import torch.nn as nn

from _finetuner.models import poolers
from _finetuner.tailor import to_embedding_model
from _finetuner.tailor.projection import ProjectionHead


def convert_backbone_to_embedding_model(
    backbone: nn.Module,
    embedding_layer: Optional[str] = None,
    embedding_dim: Optional[int] = None,
    output_dim: Optional[int] = None,
    freeze: bool = False,
    tailor_input_shape: Optional[Tuple[int, ...]] = None,
    tailor_input_dtype: str = 'float32',
    pooler: Optional[str] = None,
    pooler_options: Optional[Dict[str, Any]] = None,
    pooling_layer: Optional[str] = None,
) -> nn.Module:
    """Convert backbone to embedding model.

    :param backbone: The backbone loaded from the model builders.
    :param embedding_layer: The layer to be used to extract features.
    :param embedding_dim: The dimensionality of the embedding layer.
    :param output_dim: The expected output dimensionality. If set and not equal
        to `embedding_dim`, will attach mlp to the end.
    :param freeze: If freeze the model or not.
    :param tailor_input_shape: The input shape of the model, used to interpret
        the model structure by construct a random tensor and bypass the model.
    :param tailor_input_dtype: The input dtype of the tensor.
    :param pooler: A `str` to specify what pooling layer should be add, if any.
        The default, and currently the only valid option, is 'GeM'.
    :param pooler_options: A dictionary of additional arguments to provide to the
        pooling layer.
    :param pooling_layer: The attribute name of the layer to be replaced.
    :return:
    """
    projection_head = None
    embedding_layer = embedding_layer
    embedding_dim = embedding_dim
    output_dim = output_dim

    if freeze and not output_dim:
        output_dim = embedding_dim

    if output_dim and (embedding_dim != output_dim or freeze):
        projection_head = ProjectionHead(
            in_features=embedding_dim, output_dim=output_dim
        )

    model = to_embedding_model(
        model=backbone,
        layer_name=embedding_layer,
        freeze=freeze,
        projection_head=projection_head,
        input_shape=tailor_input_shape,
        input_dtype=tailor_input_dtype,
    )
    if pooler and pooling_layer:
        add_pooling_layer(
            model,
            pooling_layer=pooling_layer,
            pooler_name=pooler,
            pooler_options=pooler_options,
        )
    return model


def add_pooling_layer(
    model: nn.Module,
    pooling_layer: str,
    pooler_name: str = 'GeM',
    pooler_options: Optional[Dict[str, Any]] = None,
) -> None:
    """Add a pooling layer or one to a model or replace an existing one.
    :param model: The model to add a pooler to.
    :param pooler_name: The name of the type of pooling layer to add. By default is
        the GeM pooler as it is currently the only layer supported by this method.
    :param pooler_options: A dictionary of additional parameters to pass to the pooler
        during construction, None by default.
    :param pooling_layer: The attribute name of the layer to be replaced.
    """

    if getattr(model, pooling_layer, None) is None:
        warnings.warn(
            f'Given model has no layer: {pooling_layer}, adding a pooler here may have no effect'
        )
    pooler_options = pooler_options or {}
    pooler = getattr(poolers, pooler_name, None)
    if pooler:
        pooler = pooler(**pooler_options)
    else:
        raise ValueError(f'No pooler named {pooler_name}')

    setattr(model, pooling_layer, pooler)
