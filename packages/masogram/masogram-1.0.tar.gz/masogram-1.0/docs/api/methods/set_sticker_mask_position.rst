######################
setStickerMaskPosition
######################

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_sticker_mask_position
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_sticker_mask_position(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_sticker_mask_position import SetStickerMaskPosition`
- alias: :code:`from masogram.methods import SetStickerMaskPosition`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetStickerMaskPosition(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetStickerMaskPosition(...)
