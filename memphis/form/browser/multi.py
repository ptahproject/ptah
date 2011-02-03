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

$Id: multi.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
from operator import attrgetter

import zope.component
import zope.interface

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form import widget
from memphis.form import button
from memphis.form.browser.widget import HTMLFormElement

_ = interfaces.MessageFactory


class FormMixin(object):
    zope.interface.implements(interfaces.IButtonForm, interfaces.IHandlerForm)


class MultiWidget(HTMLFormElement, widget.MultiWidget, FormMixin):
    """Multi widget implementation."""
    zope.interface.implements(interfaces.IMultiWidget)

    buttons = button.Buttons()

    prefix = 'widget'
    klass = u'multi-widget'
    items = ()

    showLabel = True # show labels for item subwidgets or not

    # Internal attributes
    _adapterValueAttributes = widget.MultiWidget._adapterValueAttributes + \
        ('showLabel',)

    def updateActions(self):
        self.updateAllowAddRemove()
        if self.name is not None:
            self.prefix = self.name
        self.actions = zope.component.getMultiAdapter(
            (self, self.request, self), interfaces.IActions)
        self.actions.update()

    def update(self):
        """See memphis.form.interfaces.IWidget."""
        super(MultiWidget, self).update()
        self.updateActions()
        self.actions.execute()
        self.updateActions() # Update again, as conditions may change

    @button.buttonAndHandler(_('Add'), name='add',
                             condition=attrgetter('allowAdding'))
    def handleAdd(self, action):
        self.appendAddingWidget()

    @button.buttonAndHandler(_('Remove selected'), name='remove',
                             condition=attrgetter('allowRemoving'))
    def handleRemove(self, action):
        self.widgets = [widget for widget in self.widgets
                        if ('%s.remove' % (widget.name)) not in self.request]
        self.value = [widget.value for widget in self.widgets]


@zope.interface.implementer(interfaces.IFieldWidget)
def multiFieldWidgetFactory(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, MultiWidget(request))


@config.adapter(zope.schema.interfaces.IList,
                zope.schema.interfaces.IField, None)
@config.adapter(zope.schema.interfaces.ITuple,
                zope.schema.interfaces.IField, None)
@zope.interface.implementer(interfaces.IFieldWidget)
def MultiFieldWidget(field, value_type, request):
    """IFieldWidget factory for TextLinesWidget."""
    return multiFieldWidgetFactory(field, request)


config.action(
    view.registerPagelet,
    pagelets.IWidgetDisplayView, interfaces.IMultiWidget,
    template=view.template("memphis.form.browser:multi_display.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetInputView, interfaces.IMultiWidget,
    template=view.template("memphis.form.browser:multi_input.pt"))


config.action(
    view.registerPagelet,
    pagelets.IWidgetHiddenView, interfaces.IMultiWidget,
    template=view.template("memphis.form.browser:multi_hidden.pt"))
