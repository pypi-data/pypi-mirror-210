########
Observer
########

Observer is used for filtering and handling different events. That is part of internal API with some public methods and is recommended to don't use methods is not listed here.

In `masogram` framework is available two variants of observer:

- `EventObserver <#eventobserver>`__
- `TelegramEventObserver <#telegrameventobserver>`__


EventObserver
=============

.. autoclass:: masogram.dispatcher.event.event.EventObserver
    :members: register, trigger, __call__
    :member-order: bysource


TelegramEventObserver
=====================

.. autoclass:: masogram.dispatcher.event.telegram.TelegramEventObserver
    :members: register, trigger, __call__, bind_filter, middleware, outer_middleware
    :member-order: bysource
