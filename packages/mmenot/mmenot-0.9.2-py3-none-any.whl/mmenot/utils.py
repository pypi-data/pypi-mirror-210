import copy
import os.path as osp
import tempfile
import time
import warnings
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import mmengine
import numpy as np
import onnx
import torch
from enot_latency_server.client import measure_latency_remote
from fvcore.nn.flop_count import FlopCountAnalysis
from mmdeploy.apis import extract_model
from mmdeploy.apis import get_predefined_partition_cfg
from mmdeploy.apis import torch2onnx
from mmdeploy.core import reset_mark_function_count
from mmdeploy.utils import get_partition_config
from mmdeploy.utils import load_config
from mmengine.config import Config
from mmengine.config import ConfigDict
from mmengine.dist import master_only
from mmengine.fileio import FileClient
from mmengine.fileio import join_path
from mmengine.logging.logger import MMLogger
from mmengine.model import is_model_wrapper
from mmengine.model import revert_sync_batchnorm
from mmengine.optim import OptimWrapper
from mmengine.runner import Runner
from mmengine.runner.checkpoint import get_state_dict
from mmengine.runner.checkpoint import save_checkpoint
from mmengine.runner.checkpoint import weights_to_cpu
from mmengine.utils import get_git_hash
from onnx import ModelProto
from onnx import TensorProto
from onnx import helper
from torch import nn

ConfigType = Union[Dict, Config, ConfigDict]


def count_mmac(model: nn.Module, input_shape: Tuple[int, int]) -> float:
    """Computes FLOPs (in MMACs)."""
    device = next(model.parameters()).device

    mode = model.training
    model.eval()

    flop_counter = FlopCountAnalysis(model=model.eval(), inputs=torch.ones(1, 3, *input_shape).to(device))
    flop_counter.unsupported_ops_warnings(False)
    flop_counter.uncalled_modules_warnings(False)
    mflops = flop_counter.total() / 1e6

    model.train(mode)

    return mflops


def check_latency_server(host: str, port: int, endpoint: str, logger: MMLogger) -> None:
    """Checks remote latency server."""
    logger.info('Checking remote latency server...')
    response = measure_latency_remote(
        model=_one_conv_model().SerializeToString(),
        host=host,
        port=port,
        endpoint=endpoint,
        timeout=5,
    )
    logger.info(f'Response received: {response}')


def _one_conv_model() -> ModelProto:
    inputs = helper.make_tensor_value_info(name='input', elem_type=TensorProto.FLOAT, shape=[1, 3, 16, 16])
    weight = helper.make_tensor(
        name='weight',
        data_type=TensorProto.FLOAT,
        dims=(1, 3, 3, 3),
        vals=[1.0] * 1 * 3 * 3 * 3,
    )
    output = helper.make_tensor_value_info(name='output', elem_type=TensorProto.FLOAT, shape=[1, 1, 14, 14])

    conv_node = helper.make_node(
        op_type='Conv',
        inputs=['input', 'weight'],
        outputs=['output'],
        kernel_shape=[3, 3],
    )

    graph = helper.make_graph(
        nodes=[conv_node],
        name='one_conv_model',
        inputs=[inputs],
        outputs=[output],
        initializer=[weight],
    )
    model = helper.make_model(graph)
    model.opset_import[0].version = 13
    onnx.checker.check_model(model)  # type: ignore
    return model


def from_cfg(cls, cfg: ConfigType) -> 'Runner':
    """Patched version of mmengine from_cfg, supports loading from checkpoint."""
    cfg = copy.deepcopy(cfg)

    if isinstance(cfg['model'], str):
        model: nn.Module = torch.load(cfg['model'], map_location='cpu')
    else:
        model = cfg['model']

    runner = cls(
        model=model,
        work_dir=cfg['work_dir'],
        train_dataloader=cfg.get('train_dataloader'),
        val_dataloader=cfg.get('val_dataloader'),
        test_dataloader=cfg.get('test_dataloader'),
        train_cfg=cfg.get('train_cfg'),
        val_cfg=cfg.get('val_cfg'),
        test_cfg=cfg.get('test_cfg'),
        auto_scale_lr=cfg.get('auto_scale_lr'),
        optim_wrapper=cfg.get('optim_wrapper'),
        param_scheduler=cfg.get('param_scheduler'),
        val_evaluator=cfg.get('val_evaluator'),
        test_evaluator=cfg.get('test_evaluator'),
        default_hooks=cfg.get('default_hooks'),
        custom_hooks=cfg.get('custom_hooks'),
        data_preprocessor=cfg.get('data_preprocessor'),
        load_from=cfg.get('load_from'),
        resume=cfg.get('resume', False),
        launcher=cfg.get('launcher', 'none'),
        env_cfg=cfg.get('env_cfg'),  # type: ignore
        log_processor=cfg.get('log_processor'),
        log_level=cfg.get('log_level', 'INFO'),
        visualizer=cfg.get('visualizer'),
        default_scope=cfg.get('default_scope', 'mmengine'),
        randomness=cfg.get('randomness', {'seed': None}),
        experiment_name=cfg.get('experiment_name'),
        cfg=cfg,
    )
    return runner


@master_only
def runner_save_checkpoint(  # pylint: disable=too-many-branches
    self,
    out_dir: str,
    filename: str,
    file_client_args: Optional[dict] = None,
    save_optimizer: bool = True,
    save_param_scheduler: bool = True,
    meta: Optional[dict] = None,
    by_epoch: bool = True,
    backend_args: Optional[dict] = None,
):
    """Patched runner.save_checkpoint: additionaly saves checkpoint (not statedict)."""
    if meta is None:
        meta = {}
    elif not isinstance(meta, dict):
        raise TypeError(f'meta should be a dict or None, but got {type(meta)}')

    if by_epoch:
        # self.epoch increments 1 after
        # `self.call_hook('after_train_epoch)` but `save_checkpoint` is
        # called by `after_train_epoch`` method of `CheckpointHook` so
        # `epoch` should be `self.epoch + 1`
        meta.update(epoch=self.epoch + 1, iter=self.iter)
    else:
        meta.update(epoch=self.epoch, iter=self.iter + 1)

    if file_client_args is not None:
        warnings.warn(
            '"file_client_args" will be deprecated in future. Please use "backend_args" instead', DeprecationWarning
        )
        if backend_args is not None:
            raise ValueError('"file_client_args" and "backend_args" cannot be set at the same time.')

        file_client = FileClient.infer_client(file_client_args, out_dir)
        filepath = file_client.join_path(out_dir, filename.replace('.pth', '_state_dict.pth'))
        checkpoint_filepath = file_client.join_path(out_dir, filename)
    else:
        filepath = join_path(out_dir, filename.replace('.pth', '_state_dict.pth'), backend_args=backend_args)
        checkpoint_filepath = join_path(out_dir, filename, backend_args=backend_args)

    meta.update(
        cfg=self.cfg.pretty_text,
        seed=self.seed,
        experiment_name=self.experiment_name,
        time=time.strftime('%Y%m%d_%H%M%S', time.localtime()),
        mmengine_version=mmengine.__version__ + get_git_hash(),
    )

    if hasattr(self.train_dataloader.dataset, 'metainfo'):
        meta.update(dataset_meta=self.train_dataloader.dataset.metainfo)

    if is_model_wrapper(self.model):
        model = self.model.module
    else:
        model = self.model

    checkpoint = {
        'meta': meta,
        'state_dict': weights_to_cpu(get_state_dict(model)),
        'message_hub': self.message_hub.state_dict(),
    }
    # save optimizer state dict to checkpoint
    if save_optimizer:
        if isinstance(self.optim_wrapper, OptimWrapper):
            checkpoint['optimizer'] = self.optim_wrapper.state_dict()
        else:
            raise TypeError(
                'self.optim_wrapper should be an `OptimWrapper` '
                'or `OptimWrapperDict` instance, but got '
                f'{self.optim_wrapper}'
            )

    # save param scheduler state dict
    if save_param_scheduler and self.param_schedulers is None:
        self.logger.warning(
            '`save_param_scheduler` is True but `self.param_schedulers` is None, so skip saving parameter schedulers'
        )
        save_param_scheduler = False
    if save_param_scheduler:
        if isinstance(self.param_schedulers, dict):
            checkpoint['param_schedulers'] = {}
            for name, schedulers in self.param_schedulers.items():
                checkpoint['param_schedulers'][name] = []
                for scheduler in schedulers:
                    state_dict = scheduler.state_dict()
                    checkpoint['param_schedulers'][name].append(state_dict)
        else:
            checkpoint['param_schedulers'] = []
            for scheduler in self.param_schedulers:  # type: ignore
                state_dict = scheduler.state_dict()  # type: ignore
                checkpoint['param_schedulers'].append(state_dict)

    self.call_hook('before_save_checkpoint', checkpoint=checkpoint)

    save_checkpoint(checkpoint, filepath)
    save_checkpoint(model, checkpoint_filepath)


def load_model_from_checkpoint(
    self,
    model_checkpoint: Optional[str] = None,
    cfg_options: Optional[Dict] = None,
    **kwargs,
) -> torch.nn.Module:
    """Patched BaseTask.build_pytorch_model: loads model from checkpoint, not from cfg."""
    del cfg_options, kwargs

    assert model_checkpoint
    model = torch.load(model_checkpoint, map_location=self.device)

    model = revert_sync_batchnorm(model)
    if hasattr(model, 'backbone') and hasattr(model.backbone, 'switch_to_deploy'):
        model.backbone.switch_to_deploy()  # type: ignore
    model = model.to(self.device)
    model.eval()
    return model


def export_to_onnx(model: nn.Module, input_shape: Tuple[int, int], deploy_cfg: str, model_cfg: str) -> ModelProto:
    """Exports model to ONNX using mm-like workflow."""
    device = next(model.parameters()).device
    model.cpu()

    model_ = copy.deepcopy(model)
    model.to(device)

    with tempfile.TemporaryDirectory() as tempdir:
        # pylint: disable = import-outside-toplevel
        import mmdeploy.codebase.base.task
        import mmdeploy.utils

        _get_input_shape = mmdeploy.utils.get_input_shape
        mmdeploy.utils.get_input_shape = lambda _: input_shape

        _build_pytorch_model = mmdeploy.codebase.base.task.BaseTask.build_pytorch_model
        mmdeploy.codebase.base.task.BaseTask.build_pytorch_model = lambda *args, **kwargs: model_  # type: ignore

        reset_mark_function_count()

        torch2onnx(
            img=np.random.rand(16, 16, 3),
            work_dir=tempdir,
            save_file='model.onnx',
            deploy_cfg=deploy_cfg,
            model_cfg=model_cfg,
        )

        # partition model
        deploy_cfg_ = load_config(deploy_cfg)[0]
        partition_cfgs = get_partition_config(deploy_cfg_)

        if partition_cfgs is not None:
            if 'partition_cfg' in partition_cfgs:
                partition_cfgs = partition_cfgs.get('partition_cfg', None)
            else:
                assert 'type' in partition_cfgs
                partition_cfgs = get_predefined_partition_cfg(deploy_cfg_, partition_cfgs['type'])

            origin_ir_file = osp.join(tempdir, 'model.onnx')

            assert partition_cfgs is not None  # for static type checker
            if len(partition_cfgs) != 1:
                raise ValueError(f'Expected partition number for pruning is 1, got {len(partition_cfgs)}')

            partition_cfg = next(iter(partition_cfgs))
            save_path = osp.join(tempdir, 'model.onnx')
            start = partition_cfg['start']
            end = partition_cfg['end']
            dynamic_axes = partition_cfg.get('dynamic_axes', None)

            extract_model(origin_ir_file, start, end, dynamic_axes=dynamic_axes, save_file=save_path)

        mmdeploy.utils.get_input_shape = _get_input_shape
        mmdeploy.codebase.base.task.BaseTask.build_pytorch_model = _build_pytorch_model

        proto = onnx.load(f'{tempdir}/model.onnx')
        return proto
