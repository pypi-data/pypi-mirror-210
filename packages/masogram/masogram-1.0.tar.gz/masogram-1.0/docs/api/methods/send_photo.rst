#########
sendPhoto
#########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_photo
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_photo(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_photo import SendPhoto`
- alias: :code:`from masogram.methods import SendPhoto`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendPhoto(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendPhoto(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_photo`
- :meth:`masogram.types.message.Message.reply_photo`
