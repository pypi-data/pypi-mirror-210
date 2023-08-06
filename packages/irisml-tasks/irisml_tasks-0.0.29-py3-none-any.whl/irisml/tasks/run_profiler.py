import cProfile
import dataclasses
import logging
import pathlib
import tempfile
import typing
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Run profiler on the given tasks.

    cProfile is used to profile the task.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False
    RESOLVE_CONFIG_VARIABLES = False

    @dataclasses.dataclass
    class Config:
        tasks: typing.List[irisml.core.TaskDescription]

    @dataclasses.dataclass
    class Outputs:
        stats_bytes: bytes

    def execute(self, inputs):
        tasks = [irisml.core.Task(t) for t in self.config.tasks]

        logger.info(f"Starting profiling for {len(tasks)} tasks.")
        with cProfile.Profile() as p:
            for task in tasks:
                task.load_module()
                task.execute(self.context)

        logger.info("Profiling finished. Printing stats.")

        p.print_stats()
        with tempfile.NamedTemporaryFile() as f:
            p.dump_stats(f.name)
            stats_bytes = pathlib.Path(f.name).read_bytes()

        return self.Outputs(stats_bytes=stats_bytes)

    def dry_run(self, inputs):
        return self.execute(inputs)
