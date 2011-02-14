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
from zope import interface, schema
from zope.i18n import translate

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.browser import widget
from memphis.form.interfaces import _, IRadioWidget


class RadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""
    interface.implementsOnly(IRadioWidget)
    config.adapts(schema.interfaces.IBool, None)
    config.adapts(schema.interfaces.IBool, None, name='radio')
    config.adapts(schema.interfaces.IChoice, None, name='radio')

    klass = u'radio-widget'
    items = ()

    __fname__ = 'radio'
    __title__ = _('Radio widget')
    __description__ = _('HTML Radio input widget.')

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
            if schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(
                    term.title, context=self.request, default=term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})

config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, IRadioWidget,
    template=view.template("memphis.form.browser:radio_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, IRadioWidget,
    template=view.template("memphis.form.browser:radio_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, IRadioWidget,
    template=view.template("memphis.form.browser:radio_hidden.pt"))
