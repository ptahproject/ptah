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
"""Check Widget Implementation"""
import zope.interface
import zope.schema
from zope.schema import vocabulary
from zope.i18n import translate

from memphis import config, view
from memphis.form import term, pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.browser import widget
from memphis.form.interfaces import _, ICheckBoxWidget, ISingleCheckBoxWidget


class CheckBoxWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type checkbox widget implementation."""
    zope.interface.implementsOnly(ICheckBoxWidget)

    klass = u'checkbox-widget'
    items = ()

    __fname__ = 'checkbox'
    __title__ = _('Checkbox widget')
    __description__ = _('HTML Checkbox input based widget.')

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(CheckBoxWidget, self).update()
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


class SingleCheckBoxWidget(CheckBoxWidget):
    """Single Input type checkbox widget implementation."""
    zope.interface.implementsOnly(ISingleCheckBoxWidget)
    config.adapts(zope.schema.interfaces.IBool, None, name='singlecheckbox')

    klass = u'single-checkbox-widget'

    __fname__ = 'singlecheckbox'
    __title__ = _('Single checkbox')
    __description__ = _('Single checkbox widget.')

    def update(self):
        super(SingleCheckBoxWidget, self).update()

    def updateTerms(self):
        if self.terms is None:
            self.terms = term.Terms()
            self.terms.terms = vocabulary.SimpleVocabulary((
                vocabulary.SimpleTerm('selected', 'selected', ''), ))
        return self.terms


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, ICheckBoxWidget,
    template=view.template("memphis.form.browser:checkbox_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, ICheckBoxWidget,
    template=view.template("memphis.form.browser:checkbox_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, ICheckBoxWidget,
    template=view.template("memphis.form.browser:checkbox_hidden.pt"))
