###########
sendMessage
###########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_message
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_message(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_message import SendMessage`
- alias: :code:`from masogram.methods import SendMessage`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendMessage(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendMessage(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer`
- :meth:`masogram.types.message.Message.reply`
