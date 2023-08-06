import abc
import inspect
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from _finetuner.excepts import NoSuchModel, SelectModelRequired

ModelStubType = TypeVar('ModelStubType', bound='_ModelStub')


class _ModelStub(metaclass=abc.ABCMeta):
    name: str
    display_name: str
    descriptor: str
    description: str
    architecture: str
    builder: str
    input_names: List[str]
    input_shapes: List[Tuple[Union[int, str], ...]]
    input_dtypes: List[str]
    output_name: str
    output_shape: Tuple[Union[int, str], ...]
    dynamic_axes: Dict[str, Dict[int, str]]
    preprocess_types: Dict[str, str]
    collate_types: Dict[str, str]
    preprocess_options: Dict[str, Dict[str, Any]] = {}
    collate_options: Dict[str, Dict[str, Any]] = {}
    options: Dict[str, Any] = {}
    supports_onnx_export: bool = True

    def __init__(
        self,
        preprocess_options: Optional[Dict[str, Dict[str, Any]]] = None,
        collate_options: Optional[Dict[str, Dict[str, Any]]] = None,
        **options: Any,
    ) -> None:
        self.options = options
        if preprocess_options:
            self.preprocess_options.update(preprocess_options)
        if collate_options:
            self.collate_options.update(collate_options)

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def descriptor(self) -> str:
        ...


class _EmbeddingModelStub(_ModelStub, metaclass=abc.ABCMeta):
    task: str
    default: bool = False
    embedding_layer: Optional[str]
    pooling_layer: Optional[str]


def get_model_stubs_dict() -> Tuple[
    Dict[str, List[ModelStubType]], Dict[str, List[ModelStubType]]
]:
    """
    Creates two dictionaries containing all children of :class:`_ModelStub.`
    The first dictionary maps model descriptors to lists of model stubs with that
    descriptor. The second one maps model display names to lists of model stubs.

    :return: Tuple of dictionaries mapping strings to lists of :class:`_ModelStub`.
    """
    _stubs_by_descriptor = defaultdict(list)
    _stubs_by_display_name = defaultdict(list)

    for _, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):

        if (
            inspect.isclass(obj)
            and issubclass(obj, _ModelStub)
            and not inspect.isabstract(obj)
        ):
            _stubs_by_descriptor[obj.descriptor].append(obj)
            _stubs_by_display_name[obj.display_name].append(obj)
    return _stubs_by_descriptor, _stubs_by_display_name


def get_stub(
    descriptor_or_display_name: str,
    select_model: Optional[str] = None,
    model_options: Optional[Dict[str, Any]] = None,
) -> ModelStubType:
    """
    Searches the stubs of all models and returns the one
    matching the given name

    :param descriptor_or_display_name: Refers to a pre-trained model.
    :param select_model: In the case of building a CLIP model,
        specifies wether to return the text or vision model
    :param model_options: A dictionary of options that are used
        by certain models
    :return: A stub of a pre-trained model
    """
    _stubs_by_descriptor, _stubs_by_display_name = get_model_stubs_dict()

    if descriptor_or_display_name in _stubs_by_descriptor:
        stub_cls = _stubs_by_descriptor[descriptor_or_display_name]
    elif descriptor_or_display_name in _stubs_by_display_name:
        stub_cls = _stubs_by_display_name[descriptor_or_display_name]
    else:
        raise ValueError(f'No model named {descriptor_or_display_name}')

    if len(stub_cls) > 1:
        if select_model is None:
            raise SelectModelRequired(
                f'Found more than 1 models with name {descriptor_or_display_name}, please select model '
                'using `select_model`'
            )
        stub = None
        for x in stub_cls:
            if x.name == select_model:
                stub = x
                break
        if not stub:
            raise NoSuchModel(f'No model named \'{select_model}\'')
    else:
        stub = stub_cls[0]
    stub = stub()
    stub.options.update(model_options or {})
    return stub


class _CNNStub(_EmbeddingModelStub, metaclass=abc.ABCMeta):
    """CNN model stub."""

    task = 'image-to-image'
    architecture = 'cnn'
    input_names = ['image']
    input_dtypes = ['float32']
    output_name = 'embedding'
    dynamic_axes = {'image': {0: 'batch-size'}, 'embedding': {0: 'batch-size'}}
    preprocess_types = {'image': 'VisionPreprocess'}
    collate_types = {'image': 'DefaultCollate'}
    preprocess_options = {'image': {}}
    collate_options = {'image': {}}
    pooler = None
    pooler_options = {}

    def __init__(
        self,
        preprocess_options: Optional[Dict[str, Dict[str, Any]]] = None,
        collate_options: Optional[Dict[str, Dict[str, Any]]] = None,
        pooler: Optional[str] = None,
        pooler_options: Optional[Dict[str, Any]] = None,
    ):
        super(_CNNStub, self).__init__(
            preprocess_options=preprocess_options,
            collate_options=collate_options,
            pooler=pooler,
            pooler_options=pooler_options or {},
        )
        self.input_shapes = [
            (
                'batch-size',
                3,
                self.preprocess_options['image'].get('height', 224),
                self.preprocess_options['image'].get('width', 224),
            ),
        ]


class _TextTransformerStub(_EmbeddingModelStub, metaclass=abc.ABCMeta):
    """Text transformer model stub."""

    task = 'text-to-text'
    architecture = 'transformer'
    builder = 'TextTransformerBuilder'
    input_names = ['input_ids', 'attention_mask']
    input_dtypes = ['int32', 'int32']
    input_shapes = [
        ('batch-size', 'sequence-length'),
        ('batch-size', 'sequence-length'),
    ]
    output_name = 'embedding'
    dynamic_axes = {
        'input_ids': {0: 'batch-size', 1: 'sequence-length'},
        'attention_mask': {0: 'batch-size', 1: 'sequence-length'},
        'embedding': {0: 'batch-size'},
    }
    preprocess_types = {'text': 'TextPreprocess'}
    collate_types = {'text': 'TransformersCollate'}
    preprocess_options = {'text': {}}
    collate_options = {'text': {}}
    pooler_options = {}

    def __init__(
        self,
        pooler: str = 'mean',
        preprocess_options: Optional[Dict[str, Dict[str, Any]]] = None,
        collate_options: Optional[Dict[str, Dict[str, Any]]] = None,
        pooler_options: Optional[Dict[str, Any]] = None,
    ):
        self.collate_options = {
            'text': {'name': self.descriptor, 'truncation': True, 'padding': True}
        }
        super(_TextTransformerStub, self).__init__(
            preprocess_options=preprocess_options,
            collate_options=collate_options,
            pooler=pooler,
            pooler_options=pooler_options,
        )


class _VisionTransformerStub(_EmbeddingModelStub, metaclass=abc.ABCMeta):
    """Vision transformer model stub."""

    task = 'image-to-image'
    architecture = 'transformer'
    builder = 'VisionTransformerBuilder'
    input_names = ['pixel_values']
    input_dtypes = ['float32']
    output_name = 'embedding'
    dynamic_axes = {
        'pixel_values': {
            0: 'batch-size',
        },
        'embedding': {0: 'batch-size'},
    }
    preprocess_types = {'image': 'VisionPreprocess'}
    collate_types = {'image': 'VisionTransformersCollate'}
    collate_options = {'image': {}}

    def __init__(
        self,
        preprocess_options: Optional[Dict[str, Dict[str, Any]]] = None,
        collate_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.collate_options = {'image': {'name': self.descriptor}}
        super(_VisionTransformerStub, self).__init__(
            preprocess_options=preprocess_options, collate_options=collate_options
        )
        self.input_shapes = [
            (
                'batch-size',
                3,
                self.preprocess_options['image'].get('height', 224),
                self.preprocess_options['image'].get('width', 224),
            ),
        ]


class _HFCLIPTextStub(_TextTransformerStub, metaclass=abc.ABCMeta):
    """Huggingface CLIP text encoder model stub."""

    name = 'clip-text'
    builder = 'CLIPTextBuilder'
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 512)


class _HFCLIPVisionStub(_VisionTransformerStub, metaclass=abc.ABCMeta):
    """Huggingface CLIP vision encoder model stub."""

    name = 'clip-vision'
    builder = 'CLIPVisionBuilder'
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 512)
    preprocess_options = {
        'image': {'normalization': False, 'move_channel_axis': True, 'resize': False}
    }


class _OpenCLIPTextStub(_EmbeddingModelStub, metaclass=abc.ABCMeta):
    """Open CLIP text encoder model stub."""

    task = 'text-to-image'
    architecture = 'transformer'
    builder = 'OpenCLIPTextBuilder'
    input_names = ['text']
    input_dtypes = ['int32']
    input_shapes = [
        ('batch-size', 77),
    ]
    output_name = 'embedding'
    dynamic_axes = {
        'text': {0: 'batch-size'},
        'embedding': {0: 'batch-size'},
    }
    preprocess_types = {'text': 'TextPreprocess'}
    collate_types = {'text': 'OpenCLIPTextCollate'}
    preprocess_options = {'text': {}}
    collate_options = {'text': {}}
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 512)
    name = 'clip-text'

    def __init__(self):
        self.collate_options = {'text': {'name': self.descriptor}}


class _OpenCLIPVisionStub(_EmbeddingModelStub, metaclass=abc.ABCMeta):
    """Open CLIP vision encoder model stub."""

    task = 'text-to-image'
    architecture = 'transformer'
    builder = 'OpenCLIPVisionBuilder'
    input_names = ['image']
    input_dtypes = ['float32']
    output_name = 'embedding'
    dynamic_axes = {
        'image': {
            0: 'batch-size',
        },
        'embedding': {0: 'batch-size'},
    }
    preprocess_types = {'image': 'VisionPreprocess'}
    collate_types = {'image': 'OpenCLIPVisionCollate'}
    preprocess_options = {
        'image': {'normalization': False, 'move_channel_axis': False, 'resize': False}
    }
    collate_options = {'image': {}}
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 512)
    name = 'clip-vision'

    def __init__(self):
        self.collate_options = {'image': {'name': self.descriptor}}
        super(_OpenCLIPVisionStub, self).__init__()
        self.input_shapes = [
            (
                'batch-size',
                3,
                self.preprocess_options['image'].get('height', 224),
                self.preprocess_options['image'].get('width', 224),
            ),
        ]


class MLPStub(_EmbeddingModelStub):
    """MLP model stub.

    :param input_size: Size of the input representations.
    :param hidden_sizes: A list of sizes of the hidden layers. The last hidden size is
        the output size.
    :param bias: Whether to add bias to each layer.
    :param activation: A string to configure activation function, `relu`, `tanh` or
        `sigmoid`. Set to `None` for no activation.
    :param l2: Apply L2 normalization at the output layer.
    """

    name = 'mlp'
    display_name = 'mlp'
    descriptor = 'mlp'
    description = 'Simple MLP encoder trained from scratch'
    task = 'any'
    architecture = 'mlp'
    builder = 'MLPBuilder'
    embedding_layer = None
    pooling_layer = None
    input_names = ['features']
    input_dtypes = ['float32']
    output_name = 'embedding'
    dynamic_axes = {'features': {0: 'batch-size'}, 'embedding': {0: 'batch-size'}}
    preprocess_types = {'features': 'DefaultPreprocess'}
    collate_types = {'features': 'DefaultCollate'}
    preprocess_options = {'features': {}}
    collate_options = {'features': {}}

    def __init__(
        self,
        input_size: int,
        hidden_sizes: Tuple[int, ...] = (),
        bias: bool = True,
        activation: Optional[str] = None,
        l2: bool = False,
        preprocess_options: Optional[Dict[str, Dict[str, Any]]] = None,
        collate_options: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        super(MLPStub, self).__init__(
            preprocess_options=preprocess_options,
            collate_options=collate_options,
            input_size=input_size,
            hidden_sizes=hidden_sizes,
            bias=bias,
            activation=activation,
            l2=l2,
        )
        self.input_shapes = [('batch-size', input_size)]
        self.output_shape = (
            'batch-size',
            hidden_sizes[-1] if len(hidden_sizes) > 0 else input_size,
        )


class ResNet50Stub(_CNNStub):
    """ResNet50 model stub."""

    name = 'resnet50'
    display_name = 'resnet-base'
    descriptor = 'resnet50'
    builder = 'ResNet50Builder'
    description = 'ResNet50 pre-trained on ImageNet'
    embedding_layer = 'adaptiveavgpool2d_173'
    pooling_layer = 'avgpool'
    output_shape = ('batch-size', 2048)


class ResNet152Stub(_CNNStub):
    """ResNet152 model stub."""

    name = 'resnet152'
    display_name = 'resnet-large'
    descriptor = 'resnet152'
    builder = 'ResNet152Builder'
    description = 'ResNet152 pre-trained on ImageNet'
    embedding_layer = 'adaptiveavgpool2d_513'
    pooling_layer = 'avgpool'
    output_shape = ('batch-size', 2048)


class EfficientNetB4Stub(_CNNStub):
    """EfficientNetB4 model stub."""

    name = 'efficientnet_b4'
    display_name = 'efficientnet-base'
    descriptor = 'efficientnet_b4'
    default = True
    builder = 'EfficientNetB4Builder'
    description = 'EfficientNet B4 pre-trained on ImageNet'
    embedding_layer = 'dropout_507'
    pooling_layer = 'avgpool'
    output_shape = ('batch-size', 1792)


class EfficientNetB7Stub(_CNNStub):
    """EfficientNetB4 model stub."""

    name = 'efficientnet_b7'
    display_name = 'efficientnet-large'
    descriptor = 'efficientnet_b7'
    builder = 'EfficientNetB7Builder'
    description = 'EfficientNet B7 pre-trained on ImageNet'
    embedding_layer = 'dropout_869'
    pooling_layer = 'avgpool'
    output_shape = ('batch-size', 2560)


class BERTStub(_TextTransformerStub):
    """BERT model stub."""

    name = 'bert-base-cased'
    display_name = 'bert-base-en'
    descriptor = 'bert-base-cased'
    description = 'BERT model pre-trained on BookCorpus and English Wikipedia'
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 768)


class SBERTStub(_TextTransformerStub):
    """SentenceTransformer model stub."""

    name = 'sentence-transformers/msmarco-distilbert-base-v3'
    display_name = 'sbert-base-en'
    descriptor = 'sentence-transformers/msmarco-distilbert-base-v3'
    description = 'Pretrained BERT, fine-tuned on MS Marco'
    default = True
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 768)


class CLIPTextBase32PStub(_HFCLIPTextStub):
    """Huggingface CLIP text model stub."""

    task = 'text-to-image'
    display_name = 'clip-base-en'
    descriptor = 'openai/clip-vit-base-patch32'
    description = 'CLIP base model'
    default = True


class CLIPVisionBase32PStub(_HFCLIPVisionStub):
    """Huggingface CLIP vision model stub."""

    task = 'text-to-image'
    display_name = 'clip-base-en'
    descriptor = 'openai/clip-vit-base-patch32'
    description = 'CLIP base model'
    default = True


class CLIPTextLarge14PStub(_HFCLIPTextStub):
    """Huggingface CLIP text model stub."""

    task = 'text-to-image'
    display_name = 'clip-large-en'
    descriptor = 'openai/clip-vit-large-patch14'
    description = 'CLIP large model with patch size 14'
    output_shape = ('batch-size', 1024)


class CLIPVisionLarge14PStub(_HFCLIPVisionStub):
    """Huggingface CLIP vision model stub."""

    task = 'text-to-image'
    display_name = 'clip-large-en'
    descriptor = 'openai/clip-vit-large-patch14'
    description = 'CLIP large model with patch size 14'
    output_shape = ('batch-size', 1024)


class OpenMCLIPTextVitB32LaionStub(_OpenCLIPTextStub):
    """Open MCLIP text model stub."""

    descriptor = 'xlm-roberta-base-ViT-B-32::laion5b_s13b_b90k'
    display_name = 'clip-base-multi'
    description = 'Open MCLIP "xlm-roberta-base-ViT-B-32::laion5b_s13b_b90k" model'
    output_shape = ('batch-size', 512)


class OpenMCLIPVisionVitB32LaionStub(_OpenCLIPVisionStub):
    """Open MCLIP text model stub."""

    descriptor = 'xlm-roberta-base-ViT-B-32::laion5b_s13b_b90k'
    display_name = 'clip-base-multi'
    description = 'Open MCLIP "xlm-roberta-base-ViT-B-32::laion5b_s13b_b90k" model'
    output_shape = ('batch-size', 512)


class PointNet2Stub(_EmbeddingModelStub):
    """PointNet2 model stub."""

    display_name = 'pointnet-base'
    task = 'mesh-to-mesh'
    default = True
    architecture = 'pointnet'
    builder = 'MeshDataModelBuilder'
    input_names = ['pointcloud']
    input_dtypes = ['float32']
    output_name = 'embedding'
    dynamic_axes = {'pointcloud': {0: 'batch-size'}, 'embedding': {0: 'batch-size'}}
    preprocess_types = {'pointcloud': 'PointCloudPreprocess'}
    collate_types = {'pointcloud': 'DefaultCollate'}
    preprocess_options = {'pointcloud': {'num_points': 2048, 'augmentation': False}}
    collate_options = {'pointcloud': {}}
    descriptor = 'pointnet++'
    name = 'pointnet++'
    description = 'PointNet++ embedding model for 3D mesh point clouds'
    output_shape = ('batch-size', 512)
    input_shapes = [
        (
            'batch-size',
            1024,
            3,
        ),
    ]
    embedding_layer = None
    pooling_layer = None
    supports_onnx_export = False


class _CrossEncoderStub(_ModelStub, metaclass=abc.ABCMeta):
    """Cross encoder model stub."""

    is_embedding_model = False
    architecture = 'transformer'
    builder = 'CrossEncoderBuilder'
    input_names = ['text-pair']
    preprocess_types = {'text-pair': 'TextTuplePreprocess'}
    collate_types = {'text-pair': 'CrossEncoderCollate'}
    preprocess_options = {'text-pair': {}}
    collate_options = {'text-pair': {}}
    embedding_layer = None
    pooling_layer = None
    supports_onnx_export = False


class MSMarcoMiniLMCrossEncoder(_CrossEncoderStub):
    """English cross encoder model stub."""

    name = 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
    display_name = 'crossencoder-base-en'
    descriptor = 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
    description = 'English cross encoder to assess the similarity of two text inputs'
    embedding_layer = None
    pooling_layer = None
    output_shape = ('batch-size', 768)
