"""Text widget implementation"""
import colander
from zope import interface
from memphis import config, view
from memphis.form import pagelets, widget, Widget
from memphis.form.widgets.widget import HTMLTextInputWidget

from interfaces import _, ITextWidget


class TextWidget(HTMLTextInputWidget, Widget):
    __doc__ = _(u'HTML Text input widget')

    interface.implementsOnly(ITextWidget)

    widget('text', _(u'Text widget'))

    klass = u'text-widget'
    value = u''


view.registerPagelet(
    'form-display', ITextWidget,
    template=view.template("memphis.form.widgets:text_display.pt"))

view.registerPagelet(
    'form-input', ITextWidget,
    template=view.template("memphis.form.widgets:text_input.pt"))

view.registerPagelet(
    'form-hidden', ITextWidget,
    template=view.template("memphis.form.widgets:text_hidden.pt"))
