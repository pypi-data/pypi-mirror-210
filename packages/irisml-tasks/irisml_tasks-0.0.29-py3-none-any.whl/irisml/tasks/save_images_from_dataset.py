import dataclasses
import logging
import pathlib
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Save images from a dataset to disk.

    Config:
        dirpath (pathlib.Path): Directory to save images to.
        extension (str): File extension to use for images.
        indices (torch.Tensor): Indices of images to save. If None, all images are saved.
    """
    VERSION = '0.2.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Config:
        dirpath: pathlib.Path = pathlib.Path('.')
        extension: str = 'png'
        indices: typing.Optional[torch.Tensor] = None

    def execute(self, inputs):
        self.config.dirpath.mkdir(parents=True, exist_ok=True)
        if self.config.indices is None:
            for i, (image, targets) in enumerate(inputs.dataset):
                self._save_image(image, targets, i)
            logger.info(f"Saved {len(inputs.dataset)} images to {self.config.dirpath}.")
        else:
            if self.config.indices.dim() != 1:
                raise ValueError(f'Indices must be a 1D tensor, got {self.config.indices.dim()}D.')

            for index in self.config.indices.tolist():
                image, targets = inputs.dataset[index]
                self._save_image(image, targets, index)
            logger.info(f"Saved {len(self.config.indices)} images to {self.config.dirpath}.")

        return self.Outputs()

    def _save_image(self, image, targets, index):
        filepath = self.config.dirpath / f'{index}.{self.config.extension}'
        image.save(filepath)
        logger.info(f'Index {index}: Saved image to {filepath}, targets: {targets}')
