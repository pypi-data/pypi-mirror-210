#####################
editGeneralForumTopic
#####################

Returns: :obj:`bool`

.. automodule:: masogram.methods.edit_general_forum_topic
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.edit_general_forum_topic(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.edit_general_forum_topic import EditGeneralForumTopic`
- alias: :code:`from masogram.methods import EditGeneralForumTopic`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(EditGeneralForumTopic(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return EditGeneralForumTopic(...)
