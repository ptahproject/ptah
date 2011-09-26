Ptah CMS API
------------

Public APIs
~~~~~~~~~~~

.. automodule:: ptah_cms

Content classes
~~~~~~~~~~~~~~~

  .. autoclass:: Node

  .. autoclass:: Content

  .. autoclass:: Container
     :members: keys, get, items, values, __contains__, __getitem__, __setitem__, __delitem__


Content loading
~~~~~~~~~~~~~~~

  .. autofunction:: loadNode

  .. autofunction:: loadParents


Type system
~~~~~~~~~~~

  .. autofunction:: Type

  .. py:data:: Types

     All registered types in system

  .. autoclass:: TypeInformation


Content action
~~~~~~~~~~~~~~

  .. autofunction:: listActions

  .. autofunction:: contentAction


Application Root/Factory/Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. py:class:: ApplicationRoot

  .. py:class:: ApplicationPolicy

  .. py:class:: ApplicationFactory

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

  .. py:class:: ContentEvent

  .. py:class:: ContentCreatedEvent

  .. py:class:: ContentAddedEvent

  .. py:class:: ContentMovedEvent

  .. py:class:: ContentModifiedEvent

  .. py:class:: ContentDeletingEvent
