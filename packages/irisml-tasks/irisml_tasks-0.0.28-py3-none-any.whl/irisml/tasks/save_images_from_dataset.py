import dataclasses
import logging
import pathlib
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Save images from a dataset to disk.

    Config:
        dirpath (pathlib.Path): Directory to save images to.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Config:
        dirpath: pathlib.Path = pathlib.Path('.')
        extension: str = 'png'

    def execute(self, inputs):
        self.config.dirpath.mkdir(parents=True, exist_ok=True)
        for i, (image, targets) in enumerate(inputs.dataset):
            filepath = self.config.dirpath / f'{i}.{self.config.extension}'
            image.save(filepath)
            logger.info(f'Index {i}: Saved image to {filepath}, targets: {targets}')
        logger.info(f"Saved {len(inputs.dataset)} images to {self.config.dirpath}.")

        return self.Outputs()
