#####
getMe
#####

Returns: :obj:`User`

.. automodule:: masogram.methods.get_me
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: User = await bot.get_me(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_me import GetMe`
- alias: :code:`from masogram.methods import GetMe`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: User = await bot(GetMe(...))
