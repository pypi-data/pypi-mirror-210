import unittest
from irisml.tasks.make_prompt_with_strings import Task


class TestMakePromptWithStrings(unittest.TestCase):
    def test_simple(self):
        output = Task(Task.Config(template='What is <|placeholder|>?')).execute(Task.Inputs(strings=['a', 'b', 'c']))
        self.assertEqual(output.prompt, 'What is a, b, c?')

    def test_sub_template(self):
        output = Task(Task.Config(template='Here is a list. <|placeholder|>', sub_template='<|index|>: <|placeholder|>')).execute(Task.Inputs(strings=['a', 'b', 'c']))
        self.assertEqual(output.prompt, 'Here is a list. 0: a, 1: b, 2: c')
