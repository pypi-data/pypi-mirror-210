################
setMyDescription
################

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_my_description
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_my_description(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_my_description import SetMyDescription`
- alias: :code:`from masogram.methods import SetMyDescription`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetMyDescription(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetMyDescription(...)
