import dataclasses
import logging
import random
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Get a subset of a dataset.

    Config:
        num_images (int): Number of images to keep in the dataset.
        verbose (bool): Shows a list of selected samples.
    """
    VERSION = '0.1.2'

    @dataclasses.dataclass
    class Config:
        num_images: int
        verbose: bool = False

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset

    def execute(self, inputs):
        num_images = len(inputs.dataset)
        new_num_images = self.config.num_images
        indexes = random.sample(range(num_images), new_num_images)
        if self.config.verbose:
            logger.info(f"Selected indexes: {indexes}")

        new_dataset = torch.utils.data.Subset(inputs.dataset, indexes)
        return self.Outputs(new_dataset)

    def dry_run(self, inputs):
        return self.execute(inputs)
