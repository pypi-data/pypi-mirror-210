import dataclasses
import logging
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """
    Remove empty images from dataset.
    Currently this task is only needed by FL OD Dyhead model training
    """
    VERSION = '0.0.1'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset

    def execute(self, inputs):
        original_dataset_size = len(inputs.dataset)

        dataset = EmptyRemovedDataset(inputs.dataset)

        logger.info(f"Removing images without any annotations."
                    f"The number of left samples is {len(dataset)}. The original number of samples is {original_dataset_size}.")

        return self.Outputs(dataset)

    def dry_run(self, inputs):
        return self.Outputs(inputs.dataset)


class EmptyRemovedDataset(torch.utils.data.Dataset):
    def __init__(self, dataset):
        self._dataset = dataset

        self._id_mappings = []
        for i in range(len(dataset)):
            if hasattr(dataset, 'get_targets'):
                targets = dataset.get_targets(i)
            else:
                targets = dataset[i][1]
            if not targets.shape or len(targets):
                self._id_mappings.append(i)

    def __len__(self):
        return len(self._id_mappings)

    def __getitem__(self, index):
        new_id = self._id_mappings[index]
        assert isinstance(new_id, int)
        return self._dataset[new_id]
