###########
sendContact
###########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_contact
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_contact(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_contact import SendContact`
- alias: :code:`from masogram.methods import SendContact`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendContact(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendContact(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_contact`
- :meth:`masogram.types.message.Message.reply_contact`
