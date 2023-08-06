#####
close
#####

Returns: :obj:`bool`

.. automodule:: masogram.methods.close
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.close(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.close import Close`
- alias: :code:`from masogram.methods import Close`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(Close(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return Close(...)
