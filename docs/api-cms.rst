ptah.cms
--------

.. automodule:: ptah.cms

Content classes
~~~~~~~~~~~~~~~

  .. autoclass:: Node

  .. autoclass:: BaseContent

  .. autoclass:: Content

  .. autoclass:: BaseContainer

  .. autoclass:: Container
     :members: keys, get, items, values, __contains__, __getitem__, __setitem__, __delitem__


Content loading
~~~~~~~~~~~~~~~

  .. autofunction:: load

  .. autofunction:: load_parents

Type system
~~~~~~~~~~~

  .. autofunction:: get_type

  .. autofunction:: get_types

  .. autofunction:: Type

  .. autoclass:: TypeInformation


Application Root/Factory/Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. autofunction:: get_app_factories

  .. autoclass:: ApplicationRoot

  .. autoclass:: ApplicationPolicy

  .. autoclass:: ApplicationFactory

  .. autofunction:: get_policy

  .. autofunction:: set_policy

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
