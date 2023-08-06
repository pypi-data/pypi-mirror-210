import dataclasses
import logging
import math
import irisml.core
import torch

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Convert number of iterations to number of epochs. Min value is 1."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        batch_size: int
        num_iterations: int
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        num_epochs: int

    def execute(self, inputs):
        num_epochs = max(math.ceil(inputs.batch_size * inputs.num_iterations / len(inputs.dataset)), 1)

        return self.Outputs(num_epochs)

    def dry_run(self, inputs):
        return self.execute(inputs)
