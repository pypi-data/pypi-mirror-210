import dataclasses
import logging
import typing
import irisml.core


PLACEHOLDER = '<|placeholder|>'
logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Make a prompt for each string.

    For example, if the template is "What is <|placeholder|>?" and the strings are ["a", "b", "c"], the prompts will be ["What is a?", "What is b?", "What is c?"].

    Config:
        template (str): The template to use for the prompt. Must contain "<|placeholder|>".
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Inputs:
        strings: typing.List[str]

    @dataclasses.dataclass
    class Config:
        template: str

    @dataclasses.dataclass
    class Outputs:
        prompts: typing.List[str]

    def execute(self, inputs):
        if PLACEHOLDER not in self.config.template:
            raise ValueError(f'"{PLACEHOLDER}" must be in template')

        prompts = [self.config.template.replace(PLACEHOLDER, s) for s in inputs.strings]
        for p in prompts:
            logger.info(f"Created a prompt: {p}")

        return self.Outputs(prompts=prompts)

    def dry_run(self, inputs):
        return self.execute(inputs)
