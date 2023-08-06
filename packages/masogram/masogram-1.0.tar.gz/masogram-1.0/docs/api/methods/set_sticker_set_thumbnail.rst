######################
setStickerSetThumbnail
######################

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_sticker_set_thumbnail
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_sticker_set_thumbnail(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_sticker_set_thumbnail import SetStickerSetThumbnail`
- alias: :code:`from masogram.methods import SetStickerSetThumbnail`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetStickerSetThumbnail(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetStickerSetThumbnail(...)
