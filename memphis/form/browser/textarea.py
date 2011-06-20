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
"""Text Area Widget Implementation"""
import zope.interface
import zope.schema.interfaces

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import Widget
from memphis.form.browser import widget
from memphis.form.interfaces import _, ITextAreaWidget


class TextAreaWidget(widget.HTMLTextAreaWidget, Widget):
    """Textarea widget implementation."""
    zope.interface.implementsOnly(ITextAreaWidget)
    config.adapts(zope.schema.interfaces.IText, None)
    config.adapts(zope.schema.interfaces.IText, None, name='textarea')
    config.adapts(zope.schema.interfaces.IASCII, None)
    config.adapts(zope.schema.interfaces.IASCII, None, name='textarea')

    klass = u'textarea-widget'
    value = u''

    rows = 5
    cols = 40

    __fname__ = 'textarea'
    __title__ = _(u'Text area widget')
    __description__ = _(u'HTML Text Area input widget')

    def update(self):
        super(TextAreaWidget, self).update()
        widget.addFieldClass(self)


view.registerPagelet(
    pagelets.IWidgetDisplayView, ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_input.pt"))

view.registerPagelet(
    pagelets.IWidgetHiddenView, ITextAreaWidget,
    template=view.template("memphis.form.browser:textarea_hidden.pt"))
