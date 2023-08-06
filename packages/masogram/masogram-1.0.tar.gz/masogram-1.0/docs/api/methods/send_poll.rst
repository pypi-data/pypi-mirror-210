########
sendPoll
########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_poll
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_poll(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_poll import SendPoll`
- alias: :code:`from masogram.methods import SendPoll`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendPoll(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendPoll(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_poll`
- :meth:`masogram.types.message.Message.reply_poll`
