import dataclasses
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class RemappedDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, mappings):
        self._dataset = dataset
        self._mappings = mappings
        if hasattr(dataset, 'get_targets'):
            self.get_targets = self.__get_targets

    def __len__(self):
        return len(self._mappings)

    def __getitem__(self, index):
        return self._dataset[self._mappings[index]]

    def __get_targets(self, index):
        return self._dataset.get_targets(self._mappings[index])


class Task(irisml.core.TaskBase):
    """Exclude negative samples from classification dataset."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset

    def execute(self, inputs):
        mappings = self._get_mappings(inputs.dataset)
        logger.info(f"New total number of samples: {len(mappings)}. Excluded {len(inputs.dataset) - len(mappings)} samples.")
        return self.Outputs(dataset=RemappedDataset(inputs.dataset, mappings))

    def dry_run(self, inputs):
        return self.execute(inputs)

    @staticmethod
    def _get_mappings(dataset):
        mappings = []
        for i in range(len(dataset)):
            if hasattr(dataset, 'get_targets'):
                targets = dataset.get_targets(i)
            else:
                targets = dataset[i][1]
            if int(targets) < 0:
                continue
            mappings.append(i)
        return mappings
