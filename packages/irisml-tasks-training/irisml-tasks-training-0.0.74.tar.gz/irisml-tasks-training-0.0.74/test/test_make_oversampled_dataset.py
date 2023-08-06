import unittest
import torch
from irisml.tasks.make_oversampled_dataset import Task

from utils import FakeDatasetWithGetTargets


class TestMakeOversampledDataset(unittest.TestCase):
    def test_calculate_weights(self):
        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        results = Task._calculcate_weights(FakeDatasetWithGetTargets(dataset), 100, 0)
        self.assertEqual(results[0], results[1])
        self.assertGreater(results[2], results[0])

    def test_min_num_samples(self):
        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        outputs = Task(Task.Config(10)).execute(Task.Inputs(FakeDatasetWithGetTargets(dataset)))
        self.assertEqual(len(outputs.dataset), 10)
        self.assertIsNotNone(outputs.dataset[0])
        self.assertIsNotNone(outputs.dataset[9])

        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        dataset = FakeDatasetWithGetTargets(dataset)
        outputs = Task(Task.Config(3)).execute(Task.Inputs(dataset))
        self.assertEqual(outputs.dataset, dataset)  # no oversampling

    def test_oversampling_rate(self):
        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        outputs = Task(Task.Config(0, 3)).execute(Task.Inputs(FakeDatasetWithGetTargets(dataset)))
        self.assertEqual(len(outputs.dataset), 9)

        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        dataset = FakeDatasetWithGetTargets(dataset)
        outputs = Task(Task.Config(0, 1)).execute(Task.Inputs(dataset))
        self.assertEqual(outputs.dataset, dataset)  # no oversampling

    def test_balancing(self):
        dataset = [(None, torch.tensor([1])), (None, torch.tensor([1])), (None, torch.tensor([0]))]
        outputs = Task(Task.Config(0, 3, balance=True)).execute(Task.Inputs(FakeDatasetWithGetTargets(dataset)))
        self.assertEqual(len(outputs.dataset), 9)
