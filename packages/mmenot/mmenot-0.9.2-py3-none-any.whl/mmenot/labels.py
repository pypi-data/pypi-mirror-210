# pylint: disable=missing-function-docstring
import warnings
from typing import List
from typing import Tuple

from enot.pruning.label_selector import GlobalPruningLabelSelectorByChannels
from enot.pruning.label_selector import GlobalPruningLabelSelectorByRatio
from enot.pruning.label_selector import GlobalPruningLabelSelectorByThreshold
from enot.pruning.label_selector import OptimalPruningLabelSelector
from enot.pruning.label_selector import UniformPruningLabelSelector
from enot.pruning.labels import Label
from enot.pruning.prune import prune_model
from enot.pruning.pruning_info import ModelPruningInfo
from enot_latency_server.client import measure_latency_remote
from mmengine.logging.logger import MMLogger
from torch import nn

from mmenot.utils import count_mmac
from mmenot.utils import export_to_onnx


def labels_equal(pruning_info: ModelPruningInfo, parameter: float, **kwargs) -> List[Label]:
    del kwargs
    if not 0 < parameter < 1:
        raise ValueError(f'Pruning parameter should be in range (0, 1), got {parameter}')

    pruning_ratio = parameter

    label_selector = UniformPruningLabelSelector(pruning_ratio)
    labels_to_prune = label_selector.select(pruning_info)
    return labels_to_prune


def labels_global_channels(pruning_info: ModelPruningInfo, parameter: float, **kwargs) -> List[Label]:
    del kwargs
    if not parameter.is_integer():
        raise ValueError(f'Pruning parameter for global pruning by channels should be integer, got {parameter}')

    channels_number_to_remove = int(parameter)

    label_selector = GlobalPruningLabelSelectorByChannels(channels_number_to_remove)
    labels_to_prune = label_selector.select(pruning_info)
    return labels_to_prune


def labels_global_threshold(pruning_info: ModelPruningInfo, parameter: float, **kwargs) -> List[Label]:
    del kwargs

    criteria_threshold = parameter

    label_selector = GlobalPruningLabelSelectorByThreshold(criteria_threshold)
    labels_to_prune = label_selector.select(pruning_info)
    return labels_to_prune


def labels_global_ratio(pruning_info: ModelPruningInfo, parameter: float, **kwargs) -> List[Label]:
    del kwargs
    if not 0 < parameter < 1:
        raise ValueError(f'Pruning parameter should be in range (0, 1), got {parameter}')

    pruning_ratio = parameter

    label_selector = GlobalPruningLabelSelectorByRatio(pruning_ratio)
    labels_to_prune = label_selector.select(pruning_info)
    return labels_to_prune


def labels_global_mmacs(
    pruning_info: ModelPruningInfo,
    parameter: float,
    model: nn.Module,
    input_shape: Tuple[int, int],
    logger: MMLogger,
    **kwargs,
) -> List[Label]:
    del kwargs
    if not 0 < parameter < 1:
        raise ValueError(f'Pruning parameter should be in range (0, 1), got {parameter}')

    acceleration_ratio = parameter

    baseline_latency = count_mmac(model, input_shape)
    logger.info(f'Baseline latency: {baseline_latency}')

    baseline_model_device = next(model.parameters()).device
    model = model.cpu()

    min_channels = 1000
    max_channels = 100_000
    channel_step = 100
    labels_to_prune: List[Label] = []

    for n_channels in range(min_channels, max_channels + channel_step, channel_step):
        logger.info(f'Number of pruned channels: {n_channels}')
        label_selector = GlobalPruningLabelSelectorByChannels(n_channels)
        labels_to_prune = label_selector.select(pruning_info)
        pruned_model = prune_model(
            model=model,
            pruning_info=pruning_info,
            prune_labels=labels_to_prune,
            inplace=False,
        )

        pruned_latency = count_mmac(pruned_model, input_shape)
        logger.info(f'Current latency: {pruned_latency}')

        if pruned_latency < baseline_latency * acceleration_ratio:
            break

    model = model.to(device=baseline_model_device)  # move model to original device
    return labels_to_prune


def labels_optimal_hw_aware(
    pruning_info: ModelPruningInfo,
    parameter: float,
    n_search_steps: int,
    model: nn.Module,
    input_shape: Tuple[int, int],
    logger: MMLogger,
    deploy_cfg: str,
    model_cfg: str,
    host: str,
    port: int,
    endpoint: str,
    **kwargs,
) -> List[Label]:
    del kwargs
    if not 0 < parameter < 1:
        raise ValueError(f'Pruning parameter should be in range (0, 1), got {parameter}')

    acceleration_ratio = parameter

    def latency_calculation_function(model: nn.Module) -> float:
        logger.info('Sending ONNX to remote latency measurement server...')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            proto = export_to_onnx(model=model, input_shape=input_shape, deploy_cfg=deploy_cfg, model_cfg=model_cfg)

        latency = measure_latency_remote(
            model=proto.SerializeToString(),
            host=host,
            port=port,
            endpoint=endpoint,
        )['latency']
        logger.info(f'Response (latency): {latency}')
        return latency

    baseline_latency = latency_calculation_function(model)
    logger.info(f'Baseline latency: {baseline_latency}')

    target_latency = baseline_latency * acceleration_ratio
    logger.info(f'Target latency: {target_latency}')

    label_selector = OptimalPruningLabelSelector(
        model=model,
        latency_calculation_function=latency_calculation_function,
        target_latency=target_latency,
        n_search_steps=n_search_steps,
    )

    labels_to_prune = label_selector.select(pruning_info)
    return labels_to_prune
