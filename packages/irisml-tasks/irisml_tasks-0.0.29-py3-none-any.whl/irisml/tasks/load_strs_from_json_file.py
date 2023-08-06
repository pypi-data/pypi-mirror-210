import dataclasses
import json
import logging
import pathlib
import typing
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Load strings from a JSON file.

    The JSON file must be a list of strings, or a dictionary with integer keys
    and string values. The strings are loaded into a list, with the index
    corresponding to the key in the dictionary.

    Config:
        filepath (Path): Path to the JSON file.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Config:
        filepath: pathlib.Path

    @dataclasses.dataclass
    class Outputs:
        strs: typing.List[str]

    def execute(self, inputs):
        data = json.loads(self.config.filepath.read_text())
        if isinstance(data, list):
            return self.Outputs(strs=data)

        if not all(k.isdigit() for k in data.keys()):
            raise ValueError('keys must be integers')

        max_key = max(int(k) for k in data.keys())
        strs = [''] * (max_key + 1)
        for k, v in data.items():
            strs[int(k)] = v
        logger.info(f"Loaded {len(data.keys())} strings to {max_key + 1} slots")
        return self.Outputs(strs=strs)

    def dry_run(self, inputs):
        return self.execute(inputs)
