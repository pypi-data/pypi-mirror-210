import unittest
import pathlib
import tempfile
import PIL.Image
import torch
from irisml.tasks.save_images_from_dataset import Task


class TestSaveImagesFromDataset(unittest.TestCase):
    def test_no_indices(self):
        dataset = [(PIL.Image.new('RGB', (10, 10)), torch.tensor(0)), (PIL.Image.new('RGB', (10, 10)), torch.tensor(1))]
        with tempfile.TemporaryDirectory() as temp_dirpath:
            temp_dirpath = pathlib.Path(temp_dirpath) / 'images'  # Nonexistent directory
            Task(Task.Config(dirpath=temp_dirpath)).execute(Task.Inputs(dataset=dataset))

            self.assertTrue((temp_dirpath / '0.png').exists())
            self.assertTrue((temp_dirpath / '1.png').exists())
            self.assertFalse((temp_dirpath / '2.png').exists())

            image0 = PIL.Image.open(temp_dirpath / '0.png')
            self.assertEqual(image0.size, (10, 10))

    def test_save_with_indices(self):
        dataset = [(PIL.Image.new('RGB', (10, 10)), torch.tensor(0)), (PIL.Image.new('RGB', (10, 10)), torch.tensor(1))] * 2
        with tempfile.TemporaryDirectory() as temp_dirpath:
            temp_dirpath = pathlib.Path(temp_dirpath) / 'images'  # Nonexistent directory
            Task(Task.Config(dirpath=temp_dirpath, indices=torch.tensor([0, 3]))).execute(Task.Inputs(dataset=dataset))

            self.assertTrue((temp_dirpath / '0.png').exists())
            self.assertFalse((temp_dirpath / '1.png').exists())
            self.assertFalse((temp_dirpath / '2.png').exists())
            self.assertTrue((temp_dirpath / '3.png').exists())

            image0 = PIL.Image.open(temp_dirpath / '0.png')
            self.assertEqual(image0.size, (10, 10))
