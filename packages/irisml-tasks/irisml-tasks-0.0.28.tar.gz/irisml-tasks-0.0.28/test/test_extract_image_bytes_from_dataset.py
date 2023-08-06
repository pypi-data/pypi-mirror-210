import unittest
import PIL.Image
import torch
from irisml.tasks.extract_image_bytes_from_dataset import Task


class TestExtractImageBytesFromDataset(unittest.TestCase):
    def test_simple(self):
        fake_image = PIL.Image.new('RGB', (300, 300))
        dataset = [(fake_image, torch.tensor(0))] * 5 + [(fake_image, torch.tensor(1))] * 5

        outputs = Task(Task.Config(num_images_per_class=1)).execute(Task.Inputs(dataset=dataset, num_classes=2))
        self.assertEqual(len(outputs.image_bytes), 2)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)

        outputs = Task(Task.Config(num_images_per_class=10)).execute(Task.Inputs(dataset=dataset, num_classes=2))
        self.assertEqual(len(outputs.image_bytes), 20)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)

        outputs = Task(Task.Config(num_images_per_class=10)).execute(Task.Inputs(dataset=dataset, num_classes=3))
        self.assertEqual(len(outputs.image_bytes), 30)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)

    def test_dry_run(self):
        outputs = Task(Task.Config(num_images_per_class=1)).dry_run(Task.Inputs(dataset=[], num_classes=2))
        self.assertEqual(len(outputs.image_bytes), 2)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)

        outputs = Task(Task.Config(num_images_per_class=10)).dry_run(Task.Inputs(dataset=[], num_classes=2))
        self.assertEqual(len(outputs.image_bytes), 20)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)

        outputs = Task(Task.Config(num_images_per_class=10)).dry_run(Task.Inputs(dataset=[], num_classes=3))
        self.assertEqual(len(outputs.image_bytes), 30)
        self.assertTrue(isinstance(b, bytes) for b in outputs.image_bytes)
