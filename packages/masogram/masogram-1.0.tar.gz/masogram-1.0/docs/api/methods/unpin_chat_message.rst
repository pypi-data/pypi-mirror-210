################
unpinChatMessage
################

Returns: :obj:`bool`

.. automodule:: masogram.methods.unpin_chat_message
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.unpin_chat_message(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.unpin_chat_message import UnpinChatMessage`
- alias: :code:`from masogram.methods import UnpinChatMessage`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(UnpinChatMessage(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return UnpinChatMessage(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.unpin`
- :meth:`masogram.types.chat.Chat.unpin_message`
