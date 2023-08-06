import json
import unittest
from irisml.tasks.get_int_from_json_strings import Task


class TestGetIntFromJsonStrings(unittest.TestCase):
    def test_simple(self):
        json_strings = [json.dumps({'a': 3, 'b': 1}), json.dumps({'a': 2, 'b': 2, 'c': 3})]
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [3, 2])
        outputs = Task(Task.Config(key_name='b')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [1, 2])
        outputs = Task(Task.Config(key_name='c')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [-1, 3])

    def test_noisy_json(self):
        json_strings = ['output: {"a": 3,\n "b": 1}.\n', 'output: {"a": 2, "b": 2, "c": {"d": 4}}.']
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [3, 2])
        outputs = Task(Task.Config(key_name='b')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [1, 2])
        outputs = Task(Task.Config(key_name='c')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [-1, -1])

    def test_multiple_json(self):
        json_strings = ['{"a": 3,\n"b": 1}{"a": 4, \n"b": 2}']
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [3])

    def test_json_with_single_quotes(self):
        json_strings = ["{'a': 3, 'b': 1}", "{'a': 2, 'b': 2, 'c': 3}"]
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [3, 2])

    def test_invalid_json(self):
        json_strings = ['{"a": 3,']
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.tensor.tolist(), [-1])
