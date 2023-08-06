##################
setChatPermissions
##################

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_chat_permissions
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_chat_permissions(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_chat_permissions import SetChatPermissions`
- alias: :code:`from masogram.methods import SetChatPermissions`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetChatPermissions(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetChatPermissions(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.set_permissions`
