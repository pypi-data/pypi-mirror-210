import json
import unittest
from irisml.tasks.get_int_from_json_strings import Task


class TestGetIntFromJsonStrings(unittest.TestCase):
    def test_simple(self):
        json_strings = [json.dumps({'a': 3, 'b': 1}), json.dumps({'a': 2, 'b': 2, 'c': 3})]
        outputs = Task(Task.Config(key_name='a')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.ints, [3, 2])
        outputs = Task(Task.Config(key_name='b')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.ints, [1, 2])
        outputs = Task(Task.Config(key_name='c')).execute(Task.Inputs(json_strings))
        self.assertEqual(outputs.ints, [-1, 3])
