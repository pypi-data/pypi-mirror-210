import dataclasses
import logging
import typing
import torch

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class LrSchedulerConfig:
    name: typing.Literal['cosine_annealing', 'linear_decreasing', 'linear', 'multistep', 'multistep_with_warm_up'] = 'cosine_annealing'
    warmup_epochs: typing.Optional[int] = None
    warmup_iters: typing.Optional[int] = None
    warmup_lr: typing.Optional[float] = None
    warmup_factor: typing.Optional[float] = None
    warmup_end_factor: typing.Optional[float] = 1.0
    min_lr: typing.Optional[float] = 0.0  # For cosine_annealing LR scheduler
    end_factor: typing.Optional[float] = 1.0  # For linear LR scheduler
    decay_milestones: typing.Optional[typing.List[float]] = None  # For multistep LR scheduler
    decay_rate: typing.Optional[float] = 0.1  # For multistep LR scheduler


class LinearLR(torch.optim.lr_scheduler._LRScheduler):
    """Custom LinearLR implmentation. The official pytorch LinearLR doesn't support end_factor > 1."""
    def __init__(self, optimizer, end_factor, total_iters, last_epoch=-1, verbose=False):
        self._end_factor = end_factor
        self._total_iters = total_iters
        super().__init__(optimizer, last_epoch, verbose)

    def get_lr(self):
        if self.last_epoch == 0 or self.last_epoch > self._total_iters:
            factor = 1
        else:
            factor = 1 + (self._end_factor - 1) * min(self._total_iters, self.last_epoch) / self._total_iters

        return [base_lr * factor for base_lr in self.base_lrs]


class MultiStepLRWithWarmUp(torch.optim.lr_scheduler.MultiStepLR):
    """Custom MultiStepLR implementation. The official pytorch MultiStepLR doesn't support warmup."""
    def __init__(self, optimizer, milestones, gamma, warmup_iters=0, warmup_lr_init=0, last_epoch=-1, verbose=False):
        self._warmup_iters = warmup_iters
        self._warmup_lr_init = warmup_lr_init
        assert self._warmup_iters > 0
        self._warmup_steps = [(v - warmup_lr_init) / self._warmup_iters for v in [group['lr'] for group in optimizer.param_groups]]
        super().__init__(optimizer, milestones, gamma, last_epoch, verbose)
        for param_group in optimizer.param_groups:
            param_group['lr'] = warmup_lr_init

    def get_lr(self):
        if self.last_epoch < self._warmup_iters:
            return [self._warmup_lr_init + self.last_epoch * s for s in self._warmup_steps]
        else:
            return super().get_lr()

    def _get_closed_form_lr(self):
        raise NotImplementedError


def build_lr_scheduler(config, optimizer, num_epochs, num_iterations_per_epoch):
    config = config or LrSchedulerConfig()
    total_iters = num_iterations_per_epoch * num_epochs
    warmup_iters = None

    if config.name == 'multistep_with_warm_up':
        return MultiStepLRWithWarmUp(optimizer,
                                     milestones=[int(total_iters*milestone) for milestone in config.decay_milestones],
                                     gamma=config.decay_rate,
                                     warmup_iters=num_iterations_per_epoch*config.warmup_epochs,
                                     warmup_lr_init=config.warmup_lr)

    if (config.warmup_epochs or config.warmup_iters) and config.warmup_factor:
        if config.warmup_epochs and config.warmup_iters:
            raise ValueError("warmup_epochs and warmup_iters cannot be used at the same time.")

        warmup_iters = num_iterations_per_epoch * config.warmup_epochs if config.warmup_epochs else config.warmup_iters
        logger.debug(f"Use learning rate warmup for {warmup_iters} iterations. {config.warmup_factor=}, {config.warmup_end_factor=}")
        # Make sure total_iters is a positive integer. Some LR scheduler doesn't allow negative values.
        total_iters = max(1, total_iters - warmup_iters)

    scheduler = None
    if config.name == 'cosine_annealing':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, total_iters, eta_min=config.min_lr)
    elif config.name == 'linear_decreasing':
        scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1, end_factor=0, total_iters=total_iters)
    elif config.name == 'linear':
        scheduler = LinearLR(optimizer, end_factor=config.end_factor, total_iters=total_iters)
    elif config.name == 'multistep':
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[int(total_iters*milestone) for milestone in config.decay_milestones], gamma=config.decay_rate)

    if not scheduler:
        raise ValueError(f"Unsupported lr scheduler name: {config.name}")

    if warmup_iters:
        warmup_scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=config.warmup_factor, end_factor=config.warmup_end_factor, total_iters=warmup_iters)
        scheduler = torch.optim.lr_scheduler.SequentialLR(optimizer, [warmup_scheduler, scheduler], milestones=[warmup_iters])

    return scheduler


class LrSchedulerFactory:
    def __init__(self, config: LrSchedulerConfig, num_epochs: int, num_iterations_per_epoch: int):
        self._config = config
        self._num_epochs = num_epochs
        self._num_iterations_per_epoch = num_iterations_per_epoch

    def __call__(self, optimizer):
        return build_lr_scheduler(self._config, optimizer, self._num_epochs, self._num_iterations_per_epoch)
