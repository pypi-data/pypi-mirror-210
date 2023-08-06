from masogram import Router
from masogram.filters import Filter
from masogram.types import Message

router = Router()


class MyFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text


@router.message(MyFilter("hello"))
async def my_handler(message: Message):
    ...
