##############
sendChatAction
##############

Returns: :obj:`bool`

.. automodule:: masogram.methods.send_chat_action
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.send_chat_action(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_chat_action import SendChatAction`
- alias: :code:`from masogram.methods import SendChatAction`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SendChatAction(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendChatAction(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.do`
