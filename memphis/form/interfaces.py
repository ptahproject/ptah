""" Form and Widget Framework Interfaces """
from zope import interface
from zope.interface.common import mapping
from translationstring import TranslationStringFactory

MessageFactory = _ = TranslationStringFactory('memphis.form')


class INPUT_MODE(interface.Interface):
    """ Input mode """


class DISPLAY_MODE(interface.Interface):
    """ display mode """


class HIDDEN_MODE(interface.Interface):
    """ hidden mode """


class NOT_CHANGED(object):

    def __repr__(self):
        return '<NOT_CHANGED>'

NOT_CHANGED = NOT_CHANGED()


class NO_VALUE(object):
    def __repr__(self):
        return '<NO_VALUE>'

NO_VALUE = NO_VALUE()


# ----[ Generic Manager Interfaces ]-----------------------------------------

class IManager(mapping.IEnumerableMapping):
    """A manager of some kind of items.

    *Important*: While managers are mappings, the order of the items is
     assumed to be important! Effectively a manager is an ordered mapping.

    In general, managers do not have to support a manipulation
    API. Oftentimes, managers are populated during initialization or while
    updating.
    """

class ISelectionManager(IManager):
    """Managers that support item selection and management.

    This manager allows one to more carefully specify the contained items.

    *Important*: The API is chosen in a way, that the manager is still
    immutable. All methods in this interface must return *new* instances of
    the manager.
    """

    def __add__(other):
        """Used for merge two managers."""

    def select(*names):
        """Return a modified instance with an ordered subset of items."""

    def omit(*names):
        """Return a modified instance omitting given items."""

    def copy():
        """Copy all items to a new instance and return it."""


# ----[ Validators ]---------------------------------------------------------

class IFormValidator(interface.Interface):
    """A validator for a form."""

    def validate(data, errors):
        """ validate data, errors is IErrors object """


# ----[ Errors ]--------------------------------------------------------------

class IErrors(interface.Interface):
    """ list """

    def append(error):
        """ append error """

    def extend(errors):
        """ extend with errors """

    def getWidgetError(name, default=None):
        """ return widget error """


class IWidgetError(interface.Interface):
    """ A special error, for can return additional errors and explicitly 
    set to which widget this error should be appied. """

    name = interface.Attribute('Widget name')

    error = interface.Attribute('Error instance')


class IErrorViewSnippet(interface.Interface):
    """A view providing a view for an error"""

    widget = interface.Attribute('Widget')

    error = interface.Attribute('Error')

    def update():
        """Update view."""

    def render():
        """Render view."""


class IMultipleErrors(interface.Interface):
    """An error that contains many errors"""

    errors = interface.Attribute("List of errors")


# ----[ Fields ]--------------------------------------------------------------

class IField(interface.Interface):
    """Field wrapping a schema field used in the form."""

    name = interface.Attribute('Title')
    field = interface.Attribute('Schema Field')
    prefix = interface.Attribute('Prefix')
    mode = interface.Attribute('Mode')
    widgetFactory = interface.Attribute('Widget Factory')


class IFields(ISelectionManager):
    """IField manager."""

    def select(prefix=None, interface=None, *names):
        """Return a modified instance with an ordered subset of items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """

    def omit(prefix=None, interface=None, *names):
        """Return a modified instance omitting given items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """


# ----[ Data Managers ]------------------------------------------------------

class IDataManager(interface.Interface):
    """Data manager."""

    def get():
        """Get the value.

        If no value can be found, raise an error
        """

    def query(default=NO_VALUE):
        """Get the value.

        If no value can be found, return the default value.
        If access is forbidden, raise an error.
        """

    def set(value):
        """Set the value"""


# term interfaces
class ITerms(interface.Interface):
    """ terms """

    context = interface.Attribute('context')
    field = interface.Attribute('Schema node')
    typ = interface.Attribute('Schem type')
    widget = interface.Attribute('Widget')

    def getTerm(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def getTermByToken(token):
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def getValue(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """

    def __iter__():
        """Iterate over terms."""

    def __len__():
        """Return number of terms."""

    def __contains__(value):
        """Check wether terms containes the ``value``."""


class IBoolTerms(ITerms):
    """A specialization that handles boolean choices."""

    trueLabel = interface.Attribute('True-value Label')

    falseLabel = interface.Attribute('False-value Label')


# ----[ Widgets ]------------------------------------------------------------

class IDefaultWidget(interface.Interface):
    """ default widget, third party components
    can override this adapter and return different widget """


class IWidget(interface.Interface):
    """A widget within a form"""

    __fname__ = interface.Attribute('Factory name')
    __title__ = interface.Attribute('Widget factory title')
    __description__ = interface.Attribute('Widget factory description')

    name = interface.Attribute('Name')
    label = interface.Attribute('Label')
    mode = interface.Attribute('Mode')
    required = interface.Attribute('Required')
    error = interface.Attribute('Error')
    value = interface.Attribute('Value')
    template = interface.Attribute('''The widget template''')
    params = interface.Attribute('Request params')

    #ugly thing to remove setErrors parameter from extract
    setErrors = interface.Attribute('Set errors')

    def extract(default=NO_VALUE):
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

    def update():
        """Setup all of the widget information used for displaying."""

    def render():
        """Return the widget's text representation."""


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


class ISelectWidget(ISequenceWidget):
    """Select widget with ITerms option."""


class IOrderedSelectWidget(ISequenceWidget):
    """Ordered Select widget with ITerms option."""


class ICheckBoxWidget(ISequenceWidget):
    """Checbox widget."""


class ISingleCheckBoxWidget(ICheckBoxWidget):
    """Single Checbox widget."""


class IRadioWidget(ISequenceWidget):
    """Radio widget."""


class ISubmitWidget(IWidget):
    """Submit widget."""


class IImageWidget(IWidget):
    """Submit widget."""


class IButtonWidget(IWidget):
    """Button widget."""


class ITextAreaWidget(IWidget):
    """Text widget."""


class ITextLinesWidget(IWidget):
    """Text lines widget."""


class ITextWidget(IWidget):
    """Text widget."""


class IFileWidget(ITextWidget):
    """File widget."""


class IPasswordWidget(ITextWidget):
    """Password widget."""


class IWidgets(IManager):
    """A widget manager"""

    prefix = interface.Attribute('Prefix')
    mode = interface.Attribute('Mode')
    errors = interface.Attribute('Errors')
    hasRequiredFields = interface.Attribute('Has required fields')

    #ugly thing to remove setErrors parameter from extract
    setErrors = interface.Attribute('Set errors')

    def update():
        """Setup widgets."""

    def extract():
        """Extract the values from the widgets and validate them.
        """


# ----[ Buttons ]------------------------------------------------------------

class IButton(interface.Interface):
    """A button in a form."""

    accessKey = interface.Attribute('Access Key')


class IButtons(ISelectionManager):
    """Buttons manager."""


class IActions(IManager):
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

    def getRequestParams():
        '''Return the request params.'''

    def getContent():
        '''Return the content to be displayed and/or edited.'''

    def updateWidgets():
        '''Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.
        '''

    def validate(data, errors):
        ''' Do form level validation, like schema invariants, etc.
        
        Add errors to errors (IErrors) object.
        '''

    def extractData(setErrors=True):
        '''Extract the data of the form.

        setErrors: needs to be passed to extract() and to sub-widgets'''

    def update():
        '''Update the form.'''

    def render():
        '''Render the form.'''


class IInlineForm(IForm):
    """ """

    weight = interface.Attribute('Sort weight')

    def isAvailable():
        """ post construction check """

    def applyChanges(data):
        """ apply changes """


class ISubForm(IInlineForm):
    """A subform."""


class IDisplayForm(IForm):
    """Mark a form as display form, used for templates."""


class IInputForm(interface.Interface):
    """A form that is meant to process the input of the form controls."""

    action = interface.Attribute('Action')
    name = interface.Attribute('Name')
    id = interface.Attribute('Id')
    method = interface.Attribute('Method')
    enctype = interface.Attribute('Encoding Type')
    acceptCharset = interface.Attribute('Accepted Character Sets')
    accept = interface.Attribute('Accepted Content Types')


class IEditForm(IForm):
    """A form to edit data of a component."""

    groups = interface.Attribute('Groups')
    subforms = interface.Attribute('Subforms')

    def listWrappedForms():
        """ list wrapped forms """

    def updateForms():
        """ load and initialize subforms and groups """

    def applyChanges(data):
        """Apply the changes to the content component."""


class IGroup(IInlineForm):
    """A group of fields/widgets within a form."""
