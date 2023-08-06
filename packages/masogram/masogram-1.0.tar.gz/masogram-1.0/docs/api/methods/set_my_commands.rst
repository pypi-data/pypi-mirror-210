#############
setMyCommands
#############

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_my_commands
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_my_commands(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_my_commands import SetMyCommands`
- alias: :code:`from masogram.methods import SetMyCommands`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetMyCommands(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetMyCommands(...)
