############
sendLocation
############

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_location
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_location(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_location import SendLocation`
- alias: :code:`from masogram.methods import SendLocation`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendLocation(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendLocation(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_location`
- :meth:`masogram.types.message.Message.reply_location`
