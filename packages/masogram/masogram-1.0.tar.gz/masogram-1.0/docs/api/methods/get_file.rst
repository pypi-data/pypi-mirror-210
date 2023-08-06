#######
getFile
#######

Returns: :obj:`File`

.. automodule:: masogram.methods.get_file
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: File = await bot.get_file(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_file import GetFile`
- alias: :code:`from masogram.methods import GetFile`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: File = await bot(GetFile(...))
