from dataclasses import dataclass, field
from collections.abc import Callable
from timeit import default_timer
from typing import Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class Timer:
    """Wraps around a timer to time a block of code"""

    prefix: str = ""
    timer: Callable[[], float] = field(default_factory=lambda: default_timer)
    factor: int = 1
    output: bool | Callable[[str], None] = False
    fmt: str = "took {:.3f} seconds"
    start: float | None = None
    end: float | None = None

    def __call__(self) -> float:
        return self.timer()

    def __enter__(self) -> "Timer":
        self.start = self()
        return self

    def __exit__(self, *args: Any) -> None:
        self.end = self()

        if self.output:
            if callable(self.output):
                output = f"{self.prefix} {self.fmt.format(self.elapsed)}"
                self.output(output)
                return
            logger.debug("%s %s", self.prefix, self.fmt.format(self.elapsed))

    def __str__(self) -> str:
        return f"{self.elapsed:.3f}"

    @property
    def elapsed(self) -> float:
        """
        Returns the elapsed time in seconds, if called within scope uses the current elapsed time.
        If called out of scope uses the time when the context manager exited.
        """
        assert self.start is not None, "Timer has not been started"

        if self.end is None:
            return (self() - self.start) * self.factor

        return (self.end - self.start) * self.factor
