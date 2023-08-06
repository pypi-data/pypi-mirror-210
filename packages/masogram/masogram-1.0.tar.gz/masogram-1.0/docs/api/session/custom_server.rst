Use Custom API server
=====================

.. autoclass:: masogram.client.telegram.TelegramAPIServer
    :members:

For example, if you want to use self-hosted API server:

.. code-block:: python3

    session = AiohttpSession(
        api=TelegramAPIServer.from_base('http://localhost:8082')
    )
    bot = Bot(..., session=session)
