import unittest
import pickle
import torch
from irisml.tasks.pickling_object import Task


class TestPicklingObject(unittest.TestCase):
    def test_tensor(self):
        tensor = torch.rand(3, 4, 5)
        outputs = Task(Task.Config()).execute(Task.Inputs(tensor))
        self.assertTrue(torch.equal(pickle.loads(outputs.data), tensor))

    def test_str(self):
        string = "Hello World"
        outputs = Task(Task.Config()).execute(Task.Inputs(string))
        self.assertEqual(pickle.loads(outputs.data), string)

    def test_list_of_tensors(self):
        list_of_tensors = [torch.Tensor([[0, 1, 0, 0, 1, 1]]), torch.Tensor([[1, 1, 0, 0, 1, 1]])]
        outputs = Task(Task.Config()).execute(Task.Inputs(list_of_tensors))
        self.assertTrue(all([torch.equal(a, b) for a, b in zip(pickle.loads(outputs.data), list_of_tensors)]))
