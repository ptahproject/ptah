""" Text Lines widget implementation """
from zope import interface
from memphis import config, view
from memphis.form import pagelets, widget
from memphis.form.widgets import textarea

from interfaces import _, ITextLinesWidget


class TextLinesWidget(textarea.TextAreaWidget):
    __doc__ = _('Text area based widget, each line is treated as sequence element.')

    widget('textlines', _('Text lines widget'))
    interface.implementsOnly(ITextLinesWidget)

    def deserialize(self, value):
        return self.node.deserialize(value.split('\n'))


view.registerPagelet(
    'form-display', ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_display.pt"))

view.registerPagelet(
    'form-input', ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_input.pt"))
