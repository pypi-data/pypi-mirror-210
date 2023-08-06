from abc import ABC

from masogram.handlers import BaseHandler
from masogram.types import ChatMemberUpdated, User


class ChatMemberHandler(BaseHandler[ChatMemberUpdated], ABC):
    """
    Base class for chat member updated events
    """

    @property
    def from_user(self) -> User:
        return self.event.from_user
