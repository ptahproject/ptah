Ptah Forms
==========

`ptah.form` is an optional form library package.  It provides some benefits when using it with the integrated environment such as autogeneration of forms for models, validation using the sqlalchemy constraints, and JSON representations for the REST api.  

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

.. code-block:: python
   :linenos:
   
    TELEPHONE_REGEX = u'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
    class Telephone(form.Regex):
        """ Telephone number validator """
        def __init__(self, msg=None):
            if msg is None:
                msg = "Invalid telephone number"
            super(Telephone, self).__init__(TELEPHONE_REGEX, msg=msg)

A `ptah.form.Field` accepts a `validator` in its constructor.  The 
fields' validator will be called by the form with both `field` and `value`
as parameters.

.. code-block:: python
   :linenos:
   :emphasize-lines: 5

    form.TextField(
        'phone',
        title = u'Telephone number',
        description=u'Please provide telephone number',
        validator = Telephone()),

Field Extraction
~~~~~~~~~~~~~~~~
Extracts the value from request.  

Field Factory
-------------
Expert level usage.  This is how Ptah's internals work.

Examples
--------

There are 2 form examples which can be found in `ptah_models` package in
the `examples repository <https://github.com/ptahproject/examples>`_.  You can find both examples in `ptah_models/views.py`.

Manual Form & Fieldset
~~~~~~~~~~~~~~~~~~~~~~

The contact-us form in `ptah_models`.

.. code-block:: python
   :linenos:

    contactform = form.Form(context, request)
    contactform.fields = form.Fieldset(
        form.TextField(
            'fullname',
            title = u'First & Last Name'),

        form.TextField(
            'phone',
            title = u'Telephone number',
            description=u'Please provide telephone number',
            validator = Telephone()),

        form.TextField(
            'email',
            title = u'Your email',
            description = u'Please provide email address.',
            validator = form.Email()),

        form.TextAreaField(
            'subject',
            title = u'How can we help?',
            missing = u''),
        )

    # form actions
    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()

        if errors:
            form.message(errors, 'form-error')
            return

        # form.context is ...
        form.context.fullname = data['fullname']
        form.context.phone = data['phone']
        form.context.email = data['email']
        form.context.subject = data['subject']

        # You would add any logic/database updates/insert here.
        # You would probably also redirect.

        log.info('The form was updated successfully')
        form.message('The form was updated successfully')

    contactform.label = u'Contact us'
    contactform.buttons.add_action('Update', action=updateAction)
    contactform.buttons.add_action('Cancel', action=cancelAction)

    # form default values
    contactform.content = {}

    # compute the form
    result = contactform.update()
    if isinstance(result, HTTPFound):
        return result
    
    # generate HTML from form
    html = contactform.render()


Manual Form & Auto-Fieldset
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the `ptah_models` package there is a content model, Link.  This model can
be found in ``ptah_models/models.py``.  This code-snippet is found in
the ``ptah_models/views.py``.   

.. code-block:: python
   :linenos:

    linkform = form.Form(context,request)
    linkform.fields = models.Link.__type__.fieldset

    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return

        link = models.Link(title = data['title'],
                           href = data['href'],
                           color = data['color'])
        ptah.get_session().add(link)

        form.message('Link has been created.')
        return HTTPFound(location='/')

    linkform.label = u'Add link'
    linkform.buttons.add_action('Add', action=updateAction)
    linkform.buttons.add_action('Cancel', action=cancelAction)

    result = linkform.update() # prepare form for rendering
    if isinstance(result, HTTPFound):
        return result

    rendered_form = linkform.render()

Everything Manual
~~~~~~~~~~~~~~~~~

Using form without context and request.

.. code-block:: python
   :linenos:

    from ptah import form
    from ptah_models.models import Link

    def action1(form):
        print ('action1', form)

    def action2(form):
        print ('action2', form)

    eform = form.Form(None, None)
    eform.params = {}
    eform.method = 'params'
    eform.fields = Link.__type__.fieldset

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

Class-based Form
~~~~~~~~~~~~~~~~

Example of subclassing ptah.form.Form.
