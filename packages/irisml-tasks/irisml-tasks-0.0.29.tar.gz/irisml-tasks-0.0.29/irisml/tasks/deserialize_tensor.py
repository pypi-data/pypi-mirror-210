import dataclasses
import io
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Deserialize a pytorch tensor."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        data: bytes

    @dataclasses.dataclass
    class Outputs:
        tensor: torch.Tensor

    def execute(self, inputs):
        tensor = torch.load(io.BytesIO(inputs.data))
        if not isinstance(tensor, torch.Tensor):
            raise ValueError(f"The deserialized object has unexpected type: {type(tensor)}")
        return self.Outputs(tensor)

    def dry_run(self, inputs):
        return self.execute(inputs)
