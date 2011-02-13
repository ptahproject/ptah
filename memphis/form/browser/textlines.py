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
from zope import interface
from zope.schema.interfaces import ISequence

from memphis import config, view
from memphis.form import interfaces, pagelets
from memphis.form.browser import textarea


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    config.adapts(ISequence, None)
    interface.implementsOnly(interfaces.ITextLinesWidget)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ITextLinesWidget,
    template=view.template("memphis.form.browser:textlines_display.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ITextLinesWidget,
    template=view.template("memphis.form.browser:textlines_input.pt"))
