##########################
unpinAllForumTopicMessages
##########################

Returns: :obj:`bool`

.. automodule:: masogram.methods.unpin_all_forum_topic_messages
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.unpin_all_forum_topic_messages(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.unpin_all_forum_topic_messages import UnpinAllForumTopicMessages`
- alias: :code:`from masogram.methods import UnpinAllForumTopicMessages`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(UnpinAllForumTopicMessages(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return UnpinAllForumTopicMessages(...)
