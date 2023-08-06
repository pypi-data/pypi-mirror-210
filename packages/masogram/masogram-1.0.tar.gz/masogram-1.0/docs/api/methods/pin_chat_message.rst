##############
pinChatMessage
##############

Returns: :obj:`bool`

.. automodule:: masogram.methods.pin_chat_message
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.pin_chat_message(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.pin_chat_message import PinChatMessage`
- alias: :code:`from masogram.methods import PinChatMessage`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(PinChatMessage(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return PinChatMessage(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.pin`
- :meth:`masogram.types.chat.Chat.pin_message`
