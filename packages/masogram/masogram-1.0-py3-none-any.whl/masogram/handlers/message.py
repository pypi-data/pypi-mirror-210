from abc import ABC
from typing import Optional, cast

from masogram.filters import CommandObject
from masogram.handlers.base import BaseHandler, BaseHandlerMixin
from masogram.types import Chat, Message, User


class MessageHandler(BaseHandler[Message], ABC):
    """
    Base class for message handlers
    """

    @property
    def from_user(self) -> Optional[User]:
        return self.event.from_user

    @property
    def chat(self) -> Chat:
        return self.event.chat


class MessageHandlerCommandMixin(BaseHandlerMixin[Message]):
    @property
    def command(self) -> Optional[CommandObject]:
        if "command" in self.data:
            return cast(CommandObject, self.data["command"])
        return None
