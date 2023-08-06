import argparse
import os.path as osp

import torch
from mmengine.config import Config
from mmengine.config import DictAction

from mmenot.loops import EpochBasedPruningLoop  # pylint: disable=unused-import
from mmenot.runner import PruningRunner

# apply patches.
try:
    # pylint: disable=C0412
    import mmseg.models.decode_heads.decode_head

    from mmenot.patches import loss_by_feat

    mmseg.models.decode_heads.decode_head.BaseDecodeHead.loss_by_feat = loss_by_feat
except ImportError:
    pass


def parse_args():  # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(description='Prune a model')
    parser.add_argument('config', help='train config file path')
    parser.add_argument('--checkpoint', type=str, default='', help='path to checkpoint, overrides model config')
    parser.add_argument(
        '--pruning-type',
        type=str,
        help='pruning type: equal, global, global-mmacs, optimal-hw-aware',
        required=True,
    )
    parser.add_argument(
        '--pruning-parameter',
        type=float,
        help='has its own meaning for each type of pruning',
        required=True,
    )
    parser.add_argument(
        '--input-shape',
        type=int,
        nargs='+',
        help='input shape for MMAC / Latency calculation',
        required=True,
    )
    parser.add_argument(
        '--max-prunable-labels',
        type=int,
        default=4096,
        help='maximum number of labels in group which can be pruned',
    )
    parser.add_argument(
        '--n-search-steps',
        type=int,
        default=200,
        help='number of search steps for optimal-hw-aware pruning',
    )
    parser.add_argument('--entry-point', type=str, default='forward', help='pruning entry-point')
    parser.add_argument('--one-batch-only', nargs='?', const=True, default=False, help='prune on one batch only')
    parser.add_argument('--enable-logging', nargs='?', const=True, default=False, help='enable logging')
    parser.add_argument('--disable-cudnn', nargs='?', const=True, default=False, help='disable cudnn')
    parser.add_argument('--host', nargs='?', type=str, default='', help='latency measurement server host')
    parser.add_argument('--port', nargs='?', type=int, default=0, help='latency measurement server port')
    parser.add_argument(
        '--endpoint',
        nargs='?',
        type=str,
        default='measure_latency',
        help='latency measurement endpoint, default: measure_latency',
    )
    parser.add_argument('--deploy-cfg', type=str, default='', help='deploy config path (for hw-aware pruning)')
    parser.add_argument('--work-dir', help='the dir to save logs and models')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.',
    )
    args = parser.parse_args()
    return args


def prune():  # pylint: disable=missing-function-docstring
    args = parse_args()

    if args.pruning_type == 'optimal-hw-aware':
        if not args.host:
            raise ValueError('For "optimal-hw-aware" pruning type the "host" argument should be passed')
        if not args.port:
            raise ValueError('For "optimal-hw-aware" pruning type the "port" argument should be passed')
        if not args.deploy_cfg:
            raise ValueError('For "optimal-hw-aware" pruning type the "deploy-cfg" argument should be passed')

    try:
        # pylint: disable=import-outside-toplevel
        from mmdet.utils import setup_cache_size_limit_of_dynamo

        setup_cache_size_limit_of_dynamo()
    except ImportError:
        pass

    # Will be moved to the main import section when logging will be merged into main branch.
    if args.enable_logging:
        # pylint: disable=C0415
        import enot.logging
        from loguru import logger

        enot.logging.enable_logging()
        logger.add('mmenot.log')

    if args.disable_cudnn:
        torch.backends.cudnn.enabled = False  # type: ignore

    cfg = Config.fromfile(args.config)
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)

    if args.work_dir is not None:
        cfg.work_dir = args.work_dir
    elif cfg.get('work_dir', None) is None:
        cfg.work_dir = osp.join('./work_dirs', osp.splitext(osp.basename(args.config))[0])

    if args.checkpoint:
        cfg['model'] = args.checkpoint  # replace model config by checkpoint path

    cfg['train_cfg']['pruning_type'] = args.pruning_type
    cfg['train_cfg']['pruning_parameter'] = args.pruning_parameter
    cfg['train_cfg']['max_prunable_labels'] = args.max_prunable_labels
    cfg['train_cfg']['n_search_steps'] = args.n_search_steps
    cfg['train_cfg']['input_shape'] = tuple(args.input_shape)
    cfg['train_cfg']['entry_point'] = args.entry_point
    cfg['train_cfg']['one_batch_only'] = args.one_batch_only
    cfg['train_cfg']['host'] = args.host
    cfg['train_cfg']['port'] = args.port
    cfg['train_cfg']['endpoint'] = args.endpoint
    cfg['train_cfg']['deploy_cfg'] = args.deploy_cfg
    cfg['train_cfg']['model_cfg'] = args.config
    cfg['train_cfg']['type'] = 'EpochBasedPruningLoop'
    cfg['train_cfg'].pop('max_iters', None)  # remove max_iters for EpochBasedPruningLoop

    runner = PruningRunner.from_cfg(cfg)
    runner.train()


if __name__ == '__main__':
    prune()
