#########
sendAudio
#########

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_audio
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_audio(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_audio import SendAudio`
- alias: :code:`from masogram.methods import SendAudio`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendAudio(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendAudio(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_audio`
- :meth:`masogram.types.message.Message.reply_audio`
