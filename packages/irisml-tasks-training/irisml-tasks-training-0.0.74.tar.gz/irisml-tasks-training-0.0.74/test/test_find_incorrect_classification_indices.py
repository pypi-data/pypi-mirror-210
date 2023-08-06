import unittest
import torch
from irisml.tasks.find_incorrect_classification_indices import Task


class TestFindIncorrectClassificationIndices(unittest.TestCase):
    def test_1d(self):
        predictions = torch.tensor([0, 1, 2, 2, 2, 5])
        targets = torch.tensor([0, 1, 2, 3, 4, 5])
        outputs = Task(Task.Config()).execute(Task.Inputs(predictions, targets))
        self.assertEqual(outputs.indices.tolist(), [3, 4])

    def test_2d(self):
        predictions = torch.tensor([[0, 0, 0, 0, 0, 1],
                                    [0, 1, 0, 0, 0, 0],
                                    [0, 0, 0, 1, 0, 0],
                                    [0, 0, 0, 1, 0, 0],
                                    [0, 1, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 1]])
        targets = torch.tensor([0, 1, 2, 3, 4, 5])
        outputs = Task(Task.Config()).execute(Task.Inputs(predictions, targets))
        self.assertEqual(outputs.indices.tolist(), [0, 2, 4])
