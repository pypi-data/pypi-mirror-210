import unittest
import torch
from irisml.tasks.benchmark_dataset import Task


class TestBenchmarkDataset(unittest.TestCase):
    def test_simple(self):
        dataset = torch.utils.data.TensorDataset(torch.randn(100, 3, 32, 32), torch.randint(0, 10, (100,)))

        def fake_transform(x):
            return x

        outputs = Task(Task.Config(batch_size=1)).execute(Task.Inputs(dataset=dataset, transform=fake_transform))
        self.assertGreater(outputs.time_per_batch, 0.0)
