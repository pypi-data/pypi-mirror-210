###############
unbanChatMember
###############

Returns: :obj:`bool`

.. automodule:: masogram.methods.unban_chat_member
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.unban_chat_member(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.unban_chat_member import UnbanChatMember`
- alias: :code:`from masogram.methods import UnbanChatMember`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(UnbanChatMember(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return UnbanChatMember(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.unban`
