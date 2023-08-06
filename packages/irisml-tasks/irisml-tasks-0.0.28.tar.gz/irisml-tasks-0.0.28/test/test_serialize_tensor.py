import io
import unittest
import torch
from irisml.tasks.serialize_tensor import Task


class TestSerializeTensor(unittest.TestCase):
    def test_simple(self):
        tensor = torch.rand(3, 4, 5)
        outputs = Task(Task.Config()).execute(Task.Inputs(tensor))
        self.assertTrue(torch.equal(torch.load(io.BytesIO(outputs.data)), tensor))
