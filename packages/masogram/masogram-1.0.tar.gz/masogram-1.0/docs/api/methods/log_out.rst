######
logOut
######

Returns: :obj:`bool`

.. automodule:: masogram.methods.log_out
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.log_out(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.log_out import LogOut`
- alias: :code:`from masogram.methods import LogOut`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(LogOut(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return LogOut(...)
