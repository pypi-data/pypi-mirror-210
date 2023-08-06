import unittest
from irisml.tasks.compare import Task


class TestCompare(unittest.TestCase):
    TEST_CASES = [(1, 0), (0, 0), (0, 1)]

    def test_greater(self):
        self._base_test([True, False, False], False, True)

    def test_greater_or_equal(self):
        self._base_test([True, True, False], True, True)

    def test_less(self):
        self._base_test([False, False, True], False, False)

    def test_less_or_equal(self):
        self._base_test([False, True, True], True, False)

    def _base_test(self, expected, equal_allowed, greater):
        for test_case, result in zip(self.TEST_CASES, expected):
            outputs = Task(Task.Config(equal_allowed=equal_allowed, greater=greater)).execute(Task.Inputs(test_case[0], test_case[1]))
            self.assertEqual(outputs.result, result)
