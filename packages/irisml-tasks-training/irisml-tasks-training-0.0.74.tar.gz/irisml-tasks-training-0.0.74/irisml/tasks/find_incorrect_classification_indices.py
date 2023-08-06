import dataclasses
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Find incorrect classification indices."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        predictions: torch.Tensor
        targets: torch.Tensor

    @dataclasses.dataclass
    class Outputs:
        indices: torch.Tensor

    def execute(self, inputs):
        if len(inputs.predictions) != len(inputs.targets):
            raise ValueError("The number of predictions and targets must be the same.")

        if len(inputs.predictions.shape) == 1:
            predicted_max_indices = inputs.predictions
        elif len(inputs.predictions.shape) == 2:
            predicted_max_indices = torch.argmax(inputs.predictions, dim=1)
        else:
            raise ValueError("The predictions tensor must be 1D or 2D.")

        assert predicted_max_indices.shape == inputs.targets.shape

        indices = []
        for i in range(len(predicted_max_indices)):
            if predicted_max_indices[i] != inputs.targets[i]:
                logger.info(f"Index {i}: Predicted: {predicted_max_indices[i]}, Actual: {inputs.targets[i]}")

                indices.append(i)
        return self.Outputs(torch.tensor(indices))

    def dry_run(self, inputs):
        return self.execute(inputs)
