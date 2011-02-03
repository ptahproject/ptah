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
"""Browser Widget Framework Interfaces

$Id: interfaces.py 11744 2011-01-28 09:15:15Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema


class IHTMLCoreAttributes(zope.interface.Interface):
    """The HTML element 'core' attributes."""

    id = zope.schema.BytesLine(
        title=u'Id',
        description=(u'This attribute assigns a name to an element. This '
                     u'name must be unique in a document.'),
        required=False)

    # HTML "class" attribute; "class" is a keyword in Python.
    klass = zope.schema.TextLine(
        title=u'Class',
        description=(u'This attribute assigns a class name or set of '
                     u'class names to an element. Any number of elements '
                     u'may be assigned the same class name or names.'),
        required=False)

    style = zope.schema.TextLine(
        title=u'Style',
        description=(u'This attribute offers advisory information about '
                     u'the element for which it is set.'),
        required=False)

    title = zope.schema.TextLine(
        title=u'Title',
        description=(u'This attribute offers advisory information about '
                     u'the element for which it is set.'),
        required=False)


class IHTMLI18nAttributes(zope.interface.Interface):
    """The HTML element 'i18n' attributes."""

    lang = zope.schema.TextLine(
        title=u'Language',
        description=(u"This attribute specifies the base language of an "
                     u"element's attribute values and text content."),
        required=False)


class IHTMLEventsAttributes(zope.interface.Interface):
    """The HTML element 'events' attributes."""

    onclick = zope.schema.TextLine(
        title=u'On Click',
        description=(u'The ``onclick`` event occurs when the pointing device '
                    u'button is clicked over an element.'),
        required=False)

    ondblclick = zope.schema.TextLine(
        title=u'On Double-Click',
        description=(u'The ``ondblclick`` event occurs when the pointing '
                     u'device button is double clicked over an element.'),
        required=False)

    onmousedown = zope.schema.TextLine(
        title=u'On Mouse Down',
        description=(u'The onmousedown event occurs when the pointing '
                     u'device button is pressed over an element.'),
        required=False)

    onmouseup = zope.schema.TextLine(
        title=u'On Mouse Up',
        description=(u'The ``onmouseup`` event occurs when the pointing '
                     u'device button is released over an element.'),
        required=False)

    onmouseover = zope.schema.TextLine(
        title=u'On Mouse Over',
        description=(u'The ``onmouseover`` event occurs when the pointing '
                     u'device is moved onto an element.'),
        required=False)

    onmousemove = zope.schema.TextLine(
        title=u'On Mouse Move',
        description=(u'The ``onmousemove`` event occurs when the pointing '
                     u'device is moved while it is over an element.'),
        required=False)

    onmouseout = zope.schema.TextLine(
        title=u'On Mouse Out',
        description=(u'The ``onmouseout`` event occurs when the pointing '
                     u'device is moved away from an element.'),
        required=False)

    onkeypress = zope.schema.TextLine(
        title=u'On Key Press',
        description=(u'The ``onkeypress`` event occurs when a key is '
                     u'pressed and released over an element.'),
        required=False)

    onkeydown = zope.schema.TextLine(
        title=u'On Key Down',
        description=(u'The ``onkeydown`` event occurs when a key is pressed '
                     u'down over an element.'),
        required=False)

    onkeyup = zope.schema.TextLine(
        title=u'On Key Up',
        description=(u'The ``onkeyup`` event occurs when a key is released '
                     u'over an element.'),
        required=False)


class IHTMLFormElement(IHTMLCoreAttributes,
                       IHTMLI18nAttributes,
                       IHTMLEventsAttributes):
    """A generic form-related element."""

    disabled = zope.schema.Choice(
        title=u'Disabled',
        description=(u'When set for a form control, this boolean attribute '
                     u'disables the control for user input.'),
        values=(None, 'disabled'),
        required=False)

    tabindex = zope.schema.Int(
        title=u'Tab Index',
        description=(u'This attribute specifies the position of the current '
                     u'element in the tabbing order for the current '
                     u'document. This value must be a number between 0 and '
                     u'32767.'),
        required=False)

    onfocus = zope.schema.TextLine(
        title=u'On Focus',
        description=(u'The ``onfocus`` event occurs when an element receives '
                     u'focus either by the pointing device or by tabbing '
                     u'navigation.'),
        required=False)

    onblur = zope.schema.TextLine(
        title=u'On blur',
        description=(u'The ``onblur`` event occurs when an element loses '
                     u'focus either by the pointing device or by tabbing '
                     u'navigation.'),
        required=False)

    onchange = zope.schema.TextLine(
        title=u'On Change',
        description=(u'The onchange event occurs when a control loses the '
                     u'input focus and its value has been modified since '
                     u'gaining focus.'),
        required=False)

    def addClass(klass):
        """Add a class to the HTML element.

        The class must be added to the ``klass`` attribute.
        """


class IHTMLInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element."""

    readonly = zope.schema.Choice(
        title=u'Read-Only',
        description=(u'When set for a form control, this boolean attribute '
                     u'prohibits changes to the control.'),
        values=(None, 'readonly'),
        required=False)

    alt = zope.schema.TextLine(
        title=u'Alternate Text',
        description=(u'For user agents that cannot display images, forms, '
                     u'or applets, this attribute specifies alternate text.'),
        required=False)

    accesskey = zope.schema.TextLine(
        title=u'Access Key',
        description=(u'This attribute assigns an access key to an element.'),
        min_length=1,
        max_length=1,
        required=False)

    onselect = zope.schema.TextLine(
        title=u'On Select',
        description=(u'The ``onselect`` event occurs when a user selects '
                     u'some text in a text field.'),
        required=False)


class IHTMLImageWidget(IHTMLInputWidget):
    """A widget using the HTML INPUT element with type 'image'."""

    src = zope.schema.TextLine(
        title=u'Image Source',
        description=(u'The source of the image used to display the widget.'),
        required=True)


class IHTMLTextInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element (for text types)."""

    size = zope.schema.Int(
        title=u'Size',
        description=(u'This attribute tells the user agent the initial width '
                     u'of the control -- in this case in characters.'),
        required=False)

    maxlength = zope.schema.Int(
        title=u'Maximum Length',
        description=(u'This attribute specifies the maximum number of '
                     u'characters the user may enter.'),
        required=False)


class IHTMLTextAreaWidget(IHTMLFormElement):
    """A widget using the HTML TEXTAREA element."""

    rows = zope.schema.Int(
        title=u'Rows',
        description=(u'This attribute specifies the number of visible text '
                     u'lines.'),
        required=False)

    cols = zope.schema.Int(
        title=u'columns',
        description=(u'This attribute specifies the visible width in average '
                     u'character widths.'),
        required=False)

    readonly = zope.schema.Choice(
        title=u'Read-Only',
        description=(u'When set for a form control, this boolean attribute '
                     u'prohibits changes to the control.'),
        values=(None, 'readonly'),
        required=False)

    accesskey = zope.schema.TextLine(
        title=u'Access Key',
        description=(u'This attribute assigns an access key to an element.'),
        min_length=1,
        max_length=1,
        required=False)

    onselect = zope.schema.TextLine(
        title=u'On Select',
        description=(u'The ``onselect`` event occurs when a user selects '
                     u'some text in a text field.'),
        required=False)


class IHTMLSelectWidget(IHTMLFormElement):
    """A widget using the HTML SELECT element."""

    multiple = zope.schema.Choice(
        title=u'Multiple',
        description=(u'If set, this boolean attribute allows multiple '
                     u'selections.'),
        values=(None, 'multiple'),
        required=False)

    size = zope.schema.Int(
        title=u'Size',
        description=(u'If a  SELECT element is presented as a scrolled '
                     u'list box, this attribute specifies the number of '
                     u'rows in the list that should be visible at the '
                     u'same time.'),
        default=1,
        required=False)
