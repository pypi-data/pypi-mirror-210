import dataclasses
import torch
import irisml.core


class DatasetWithTargets(torch.utils.data.Dataset):
    def __init__(self, dataset, targets):
        super().__init__()
        self._dataset = dataset
        self._targets = targets

    def __len__(self):
        return len(self._dataset)

    def __getitem__(self, index):
        return self._dataset[index][0], self._targets[index]


class Task(irisml.core.TaskBase):
    """Make a classification dataset from predictions.

    This task takes a dataset and a tensor of predictions and returns a new dataset
    with the targets set to the predicted class.

    The predictions tensor can be either a 1D tensor of class indices or a 2D tensor
    of class probabilities. In the latter case, the class with the highest probability
    is used as the target.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        predictions: torch.Tensor  # Shape: (N, C) or (N,)

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset

    def execute(self, inputs):
        if len(inputs.predictions.shape) == 1:
            targets = inputs.predictions
        elif len(inputs.predictions.shape) == 2:
            targets = torch.argmax(inputs.predictions, dim=1)
        else:
            raise ValueError(f"Invalid shape for predictions: {inputs.predictions.shape}")

        if len(inputs.dataset) != len(targets):
            raise ValueError(f"Dataset and predictions have different lengths: {len(inputs.dataset)} vs {len(targets)}")

        return self.Outputs(dataset=DatasetWithTargets(inputs.dataset, targets))

    def dry_run(self, inputs):
        return self.execute(inputs)
