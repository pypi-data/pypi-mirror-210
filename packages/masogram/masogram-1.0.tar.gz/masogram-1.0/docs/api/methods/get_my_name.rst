#########
getMyName
#########

Returns: :obj:`BotName`

.. automodule:: masogram.methods.get_my_name
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: BotName = await bot.get_my_name(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_my_name import GetMyName`
- alias: :code:`from masogram.methods import GetMyName`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: BotName = await bot(GetMyName(...))
