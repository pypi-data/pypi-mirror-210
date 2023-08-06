################
getMyDescription
################

Returns: :obj:`BotDescription`

.. automodule:: masogram.methods.get_my_description
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: BotDescription = await bot.get_my_description(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_my_description import GetMyDescription`
- alias: :code:`from masogram.methods import GetMyDescription`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: BotDescription = await bot(GetMyDescription(...))
