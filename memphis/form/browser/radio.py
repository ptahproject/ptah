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

$Id: radio.py 11797 2011-01-31 04:13:41Z fafhrd91 $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form.widget import SequenceWidget, FieldWidget
from memphis.form.browser import widget


class RadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""
    zope.interface.implementsOnly(interfaces.IRadioWidget)

    klass = u'radio-widget'
    items = ()

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        """See memphis.form.interfaces.IWidget."""
        super(RadioWidget, self).update()
        widget.addFieldClass(self)
        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


@config.adapter(zope.schema.interfaces.IBool, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def RadioFieldWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return FieldWidget(field, RadioWidget(request))

config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.IRadioWidget,
    template=view.template("memphis.form.browser:radio_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.IRadioWidget,
    template=view.template("memphis.form.browser:radio_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, interfaces.IRadioWidget,
    template=view.template("memphis.form.browser:radio_hidden.pt"))
