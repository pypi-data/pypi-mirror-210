import json
import pathlib
import tempfile
import unittest
from irisml.tasks.load_strs_from_json_file import Task


class TestLoadStrsFromJsonFile(unittest.TestCase):
    def test_simple(self):
        with tempfile.NamedTemporaryFile() as f:
            filepath = pathlib.Path(f.name)

            # List[str]
            filepath.write_text(json.dumps(["a", "b", "c"]))
            outputs = Task(Task.Config(filepath)).execute(Task.Inputs())
            self.assertEqual(outputs.strs, ["a", "b", "c"])

            # Dict[int, str]
            filepath.write_text(json.dumps({0: "a", 2: "c", 1: "b"}))
            outputs = Task(Task.Config(filepath)).execute(Task.Inputs())
            self.assertEqual(outputs.strs, ["a", "b", "c"])

            # Missing key
            filepath.write_text(json.dumps({0: "a", 2: "c"}))
            outputs = Task(Task.Config(filepath)).execute(Task.Inputs())
            self.assertEqual(outputs.strs, ["a", "", "c"])
