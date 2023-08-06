#######################
unhideGeneralForumTopic
#######################

Returns: :obj:`bool`

.. automodule:: masogram.methods.unhide_general_forum_topic
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.unhide_general_forum_topic(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.unhide_general_forum_topic import UnhideGeneralForumTopic`
- alias: :code:`from masogram.methods import UnhideGeneralForumTopic`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(UnhideGeneralForumTopic(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return UnhideGeneralForumTopic(...)
