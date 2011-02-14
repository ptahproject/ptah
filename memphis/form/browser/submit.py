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
"""Submit Widget Implementation"""
import zope.component
import zope.interface

from memphis import config, view
from memphis.form import interfaces, pagelets
from memphis.form.browser import button


class SubmitWidget(button.ButtonWidget):
    """A submit button of a form."""
    config.adapts(interfaces.IButton, None)
    zope.interface.implementsOnly(interfaces.ISubmitWidget)

    klass = u'submit-widget z-form-button'


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.browser:submit_display.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.browser:submit_input.pt"))
