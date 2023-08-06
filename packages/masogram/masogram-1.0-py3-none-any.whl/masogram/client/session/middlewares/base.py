from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Awaitable, Callable, Union

from masogram.methods import Response, TelegramMethod
from masogram.methods.base import TelegramType

if TYPE_CHECKING:
    from ...bot import Bot

NextRequestMiddlewareType = Callable[
    ["Bot", TelegramMethod[TelegramType]], Awaitable[Response[TelegramType]]
]
RequestMiddlewareType = Union[
    "BaseRequestMiddleware",
    Callable[
        [NextRequestMiddlewareType[TelegramType], "Bot", TelegramMethod[TelegramType]],
        Awaitable[Response[TelegramType]],
    ],
]


class BaseRequestMiddleware(ABC):
    """
    Generic middleware class
    """

    @abstractmethod
    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: "Bot",
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        """
        Execute middleware

        :param make_request: Wrapped make_request in middlewares chain
        :param bot: bot for request making
        :param method: Request method (Subclass of :class:`masogram.methods.base.TelegramMethod`)

        :return: :class:`masogram.methods.Response`
        """
        pass
