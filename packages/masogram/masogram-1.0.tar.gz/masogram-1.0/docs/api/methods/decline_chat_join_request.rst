######################
declineChatJoinRequest
######################

Returns: :obj:`bool`

.. automodule:: masogram.methods.decline_chat_join_request
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.decline_chat_join_request(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.decline_chat_join_request import DeclineChatJoinRequest`
- alias: :code:`from masogram.methods import DeclineChatJoinRequest`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(DeclineChatJoinRequest(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return DeclineChatJoinRequest(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.chat_join_request.ChatJoinRequest.decline`
