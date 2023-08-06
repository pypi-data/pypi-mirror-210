import unittest
import unittest.mock
from irisml.tasks.switch_pick import Task


class TestSwitchPick(unittest.TestCase):
    def test_switch_pick(self):
        test_cases = [([True, True, False], [1, 2, 3], 1), ([False, True], [1, 2], 2), ([False, False], [1, 2], None),
                      ([], [], None), ([True], [[1, 2]], [1, 2]), ([False, True], [[1, 2], [3, 4]], [3, 4])]
        for conditions, vals, expect in test_cases:
            task = Task(Task.Config())
            result = task.execute(Task.Inputs(conditions, vals)).result
            self.assertEqual(result, expect)

    def test_switch_pick_len_not_equal(self):
        task = Task(Task.Config())
        self.assertRaises(Exception, lambda: task.execute(Task.Inputs([True], [1, 2])))

    def test_default_val_works(self):
        task = Task(Task.Config())
        self.assertEqual(task.execute(Task.Inputs([False, False], [1, 2], 3)).result, 3)
