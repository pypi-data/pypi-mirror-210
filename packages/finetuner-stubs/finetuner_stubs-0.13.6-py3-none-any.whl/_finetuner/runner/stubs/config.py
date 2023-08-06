import dataclasses
import inspect
import warnings
from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union

from pydantic import (
    BaseConfig,
    BaseModel,
    Extra,
    Field,
    confloat,
    conint,
    constr,
    create_model,
    root_validator,
    validator,
)
from pydantic.validators import _VALIDATORS

from _finetuner.runner.stubs import callback as callback_stubs
from _finetuner.runner.stubs import model as model_stubs

_PYDANTIC_STANDARD_TYPES = [_type for _type, _ in _VALIDATORS]

_TASK_DESCRIPTIONS = {
    'text-to-text': {
        'description': (
            'Text-to-text search is a type of search that uses Natural Language '
            'Processing (NLP) to match a text query to a text document, or to compare '
            'two or more text documents to find similarities and differences.'
        ),
        'examples': [
            'Finding specific keywords or phrases within a large corpus of text',
            'Retrieving relevant documents or passages in response to a user query',
            'Identifying patterns or trends in large sets of unstructured data',
        ],
    },
    'image-to-image': {
        'description': (
            'Image to image search is a type of search that uses computer vision '
            '(CV) to match an image query to a dataset of images. With image to image '
            'search, you can search for and retrieve images from a collection of '
            'image files.'
        ),
        'examples': [
            'Retrieving similar images based on visual content',
            'Identifying and grouping images based on their content',
            'Facilitating reverse image search, allowing users to search for where an '
            'image originally came from',
        ],
    },
    'text-to-image': {
        'description': (
            'Text to image search is a technology that allows users to search for '
            'images based on text queries. It can be used to detect patterns and '
            'correlations among different types of data, and to improve the accuracy '
            'of search results. With text-to-image search, you can search across '
            'multiple types of data and retrieve results from those different '
            'modalities.'
        ),
        'examples': [
            'Retrieve an image related to a specific keyword or phrase',
            'Identify an image of a specific object or person',
            'Locate an image within a specific category',
        ],
    },
    'mesh-to-mesh': {
        'description': (
            '3D mesh search is a type of search to match a 3D mesh query to a another '
            '3D mesh. This type of search allows users to search for specific 3D '
            'shapes, or to find similar 3D shapes based on their visual similarity.'
        ),
        'examples': [
            'Retrieving similar 3D shapes based on visual content',
            'Identifying and categorizing 3D meshes based on their content',
            'Facilitating reverse 3D mesh search, allowing users to search for where '
            'a 3D mesh originally came from',
        ],
    },
    'any': {
        'description': '-',
        'examples': [],
    },
}


def _get_contained_classes(
    package: Any,
    subtypes: Optional[List[Any]] = None,
    subtypes_only: bool = False,
    dataclasses_only: bool = False,
) -> Dict[str, Any]:
    """Search a package for defined classes."""
    if subtypes is None:
        # set to object, which is a superclass of any class.
        subtypes = [object]

    def classfilter(cls) -> bool:
        if inspect.isclass(cls) and not inspect.isabstract(cls):
            if subtypes_only:
                return any([issubclass(cls, subtype) for subtype in subtypes])
            if dataclasses_only:
                if dataclasses.is_dataclass(cls):
                    return True
                return False
            return True
        return False

    return {
        name: obj
        for name, obj in inspect.getmembers(package, inspect.isclass)
        if classfilter(obj)
    }


def _get_class_names_and_args(
    package: Any,
    subtypes: Optional[List[Any]] = None,
    subtypes_only: bool = False,
    dataclasses_only: bool = False,
    exclude_args: Tuple[str, ...] = (),
    name_attr: str = '__name__',
) -> Tuple[Tuple[str, ...], Dict[str, Type[BaseModel]]]:
    if subtypes is None:
        # set to object, which is a superclass of any class.
        subtypes = [object]

    class OptionsConfig(BaseConfig):

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)

    names = set()
    options = {}
    for _, obj in _get_contained_classes(
        package, subtypes, subtypes_only, dataclasses_only
    ).items():
        name = str(getattr(obj, name_attr))
        names.add(name)
        display_name = getattr(obj, 'display_name', lambda: None)
        if isinstance(display_name, str):
            names.add(display_name)
        _args = {}
        for _, v in inspect.signature(obj).parameters.items():

            if (
                v.name in exclude_args
                or v.kind == v.VAR_KEYWORD
                or v.kind == v.VAR_POSITIONAL
            ):
                continue

            if v.annotation == v.empty:
                if v.default == v.empty or v.default is None:
                    continue
                _annotation = type(v.default)
                if (
                    package.__name__ == 'torch.optim'
                    and v.default == 0
                    and type(v.default) == int
                ):
                    _annotation = float
                if _annotation not in _PYDANTIC_STANDARD_TYPES:
                    continue
            else:
                _annotation = v.annotation

            _args[v.name] = (
                (_annotation, ...) if v.empty == v.default else (_annotation, v.default)
            )

        _pyd_model = create_model(
            f'{obj.__name__}Options', __config__=OptionsConfig, **_args
        )
        options[name] = _pyd_model
        if isinstance(display_name, str):
            options[display_name] = _pyd_model

    return tuple(names), options


def _get_tasks_and_models() -> Dict[str, Dict[str, Any]]:
    """Get a mapping of tasks to models."""
    _model_classes: Dict[str, model_stubs._EmbeddingModelStub] = _get_contained_classes(
        package=model_stubs,
        subtypes=[model_stubs._EmbeddingModelStub],
        subtypes_only=True,
    )
    _tasks2models = defaultdict(set)
    _descriptor2data = dict()
    for _, obj in _model_classes.items():
        _tasks2models[obj.task].add(obj.display_name)
        _descriptor2data[obj.display_name] = {
            'name': obj.display_name,
            'default': obj.default,
            'description': obj.description,
        }
    _tasks_and_models = {}
    for name, models in _tasks2models.items():
        _task_info = {
            'models': list([_descriptor2data[x] for x in _tasks2models[name]]),
            **_TASK_DESCRIPTIONS[name],
        }
        _tasks_and_models[name] = _task_info

    return _tasks_and_models


def _get_literals() -> Dict[str, Tuple[Tuple[str, ...], Dict[str, Type[BaseModel]]]]:

    _models, _model_options = _get_class_names_and_args(
        model_stubs,
        subtypes=[model_stubs._ModelStub],
        subtypes_only=True,
        exclude_args=('preprocess_options', 'collate_options'),
        name_attr='descriptor',
    )
    _callbacks, _callback_options = _get_class_names_and_args(
        callback_stubs, dataclasses_only=True
    )
    _literals = {
        'models': (_models, _model_options),
        'callbacks': (_callbacks, _callback_options),
        'losses': (tuple(), {}),
        'miners': (tuple(), {}),
        'optimizers': (tuple(), {}),
        'schedulers': tuple(),
    }

    try:
        import torch
        import transformers
        from pytorch_metric_learning.losses import BaseMetricLossFunction
        from pytorch_metric_learning.miners import BaseMiner

        from finetuner import loss, miner

        _literals['losses'] = _get_class_names_and_args(
            loss,
            subtypes_only=True,
            subtypes=[
                BaseMetricLossFunction,
                loss.MarginMSELoss,
                loss.CosineSimilarityLoss,
            ],
        )
        _literals['miners'] = _get_class_names_and_args(
            miner, subtypes_only=True, subtypes=[BaseMiner]
        )
        _literals['optimizers'] = _get_class_names_and_args(
            torch.optim, subtypes_only=True, subtypes=[torch.optim.Optimizer]
        )
        _literals['schedulers'] = tuple(e.value for e in transformers.SchedulerType)
    except (ImportError, ModuleNotFoundError):
        pass

    return _literals


def _get_json_schema_conditions(
    name_arg: str,
    options_arg: str,
    options: Dict[str, Type[BaseModel]],
) -> List[Dict[str, Any]]:

    conditions = []
    _options: Dict[Union[str, None], Type[BaseModel]] = deepcopy(options)

    for name, options_model in _options.items():
        _options_schema = dict(options_model.schema())
        _options_schema['additionalProperties'] = False
        condition = {
            'if': {'properties': {name_arg: {'const': name}}, 'required': [name_arg]},
            'then': {'properties': {options_arg: _options_schema}},
        }
        if len(_options_schema.get('required', [])) > 0:
            condition['then']['required'] = [options_arg]
        else:
            _type = _options_schema.pop('type')
            condition['then']['properties'][options_arg]['anyOf'] = [
                {'type': 'null'},
                {'type': _type},
            ]

        conditions.append(condition)

    return conditions


def _patch_nullable_fields(schema, _model):
    for prop, value in schema.get('properties', {}).items():
        field = [x for x in _model.__fields__.values() if x.alias == prop][0]
        if field.allow_none:
            if 'enum' in value:
                value['enum'] = value['enum'] + [None]
            if 'type' in value:
                value['anyOf'] = [{'type': value.pop('type')}]
            elif '$ref' in value:
                if issubclass(field.type_, BaseModel):
                    value['title'] = (
                        field.type_.__config__.title or field.type_.__name__
                    )
                value['anyOf'] = [{'$ref': value.pop('$ref')}]
            if 'anyOf' not in value:
                value['anyOf'] = [{'type': 'object'}]
            value['anyOf'].append({'type': 'null'})


tasks2models = _get_tasks_and_models()
literals = _get_literals()
models, model_options = literals['models']
callbacks, callback_options = literals['callbacks']
losses, loss_options = literals['losses']
miners, miner_options = literals['miners']
optimizers, optimizer_options = literals['optimizers']
schedulers = literals['schedulers']

ModelType = Literal[models] if len(models) > 0 else constr(min_length=1)
CallbackType = Literal[callbacks] if len(callbacks) > 0 else constr(min_length=1)
LossType = Literal[losses] if len(losses) > 0 else constr(min_length=1)
MinerType = Literal[miners] if len(miners) > 0 else Optional[constr(min_length=1)]
OptimizerType = Literal[optimizers] if len(optimizers) > 0 else constr(min_length=1)
SchedulerType = Literal[schedulers] if len(schedulers) > 0 else constr(min_length=1)


class ModelConfig(BaseModel):
    name: Union[ModelType, None] = Field(
        default=None,
        description='The name of the backbone model that will be fine-tuned.',
    )
    artifact: Union[constr(min_length=1), None] = Field(
        default=None, description='The name of a model artifact to further fine-tune.'
    )
    freeze: bool = Field(
        default=False,
        description=(
            'If set to True all layers in the backbone model except the last '
            'one will be freezed.'
        ),
    )
    output_dim: Union[conint(gt=0), None] = Field(
        default=None,
        description=(
            'The embedding model\'s output dimensionality. If set, a projection '
            'head will be attached to the backbone model.'
        ),
    )
    options: Union[Dict[str, Any], None] = Field(
        default=None,
        description=(
            'Additional arguments to pass to the backbone model construction. These '
            'are model specific options and are different depending on the model you '
            'choose.'
        ),
    )
    to_onnx: bool = Field(
        default=False, description='If set `True` will convert model as onnx.'
    )

    @root_validator
    def check_model_or_artifact(cls, values):
        if not (values.get('name') or values.get('artifact')):
            raise ValueError(
                'Either a model configuration ("model" key) or an artifact should be '
                'provided.'
            )
        else:
            return values

    @validator('to_onnx')
    def valid_to_onnx(cls, v_to_onnx, values):
        (
            stubs_dict_descriptor,
            stubs_dict_display_name,
        ) = model_stubs.get_model_stubs_dict()
        v_name = values['name']
        if v_name in stubs_dict_descriptor:
            stubs_dict = stubs_dict_descriptor
        else:
            stubs_dict = stubs_dict_display_name
        if v_to_onnx:
            for c in stubs_dict[v_name]:
                if not c.supports_onnx_export:
                    raise ValueError(
                        f'The backbone {v_name} mentioned in the config does not '
                        'support ONNX export. Thus you need to set to_onnx=False.'
                    )
        return v_to_onnx

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)
            _name_and_artifact_condition = {
                'if': {
                    'anyOf': [
                        {'properties': {'name': False}},
                        {'properties': {'name': {'type': 'null'}}},
                    ]
                },
                'then': {
                    'allOf': [
                        {
                            'required': ['artifact'],
                            '_message': 'Either \'name\' or \'artifact\' is required',
                        },
                        {
                            'properties': {
                                'artifact': {
                                    'type': 'string',
                                    '_message': (
                                        'Either \'name\' or \'artifact\' is required'
                                    ),
                                },
                            }
                        },
                    ]
                },
                'else': {
                    'properties': {
                        'artifact': {
                            'type': 'null',
                            '_message': (
                                'Fields \'name\' and \'artifact\' can not be set at '
                                'the same time'
                            ),
                        },
                    }
                },
            }
            conditions = [_name_and_artifact_condition]
            conditions.extend(
                _get_json_schema_conditions(
                    name_arg='name',
                    options_arg='options',
                    options=model_options,
                )
            )
            schema['allOf'] = conditions


class DataConfig(BaseModel):
    train_data: constr(min_length=1) = Field(
        description='The training data to use for fine-tuning the model.'
    )
    eval_data: Union[constr(min_length=1), None] = Field(
        default=None,
        description=(
            'Optional evaluation data to use for the fine-tuning run. '
            'Validation loss is computed per epoch agaist this dataset.'
        ),
    )
    val_split: confloat(ge=0, lt=1) = Field(
        default=0.0,
        description=(
            'Determines which portion of the `train_data` specified in the '
            '`fit` function is held out and used for validation (and not for '
            'training). If it is set to 0, or an `eval_data` parameter is provided '
            'to the `fit` function, no training data is held out for validation.'
        ),
    )
    evaluate: bool = Field(
        default=False,
        description=(
            'If set to `True`, Finetuner will automatically initialize an evaluation '
            'callback with the evaluation data to calculate retrieval metrics.'
        ),
    )
    num_workers: conint(gt=0) = Field(
        default=8, description='Number of workers used by the dataloaders.'
    )
    sampler: Literal['auto', 'class', 'random'] = Field(
        default='auto',
        description=(
            'Determines which sampling method will be used in the case that the data '
            'is labeled. By default is `auto`, meaning that the appropriate sampler '
            'will be chosen depending on the loss function used. '
            'If set to `random` then `num_items_per_class` is disregarded.'
        ),
    )
    num_items_per_class: conint(gt=1) = Field(
        default=4,
        description=(
            'Number of same-class items that will make it in the batch. '
            'Only relevant if `sampler` is set to `class`.'
        ),
    )

    class Config:
        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)


class CallbackConfig(BaseModel):
    name: CallbackType = Field(description='The name of the callback.')
    options: Union[Dict[str, Any], None] = Field(
        default=None,
        description='Arguments to pass to the callback construction.',
    )

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)
            conditions = _get_json_schema_conditions(
                name_arg='name', options_arg='options', options=callback_options
            )
            if len(conditions) > 0:
                schema['allOf'] = conditions


class SchedulerOptionsConfig(BaseModel):
    num_warmup_steps: conint(ge=0) = Field(
        default=0,
        description=(
            'Number of warmup steps to use for the scheduler. It determines the number '
            'of processed batches at the beginning which the scheduler applies a '
            'specific warmup behavior.'
        ),
    )
    num_training_steps: Union[conint(ge=0), Literal['auto']] = Field(
        default='auto',
        description=(
            'Number of training steps to use for the scheduler. If set to `auto` it '
            'is set automatically to the total number of steps (batch_size * epochs).'
        ),
    )
    scheduler_step: Literal['batch', 'epoch'] = Field(
        default='batch',
        description=(
            'At which interval should the learning rate scheduler\'s '
            'step function be called. Valid options are `batch` and `epoch`.'
        ),
    )

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)


class HyperParametersConfig(BaseModel):
    optimizer: OptimizerType = Field(
        default='Adam',
        description=(
            'Name of the optimizer that will be used for fine-tuning. See '
            'https://pytorch.org/docs/stable/optim.html for available options.'
        ),
    )
    optimizer_options: Union[Dict[str, Any], None] = Field(
        default=None,
        description='Specify arguments to pass to the optimizer construction.',
    )
    loss: LossType = Field(
        default='TripletMarginLoss',
        description=(
            'Name of the loss function to use for fine-tuning. See '
            'https://finetuner.jina.ai/api/finetuner/#finetuner.fit for '
            'available options.'
        ),
    )
    loss_options: Union[Dict[str, Any], None] = Field(
        default=None,
        description='Specify arguments to pass to the loss construction.',
    )
    loss_optimizer: Union[OptimizerType, None] = Field(
        default=None,
        description=(
            'Name of the optimizer that will be used for fine-tuning, specifically '
            'finetuning the parameters of the loss function if it is a function '
            'that requires an optimizer. If left as None then the same type of '
            'optimizer will be used as the one for fine-tuning the rest of the model'
        ),
    )
    loss_optimizer_options: Union[Dict[str, Any], None] = Field(
        default=None,
        description='Specify arguments to pass to the optimizer of the loss function.',
    )
    miner: Union[MinerType, None] = Field(
        default=None,
        description=(
            'Specify the miner that will be used for fine-tuning. See '
            'https://kevinmusgrave.github.io/pytorch-metric-learning/miners/ for '
            'available options.'
        ),
    )
    miner_options: Union[Dict[str, Any], None] = Field(
        default=None,
        description=(
            'Specify arguments to pass to the miner construction. See '
            'https://kevinmusgrave.github.io/pytorch-metric-learning/miners/ for '
            'detailed information about all possible attributes.'
        ),
    )
    scheduler: Union[SchedulerType, None] = Field(
        default=None,
        description=(
            'Specify the learning rate scheduler that will be used for fine-tuning.'
        ),
    )
    scheduler_options: Union[SchedulerOptionsConfig, None] = Field(
        default=SchedulerOptionsConfig(),
        description='Specify options for the scheduler construction.',
    )
    batch_size: Union[conint(gt=0), None] = Field(
        default=None,
        description=(
            'The training batch size, set to None for automatic configuration.'
        ),
    )
    learning_rate: Union[confloat(ge=0, lt=1), None] = Field(
        default=None,
        description=(
            'The learning rate to use during training. If given, this argument '
            'overwrites the optimizer default learning rate or the learning rate '
            'specified in the optimizer options.'
        ),
    )
    epochs: conint(ge=0, lt=50) = Field(
        default=5, description='Number of fine-tuning epochs.'
    )

    @validator('scheduler_options')
    def set_default_scheduler_options(cls, v):
        return v or SchedulerOptionsConfig()

    @validator('batch_size')
    def batch_size_warning(cls, v):
        if v and v >= 256:
            warnings.warn('batch_size >= 256 may result in OOM (out of memory) errors.')
        return v

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)
            optimizer_conditions = _get_json_schema_conditions(
                name_arg='optimizer',
                options_arg='optimizer_options',
                options=optimizer_options,
            )
            loss_conditions = _get_json_schema_conditions(
                name_arg='loss', options_arg='loss_options', options=loss_options
            )
            loss_optimizer_conditions = _get_json_schema_conditions(
                name_arg='loss_optimizer',
                options_arg='loss_optimizer_options',
                options=optimizer_options,
            )
            miner_conditions = _get_json_schema_conditions(
                name_arg='miner',
                options_arg='miner_options',
                options=miner_options,
            )
            conditions = (
                optimizer_conditions
                + loss_conditions
                + loss_optimizer_conditions
                + miner_conditions
            )
            if len(conditions) > 0:
                schema['allOf'] = conditions


class RunConfig(BaseModel):
    public: bool = Field(
        default=False,
        description='If set to True artifact will be set as public artifact.',
    )
    run_name: Union[constr(min_length=1), None] = Field(
        default=None, description='Specify a run name.'
    )
    experiment_name: Union[constr(min_length=1), None] = Field(
        default=None, description='Specify an experiment name.'
    )

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)


class FinetuningConfig(RunConfig):
    model: ModelConfig = Field(description='Model configuration.')
    data: DataConfig = Field(description='Data configuration.')
    callbacks: List[CallbackConfig] = Field(
        default_factory=lambda: [],
        description='List of callbacks that will be used during fine-tuning.',
    )
    hyper_parameters: HyperParametersConfig = Field(
        default=HyperParametersConfig(), description='Hyper-parameter configuration.'
    )


class RelationMiningConfig(BaseModel):
    models: List[str] = Field(description='List of models to use for relation mining.')
    num_relations: int = Field(description='Number of relations to mine per query.')

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)


class RawDataConfig(BaseModel):
    queries: str = Field(description='Name of artifact with queries.')
    corpus: str = Field(description='Name of artifact with documents.')

    class Config:

        extra = Extra.forbid
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: BaseModel, *_, **__) -> None:
            _patch_nullable_fields(schema, model)


class DataGenerationConfig(RunConfig):
    data: RawDataConfig = Field(
        description='Configuration for raw query and corpus data.'
    )
    relation_mining: RelationMiningConfig = Field(description='Relation mining config.')
    cross_encoder: str = Field(description='Descriptor of cross encoder.')
    max_num_docs: Union[int, None] = Field(
        default=None, description='Maximum number of documents to consider.'
    )


__FINETUNER_RUNNER_MODELS__ = tasks2models
__FINETUNER_RUNNER_CONFIG_TRAINING_JSONSCHEMA__ = FinetuningConfig.schema()
__FINETUNER_RUNNER_CONFIG_GENERATION_JSONSCHEMA__ = DataGenerationConfig.schema()
__FINETUNER_RUNNER_CONFIG_DATAPATHS__ = [
    'data.train_data',
    'data.eval_data',
    'data.queries',
    'data.corpus',
    'callbacks.ANY.options.query_data',
    'callbacks.ANY.options.index_data',
]
__FINETUNER_RUNNER_METADATA__ = {
    'models': __FINETUNER_RUNNER_MODELS__,
    'schemas': {
        'training': __FINETUNER_RUNNER_CONFIG_TRAINING_JSONSCHEMA__,
        'generation': __FINETUNER_RUNNER_CONFIG_GENERATION_JSONSCHEMA__,
    },
    'datapaths': __FINETUNER_RUNNER_CONFIG_DATAPATHS__,
}
