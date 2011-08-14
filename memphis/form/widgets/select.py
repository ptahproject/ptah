""" Select/Multi select widget implementation """
from zope import interface, schema
from zope.schema.interfaces import ITitledTokenizedTerm
from pyramid.i18n import get_localizer

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import SequenceWidget
from memphis.form.widgets import widget
from memphis.form.interfaces import _, ISelectWidget


class SelectWidget(widget.HTMLSelectWidget, SequenceWidget):
    """Select widget implementation."""
    interface.implementsOnly(ISelectWidget)

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

        localizer = get_localizer(self.request)

        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if ITitledTokenizedTerm.providedBy(term):
                content = localizer.translate(term.title)
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


view.registerPagelet(
    pagelets.IWidgetDisplayView, ISelectWidget,
    template=view.template("memphis.form.widgets:select_display.pt",
                           "HTML Select: display template"))

view.registerPagelet(
    pagelets.IWidgetInputView, ISelectWidget,
    template=view.template("memphis.form.widgets:select_input.pt",
                           "HTML Select: input template"))

view.registerPagelet(
    pagelets.IWidgetHiddenView, ISelectWidget,
    template=view.template("memphis.form.widgets:select_hidden.pt",
                           "HTML Select: hidden input template"))
