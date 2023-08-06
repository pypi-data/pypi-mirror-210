import dataclasses
import logging
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Get the largest Topk values and indices.

    Inputs:
        tensor (torch.Tensor): The input tensor

    Config:
        k (int): The "k".
        device (str): The device to use. If not specified, it uses cuda if available.
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Inputs:
        tensor: torch.Tensor

    @dataclasses.dataclass
    class Config:
        k: int
        device: typing.Optional[typing.Literal['cpu', 'cuda']] = None

    @dataclasses.dataclass
    class Outputs:
        values: torch.Tensor
        indices: torch.LongTensor

    def execute(self, inputs):
        device = self._get_device()
        result = torch.topk(inputs.tensor.to(device), self.config.k)
        return self.Outputs(result.values.to('cpu'), result.indices.to('cpu'))

    def dry_run(self, inputs):
        shape = [*inputs.tensor.shape[:-1], self.config.k]
        fake_values = torch.zeros(shape)
        fake_indices = torch.arange(self.config.k).expand(shape)
        return self.Outputs(fake_values, fake_indices)

    def _get_device(self) -> torch.device:
        """Get a torch device based on the configuration. If not specified explicitly, it uses cuda if available."""
        if self.config.device:
            device_name = self.config.device
        else:
            device_name = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Device is selected automatically: {device_name}. To specify the device manually, please set Config.device.")

        return torch.device(device_name)
