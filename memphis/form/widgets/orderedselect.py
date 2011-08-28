"""Ordered-Selection Widget Implementation"""
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces

from memphis import config, view

from memphis.form import interfaces, pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.widgets import widget

import interfaces


class OrderedSelectWidget(widget.HTMLSelectWidget, SequenceWidget):
    """Ordered-Select widget implementation."""
    zope.interface.implementsOnly(interfaces.IOrderedSelectWidget)

    size = 5
    multiple = u'multiple'
    items = ()
    selectedItems = ()
    notselectedItems = ()

    def getItem(self, term, count=0):
        id = '%s-%i' % (self.id, count)
        content = term.value
        if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
            content = view.translate(
                term.title, context=self.request, default=term.title)
        return {'id':id, 'value':term.token, 'content':content}

    def update(self):
        super(OrderedSelectWidget, self).update()

        self.items = [
            self.getItem(term, count)
            for count, term in enumerate(self.terms)]
        self.selectedItems = [
            self.getItem(self.terms.getTermByToken(token), count)
            for count, token in enumerate(self.value)]
        self.notselectedItems = self.deselect()

    def deselect(self):
        selecteditems = []
        notselecteditems = []
        for selecteditem in self.selectedItems:
            selecteditems.append(selecteditem['content'])
        for item in self.items:
            if not item['content'] in selecteditems:
                notselecteditems.append(item)
        return notselecteditems


#@zope.component.adapter(zope.schema.interfaces.ISequence, None)
#@zope.interface.implementer(interfaces.IWidget)
def OrderedSelectFieldWidget(field, request):
    """IWidget factory for SelectWidget."""
    return FieldWidget(field, OrderedSelectWidget(request))


#@config.adapter(zope.schema.interfaces.ISequence, None)
#@zope.interface.implementer(interfaces.IWidget)
def SequenceSelectFieldWidget(field, request):
    """IWidget factory for SelectWidget."""
    return zope.component.getMultiAdapter(
        (field, field.value_type, request), interfaces.IWidget)


#@config.adapter(
#    zope.schema.interfaces.IList, zope.schema.interfaces.IChoice, None)
#@config.adapter(
#    zope.schema.interfaces.ITuple, zope.schema.interfaces.IChoice, None)
@zope.interface.implementer(interfaces.IWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    """IWidget factory for SelectWidget."""
    return OrderedSelectFieldWidget(field, request)


#view.registerPagelet(
#    pagelets.IWidgetDisplayView, interfaces.IOrderedSelectWidget,
#    template=view.template("memphis.form.widgets:orderedselect_display.pt"))


#view.registerPagelet(
#    pagelets.IWidgetInputView, interfaces.IOrderedSelectWidget,
#    template=view.template("memphis.form.widgets:orderedselect_input.pt"))
