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
"""Text Widget Implementation

$Id: text.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form.widget import Widget
from memphis.form.browser import widget


class TextWidget(widget.HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""
    zope.interface.implementsOnly(interfaces.ITextWidget)

    klass = u'text-widget'
    value = u''

    def update(self):
        super(TextWidget, self).update()
        widget.addFieldClass(self)


@config.adapter(zope.schema.interfaces.IField, None)
@config.adapter(zope.schema.interfaces.IBytesLine, None)
@config.adapter(zope.schema.interfaces.IASCIILine, None)
@config.adapter(zope.schema.interfaces.ITextLine, None)
@config.adapter(zope.schema.interfaces.IId, None)
@config.adapter(zope.schema.interfaces.IInt, None)
@config.adapter(zope.schema.interfaces.IFloat, None)
@config.adapter(zope.schema.interfaces.IDecimal, None)
@config.adapter(zope.schema.interfaces.IDate, None)
@config.adapter(zope.schema.interfaces.IDatetime, None)
@config.adapter(zope.schema.interfaces.ITime, None)
@config.adapter(zope.schema.interfaces.ITimedelta, None)
@config.adapter(zope.schema.interfaces.IURI, None)
@zope.interface.implementer(interfaces.ITextWidget)
def TextFieldWidget(field, request):
    return TextWidget(field, request)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ITextWidget,
    template=view.template("memphis.form.browser:text_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ITextWidget,
    template=view.template("memphis.form.browser:text_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, interfaces.ITextWidget,
    template=view.template("memphis.form.browser:text_hidden.pt"))
