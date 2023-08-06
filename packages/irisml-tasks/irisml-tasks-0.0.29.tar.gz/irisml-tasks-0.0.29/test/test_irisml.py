import pathlib
from irisml.test import generate_task_tests


TestTasks = generate_task_tests((pathlib.Path(__file__).parent.parent / 'irisml' / 'tasks').glob('*.py'))
