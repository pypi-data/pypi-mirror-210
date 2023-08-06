import dataclasses
import logging
import typing
import irisml.core


PLACEHOLDER = '<|placeholder|>'
INDEX_PLACEHOLDER = '<|index|>'
logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Make a prompt with a list of strings.

    For example, if the template is "What is <placeholder>?" and the strings are ["a", "b", "c"], the prompt will be "What is a, b, c?".

    Optionally, you can specify a sub_template to use for each string. For example, if the template is "What is <|placeholder|>?" and
    the sub_template is "<|index|>.<|placeholder|>", the prompt will be "What is 0.a, 1.b, 2.c?".

    Config:
        template (str): The template to use for the prompt. Must contain "<|placeholder|>".
        sub_template (str): The template to use for each string. Must contain "<|placeholder|>". Can also contain "<|index|>".
        delimiter (str): The delimiter to use between the strings. Defaults to ", ".
    """
    VERSION = '0.2.0'

    @dataclasses.dataclass
    class Inputs:
        strings: typing.List[str]

    @dataclasses.dataclass
    class Config:
        template: str
        sub_template: str = PLACEHOLDER
        delimiter: str = ', '

    @dataclasses.dataclass
    class Outputs:
        prompt: str

    def execute(self, inputs):
        if PLACEHOLDER not in self.config.template:
            raise ValueError(f'"{PLACEHOLDER}" must be in template')
        if PLACEHOLDER not in self.config.sub_template:
            raise ValueError(f'"{PLACEHOLDER}" must be in sub_template')

        strings = [self.config.sub_template.replace(PLACEHOLDER, s).replace(INDEX_PLACEHOLDER, str(i)) for i, s in enumerate(inputs.strings)]
        prompt = self.config.template.replace(PLACEHOLDER, self.config.delimiter.join(strings))
        logger.info(f"Created a prompt: {prompt}")
        return self.Outputs(prompt=prompt)

    def dry_run(self, inputs):
        return self.execute(inputs)
