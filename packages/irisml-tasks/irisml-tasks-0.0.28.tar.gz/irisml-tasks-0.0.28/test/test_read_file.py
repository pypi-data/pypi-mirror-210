import pathlib
import tempfile
import unittest
from irisml.tasks.read_file import Task


class TestReadFile(unittest.TestCase):
    def test_simple(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'Hello World!')
            f.flush()
            outputs = Task(Task.Config(path=pathlib.Path(f.name))).execute(Task.Inputs())
            self.assertEqual(outputs.data, b'Hello World!')
