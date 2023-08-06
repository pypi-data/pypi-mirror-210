import dataclasses
import logging
import irisml.core
from typing import Union, List, Optional

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """ pick from vals based on conditions. Task will return the first val with condition being True.
    default will be returned, if all conditions are false.

    Inputs:
        conditions (bool): conditions
        vals (float, int, str): vals
        default (float, int, str): default value
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        conditions: List[bool]
        vals: List[Union[float, int, str, list]]
        default: Optional[Union[float, int, str, list]] = None

    @dataclasses.dataclass
    class Outputs:
        result: Union[float, int, str, list]

    def execute(self, inputs):
        assert len(inputs.conditions) == len(inputs.vals)

        for i, cond in enumerate(inputs.conditions):
            if cond:
                logger.info(f'{i}th condition is True and got picked.')
                return self.Outputs(inputs.vals[i])

        logger.info(f'None of conditions is True: default {inputs.default} returned.')
        return self.Outputs(inputs.default)

    def dry_run(self, inputs):
        return self.execute(inputs)
