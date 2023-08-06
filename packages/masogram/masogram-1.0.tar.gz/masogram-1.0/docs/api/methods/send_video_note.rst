#############
sendVideoNote
#############

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_video_note
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_video_note(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_video_note import SendVideoNote`
- alias: :code:`from masogram.methods import SendVideoNote`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendVideoNote(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendVideoNote(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_video_note`
- :meth:`masogram.types.message.Message.reply_video_note`
