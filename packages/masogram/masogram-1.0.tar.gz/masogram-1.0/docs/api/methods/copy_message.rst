###########
copyMessage
###########

Returns: :obj:`MessageId`

.. automodule:: masogram.methods.copy_message
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: MessageId = await bot.copy_message(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.copy_message import CopyMessage`
- alias: :code:`from masogram.methods import CopyMessage`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: MessageId = await bot(CopyMessage(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return CopyMessage(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.copy_to`
