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
"""Password Widget Implementation"""
import zope.interface
import zope.schema.interfaces

from memphis import config, view
from memphis.form import pagelets
from memphis.form.browser import text
from memphis.form.interfaces import _, IPasswordWidget


class PasswordWidget(text.TextWidget):
    """Input type password widget implementation."""
    zope.interface.implementsOnly(IPasswordWidget)
    config.adapts(zope.schema.interfaces.IPassword, None)
    config.adapts(zope.schema.interfaces.IPassword, None, name='password')
    config.adapts(zope.schema.interfaces.ITextLine, None, name='password')

    klass = u'password-widget'

    __fname__ = 'password'
    __title__ = _('Password Widget')
    __description__ = _('HTML Password input widget.')


view.registerPagelet(
    pagelets.IWidgetDisplayView, IPasswordWidget,
    template=view.template("memphis.form.browser:password_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, IPasswordWidget,
    template=view.template("memphis.form.browser:password_input.pt"))
