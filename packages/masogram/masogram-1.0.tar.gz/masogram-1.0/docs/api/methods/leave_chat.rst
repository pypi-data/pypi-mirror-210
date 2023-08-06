#########
leaveChat
#########

Returns: :obj:`bool`

.. automodule:: masogram.methods.leave_chat
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.leave_chat(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.leave_chat import LeaveChat`
- alias: :code:`from masogram.methods import LeaveChat`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(LeaveChat(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return LeaveChat(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.leave`
