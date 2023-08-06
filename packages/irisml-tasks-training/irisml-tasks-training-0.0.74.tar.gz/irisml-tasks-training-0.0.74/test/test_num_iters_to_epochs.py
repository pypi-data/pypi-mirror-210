import unittest
from irisml.tasks.num_iters_to_epochs import Task
from utils import FakeDataset


class TestNumItersToEpochs(unittest.TestCase):
    def test_more_than_1_epoch(self):
        task = Task(Task.Config())
        epochs = task.execute(Task.Inputs(batch_size=16, num_iterations=10, dataset=FakeDataset([1, 2, 3, 4]))).num_epochs
        self.assertEqual(epochs, 40)

    def test_less_than_1_epoch(self):
        task = Task(Task.Config())
        epochs = task.execute(Task.Inputs(batch_size=2, num_iterations=1, dataset=FakeDataset([1, 2, 3, 4]))).num_epochs
        self.assertEqual(epochs, 1)
