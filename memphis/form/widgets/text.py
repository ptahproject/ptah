"""Text widget implementation"""
import colander
from zope import interface
from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import Widget
from memphis.form.widgets import widget

from interfaces import _, ITextWidget


class TextWidget(widget.HTMLTextInputWidget, Widget):
    __doc__ = _(u'HTML Text input widget')

    interface.implementsOnly(ITextWidget)
    config.adapts(colander.SchemaNode, colander.Str)
    config.adapts(colander.SchemaNode, colander.Int)
    config.adapts(colander.SchemaNode, colander.Float)

    klass = u'text-widget'
    value = u''

    __fname__ = 'text'
    __title__ = _(u'Text widget')


view.registerPagelet(
    'form-display', ITextWidget,
    template=view.template("memphis.form.widgets:text_display.pt"))

view.registerPagelet(
    'form-input', ITextWidget,
    template=view.template("memphis.form.widgets:text_input.pt"))

view.registerPagelet(
    'form-hidden', ITextWidget,
    template=view.template("memphis.form.widgets:text_hidden.pt"))
