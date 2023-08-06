import unittest
import torch
from irisml.tasks.remove_empty_images_from_dataset import Task

from utils import FakeDatasetWithGetTargets


class TestRemoveEmptyImagesFromDataset(unittest.TestCase):
    def test_object_detection(self):
        data = [(None, torch.tensor([[i, 0, 0, 1, 1]])) for i in range(10)]
        outputs = Task(Task.Config()).execute(Task.Inputs(FakeDatasetWithGetTargets(data)))
        self.assertEqual(len(outputs.dataset), 10)

        data = [(None, torch.tensor([[i, 0, 0, 1, 1]])) for i in range(10)] + [(None, torch.tensor([])) for _ in range(10)]
        outputs = Task(Task.Config()).execute(Task.Inputs(FakeDatasetWithGetTargets(data)))
        self.assertEqual(len(outputs.dataset), 10)

    def test_classification(self):
        data = [(None, torch.tensor([i])) for i in range(10)]
        outputs = Task(Task.Config()).execute(Task.Inputs(FakeDatasetWithGetTargets(data)))
        self.assertEqual(len(outputs.dataset), 10)

        data = [(None, torch.tensor([i])) for i in range(10)] + [(None, torch.tensor([])) for _ in range(10)]
        outputs = Task(Task.Config()).execute(Task.Inputs(FakeDatasetWithGetTargets(data)))
        self.assertEqual(len(outputs.dataset), 10)
