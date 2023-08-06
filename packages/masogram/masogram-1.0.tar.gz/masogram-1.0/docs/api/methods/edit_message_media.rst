################
editMessageMedia
################

Returns: :obj:`Union[Message, bool]`

.. automodule:: masogram.methods.edit_message_media
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Union[Message, bool] = await bot.edit_message_media(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.edit_message_media import EditMessageMedia`
- alias: :code:`from masogram.methods import EditMessageMedia`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Union[Message, bool] = await bot(EditMessageMedia(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return EditMessageMedia(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.edit_media`
