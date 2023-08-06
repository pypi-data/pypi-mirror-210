import dataclasses
import pickle
import logging
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Pickling an object."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        data: object

    @dataclasses.dataclass
    class Outputs:
        data: bytes

    def execute(self, inputs):
        data = pickle.dumps(inputs.data)
        logger.info("Pickling an object.")
        return self.Outputs(data)

    def dry_run(self, inputs):
        return self.execute(inputs)
