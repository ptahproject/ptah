Ptah in Memphis Forms
=====================

There are several aspect to Forms when working with Ptah that you should understand.  ptah.form provides the fields library and form infrastucture.  The only public usage of Form is in ptah.form and ptah.cmsapp.  Ptah App provides two forms, AddForm and EditForm found at ptah.cmsapp/forms.py which can assume you are working with content and provides form actions such as Submit and Cancel.

Form
----
Supports HTML generation, CSRF protection, additional field validation.

Form Validation
~~~~~~~~~~~~~~~
The default form validation uses CSRF prtoection to validate data input.

Fieldset
--------
A ordered dictionary of Field instances. Fieldset supports validation and extraction.

Fieldset Validation
~~~~~~~~~~~~~~~~~~~
Is used when you have validation dependencies between Fields.  For instance if Field Y depends

Fieldset Extraction
~~~~~~~~~~~~~~~~~~~
Internal implementation details and only needed for expert usage.  Possibly needs renaming or refactoring.

Field
-----

Fields are important in Ptah not only because its how forms are used in the HTML interface but they are also used in the REST interface.  For instance when you send update via HTTP (html POST or json POST) the same field implementation is used for deserialization and validation.

Field Serialization
~~~~~~~~~~~~~~~~~~~

  * serialize converts the field and data python structure into string representation. e.g. dattime.date(2011, 12, 12) into '2011-12-12'.
  
  * deserailize converts a string representation into the internal representation.  e.g. `2011-12-12` into datetime.date(2011, 12, 12)
  
Field Modes
~~~~~~~~~~~
Display mode and input mode.

Field Validation
~~~~~~~~~~~~~~~~
Specific validation rules or whether a field is required is validated through the field validation.

Field Extraction
~~~~~~~~~~~~~~~~
Extracts the value from request.  

Field Factory
-------------
Expert level usage.  This is how Ptah's internals work.

Examples
--------
This is low level internal implementation note for manually working with forms.
This example does not contain the droids you are looking for.

Using form without context and request::

    from pprint import pprint
    from ptah import form
    from ptah.cmsapp.content import Page

    def action1(form):
        print ('action1', form)

    def action2(form):
        print ('action2', form)

    eform = form.Form(None, None)
    eform.params = {}
    eform.method = 'params'
    eform.fields = Page.__type__.fieldset

    eform.buttons.add_action('Test submit', name='ac1', action=action1)
    eform.buttons.add_action('Test action2', name='ac2', action=action2)

    print "==== execute action1 ===="
    eform.params = {'%sbuttons.ac1'%eform.prefix: 'value'}
    eform.update()

    print
    print "==== extract data ====="
    data, errors = eform.extract()

    print
    print "DATA:"
    pprint(data)

    print
    print "ERRORS:"
    pprint(errors)