import dataclasses
import itertools
import logging
import math
import multiprocessing
import os
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Extract only targets from a given Dataset.

    If the targets are integers or tensors with same shape, a tensor will be returned. Otherwise, returns a list of targets.

    If the dataset instance provides 'get_targets(index)' method, this task will use it in order to get targets faster.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        targets: typing.Union[typing.List, torch.Tensor] = dataclasses.field(default_factory=list)

    def execute(self, inputs):
        targets = self._collect_targets(inputs.dataset)
        if torch.is_tensor(targets[0]):
            shape = targets[0].shape
            if all(t.shape == shape for t in targets):
                targets = torch.stack(targets)
        elif isinstance(targets[0], int):
            targets = torch.tensor(targets)

        return self.Outputs(targets)

    @staticmethod
    def _worker(dataset, process_index, batch_size, queue):
        start_index = batch_size * process_index
        end_index = min(start_index + batch_size, len(dataset))
        targets = [dataset[i][1] for i in range(start_index, end_index)]
        queue.put((process_index, targets))
        queue.join()

    @staticmethod
    def _collect_targets(dataset):
        if hasattr(dataset, 'get_targets'):
            return [dataset.get_targets(i) for i in range(len(dataset))]

        try:
            num_processes = len(os.sched_getaffinity(0))
            assert num_processes > 0
            batch_size = math.ceil(len(dataset) / num_processes)

            logger.info(f"Using {num_processes} processes to collect {len(dataset)} targets.")

            context = multiprocessing.get_context('fork')
            queue = context.JoinableQueue(num_processes)
            processes = [context.Process(target=Task._worker, args=(dataset, i, batch_size, queue), daemon=True) for i in range(num_processes)]
            for p in processes:
                p.start()

            collected_batches = [None] * num_processes
            for _ in range(num_processes):
                i, batch = queue.get(timeout=3600)
                collected_batches[i] = batch
                queue.task_done()

            for p in processes:
                p.join()

            assert all(b is not None for b in collected_batches)

            targets = list(itertools.chain.from_iterable(collected_batches))
            assert len(targets) == len(dataset)
            return targets

        except Exception:
            logger.exception("Failed to collect targets in parallel.")
            return [t for _, t in dataset]
