from abc import ABC

from masogram.handlers import BaseHandler
from masogram.types import ShippingQuery, User


class ShippingQueryHandler(BaseHandler[ShippingQuery], ABC):
    """
    Base class for shipping query handlers
    """

    @property
    def from_user(self) -> User:
        return self.event.from_user
