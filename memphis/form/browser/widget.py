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
"""Widget Framework Implementation"""
import zope.interface
from memphis.form.interfaces import IWidget
from memphis.form.browser.interfaces import \
    IHTMLFormElement, IHTMLInputWidget, IHTMLSelectWidget, \
    IHTMLTextInputWidget, IHTMLTextAreaWidget


class HTMLFormElement(object):
    zope.interface.implements(IHTMLFormElement)

    id = None
    klass = None
    style = None
    title = None

    lang = None

    onclick = None
    ondblclick = None
    onmousedown = None
    onmouseup = None
    onmouseover = None
    onmousemove = None
    onmouseout = None
    onkeypress = None
    onkeydown = None
    onkeyup = None

    disabled = None
    tabindex = None
    onfocus = None
    onblur = None
    onchange = None

    def addClass(self, klass):
        """See interfaces.IHTMLFormElement"""
        if not self.klass:
            self.klass = klass
        else:
            #make sure items are not repeated
            if klass not in self.klass:
                self.klass = u'%s %s'%(self.klass, klass)

    def update(self):
        """See memphis.form.interfaces.IWidget"""
        super(HTMLFormElement, self).update()
        if self.required:
            self.addClass('required')


class HTMLInputWidget(HTMLFormElement):
    zope.interface.implements(IHTMLInputWidget)

    readonly = None
    alt = None
    accesskey = None
    onselect = None


class HTMLTextInputWidget(HTMLInputWidget):
    zope.interface.implements(IHTMLTextInputWidget)

    size = None
    maxlength = None


class HTMLTextAreaWidget(HTMLFormElement):
    zope.interface.implements(IHTMLTextAreaWidget)

    rows = None
    cols = None
    readonly = None
    accesskey = None
    onselect = None


class HTMLSelectWidget(HTMLFormElement):
    zope.interface.implements(IHTMLSelectWidget)

    multiple = None
    size = 1


def addFieldClass(widget):
    """Add a class to the widget that is based on the field type name.

    If the widget does not have field, then nothing is done.
    """
    if IWidget.providedBy(widget):
        klass = unicode(widget.field.__class__.__name__.lower() + '-field')
        widget.addClass(klass)
