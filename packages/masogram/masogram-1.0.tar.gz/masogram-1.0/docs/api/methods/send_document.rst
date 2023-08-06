############
sendDocument
############

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_document
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_document(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_document import SendDocument`
- alias: :code:`from masogram.methods import SendDocument`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendDocument(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendDocument(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_document`
- :meth:`masogram.types.message.Message.reply_document`
