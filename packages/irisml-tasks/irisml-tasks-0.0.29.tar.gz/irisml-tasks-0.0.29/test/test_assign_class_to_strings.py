import unittest
import torch
from irisml.tasks.assign_class_to_strings import Task


class TestAssignClassToStrings(unittest.TestCase):
    def test_simple(self):
        strings = ["white cat", "black cat", "red dog", "blue dog"]
        class_names = ["cat", "dog"]
        outputs = Task(Task.Config()).execute(Task.Inputs(strings, class_names))
        self.assertIsInstance(outputs.classes, torch.Tensor)
        self.assertEqual(outputs.classes.shape, (4,))
        self.assertEqual(outputs.classes.tolist(), [0, 0, 1, 1])

    def test_assign_similar_class(self):
        strings = ["white cat", "black cat", "red d0g", "blue d0g", "unknown"]
        class_names = ["cat", "dog"]
        outputs = Task(Task.Config()).execute(Task.Inputs(strings, class_names))
        self.assertIsInstance(outputs.classes, torch.Tensor)
        self.assertEqual(outputs.classes.shape, (5,))
        self.assertEqual(outputs.classes.tolist()[:4], [0, 0, 1, 1])
        self.assertIn(outputs.classes[4], (0, 1))

    def test_unknown_class_negative(self):
        strings = ["white cat", "black cat", "red dog", "blue dog", "unknown"]
        class_names = ["cat", "dog"]
        outputs = Task(Task.Config(assign_negative_class_if_no_match=True)).execute(Task.Inputs(strings, class_names))
        self.assertIsInstance(outputs.classes, torch.Tensor)
        self.assertEqual(outputs.classes.shape, (5,))
        self.assertEqual(outputs.classes.tolist(), [0, 0, 1, 1, -1])
