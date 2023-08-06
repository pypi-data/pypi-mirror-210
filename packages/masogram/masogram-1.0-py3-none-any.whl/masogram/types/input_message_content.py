from __future__ import annotations

from .base import MutableTelegramObject


class InputMessageContent(MutableTelegramObject):
    """
    This object represents the content of a message to be sent as a result of an inline query. Telegram clients currently support the following 5 types:

     - :class:`masogram.types.input_text_message_content.InputTextMessageContent`
     - :class:`masogram.types.input_location_message_content.InputLocationMessageContent`
     - :class:`masogram.types.input_venue_message_content.InputVenueMessageContent`
     - :class:`masogram.types.input_contact_message_content.InputContactMessageContent`
     - :class:`masogram.types.input_invoice_message_content.InputInvoiceMessageContent`

    Source: https://core.telegram.org/bots/api#inputmessagecontent
    """
