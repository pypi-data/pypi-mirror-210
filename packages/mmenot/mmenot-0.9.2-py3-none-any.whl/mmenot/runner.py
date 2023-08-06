from typing import Dict
from typing import Union

import torch
from mmengine.config import Config
from mmengine.config import ConfigDict
from mmengine.registry import RUNNERS
from mmengine.runner import Runner
from torch import nn

ConfigType = Union[Dict, Config, ConfigDict]


@RUNNERS.register_module()
class PruningRunner(Runner):
    """Pruning runner"""

    def __init__(self, model: Union[nn.Module, Dict, str], *args, **kwargs):
        if isinstance(model, str):
            model = torch.load(model, map_location='cpu')

        assert isinstance(model, (nn.Module, Dict))
        super().__init__(model, *args, **kwargs)
