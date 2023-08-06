"""Model Exponential Moving Average (EMA)

This plugin keeps expornential moving average of the model parameter as it is training.

The EMA weights are updated as follows at the end of each epoch:
    ema_weights = decay * ema_weights + (1 - decay) * current_weights

Parameters:
    decay (float): the decay parameter. See the comments above.
    num_skip_iterations (int): The number of iterations this plugin waits to initialize the averaged model.
    use_cpu_memory (bool): Use the cpu memory to keep the averaged model. Slow, but useful when there is not enough CUDA memory.
"""
import logging
import torch
from .plugin_base import PluginBase

logger = logging.getLogger(__name__)


class Plugin(PluginBase):
    def __init__(self, decay: float = 0.99, num_skip_iterations: int = 100, use_cpu_memory: bool = False):
        if not (0.0 <= decay <= 1.0):
            raise ValueError(f"Decay must be in the range [0, 1]. decay={decay}")
        self._decay = decay
        self._num_skip_iterations = num_skip_iterations
        self._use_cpu_memory = use_cpu_memory
        self._averaged_model = None
        self._counter = 0

    def on_train_start(self, trainer, model):
        if not self._num_skip_iterations:
            self._init_ema(model)
        self._counter = 0
        self._weights_updated = False

    def on_optimizer_step_start(self, trainer, model, optimizer):
        self._weights_updated = True
        return optimizer

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        if self._weights_updated:  # Weights might not be updated when gradient accumulation was used.
            if self._averaged_model:
                self._averaged_model.update_parameters(model)
            elif self._counter >= self._num_skip_iterations - 1:
                self._init_ema(model)
            else:
                self._counter += 1
            self._weights_updated = False

    def on_train_end(self, trainer, model):
        if self._averaged_model:
            self._copy_weights(list(self._averaged_model.parameters()), list(model.parameters()))
            logger.info("Updated the model with the averaged parameters.")
        self._averaged_model = None

    def on_validation_start(self, trainer, model):
        if self._averaged_model:
            self._model_weights_backup = [p.detach().clone().to('cpu') for p in model.parameters()]
            self._copy_weights(list(self._averaged_model.parameters()), list(model.parameters()))
            logger.debug("Copying the averaged parameters to the model.")

    def on_validation_end(self, trainer, model):
        if self._averaged_model:
            self._copy_weights(self._model_weights_backup, list(model.parameters()))
            self._model_weights_backup = None

    def _init_ema(self, model):
        def ema_avg(averaged_model_params, model_params, num_averaged):
            return self._decay * averaged_model_params + (1 - self._decay) * model_params

        # Keep the copy on CPU memory.
        device = torch.device('cpu') if self._use_cpu_memory else next(model.parameters()).device
        self._averaged_model = torch.optim.swa_utils.AveragedModel(model, avg_fn=ema_avg, device=torch.device('cpu'))
        logger.info(f"Model EMA is enabled with decay={self._decay}, {device=}")

    @staticmethod
    def _copy_weights(src_params, dst_params):
        assert len(src_params) == len(dst_params)
        for src_param, dst_param in zip(src_params, dst_params):
            assert src_param.shape == dst_param.shape
            dst_param.detach().copy_(src_param.to(dst_param.device))
