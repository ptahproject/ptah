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
""" Text Lines widget implementation """
from zope import interface
from zope.schema.interfaces import ISequence

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widgets import textarea
from memphis.form.interfaces import _, ITextLinesWidget


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    config.adapts(ISequence, None)
    config.adapts(ISequence, None, name='textlines')
    interface.implementsOnly(ITextLinesWidget)

    __fname__ = 'textlines'
    __title__ = _('Text lines widget')
    __description__ = _('Text area based widget, '
                        'each line is treated as sequence element.')


view.registerPagelet(
    pagelets.IWidgetDisplayView, ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_input.pt"))
