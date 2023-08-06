#############
deleteMessage
#############

Returns: :obj:`bool`

.. automodule:: masogram.methods.delete_message
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.delete_message(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.delete_message import DeleteMessage`
- alias: :code:`from masogram.methods import DeleteMessage`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(DeleteMessage(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return DeleteMessage(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.delete`
- :meth:`masogram.types.chat.Chat.delete_message`
