###############################
getMyDefaultAdministratorRights
###############################

Returns: :obj:`ChatAdministratorRights`

.. automodule:: masogram.methods.get_my_default_administrator_rights
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: ChatAdministratorRights = await bot.get_my_default_administrator_rights(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_my_default_administrator_rights import GetMyDefaultAdministratorRights`
- alias: :code:`from masogram.methods import GetMyDefaultAdministratorRights`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: ChatAdministratorRights = await bot(GetMyDefaultAdministratorRights(...))
