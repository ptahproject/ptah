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

$Id: select.py 11790 2011-01-31 00:41:45Z fafhrd91 $
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

_ = interfaces.MessageFactory


class SelectWidget(widget.HTMLSelectWidget, SequenceWidget):
    """Select widget implementation."""
    zope.interface.implementsOnly(interfaces.ISelectWidget)

    klass = u'select-widget'
    prompt = False

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    # Internal attributes
    _adapterValueAttributes = SequenceWidget._adapterValueAttributes + \
        ('noValueMessage', 'promptMessage', 'prompt')

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


@config.adapter(zope.schema.interfaces.IChoice, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def ChoiceWidgetDispatcher(field, request):
    """Dispatch widget for IChoice based also on its source."""
    return zope.component.getMultiAdapter((field, field.vocabulary, request),
                                          interfaces.IFieldWidget)


@config.adapter(zope.schema.interfaces.IChoice, zope.interface.Interface, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, SelectWidget(real_request))


@config.adapter(zope.schema.interfaces.IUnorderedCollection, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def CollectionSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    widget = zope.component.getMultiAdapter((field, field.value_type, request),
        interfaces.IFieldWidget)
    widget.size = 5
    widget.multiple = 'multiple'
    return widget


@config.adapter(zope.schema.interfaces.IUnorderedCollection,
                zope.schema.interfaces.IChoice, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return SelectFieldWidget(field, None, request)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.ISelectWidget,
    template=view.template("memphis.form.browser:select_display.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.ISelectWidget,
    template=view.template("memphis.form.browser:select_input.pt"))

config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, interfaces.ISelectWidget,
    template=view.template("memphis.form.browser:select_hidden.pt"))
