"""Radio widget implementation"""
import colander
from zope import interface, schema

from memphis import config, view
from memphis.form import pagelets, widget
from memphis.form.widget import SequenceWidget
from memphis.form.widgets.widget import HTMLInputWidget

from interfaces import _, IRadioWidget


class RadioWidget(HTMLInputWidget, SequenceWidget):
    __doc__ = _('HTML Radio input widget.')

    widget('radio', _('Radio widget'))
    interface.implementsOnly(IRadioWidget)

    #config.adapts(colander.SchemaNode, colander.Bool, name='radio')
    #config.adapts(schema.interfaces.IChoice, name='radio')

    klass = u'radio-widget'
    items = ()

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
    __doc__ = _('HTML Radio input widget.')
    widget('radio-horizontal', _('Horizontal Radio widget'))


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
