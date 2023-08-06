import pathlib
import tempfile
import unittest
import PIL.Image
from irisml.tasks.load_simple_classification_dataset import Task


class TestLoadSimpleClassificationDataset(unittest.TestCase):
    def test_simple(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            index_filepath = temp_dir / 'images.txt'
            index_filepath.write_text('\n'.join(['image0.jpg 0', 'image1.jpg 1', 'image2.jpg 0']))
            labels_filepath = temp_dir / 'labels.txt'
            labels_filepath.write_text('\n'.join(['cat', 'dog']))
            PIL.Image.new('RGB', (10, 10)).save(temp_dir / 'image0.jpg')
            PIL.Image.new('RGB', (10, 10)).save(temp_dir / 'image1.jpg')
            PIL.Image.new('RGB', (10, 10)).save(temp_dir / 'image2.jpg')
            outputs = Task(Task.Config(index_filepath)).execute(Task.Inputs())

            self.assertEqual(outputs.num_classes, 2)
            self.assertEqual(outputs.class_names, ['cat', 'dog'])
            self.assertEqual(len(outputs.dataset), 3)
            self.assertEqual(outputs.dataset[0][1], 0)
            self.assertEqual(outputs.dataset[1][1], 1)
            self.assertEqual(outputs.dataset[2][1], 0)
            self.assertIsInstance(outputs.dataset[0][0], PIL.Image.Image)
            self.assertIsInstance(outputs.dataset[1][0], PIL.Image.Image)
            self.assertIsInstance(outputs.dataset[2][0], PIL.Image.Image)
