import unittest
from irisml.tasks.make_prompt_for_each_string import Task


class TestMakePromptForEachString(unittest.TestCase):
    def test_simple(self):
        output = Task(Task.Config(template='What is <|placeholder|>?')).execute(Task.Inputs(strings=['a', 'b', 'c']))
        self.assertEqual(output.prompts, ['What is a?', 'What is b?', 'What is c?'])
