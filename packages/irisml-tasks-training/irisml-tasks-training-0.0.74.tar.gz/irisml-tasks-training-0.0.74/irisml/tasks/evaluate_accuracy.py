import dataclasses
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Calculate accuracy of the given prediction results.

    This task supports only multiclass classification.

    Inputs:
        predictions: The prediction results. The shape is (N, num_classes) or (N, ). If the shape is (N, ), the values are the indexes of the maximum values.
        targets: The ground truth labels. The shape is (N, ) or (N, 1).
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Inputs:
        predictions: torch.Tensor  # Shape: (N, num_classes) or (N, )
        targets: torch.Tensor  # Shape: (N, ) or (N, 1)

    @dataclasses.dataclass
    class Outputs:
        accuracy: float = 0

    def execute(self, inputs):
        if len(inputs.predictions) == 0 or len(inputs.targets) == 0:
            raise ValueError("The predictions or the targets are empty.")

        if inputs.predictions.shape[0] != inputs.targets.shape[0]:
            raise ValueError(f"The predictions or the targets have unexpected shape: {inputs.predictions.shape} vs {inputs.targets.shape}")

        if len(inputs.predictions.shape) == 1:
            predicted_max_indexes = inputs.predictions
        elif len(inputs.predictions.shape) == 2:
            _, predicted_max_indexes = inputs.predictions.max(dim=1)
            predicted_max_indexes = predicted_max_indexes.flatten()
        else:
            raise ValueError(f"Unexpected shape of the predictions: {inputs.predictions.shape}")

        targets = inputs.targets.flatten()

        if targets.shape != predicted_max_indexes.shape:
            raise RuntimeError(f"The predictions or the targets have unexpected shape: {targets.shape} vs {predicted_max_indexes.shape}")

        accuracy = ((predicted_max_indexes == targets).sum() / len(targets)).item()

        logger.info(f"Accuracy: {accuracy:.3f}")
        return self.Outputs(accuracy)
