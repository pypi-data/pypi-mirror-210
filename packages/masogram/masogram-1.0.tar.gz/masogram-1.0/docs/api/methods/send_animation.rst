#############
sendAnimation
#############

Returns: :obj:`Message`

.. automodule:: masogram.methods.send_animation
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Message = await bot.send_animation(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.send_animation import SendAnimation`
- alias: :code:`from masogram.methods import SendAnimation`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Message = await bot(SendAnimation(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SendAnimation(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.answer_animation`
- :meth:`masogram.types.message.Message.reply_animation`
