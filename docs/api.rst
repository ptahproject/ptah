Ptah CMS API
------------

.. automodule:: ptah_cms

Content classes
~~~~~~~~~~~~~~~

  .. autoclass:: Node

  .. autoclass:: Content

  .. autoclass:: Container
     :members: keys, get, items, values, __contains__, __getitem__, __setitem__, __delitem__


Content loading
~~~~~~~~~~~~~~~

  .. autofunction:: load

  .. autofunction:: load_parents


Type system
~~~~~~~~~~~

  .. autofunction:: Type

  .. py:data:: Types

     Dictionary `Types` contains all registered types in system.

  .. autoclass:: TypeInformation


Application Root/Factory/Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. autoclass:: ApplicationRoot

  .. autoclass:: ApplicationPolicy

  .. autoclass:: ApplicationFactory

Blob api
~~~~~~~~

  .. py:data:: blobStorage

  .. py:class:: IBlob

  .. py:class:: IBlobStorage

Content schema
~~~~~~~~~~~~~~

  .. py:class:: ContentSchema

  .. py:class:: ContentNameSchema


Permissions
~~~~~~~~~~~

  .. py:data:: View

  .. py:data:: AddContent

  .. py:data:: DeleteContent

  .. py:data:: ModifyContent

  .. py:data:: ShareContent

  .. py:data:: NOT_ALLOWED

  .. py:data:: ALL_PERMISSIONS


Events
~~~~~~

  .. autoclass:: ContentEvent

  .. autoclass:: ContentCreatedEvent

  .. autoclass:: ContentAddedEvent

  .. autoclass:: ContentMovedEvent

  .. autoclass:: ContentModifiedEvent

  .. autoclass:: ContentDeletingEvent
