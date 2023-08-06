import dataclasses
import io
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Serialize a pytorch tensor."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        tensor: torch.Tensor

    @dataclasses.dataclass
    class Outputs:
        data: bytes

    def execute(self, inputs):
        bytes_io = io.BytesIO()
        torch.save(inputs.tensor, bytes_io)
        data = bytes_io.getvalue()
        logger.info(f"Serialized a tensor (shape: {inputs.tensor.shape}). {len(data)} bytes.")
        return self.Outputs(data)

    def dry_run(self, inputs):
        return self.execute(inputs)
