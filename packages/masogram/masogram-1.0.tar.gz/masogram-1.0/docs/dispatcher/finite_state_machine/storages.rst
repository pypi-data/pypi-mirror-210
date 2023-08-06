########
Storages
########

Storages out of the box
=======================

MemoryStorage
-------------

.. autoclass:: masogram.fsm.storage.memory.MemoryStorage
    :members: __init__
    :member-order: bysource

RedisStorage
------------

.. autoclass:: masogram.fsm.storage.redis.RedisStorage
    :members: __init__, from_url
    :member-order: bysource

Keys inside storage can be customized via key builders:

.. autoclass:: masogram.fsm.storage.redis.KeyBuilder
    :members:
    :member-order: bysource

.. autoclass:: masogram.fsm.storage.redis.DefaultKeyBuilder
    :members:
    :member-order: bysource


Writing own storages
====================

.. autoclass:: masogram.fsm.storage.base.BaseStorage
    :members:
    :member-order: bysource
