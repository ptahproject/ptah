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
"""
$Id: textlines.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"

import zope.interface

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form import widget
from memphis.form.browser import textarea


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    zope.interface.implementsOnly(interfaces.ITextLinesWidget)


def TextLinesFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def TextLinesFieldWidgetFactory(field, value_type, request):
    """IFieldWidget factory for TextLinesWidget."""
    return TextLinesFieldWidget(field, request)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ITextLinesWidget,
    template=view.template("memphis.form.browser:textlines_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ITextLinesWidget,
    template=view.template("memphis.form.browser:textlines_input.pt"))
