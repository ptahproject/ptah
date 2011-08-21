"""Button widget implementation"""
import zope.interface

from memphis import view
from memphis.form import interfaces, pagelets
from memphis.form.widget import Widget
from memphis.form.widgets import widget


class ButtonWidget(widget.HTMLInputWidget, Widget):
    """A simple button of a form."""
    zope.interface.implementsOnly(interfaces.IButtonWidget)

    klass = u'btn button-widget'

    def update(self):
        self.value = self.field.title
        if self.field.primary:
            self.addClass('primary')


view.registerPagelet(
    pagelets.IWidgetDisplayView, interfaces.IButtonWidget,
    template=view.template("memphis.form.widgets:button_display.pt"))

view.registerPagelet(
    pagelets.IWidgetInputView, interfaces.IButtonWidget,
    template=view.template("memphis.form.widgets:button_input.pt"))
