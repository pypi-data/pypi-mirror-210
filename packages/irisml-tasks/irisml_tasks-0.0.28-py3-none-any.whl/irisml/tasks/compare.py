import dataclasses
import logging
import irisml.core
from typing import Union, Optional

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """ Compare two values

    Inputs:
        val1 (float, int, str): value 1
        val2 (float, int, str): value 2
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        val1: Union[float, int, str]
        val2: Union[float, int, str]

    @dataclasses.dataclass
    class Outputs:
        result: bool

    @dataclasses.dataclass
    class Config:
        equal_allowed: Optional[bool] = True
        greater: Optional[bool] = True

    def execute(self, inputs):
        if self.config.equal_allowed and inputs.val1 == inputs.val2:
            return self.Outputs(True)

        return self.Outputs(inputs.val1 > inputs.val2 if self.config.greater else inputs.val1 < inputs.val2)

    def dry_run(self, inputs):
        return self.execute(inputs)
