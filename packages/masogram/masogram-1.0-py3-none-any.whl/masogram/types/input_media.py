from __future__ import annotations

from .base import MutableTelegramObject


class InputMedia(MutableTelegramObject):
    """
    This object represents the content of a media message to be sent. It should be one of

     - :class:`masogram.types.input_media_animation.InputMediaAnimation`
     - :class:`masogram.types.input_media_document.InputMediaDocument`
     - :class:`masogram.types.input_media_audio.InputMediaAudio`
     - :class:`masogram.types.input_media_photo.InputMediaPhoto`
     - :class:`masogram.types.input_media_video.InputMediaVideo`

    Source: https://core.telegram.org/bots/api#inputmedia
    """
