#####################
getMyShortDescription
#####################

Returns: :obj:`BotShortDescription`

.. automodule:: masogram.methods.get_my_short_description
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: BotShortDescription = await bot.get_my_short_description(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_my_short_description import GetMyShortDescription`
- alias: :code:`from masogram.methods import GetMyShortDescription`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: BotShortDescription = await bot(GetMyShortDescription(...))
