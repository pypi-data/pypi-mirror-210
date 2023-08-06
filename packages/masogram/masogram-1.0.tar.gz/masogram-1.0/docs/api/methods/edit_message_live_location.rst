#######################
editMessageLiveLocation
#######################

Returns: :obj:`Union[Message, bool]`

.. automodule:: masogram.methods.edit_message_live_location
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Union[Message, bool] = await bot.edit_message_live_location(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.edit_message_live_location import EditMessageLiveLocation`
- alias: :code:`from masogram.methods import EditMessageLiveLocation`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Union[Message, bool] = await bot(EditMessageLiveLocation(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return EditMessageLiveLocation(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.edit_live_location`
