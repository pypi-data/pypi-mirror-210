import unittest
import torch
from irisml.tasks.exclude_negative_samples_from_classification_dataset import Task


class TestExcludeNegativeSamplesFromClassificationDataset(unittest.TestCase):
    def test_multiclass(self):
        dataset = [(None, torch.tensor(0)), (None, torch.tensor(-1)), (None, torch.tensor(2)), (None, torch.tensor(-1))]
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset=dataset))
        self.assertEqual(len(outputs.dataset), 2)
        self.assertEqual(outputs.dataset[0][1], torch.tensor(0))
        self.assertEqual(outputs.dataset[1][1], torch.tensor(2))
        with self.assertRaises(IndexError):
            outputs.dataset[3]
        self.assertFalse(hasattr(outputs.dataset, 'get_targets'))
