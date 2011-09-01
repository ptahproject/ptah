"""Check Widget Implementation"""
import colander
import zope.interface
import zope.schema
from zope.schema import vocabulary

from memphis import config, view
from memphis.form import term, pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.widgets import widget

from interfaces import _, ICheckBoxWidget, ISingleCheckBoxWidget


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

        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = self.localizer.translate(term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


class SingleCheckBoxWidget(CheckBoxWidget):
    """Single Input type checkbox widget implementation."""
    zope.interface.implementsOnly(ISingleCheckBoxWidget)
    config.adapter(colander.SchemaNode, colander.Bool, name='checkbox')

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


view.registerPagelet(
    'form-display', ICheckBoxWidget,
    template=view.template("memphis.form.widgets:checkbox_display.pt"))

view.registerPagelet(
    'form-input', ICheckBoxWidget,
    template=view.template("memphis.form.widgets:checkbox_input.pt"))

view.registerPagelet(
    'form-hidden', ICheckBoxWidget,
    template=view.template("memphis.form.widgets:checkbox_hidden.pt"))
