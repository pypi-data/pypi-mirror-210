######################
getCustomEmojiStickers
######################

Returns: :obj:`List[Sticker]`

.. automodule:: masogram.methods.get_custom_emoji_stickers
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: List[Sticker] = await bot.get_custom_emoji_stickers(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_custom_emoji_stickers import GetCustomEmojiStickers`
- alias: :code:`from masogram.methods import GetCustomEmojiStickers`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: List[Sticker] = await bot(GetCustomEmojiStickers(...))
