import dataclasses
import difflib
import logging
import random
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Assigns a class to a string based on the class name being present in the string.

    This task uses multiple matchers to assign a class to a string. The matchers are
    executed in the following order:

    1. ExactClassMatcher: If the class name is present in the string, it assigns the class
    to the string.
    2. WordCountClassMatcher: Count the number of matching words between the class name
    and the string. If the number of matching words is greater than 0, it assigns the
    class to the string.
    3. DifflibClassMatcher: Uses Difflib to find the class name that is most similar to the string.

    Config:
        assign_negative_class_if_no_match: If True, assigns -1 to the string if it doesn't find a match by ExactClassMatcher.
    """
    VERSION = '0.1.3'

    @dataclasses.dataclass
    class Inputs:
        strings: typing.List[str]
        class_names: typing.List[str]

    @dataclasses.dataclass
    class Config:
        assign_negative_class_if_no_match: bool = False

    @dataclasses.dataclass
    class Outputs:
        classes: torch.Tensor  # Shape: (N, )

    def execute(self, inputs):
        matchers = [ExactClassMatcher(inputs.class_names), WordCountClassMatcher(inputs.class_names), DifflibClassMatcher(inputs.class_names)]

        results = [None] * len(inputs.strings)
        for i, matcher in enumerate(matchers):
            num_unknowns_before = results.count(None)
            results = [c if c is not None else matcher(s) for s, c in zip(inputs.strings, results)]
            num_unknowns_after = results.count(None)
            logger.info(f"Assigned {num_unknowns_before - num_unknowns_after}/{num_unknowns_before} strings based on {i}th matcher.")

            if num_unknowns_after == 0:
                break

            if i == 0:
                if self.config.assign_negative_class_if_no_match:
                    results = [c if c is not None else -1 for c in results]
                    logger.info(f"Assigned {num_unknowns_after}/{len(inputs.strings)} strings to class -1")

        return self.Outputs(torch.tensor(results))

    def dry_run(self, inputs):
        return self.execute(inputs)


class ClassMatcher:
    def __init__(self, class_names):
        self.class_names = [n.lower() for n in class_names]

    def __call__(self, s):
        return self.find(s.lower())

    def find(self, s):
        raise NotImplementedError


class ExactClassMatcher(ClassMatcher):
    def find(self, s):
        for i, c in enumerate(self.class_names):
            if c in s:
                return i
        return None


class WordCountClassMatcher(ClassMatcher):
    def __init__(self, class_names):
        super().__init__(class_names)
        self.class_name_words = [set(n.split()) for n in self.class_names]

    def find(self, s):
        word_set = set(s.split())
        matched_word_counts = [len(c.intersection(word_set)) / len(c) for c in self.class_name_words]
        max_matched_word_count = max(matched_word_counts)
        if max_matched_word_count == 0:
            return None
        max_indexes = [i for i, x in enumerate(matched_word_counts) if x == max_matched_word_count]
        class_index = random.choice(max_indexes) if len(max_indexes) > 1 else max_indexes[0]
        logger.debug(f"Assigned {repr(self.class_names[class_index])} to {repr(s)} by score {max_matched_word_count}")
        return class_index


class DifflibClassMatcher(ClassMatcher):
    def find(self, s):
        scores = [difflib.SequenceMatcher(None, s, c).ratio() for c in self.class_names]
        max_scores = max(scores)
        max_indexes = [i for i, x in enumerate(scores) if x == max_scores]
        class_index = random.choice(max_indexes) if len(max_indexes) > 1 else max_indexes[0]
        logger.debug(f"Assigned {repr(self.class_names[class_index])} to {repr(s)} by Difflib")
        return class_index
