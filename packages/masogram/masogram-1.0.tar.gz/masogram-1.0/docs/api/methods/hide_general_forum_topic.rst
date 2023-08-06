#####################
hideGeneralForumTopic
#####################

Returns: :obj:`bool`

.. automodule:: masogram.methods.hide_general_forum_topic
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.hide_general_forum_topic(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.hide_general_forum_topic import HideGeneralForumTopic`
- alias: :code:`from masogram.methods import HideGeneralForumTopic`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(HideGeneralForumTopic(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return HideGeneralForumTopic(...)
