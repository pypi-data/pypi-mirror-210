########
sendGame
########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_game
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_game(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_game import SendGame`
- alias: :code:`from masogram.methods import SendGame`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendGame(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendGame(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_game`
- :meth:`masogram.types.message.Message.reply_game`
