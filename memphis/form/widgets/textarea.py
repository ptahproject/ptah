""" HTML Textarea widget """
from zope import interface
from memphis import config, view
from memphis.form import pagelets
from memphis.form.widget import Widget
from memphis.form.widgets import widget
from memphis.form.interfaces import _, ITextAreaWidget


class TextAreaWidget(widget.HTMLTextAreaWidget, Widget):
    """ Textarea widget implementation """
    interface.implementsOnly(ITextAreaWidget)

    klass = u'textarea-widget'
    value = u''

    rows = 5
    cols = 40

    __fname__ = 'textarea'
    __title__ = _(u'Text area widget')
    __description__ = _(u'HTML Text Area input widget')

    def update(self):
        super(TextAreaWidget, self).update()
        widget.addFieldClass(self)


view.registerPagelet(
    pagelets.IWidgetDisplayView, ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_input.pt"))

view.registerPagelet(
    pagelets.IWidgetHiddenView, ITextAreaWidget,
    template=view.template("memphis.form.widgets:textarea_hidden.pt"))
