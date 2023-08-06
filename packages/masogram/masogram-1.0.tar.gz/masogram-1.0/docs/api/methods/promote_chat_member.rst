#################
promoteChatMember
#################

Returns: :obj:`bool`

.. automodule:: masogram.methods.promote_chat_member
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.promote_chat_member(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.promote_chat_member import PromoteChatMember`
- alias: :code:`from masogram.methods import PromoteChatMember`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(PromoteChatMember(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return PromoteChatMember(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat.Chat.promote`
