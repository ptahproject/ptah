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
"""Submit Widget Implementation

$Id: submit.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form.widget import FieldWidget
from memphis.form.browser import button


class SubmitWidget(button.ButtonWidget):
    """A submit button of a form."""
    zope.interface.implementsOnly(interfaces.ISubmitWidget)
    klass = u'submit-widget z-form-button'


@config.adapter(interfaces.IButton, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def SubmitFieldWidget(field, request):
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.browser:submit_display.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ISubmitWidget,
    template=view.template("memphis.form.browser:submit_input.pt"))
