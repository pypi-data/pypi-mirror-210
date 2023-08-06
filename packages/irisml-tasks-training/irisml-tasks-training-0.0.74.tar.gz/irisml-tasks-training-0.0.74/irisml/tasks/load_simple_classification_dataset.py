import dataclasses
import logging
import pathlib
import typing
import PIL.Image
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Load a simple classification dataset from a directory of images and an index file.

    Config:
        filepath (Path): Path to the index file. The index file should be a text file with one line per image.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        filepath: pathlib.Path

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset
        num_classes: int
        class_names: typing.List[str]

    def execute(self, inputs):
        dataset = SimpleClassificationDataset(self.config.filepath)
        return self.Outputs(dataset=dataset, num_classes=len(dataset.class_names), class_names=dataset.class_names)

    def dry_run(self, inputs):
        return self.execute(inputs)


class SimpleClassificationDataset(torch.utils.data.Dataset):
    def __init__(self, index_filepath):
        super().__init__()
        self._index_filepath = index_filepath
        self._base_dir = index_filepath.parent

        index_lines = index_filepath.read_text().splitlines()
        self._image_indexes = [(path, int(label)) for line in index_lines for path, label in [line.split()]]

        max_class_id = max(label for _, label in self._image_indexes)

        labels_filepath = self._base_dir / 'labels.txt'
        if labels_filepath.exists():
            self._class_names = labels_filepath.read_text().splitlines()
            if max_class_id >= len(self._class_names):
                raise ValueError(f"Number of classes in {labels_filepath} is less than max class id in {index_filepath}")
        else:
            self._class_names = [str(i) for i in range(max_class_id + 1)]

        logger.info(f"Loaded Dataset {index_filepath} with {len(self)} images and {len(self._class_names)} classes")

    def __len__(self):
        return len(self._image_indexes)

    def __getitem__(self, index):
        image_path, label = self._image_indexes[index]
        image = PIL.Image.open(self._base_dir / image_path)
        return image, torch.tensor(label)

    @property
    def class_names(self):
        return self._class_names

    def get_targets(self, index):
        return self._image_indexes[index][1]
