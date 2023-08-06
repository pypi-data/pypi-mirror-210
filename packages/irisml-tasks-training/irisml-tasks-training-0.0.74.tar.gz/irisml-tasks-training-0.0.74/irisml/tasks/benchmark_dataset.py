import dataclasses
import logging
import time
import typing
import torch.utils.data
import irisml.core
from irisml.tasks.train.build_dataloader import build_dataloader

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Benchmark dataset loading and preprocessing

    Config:
        batch_size (int): Batch size
        num_workers (int): Number of workers for data loading
        num_batches (int): Number of batches to iterate over. If 0, iterate over all batches.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        transform: typing.Callable

    @dataclasses.dataclass
    class Config:
        batch_size: int
        num_workers: int = 4
        num_batches: int = 0

    @dataclasses.dataclass
    class Outputs:
        time_per_batch: float = 0.0

    def execute(self, inputs):
        dataloader = build_dataloader(inputs.dataset, inputs.transform, batch_size=self.config.batch_size, num_workers=self.config.num_workers, shuffle=False, drop_last=False)

        num_batches = min(self.config.num_batches, len(dataloader)) if self.config.num_batches > 0 else len(dataloader)
        start_time = time.time()
        first_batch_time = 0.0
        for i, _ in enumerate(dataloader):
            if i == 0:
                first_batch_time = time.time() - start_time
            elif i >= num_batches:
                break
        end_time = time.time()

        time_per_batch = (end_time - start_time) / num_batches
        logger.info(f"Took {end_time - start_time} seconds to iterate over {num_batches} batches of size {self.config.batch_size}")
        logger.info(f"First batch: {first_batch_time:.3f} seconds")
        logger.info(f"Time per batch: {time_per_batch:.3f} seconds")

        return self.Outputs(time_per_batch=time_per_batch)
