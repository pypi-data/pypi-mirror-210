from abc import ABC

from masogram.handlers import BaseHandler
from masogram.types import InlineQuery, User


class InlineQueryHandler(BaseHandler[InlineQuery], ABC):
    """
    Base class for inline query handlers
    """

    @property
    def from_user(self) -> User:
        return self.event.from_user

    @property
    def query(self) -> str:
        return self.event.query
