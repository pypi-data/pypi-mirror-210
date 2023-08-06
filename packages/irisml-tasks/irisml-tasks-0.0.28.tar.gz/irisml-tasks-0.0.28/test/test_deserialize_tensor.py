import io
import unittest
import torch
from irisml.tasks.deserialize_tensor import Task


class TestDeserializeTensor(unittest.TestCase):
    def test_simple(self):
        tensor = torch.rand(3, 4, 5)
        bytes_io = io.BytesIO()
        torch.save(tensor, bytes_io)
        serialized = bytes_io.getvalue()

        outputs = Task(Task.Config()).execute(Task.Inputs(serialized))
        self.assertTrue(torch.equal(outputs.tensor, tensor))
