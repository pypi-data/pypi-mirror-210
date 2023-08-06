########
stopPoll
########

Returns: :obj:`Poll`

.. automodule:: masogram.methods.stop_poll
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Poll = await bot.stop_poll(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.stop_poll import StopPoll`
- alias: :code:`from masogram.methods import StopPoll`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Poll = await bot(StopPoll(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return StopPoll(...)
