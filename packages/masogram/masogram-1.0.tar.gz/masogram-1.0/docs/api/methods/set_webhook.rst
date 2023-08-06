##########
setWebhook
##########

Returns: :obj:`bool`

.. automodule:: masogram.methods.set_webhook
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: bool = await bot.set_webhook(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.set_webhook import SetWebhook`
- alias: :code:`from masogram.methods import SetWebhook`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: bool = await bot(SetWebhook(...))

As reply into Webhook in handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    return SetWebhook(...)
