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
"""Widget Framework Implementation

$Id: widget.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from memphis.form.interfaces import IFieldWidget
from memphis.form.browser.interfaces import \
    IHTMLFormElement, IHTMLInputWidget, IHTMLSelectWidget, \
    IHTMLTextInputWidget, IHTMLTextAreaWidget


class HTMLFormElement(object):
    zope.interface.implements(IHTMLFormElement)

    id = FieldProperty(IHTMLFormElement['id'])
    klass = FieldProperty(IHTMLFormElement['klass'])
    style = FieldProperty(IHTMLFormElement['style'])
    title = FieldProperty(IHTMLFormElement['title'])

    lang = FieldProperty(IHTMLFormElement['lang'])

    onclick = FieldProperty(IHTMLFormElement['onclick'])
    ondblclick = FieldProperty(IHTMLFormElement['ondblclick'])
    onmousedown = FieldProperty(IHTMLFormElement['onmousedown'])
    onmouseup = FieldProperty(IHTMLFormElement['onmouseup'])
    onmouseover = FieldProperty(IHTMLFormElement['onmouseover'])
    onmousemove = FieldProperty(IHTMLFormElement['onmousemove'])
    onmouseout = FieldProperty(IHTMLFormElement['onmouseout'])
    onkeypress = FieldProperty(IHTMLFormElement['onkeypress'])
    onkeydown = FieldProperty(IHTMLFormElement['onkeydown'])
    onkeyup = FieldProperty(IHTMLFormElement['onkeyup'])

    disabled = FieldProperty(IHTMLFormElement['disabled'])
    tabindex = FieldProperty(IHTMLFormElement['tabindex'])
    onfocus = FieldProperty(IHTMLFormElement['onfocus'])
    onblur = FieldProperty(IHTMLFormElement['onblur'])
    onchange = FieldProperty(IHTMLFormElement['onchange'])

    def addClass(self, klass):
        """See interfaces.IHTMLFormElement"""
        if not self.klass:
            self.klass = unicode(klass)
        else:
            #make sure items are not repeated
            parts = self.klass.split()+[unicode(klass)]
            seen = {}
            unique = []
            for item in parts:
                if item in seen:
                    continue
                seen[item]=1
                unique.append(item)
            self.klass = u' '.join(unique)

    def update(self):
        """See memphis.form.interfaces.IWidget"""
        super(HTMLFormElement, self).update()
        if self.required:
            self.addClass('required')


class HTMLInputWidget(HTMLFormElement):
    zope.interface.implements(IHTMLInputWidget)

    readonly = FieldProperty(IHTMLInputWidget['readonly'])
    alt = FieldProperty(IHTMLInputWidget['alt'])
    accesskey = FieldProperty(IHTMLInputWidget['accesskey'])
    onselect = FieldProperty(IHTMLInputWidget['onselect'])


class HTMLTextInputWidget(HTMLInputWidget):
    zope.interface.implements(IHTMLTextInputWidget)

    size = FieldProperty(IHTMLTextInputWidget['size'])
    maxlength = FieldProperty(IHTMLTextInputWidget['maxlength'])


class HTMLTextAreaWidget(HTMLFormElement):
    zope.interface.implements(IHTMLTextAreaWidget)

    rows = FieldProperty(IHTMLTextAreaWidget['rows'])
    cols = FieldProperty(IHTMLTextAreaWidget['cols'])
    readonly = FieldProperty(IHTMLTextAreaWidget['readonly'])
    accesskey = FieldProperty(IHTMLTextAreaWidget['accesskey'])
    onselect = FieldProperty(IHTMLTextAreaWidget['onselect'])


class HTMLSelectWidget(HTMLFormElement):
    zope.interface.implements(IHTMLSelectWidget)

    multiple = FieldProperty(IHTMLSelectWidget['multiple'])
    size = FieldProperty(IHTMLSelectWidget['size'])


def addFieldClass(widget):
    """Add a class to the widget that is based on the field type name.

    If the widget does not have field, then nothing is done.
    """
    if IFieldWidget.providedBy(widget):
        klass = unicode(widget.field.__class__.__name__.lower() + '-field')
        widget.addClass(klass)
