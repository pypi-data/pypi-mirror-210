################
deleteStickerSet
################

Returns: :obj:`bool`

.. automodule:: masogram.methods.delete_sticker_set
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.delete_sticker_set(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.delete_sticker_set import DeleteStickerSet`
- alias: :code:`from masogram.methods import DeleteStickerSet`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(DeleteStickerSet(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return DeleteStickerSet(...)
