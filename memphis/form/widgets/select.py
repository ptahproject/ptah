""" Select/Multi select widget implementation """
from zope import interface

from memphis import config, view
from memphis.form import pagelets, widget
from memphis.form.interfaces import ITerm
from memphis.form.widget import SequenceWidget
from memphis.form.widgets.widget import HTMLSelectWidget

from interfaces import _, ISelectWidget


class SelectWidget(HTMLSelectWidget, SequenceWidget):
    __doc__ = _('HTML Select input widget.')

    interface.implementsOnly(ISelectWidget)

    klass = u'select-widget'
    prompt = False

    widget('select', _('Select widget'))

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    def isSelected(self, term):
        return term.token in self.value

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
            if ITerm.providedBy(term):
                content = self.localizer.translate(term.title)
            items.append(
                {'id':id, 'value':term.token, 'content':content,
                 'selected':selected})
        return items


class MultiSelectWidget(SelectWidget):
    __doc__ = _('HTML Multi Select input widget.')

    size = 5
    multiple = 'multiple'

    widget('multiselect', _('Multi select widget'))


view.registerPagelet(
    'form-display', ISelectWidget,
    template=view.template("memphis.form.widgets:select_display.pt",
                           title="HTML Select: display template"))

view.registerPagelet(
    'form-input', ISelectWidget,
    template=view.template("memphis.form.widgets:select_input.pt",
                           title="HTML Select: input template"))

view.registerPagelet(
    'form-hidden', ISelectWidget,
    template=view.template("memphis.form.widgets:select_hidden.pt",
                           title="HTML Select: hidden input template"))
