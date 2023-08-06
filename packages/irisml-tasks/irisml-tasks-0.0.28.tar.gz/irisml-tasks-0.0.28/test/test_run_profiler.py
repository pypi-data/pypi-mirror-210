import sys
import unittest
import unittest.mock
from irisml.core import TaskBase, TaskDescription
from irisml.tasks.run_profiler import Task


class FakeTask:
    class Task(TaskBase):
        VERSION = '0.1.0'

        def execute(self, inputs):
            return self.Outputs()


class TestRunProfiler(unittest.TestCase):
    def test_run(self):
        tasks = [TaskDescription.from_dict(t) for t in [{'task': 'fake_task'}, {'task': 'fake_task'}]]
        with unittest.mock.patch.dict('sys.modules'):
            sys.modules['irisml.tasks.fake_task'] = FakeTask
            outputs = Task(Task.Config(tasks=tasks)).execute(None)
        self.assertGreater(len(outputs.stats_bytes), 0)
