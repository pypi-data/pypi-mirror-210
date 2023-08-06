#######################
stopMessageLiveLocation
#######################

Returns: :obj:`Union[Message, bool]`

.. automodule:: masogram.methods.stop_message_live_location
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: Union[Message, bool] = await bot.stop_message_live_location(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.stop_message_live_location import StopMessageLiveLocation`
- alias: :code:`from masogram.methods import StopMessageLiveLocation`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: Union[Message, bool] = await bot(StopMessageLiveLocation(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return StopMessageLiveLocation(...)


As shortcut from received object
--------------------------------

- :meth:`masogram.types.message.Message.stop_live_location`
