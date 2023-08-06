from abc import ABC
from typing import List

from masogram.handlers import BaseHandler
from masogram.types import Poll, PollOption


class PollHandler(BaseHandler[Poll], ABC):
    """
    Base class for poll handlers
    """

    @property
    def question(self) -> str:
        return self.event.question

    @property
    def options(self) -> List[PollOption]:
        return self.event.options
