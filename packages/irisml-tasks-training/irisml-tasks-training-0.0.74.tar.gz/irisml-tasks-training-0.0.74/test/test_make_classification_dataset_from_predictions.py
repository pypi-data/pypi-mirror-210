import unittest
import PIL.Image
import torch
from irisml.tasks.make_classification_dataset_from_predictions import Task


class FakeDataset(torch.utils.data.Dataset):
    def __init__(self, num_images):
        super().__init__()
        self._num_images = num_images

    def __len__(self):
        return self._num_images

    def __getitem__(self, index):
        return PIL.Image.new('RGB', (100, 100)), torch.zeros(1)


class TestMakeClassificationDatasetFromPredictions(unittest.TestCase):
    def test_2d_predictions(self):
        dataset = FakeDataset(10)
        predictions = torch.zeros(10, 3)
        predictions[:, 1] = 1
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset=dataset, predictions=predictions))
        self.assertIsInstance(outputs.dataset, torch.utils.data.Dataset)
        self.assertIsInstance(outputs.dataset[0][1], torch.Tensor)
        self.assertEqual(len(outputs.dataset), 10)
        self.assertEqual([int(outputs.dataset[i][1]) for i in range(10)], [1] * 10)

    def test_1d_predictions(self):
        dataset = FakeDataset(10)
        predictions = torch.ones(10)
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset=dataset, predictions=predictions))
        self.assertIsInstance(outputs.dataset, torch.utils.data.Dataset)
        self.assertIsInstance(outputs.dataset[0][1], torch.Tensor)
        self.assertEqual(len(outputs.dataset), 10)
        self.assertEqual([int(outputs.dataset[i][1]) for i in range(10)], [1] * 10)
