##########
getUpdates
##########

Returns: :obj:`List[Update]`

.. automodule:: masogram.methods.get_updates
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: List[Update] = await bot.get_updates(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_updates import GetUpdates`
- alias: :code:`from masogram.methods import GetUpdates`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: List[Update] = await bot(GetUpdates(...))
