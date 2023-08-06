from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, TypeVar, Union

CallbackStubType = TypeVar('CallbackStubType')


@dataclass
class BestModelCheckpoint:
    # noinspection PyUnresolvedReferences
    """
    Callback to save the best model across all epochs

    An option this callback provides include:
    - Definition of 'best'; which quantity to monitor and whether it should be
        maximized or minimized.

    :param monitor: if `monitor='train_loss'` best model saved will be according
        to the training loss, while if `monitor='val_loss'` best model saved will be
        according to the validation loss.
    :param mode: one of {'auto', 'min', 'max'}. The decision to overwrite the
        currently saved model is made based on either the maximization or the
        minimization of the monitored quantity.
        For an evaluation metric, this should be `max`, for `val_loss` this should
        be `min`, etc. In `auto` mode, the mode is set to `min` if `monitor='loss'`
        or `monitor='val_loss'` and to `max` otherwise.
    :param verbose: Whether to log notifications when a checkpoint is saved.
    """
    monitor: str = 'val_loss'
    mode: str = 'auto'


@dataclass
class TrainingCheckpoint:
    # noinspection PyUnresolvedReferences
    """
    Callback that saves the tuner state at every epoch or the last k epochs.

    :param last_k_epochs: This parameter is an integer. Only the most
        recent k checkpoints will be kept. Older checkpoints are deleted.
    :param verbose: Whether to log notifications when a checkpoint is saved/deleted.
    """
    last_k_epochs: int = 1


@dataclass
class WandBLogger:
    # noinspection PyUnresolvedReferences
    """
    `Weights & Biases <https://wandb.ai/site>`_ logger to log metrics for training and
    validation.
    This callback will use the
    Weights & Biases Anonymous Mode <https://docs.wandb.ai/ref/app/features/anon>
    to track your experiment without WandB account needed.

    :param metrics_logger_step: Whether to log metrics per batch or per epoch.
    :param wandb_args: Keyword arguments that are passed to ``wandb.init`` function.
    """
    metrics_logger_step: Literal['batch', 'epoch'] = 'epoch'
    wandb_args: Union[Dict[str, Any], None] = None


@dataclass
class EarlyStopping:
    # noinspection PyUnresolvedReferences
    """
    Callback to stop training when a monitored metric has stopped improving.
    A `finetuner.fit()` training loop will check at the end of every epoch whether
    the monitored metric is still improving or not.

    :param monitor: if `monitor='train_loss'` best model saved will be according
        to the training loss, while if `monitor='val_loss'` best model saved will be
        according to the validation loss.
    :param mode: one of {'auto', 'min', 'max'}. The decision to overwrite the
        current best monitor value is made based on either the maximization or the
        minimization of the monitored quantity.
        For an evaluation metric, this should be `max`, for `val_loss` this should
        be `min`, etc. In `auto` mode, the mode is set to `min` if `monitor='loss'`
        or `monitor='val_loss'` and to `max` otherwise.
    :param patience: integer, the number of epochs after which the training is
        stopped if there is no improvement. For example for `patience = 2`', if the
        model doesn't improve for 2 consecutive epochs, the training is stopped.
    :param min_delta: Minimum change in the monitored quantity to qualify as an
        improvement, i.e. an absolute change of less than min_delta, will count as
        no improvement.
    :param baseline: Baseline value for the monitored quantity.
        Training will stop if the model doesn't show improvement over the
        baseline.
    :param verbose: Whether to log score improvement events.
    """

    monitor: str = 'val_loss'
    mode: str = 'auto'
    patience: int = 2
    min_delta: int = 0
    baseline: Optional[float] = None


@dataclass
class EvaluationCallback:
    # noinspection PyUnresolvedReferences
    """
    A callback that uses the Evaluator to calculate IR metrics at the end of each epoch.
    When used with other callbacks that rely on metrics, like checkpoints and logging,
    this callback should be defined first, so that it precedes in execution.

    :param query_data: Search data used by the evaluator at the end of each epoch,
        to evaluate the model.
    :param index_data: Index data or catalog used by the evaluator at the end of
        each epoch, to evaluate the model.
    :param model: The model used for encoding the data in `query_data`. If no
        `index_model` is provided, this model is also used to encode the documents
        in `index_data`.
    :param index_model: The model used for encoding the data in `index_data`.
    :param multi_modal: A flag that indicates whether docs should be treated as
        multi-modal docs. Multi-modal docs are expected to host different modalities
        in ``.chunks``.
    :param batch_size: Batch size for computing embeddings.
    :param exclude_self: Whether to exclude self when matching.
    :param limit: The number of top search results to consider when computing the
        evaluation metrics.
    :param distance: The type of distance metric to use when matching query and
        index docs, available options are ``'cosine'``, ``'euclidean'`` and
        ``'sqeuclidean'``.
    :param steps_per_interval: For large datasets, one may want to evaluate multiple
        times during each epoch. This parameter allows to specify a number of
        batches after which an evaluation should be performed. If set to `None`, an
        evaluation is performed only at the end of each epoch.
    :param gather_examples: If set to `True`, the callback will store results of
            example queries.
    :param num_example_queries: The number of example queries to store in the
        tuner if `gather_examples` is set to `True`.
    :param num_workers: The number of workers to use when matching query and
        index data.
    :param caption: Specifies the name of the evaluation dataset. If set, this
        caption is  attached as prefix to the names of the  retrieval metrics.
        If you are using multiple evaluation callbacks this is required to prevent
        callbacks from overwriting of the metrics of each other.
    :param output_model_names: Whether to add the model names to the captions of the
        metrics.
    :param query_sample_size: For large datasets you might not want to train on all
        queries, because this will take to much time and do not contribute much to
        the resolution of the retrieval metrics. Therefore, a number of samples to
        draw from the query set can be set via this parameter.
    """

    query_data: str
    index_data: Optional[str] = None
    model: Optional[str] = None
    index_model: Optional[str] = None
    multi_modal: bool = False
    batch_size: int = 32
    exclude_self: bool = True
    limit: int = 20
    distance: str = 'cosine'
    steps_per_interval: Optional[int] = None
    gather_examples: bool = False
    num_example_queries: int = 5
    num_workers: int = 8
    caption: Optional[str] = None
    output_model_names: bool = False
    query_sample_size: Optional[int] = None


@dataclass
class WiSEFTCallback:
    # noinspection PyUnresolvedReferences
    """
    Callback to apply WiSE-FT to fine-tuned models.

    WiSE-FT: Mitchell et al. Robust fine-tuning of zero-shot models, takes
        pre-trained model and fine-tuned model together and merge their weights
        based on coefficient `alpha`. `alpha` should be greater equal than 0
        while less equal than 1.

    :param alpha: The coefficient controls the weights between pre-trained model and
        fine-tuned model. If `alpha` set to 0, fully use pre-trained weights,
        if `alpha` set to 1, fully use fine-tuned model.
    :param save_dir: string, path to save the model file.
    :param verbose: Whether to log notifications when a checkpoint is saved.
    """

    alpha: Union[int, float] = 0.4
