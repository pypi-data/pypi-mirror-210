import dataclasses
import logging
import time
import torch
from irisml.tasks.train_with_gradient_cache import GradientCachingMixin, GradientCachingTrainer
from irisml.tasks.benchmark_model import Task as BenchmarkModelTask

logger = logging.getLogger(__name__)


class Task(BenchmarkModelTask):
    """Benchmark a given model using a given dataset with grad caching. Useful for cases which require sub batching.

    Config:
        sub_batch_size (int)
    """
    VERSION = '0.0.2'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Config(BenchmarkModelTask.Config):
        sub_batch_size: int = 1

    def _training_step(self, model, inputs, targets, device, plugins):
        assert self.config.batch_size % self.config.sub_batch_size == 0, 'batch_size must be divisible by sub_batch_size'
        grad_cache_wrapper = BenchmarkGradientCachingTrainer(self.config.sub_batch_size, plugins)
        return grad_cache_wrapper._training_step(model, inputs, targets, device)


class BenchmarkGradientCachingTrainer(GradientCachingTrainer):

    def __init__(self, sub_batch_size, plugins):
        self._sub_batch_size = sub_batch_size
        self._plugins = plugins

    def _training_step(self, model, inputs, targets, device):

        sub_batches = list(zip(self._split_tensor_or_list(inputs), self._split_tensor_or_list(targets)))
        _model = GradientCachingMixin.ModelWrapper(model, device)

        self._synchronize(device)
        start = time.time()
        _batch = (inputs, targets)
        loss, features, features_local, rng_states = self._forward_pass(_model, _batch, sub_batches)
        self._synchronize(device)
        forward_time_first = time.time() - start

        start = time.time()
        loss = self._calculate_gradients(model, loss)
        self._synchronize(device)
        # NOTE: not the actual backward pass, but the time it takes to calculate the gradients with a backward pass
        backward_time = time.time() - start

        start = time.time()
        self._forward_backward_pass_with_gradients(model, _model, features, features_local, rng_states, sub_batches)
        self._synchronize(device)
        forward_time_second = time.time() - start

        return loss, forward_time_first + forward_time_second, backward_time

    @staticmethod
    def _synchronize(device):
        if device.type == 'cuda':
            torch.cuda.synchronize()
