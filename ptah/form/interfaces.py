""" Form and Field Interfaces """
from zope import interface
from zope.interface.common import mapping
from translationstring import TranslationStringFactory

MessageFactory = _ = TranslationStringFactory('ptah.form')

FORM_INPUT = 'form-input'
FORM_DISPLAY = 'form-display'


class Invalid(Exception):
    """An exception raised by data types and validators indicating that
    the value for a particular node was not valid."""

    def __init__(self, field, msg):
        self.field = field
        self.msg = msg

    def __str__(self):
        return 'Invalid: %s: <%s>' % (self.field, self.msg)

    def __repr__(self):
        return 'Invalid(%s: <%s>)' % (self.field, self.msg)


class _null(object):
    """ Represents a null value in field-related operations. """

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return '<widget.null>'

null = _null()


class _required(object):
    """ Represents a required value in field-related operations. """

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return '<widget.required>'

required = _required()


# ----[ Vocabulary ]----------------------------------------------------------

# vocabulary/term interfaces
class ITerm(interface.Interface):
    """ term """

    value = interface.Attribute('Value')
    token = interface.Attribute('Token')
    title = interface.Attribute('Title')


class IVocabulary(interface.Interface):
    """ vocabulary """

    def get_term(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def get_term_bytoken(token):
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def get_value(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """

    def __iter__():
        """Iterate over terms."""

    def __len__():
        """Return number of terms."""

    def __contains__(value):
        """Check wether terms containes the ``value``."""


# ----[ Widgets ]------------------------------------------------------------

class IWidget(interface.Interface):
    """A widget within a form"""

    node = interface.Attribute('Schema node')
    typ = interface.Attribute('Schema type')

    id = interface.Attribute('Id')
    name = interface.Attribute('Name')
    label = interface.Attribute('Label')
    description = interface.Attribute('Description')
    mode = interface.Attribute('Mode')
    required = interface.Attribute('Required')
    error = interface.Attribute('Error')
    form_value = interface.Attribute('Form Value')
    params = interface.Attribute('Request params')
    localizer = interface.Attribute('Localizer')

    template = interface.Attribute('Template')
    widgetTemplate = interface.Attribute('Widget template')

    value = interface.Attribute('Widget value')

    def extract(default=null):
        """Extract the string value(s) of the widget from the form.

        The return value may be any Python construct, but is typically a
        simple string, sequence of strings or a dictionary.

        The value *must not* be converted into a native format.

        If an error occurs during the extraction, the default value should be
        returned. Since this should never happen, if the widget is properly
        designed and used, it is okay to NOT raise an error here, since we do
        not want to crash the system during an inproper request.

        If there is no value to extract, the default is to be returned.
        """

    def update(request):
        """Setup all of the widget information used for displaying."""

    def render(request):
        """Render form widget. First it tring to use template. If template is
        not set then it uses one of the snippets."""

    def serialize(value):
        """ serialize value into widget compatible form """

    def deserialize(value):
        """ deserialize value """

    def loads(value):
        """ load value from json format """

    def dumps(value):
        """ dumps value to json format """


class ISequenceWidget(IWidget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    noValueToken = interface.Attribute('NO_VALUE Token')
    terms = interface.Attribute('Terms')

    def updateTerms():
        """Update the widget's ``terms`` attribute and return the terms.

        This method can be used by external components to get the terms
        without having to worry whether they are already created or not.
        """


class IWidgets(mapping.IEnumerableMapping):
    """A widget manager"""

    prefix = interface.Attribute('Prefix')
    mode = interface.Attribute('Mode')
    errors = interface.Attribute('Errors')

    def update():
        """Setup widgets."""

    def extract(setErrors=True):
        """Extract the values from the widgets and validate them."""


# ----[ Buttons ]------------------------------------------------------------

class IButton(interface.Interface):
    """A button in a form."""

    accessKey = interface.Attribute('Access Key')
    actype = interface.Attribute('Action type (i.e. primary, danger, etc)')
    condition = interface.Attribute('Callable, first argument is form instance')


class IButtons(mapping.IEnumerableMapping):
    """Buttons manager."""


class IActions(mapping.IEnumerableMapping):
    """A button widgets manager"""

    prefix = interface.Attribute('Prefix')

    def update():
        """Setup button widgets."""

    def execute():
        """Execute selected button action."""


# ----[ Forms ]--------------------------------------------------------------

class IForm(interface.Interface):
    """Form"""

    mode = interface.Attribute('Mode')
    widgets = interface.Attribute('Widgets')
    label = interface.Attribute('Label')
    prefix = interface.Attribute('Prefix')
    fields = interface.Attribute('Fields')
    buttons = interface.Attribute('Buttons')

    def form_params():
        '''Return the request params dict.'''

    def form_content():
        '''Return the content to be displayed and/or edited.'''

    def update_widgets():
        '''Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.
        '''

    def validate(data, errors):
        ''' Do form level validation, like schema invariants, etc.

        Add errors to errors (IErrors) object.
        '''

    def extract(setErrors=True):
        '''Extract the data of the form.

        setErrors: needs to be passed to extract() and to sub-widgets'''

    def update():
        '''Update the form.'''

    def render():
        '''Render the form.'''


class IDisplayForm(IForm):
    """Mark a form as display form, used for templates."""


class IInputForm(interface.Interface):
    """A form that is meant to process the input of the form controls."""

    id = interface.Attribute('Id')
    name = interface.Attribute('Name')
    method = interface.Attribute('Method')
    action = interface.Attribute('Action')
    enctype = interface.Attribute('Encoding Type')
    accept = interface.Attribute('Accepted Content Types')
    acceptCharset = interface.Attribute('Accepted Character Sets')

    csrf = interface.Attribute('Enable csrf protection')
    csrfname = interface.Attribute('csrf field name')
    token = interface.Attribute('csrf token')


def Validator(field, value):
    """
    A validator is called during field value validation.

    If ``value`` is not valid, raise a :class:`ptah.form.Invalid`
    instance as an exception after.

    ``field`` is a :class:`ptah.form.Field` instance, for use when
    raising a :class:`ptah.form.Invalid` exception.
    """


def Preview(request):
    """
    A preview is called by ``Field types`` management module.

    :param request: Pyramid request object
    :rtype: Html snippet
    """
