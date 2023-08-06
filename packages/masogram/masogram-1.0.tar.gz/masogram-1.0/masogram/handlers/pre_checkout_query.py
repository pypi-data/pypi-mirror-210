from abc import ABC

from masogram.handlers import BaseHandler
from masogram.types import PreCheckoutQuery, User


class PreCheckoutQueryHandler(BaseHandler[PreCheckoutQuery], ABC):
    """
    Base class for pre-checkout handlers
    """

    @property
    def from_user(self) -> User:
        return self.event.from_user
