import dataclasses
import json
import logging
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Get an integer from a JSON string.

    This task takes a list of JSON strings and returns a list of integers. The
    JSON strings are expected to be dictionaries with a key that matches the
    `key_name` config value. If the JSON string cannot be decoded or the key
    cannot be found, the value -1 is returned.

    This task ignores any non-JSON text before or after the JSON string.

    If single quotes are used in the JSON string, they are replaced with double
    quotes before decoding.

    Config:
        key_name: The key to look for in the JSON string.
    """
    VERSION = '1.0.0'

    @dataclasses.dataclass
    class Inputs:
        json_strings: typing.List[str]

    @dataclasses.dataclass
    class Config:
        key_name: str

    @dataclasses.dataclass
    class Outputs:
        tensor: torch.Tensor

    def execute(self, inputs):
        ints = []
        for i, json_string in enumerate(inputs.json_strings):
            value = -1
            try:
                json_dict = self._decode_json(json_string)
                if not isinstance(json_dict[self.config.key_name], int):
                    raise TypeError(f"Value {json_dict[self.config.key_name]} is not an integer")
                value = json_dict[self.config.key_name]
                logger.info(f"Index {i}: Found value {value} in JSON string: {repr(json_string)}")
            except json.JSONDecodeError:
                logger.warning(f"Index {i}: Failed to decode JSON string: {repr(json_string)}")
            except KeyError:
                logger.warning(f"Index {i}: Failed to find key {self.config.key_name} in JSON string: {repr(json_string)}")
            except TypeError as e:
                logger.warning(f"Index {i}: {e}")

            ints.append(value)

        int_tensor = torch.tensor(ints)
        logger.info(f"Returning {int_tensor.shape} tensor of ints")
        return self.Outputs(int_tensor)

    def dry_run(self, inputs):
        return self.execute(inputs)

    @staticmethod
    def _decode_json(json_str):
        start = json_str.find('{')
        if start == -1:
            return ''

        try:
            decoded, _ = json.JSONDecoder().raw_decode(json_str[start:])
            return decoded
        except json.JSONDecodeError:
            pass

        try:
            # Try replacing a single quote with a double quote and vice versa.
            trans = str.maketrans('\'"', '"\'')
            decoded, _ = json.JSONDecoder().raw_decode(json_str.translate(trans)[start:])
            return decoded
        except json.JSONDecodeError:
            pass

        try:
            # Try replacing a single quote with a double quote
            decoded, _ = json.JSONDecoder().raw_decode(json_str.replace('\'', '"')[start:])
            return decoded
        except json.JSONDecodeError:
            raise
