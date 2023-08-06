import dataclasses
import logging
import random
import typing
import irisml.core
import torch
import PIL.Image
import PIL.ImageDraw

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Generate a fake object detection dataset.

    A generated dataset returns (image:PIL.Image, targets:List[Tensor[N, 5]])

    Configs:
        num_images (int): The number of images to make
        num_classes (int): The number of classes
        num_max_boxes (int): The max number of objects per image
        image_sizes ([(int, int), ...]): A list of candidate image sizes.
    """
    VERSION = '0.1.2'

    @dataclasses.dataclass
    class Config:
        num_images: int = 100
        num_classes: int = 10
        num_max_boxes: int = 10  # The max number of objects per image.
        image_sizes: typing.List[typing.Tuple[int, int]] = dataclasses.field(default_factory=lambda: [(320, 320)])

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset
        num_classes: int
        class_names: typing.List[str]

    class FakeDataset(torch.utils.data.Dataset):
        def __init__(self, targets: typing.List[torch.Tensor], colors: typing.List[typing.Tuple[int, int, int]], sizes: typing.List[typing.Tuple[int, int]]):
            assert len(targets) == len(sizes)
            self._targets = targets
            self._colors = colors
            self._sizes = sizes

        def __len__(self):
            return len(self._targets)

        def __getitem__(self, index):
            targets = self._targets[index]
            return self._generate_image(index, targets), targets

        def _generate_image(self, index, targets):
            size = self._sizes[index]
            image = PIL.Image.new('RGB', size)
            draw = PIL.ImageDraw.Draw(image)
            for t in targets:
                rect = [t[1] * size[0], t[2] * size[1], t[3] * size[0], t[4] * size[1]]
                draw.rectangle(rect, fill=self._colors[int(t[0])])
            return image

    def execute(self, inputs):
        def _random_box():
            cx = random.random()
            cy = random.random()
            w = random.uniform(0, min(1 - cx, cx))
            h = random.uniform(0, min(1 - cy, cy))
            return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        if not self.config.image_sizes:
            raise ValueError("Image sizes setting is empty.")

        for c in self.config.image_sizes:
            if len(c) != 2 or c[0] <= 0 or c[1] <= 0:
                raise ValueError(f"Invalid image size configs: {self.config.image_sizes}")

        targets = [torch.tensor([[random.randrange(self.config.num_classes), *_random_box()] for _ in range(random.randrange(self.config.num_max_boxes + 1))]).reshape(-1, 5)
                   for _ in range(self.config.num_images)]

        colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(self.config.num_classes)]
        logger.debug(f"Generated labels: {colors}")

        sizes = random.choices(self.config.image_sizes, k=self.config.num_images)
        dataset = Task.FakeDataset(targets, colors, sizes)
        class_names = [f'class_{i}' for i in range(self.config.num_classes)]
        return self.Outputs(dataset, num_classes=self.config.num_classes, class_names=class_names)

    def dry_run(self, inputs):
        return self.execute(inputs)
