"""Radio widget implementation"""
from zope import interface, schema

import colander
from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.widgets import widget
from memphis.form.interfaces import _, IRadioWidget


class RadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""
    interface.implementsOnly(IRadioWidget)
    config.adapts(colander.SchemaNode, colander.Bool, None, name='radio')
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
                label = view.translate(
                    term.title, context=self.request, default=term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


class HorizontalRadioWidget(RadioWidget):
    config.adapts(colander.SchemaNode, colander.Bool, None)
    config.adapts(schema.interfaces.IBool, None, name='radio-horizontal')

    __fname__ = 'radio-horizontal'
    __title__ = _('Horizontal Radio widget')
    __description__ = _('HTML Radio input widget.')


view.registerPagelet(
    pagelets.IWidgetDisplayView, IRadioWidget,
    template=view.template("memphis.form.widgets:radio_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, IRadioWidget,
    template=view.template("memphis.form.widgets:radio_input.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, HorizontalRadioWidget,
    template=view.template("memphis.form.widgets:radiohoriz_input.pt"))

view.registerPagelet(
    pagelets.IWidgetHiddenView, IRadioWidget,
    template=view.template("memphis.form.widgets:radio_hidden.pt"))
