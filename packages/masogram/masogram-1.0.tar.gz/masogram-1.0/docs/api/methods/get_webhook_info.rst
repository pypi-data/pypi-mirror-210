##############
getWebhookInfo
##############

Returns: :obj:`WebhookInfo`

.. automodule:: masogram.methods.get_webhook_info
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: WebhookInfo = await bot.get_webhook_info(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_webhook_info import GetWebhookInfo`
- alias: :code:`from masogram.methods import GetWebhookInfo`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: WebhookInfo = await bot(GetWebhookInfo(...))
