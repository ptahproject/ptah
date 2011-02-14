##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Form and Widget Framework Interfaces

$Id: interfaces.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
from zope import interface
import zope.i18nmessageid
import zope.interface
import zope.schema
from zope.interface.common import mapping
from pyramid.i18n import TranslationStringFactory

MessageFactory = _ = TranslationStringFactory('memphis.form')

INPUT_MODE = 'input'
DISPLAY_MODE = 'display'
HIDDEN_MODE = 'hidden'


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

class IValidator(zope.interface.Interface):
    """A validator for a particular value."""

    def validate(value):
        """Validate the value.

        If successful, return ``None``. Otherwise raise an ``Invalid`` error.
        """

class IFormValidator(zope.interface.Interface):
    """A validator for a form."""

    def validate(data):
        """ validate data """


# ----[ Errors ]--------------------------------------------------------------

class IWidgetError(zope.interface.Interface):
    """ A special error, for can return additional errors and explicitly 
    set to which widget this error should be appied. """

    name = interface.Attribute('Widget name')

    error = interface.Attribute('Error instance')


class IErrorViewSnippet(zope.interface.Interface):
    """A view providing a view for an error"""

    widget = zope.schema.Field(
        title = _("Widget"),
        description = _("The widget that the view is on"),
        required = True)

    error = zope.schema.Field(
        title=_('Error'),
        description=_('Error the view is for.'),
        required=True)

    def update():
        """Update view."""

    def render():
        """Render view."""


class IMultipleErrors(zope.interface.Interface):
    """An error that contains many errors"""

    errors = zope.interface.Attribute("List of errors")


# ----[ Fields ]--------------------------------------------------------------

class IField(zope.interface.Interface):
    """Field wrapping a schema field used in the form."""

    __name__ = zope.schema.TextLine(
        title=_('Title'),
        description=_('The name of the field within the form.'),
        required=True)

    field = zope.schema.Field(
        title=_('Schema Field'),
        description=_('The schema field that is to be rendered.'),
        required=True)

    prefix = zope.schema.Field(
        title=_('Prefix'),
        description=_('The prefix of the field used to avoid name clashes.'),
        required=True)

    mode = zope.schema.Field(
        title=_('Mode'),
        description=_('The mode in which to render the widget for the field.'),
        required=True)

    interface = zope.schema.Field(
        title=_('Interface'),
        description=_('The interface from which the field is coming.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the context for a value.'),
        required=False)

    widgetFactory = zope.schema.Field(
        title=_('Widget Factory'),
        description=_('The widget factory.'),
        required=False,
        default=None,
        missing_value=None)


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

class IDataManager(zope.interface.Interface):
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


# ----[ Data Converters ]----------------------------------------------------

class IDataConverter(zope.interface.Interface):
    """A data converter from field to widget values and vice versa."""

    def toWidgetValue(value):
        """Convert the field value to a widget output value.

        If conversion fails or is not possible, a ``ValueError`` *must* be
        raised. However, this method should effectively never fail, because
        incoming value is well-defined.
        """

    def toFieldValue(value):
        """Convert an input value to a field/system internal value.

        This methods *must* also validate the converted value against the
        field.

        If the conversion fails, a ``ValueError`` *must* be raised. If
        the validation fails, a ``ValidationError`` *must* be raised.
        """

# term interfaces
class ITerms(zope.interface.Interface):
    """ """

    context = zope.schema.Field()
    request = zope.schema.Field()
    form = zope.schema.Field()
    field = zope.schema.Field()
    widget = zope.schema.Field()

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

    trueLabel = zope.schema.TextLine(
        title=_('True-value Label'),
        description=_('The label for a true value of the Bool field.'),
        required=True)

    falseLabel = zope.schema.TextLine(
        title=_('False-value Label'),
        description=_('The label for a false value of the Bool field.'),
        required=False)


# ----[ Widgets ]------------------------------------------------------------

class IDefaultWidget(zope.interface.Interface):
    """ default widget, third party components
    can override this adapter and return different widget """


class IWidget(zope.interface.Interface):
    """A widget within a form"""

    __fname__ = zope.interface.Attribute('Factory name')
    __title__ = zope.interface.Attribute('Widget factory title')
    __description__ = zope.interface.Attribute('Widget factory description')

    name = zope.schema.BytesLine(
        title=_('Name'),
        description=_('The name the widget is known under.'),
        required=True)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('''
        The widget label.

        Label may be translated for the request.

        The attribute may be implemented as either a read-write or read-only
        property, depending on the requirements for a specific implementation.
        '''),
        required=True)

    mode = zope.schema.BytesLine(
        title=_('Mode'),
        description=_('A widget mode.'),
        default=INPUT_MODE,
        required=True)

    required = zope.schema.Bool(
        title=_('Required'),
        description=_('If true the widget should be displayed as required '
                      'input.'),
        default=False,
        required=True)

    error = zope.schema.Field(
        title=_('Error'),
        description=_('If an error occurred during any step, the error view '
                      'stored here.'),
        required=False)

    value = zope.schema.Field(
        title=_('Value'),
        description=_('The value that the widget represents.'),
        required=False)

    template = zope.interface.Attribute('''The widget template''')

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the request for a value.'),
        default=False,
        required=False)

    #ugly thing to remove setErrors parameter from extract
    setErrors = zope.schema.Bool(
        title=_('Set errors'),
        description=_('A flag, when set, the widget sets error messages '
                      'on calling extract().'),
        default=True,
        required=False)

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

    noValueToken = zope.schema.ASCIILine(
        title=_('NO_VALUE Token'),
        description=_('The token to be used, if no value has been selected.'))

    terms = zope.schema.Object(
        title=_('Terms'),
        description=_('A component that provides the options for selection.'),
        schema=ITerms)

    def updateTerms():
        """Update the widget's ``terms`` attribute and return the terms.

        This method can be used by external components to get the terms
        without having to worry whether they are already created or not.
        """

class ISelectWidget(ISequenceWidget):
    """Select widget with ITerms option."""

    prompt = zope.schema.Bool(
        title=_('Prompt'),
        description=_('A flag, when set, enables a choice explicitely '
                      'requesting the user to choose a value.'),
        default=False)

    items = zope.schema.Tuple(
        title=_('Items'),
        description=_('A collection of dictionaries containing all pieces of '
                      'information for rendering. The following keys must '
                      'be in each dictionary: id, value, content, selected'))

    noValueMessage = zope.schema.Text(
        title=_('No-Value Message'),
        description=_('A human-readable text that is displayed to refer the '
                      'missing value.'))

    promptMessage = zope.schema.Text(
        title=_('Prompt Message'),
        description=_('A human-readable text that is displayed to refer the '
                      'missing value.'))


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

    prefix = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the widgets.'),
        default='widgets.',
        required=True)

    mode = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the widgets.'),
        default=INPUT_MODE,
        required=True)

    errors = zope.schema.Field(
        title=_('Errors'),
        description=_('The collection of errors that occured during '
                      'validation.'),
        default=(),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('If set the context is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('If set the request is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreReadonly = zope.schema.Bool(
        title=_('Ignore Readonly'),
        description=_('If set then readonly fields will also be shown.'),
        default=False,
        required=True)

    hasRequiredFields = zope.schema.Bool(
        title=_('Has required fields'),
        description=_('A flag set when at least one field is marked as '
                      'required'),
        default=False,
        required=False)

    #ugly thing to remove setErrors parameter from extract
    setErrors = zope.schema.Bool(
        title=_('Set errors'),
        description=_('A flag, when set, the contained widgets set error '
                      'messages on calling extract().'),
        default=True,
        required=False)

    field = zope.schema.Field(
        title=_('Field'),
        description=_('The schema field which the widget is representing.'),
        required=True)

    def update():
        """Setup widgets."""

    def extract():
        """Extract the values from the widgets and validate them.
        """


# ----[ Actions ]------------------------------------------------------------

class ActionExecutionError(Exception):
    """An error that occurs during the execution of an action handler."""

    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return '<%s wrapping %r>' %(self.__class__.__name__, self.error)


class WidgetActionExecutionError(ActionExecutionError):
    """An action execution error that occurred due to a widget value being
    incorrect."""

    def __init__(self, widgetName, error):
        ActionExecutionError.__init__(self, error)
        self.widgetName = widgetName


class IAction(zope.interface.Interface):
    """Action"""

    __name__ = zope.schema.TextLine(
        title=_('Name'),
        description=_('The object name.'),
        required=False,
        default=None)

    title = zope.schema.TextLine(
        title=_('Title'),
        description=_('The action title.'),
        required=True)

    def isExecuted():
        """Determine whether the action has been executed."""


class IActionHandler(zope.interface.Interface):
    """Action handler."""


class IActionEvent(zope.interface.Interface):
    """An event specific for an action."""

    action = zope.schema.Object(
        title=_('Action'),
        description=_('The action for which the event is created.'),
        schema=IAction,
        required=True)


class IActionErrorEvent(IActionEvent):
    """An action event that is created when an error occurred."""

    error = zope.schema.Field(
        title=_('Error'),
        description=_('The error that occurred during the action.'),
        required=True)


class IActions(IManager):
    """A action manager"""

    executedActions = zope.interface.Attribute(
        '''An iterable of all executed actions (usually just one).''')

    def update():
        """Setup actions."""

    def execute():
        """Exceute actions.

        If an action execution error is raised, the system is notified using
        the action occurred error; on the other hand, if successful, the
        action successfull event is sent to the system.
        """


class IButton(zope.schema.interfaces.IField):
    """A button in a form."""

    accessKey = zope.schema.TextLine(
        title=_('Access Key'),
        description=_('The key when pressed causes the button to be pressed.'),
        min_length=1,
        max_length=1,
        required=False)

    actionFactory = zope.schema.Field(
        title=_('Action Factory'),
        description=_('The action factory.'),
        required=False,
        default=None,
        missing_value=None)


class IButtons(ISelectionManager):
    """Button manager."""


class IButtonAction(IAction, IWidget):
    """Button action."""


class IButtonHandlers(zope.interface.Interface):
    """A collection of handlers for buttons."""

    def addHandler(button, handler):
        """Add a new handler for a button."""

    def getHandler(button):
        """Get the handler for the button."""

    def copy():
        """Copy this object and return the copy."""

    def __add__(other):
        """Add another handlers object.

        During the process a copy of the current handlers object should be
        created and the other one is added to the copy. The return value is
        the copy.
        """


class IButtonHandler(zope.interface.Interface):
    """A handler managed by the button handlers."""

    def __call__(form, action):
        """Execute the handler."""


# ----[ Forms ]--------------------------------------------------------------

class IHandlerForm(zope.interface.Interface):
    """A form that stores the handlers locally."""

    handlers = zope.schema.Object(
        title=_('Handlers'),
        description=_('A list of action handlers defined on the form.'),
        schema=IButtonHandlers,
        required=True)


class IActionForm(zope.interface.Interface):
    """A form that stores executable actions"""

    actions = zope.schema.Object(
        title=_('Actions'),
        description=_('A list of actions defined on the form'),
        schema=IActions,
        required=True)

    refreshActions = zope.schema.Bool(
        title=_('Refresh actions'),
        description=_('A flag, when set, causes form actions to be '
                      'updated again after their execution.'),
        default=False,
        required=True)


class IContextAware(zope.interface.Interface):
    """Offers a context attribute.

    For advanced uses, the widget will make decisions based on the context
    it is rendered in.
    """

    context = zope.schema.Field(
        title=_('Context'),
        description=_('The context in which the widget is displayed.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the context for a value.'),
        default=False,
        required=False)


class IFormAware(zope.interface.Interface):
    """Offers a form attribute.

    For advanced uses the widget will make decisions based on the form
    it is rendered in.
    """

    form = zope.schema.Field()


class IForm(zope.interface.Interface):
    """Form"""

    mode = zope.schema.Field(
        title=_('Mode'),
        description=_('The mode in which to render the widgets.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('If set the context is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('If set the request is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreReadonly = zope.schema.Bool(
        title=_('Ignore Readonly'),
        description=_('If set then readonly fields will also be shown.'),
        default=False,
        required=True)

    widgets = zope.schema.Object(
        title=_('Widgets'),
        description=_('A widget manager containing the widgets to be used in '
                      'the form.'),
        schema=IWidgets)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('A human readable text describing the form that can be '
                      'used in the UI.'),
        required=False)

    prefix = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the form used to uniquely identify it.'),
        default='form.')

    def getContent():
        '''Return the content to be displayed and/or edited.'''

    def updateWidgets():
        '''Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.
        '''

    def validate(data):
        ''' Do form level validation, like schema invariants, etc.
        
        Return sequence of errors or None
        '''

    def extractData(setErrors=True):
        '''Extract the data of the form.

        setErrors: needs to be passed to extract() and to sub-widgets'''

    def update():
        '''Update the form.'''

    def render():
        '''Render the form.'''


class IWrappedForm(IForm):
    """ """

    weight = interface.Attribute('Sort weight')

    def isAvailable():
        """ post construction check """

    def applyChanges(data):
        """ apply changes """


class ISubForm(IWrappedForm):
    """A subform."""


class IDisplayForm(IForm):
    """Mark a form as display form, used for templates."""


class IInputForm(zope.interface.Interface):
    """A form that is meant to process the input of the form controls."""

    action = zope.schema.URI(
        title=_('Action'),
        description=_('The action defines the URI to which the form data are '
                      'sent.'),
        required=True)

    name = zope.schema.TextLine(
        title=_('Name'),
        description=_('The name of the form used to identify it.'),
        required=False)

    id = zope.schema.TextLine(
        title=_('Id'),
        description=_('The id of the form used to identify it.'),
        required=False)

    method = zope.schema.Choice(
        title=_('Method'),
        description=_('The HTTP method used to submit the form.'),
        values=('get', 'post'),
        default='post',
        required=False)

    enctype = zope.schema.ASCIILine(
        title=_('Encoding Type'),
        description=_('The data encoding used to submit the data safely.'),
        default='multipart/form-data',
        required=False)

    acceptCharset = zope.schema.ASCIILine(
        title=_('Accepted Character Sets'),
        description=_('This is a list of character sets the server accepts. '
                      'By default this is unknown.'),
        required=False)

    accept = zope.schema.ASCIILine(
        title=_('Accepted Content Types'),
        description=_('This is a list of content types the server can '
                      'safely handle.'),
        required=False)


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


class IFieldsForm(IForm):
    """A form that is based upon defined fields."""

    fields = zope.schema.Object(
        title=_('Fields'),
        description=_('A field manager describing the fields to be used for '
                      'the form.'),
        schema=IFields)


class IButtonForm(IForm):
    """A form that is based upon defined buttons."""

    buttons = zope.schema.Object(
        title=_('Buttons'),
        description=_('A button manager describing the buttons to be used for '
                      'the form.'),
        schema=IButtons)


class IGroup(IWrappedForm):
    """A group of fields/widgets within a form."""
