ptah.form
---------

.. automodule:: ptah.form

  .. py:data:: null

     Represents a null value in field-related operations.

  .. py:data:: required

     Represents a required value in field-related operations.

  .. autoclass:: Invalid

Form
~~~~

  .. autoclass:: Form
     :members:

  .. autoclass:: DisplayForm

  .. autoclass:: FormWidgets


Field
~~~~~

  .. autoclass:: Field
     :members:

  .. autoclass:: FieldFactory

  .. autoclass:: Fieldset
     :members:

  .. autoclass:: FieldsetErrors

  .. autoclass:: field

  .. autofunction:: fieldpreview

  .. autofunction:: get_field_factory

  .. autofunction:: get_field_preview


Button
~~~~~~

  .. autofunction:: button

  .. autoclass:: Button()

  .. autoclass:: Buttons

  .. py:data:: AC_DEFAULT

  .. py:data:: AC_PRIMARY

  .. py:data:: AC_DANGER

  .. py:data:: AC_SUCCESS

  .. py:data:: AC_INFO


Vocabulary
~~~~~~~~~~

  .. autoclass:: SimpleTerm
     :members:

  .. autoclass:: SimpleVocabulary
     :members:


Validators
~~~~~~~~~~

  .. autoclass:: All

  .. autoclass:: Function

  .. autoclass:: Regex

  .. autoclass:: Email

  .. autoclass:: Range

  .. autoclass:: Length

  .. autoclass:: OneOf


Predefined fields
~~~~~~~~~~~~~~~~~

  Any field can be create with two different way.
  Using field class:

  .. code-block:: python

      field = ptah.form.TextField(
          'field',
          title='Text',
	  description='Field description')


  Or using field factory:

  .. code-block:: python

      field = ptah.form.FieldFactory(
          'text', 'field',
          title='Text',
	  description='Field description')


  .. autoclass:: TextField

  .. autoclass:: IntegerField

  .. autoclass:: FloatField

  .. autoclass:: DecimalField

  .. autoclass:: TextAreaField

  .. autoclass:: FileField

  .. autoclass:: LinesField

  .. autoclass:: PasswordField

  .. autoclass:: DateField

  .. autoclass:: DateTimeField

  .. autoclass:: RadioField

  .. autoclass:: BoolField

  .. autoclass:: ChoiceField

  .. autoclass:: MultiChoiceField

  .. autoclass:: MultiSelectField

  .. autoclass:: JSDateField

  .. autoclass:: JSDateTimeField

  .. autoclass:: TinymceField


Form snippets
~~~~~~~~~~~~~

  .. py:data:: FORM_VIEW

  .. py:data:: FORM_ACTIONS

  .. py:data:: FORM_WIDGET

  .. py:data:: FORM_DISPLAY_WIDGET
