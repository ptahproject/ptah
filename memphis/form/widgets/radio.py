"""Radio widget implementation"""
import colander
from zope import interface, schema

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.widgets import widget

from interfaces import _, IRadioWidget


class RadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""
    interface.implementsOnly(IRadioWidget)
    config.adapts(colander.SchemaNode, colander.Bool, name='radio')
    config.adapts(schema.interfaces.IChoice, name='radio')

    klass = u'radio-widget'
    items = ()

    __fname__ = 'radio'
    __title__ = _('Radio widget')
    __description__ = _('HTML Radio input widget.')

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        super(RadioWidget, self).update()

        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = self.localizer.translate(term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


class HorizontalRadioWidget(RadioWidget):
    config.adapts(colander.SchemaNode, colander.Bool)
    config.adapts(colander.SchemaNode, colander.Bool, name='radio-horizontal')

    __fname__ = 'radio-horizontal'
    __title__ = _('Horizontal Radio widget')
    __description__ = _('HTML Radio input widget.')


view.registerPagelet(
    'form-display', IRadioWidget,
    template=view.template("memphis.form.widgets:radio_display.pt"))

view.registerPagelet(
    'form-input', IRadioWidget,
    template=view.template("memphis.form.widgets:radio_input.pt"))

view.registerPagelet(
    'form-input', HorizontalRadioWidget,
    template=view.template("memphis.form.widgets:radiohoriz_input.pt"))

view.registerPagelet(
    'form-hidden', IRadioWidget,
    template=view.template("memphis.form.widgets:radio_hidden.pt"))
