import unittest
import torch
from irisml.tasks.get_targets_from_dataset import Task

from utils import FakeDataset


class FakeDatasetWithGetTargets(FakeDataset):
    def __init__(self, data):
        self._data = data
        self._counter = 0

    @property
    def call_count(self):
        return self._counter

    def get_targets(self, index):
        self._counter += 1
        return self._data[index][1]

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        raise RuntimeError


class TestGetTargetsFromDataset(unittest.TestCase):
    def test_simple(self):
        data = [('image0', 0), ('image1', 2), ('image2', 4)]
        inputs = Task.Inputs(FakeDataset(data))
        outputs = Task(Task.Config()).execute(inputs)

        targets = outputs.targets

        self.assertIsInstance(targets, torch.Tensor)
        self.assertEqual(targets.tolist(), [0, 2, 4])

    def test_object_detection(self):
        data = [(None, torch.tensor([[i, 0, 0, 1, 1]])) for i in range(100)]
        outputs = Task(Task.Config()).execute(Task.Inputs(FakeDataset(data)))

        for i in range(100):
            self.assertTrue(torch.equal(outputs.targets[i], torch.tensor([[i, 0, 0, 1, 1]])))

    def test_get_targets(self):
        dataset = FakeDatasetWithGetTargets([(None, torch.tensor(i)) for i in range(100)])
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertTrue(torch.equal(outputs.targets, torch.tensor([i for i in range(100)])))
        self.assertEqual(dataset.call_count, 100)
