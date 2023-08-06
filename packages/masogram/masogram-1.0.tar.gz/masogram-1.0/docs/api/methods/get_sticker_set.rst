#############
getStickerSet
#############

Returns: :obj:`StickerSet`

.. automodule:: masogram.methods.get_sticker_set
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: StickerSet = await bot.get_sticker_set(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_sticker_set import GetStickerSet`
- alias: :code:`from masogram.methods import GetStickerSet`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: StickerSet = await bot(GetStickerSet(...))
