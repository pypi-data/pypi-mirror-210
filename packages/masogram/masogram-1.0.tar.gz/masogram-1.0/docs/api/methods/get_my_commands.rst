#############
getMyCommands
#############

Returns: :obj:`List[BotCommand]`

.. automodule:: masogram.methods.get_my_commands
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: List[BotCommand] = await bot.get_my_commands(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_my_commands import GetMyCommands`
- alias: :code:`from masogram.methods import GetMyCommands`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: List[BotCommand] = await bot(GetMyCommands(...))
