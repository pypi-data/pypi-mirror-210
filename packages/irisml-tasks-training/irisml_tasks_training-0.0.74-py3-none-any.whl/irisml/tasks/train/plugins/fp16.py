"""Run the model in half precision.

Not recommended in the trianing phase. Use AMP plugin instead.
"""
import logging
from .plugin_base import PluginBase

logger = logging.getLogger(__name__)


def _make_half(tensor_or_list):
    if isinstance(tensor_or_list, list):
        return [_make_half(x) for x in tensor_or_list]
    return tensor_or_list.half()


class Plugin(PluginBase):
    def on_train_start(self, trainer, model):
        logger.info("Converting the model to FP16.")
        model.half()

    def on_train_end(self, trainer, model):
        model.float()

    def on_train_batch_start(self, trainer, model, batch, batch_index):
        assert len(batch) == 2
        return _make_half(batch[0]), batch[1]

    def on_validation_batch_start(self, trainer, model, batch, batch_index):
        assert len(batch) == 2
        return _make_half(batch[0]), batch[1]

    def on_prediction_batch_start(self, trainer, model, batch, batch_index):
        assert len(batch) == 2
        return _make_half(batch[0]), batch[1]

    def on_prediction_start(self, trainer, model):
        logger.info("Converting the model to FP16.")
        model.half()

    def on_prediction_end(self, trainer, model):
        model.float()
