"""Text widget implementation"""
import colander
from zope import interface

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import Widget
from memphis.form.widgets import widget
from memphis.form.interfaces import _, ITextWidget


class TextWidget(widget.HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""
    interface.implementsOnly(ITextWidget)
    config.adapts(colander.SchemaNode, colander.Str, None)
    config.adapts(colander.SchemaNode, colander.Int, None)
    config.adapts(colander.SchemaNode, colander.Float, None)
    config.adapts(colander.SchemaNode, colander.Date, None)
    config.adapts(colander.SchemaNode, colander.DateTime, None)

    klass = u'text-widget'
    value = u''

    __fname__ = 'text'
    __title__ = _(u'Text widget')
    __description__ = _(u'HTML Text input widget')


view.registerPagelet(
    pagelets.IWidgetDisplayView, ITextWidget,
    template=view.template("memphis.form.widgets:text_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, ITextWidget,
    template=view.template("memphis.form.widgets:text_input.pt"))

view.registerPagelet(
    pagelets.IWidgetHiddenView, ITextWidget,
    template=view.template("memphis.form.widgets:text_hidden.pt"))
