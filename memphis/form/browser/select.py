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
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.browser import widget
from memphis.form.interfaces import _, ISelectWidget


class SelectWidget(widget.HTMLSelectWidget, SequenceWidget):
    """Select widget implementation."""
    zope.interface.implementsOnly(ISelectWidget)
    config.adapts(zope.schema.interfaces.IChoice, None)
    config.adapts(zope.schema.interfaces.IChoice, None, name='select')

    klass = u'select-widget'
    prompt = False

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    __fname__ = 'select'
    __title__ = _('Select widget')
    __description__ = _('HTML Select input based widget.')

    def isSelected(self, term):
        return term.token in self.value

    def update(self):
        """See memphis.form.interfaces.IWidget."""
        super(SelectWidget, self).update()
        widget.addFieldClass(self)

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            items.append(
                {'id':id, 'value':term.token, 'content':content,
                 'selected':selected})
        return items


class MultiSelectWidget(SelectWidget):

    size = 5
    multiple = 'multiple'

    __fname__ = 'multiselect'
    __title__ = _('Multi select widget')
    __description__ = _('HTML Multi Select input based widget.')


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, ISelectWidget,
    template=view.template("memphis.form.browser:select_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, ISelectWidget,
    template=view.template("memphis.form.browser:select_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, ISelectWidget,
    template=view.template("memphis.form.browser:select_hidden.pt"))
