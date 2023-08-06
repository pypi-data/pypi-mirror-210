###############
deleteChatPhoto
###############

Returns: :obj:`bool`

.. automodule:: masogram.methods.delete_chat_photo
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.delete_chat_photo(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.delete_chat_photo import DeleteChatPhoto`
- alias: :code:`from masogram.methods import DeleteChatPhoto`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(DeleteChatPhoto(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return DeleteChatPhoto(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.delete_photo`
