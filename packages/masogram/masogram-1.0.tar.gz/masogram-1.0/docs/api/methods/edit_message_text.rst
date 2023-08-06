###############
editMessageText
###############

Returns: :obj:`Union[Message, bool]`

.. automodule:: masogram.methods.edit_message_text
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Union[Message, bool] = await bot.edit_message_text(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.edit_message_text import EditMessageText`
- alias: :code:`from masogram.methods import EditMessageText`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Union[Message, bool] = await bot(EditMessageText(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return EditMessageText(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.edit_text`
