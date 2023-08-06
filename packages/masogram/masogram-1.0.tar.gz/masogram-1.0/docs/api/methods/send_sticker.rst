###########
sendSticker
###########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_sticker
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_sticker(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_sticker import SendSticker`
- alias: :code:`from masogram.methods import SendSticker`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendSticker(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendSticker(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_sticker`
- :meth:`masogram.types.message.Message.reply_sticker`
