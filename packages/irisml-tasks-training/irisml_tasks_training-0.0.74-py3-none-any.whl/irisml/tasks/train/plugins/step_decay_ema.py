"""Model Exponential Moving Average (EMA) aligned with step decay.

This plugin keeps expornential moving average of the model parameter as it is training.

"""
from collections import OrderedDict
import logging
import torch
from .plugin_base import PluginBase


logger = logging.getLogger(__name__)


class ExponentialSmoothingState(object):
    """Exponential moving average of model parameters.
    It maintains a smoothed copy of the model's parameter tensors.

    Args:
        model (torch.nn.Module): Model with parameters whose EMA will be kept.
        decay (float): Decay factor for the exponential moving average.
        device ('cuda', 'cpu', None): Device to store the EMA parameters.
    """
    def __init__(self, model, decay: float = 0.999, device=None):
        self.decay = decay
        if device:
            device = torch.device(device)
        else:
            device = next(model.parameters()).device
        self.device = device

        # Register model parameters
        self.load_shadow_from_model(model)

    @torch.no_grad()
    def load_shadow_from_model(self, model):
        self.shadow = OrderedDict()
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone().detach().to(self.device)

    @torch.no_grad()
    def step(self, model, steps):
        # Decay parameters more quickly at the beginning to avoid retaining the random initialization
        decay = min(self.decay, (steps + 1.) / (steps + 10))
        for name, param in model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                self.shadow[name].copy_((1.0 - decay) * param.detach().to(self.device) + decay * self.shadow[name])


class Plugin(PluginBase):
    def __init__(self, decay: float = 0.999):
        if not (0.0 <= decay <= 1.0):
            raise ValueError(f"Decay must be in the range [0, 1]. decay={decay}")
        self._decay = decay
        self.weight_smoothing_states = None
        self._counter = 0

    def on_train_start(self, trainer, model):
        self._init_ema(model)
        self._counter = 0
        self._weights_updated = False

    def on_optimizer_step_start(self, trainer, model, optimizer):
        self._weights_updated = True
        return optimizer

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        if self._weights_updated:  # Weights might not be updated when gradient accumulation was used.
            self._counter += 1
            self.weight_smoothing_states.step(model, self._counter)
            self._weights_updated = False

    def on_train_end(self, trainer, model):
        if self.weight_smoothing_states:
            self._copy_weights(self.weight_smoothing_states.shadow, list(model.named_parameters()))
            logger.info("Updated the model with the Step Decay EMA parameters.")
        self.weight_smoothing_states = None

    def on_validation_start(self, trainer, model):
        if self.weight_smoothing_states:
            self._model_weights_backup = {n: p.detach().clone() for n, p in model.named_parameters()}
            self._copy_weights(self.weight_smoothing_states.shadow, list(model.named_parameters()))
            logger.debug("Copying the Step Decay EMA parameters to the model.")

    def on_validation_end(self, trainer, model):
        if self.weight_smoothing_states:
            self._copy_weights(self._model_weights_backup, list(model.named_parameters()))
            self._model_weights_backup = None

    def _init_ema(self, model):
        self.weight_smoothing_states = ExponentialSmoothingState(model, self._decay)
        logger.info(f"Model Step Decay EMA is enabled with decay={self._decay}, on {self.weight_smoothing_states.device}.")

    @staticmethod
    def _copy_weights(src_params, dst_params):
        for name, dst_param in dst_params:
            if dst_param.requires_grad:
                dst_param.detach().copy_(src_params[name].to(dst_param.device))
