"""Temporary patches for OpenMMLab."""
from mmseg.models.utils import resize
from mmseg.utils import SampleList
from torch import Tensor
from torch import nn


def loss_by_feat(self, seg_logits: Tensor, batch_data_samples: SampleList) -> dict:
    """
    Patch for mmseg.models.decode_heads.decode_head.BaseDecodeHead.loss_by_feat:
        removed one line: loss['acc_seg'] = accuracy(seg_logits, seg_label, ignore_index=self.ignore_index)
    """
    seg_label = self._stack_batch_gt(batch_data_samples)  # pylint: disable=W0212
    loss = {}
    seg_logits = resize(
        input=seg_logits,
        size=seg_label.shape[2:],
        mode='bilinear',
        align_corners=self.align_corners,
    )
    if self.sampler is not None:
        seg_weight = self.sampler.sample(seg_logits, seg_label)
    else:
        seg_weight = None
    seg_label = seg_label.squeeze(1)

    if not isinstance(self.loss_decode, nn.ModuleList):
        losses_decode = [self.loss_decode]
    else:
        losses_decode = self.loss_decode
    for loss_decode in losses_decode:
        if loss_decode.loss_name not in loss:
            loss[loss_decode.loss_name] = loss_decode(
                seg_logits, seg_label, weight=seg_weight, ignore_index=self.ignore_index
            )
        else:
            loss[loss_decode.loss_name] += loss_decode(
                seg_logits, seg_label, weight=seg_weight, ignore_index=self.ignore_index
            )

    return loss
