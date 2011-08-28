"""Browser Widget Interfaces"""
from zope import interface
from memphis.form.interfaces import _, IWidget, ISequenceWidget


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


class IDateWidget(ITextWidget):
    """Date widget"""


class IDatetimeWidget(ITextWidget):
    """Date widget"""


class ITinymceWidget(IWidget):
    """ TinyMCE widget """


class IHTMLCoreAttributes(interface.Interface):
    """The HTML element 'core' attributes."""

    id = interface.Attribute(
        u'This attribute assigns a name to an element. This '
        u'name must be unique in a document.')

    # HTML "class" attribute; "class" is a keyword in Python.
    klass = interface.Attribute(
        u'This attribute assigns a class name or set of '
        u'class names to an element. Any number of elements '
        u'may be assigned the same class name or names.')

    title = interface.Attribute(
        u'This attribute offers advisory information about '
        u'the element for which it is set.')


class IHTMLI18nAttributes(interface.Interface):
    """The HTML element 'i18n' attributes."""

    lang = interface.Attribute(
        u"This attribute specifies the base language of an "
        u"element's attribute values and text content.")


class IHTMLFormElement(IHTMLCoreAttributes,
                       IHTMLI18nAttributes):
    """A generic form-related element."""

    disabled = interface.Attribute(
        u'When set for a form control, this boolean attribute '
        u'disables the control for user input.')

    tabindex = interface.Attribute(
        u'This attribute specifies the position of the current '
        u'element in the tabbing order for the current '
        u'document. This value must be a number between 0 and '
        u'32767.')

    def addClass(klass):
        """Add a class to the HTML element.

        The class must be added to the ``klass`` attribute.
        """


class IHTMLInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element."""

    readonly = interface.Attribute(
        u'When set for a form control, this boolean attribute '
        u'prohibits changes to the control.')

    alt = interface.Attribute(
        u'For user agents that cannot display images, forms, '
        u'or applets, this attribute specifies alternate text.')

    accesskey = interface.Attribute(
        u'This attribute assigns an access key to an element.')


class IHTMLImageWidget(IHTMLInputWidget):
    """A widget using the HTML INPUT element with type 'image'."""

    src = interface.Attribute(
        u'The source of the image used to display the widget.')


class IHTMLTextInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element (for text types)."""

    size = interface.Attribute(
        u'This attribute tells the user agent the initial width '
        u'of the control -- in this case in characters.')

    maxlength = interface.Attribute(
        u'This attribute specifies the maximum number of '
        u'characters the user may enter.')


class IHTMLTextAreaWidget(IHTMLFormElement):
    """A widget using the HTML TEXTAREA element."""

    rows = interface.Attribute(
        u'This attribute specifies the number of visible text lines.')

    cols = interface.Attribute(
        u'This attribute specifies the visible width in average '
        u'character widths.')

    readonly = interface.Attribute(
        u'When set for a form control, this boolean attribute '
        u'prohibits changes to the control.')

    accesskey = interface.Attribute(
        u'This attribute assigns an access key to an element.')


class IHTMLSelectWidget(IHTMLFormElement):
    """A widget using the HTML SELECT element."""

    multiple = interface.Attribute(
        u'If set, this boolean attribute allows multiple selections.')

    size = interface.Attribute(
        u'If a  SELECT element is presented as a scrolled '
        u'list box, this attribute specifies the number of '
        u'rows in the list that should be visible at the '
        u'same time.')
