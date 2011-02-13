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
"""Text Area Widget Implementation

$Id: textarea.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form.widget import Widget
from memphis.form.browser import widget


class TextAreaWidget(widget.HTMLTextAreaWidget, Widget):
    """Textarea widget implementation."""
    zope.interface.implementsOnly(interfaces.ITextAreaWidget)
    config.adapts(zope.schema.interfaces.IASCII, None)

    klass = u'textarea-widget'
    value = u''

    def update(self):
        super(TextAreaWidget, self).update()
        widget.addFieldClass(self)


config.action(
    config.registerAdapter,
    TextAreaWidget, (zope.schema.interfaces.IText, None))


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, interfaces.ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_hidden.pt"))
