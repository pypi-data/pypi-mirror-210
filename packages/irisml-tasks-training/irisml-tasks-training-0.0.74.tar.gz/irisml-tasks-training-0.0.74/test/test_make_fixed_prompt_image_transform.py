import unittest
import PIL.Image
import torch
import torchvision
from irisml.tasks.make_fixed_prompt_image_transform import Task


class TestMakeFixedPromptImageTransform(unittest.TestCase):
    def test_simple(self):
        image_transform = torchvision.transforms.ToTensor()
        prompt = 'What is in the image?'

        outputs = Task(Task.Config(prompt=prompt)).execute(Task.Inputs(image_transform=image_transform))

        transformed = outputs.transform(PIL.Image.new('RGB', (32, 32)), torch.tensor(3))
        self.assertEqual(len(transformed), 2)
        self.assertEqual(len(transformed[0]), 2)
        self.assertEqual(transformed[0][0], prompt)
        self.assertEqual(len(transformed[0][1]), 1)
        self.assertIsInstance(transformed[0][1][0], torch.Tensor)
        self.assertEqual(transformed[0][1][0].shape, (3, 32, 32))
        self.assertEqual(transformed[1], torch.tensor(3))
