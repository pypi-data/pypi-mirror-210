import abc
from typing import Optional, TypeVar

from torch import nn
from transformers import AutoConfig, AutoModel, AutoModelForSequenceClassification

from _finetuner.models.nn.modules import (
    CLIP,
    MLP,
    CrossEncoder,
    MeshDataModel,
    OpenCLIPTextModel,
    OpenCLIPVisionModel,
    TextTransformer,
)

BackboneBuilderType = TypeVar('BackboneBuilderType', bound='_BackboneBuilder')


def load_open_clip_model(
    descriptor: str, download_pretrained: bool = False
) -> nn.Module:
    """
    Loads an Open CLIP model from a given descriptor. If `download_pretrained` set
    to True, download pretrained weights, otherwise use random initialized weights.

    :param descriptor: Refers to a pre-trained open clip model.
    :param download_pretrained: If set to `True`, download pretrained weights.
    :return: An Open CLIP PyTorch model.
    """
    import open_clip

    name, pretrained = descriptor.split('::')
    if download_pretrained:
        return open_clip.create_model(name, pretrained=pretrained)
    else:
        return open_clip.create_model(name, pretrained=None)


class _BackboneBuilder(metaclass=abc.ABCMeta):
    """Base backbone model builder."""

    _supports_tailor: bool = False

    def __init__(
        self,
        descriptor: str,
        options: Optional[dict] = None,
        download_pretrained: bool = False,
    ) -> None:
        self._descriptor = descriptor
        self._options = options
        self._download_pretrained = download_pretrained

    def __call__(self) -> nn.Module:
        return self.build()

    @abc.abstractmethod
    def build(self) -> nn.Module:
        ...


class EfficientNetB4Builder(_BackboneBuilder):
    """Build a CNN based model efficientnet_b4 using the torchvision library."""

    _supports_tailor = True

    def build(self) -> nn.Module:
        import torchvision

        weights = (
            torchvision.models.EfficientNet_B4_Weights.DEFAULT
            if self._download_pretrained
            else None
        )

        model = getattr(torchvision.models, self._descriptor)(weights=weights)
        return model


class EfficientNetB7Builder(_BackboneBuilder):
    """Build a CNN based model efficientnet_b7 using the torchvision library."""

    _supports_tailor = True

    def build(self) -> nn.Module:
        import torchvision

        weights = (
            torchvision.models.EfficientNet_B7_Weights.DEFAULT
            if self._download_pretrained
            else None
        )

        model = getattr(torchvision.models, self._descriptor)(weights=weights)
        return model


class ResNet50Builder(_BackboneBuilder):
    """Build a CNN based model resnet_50 using the torchvision library."""

    _supports_tailor = True

    def build(self) -> nn.Module:
        import torchvision

        weights = (
            torchvision.models.ResNet50_Weights.DEFAULT
            if self._download_pretrained
            else None
        )

        model = getattr(torchvision.models, self._descriptor)(weights=weights)
        return model


class ResNet152Builder(_BackboneBuilder):
    """Build a CNN based model resnet_152 using the torchvision library."""

    _supports_tailor = True

    def build(self) -> nn.Module:
        import torchvision

        weights = (
            torchvision.models.ResNet152_Weights.DEFAULT
            if self._download_pretrained
            else None
        )

        model = getattr(torchvision.models, self._descriptor)(weights=weights)
        return model


class OpenCLIPTextBuilder(_BackboneBuilder):
    """Build a text transformer model for an Open CLIP model."""

    def build(self) -> nn.Module:
        model = load_open_clip_model(
            self._descriptor, download_pretrained=self._download_pretrained
        )
        return OpenCLIPTextModel(model)


class OpenCLIPVisionBuilder(_BackboneBuilder):
    """Build a vision model for an Open CLIP model."""

    def build(self) -> nn.Module:
        model = load_open_clip_model(
            self._descriptor, download_pretrained=self._download_pretrained
        )
        return OpenCLIPVisionModel(model)


class CLIPTextBuilder(_BackboneBuilder):
    """Build a CLIP text model using the transformers package."""

    def build(self) -> nn.Module:
        if self._download_pretrained:
            model = AutoModel.from_pretrained(self._descriptor)
        else:
            config = AutoConfig.from_pretrained(self._descriptor)
            model = AutoModel.from_config(config)
        return CLIP(model.text_model, model.text_projection)


class CLIPVisionBuilder(_BackboneBuilder):
    """Build a CLIP vision model using the transformers package."""

    def build(self) -> nn.Module:
        if self._download_pretrained:
            model = AutoModel.from_pretrained(self._descriptor)
        else:
            config = AutoConfig.from_pretrained(self._descriptor)
            model = AutoModel.from_config(config)
        return CLIP(model.vision_model, model.visual_projection)


class TextTransformerBuilder(_BackboneBuilder):
    """Build a text transformer model using huggingface transformers."""

    def build(self) -> nn.Module:
        if self._download_pretrained:
            model = AutoModel.from_pretrained(self._descriptor)
        else:
            config = AutoConfig.from_pretrained(self._descriptor)
            model = AutoModel.from_config(config)
        return TextTransformer(model, **self._options)


class MLPBuilder(_BackboneBuilder):
    """Build an MLP model from scratch, to fine-tune with pre-embedded documents."""

    def build(self) -> nn.Module:
        return MLP(**self._options)


class MeshDataModelBuilder(_BackboneBuilder):
    """Builds a model for encoding meshes."""

    def build(self) -> nn.Module:
        return MeshDataModel(**self._options)


class CrossEncoderBuilder(_BackboneBuilder):
    """Builds a cross encoder transformer model."""

    def build(self) -> nn.Module:
        config = AutoConfig.from_pretrained(self._descriptor)
        return CrossEncoder(
            AutoModelForSequenceClassification.from_pretrained(
                self._descriptor, config=config
            )
        )
