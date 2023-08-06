###################
unbanChatSenderChat
###################

Returns: :obj:`bool`

.. automodule:: masogram.methods.unban_chat_sender_chat
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.unban_chat_sender_chat(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.unban_chat_sender_chat import UnbanChatSenderChat`
- alias: :code:`from masogram.methods import UnbanChatSenderChat`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(UnbanChatSenderChat(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return UnbanChatSenderChat(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.unban_sender_chat`
