from typing import Any

from masogram.handlers import PreCheckoutQueryHandler
from masogram.types import PreCheckoutQuery, User


class TestPreCheckoutQueryHandler:
    async def test_attributes_aliases(self):
        event = PreCheckoutQuery(
            id="query",
            from_user=User(id=42, is_bot=False, first_name="Test"),
            currency="BTC",
            total_amount=7,
            invoice_payload="payload",
        )

        class MyHandler(PreCheckoutQueryHandler):
            async def handle(self) -> Any:
                assert self.event == event
                assert self.from_user == self.event.from_user
                return True

        assert await MyHandler(event)
