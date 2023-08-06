########
sendDice
########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_dice
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_dice(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_dice import SendDice`
- alias: :code:`from masogram.methods import SendDice`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendDice(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendDice(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_dice`
- :meth:`masogram.types.message.Message.reply_dice`
