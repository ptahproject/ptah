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
"""Text Widget Implementation"""
import zope.interface
import zope.schema.interfaces

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import Widget
from memphis.form.browser import widget
from memphis.form.interfaces import _, ITextWidget


class TextWidget(widget.HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""
    zope.interface.implementsOnly(ITextWidget)
    config.adapts(zope.schema.interfaces.IBytesLine, None)
    config.adapts(zope.schema.interfaces.IBytesLine, None, name='text')
    config.adapts(zope.schema.interfaces.IASCIILine, None)
    config.adapts(zope.schema.interfaces.IASCIILine, None, name='text')
    config.adapts(zope.schema.interfaces.ITextLine, None)
    config.adapts(zope.schema.interfaces.ITextLine, None, name='text')
    config.adapts(zope.schema.interfaces.IId, None)
    config.adapts(zope.schema.interfaces.IId, None, name='text')
    config.adapts(zope.schema.interfaces.IInt, None)
    config.adapts(zope.schema.interfaces.IInt, None, name='text')
    config.adapts(zope.schema.interfaces.IFloat, None)
    config.adapts(zope.schema.interfaces.IFloat, None, name='text')
    config.adapts(zope.schema.interfaces.IDecimal, None)
    config.adapts(zope.schema.interfaces.IDecimal, None, name='text')
    config.adapts(zope.schema.interfaces.IDate, None)
    config.adapts(zope.schema.interfaces.IDate, None, name='text')
    config.adapts(zope.schema.interfaces.IDatetime, None)
    config.adapts(zope.schema.interfaces.IDatetime, None, name='text')
    config.adapts(zope.schema.interfaces.ITime, None)
    config.adapts(zope.schema.interfaces.ITime, None, name='text')
    config.adapts(zope.schema.interfaces.ITimedelta, None)
    config.adapts(zope.schema.interfaces.ITimedelta, None, name='text')
    config.adapts(zope.schema.interfaces.IURI, None)
    config.adapts(zope.schema.interfaces.IURI, None, name='text')

    klass = u'text-widget'
    value = u''

    __fname__ = 'text'
    __title__ = _(u'Text widget')
    __description__ = _(u'HTML Text input widget')

    def update(self):
        super(TextWidget, self).update()
        widget.addFieldClass(self)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, ITextWidget,
    template=view.template("memphis.form.browser:text_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, ITextWidget,
    template=view.template("memphis.form.browser:text_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, ITextWidget,
    template=view.template("memphis.form.browser:text_hidden.pt"))
