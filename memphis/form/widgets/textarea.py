""" HTML Textarea widget """
from zope import interface
from memphis import config, view
from memphis.form import pagelets, widget
from memphis.form.widget import Widget
from memphis.form.widgets.widget import HTMLTextAreaWidget

from interfaces import _, ITextAreaWidget


class TextAreaWidget(HTMLTextAreaWidget, Widget):
    __doc__ = _(u'HTML Text Area input widget')
    interface.implementsOnly(ITextAreaWidget)

    widget('textarea', _(u'TextArea widget'))

    klass = u'textarea-widget'
    value = u''

    rows = 5
    cols = 40


view.registerPagelet(
    'form-display', ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_display.pt"))

view.registerPagelet(
    'form-input', ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_input.pt"))

view.registerPagelet(
    'form-hidden', ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_hidden.pt"))
