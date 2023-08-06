from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import torch
from enot.pruning.labels import Label
from enot.pruning.prune import prune_model
from enot.pruning.prune_calibrator import PruningCalibrator
from mmengine.registry import LOOPS
from mmengine.runner import Runner
from mmengine.runner.loops import EpochBasedTrainLoop
from torch.utils.data import DataLoader

from mmenot.labels import labels_equal
from mmenot.labels import labels_global_channels
from mmenot.labels import labels_global_mmacs
from mmenot.labels import labels_global_ratio
from mmenot.labels import labels_global_threshold
from mmenot.labels import labels_optimal_hw_aware
from mmenot.utils import check_latency_server
from mmenot.utils import count_mmac


@LOOPS.register_module()
class EpochBasedPruningLoop(EpochBasedTrainLoop):
    """
    Pruning loop.

    Calibrates and prunes model on one epoch.
    """

    _LABEL_SELECTOR_REGISTRY: Dict[str, Callable[..., List[Label]]] = {
        'equal': labels_equal,
        'global': labels_global_ratio,
        'global-mmacs': labels_global_mmacs,
        'optimal-hw-aware': labels_optimal_hw_aware,
        'global-channels': labels_global_channels,
        'global-threshold': labels_global_threshold,
    }
    _PRUNED_MODEL_STATE_DICT_FILENAME = 'pruned_state_dict.pth'
    _PRUNED_MODEL_FILENAME = 'pruned.pth'
    _BASELINE_MODEL_FILENAME = 'baseline.pth'

    def __init__(  # pylint: disable=too-many-arguments
        self,
        runner,
        dataloader: Union[DataLoader, Dict],
        pruning_parameter: float,
        pruning_type: str,
        input_shape: Tuple[int, int],
        host: str,
        port: int,
        endpoint: str,
        deploy_cfg: str,
        model_cfg: str,
        max_prunable_labels: int = 4096,
        n_search_steps: int = 200,
        entry_point: str = 'forward',
        one_batch_only: bool = False,
        max_epochs: int = 1,
        val_begin: int = 1,
        val_interval: int = 1,
        dynamic_intervals=None,
    ) -> None:
        del val_begin, val_interval, dynamic_intervals, max_epochs
        super().__init__(runner=runner, dataloader=dataloader, max_epochs=1)
        self.runner: Runner  # for static analyzer

        self._max_prunable_labels = max_prunable_labels
        self._n_search_steps = n_search_steps
        self._pruning_parameter = pruning_parameter
        self._input_shape: Tuple[int, int] = input_shape
        self._entry_point = entry_point
        self._one_batch_only = one_batch_only

        if pruning_type not in self._LABEL_SELECTOR_REGISTRY:
            raise ValueError(
                f'Unsupported pruning type: {pruning_type}, supported types: {[*self._LABEL_SELECTOR_REGISTRY.keys()]}'
            )
        self._pruning_type = pruning_type

        self._host = host
        self._port = port
        self._endpoint = endpoint
        self._deploy_cfg = deploy_cfg
        self._model_cfg = model_cfg

        if self._pruning_type == 'optimal-hw-aware':
            check_latency_server(host=self._host, port=self._port, endpoint=self._endpoint, logger=self.runner.logger)

        self._pruning_calibrator = PruningCalibrator(
            model=self.runner.model,
            entry_point=self._entry_point,
            max_prunable_labels=self._max_prunable_labels,
        )

    def run(self) -> torch.nn.Module:
        """Launch pruning."""
        # Save baseline before training.
        torch.save(obj=self.runner.model, f=f'{self.runner.work_dir}/{self._BASELINE_MODEL_FILENAME}')

        self.runner.call_hook('before_train')

        self.run_epoch()  # calibrate and prune on one epoch.
        self._prune()  # inplace

        self.runner.save_checkpoint(out_dir=self.runner.work_dir, filename=self._PRUNED_MODEL_STATE_DICT_FILENAME)
        torch.save(obj=self.runner.model, f=f'{self.runner.work_dir}/{self._PRUNED_MODEL_FILENAME}')

        if self.runner.val_loop:
            self.runner.val_loop.run()

        self.runner.call_hook('after_train')
        return self.runner.model

    def run_epoch(self) -> None:
        """Iterate one epoch."""
        self.runner.call_hook('before_train_epoch')
        self.runner.model.eval()  # calibration should be performed in eval mode
        with self._pruning_calibrator:
            dataloader_len, idx = len(self.dataloader), 0  # support inf dataloaders
            for data_batch in self.dataloader:
                self.run_iter(idx, data_batch)
                idx += 1

                if idx >= dataloader_len or self._one_batch_only:
                    break

        self.runner.call_hook('after_train_epoch')  # this hook saves checkpoint
        self._epoch += 1  # pylint: disable=no-member

    def _prune(self) -> None:
        pruning_info = self._pruning_calibrator.pruning_info
        if pruning_info is None:
            raise RuntimeError(
                'Calibrator instance was not used as a context manager or model was calibrated incorrectly'
            )

        if self._pruning_type != 'optimal-hw-aware':
            self.runner.logger.info(f'MMACs: {count_mmac(self.runner.model, self._input_shape)}')

        label_selector = self._LABEL_SELECTOR_REGISTRY[self._pruning_type]
        labels_to_prune = label_selector(
            pruning_info=pruning_info,
            parameter=self._pruning_parameter,
            n_search_steps=self._n_search_steps,
            model=self.runner.model,
            logger=self.runner.logger,
            input_shape=self._input_shape,
            deploy_cfg=self._deploy_cfg,
            model_cfg=self._model_cfg,
            host=self._host,
            port=self._port,
            endpoint=self._endpoint,
        )
        prune_model(model=self.runner.model, pruning_info=pruning_info, prune_labels=labels_to_prune, inplace=True)

        if self._pruning_type != 'optimal-hw-aware':
            self.runner.logger.info(f'MMACs (pruned): {count_mmac(self.runner.model, self._input_shape)}')
