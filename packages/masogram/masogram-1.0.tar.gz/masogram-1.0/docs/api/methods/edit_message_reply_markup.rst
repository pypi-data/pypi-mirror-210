######################
editMessageReplyMarkup
######################

Returns: :obj:`Union[Message, bool]`

.. automodule:: masogram.methods.edit_message_reply_markup
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Union[Message, bool] = await bot.edit_message_reply_markup(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.edit_message_reply_markup import EditMessageReplyMarkup`
- alias: :code:`from masogram.methods import EditMessageReplyMarkup`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Union[Message, bool] = await bot(EditMessageReplyMarkup(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return EditMessageReplyMarkup(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.edit_reply_markup`
