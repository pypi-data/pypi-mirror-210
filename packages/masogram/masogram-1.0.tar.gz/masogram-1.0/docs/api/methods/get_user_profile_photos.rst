####################
getUserProfilePhotos
####################

Returns: :obj:`UserProfilePhotos`

.. automodule:: masogram.methods.get_user_profile_photos
    :members:
    :member-order: bysource
    :undoc-members: True


Usage
=====

As bot method
-------------

.. code-block::

    result: UserProfilePhotos = await bot.get_user_profile_photos(...)


Method as object
----------------

Imports:

- :code:`from masogram.methods.get_user_profile_photos import GetUserProfilePhotos`
- alias: :code:`from masogram.methods import GetUserProfilePhotos`

With specific bot
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result: UserProfilePhotos = await bot(GetUserProfilePhotos(...))




As shortcut from received object
--------------------------------

- :meth:`masogram.types.user.User.get_profile_photos`
