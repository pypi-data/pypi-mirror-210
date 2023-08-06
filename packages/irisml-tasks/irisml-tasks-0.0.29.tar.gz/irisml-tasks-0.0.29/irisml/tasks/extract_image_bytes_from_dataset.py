import collections
import dataclasses
import io
import logging
import random
import typing
import PIL.Image
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Extract images from a dataset and convert them to bytes.

    For example, if you have a dataset with 10 classes and you want to extract 5 images per class, you will get 50 images.

    Config:
        num_images_per_class (int): Number of images to extract per class.
        image_size (int): Size of the extracted images.
        random_seed (int): Random seed to use when extracting images.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        num_classes: int

    @dataclasses.dataclass
    class Config:
        num_images_per_class: int = 1
        image_size: int = 224
        random_seed: int = 0

    @dataclasses.dataclass
    class Outputs:
        image_bytes: typing.List[bytes]

    def execute(self, inputs):
        extracted_images = collections.defaultdict(list)
        random_list = random.Random(self.config.random_seed).sample(list(range(len(inputs.dataset))), k=len(inputs.dataset))
        for i in random_list:
            image, targets = inputs.dataset[i]
            class_id = self._get_class(targets)
            if len(extracted_images[class_id]) < self.config.num_images_per_class:
                extracted_images[class_id].append(image.resize((self.config.image_size, self.config.image_size)))

        # Add empty images if we could not extract enough images for a class
        for i in range(inputs.num_classes):
            if len(extracted_images[i]) < self.config.num_images_per_class:
                logger.warning(f"Could not extract {self.config.num_images_per_class} images for class {i}. Actual: {len(extracted_images[i])}. Adding empty images.")
                extracted_images[i].extend([PIL.Image.new('RGB', (self.config.image_size, self.config.image_size))] * (self.config.num_images_per_class - len(extracted_images[i])))

        # Convert images to bytes
        image_bytes = []
        for i in range(inputs.num_classes):
            for image in extracted_images[i]:
                bytes_io = io.BytesIO()
                image.save(bytes_io, format='JPEG')
                image_bytes.append(bytes_io.getvalue())

        return self.Outputs(image_bytes=image_bytes)

    def dry_run(self, inputs):
        bytes_io = io.BytesIO()
        PIL.Image.new('RGB', (self.config.image_size, self.config.image_size)).save(bytes_io, format='JPEG')
        fake_image_bytes = bytes_io.getvalue()
        return self.Outputs(image_bytes=[fake_image_bytes] * inputs.num_classes * self.config.num_images_per_class)

    @staticmethod
    def _get_class(targets):
        if not isinstance(targets, torch.Tensor):
            raise ValueError(f"Expected targets to be a torch.Tensor, got {type(targets)}")
        return int(targets)
