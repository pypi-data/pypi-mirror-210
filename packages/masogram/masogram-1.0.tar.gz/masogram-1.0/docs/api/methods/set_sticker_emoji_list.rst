###################
setStickerEmojiList
###################

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_sticker_emoji_list
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_sticker_emoji_list(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_sticker_emoji_list import SetStickerEmojiList`
- alias: :code:`from masogram.methods import SetStickerEmojiList`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetStickerEmojiList(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetStickerEmojiList(...)
