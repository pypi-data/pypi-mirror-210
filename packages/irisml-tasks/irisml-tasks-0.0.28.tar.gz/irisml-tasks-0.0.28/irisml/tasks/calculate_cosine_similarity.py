import dataclasses
import logging
import typing
import torch
import irisml.core


logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Calculate cosine similarity between two sets of vectors.

    Inputs:
        tensor0 (torch.Tensor): Shape [N0, M]
        tensor1 (torch.Tensor): Shape [N1, M]

    Config:
        device (str): Device to use. If not specified, it uses cuda if available.

    Outputs:
        cosine_similarity (torch.Tensor): Shape [N0, N1]
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Inputs:
        tensor0: torch.Tensor
        tensor1: torch.Tensor

    @dataclasses.dataclass
    class Config:
        device: typing.Optional[typing.Literal['cpu', 'cuda']] = None

    @dataclasses.dataclass
    class Outputs:
        cosine_similarity: torch.Tensor

    def execute(self, inputs):
        if inputs.tensor0.shape[1] != inputs.tensor1.shape[1] or len(inputs.tensor0.shape) != 2 or len(inputs.tensor1.shape) != 2:
            raise RuntimeError(f"Input tensors have unexpected shape: tensor0.shape={inputs.tensor0.shape}, tensor1.shape={inputs.tensor1.shape}")

        device = self._get_device()
        tensor0 = inputs.tensor0.to(device)
        tensor1 = inputs.tensor1.to(device)

        eps = 1e-8
        norm0 = tensor0.norm(dim=1)[:, None]
        norm1 = tensor1.norm(dim=1)[:, None]
        normalized_tensor0 = tensor0 / torch.clamp(norm0, min=eps)
        normalized_tensor1 = tensor1 / torch.clamp(norm1, min=eps)
        cosine_similarity = torch.mm(normalized_tensor0, normalized_tensor1.transpose(0, 1)).to('cpu')
        assert cosine_similarity.shape == (inputs.tensor0.shape[0], inputs.tensor1.shape[0])
        return self.Outputs(cosine_similarity)

    def dry_run(self, inputs):
        fake_result = torch.zeros((inputs.tensor0.shape[0], inputs.tensor1.shape[0]))
        return self.Outputs(fake_result)

    def _get_device(self) -> torch.device:
        """Get a torch device based on the configuration. If not specified explicitly, it uses cuda if available."""
        if self.config.device:
            device_name = self.config.device
        else:
            device_name = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Device is selected automatically: {device_name}. To specify the device manually, please set Config.device.")

        return torch.device(device_name)
