import dataclasses
import json
import logging
import typing
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Get an integer from a JSON string.

    This task takes a list of JSON strings and returns a list of integers. The
    JSON strings are expected to be dictionaries with a key that matches the
    `key_name` config value. If the JSON string cannot be decoded or the key
    cannot be found, the value -1 is returned.

    Config:
        key_name: The key to look for in the JSON string.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        json_strings: typing.List[str]

    @dataclasses.dataclass
    class Config:
        key_name: str

    @dataclasses.dataclass
    class Outputs:
        ints: typing.List[int]

    def execute(self, inputs):
        ints = []
        for i, json_string in enumerate(inputs.json_strings):
            value = -1
            try:
                json_dict = json.loads(json_string)
                value = json_dict[self.config.key_name]
                logger.info(f"Index {i}: Found value {value} in JSON string: {json_string}")
            except json.JSONDecodeError:
                logger.warning(f"Index {i}: Failed to decode JSON string: {json_string}")
            except KeyError:
                logger.warning(f"Index {i}: Failed to find key {self.config.key_name} in JSON string: {json_string}")
            ints.append(value)

        return self.Outputs(ints=ints)

    def dry_run(self, inputs):
        return self.execute(inputs)
