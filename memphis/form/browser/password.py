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
"""Password Widget Implementation

$Id: password.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from memphis import config, view
from memphis.form import interfaces, widget, pagelets
from memphis.form.browser import text


class PasswordWidget(text.TextWidget):
    """Input type password widget implementation."""
    zope.interface.implementsOnly(interfaces.IPasswordWidget)
    config.adapts(zope.schema.interfaces.IPassword, None)

    klass = u'password-widget'


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.IPasswordWidget,
    template=view.template("memphis.form.browser:password_display.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.IPasswordWidget,
    template=view.template("memphis.form.browser:password_input.pt"))
